#!/bin/bash
#
# session-start.sh - H-Claude Session Start Hook
#
# CRITICAL SAFETY REQUIREMENTS:
# - ALWAYS exits 0 (never fails session)
# - Runs checks in background (non-blocking)
# - Total execution <2 seconds
# - Output to stderr only
# - No file reading/parsing (existence checks only)
# - NEVER invoke 'claude' command (causes recursion!)
#

# SAFETY: Catch ALL errors and exit cleanly
trap 'exit 0' ERR EXIT SIGTERM SIGINT

# SAFETY: Run all checks in background, don't block session start
{
    warnings=""

    # Check context.yaml exists (fast, local)
    if [[ ! -f ".claude/context.yaml" ]]; then
        warnings+="context.yaml missing\n"
    fi

    # Check at least one proxy is responding (with 1s timeout each)
    proxy_ok=false
    if timeout 1 curl -sf http://localhost:2405/health >/dev/null 2>&1; then
        proxy_ok=true
    elif timeout 1 curl -sf http://localhost:2406/health >/dev/null 2>&1; then
        proxy_ok=true
    elif timeout 1 curl -sf http://localhost:2408/health >/dev/null 2>&1; then
        proxy_ok=true
    fi

    if [[ "$proxy_ok" == "false" ]]; then
        warnings+="No proxies responding\n"
    fi

    # Output warnings to stderr (if any)
    if [[ -n "$warnings" ]]; then
        echo "" >&2
        echo "[H-Claude] Environment warnings:" >&2
        echo -e "$warnings" | while read -r line; do
            [[ -n "$line" ]] && echo "  - $line" >&2
        done
        echo "Run ./hc-init for details" >&2
        echo "" >&2
    fi
} &

# SAFETY: Don't wait for background process - exit immediately
exit 0
