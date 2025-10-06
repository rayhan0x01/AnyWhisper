# AnyWhisper Quick Start Guide

## TL;DR

```bash
# 1. Install (one-time)
./setup.sh

# 2. Start daemon
./start_daemon.sh
# Or use systemd: ./setup_autostart.sh

# 3. Set up keyboard shortcut in your Desktop Environment:
#    Command: /path/to/AnyWhisper/voice_trigger.py
#    Shortcut: Ctrl+Shift+Space (or whatever you prefer)

# 4. Press shortcut → speak → press again → text appears!
```

## How It Works

### The Daemon (Background Service)

- **`voice_daemon.py`** runs in the background
- Listens on a Unix socket at `/tmp/voice_to_text.sock`
- Handles recording, transcription, and text injection

### The Trigger (What Your Shortcut Runs)

- **`voice_trigger.py`** is a lightweight script
- Sends `TOGGLE` command to the daemon
- Returns immediately (no blocking)

### Your Global Shortcut

- Set in GNOME/KDE settings
- Runs `voice_trigger.py` when pressed
- **Works anywhere in the OS**

## Setup Global Shortcut (GNOME)

1. Press `Super` key and type "Keyboard"
2. Open **Settings** → **Keyboard** → **Keyboard Shortcuts**
3. Scroll to bottom, click **"View and Customize Shortcuts"**
4. Click **"Custom Shortcuts"**
5. Click the **+** button
6. Fill in:
   - Name: `AnyWhisper`
   - Command: `/path/to/AnyWhisper/voice_trigger.py`
   - Shortcut: Press your desired keys (e.g., `Ctrl+Shift+Space`)
7. Click **Add**

## Testing

```bash
# Test if daemon is running
./voice_trigger.py PING
# Expected: Response: PONG

# Test recording manually
./voice_trigger.py START
# Speak something...
./voice_trigger.py STOP
# Text should appear in focused application

# Check daemon status
./voice_trigger.py STATUS
```

## Daemon Management

### Manual Start (for testing)

```bash
./start_daemon.sh
# Keep terminal open, daemon runs in foreground
# Press Ctrl+C to stop
```

### Systemd Service (recommended)

```bash
# Setup (one-time)
./setup_autostart.sh

# Control
systemctl --user start any-whisper    # Start
systemctl --user stop any-whisper     # Stop  
systemctl --user status any-whisper   # Check status
systemctl --user enable any-whisper   # Auto-start on login
systemctl --user disable any-whisper  # Disable auto-start

# View logs
journalctl --user -u any-whisper -f
```

## Usage Flow

```
┌─────────────────────────────────────────────────────┐
│ 1. Press Global Shortcut (Ctrl+Shift+Space)         │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 2. voice_trigger.py sends "TOGGLE" to daemon        │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 3. Daemon starts recording                          │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 4. You speak into your microphone                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 5. Press shortcut again OR wait for silence         │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 6. Daemon stops recording, sends to Whisper API     │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 7. Text is transcribed and injected into active app │
└─────────────────────────────────────────────────────┘
```

## Troubleshooting

### "Daemon not running" error

```bash
# Check if daemon is running
ps aux | grep voice_daemon

# Start it
./start_daemon.sh
# or
systemctl --user start any-whisper
```

### Global shortcut doesn't trigger

- Make sure `voice_trigger.py` is executable: `chmod +x voice_trigger.py`
- Use absolute path in Desktop Environment settings: `/path/to/AnyWhisper/voice_trigger.py`
- Test manually: `./voice_trigger.py PING`

### Text not being typed (Wayland)

The setup script automatically downloads `ydotool` and `ydotoold` binaries. The daemon starts `ydotoold` automatically when needed.

If text injection still doesn't work, text will be copied to clipboard. Paste with `Ctrl+V`.

### Whisper API not responding

```bash
# Check if Docker container is running
docker ps | grep whisper-assistant

# Start it if not running
docker run -d -p 127.0.0.1:4444:4444 --name whisper-assistant whisper-assistant

# Check logs
docker logs whisper-assistant
```

## Configuration

Edit `/path/to/AnyWhisper/config.py`:

```python
# Maximum recording duration
MAX_RECORDING_DURATION = 240  # seconds

# Silence detection
SILENCE_THRESHOLD = 0.01  # 0.0 to 1.0 (higher = more sensitive)
SILENCE_DURATION = 2.0    # seconds of silence before auto-stop

# Post-transcription actions
ENABLE_TRANSCRIPTION_ACTIONS = True  # Enable/disable this feature

POST_TRANSCRIPTION_ACTIONS = {
    r'hit enter$': 'ENTER',     # Auto-press ENTER after typing
    r'press tab$': 'TAB',       # Auto-press TAB after typing
}

# Handle periods Whisper adds at end
POST_TRANSCRIPTION_OPT_DOT = True  # Matches "hit enter" and "hit enter."

# API endpoint
WHISPER_API_URL = "http://localhost:4444/v1/audio/transcriptions"
```

**Pro Tip:** Say "send message hit enter" to type "send message" and press ENTER!
**Note:** Works even if Whisper adds a period: "send message hit enter."

See [POST_TRANSCRIPTION_ACTIONS.md](POST_TRANSCRIPTION_ACTIONS.md) for more details.

### AI Processing (Optional)

Enhance transcriptions with AI (supports 100+ providers via LiteLLM):

```python
ENABLE_AI_PROCESSING = True
AI_API_KEY = "your-api-key"
AI_PROVIDER = 'gemini'  # Options: gemini, openai, anthropic, groq, etc.
AI_MODEL_NAME = 'gemini-2.5-flash-lite'
```

**Usage:** Say "create login page, generate this as prompt, hit enter"

See [AI_PROCESSING.md](AI_PROCESSING.md) for setup guide.

### Fast Text Injection (Optional)

For large AI outputs, use clipboard paste instead of typing:

```python
USE_COPY_PASTE_METHOD = True  # Instant paste via Shift+Insert (fast!)
```

**Why use it:**
- AI responses are often 100+ words
- Clipboard paste is instant regardless of length
- Character-by-character typing can take 5-10 seconds for long text
- Preserves your existing clipboard content automatically

After changing config, restart daemon:
```bash
systemctl --user restart any-whisper
```

## Advanced Usage

### Different Shortcuts for Start/Stop

Instead of toggle, use separate shortcuts:

**Start Recording Shortcut:**
- Command: `/path/to/AnyWhisper/voice_trigger.py START`
- Shortcut: `Ctrl+Shift+R`

**Stop Recording Shortcut:**
- Command: `/path/to/AnyWhisper/voice_trigger.py STOP`
- Shortcut: `Ctrl+Shift+S`

### Check Recording Status

```bash
./voice_trigger.py STATUS
```

Outputs: `IDLE` or `RECORDING`

## System Requirements

- Ubuntu 20.04+ (or Debian-based distro)
- Python 3.8+
- Wayland or X11
- Whisper API (Docker)
- `ydotool` (Wayland) or `xdotool` (X11) for text injection

## Support

- **[WAYLAND_SETUP.md](WAYLAND_SETUP.md)** - Complete Wayland setup guide


