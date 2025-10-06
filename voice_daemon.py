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
import logging
from audio_recorder import AudioRecorder
from api_client import WhisperAPIClient
import config
from text_injector import TextInjector
from config import (
    ENABLE_TRANSCRIPTION_ACTIONS,
    POST_TRANSCRIPTION_ACTIONS,
    POST_TRANSCRIPTION_OPT_DOT,
    ENABLE_AI_PROCESSING,
    AI_API_KEY,
    AI_MODEL_NAME,
    AI_PROVIDER,
    AI_PROMPT_TEMPLATES,
    POST_AI_TRIGGERS,
    LOG_FILE,
    LOG_LEVEL
)


SOCKET_PATH = "/tmp/voice_to_text.sock"

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AnyWhisper')


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
        
        logger.info("=" * 60)
        logger.info("AnyWhisper Daemon initialized")
        logger.info(f"Log file: {LOG_FILE}")
        logger.info(f"Log level: {LOG_LEVEL}")
        logger.info(f"AI Processing: {'ENABLED' if ENABLE_AI_PROCESSING else 'DISABLED'}")
        logger.info(f"Transcription Actions: {'ENABLED' if ENABLE_TRANSCRIPTION_ACTIONS else 'DISABLED'}")
        logger.info("=" * 60)
    
    def notify(self, title, message):
        """Send desktop notification."""
        try:
            os.system(f'notify-send "{title}" "{message}" 2>/dev/null &')
        except:
            pass
    
    def start_recording(self):
        """Start voice recording."""
        if self.is_recording:
            logger.warning("Recording start requested but already recording")
            return "ALREADY_RECORDING"
        
        logger.info("Recording started")
        self.is_recording = True
        print("🎤 Recording started...")
        # self.notify("AnyWhisper", "🎤 Recording... Speak now!")
        
        success = self.recorder.start_recording()
        if not success:
            logger.error("Failed to start audio recorder")
            self.is_recording = False
            print("❌ Failed to start recording")
            self.notify("AnyWhisper", "❌ Failed to start recording")
            return "ERROR"
        
        logger.debug("Audio recorder started successfully")
        # Start monitoring thread to detect when recording stops automatically
        threading.Thread(target=self._monitor_recording, daemon=True).start()
        logger.debug("Recording monitor thread started")
        
        return "RECORDING"
    
    def stop_recording(self):
        """Stop recording and process audio."""
        if not self.is_recording:
            logger.warning("Stop recording requested but not currently recording")
            return "NOT_RECORDING"
        
        logger.info("Stopping recording...")
        print("⏹️  Stopping recording...")
        # self.notify("AnyWhisper", "⏹️ Processing...")
        
        # Stop recording and get the audio file
        audio_file = self.recorder.stop_recording()
        self.is_recording = False
        
        if not audio_file:
            logger.warning("No audio recorded - recorder returned None")
            print("❌ No audio recorded")
            self.notify("AnyWhisper", "❌ No audio recorded")
            return "NO_AUDIO"
        
        logger.info(f"Audio file saved: {audio_file}")
        # Transcribe in a separate thread to not block
        threading.Thread(target=self._process_audio, args=(audio_file,), daemon=True).start()
        logger.debug("Audio processing thread started")
        return "PROCESSING"
    
    def toggle_recording(self):
        """Toggle recording on/off."""
        if self.is_recording:
            return self.stop_recording()
        else:
            return self.start_recording()
    
    def _process_with_ai(self, text, template_name):
        """
        Process text with AI using the specified template.
        
        Args:
            text (str): The text to process
            template_name (str): Name of the template from AI_PROMPT_TEMPLATES
            
        Returns:
            str: AI-processed text, or original text if processing fails
        """
        logger.info(f"AI processing started: template={template_name}, input_length={len(text)}")
        
        if not ENABLE_AI_PROCESSING:
            logger.debug("AI Processing is disabled")
            return text
        
        if not AI_API_KEY:
            logger.warning("AI_API_KEY not configured")
            print("⚠️  AI_API_KEY not configured, skipping AI processing")
            return text
        
        template = AI_PROMPT_TEMPLATES.get(template_name)
        if not template:
            logger.error(f"AI template '{template_name}' not found in AI_PROMPT_TEMPLATES")
            print(f"⚠️  Template '{template_name}' not found")
            return text
        
        try:
            from litellm import completion
        except ImportError:
            logger.error("litellm library not installed")
            print("⚠️  litellm library not installed. Install with: pip install litellm")
            return text
        
        try:
            # Set API key as environment variable for litellm
            env_var_name = f"{AI_PROVIDER.upper()}_API_KEY"
            os.environ[env_var_name] = AI_API_KEY
            
            # Construct model name with provider prefix
            full_model_name = f"{AI_PROVIDER}/{AI_MODEL_NAME}"
            logger.debug(f"Calling AI API: model={full_model_name}, provider={AI_PROVIDER}")
            print(f"🤖 Processing with AI ({full_model_name})...")
            
            # Replace placeholder with actual user input
            messages = []
            for msg in template:
                message = {
                    "role": msg["role"],
                    "content": msg["content"].replace("__USER_INPUT__", text)
                }
                messages.append(message)
            
            logger.debug(f"AI messages prepared: {len(messages)} messages")
            
            # Call LiteLLM completion API
            response = completion(
                model=full_model_name,
                messages=messages
            )
            
            ai_output = response.choices[0].message.content.strip()
            logger.info(f"AI processing successful: output_length={len(ai_output)}")
            logger.debug(f"AI full output: '{ai_output}'")
            print(f"✅ AI processed: {ai_output[:100]}{'...' if len(ai_output) > 100 else ''}")
            return ai_output

        except Exception as e:
            logger.error(f"AI processing failed: {type(e).__name__}: {e}", exc_info=True)
            print(f"⚠️  AI processing failed: {e}")
            return text
    
    def _monitor_recording(self):
        """Monitor the recording and auto-process when it stops."""
        import time
        
        logger.debug("Recording monitor: watching for automatic stop")
        
        # Wait while recording is active
        while self.is_recording and self.recorder.is_recording:
            time.sleep(0.2)
        
        # Give a small delay to ensure recording thread fully completes
        time.sleep(0.3)
        
        # Check if recording stopped automatically (not manually)
        # The daemon still thinks it's recording, but recorder has stopped
        if self.is_recording and not self.recorder.is_recording:
            logger.info("Recording stopped automatically (silence detected)")
            print("🔔 Recording stopped automatically (silence detected)")
            # Trigger the normal stop process
            self.stop_recording()
    
    def _process_audio(self, audio_file):
        """Process audio file (transcribe and inject text)."""
        logger.info("Starting audio transcription...")
        print("🔄 Transcribing audio...")
        text = self.api_client.transcribe_audio(audio_file)
        
        if text:
            logger.info(f"Raw transcription: '{text}'")
            print(f"✅ Transcription: {text}")
            # self.notify("AnyWhisper", f"📝 {text[:50]}{'...' if len(text) > 50 else ''}")
            
            # Check for post-transcription actions (if enabled)
            post_action = None
            cleaned_text = text
            matched_pattern = None
            
            if ENABLE_TRANSCRIPTION_ACTIONS:
                logger.debug("Checking POST_TRANSCRIPTION_ACTIONS...")
                for pattern, action in POST_TRANSCRIPTION_ACTIONS.items():
                    # Optionally add \.? before $ to handle periods Whisper may add
                    modified_pattern = pattern
                    if POST_TRANSCRIPTION_OPT_DOT and pattern.endswith('$'):
                        # Insert \.? before the $
                        modified_pattern = pattern[:-1] + r'\.?$'
                    
                    # Check if pattern matches (case-insensitive)
                    match = re.search(modified_pattern, text, re.IGNORECASE)
                    if match:
                        logger.info(f"POST_TRANSCRIPTION_ACTIONS triggered: pattern='{pattern}' → action={action}")
                        print(f"🎯 Pattern matched: '{pattern}' → Action: {action}")
                        post_action = action
                        matched_pattern = modified_pattern
                        # Remove the matched pattern from text
                        cleaned_text = re.sub(modified_pattern, '', text, flags=re.IGNORECASE).strip()
                        logger.debug(f"Text after removing pattern: '{cleaned_text}'")
                        break
                
                if not post_action:
                    logger.debug("No POST_TRANSCRIPTION_ACTIONS pattern matched")
            else:
                logger.debug("POST_TRANSCRIPTION_ACTIONS is disabled")
            
            # Process with AI if enabled and triggered
            ai_template = None
            final_text = cleaned_text if post_action else text
            
            if ENABLE_AI_PROCESSING and AI_API_KEY:
                logger.debug("Checking POST_AI_TRIGGERS...")
                for pattern, template in POST_AI_TRIGGERS.items():
                    # Optionally add \.? before $ to handle periods
                    modified_pattern = pattern
                    if POST_TRANSCRIPTION_OPT_DOT and pattern.endswith('$'):
                        modified_pattern = pattern[:-1] + r'\.?$'
                    
                    # Check if AI trigger pattern matches
                    match = re.search(modified_pattern, final_text, re.IGNORECASE)
                    if match:
                        logger.info(f"POST_AI_TRIGGERS matched: pattern='{pattern}' → template={template}")
                        print(f"🎯 AI trigger matched: '{pattern}' → Template: {template}")
                        ai_template = template
                        # Remove the AI trigger phrase from text
                        final_text = re.sub(modified_pattern, '', final_text, flags=re.IGNORECASE).strip()
                        logger.debug(f"Text after removing AI trigger: '{final_text}'")
                        break
                
                if not ai_template:
                    logger.debug("No POST_AI_TRIGGERS pattern matched")
            else:
                if not ENABLE_AI_PROCESSING:
                    logger.debug("AI Processing is disabled")
                elif not AI_API_KEY:
                    logger.debug("AI Processing enabled but no API key configured")
            
            # Process with AI if triggered
            if ai_template:
                logger.info(f"Processing with AI using template: {ai_template}")
                final_text = self._process_with_ai(final_text, ai_template)
                logger.info(f"AI output: '{final_text}'")
            else:
                logger.debug("No AI processing triggered")
            
            # Inject the text (after all processing)
            if final_text:  # Only inject if there's text left after all processing
                logger.info(f"Injecting text: '{final_text}' (length={len(final_text)})")
                if config.USE_COPY_PASTE_METHOD:
                    logger.info("Using clipboard paste method")
                else:
                    logger.info("Using character-by-character typing method")
                if post_action:
                    logger.info(f"Will execute post-action after text injection: {post_action}")
                print(f"⌨️  Injecting text: {final_text}")
                success = self.text_injector.inject_text(final_text, post_action=post_action)
                
                if success:
                    logger.info("Text injection successful")
                else:
                    logger.warning("Text injection failed, falling back to clipboard")
                    print("⚠️  Falling back to clipboard...")
                    self.text_injector.copy_to_clipboard(final_text)
                    self.notify("AnyWhisper", "📋 Copied to clipboard (Ctrl+V to paste)")
            elif post_action:
                # No text to type, just execute the action
                logger.info(f"Executing key action only (no text): {post_action}")
                print(f"⌨️  Executing action: {post_action}")
                self.text_injector._execute_key_action(post_action)
            else:
                logger.warning("No final text to inject and no post-action to execute")
        else:
            logger.error("Transcription failed - no text returned from API")
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
            logger.debug(f"Received command: '{data}'")
            
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
                logger.warning(f"Unknown command received: '{data}'")
                response = "UNKNOWN_COMMAND"
            
            client_socket.send(response.encode('utf-8'))
            logger.debug(f"Sent response: '{response}'")
        except Exception as e:
            logger.error(f"Error handling client: {e}", exc_info=True)
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    def start_ydotoold_if_needed(self):
        """Start ydotoold if on Wayland and not already running."""
        if self.text_injector.method != 'wayland':
            logger.debug("Not on Wayland, skipping ydotoold start")
            return
        
        logger.info("Checking ydotoold status (Wayland mode)")
        # Check if ydotoold is already running
        try:
            result = os.popen('pgrep -x ydotoold').read().strip()
            if result:
                logger.info("ydotoold already running")
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
                logger.info(f"Starting local ydotoold from: {ydotoold_path}")
                self.ydotoold_process = subprocess.Popen([ydotoold_path])
                import time
                time.sleep(1)
                logger.info("Local ydotoold daemon started successfully")
                print("✓ Started local ydotoold daemon")
            except Exception as e:
                logger.error(f"Could not start ydotoold: {e}")
                print(f"⚠️  Could not start ydotoold: {e}")
    
    def start(self):
        """Start the daemon."""
        logger.info("Starting daemon...")
        # Start ydotoold if needed (Wayland only)
        self.start_ydotoold_if_needed()
        
        # Remove old socket if it exists
        try:
            os.unlink(SOCKET_PATH)
            logger.debug(f"Removed old socket: {SOCKET_PATH}")
        except OSError:
            if os.path.exists(SOCKET_PATH):
                raise
        
        # Create Unix socket
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(SOCKET_PATH)
        self.socket.listen(5)
        
        # Make socket accessible
        os.chmod(SOCKET_PATH, 0o666)
        logger.info(f"Unix socket created and listening: {SOCKET_PATH}")
        logger.info(f"Display server: {self.text_injector.method}")
        
        print("=" * 60)
        print("AnyWhisper Daemon Started")
        print("=" * 60)
        print(f"Socket: {SOCKET_PATH}")
        print(f"Display server: {self.text_injector.method}")
        
        # Check API health
        print("\n🔍 Checking Whisper API...")
        logger.info("Checking Whisper API health...")
        if self.api_client.check_api_health():
            logger.info("Whisper API is accessible")
            print("✅ Whisper API is accessible")
        else:
            logger.warning("Cannot reach Whisper API")
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
        logger.info("Daemon ready, accepting connections...")
        while self.running:
            try:
                self.socket.settimeout(1.0)
                try:
                    client, _ = self.socket.accept()
                    logger.debug("Client connected")
                    threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()
                except socket.timeout:
                    continue
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                if self.running:
                    logger.error(f"Error in main loop: {e}", exc_info=True)
                    print(f"Error: {e}")
        
        self.shutdown(None, None)
    
    def shutdown(self, signum, frame):
        """Shutdown the daemon."""
        if not self.running:
            return
        
        logger.info("Shutdown initiated")
        print("\n\n👋 Shutting down...")
        self.running = False
        
        if self.is_recording:
            logger.info("Stopping active recording...")
            self.recorder.stop_recording()
        
        if self.socket:
            self.socket.close()
            logger.debug("Socket closed")
        
        try:
            os.unlink(SOCKET_PATH)
            logger.debug(f"Removed socket: {SOCKET_PATH}")
        except:
            pass
        
        # Stop ydotoold if we started it
        if self.ydotoold_process:
            try:
                logger.info("Stopping ydotoold process...")
                self.ydotoold_process.terminate()
                self.ydotoold_process.wait(timeout=5)
                logger.info("ydotoold stopped successfully")
                print("Stopped ydotoold daemon")
            except:
                logger.warning("ydotoold did not stop gracefully")
                pass
        
        logger.info("AnyWhisper Daemon stopped")
        logger.info("=" * 60)
        print("Daemon stopped.")
        sys.exit(0)


def main():
    """Main entry point."""
    daemon = VoiceDaemon()
    daemon.start()


if __name__ == "__main__":
    main()

