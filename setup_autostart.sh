#!/bin/bash

# Setup script to configure the voice daemon to start automatically

echo "Setting up AnyWhisper daemon autostart..."
echo ""

DAEMON_PATH="$(pwd)/voice_daemon.py"
VENV_PYTHON="$(pwd)/venv/bin/python"

# Create systemd user service directory if it doesn't exist
mkdir -p ~/.config/systemd/user/

# Create systemd service file
cat > ~/.config/systemd/user/any-whisper.service << EOF
[Unit]
Description=AnyWhisper Daemon
After=graphical-session.target

[Service]
Type=simple
WorkingDirectory=$SCRIPT_DIR
ExecStart=$VENV_PYTHON $DAEMON_PATH
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

echo "✅ Systemd service created: ~/.config/systemd/user/any-whisper.service"
echo ""

# Reload systemd
systemctl --user daemon-reload

echo "To manage the daemon:"
echo "  Start:   systemctl --user start any-whisper"
echo "  Stop:    systemctl --user stop any-whisper"
echo "  Status:  systemctl --user status any-whisper"
echo "  Enable:  systemctl --user enable any-whisper  (auto-start on login)"
echo "  Disable: systemctl --user disable any-whisper"
echo ""

read -p "Do you want to start and enable the daemon now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl --user enable any-whisper
    systemctl --user start any-whisper
    echo ""
    echo "✅ Daemon started and enabled!"
    sleep 1
    systemctl --user status any-whisper --no-pager
fi

echo ""
echo "Next steps:"
echo "1. Set up global keyboard shortcut in your desktop environment:"
echo "   GNOME: Settings → Keyboard → Keyboard Shortcuts → Custom Shortcuts"
echo "   KDE: System Settings → Shortcuts → Custom Shortcuts"
echo ""
echo "2. Create a new custom shortcut with:"
echo "   Name: AnyWhisper"
echo "   Command: $(pwd)/voice_trigger.py"
echo "   Shortcut: Ctrl+Shift+Space (or any combination you prefer)"
echo ""

