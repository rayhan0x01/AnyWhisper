# get username
import os
username = os.getenv('USER')

"""Configuration settings for the AnyWhisper application."""

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

# Post-transcription key actions
# Enable/disable post-transcription action processing
ENABLE_TRANSCRIPTION_ACTIONS = True

# Regex patterns to match against transcription text
# If pattern matches, the corresponding key action will be executed after typing
POST_TRANSCRIPTION_ACTIONS = {
    r'hit enter$': 'ENTER',
    r'^enter$': 'ENTER',
    r'press enter$': 'ENTER',
    r'new line$': 'ENTER',
    r'hit tab$': 'TAB',
    r'press tab$': 'TAB',
    r'hit escape$': 'ESCAPE',
    r'press escape$': 'ESCAPE',
}

# Auto-handle optional period at end of transcription
# Whisper sometimes adds a period to complete sentences
# If True, patterns ending with $ will also match an optional period (\.?)
# Example: "hit enter$" will match both "hit enter" and "hit enter."
POST_TRANSCRIPTION_OPT_DOT = True

# ydotool key codes for common keys
# Format: keycode:1 keycode:0 (press and release)
YDOTOOL_KEY_CODES = {
    'ENTER': '28:1 28:0',
    'ESCAPE': '1:1 1:0',
    'ESC': '1:1 1:0',
    'TAB': '15:1 15:0',
    'BACKSPACE': '14:1 14:0',
    'SPACE': '57:1 57:0',
    'UP': '103:1 103:0',
    'DOWN': '108:1 108:0',
    'LEFT': '105:1 105:0',
    'RIGHT': '106:1 106:0',
    'HOME': '102:1 102:0',
    'END': '107:1 107:0',
    'PAGEUP': '104:1 104:0',
    'PAGEDOWN': '109:1 109:0',
    'DELETE': '111:1 111:0',
    'INSERT': '110:1 110:0',
}

