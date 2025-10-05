#!/bin/bash

# Start ydotoold daemon in user context

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
YDOTOOLD="$SCRIPT_DIR/ydotoold"

# Check if ydotoold binary exists
if [ ! -f "$YDOTOOLD" ]; then
    echo "Error: ydotoold not found at $YDOTOOLD"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Check if ydotoold is already running
if pgrep -x "ydotoold" > /dev/null; then
    echo "ydotoold is already running"
    exit 0
fi

# Start ydotoold
echo "Starting ydotoold..."
"$YDOTOOLD" &

# Wait a moment for it to start
sleep 1

if pgrep -x "ydotoold" > /dev/null; then
    echo "✓ ydotoold started successfully"
else
    echo "✗ Failed to start ydotoold"
    exit 1
fi

