# get username
import os
username = os.getenv('USER')

"""Configuration settings for the Voice-to-Text application."""

# Whisper API settings
WHISPER_API_URL = "http://localhost:4444/v1/audio/transcriptions"

# Audio recording settings
SAMPLE_RATE = 16000  # Sample rate in Hz (Whisper works best with 16kHz)
CHANNELS = 1  # Mono audio
AUDIO_FORMAT = 'wav'  # Audio file format

# Recording behavior
MAX_RECORDING_DURATION = 240  # Maximum recording duration in seconds
SILENCE_THRESHOLD = 0.01  # Silence detection threshold (0.0 to 1.0)
SILENCE_DURATION = 2.0  # Duration of silence to stop recording (seconds)

# Temp file settings
TEMP_AUDIO_FILE = f"/tmp/{username}_whisper_recording.wav"

# Notification settings
ENABLE_NOTIFICATIONS = True  # Show desktop notifications (requires notify-send)

