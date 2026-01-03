#!/bin/bash
# Start H-Claude proxy servers
# Runs CG-Flash (2405), CG-Pro (2406), and CC-Claude (2408) in background

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="/tmp/h-claude"

mkdir -p "$LOG_DIR"

echo "=== Starting H-Claude Proxies ==="
echo ""

# Check if already running
check_port() {
    lsof -ti:$1 > /dev/null 2>&1
}

# Start CG-Flash (2405)
if check_port 2405; then
    echo "CG-Flash (2405): Already running"
else
    cd "$SCRIPT_DIR/infrastructure/CG-Flash"
    nohup npm start > "$LOG_DIR/cg-flash.log" 2>&1 &
    echo "CG-Flash (2405): Started (PID: $!)"
fi

# Start CG-Pro (2406)
if check_port 2406; then
    echo "CG-Pro (2406): Already running"
else
    cd "$SCRIPT_DIR/infrastructure/CG-Pro"
    nohup npm start > "$LOG_DIR/cg-pro.log" 2>&1 &
    echo "CG-Pro (2406): Started (PID: $!)"
fi

# Start CC-Claude (2408)
if check_port 2408; then
    echo "CC-Claude (2408): Already running"
else
    cd "$SCRIPT_DIR/infrastructure/CC-Claude"
    nohup npm start > "$LOG_DIR/cc-claude.log" 2>&1 &
    echo "CC-Claude (2408): Started (PID: $!)"
fi

cd "$SCRIPT_DIR"

echo ""
echo "Waiting for proxies to initialize..."
sleep 3

echo ""
echo "=== Health Check ==="

# Health checks
check_health() {
    local port=$1
    local name=$2
    if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "$name ($port): OK"
        return 0
    else
        echo "$name ($port): FAILED"
        return 1
    fi
}

check_health 2405 "CG-Flash"
check_health 2406 "CG-Pro"
check_health 2408 "CC-Claude"

echo ""
echo "Logs: $LOG_DIR/"
echo "Stop: ./stop-proxies.sh"
echo ""
