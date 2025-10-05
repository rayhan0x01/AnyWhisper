#!/bin/bash

# Setup script to configure the voice daemon to start automatically

echo "Setting up Voice-to-Text daemon autostart..."
echo ""

DAEMON_PATH="$(pwd)/voice_daemon.py"
VENV_PYTHON="$(pwd)/venv/bin/python"

# Create systemd user service directory if it doesn't exist
mkdir -p ~/.config/systemd/user/

# Create systemd service file
cat > ~/.config/systemd/user/voice-to-text.service << EOF
[Unit]
Description=Voice-to-Text Daemon
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

echo "✅ Systemd service created: ~/.config/systemd/user/voice-to-text.service"
echo ""

# Reload systemd
systemctl --user daemon-reload

echo "To manage the daemon:"
echo "  Start:   systemctl --user start voice-to-text"
echo "  Stop:    systemctl --user stop voice-to-text"
echo "  Status:  systemctl --user status voice-to-text"
echo "  Enable:  systemctl --user enable voice-to-text  (auto-start on login)"
echo "  Disable: systemctl --user disable voice-to-text"
echo ""

read -p "Do you want to start and enable the daemon now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl --user enable voice-to-text
    systemctl --user start voice-to-text
    echo ""
    echo "✅ Daemon started and enabled!"
    sleep 1
    systemctl --user status voice-to-text --no-pager
fi

echo ""
echo "Next steps:"
echo "1. Set up global keyboard shortcut in your desktop environment:"
echo "   GNOME: Settings → Keyboard → Keyboard Shortcuts → Custom Shortcuts"
echo "   KDE: System Settings → Shortcuts → Custom Shortcuts"
echo ""
echo "2. Create a new custom shortcut with:"
echo "   Name: Voice to Text"
echo "   Command: $(pwd)/voice_trigger.py"
echo "   Shortcut: Ctrl+Shift+Space (or any combination you prefer)"
echo ""

