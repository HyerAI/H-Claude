#!/bin/bash
# Stop H-Claude proxy servers

echo "=== Stopping H-Claude Proxies ==="
echo ""

stop_port() {
    local port=$1
    local name=$2
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill 2>/dev/null
        echo "$name ($port): Stopped"
    else
        echo "$name ($port): Not running"
    fi
}

stop_port 2405 "CG-Flash"
stop_port 2406 "CG-Pro"
stop_port 2408 "CC-Claude"

echo ""
echo "All proxies stopped."
