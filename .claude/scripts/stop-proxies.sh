#!/bin/bash
# Stop H-Claude proxy servers (New Architecture)

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

# New proxies (2410-2415)
stop_port 2410 "HC-Reas-A"
stop_port 2411 "HC-Reas-B"
stop_port 2412 "HC-Work"
stop_port 2413 "HC-Work-R"
stop_port 2414 "HC-Orca"
stop_port 2415 "HC-Orca-R"

# CG-Image (if running)
stop_port 2407 "CG-Image"

# Old proxies (cleanup)
stop_port 2405 "CG-Flash (legacy)"
stop_port 2406 "CG-Pro (legacy)"
stop_port 2408 "CC-Claude (legacy)"

echo ""
echo "All proxies stopped."
