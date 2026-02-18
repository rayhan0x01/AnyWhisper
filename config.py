"""Configuration settings for the AnyWhisper application."""

import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('USER')


def _bool(val):
    """Parse a boolean from an environment variable string."""
    return val.lower() in ("true", "1", "yes")


# Whisper API settings
WHISPER_API_URL = os.getenv("WHISPER_API_URL", "http://localhost:4444/v1/audio/transcriptions")

# Audio recording settings
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))
CHANNELS = int(os.getenv("CHANNELS", "1"))
AUDIO_FORMAT = os.getenv("AUDIO_FORMAT", "wav")

# Recording behavior
MAX_RECORDING_DURATION = int(os.getenv("MAX_RECORDING_DURATION", "240"))
SILENCE_THRESHOLD = float(os.getenv("SILENCE_THRESHOLD", "0.01"))
SILENCE_DURATION = float(os.getenv("SILENCE_DURATION", "4.0"))

# Temp file settings
TEMP_AUDIO_FILE = f"/tmp/{username}_whisper_recording.wav"

# Notification settings
ENABLE_NOTIFICATIONS = _bool(os.getenv("ENABLE_NOTIFICATIONS", "true"))

# Text injection method
USE_COPY_PASTE_METHOD = _bool(os.getenv("USE_COPY_PASTE_METHOD", "true"))

# Logging settings
LOG_FILE = f"/tmp/{username}_anywhisper.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Post-transcription key actions
ENABLE_TRANSCRIPTION_ACTIONS = _bool(os.getenv("ENABLE_TRANSCRIPTION_ACTIONS", "true"))

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

POST_TRANSCRIPTION_OPT_DOT = _bool(os.getenv("POST_TRANSCRIPTION_OPT_DOT", "true"))

# ydotool key codes for common keys
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

# AI Processing Configuration
ENABLE_AI_PROCESSING = _bool(os.getenv("ENABLE_AI_PROCESSING", "true"))

AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "gemini-2.5-flash-lite")

# Post-AI Processing Triggers
POST_AI_TRIGGERS = {
    r'whisper with ai': 'GEN_AI_TEMPLATE',
    r'generate this as prompt': 'ENHANCE_PROMPT_TEMPLATE',
    r'generate as command': 'COMMAND_GENERATION_TEMPLATE',
    r'extend the vibe': 'VIBE_EXTEND_TEMPLATE',
}

# AI Prompt Templates
AI_PROMPT_TEMPLATES = {
    'GEN_AI_TEMPLATE': [
        {"role": "system", "content": "You are a helpful AI writing assistant. Complete the user's generation request without any preamble, explanations, or meta-commentary."},
        {"role": "user", "content": "__USER_INPUT__"}
    ],
    'ENHANCE_PROMPT_TEMPLATE': [
        {"role": "system", "content": "You are an expert prompt engineer. Transform the user's brief input into a clear, concise, and actionable prompt. Only expand if necessary. This is a voice-to-text input so correct spelling and grammar when needed. Return only the enhanced prompt without any preamble, explanations, or meta-commentary."},
        {"role": "user", "content": "__USER_INPUT__"}
    ],
    'COMMAND_GENERATION_TEMPLATE': [
        {"role": "system", "content": "You are a bash command generator. Convert the user's request into a valid bash command. Return ONLY the command, no explanations or markdown."},
        {"role": "user", "content": "Generate a bash command for: __USER_INPUT__"}
    ],
    'VIBE_EXTEND_TEMPLATE': [
        {"role": "system", "content": "You are assisting with VibeCoding - a conversational AI-assisted coding workflow. The user is giving brief instructions to their AI coding assistant. Transform their concise input into a detailed, actionable prompt that provides context, specifies requirements, mentions best practices, and clearly defines the expected outcome. Make it developer-friendly and ready for an AI coding assistant to act upon. Return only the expanded prompt."},
        {"role": "user", "content": "__USER_INPUT__"}
    ],
}

# Daemon socket path
SOCKET_PATH = os.getenv("SOCKET_PATH", "/tmp/voice_to_text.sock")
