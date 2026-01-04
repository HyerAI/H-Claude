#!/bin/bash
# Start PM-View wiki server
# Reads port from .env file (default: 8003)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load .env if exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Defaults
HOST="${PM_VIEW_HOST:-127.0.0.1}"
PORT="${PM_VIEW_PORT:-8003}"

# Kill existing process on this port
fuser -k "$PORT/tcp" 2>/dev/null

echo "Starting PM-View wiki on http://$HOST:$PORT"
mkdocs serve --dev-addr "$HOST:$PORT"
