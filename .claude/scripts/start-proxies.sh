#!/bin/bash
# Start H-Claude proxy servers (New Architecture)
# Runs 6 role-based proxies on ports 2410-2415

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="/tmp/h-claude"

mkdir -p "$LOG_DIR"

echo "=== Starting H-Claude Proxies ==="
echo ""

# Check if already running
check_port() {
    lsof -ti:$1 > /dev/null 2>&1
}

# Start HC-Reas-A (2410) - Claude Opus for heavy reasoning
if check_port 2410; then
    echo "HC-Reas-A (2410): Already running"
else
    cd "$PROJECT_ROOT/HC-Proxies/HC-Reas-A"
    nohup npm start > "$LOG_DIR/hc-reas-a.log" 2>&1 &
    echo "HC-Reas-A (2410): Started (PID: $!)"
fi

# Start HC-Reas-B (2411) - Gemini Pro for challenger reasoning
if check_port 2411; then
    echo "HC-Reas-B (2411): Already running"
else
    cd "$PROJECT_ROOT/HC-Proxies/HC-Reas-B"
    nohup npm start > "$LOG_DIR/hc-reas-b.log" 2>&1 &
    echo "HC-Reas-B (2411): Started (PID: $!)"
fi

# Start HC-Work (2412) - Gemini Flash for workers
if check_port 2412; then
    echo "HC-Work (2412): Already running"
else
    cd "$PROJECT_ROOT/HC-Proxies/HC-Work"
    nohup npm start > "$LOG_DIR/hc-work.log" 2>&1 &
    echo "HC-Work (2412): Started (PID: $!)"
fi

# Start HC-Work-R (2413) - Gemini Flash with reasoning
if check_port 2413; then
    echo "HC-Work-R (2413): Already running"
else
    cd "$PROJECT_ROOT/HC-Proxies/HC-Work-R"
    nohup npm start > "$LOG_DIR/hc-work-r.log" 2>&1 &
    echo "HC-Work-R (2413): Started (PID: $!)"
fi

# Start HC-Orca (2414) - Gemini Flash for light coordination
if check_port 2414; then
    echo "HC-Orca (2414): Already running"
else
    cd "$PROJECT_ROOT/HC-Proxies/HC-Orca"
    nohup npm start > "$LOG_DIR/hc-orca.log" 2>&1 &
    echo "HC-Orca (2414): Started (PID: $!)"
fi

# Start HC-Orca-R (2415) - Gemini Pro for heavy coordination
if check_port 2415; then
    echo "HC-Orca-R (2415): Already running"
else
    cd "$PROJECT_ROOT/HC-Proxies/HC-Orca-R"
    nohup npm start > "$LOG_DIR/hc-orca-r.log" 2>&1 &
    echo "HC-Orca-R (2415): Started (PID: $!)"
fi

# Keep CG-Image (2407) if it exists
if [ -d "$PROJECT_ROOT/HC-Proxies/CG-Image" ]; then
    if check_port 2407; then
        echo "CG-Image (2407): Already running"
    else
        cd "$PROJECT_ROOT/HC-Proxies/CG-Image"
        nohup npm start > "$LOG_DIR/cg-image.log" 2>&1 &
        echo "CG-Image (2407): Started (PID: $!)"
    fi
fi

cd "$PROJECT_ROOT"

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

check_health 2410 "HC-Reas-A"
check_health 2411 "HC-Reas-B"
check_health 2412 "HC-Work"
check_health 2413 "HC-Work-R"
check_health 2414 "HC-Orca"
check_health 2415 "HC-Orca-R"
[ -d "$PROJECT_ROOT/HC-Proxies/CG-Image" ] && check_health 2407 "CG-Image"

echo ""
echo "Logs: $LOG_DIR/"
echo "Stop: .claude/scripts/stop-proxies.sh"
echo ""
