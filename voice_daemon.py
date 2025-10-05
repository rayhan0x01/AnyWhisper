#!/usr/bin/env python3
"""
AnyWhisper Daemon

Background service that listens for recording triggers via a Unix socket.
"""

import os
import socket
import threading
import signal
import sys
import re
from audio_recorder import AudioRecorder
from api_client import WhisperAPIClient
from text_injector import TextInjector
from config import (
    ENABLE_TRANSCRIPTION_ACTIONS,
    POST_TRANSCRIPTION_ACTIONS,
    POST_TRANSCRIPTION_OPT_DOT
)


SOCKET_PATH = "/tmp/voice_to_text.sock"


class VoiceDaemon:
    """Background daemon for any-whisper processing."""
    
    def __init__(self):
        self.recorder = AudioRecorder()
        self.api_client = WhisperAPIClient()
        self.text_injector = TextInjector()
        self.is_recording = False
        self.socket = None
        self.running = True
        self.ydotoold_process = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
    
    def notify(self, title, message):
        """Send desktop notification."""
        try:
            os.system(f'notify-send "{title}" "{message}" 2>/dev/null &')
        except:
            pass
    
    def start_recording(self):
        """Start voice recording."""
        if self.is_recording:
            return "ALREADY_RECORDING"
        
        self.is_recording = True
        print("🎤 Recording started...")
        # self.notify("AnyWhisper", "🎤 Recording... Speak now!")
        
        success = self.recorder.start_recording()
        if not success:
            self.is_recording = False
            print("❌ Failed to start recording")
            self.notify("AnyWhisper", "❌ Failed to start recording")
            return "ERROR"
        
        # Start monitoring thread to detect when recording stops automatically
        threading.Thread(target=self._monitor_recording, daemon=True).start()
        
        return "RECORDING"
    
    def stop_recording(self):
        """Stop recording and process audio."""
        if not self.is_recording:
            return "NOT_RECORDING"
        
        print("⏹️  Stopping recording...")
        # self.notify("AnyWhisper", "⏹️ Processing...")
        
        # Stop recording and get the audio file
        audio_file = self.recorder.stop_recording()
        self.is_recording = False
        
        if not audio_file:
            print("❌ No audio recorded")
            self.notify("AnyWhisper", "❌ No audio recorded")
            return "NO_AUDIO"
        
        # Transcribe in a separate thread to not block
        threading.Thread(target=self._process_audio, args=(audio_file,), daemon=True).start()
        return "PROCESSING"
    
    def toggle_recording(self):
        """Toggle recording on/off."""
        if self.is_recording:
            return self.stop_recording()
        else:
            return self.start_recording()
    
    def _monitor_recording(self):
        """Monitor the recording and auto-process when it stops."""
        import time
        
        # Wait while recording is active
        while self.is_recording and self.recorder.is_recording:
            time.sleep(0.2)
        
        # Give a small delay to ensure recording thread fully completes
        time.sleep(0.3)
        
        # Check if recording stopped automatically (not manually)
        # The daemon still thinks it's recording, but recorder has stopped
        if self.is_recording and not self.recorder.is_recording:
            print("🔔 Recording stopped automatically (silence detected)")
            # Trigger the normal stop process
            self.stop_recording()
    
    def _process_audio(self, audio_file):
        """Process audio file (transcribe and inject text)."""
        print("🔄 Transcribing audio...")
        text = self.api_client.transcribe_audio(audio_file)
        
        if text:
            print(f"✅ Transcription: {text}")
            # self.notify("AnyWhisper", f"📝 {text[:50]}{'...' if len(text) > 50 else ''}")
            
            # Check for post-transcription actions (if enabled)
            post_action = None
            cleaned_text = text
            matched_pattern = None
            
            if ENABLE_TRANSCRIPTION_ACTIONS:
                for pattern, action in POST_TRANSCRIPTION_ACTIONS.items():
                    # Optionally add \.? before $ to handle periods Whisper may add
                    modified_pattern = pattern
                    if POST_TRANSCRIPTION_OPT_DOT and pattern.endswith('$'):
                        # Insert \.? before the $
                        modified_pattern = pattern[:-1] + r'\.?$'
                    
                    # Check if pattern matches (case-insensitive)
                    match = re.search(modified_pattern, text, re.IGNORECASE)
                    if match:
                        print(f"🎯 Pattern matched: '{pattern}' → Action: {action}")
                        post_action = action
                        matched_pattern = modified_pattern
                        # Remove the matched pattern from text
                        cleaned_text = re.sub(modified_pattern, '', text, flags=re.IGNORECASE).strip()
                        break
            
            # Inject the text (with cleaned version if pattern was found)
            text_to_inject = cleaned_text if post_action else text
            
            if text_to_inject:  # Only inject if there's text left after cleaning
                print(f"⌨️  Injecting text: {text_to_inject}")
                success = self.text_injector.inject_text(text_to_inject, post_action=post_action)
                
                if not success:
                    print("⚠️  Falling back to clipboard...")
                    self.text_injector.copy_to_clipboard(text_to_inject)
                    self.notify("AnyWhisper", "📋 Copied to clipboard (Ctrl+V to paste)")
            elif post_action:
                # No text to type, just execute the action
                print(f"⌨️  Executing action: {post_action}")
                self.text_injector._execute_key_action(post_action)
        else:
            print("❌ Transcription failed")
            self.notify("AnyWhisper", "❌ Transcription failed")
        
        # Clean up temp file
        try:
            if os.path.exists(audio_file):
                os.remove(audio_file)
        except:
            pass
    
    def handle_client(self, client_socket):
        """Handle client connection."""
        try:
            data = client_socket.recv(1024).decode('utf-8').strip()
            
            if data == "START":
                response = self.start_recording()
            elif data == "STOP":
                response = self.stop_recording()
            elif data == "TOGGLE":
                response = self.toggle_recording()
            elif data == "STATUS":
                response = "RECORDING" if self.is_recording else "IDLE"
            elif data == "PING":
                response = "PONG"
            else:
                response = "UNKNOWN_COMMAND"
            
            client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    def start_ydotoold_if_needed(self):
        """Start ydotoold if on Wayland and not already running."""
        if self.text_injector.method != 'wayland':
            return
        
        # Check if ydotoold is already running
        try:
            result = os.popen('pgrep -x ydotoold').read().strip()
            if result:
                print("✓ ydotoold already running")
                return
        except:
            pass
        
        # Try to start local ydotoold
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ydotoold_path = os.path.join(script_dir, 'ydotoold')
        
        if os.path.exists(ydotoold_path) and os.access(ydotoold_path, os.X_OK):
            try:
                import subprocess
                self.ydotoold_process = subprocess.Popen([ydotoold_path])
                import time
                time.sleep(1)
                print("✓ Started local ydotoold daemon")
            except Exception as e:
                print(f"⚠️  Could not start ydotoold: {e}")
    
    def start(self):
        """Start the daemon."""
        # Start ydotoold if needed (Wayland only)
        self.start_ydotoold_if_needed()
        
        # Remove old socket if it exists
        try:
            os.unlink(SOCKET_PATH)
        except OSError:
            if os.path.exists(SOCKET_PATH):
                raise
        
        # Create Unix socket
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(SOCKET_PATH)
        self.socket.listen(5)
        
        # Make socket accessible
        os.chmod(SOCKET_PATH, 0o666)
        
        print("=" * 60)
        print("AnyWhisper Daemon Started")
        print("=" * 60)
        print(f"Socket: {SOCKET_PATH}")
        print(f"Display server: {self.text_injector.method}")
        
        # Check API health
        print("\n🔍 Checking Whisper API...")
        if self.api_client.check_api_health():
            print("✅ Whisper API is accessible")
        else:
            print("⚠️  Warning: Cannot reach Whisper API")
            print("   Make sure Docker container is running:")
            print("   docker run -d -p 127.0.0.1:4444:4444 --name whisper-assistant whisper-assistant")
        
        print("\n📝 To bind global shortcut:")
        print("   GNOME: Settings → Keyboard → Custom Shortcuts")
        print(f"   Command: {os.path.abspath('voice_trigger.py')}")
        print("\n🛑 Press Ctrl+C to stop")
        print("=" * 60)
        
        self.notify("AnyWhisper", "✅ Daemon started")
        
        # Accept connections
        while self.running:
            try:
                self.socket.settimeout(1.0)
                try:
                    client, _ = self.socket.accept()
                    threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()
                except socket.timeout:
                    continue
            except KeyboardInterrupt:
                break
            except Exception as e:
                if self.running:
                    print(f"Error: {e}")
        
        self.shutdown(None, None)
    
    def shutdown(self, signum, frame):
        """Shutdown the daemon."""
        if not self.running:
            return
        
        print("\n\n👋 Shutting down...")
        self.running = False
        
        if self.is_recording:
            self.recorder.stop_recording()
        
        if self.socket:
            self.socket.close()
        
        try:
            os.unlink(SOCKET_PATH)
        except:
            pass
        
        # Stop ydotoold if we started it
        if self.ydotoold_process:
            try:
                self.ydotoold_process.terminate()
                self.ydotoold_process.wait(timeout=5)
                print("Stopped ydotoold daemon")
            except:
                pass
        
        print("Daemon stopped.")
        sys.exit(0)


def main():
    """Main entry point."""
    daemon = VoiceDaemon()
    daemon.start()


if __name__ == "__main__":
    main()

