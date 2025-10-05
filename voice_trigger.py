#!/usr/bin/env python3
"""
Voice-to-Text Trigger Script

This script communicates with the voice daemon to toggle recording.
Bind this script to a global keyboard shortcut in your DE settings.
"""

import socket
import sys
import os


SOCKET_PATH = "/tmp/voice_to_text.sock"


def send_command(command):
    """Send command to the daemon."""
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)
        client.send(command.encode('utf-8'))
        response = client.recv(1024).decode('utf-8')
        client.close()
        return response
    except FileNotFoundError:
        print("Error: Daemon not running. Start it with: python voice_daemon.py", file=sys.stderr)
        os.system('notify-send "Voice to Text" "❌ Daemon not running! Start voice_daemon.py" 2>/dev/null &')
        return None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None


def main():
    """Main entry point."""
    # Default to TOGGLE if no argument provided
    command = sys.argv[1].upper() if len(sys.argv) > 1 else "TOGGLE"
    
    if command not in ["START", "STOP", "TOGGLE", "STATUS", "PING"]:
        print(f"Unknown command: {command}")
        print("Usage: voice_trigger.py [START|STOP|TOGGLE|STATUS|PING]")
        sys.exit(1)
    
    response = send_command(command)
    
    if response:
        print(f"Response: {response}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

