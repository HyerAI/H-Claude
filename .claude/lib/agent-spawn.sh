#!/bin/bash
# Agent Spawn Library - ADR-006 + ADR-007 Implementation
# Source this file: source .claude/lib/agent-spawn.sh
#
# V1.1.0 - Added resilience features (ADR-007):
#   - Pre/post spawn checkpointing
#   - Automatic CYCLE_STATE.yaml updates
#   - Git checkpoint commits
#   - Crash recovery protocol

# ============================================================================
# STATE MANAGEMENT FUNCTIONS
# ============================================================================

# Update CYCLE_STATE.yaml with current step status
# Usage: update_cycle_state PHASE STEP STATUS [OUTCOME] [EXTRA_YAML]
# Example: update_cycle_state "PHASE-002" "execute" "complete" "success" "commit: abc123"
update_cycle_state() {
  local PHASE="$1"
  local STEP="$2"
  local STATUS="$3"
  local OUTCOME="${4:-}"
  local EXTRA="${5:-}"

  local CYCLE_STATE="${CYCLE_SESSION_PATH:-$SESSION_PATH}/CYCLE_STATE.yaml"

  if [[ ! -f "$CYCLE_STATE" ]]; then
    echo "[WARN] CYCLE_STATE.yaml not found at $CYCLE_STATE"
    return 1
  fi

  local TIMESTAMP=$(date -Iseconds)

  # Use Python for reliable YAML manipulation (available in our stack)
  python3 << EOF
import yaml
import sys

cycle_state_path = "$CYCLE_STATE"
phase_id = "$PHASE"
step_name = "$STEP"
status = "$STATUS"
outcome = "$OUTCOME"
extra = "$EXTRA"
timestamp = "$TIMESTAMP"

try:
    with open(cycle_state_path, 'r') as f:
        state = yaml.safe_load(f)

    # Find the phase
    phase_found = False
    for phase in state.get('phases', []):
        if phase.get('id') == phase_id:
            phase_found = True
            # Update step status
            if 'steps' not in phase:
                phase['steps'] = {}
            if step_name not in phase['steps']:
                phase['steps'][step_name] = {}

            phase['steps'][step_name]['status'] = status

            if status == 'in_progress':
                phase['steps'][step_name]['started_at'] = timestamp
                phase['status'] = 'in_progress'
            elif status == 'complete':
                phase['steps'][step_name]['completed_at'] = timestamp
                if outcome:
                    phase['steps'][step_name]['outcome'] = outcome
            elif status == 'failed':
                phase['steps'][step_name]['failed_at'] = timestamp
                if outcome:
                    phase['steps'][step_name]['error'] = outcome

            # Parse extra YAML fields
            if extra:
                for item in extra.split(','):
                    if ':' in item:
                        key, val = item.split(':', 1)
                        phase['steps'][step_name][key.strip()] = val.strip()
            break

    if not phase_found:
        print(f"[WARN] Phase {phase_id} not found in CYCLE_STATE", file=sys.stderr)
        sys.exit(1)

    # Update current_step tracker
    state['current_step'] = {
        'phase': phase_id,
        'step': step_name,
        'status': status,
        'updated_at': timestamp
    }

    with open(cycle_state_path, 'w') as f:
        yaml.dump(state, f, default_flow_style=False, sort_keys=False)

    print(f"[STATE] {phase_id}.{step_name} = {status}")

except Exception as e:
    print(f"[ERROR] Failed to update CYCLE_STATE: {e}", file=sys.stderr)
    sys.exit(1)
EOF

  return $?
}

# Append entry to ORCHESTRATOR_LOG.md
# Usage: log_orchestrator MESSAGE
log_orchestrator() {
  local MESSAGE="$1"
  local TIMESTAMP=$(date +"%H:%M")
  local LOG_FILE="${CYCLE_SESSION_PATH:-$SESSION_PATH}/ORCHESTRATOR_LOG.md"

  if [[ -f "$LOG_FILE" ]]; then
    echo "" >> "$LOG_FILE"
    echo "## ${TIMESTAMP} - ${MESSAGE}" >> "$LOG_FILE"
  fi
}

# Mark the entire cycle as complete
# Usage: complete_cycle [STATUS] [PHASES_COMPLETED] [PHASES_FAILED]
# Example: complete_cycle "complete" 3 0
complete_cycle() {
  local STATUS="${1:-complete}"
  local COMPLETED="${2:-1}"
  local FAILED="${3:-0}"

  local CYCLE_STATE="${CYCLE_SESSION_PATH:-$SESSION_PATH}/CYCLE_STATE.yaml"

  if [[ ! -f "$CYCLE_STATE" ]]; then
    echo "[WARN] CYCLE_STATE.yaml not found"
    return 1
  fi

  local TIMESTAMP=$(date -Iseconds)

  python3 << EOF
import yaml

cycle_state_path = "$CYCLE_STATE"
status = "$STATUS"
completed = $COMPLETED
failed = $FAILED
timestamp = "$TIMESTAMP"

try:
    with open(cycle_state_path, 'r') as f:
        state = yaml.safe_load(f)

    # Update outcome
    state['outcome'] = {
        'status': status,
        'phases_completed': completed,
        'phases_failed': failed,
        'completed_at': timestamp
    }

    # Update current_step to show completion
    state['current_step']['status'] = status
    state['current_step']['updated_at'] = timestamp

    with open(cycle_state_path, 'w') as f:
        yaml.dump(state, f, default_flow_style=False, sort_keys=False)

    print(f"[CYCLE] Marked as {status} ({completed} completed, {failed} failed)")

except Exception as e:
    print(f"[ERROR] Failed to complete cycle: {e}")
    exit(1)
EOF

  return $?
}

# Create a git checkpoint commit for state changes
# Usage: git_checkpoint MESSAGE [FILES...]
# If no files specified, commits all state files in .claude/PM/
git_checkpoint() {
  local MESSAGE="$1"
  shift
  local FILES=("$@")

  # Default files if none specified
  if [[ ${#FILES[@]} -eq 0 ]]; then
    FILES=(
      ".claude/PM/phase-cycles/"
      ".claude/PM/SSoT/ROADMAP.yaml"
    )
  fi

  # Only add files that exist
  local TO_ADD=()
  for f in "${FILES[@]}"; do
    if [[ -e "$f" ]]; then
      TO_ADD+=("$f")
    fi
  done

  if [[ ${#TO_ADD[@]} -eq 0 ]]; then
    echo "[CHECKPOINT] No state files to commit"
    return 0
  fi

  git add "${TO_ADD[@]}" 2>/dev/null

  # Check if there are staged changes
  if git diff --cached --quiet 2>/dev/null; then
    echo "[CHECKPOINT] No changes to commit"
    return 0
  fi

  git commit -m "$(cat <<EOF
${MESSAGE}

State checkpoint - crash recovery point

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)" 2>/dev/null

  local RESULT=$?
  if [[ $RESULT -eq 0 ]]; then
    local HASH=$(git rev-parse --short HEAD)
    echo "[CHECKPOINT] Committed: $HASH - $MESSAGE"
  else
    echo "[CHECKPOINT] Commit failed or nothing to commit"
  fi

  return $RESULT
}

# ============================================================================
# RECOVERY FUNCTIONS
# ============================================================================

# Check for interrupted cycles and offer recovery
# Usage: recover_cycle [CYCLE_PATH]
# Returns: 0 if clean, 1 if interrupted cycle found
#
# A cycle is "interrupted" if:
#   - outcome.status is NOT "complete" (cycle didn't finish)
#   - AND current_step.status is "in_progress" (was mid-step when stopped)
recover_cycle() {
  local CYCLE_PATH="${1:-.claude/PM/phase-cycles}"

  # Find cycles that are truly interrupted (not just have in_progress somewhere)
  local INTERRUPTED=()

  while IFS= read -r -d '' STATE_FILE; do
    # Check outcome.status - if complete, cycle finished successfully
    local OUTCOME_STATUS=$(grep -A2 "^outcome:" "$STATE_FILE" 2>/dev/null | grep "status:" | head -1 | sed 's/.*status: *//')

    if [[ "$OUTCOME_STATUS" == "complete" ]]; then
      continue  # Cycle finished, not interrupted
    fi

    # Check current_step.status - if in_progress, was mid-step when stopped
    local CURRENT_STATUS=$(grep -A4 "^current_step:" "$STATE_FILE" 2>/dev/null | grep "status:" | head -1 | sed 's/.*status: *//')

    if [[ "$CURRENT_STATUS" == "in_progress" ]]; then
      INTERRUPTED+=("$STATE_FILE")
    fi
  done < <(find "$CYCLE_PATH" -name "CYCLE_STATE.yaml" -print0 2>/dev/null)

  if [[ ${#INTERRUPTED[@]} -eq 0 ]]; then
    echo "[RECOVERY] No interrupted cycles found"
    return 0
  fi

  echo "[RECOVERY] Found ${#INTERRUPTED[@]} interrupted cycle(s):"
  for state_file in "${INTERRUPTED[@]}"; do
    local CYCLE_DIR=$(dirname "$state_file")
    local CYCLE_NAME=$(basename "$CYCLE_DIR")

    # Extract current step info
    local CURRENT_PHASE=$(grep -A4 "^current_step:" "$state_file" | grep "phase:" | head -1 | sed 's/.*phase: *//')
    local CURRENT_STEP=$(grep -A4 "^current_step:" "$state_file" | grep "step:" | head -1 | sed 's/.*step: *//')

    echo "  - $CYCLE_NAME: Interrupted at $CURRENT_PHASE / $CURRENT_STEP"
    echo "    State: $state_file"
  done

  return 1
}

# Sync gate - verify state is consistent before proceeding
# Usage: sync_gate
# Returns: 0 if in sync, 1 if mismatch detected
sync_gate() {
  local CYCLE_STATE="${CYCLE_SESSION_PATH:-$SESSION_PATH}/CYCLE_STATE.yaml"

  if [[ ! -f "$CYCLE_STATE" ]]; then
    echo "[SYNC] No CYCLE_STATE.yaml - nothing to verify"
    return 0
  fi

  local ERRORS=0

  # Check 1: CYCLE_STATE.yaml is committed
  if ! git diff --quiet "$CYCLE_STATE" 2>/dev/null; then
    echo "[SYNC] WARNING: CYCLE_STATE.yaml has uncommitted changes"
    ((ERRORS++))
  fi

  # Check 2: No uncommitted state files
  local UNCOMMITTED=$(git status --porcelain .claude/PM/phase-cycles/ 2>/dev/null | grep -v "^?" | wc -l)
  if [[ $UNCOMMITTED -gt 0 ]]; then
    echo "[SYNC] WARNING: $UNCOMMITTED uncommitted state file(s)"
    ((ERRORS++))
  fi

  # Check 3: ORCHESTRATOR_LOG.md exists and is committed
  local LOG_FILE="${CYCLE_SESSION_PATH:-$SESSION_PATH}/ORCHESTRATOR_LOG.md"
  if [[ -f "$LOG_FILE" ]] && ! git diff --quiet "$LOG_FILE" 2>/dev/null; then
    echo "[SYNC] WARNING: ORCHESTRATOR_LOG.md has uncommitted changes"
    ((ERRORS++))
  fi

  if [[ $ERRORS -gt 0 ]]; then
    echo "[SYNC] Found $ERRORS sync issue(s) - recommend: git_checkpoint before proceeding"
    return 1
  fi

  echo "[SYNC] State is in sync"
  return 0
}

# ============================================================================
# AGENT SPAWN FUNCTIONS
# ============================================================================

# Spawn an agent with activity logging and stall-based timeout
# Usage: spawn_agent AGENT_NAME PROMPT PROXY_URL [STALL_THRESHOLD] [MAX_RUNTIME]
spawn_agent() {
  local AGENT_NAME="$1"
  local PROMPT="$2"
  local PROXY_URL="$3"
  local STALL_THRESHOLD="${4:-300}"   # 5 min default (faster stall detection)
  local MAX_RUNTIME="${5:-14400}"     # 4 hour safety cap

  # Validate SESSION_PATH is set
  if [[ -z "$SESSION_PATH" && -z "$CYCLE_SESSION_PATH" ]]; then
    echo "[ERROR] SESSION_PATH or CYCLE_SESSION_PATH not set. Cannot spawn agent."
    return 1
  fi

  local BASE_PATH="${CYCLE_SESSION_PATH:-$SESSION_PATH}"
  local AGENT_LOGS="${BASE_PATH}/agent-logs"
  local LOG_FILE="${AGENT_LOGS}/${AGENT_NAME}.log"
  local START_TIME=$(date +%s)

  mkdir -p "$AGENT_LOGS"

  # Initialize log
  cat > "$LOG_FILE" << EOF
agent: $AGENT_NAME
session: $BASE_PATH
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
  local SESSION="${1:-${CYCLE_SESSION_PATH:-$SESSION_PATH}}"
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
  local SESSION="${2:-${CYCLE_SESSION_PATH:-$SESSION_PATH}}"
  tail -f "${SESSION}/agent-logs/${AGENT_NAME}.log"
}

# Cleanup stale ACTIVE_AGENTS entries (crashed agents leave orphan entries)
# Usage: cleanup_stale_agents [SESSION_PATH]
cleanup_stale_agents() {
  local SESSION="${1:-${CYCLE_SESSION_PATH:-$SESSION_PATH}}"
  local ACTIVE_FILE="${SESSION}/agent-logs/ACTIVE_AGENTS"

  if [[ ! -f "$ACTIVE_FILE" ]]; then
    return 0
  fi

  local CLEANED=0
  local TEMP_FILE=$(mktemp)

  while IFS=: read -r NAME PID START_TIME; do
    if [[ -z "$NAME" ]]; then
      continue
    fi

    # Check if PID is still running
    if kill -0 "$PID" 2>/dev/null; then
      # Still alive - keep entry
      echo "${NAME}:${PID}:${START_TIME}" >> "$TEMP_FILE"
    else
      # Dead - mark log as orphaned and skip entry
      local LOG_FILE="${SESSION}/agent-logs/${NAME}.log"
      if [[ -f "$LOG_FILE" ]]; then
        echo "  - ts: \"$(date +%H:%M:%S)\" | state: ORPHANED | msg: \"Parent process died, entry cleaned up\"" >> "$LOG_FILE"
      fi
      echo "[CLEANUP] Removed stale entry: $NAME (PID $PID dead)"
      ((CLEANED++))
    fi
  done < "$ACTIVE_FILE"

  mv "$TEMP_FILE" "$ACTIVE_FILE"

  if (( CLEANED > 0 )); then
    echo "[CLEANUP] Removed $CLEANED stale agent entries"
  fi

  return 0
}

# Cleanup stale entries across all session directories
# Usage: cleanup_all_stale_agents BASE_PATH
cleanup_all_stale_agents() {
  local BASE_PATH="${1:-.claude/PM}"

  # Find all ACTIVE_AGENTS files
  while IFS= read -r -d '' ACTIVE_FILE; do
    local SESSION_DIR=$(dirname "$(dirname "$ACTIVE_FILE")")
    cleanup_stale_agents "$SESSION_DIR"
  done < <(find "$BASE_PATH" -name "ACTIVE_AGENTS" -print0 2>/dev/null)

  echo "[CLEANUP] Stale agent cleanup complete"
}

# ============================================================================
# RESILIENT SPAWN (Recommended for Phase Cycles)
# ============================================================================

# Spawn an agent with automatic state checkpointing
# This is the RECOMMENDED function for phase cycle operations
# Usage: spawn_agent_resilient AGENT_NAME PROMPT PROXY_URL PHASE STEP [STALL_THRESHOLD]
#
# Automatically:
#   1. Updates CYCLE_STATE.yaml to in_progress BEFORE spawn
#   2. Creates git checkpoint BEFORE spawn (recovery point)
#   3. Logs to ORCHESTRATOR_LOG.md
#   4. Spawns agent with monitoring
#   5. Updates CYCLE_STATE.yaml with result AFTER spawn
#   6. Creates git checkpoint AFTER spawn
#
spawn_agent_resilient() {
  local AGENT_NAME="$1"
  local PROMPT="$2"
  local PROXY_URL="$3"
  local PHASE="$4"
  local STEP="$5"
  local STALL_THRESHOLD="${6:-300}"

  # Validate required params
  if [[ -z "$PHASE" || -z "$STEP" ]]; then
    echo "[ERROR] spawn_agent_resilient requires PHASE and STEP parameters"
    echo "Usage: spawn_agent_resilient AGENT_NAME PROMPT PROXY_URL PHASE STEP [STALL_THRESHOLD]"
    return 1
  fi

  if [[ -z "$CYCLE_SESSION_PATH" && -z "$SESSION_PATH" ]]; then
    echo "[ERROR] CYCLE_SESSION_PATH or SESSION_PATH must be set"
    return 1
  fi

  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  RESILIENT SPAWN: $AGENT_NAME"
  echo "║  Phase: $PHASE | Step: $STEP"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""

  # ──────────────────────────────────────────────────────────────────
  # PRE-SPAWN: Checkpoint BEFORE execution (crash recovery point)
  # ──────────────────────────────────────────────────────────────────

  echo "[PRE-SPAWN] Creating recovery checkpoint..."

  # 1. Update state to in_progress
  update_cycle_state "$PHASE" "$STEP" "in_progress"

  # 2. Log to orchestrator
  log_orchestrator "Starting $PHASE/$STEP - Agent: $AGENT_NAME"

  # 3. Git checkpoint (recovery point)
  git_checkpoint "[${PHASE}] Starting ${STEP}"

  echo "[PRE-SPAWN] Checkpoint complete - safe to crash now"
  echo ""

  # ──────────────────────────────────────────────────────────────────
  # SPAWN: Execute agent
  # ──────────────────────────────────────────────────────────────────

  echo "[SPAWN] Launching agent..."

  # Call base spawn_agent
  spawn_agent "$AGENT_NAME" "$PROMPT" "$PROXY_URL" "$STALL_THRESHOLD"
  local EXIT_CODE=$?

  echo ""

  # ──────────────────────────────────────────────────────────────────
  # POST-SPAWN: Record result and checkpoint
  # ──────────────────────────────────────────────────────────────────

  echo "[POST-SPAWN] Recording result..."

  local OUTCOME
  local STATUS
  if [[ $EXIT_CODE -eq 0 ]]; then
    STATUS="complete"
    OUTCOME="success"
    echo "[POST-SPAWN] Agent completed successfully"
  else
    STATUS="failed"
    OUTCOME="exit_code_$EXIT_CODE"
    echo "[POST-SPAWN] Agent failed with exit code $EXIT_CODE"
  fi

  # 1. Update state with result
  update_cycle_state "$PHASE" "$STEP" "$STATUS" "$OUTCOME" "exit_code: $EXIT_CODE"

  # 2. Log to orchestrator
  log_orchestrator "Completed $PHASE/$STEP - Result: $OUTCOME (exit: $EXIT_CODE)"

  # 3. Git checkpoint (capture result)
  git_checkpoint "[${PHASE}] Completed ${STEP}: ${OUTCOME}"

  echo "[POST-SPAWN] State checkpointed"
  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  RESULT: $STATUS ($OUTCOME)"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""

  return $EXIT_CODE
}

# Helper: Convert exit code to status string
exit_to_status() {
  local EXIT_CODE="$1"
  if [[ $EXIT_CODE -eq 0 ]]; then
    echo "complete"
  else
    echo "failed"
  fi
}

# ============================================================================
# PRE-CYCLE VALIDATION
# ============================================================================

# Check proxy health before starting cycle
# Usage: check_proxy_health [PORTS...]
# Default ports: 2410-2415
# Returns: 0 if all healthy, 1 if any failed
check_proxy_health() {
  local PORTS=("${@:-2410 2411 2412 2413 2414 2415}")
  local FAILED=0
  local HEALTHY=0

  echo "[PROXY] Checking proxy health..."

  for port in "${PORTS[@]}"; do
    # Try to connect - proxies should respond to basic request
    if curl -s --connect-timeout 2 "http://localhost:${port}" >/dev/null 2>&1; then
      echo "  ✓ Port $port: UP"
      ((HEALTHY++))
    else
      echo "  ✗ Port $port: DOWN"
      ((FAILED++))
    fi
  done

  if [[ $FAILED -gt 0 ]]; then
    echo "[PROXY] WARNING: $FAILED proxy(s) not responding"
    echo "[PROXY] Run: claude-proxy start (or check proxy configuration)"
    return 1
  fi

  echo "[PROXY] All $HEALTHY proxies healthy"
  return 0
}

# Validate NORTHSTAR and ROADMAP before cycle
# Usage: validate_cycle_prereqs [PHASES...]
# Returns: 0 if valid, 1 if issues found
validate_cycle_prereqs() {
  local PHASES=("$@")
  local ERRORS=0

  local NORTH=".claude/PM/SSoT/NORTHSTAR.md"
  local ROAD=".claude/PM/SSoT/ROADMAP.yaml"

  echo "[VALIDATE] Checking cycle prerequisites..."

  # Check NORTHSTAR for placeholders
  if [[ -f "$NORTH" ]]; then
    if grep -qiE '\[PLACEHOLDER\]|\[TODO\]|\[TBD\]|Purpose goes here|Vision goes here' "$NORTH" 2>/dev/null; then
      echo "  ✗ NORTHSTAR.md contains placeholder text"
      ((ERRORS++))
    else
      echo "  ✓ NORTHSTAR.md looks complete"
    fi
  else
    echo "  ⚠ NORTHSTAR.md not found (optional)"
  fi

  # Check ROADMAP exists and has requested phases
  if [[ -f "$ROAD" ]]; then
    for phase in "${PHASES[@]}"; do
      if grep -q "id: $phase" "$ROAD" 2>/dev/null; then
        echo "  ✓ Phase $phase exists in ROADMAP"
      else
        echo "  ✗ Phase $phase NOT FOUND in ROADMAP.yaml"
        ((ERRORS++))
      fi
    done
  else
    echo "  ⚠ ROADMAP.yaml not found (will create during cycle)"
  fi

  if [[ $ERRORS -gt 0 ]]; then
    echo "[VALIDATE] Found $ERRORS issue(s) - fix before proceeding"
    return 1
  fi

  echo "[VALIDATE] All prerequisites passed"
  return 0
}

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

# Initialize a new phase cycle session
# Usage: init_cycle_session CYCLE_NAME PHASES...
# Example: init_cycle_session "cycle_20260110_1200" "PHASE-002" "PHASE-005" "PHASE-006"
init_cycle_session() {
  local CYCLE_NAME="$1"
  shift
  local PHASES=("$@")

  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  INITIALIZING CYCLE: $CYCLE_NAME"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""

  # Pre-cycle validation (P0 reliability improvements)
  check_proxy_health || echo "[WARN] Proceeding despite proxy issues"
  validate_cycle_prereqs "${PHASES[@]}" || echo "[WARN] Proceeding despite prereq issues"

  echo ""

  local CYCLE_PATH=".claude/PM/phase-cycles/${CYCLE_NAME}"
  mkdir -p "$CYCLE_PATH"

  # Export for other functions
  export CYCLE_SESSION_PATH="$CYCLE_PATH"
  export SESSION_PATH="$CYCLE_PATH"

  # Create CYCLE_STATE.yaml
  cat > "${CYCLE_PATH}/CYCLE_STATE.yaml" << EOF
meta:
  created: '$(date -Iseconds)'
  total_phases: ${#PHASES[@]}
  current_phase: 1
  checkpoint_hash: $(git rev-parse --short HEAD 2>/dev/null || echo "none")
  requested_phases:
EOF

  for phase in "${PHASES[@]}"; do
    echo "    - $phase" >> "${CYCLE_PATH}/CYCLE_STATE.yaml"
  done

  cat >> "${CYCLE_PATH}/CYCLE_STATE.yaml" << 'EOF'

phases:
EOF

  local IDX=1
  for phase in "${PHASES[@]}"; do
    cat >> "${CYCLE_PATH}/CYCLE_STATE.yaml" << EOF
  - id: $phase
    title: 'Phase $IDX'
    status: pending
    steps:
      # 7-step cycle (V2.2.0 - removed redundant post-execute checkpoint)
      execute: { status: pending }       # Step 1: Spawn /hc-execute
      audit: { status: pending }         # Step 2: Spawn /red-team
      fixes: { status: pending }         # Step 3: Spawn FLASH workers
      checkpoint_1: { status: pending }  # Step 4: git commit (after validated fixes)
      validation: { status: pending }    # Step 5: Spawn /hc-glass
      planning: { status: pending }      # Step 6: Spawn /think-tank
      checkpoint_2: { status: pending }  # Step 7: git commit + complete_cycle

EOF
    ((IDX++))
  done

  cat >> "${CYCLE_PATH}/CYCLE_STATE.yaml" << EOF
current_step:
  phase: ${PHASES[0]}
  step: execute
  status: pending
  updated_at: '$(date -Iseconds)'

outcome:
  status: initialized
  phases_completed: 0
  phases_failed: 0
EOF

  # Create ORCHESTRATOR_LOG.md
  cat > "${CYCLE_PATH}/ORCHESTRATOR_LOG.md" << EOF
# Orchestrator Log - ${CYCLE_NAME}

**Session:** ${CYCLE_NAME}
**Requested Phases:** ${#PHASES[@]} (${PHASES[*]})
**Checkpoint:** $(git rev-parse --short HEAD 2>/dev/null || echo "none")

---

## $(date +"%H:%M") - Cycle Initialized

- Created session directory
- Requested phases: ${PHASES[*]}
- Disk usage: $(df -h / | tail -1 | awk '{print $5}')

---

EOF

  echo "[INIT] Created cycle session: $CYCLE_PATH"
  echo "[INIT] CYCLE_SESSION_PATH exported"
}

# Show current cycle status summary
# Usage: cycle_status
cycle_status() {
  local STATE_PATH="${CYCLE_SESSION_PATH:-$SESSION_PATH}"
  local CYCLE_STATE="${STATE_PATH}/CYCLE_STATE.yaml"

  if [[ ! -f "$CYCLE_STATE" ]]; then
    echo "[STATUS] No active cycle"
    return 1
  fi

  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  CYCLE STATUS"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  echo "Session: $STATE_PATH"
  echo ""

  # Parse current step
  local CURRENT_PHASE=$(grep -A4 "current_step:" "$CYCLE_STATE" | grep "phase:" | head -1 | sed 's/.*phase: *//')
  local CURRENT_STEP=$(grep -A4 "current_step:" "$CYCLE_STATE" | grep "step:" | head -1 | sed 's/.*step: *//')
  local CURRENT_STATUS=$(grep -A4 "current_step:" "$CYCLE_STATE" | grep "status:" | head -1 | sed 's/.*status: *//')

  echo "Current: $CURRENT_PHASE / $CURRENT_STEP ($CURRENT_STATUS)"
  echo ""

  # Check sync status
  sync_gate

  echo ""
}
