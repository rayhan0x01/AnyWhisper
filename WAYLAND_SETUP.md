# Wayland Global Shortcut Setup

This guide explains how to set up the any-whisper application with **true OS-level global shortcuts** that work in Wayland.

## Architecture

The application now uses a **daemon + trigger** architecture:

1. **`voice_daemon.py`** - Background service that runs continuously
2. **`voice_trigger.py`** - Lightweight trigger script you bind to a global shortcut
3. Communication via Unix socket

This allows the shortcut to work **anywhere in the OS**, regardless of which application has focus.

## Setup Instructions

### 1. Install Dependencies

```bash
./setup.sh
```

### 2. Start the Daemon

You have two options:

#### Option A: Run Manually (for testing)

```bash
source venv/bin/activate
python voice_daemon.py
```

Keep this terminal open. The daemon will run in the foreground.

#### Option B: Run as Systemd Service (recommended)

```bash
./setup_autostart.sh
```

This will:
- Create a systemd user service
- Optionally start and enable it to run automatically on login

### 3. Set Up Global Keyboard Shortcut

#### GNOME (Ubuntu default)

1. Open **Settings** → **Keyboard** → **Keyboard Shortcuts**
2. Scroll down and click **"Custom Shortcuts"** or **"View and Customize Shortcuts"**
3. Click the **"+"** button to add a new shortcut
4. Fill in:
   - **Name**: `AnyWhisper`
   - **Command**: `/path/to/AnyWhisper/voice_trigger.py`
   - **Shortcut**: Click "Set Shortcut" and press `Ctrl+Shift+Space` (or your preferred combination)
5. Click **Add**

#### KDE Plasma

1. Open **System Settings** → **Shortcuts** → **Custom Shortcuts**
2. Click **Edit** → **New** → **Global Shortcut** → **Command/URL**
3. In the **Trigger** tab: Set your keyboard shortcut (e.g., `Ctrl+Shift+Space`)
4. In the **Action** tab: Enter `/path/to/AnyWhisper/voice_trigger.py`
5. Click **Apply**

### 4. Test It!

1. Make sure the Whisper Docker container is running:
   ```bash
   docker ps | grep whisper-assistant
   ```

2. Press your configured keyboard shortcut from **any application**
3. Speak your text
4. Press the shortcut again to stop (or wait 2 seconds of silence)
5. The text will be typed into the currently focused text input

## How It Works

1. **Daemon**: Runs in the background, waiting for commands
2. **Global Shortcut**: Triggers `voice_trigger.py` when pressed
3. **Trigger Script**: Sends `TOGGLE` command to daemon via Unix socket
4. **Daemon**: Toggles recording on/off
5. **Recording**: Captures audio, sends to Whisper API, injects text

## Commands

### Daemon Control (via systemd)

```bash
# Start daemon
systemctl --user start any-whisper

# Stop daemon
systemctl --user stop any-whisper

# Check status
systemctl --user status any-whisper

# Enable auto-start on login
systemctl --user enable any-whisper

# Disable auto-start
systemctl --user disable any-whisper

# View logs
journalctl --user -u any-whisper -f
```

### Manual Testing

```bash
# Test if daemon is running
python voice_trigger.py PING
# Should output: Response: PONG

# Check status
python voice_trigger.py STATUS
# Should output: Response: IDLE or RECORDING

# Manually start recording
python voice_trigger.py START

# Manually stop recording
python voice_trigger.py STOP

# Toggle recording (same as global shortcut)
python voice_trigger.py TOGGLE
```

## Advantages of This Approach

✅ **True Global Shortcuts**: Works in any application, anywhere in the OS  
✅ **Wayland Compatible**: No X11-specific hacks  
✅ **Lightweight**: Trigger script is fast and doesn't block  
✅ **Persistent**: Daemon can run in the background indefinitely  
✅ **Reliable**: Uses Unix sockets for IPC (fast and secure)  
✅ **System Integration**: Uses systemd for proper service management  

## Troubleshooting

### "Daemon not running" notification

The daemon isn't started. Run:
```bash
systemctl --user start any-whisper
# or manually:
python voice_daemon.py
```

### Global shortcut doesn't work

1. Check if the shortcut is properly configured in your DE settings
2. Make sure the path to `voice_trigger.py` is absolute: `/path/to/AnyWhisper/voice_trigger.py`
3. Make the script executable: `chmod +x voice_trigger.py`
4. Test manually: `./voice_trigger.py PING`

### Text not being injected

**For Wayland**, the setup script automatically downloads `ydotool` and `ydotoold` binaries to the project directory. The daemon will start `ydotoold` automatically when it starts.

If text injection still doesn't work, text will be copied to clipboard. Just paste with `Ctrl+V`.

**Note:** The binaries are from the official [ydotool GitHub releases](https://github.com/ReimuNotMoe/ydotool/releases/tag/v1.0.4) (v1.0.4).

### Whisper API errors

Make sure the Docker container is running:
```bash
docker ps | grep whisper-assistant

# If not running, start it:
docker run -d -p 127.0.0.1:4444:4444 --name whisper-assistant whisper-assistant
```

## Configuration

Edit `config.py` to customize:

- API endpoint
- Recording duration
- Silence detection sensitivity
- Temp file location

Changes to config.py require restarting the daemon:
```bash
systemctl --user restart any-whisper
```

