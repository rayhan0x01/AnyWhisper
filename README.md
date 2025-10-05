# AnyWhisper

A seamless voice-to-text application that uses OpenAI's Whisper model (locally) for high-quality speech recognition and types your words into any application.

1. Select an input field and press a keyboard shortcut,
2. Speak,
3. and have your words automatically typed into the input field.

## Inspiration

A VibeCoded project that makes VibeCoding even easier by allowing us to speak our prompts everywhere instead of typing them.

## Features

- 📴 **Fully Offline Transcription**: Your data stays on your device.
- 🌍 **True Global Shortcuts**: Use native OS shortcuts to trigger recording
- 🎤 **Press-to-Talk**: Toggle recording with a keyboard shortcut
- 🤖 **High-Quality Transcription**: Uses [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) for accurate speech-to-text
- ⌨️ **Universal Text Injection**: Works with any application (browser, CLI, IDEs, etc.)
- 🔇 **Automatic Silence Detection**: Stops recording after detecting silence
- 🖥️ **Display Server Support**: Works with both X11 and Wayland
- 📋 **Clipboard Fallback**: Copies to clipboard if text injection fails
- 🔑 **Post-Transcription Actions**: Press pre-defined keys after transcription based on spoken phrases (like hit enter, press tab, etc.)
- 🔧 **Systemd Integration**: Run as a background service with auto-start

## Prerequisites

- Ubuntu 20.04 or later (Other Debian-based distributions may work too)
- Python 3.8 or higher
- Docker (for running the OpenAI Whisper Model locally)
- Microphone

## Installation

### 1. Set up the Whisper API

First, build and run the Whisper Docker container:

```bash
# Build the Docker image
docker build -t whisper-assistant .

# Run the container
docker run -d -p 127.0.0.1:4444:4444 --name whisper-assistant whisper-assistant
```

**Note**: The current Whisper model is from [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper). The model size is set to `small`, which is a 244M parameter model. It's set to run on the CPU so no GPU is needed. You can change the model size by editing the `WHISPER_MODEL_SIZE` environment variable in the `Dockerfile` and running `docker build -t whisper-assistant .` again.


### 2. Install the AnyWhisper Application

Run the setup script:

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Install required system packages (xdotool, portaudio, etc.)
- Create a Python virtual environment
- Install Python dependencies

## Usage

### Quick Start (Wayland - Recommended)

**For Wayland users with true OS-level global shortcuts**, see the detailed guide:

📖 **[WAYLAND_SETUP.md](WAYLAND_SETUP.md)** - Complete setup instructions

Quick summary:
```bash
# 1. Setup autostart
./setup_autostart.sh

# 2. Bind global shortcut in your Desktop Environment settings to:
#    /path/to/AnyWhisper/voice_trigger.py

# 3. Press your shortcut anywhere to start recording!
```

### Alternative: Manual Mode (X11)

For X11 users or manual testing:

1. Make sure the Whisper Docker container is running:
   ```bash
   docker ps | grep whisper-assistant
   ```

2. Start the daemon:
   ```bash
   source venv/bin/activate
   python voice_daemon.py
   ```

3. In another terminal, trigger recording:
   ```bash
   ./voice_trigger.py
   ```

### Using AnyWhisper

1. **Press** the keyboard shortcut (triggers recording)
2. **Speak** your text clearly
3. **Press** the shortcut again to stop (or wait for silence detection)
4. The text will be automatically typed into the currently focused application

## Configuration

Edit `config.py` to customize the application:

### Audio Settings

```python
SAMPLE_RATE = 16000  # Sample rate in Hz
MAX_RECORDING_DURATION = 240  # Maximum recording duration in seconds
SILENCE_THRESHOLD = 0.01  # Silence detection sensitivity (0.0 to 1.0)
SILENCE_DURATION = 2.0  # Duration of silence before stopping (seconds)
```

### Post-Transcription Actions

Automatically press keys after transcription based on spoken patterns:

```python
# Enable/disable post-transcription actions
ENABLE_TRANSCRIPTION_ACTIONS = True  # Set to False to disable this feature

POST_TRANSCRIPTION_ACTIONS = {
    r'hit enter$': 'ENTER',     # "send a message hit enter" → types text + presses ENTER
    r'press tab$': 'TAB',       # "john@example.com press tab" → types email + presses TAB
    r'^enter$': 'ENTER',        # Just say "enter" → presses ENTER only
}

# Auto-handle periods that Whisper adds at the end
POST_TRANSCRIPTION_OPT_DOT = True  # Makes patterns flexible to match with/without period
```

**Example:** Say "git commit -m 'update' hit enter"
- Transcription: "git commit -m 'update' hit enter." (Whisper may add period)
- Types: `git commit -m 'update'`
- Presses: ENTER

See **[POST_TRANSCRIPTION_ACTIONS.md](POST_TRANSCRIPTION_ACTIONS.md)** for detailed documentation.

### API Endpoint

If you're running the Whisper API on a different host or port:

```python
WHISPER_API_URL = "http://localhost:4444/v1/audio/transcriptions"
```

## Running as a System Service (Optional)

To run the application automatically on startup, create a systemd service by running:

```bash
./setup_autostart.sh
```

This will create a systemd service file and start the daemon automatically on startup.

## Troubleshooting

### Whisper API Not Responding

Make sure the Docker container is running:
```bash
docker ps | grep whisper-assistant
```

If not running, start it:
```bash
docker start whisper-assistant
```

### No Audio Recording

Check if your microphone is detected:
```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### Text Not Being Injected

**For X11:**
- Make sure `xdotool` is installed: `sudo apt install xdotool`

**For Wayland:**
- The setup script automatically downloads `ydotool` and `ydotoold` binaries
- The daemon starts `ydotoold` automatically when needed
- Binaries are from [ydotool releases v1.0.4](https://github.com/ReimuNotMoe/ydotool/releases/tag/v1.0.4)

**Fallback:**
If text injection fails, the text will be copied to your clipboard. Just paste it with `Ctrl+V`.

### Permission Issues (Wayland + ydotool)

The setup script automatically downloads `ydotool` and `ydotoold` binaries from the [official releases](https://github.com/ReimuNotMoe/ydotool/releases/tag/v1.0.4). The daemon starts `ydotoold` automatically.

If you encounter permission issues:
```bash
sudo chmod 666 /dev/uinput
```

### Module Import Errors

Make sure you're in the virtual environment:
```bash
source venv/bin/activate
```

## Testing Individual Components

### Test Audio Recording

```bash
python audio_recorder.py
# Speak for a few seconds, then check /tmp/whisper_recording.wav
```

### Test API Client

```bash
# Record an audio file first, then:
python api_client.py /tmp/whisper_recording.wav
```

### Test Text Injection

```bash
# Open a text editor, then run:
python text_injector.py "Hello, this is a test"
# The text should appear in the focused application after 3 seconds
```

## Architecture

The application uses a **daemon + trigger** architecture for true global shortcuts:

1. **Whisper Docker API** (`Dockerfile`): Self-hosted Whisper transcription service
2. **Voice Daemon** (`voice_daemon.py`): Background service that handles recording and transcription
3. **Trigger Script** (`voice_trigger.py`): Lightweight script bound to global keyboard shortcut
4. **Audio Recorder** (`audio_recorder.py`): Records audio with silence detection
5. **API Client** (`api_client.py`): Communicates with the Whisper API
6. **Text Injector** (`text_injector.py`): Injects transcribed text into active applications
7. **Configuration** (`config.py`): Customizable settings

This architecture allows the keyboard shortcut to work **system-wide**, regardless of which application has focus.


## Project Structure

```
Documentation:
├── QUICKSTART.md          📖 Quick reference
├── WAYLAND_SETUP.md       🖥️ Wayland guide
├── README.md              📚 Full docs
└── YDOTOOL_INTEGRATION.md 🔧 Technical details

Helper Scripts:
├── start_daemon.sh        🚀 Quick start
├── setup.sh               📥 Installation
└── setup_autostart.sh     🔄 Systemd setup

Main Components:
├── voice_daemon.py    ⭐ Background service
├── voice_trigger.py   ⭐ Global shortcut script
├── audio_recorder.py  📼 Recording with silence detection
├── api_client.py      🌐 Whisper API communication
├── text_injector.py   ⌨️ Text injection (ydotool/xdotool)
└── config.py          ⚙️ Configuration
```

## Dependencies

### Python Packages
- `sounddevice`: Audio recording
- `numpy`: Audio data processing
- `scipy`: WAV file handling
- `requests`: HTTP client for API communication

### System Packages
- `xdotool` (X11): Text injection for X11
- `ydotool`/`ydotoold` (Wayland): Text injection for Wayland (downloaded automatically)
- `portaudio`: Audio I/O library
- `libnotify-bin`: Desktop notifications
- `wl-clipboard` (Wayland): Clipboard support

## Performance Notes

- First transcription may be slower as the Whisper model loads
- Recording automatically stops after 2 seconds of silence
- Maximum recording duration is 30 seconds (configurable in `config.py`)
- The Whisper API uses CPU by default; GPU support can be added to the Dockerfile

## Security Considerations

- The application runs locally and doesn't send data to external services
- Audio files are temporarily stored in `/tmp` and deleted after transcription
- The Whisper API is only accessible on localhost by default

## License

This project is provided as-is for personal and educational use.

## Acknowledgments

- Whisper-Assistant Dockerfile from [martin-opensky/whisper-assistant-vscode](https://github.com/martin-opensky/whisper-assistant-vscode)
