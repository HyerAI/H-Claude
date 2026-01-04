#!/bin/bash
# Stop PM-View wiki server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load .env if exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

PORT="${PM_VIEW_PORT:-8003}"

if fuser -k "$PORT/tcp" 2>/dev/null; then
    echo "Stopped PM-View wiki on port $PORT"
else
    echo "No wiki running on port $PORT"
fi
