"""Audio recording component for any-whisper application."""

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import threading
import time
from config import (
    SAMPLE_RATE,
    CHANNELS,
    MAX_RECORDING_DURATION,
    SILENCE_THRESHOLD,
    SILENCE_DURATION,
    TEMP_AUDIO_FILE
)


class AudioRecorder:
    """Records audio from the microphone with silence detection."""
    
    def __init__(self):
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = SAMPLE_RATE
        self.channels = CHANNELS
        self.recording_thread = None
        
    def start_recording(self):
        """Start recording audio from the microphone."""
        if self.is_recording:
            print("Already recording!")
            return False
        
        self.is_recording = True
        self.audio_data = []
        self.recording_thread = threading.Thread(target=self._record)
        self.recording_thread.start()
        return True
    
    def stop_recording(self):
        """Stop recording and save the audio file."""
        # Set flag to false to stop the recording loop
        self.is_recording = False
        
        # Wait for recording thread to finish
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=5)
        
        # Check if we have audio data (even if recording already stopped)
        if len(self.audio_data) == 0:
            print("No audio data recorded.")
            return None
        
        # Combine all audio chunks
        audio_array = np.concatenate(self.audio_data, axis=0)
        
        # Save to WAV file
        wavfile.write(TEMP_AUDIO_FILE, self.sample_rate, audio_array)
        print(f"Audio saved to {TEMP_AUDIO_FILE}")
        
        # Clear audio data for next recording
        self.audio_data = []
        
        return TEMP_AUDIO_FILE
    
    def _record(self):
        """Internal method to record audio with silence detection."""
        print("Recording started...")
        silence_start = None
        start_time = time.time()
        
        def callback(indata, frames, time_info, status):
            """Called by sounddevice for each audio block."""
            if status:
                print(f"Status: {status}")
            
            # Calculate audio level (RMS)
            audio_level = np.sqrt(np.mean(indata**2))
            
            # Store audio data
            self.audio_data.append(indata.copy())
        
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=callback,
                dtype='float32'
            ):
                last_check = time.time()
                while self.is_recording:
                    current_time = time.time()
                    
                    # Check if max duration exceeded
                    if current_time - start_time > MAX_RECORDING_DURATION:
                        print("Max recording duration reached.")
                        break
                    
                    # Check silence detection every 0.1 seconds
                    if current_time - last_check > 0.1:
                        if len(self.audio_data) > 0:
                            # Get recent audio for silence detection
                            recent_audio = self.audio_data[-10:]  # Last ~1 second
                            if len(recent_audio) > 0:
                                recent_array = np.concatenate(recent_audio, axis=0)
                                audio_level = np.sqrt(np.mean(recent_array**2))
                                
                                # Detect silence
                                if audio_level < SILENCE_THRESHOLD:
                                    if silence_start is None:
                                        silence_start = current_time
                                    elif current_time - silence_start > SILENCE_DURATION:
                                        print("Silence detected, stopping recording.")
                                        break
                                else:
                                    silence_start = None
                        
                        last_check = current_time
                    
                    time.sleep(0.1)
        
        except Exception as e:
            print(f"Error during recording: {e}")
        finally:
            self.is_recording = False
            print("Recording stopped.")


if __name__ == "__main__":
    # Test the audio recorder
    recorder = AudioRecorder()
    
    print("Starting recording... (Press Ctrl+C to stop manually)")
    recorder.start_recording()
    
    try:
        # Wait for recording to finish (either by silence or max duration)
        while recorder.is_recording:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping...")
    
    audio_file = recorder.stop_recording()
    if audio_file:
        print(f"Recording saved to: {audio_file}")

