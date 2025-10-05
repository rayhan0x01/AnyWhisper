# ydotool Integration

This document explains how ydotool has been integrated into the Voice-to-Text application for seamless Wayland support.

## What Was Done

### 1. Automatic Binary Download

The `setup.sh` script now automatically downloads ydotool binaries from GitHub if running on Wayland:

- **ydotool**: Command-line tool for simulating keyboard input
- **ydotoold**: Background daemon that ydotool communicates with

**Source:** [ydotool v1.0.4 releases](https://github.com/ReimuNotMoe/ydotool/releases/tag/v1.0.4)

### 2. Automatic Daemon Management

The `voice_daemon.py` now:
- Automatically detects if running on Wayland
- Checks if `ydotoold` is already running
- Starts the local `ydotoold` binary if needed
- Stops `ydotoold` when the daemon shuts down

### 3. Text Injection Priority

The `text_injector.py` now tries text injection in this order:

**For Wayland:**
1. Local `ydotool` binary (in project directory)
2. System `ydotool` (if installed via apt)
3. System `wtype` (fallback)
4. Clipboard copy (final fallback)

**For X11:**
1. System `xdotool`
2. Clipboard copy (fallback)

### 4. Helper Scripts

**`start_ydotoold.sh`** - Manually start ydotoold daemon:
```bash
./start_ydotoold.sh
```

**`start_daemon.sh`** - Updated to work from any directory:
```bash
./start_daemon.sh
```

## How It Works

### When You Run Setup

```bash
./setup.sh
```

On Wayland systems, the script:
1. Detects `XDG_SESSION_TYPE=wayland`
2. Downloads `ydotool` and `ydotoold` binaries to current directory
3. Makes them executable
4. Installs `wl-clipboard` for clipboard support

### When You Start the Daemon

```bash
./start_daemon.sh
```

The daemon:
1. Detects display server (Wayland/X11)
2. If Wayland: checks if `ydotoold` is running
3. If not running: starts local `ydotoold` binary
4. Continues with normal operation

### When You Use Voice-to-Text

1. Press global shortcut
2. Speak your text
3. Text is transcribed
4. Local `ydotool` types the text into focused application
5. Works anywhere in the OS!

## File Locations

```
/path/to/AnyWhisper/
├── ydotool          # Downloaded by setup.sh (Wayland only)
├── ydotoold         # Downloaded by setup.sh (Wayland only)
└── start_ydotoold.sh   # Manual start script
```

## Socket Communication

- **ydotool socket**: `/tmp/.ydotool_socket` (created by ydotoold)
- **Voice daemon socket**: `/tmp/voice_to_text.sock` (created by voice_daemon.py)

## Troubleshooting

### ydotool not working?

Check if ydotoold is running:
```bash
pgrep -x ydotoold
```

If not, start it manually:
```bash
./start_ydotoold.sh
```

### Permission errors?

```bash
sudo chmod 666 /dev/uinput
```

This gives user access to the uinput device that ydotool needs.

### Want to use system ydotool instead?

Just install it:
```bash
sudo apt install ydotool
```

The text injector will prefer the local binary but fall back to system ydotool.

### Binaries not downloading?

Check your internet connection and manually download:
```bash
wget https://github.com/ReimuNotMoe/ydotool/releases/download/v1.0.4/ydotool-release-ubuntu-latest -O ydotool
wget https://github.com/ReimuNotMoe/ydotool/releases/download/v1.0.4/ydotoold-release-ubuntu-latest -O ydotoold
chmod +x ydotool ydotoold
```

## Why ydotool?

### Advantages

✅ **Wayland Native**: Designed for Wayland from the ground up  
✅ **No Root Required**: Runs in user context  
✅ **Low-Level**: Uses uinput for reliable keyboard simulation  
✅ **Battle-Tested**: Used by many automation tools  
✅ **Standalone**: No system-wide installation needed  

### Comparison with Alternatives

| Tool | X11 | Wayland | Installation |
|------|-----|---------|--------------|
| xdotool | ✅ | ❌ | apt package |
| wtype | ❌ | ✅ | apt package |
| ydotool | ✅ | ✅ | Binary or apt |

## References

- [ydotool GitHub](https://github.com/ReimuNotMoe/ydotool)
- [ydotool v1.0.4 Release](https://github.com/ReimuNotMoe/ydotool/releases/tag/v1.0.4)
- [Wayland Input Methods](https://wayland.freedesktop.org/)

## Technical Details

### Binary Verification

The binaries are official releases from the ydotool repository:

**ydotool binary:**
- URL: https://github.com/ReimuNotMoe/ydotool/releases/download/v1.0.4/ydotool-release-ubuntu-latest
- Built for Ubuntu (latest)
- Version: 1.0.4

**ydotoold daemon:**
- URL: https://github.com/ReimuNotMoe/ydotool/releases/download/v1.0.4/ydotoold-release-ubuntu-latest  
- Built for Ubuntu (latest)
- Version: 1.0.4

### How ydotool Works

1. **ydotoold** creates a Unix socket at `/tmp/.ydotool_socket`
2. **ydotoold** opens `/dev/uinput` to simulate input events
3. **ydotool** (client) connects to the socket
4. **ydotool** sends commands to ydotoold
5. **ydotoold** generates keyboard events via uinput
6. Events appear as real keyboard input to all applications

### Code Changes

**setup.sh** (lines 49-77):
- Added Wayland detection
- Added binary download logic
- Added chmod for executability

**text_injector.py** (lines 77-112):
- Added local ydotool path resolution
- Prioritized local binary over system binary
- Updated error messages

**voice_daemon.py** (lines 147-173):
- Added `start_ydotoold_if_needed()` method
- Added automatic ydotoold startup
- Added cleanup on shutdown

**setup_autostart.sh** (line 22):
- Added WorkingDirectory to systemd service
- Ensures daemon can find local binaries

## Notes

- The binaries are downloaded only once during setup
- If binaries exist, setup.sh skips downloading
- The daemon automatically manages ydotoold lifecycle
- No manual intervention needed after setup
- Works out of the box on Wayland Ubuntu systems

