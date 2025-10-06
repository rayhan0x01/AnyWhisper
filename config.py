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

# Text injection method
# If True, uses clipboard + Shift+Insert (faster for large text)
# If False, types character by character (more compatible)
USE_COPY_PASTE_METHOD = True

# Logging settings
LOG_FILE = f"/tmp/{username}_anywhisper.log"  # Log file location
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

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

# AI Processing Configuration
# Enable/disable AI enhancement processing
ENABLE_AI_PROCESSING = True

# LiteLLM API configuration
# Supports multiple LLM providers (Gemini, OpenAI, Anthropic, etc.)
AI_API_KEY = ""

# Provider name (gemini, openai, anthropic, etc.)
AI_PROVIDER = 'gemini'  # Options: gemini, openai, anthropic, groq, etc.

# Model name (without provider prefix)
# Google: 'gemini-2.5-flash-lite', 'gemini-2.0-flash-exp'
# OpenAI: 'gpt-4o', 'gpt-4o-mini'
# Anthropic: 'claude-sonnet-4-20250514', 'claude-3-5-sonnet-20241022'
AI_MODEL_NAME = 'gemini-2.5-flash-lite'

# Post-AI Processing Triggers
# Regex patterns that trigger AI processing
# If pattern matches, the corresponding template will be used to process the text
POST_AI_TRIGGERS = {
    r'whisper with ai': 'GEN_AI_TEMPLATE',
    r'generate this as prompt': 'ENHANCE_PROMPT_TEMPLATE',
    r'generate as command': 'COMMAND_GENERATION_TEMPLATE',
    r'extend the vibe': 'VIBE_EXTEND_TEMPLATE',
}

# AI Prompt Templates
# Library of templates with placeholders for user input
# Use __USER_INPUT__ as placeholder for the transcribed text
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

