#!/bin/bash
# Agent Spawn Library - ADR-006 Implementation
# Source this file: source .claude/lib/agent-spawn.sh

# Spawn an agent with activity logging and stall-based timeout
# Usage: spawn_agent AGENT_NAME PROMPT PROXY_URL [STALL_THRESHOLD] [MAX_RUNTIME]
spawn_agent() {
  local AGENT_NAME="$1"
  local PROMPT="$2"
  local PROXY_URL="$3"
  local STALL_THRESHOLD="${4:-480}"   # 8 min default (Pro-level)
  local MAX_RUNTIME="${5:-14400}"     # 4 hour safety cap

  # Validate SESSION_PATH is set
  if [[ -z "$SESSION_PATH" ]]; then
    echo "[ERROR] SESSION_PATH not set. Cannot spawn agent."
    return 1
  fi

  local AGENT_LOGS="${SESSION_PATH}/agent-logs"
  local LOG_FILE="${AGENT_LOGS}/${AGENT_NAME}.log"
  local START_TIME=$(date +%s)

  mkdir -p "$AGENT_LOGS"

  # Initialize log
  cat > "$LOG_FILE" << EOF
agent: $AGENT_NAME
session: $SESSION_PATH
proxy: $PROXY_URL
started: $(date -Iseconds)
stall_threshold: ${STALL_THRESHOLD}s

entries:
EOF

  # Register as active
  echo "${AGENT_NAME}:$$:${START_TIME}" >> "${AGENT_LOGS}/ACTIVE_AGENTS"

  echo "[SPAWN] $AGENT_NAME via $PROXY_URL (stall: ${STALL_THRESHOLD}s)"

  # Spawn agent with logging instruction prepended
  ANTHROPIC_API_BASE_URL=$PROXY_URL claude --dangerously-skip-permissions -p "
## AGENT LOGGING PROTOCOL (REQUIRED)

Log file: $LOG_FILE

After EVERY significant action, append a log entry:
\`\`\`bash
echo \"  - ts: \\\"\$(date +%H:%M:%S)\\\" | state: STATE | msg: \\\"description\\\"\" >> $LOG_FILE
\`\`\`

States: STARTED, WORKING, TOOL_CALL, WAITING, BLOCKED, ERROR, COMPLETED

Log at minimum:
1. When you start (STARTED)
2. Before/after tool calls (TOOL_CALL)
3. Key milestones (WORKING)
4. When done (COMPLETED)

---

$PROMPT
" 2>&1 &

  local AGENT_PID=$!

  # Monitor loop
  while kill -0 $AGENT_PID 2>/dev/null; do
    sleep 30

    local NOW=$(date +%s)

    # Safety cap check
    if (( NOW - START_TIME > MAX_RUNTIME )); then
      echo "[SAFETY] $AGENT_NAME: Max runtime exceeded (${MAX_RUNTIME}s)"
      echo "  - ts: \"$(date +%H:%M:%S)\" | state: KILLED | msg: \"Max runtime exceeded\"" >> "$LOG_FILE"
      kill -TERM $AGENT_PID 2>/dev/null
      sleep 5
      kill -9 $AGENT_PID 2>/dev/null
      break
    fi

    # Stall check
    if [[ -f "$LOG_FILE" ]]; then
      local LAST_MOD=$(stat -c %Y "$LOG_FILE" 2>/dev/null || echo 0)
      if (( NOW - LAST_MOD > STALL_THRESHOLD )); then
        echo "[STALL] $AGENT_NAME: No log update for ${STALL_THRESHOLD}s"
        echo "  - ts: \"$(date +%H:%M:%S)\" | state: KILLED | msg: \"Stall detected - no progress\"" >> "$LOG_FILE"
        kill -TERM $AGENT_PID 2>/dev/null
        sleep 5
        kill -9 $AGENT_PID 2>/dev/null
        break
      fi
    fi
  done

  wait $AGENT_PID 2>/dev/null
  local EXIT_CODE=$?

  # Mark completion
  echo "  - ts: \"$(date +%H:%M:%S)\" | state: FINISHED | exit: $EXIT_CODE" >> "$LOG_FILE"
  sed -i "/^${AGENT_NAME}:/d" "${AGENT_LOGS}/ACTIVE_AGENTS" 2>/dev/null

  echo "[DONE] $AGENT_NAME exited with code $EXIT_CODE"
  return $EXIT_CODE
}

# Quick spawn without monitoring (for simple tasks)
spawn_agent_simple() {
  local AGENT_NAME="$1"
  local PROMPT="$2"
  local PROXY_URL="$3"
  local TIMEOUT="${4:-300}"

  timeout --foreground --signal=TERM --kill-after=30 $TIMEOUT \
    bash -c "ANTHROPIC_API_BASE_URL=$PROXY_URL claude --dangerously-skip-permissions -p \"$PROMPT\"" 2>&1
}

# List active agents in a session
list_active_agents() {
  local SESSION="${1:-$SESSION_PATH}"
  if [[ -f "${SESSION}/agent-logs/ACTIVE_AGENTS" ]]; then
    echo "Active agents in $SESSION:"
    cat "${SESSION}/agent-logs/ACTIVE_AGENTS"
  else
    echo "No active agents"
  fi
}

# Tail an agent's log
tail_agent_log() {
  local AGENT_NAME="$1"
  local SESSION="${2:-$SESSION_PATH}"
  tail -f "${SESSION}/agent-logs/${AGENT_NAME}.log"
}

# Clean up orphaned entries from ACTIVE_AGENTS (dead PIDs)
# Run at session start to clear stale entries from crashed agents
cleanup_orphaned_agents() {
  local SESSION="${1:-$SESSION_PATH}"
  local ACTIVE_FILE="${SESSION}/agent-logs/ACTIVE_AGENTS"

  [[ ! -f "$ACTIVE_FILE" ]] && return 0

  local TEMP_FILE=$(mktemp)
  local CLEANED=0

  while IFS=: read -r NAME PID TIMESTAMP; do
    if kill -0 "$PID" 2>/dev/null; then
      # PID still running, keep entry
      echo "${NAME}:${PID}:${TIMESTAMP}" >> "$TEMP_FILE"
    else
      # PID dead, log orphan and skip
      echo "[CLEANUP] Removed orphaned agent: $NAME (PID $PID)"
      local LOG_FILE="${SESSION}/agent-logs/${NAME}.log"
      if [[ -f "$LOG_FILE" ]]; then
        echo "  - ts: \"$(date +%H:%M:%S)\" | state: ORPHANED | msg: \"Cleaned up - PID no longer running\"" >> "$LOG_FILE"
      fi
      ((CLEANED++))
    fi
  done < "$ACTIVE_FILE"

  mv "$TEMP_FILE" "$ACTIVE_FILE"

  if (( CLEANED > 0 )); then
    echo "[CLEANUP] Removed $CLEANED orphaned agent entries"
  fi

  return 0
}
