#!/bin/bash

# Setup script to configure AnyWhisper + ydotoold as systemd user services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAEMON_PATH="$SCRIPT_DIR/voice_daemon.py"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"
YDOTOOLD_PATH="$SCRIPT_DIR/ydotoold"

echo "Setting up AnyWhisper daemon autostart..."
echo ""

# --- Install udev rule for /dev/uinput ---
UDEV_RULE="$SCRIPT_DIR/99-uinput.rules"
if [ -f "$UDEV_RULE" ]; then
    echo "Installing udev rule for /dev/uinput..."
    sudo cp "$UDEV_RULE" /etc/udev/rules.d/99-uinput.rules
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    echo "  Installed: /etc/udev/rules.d/99-uinput.rules"
else
    echo "Warning: 99-uinput.rules not found, skipping udev setup"
fi

# --- Add user to input group (fallback for non-logind systems) ---
if ! groups "$USER" | grep -qw input; then
    echo "Adding $USER to input group..."
    sudo usermod -aG input "$USER"
    echo "  Note: You may need to log out and back in for group changes to take effect."
else
    echo "User $USER is already in the input group."
fi
echo ""

# --- Create systemd user service directory ---
mkdir -p ~/.config/systemd/user/

# --- Create ydotoold service ---
cat > ~/.config/systemd/user/ydotoold.service << EOF
[Unit]
Description=ydotoold - ydotool daemon
Documentation=https://github.com/ReimuNotMoe/ydotool

[Service]
Type=simple
ExecStart=$YDOTOOLD_PATH
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
EOF
echo "Created: ~/.config/systemd/user/ydotoold.service"

# --- Create any-whisper service ---
cat > ~/.config/systemd/user/any-whisper.service << EOF
[Unit]
Description=AnyWhisper Daemon
After=graphical-session.target ydotoold.service
Requires=ydotoold.service

[Service]
Type=simple
WorkingDirectory=$SCRIPT_DIR
ExecStart=$VENV_PYTHON $DAEMON_PATH
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF
echo "Created: ~/.config/systemd/user/any-whisper.service"
echo ""

# --- Reload systemd ---
systemctl --user daemon-reload

echo "To manage the services:"
echo "  Start:   systemctl --user start any-whisper"
echo "  Stop:    systemctl --user stop any-whisper"
echo "  Status:  systemctl --user status any-whisper"
echo "  Logs:    journalctl --user -u any-whisper -f"
echo ""

read -p "Do you want to start and enable both services now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl --user enable ydotoold
    systemctl --user start ydotoold
    echo "  ydotoold enabled and started."

    systemctl --user enable any-whisper
    systemctl --user start any-whisper
    echo "  any-whisper enabled and started."

    echo ""
    sleep 1
    systemctl --user status ydotoold --no-pager || true
    echo ""
    systemctl --user status any-whisper --no-pager || true
fi

echo ""
echo "Next steps:"
echo "1. Set up a global keyboard shortcut in your desktop environment:"
echo "   GNOME: Settings -> Keyboard -> Keyboard Shortcuts -> Custom Shortcuts"
echo "   KDE: System Settings -> Shortcuts -> Custom Shortcuts"
echo ""
echo "2. Create a new custom shortcut with:"
echo "   Name: AnyWhisper"
echo "   Command: $SCRIPT_DIR/voice_trigger.py"
echo "   Shortcut: Ctrl+Shift+Space (or any combination you prefer)"
echo ""
