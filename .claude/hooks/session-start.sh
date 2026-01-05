#!/bin/bash
#
# session-start.sh - H-Claude Session Start Hook (V1)
#
# Quick environment checks. No agent spawning.
# Runs in background, never blocks session start.
#

trap 'exit 0' ERR EXIT SIGTERM SIGINT

{
    warnings=""

    # Check context.yaml exists
    [[ ! -f ".claude/context.yaml" ]] && warnings+="context.yaml missing\n"

    # Check at least one proxy responding
    proxy_ok=false
    timeout 1 curl -sf http://localhost:2405/health >/dev/null 2>&1 && proxy_ok=true
    timeout 1 curl -sf http://localhost:2406/health >/dev/null 2>&1 && proxy_ok=true
    timeout 1 curl -sf http://localhost:2408/health >/dev/null 2>&1 && proxy_ok=true
    [[ "$proxy_ok" == "false" ]] && warnings+="No proxies responding\n"

    # Output warnings
    if [[ -n "$warnings" ]]; then
        echo "" >&2
        echo "[H-Claude] Warnings:" >&2
        echo -e "$warnings" | while read -r line; do
            [[ -n "$line" ]] && echo "  - $line" >&2
        done
    fi
} &

exit 0
