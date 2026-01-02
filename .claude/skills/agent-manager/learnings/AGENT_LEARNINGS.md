# Agent Manager Learnings

**Purpose:** Knowledge base for patterns, mistakes, and improvements discovered during agent operations.

---

## Learning Log

### 2025-12-30 - Stall Detection Protocol - Pattern

**Command:** update (all orchestration commands)
**Context:** Background agents can hang indefinitely with no visibility. Orchestrators spawn agents but can't tell if they're working or stuck.
**Learning:**

**Problem:** LLMs can hang on API calls, get stuck in loops, or silently fail. Without monitoring, orchestrators wait forever.

**Solution: Pattern 9 - Stall Detection Protocol**

1. **Heartbeat Files:** Every sub-agent writes `HEARTBEAT_${ID}.md` on start and updates every 2-3 minutes
2. **Activity Polling:** Orchestrator checks heartbeat mtime after task timeout
3. **3-Level Escalation:**
   - NUDGE: Write `[NUDGE]` to agent's COMMANDS.md
   - RESPAWN: Kill and spawn fresh with same task
   - ESCALATE: Alert HD

**Task Timeouts:**
| Type | Timeout |
|------|---------|
| QUICK | 5 min |
| STANDARD | 10 min |
| RESEARCH | 20 min |
| ORCHESTRATION | 30 min |

**Applied To:**
- execute-plan.md V2.3.0
- hc-plan.md V2.3.0
- glass.md V1.3.0
- init-sim.md V1.2.0
- red-team.md V2.2.0
- ORCHESTRATION_PATTERNS.md V1.2.0

**Recurrence:** 1 (new pattern, first implementation)
**Promotion Ready:** NO - needs validation in production

---

### 2025-12-30 - execute-plan Orchestrator - Pattern

**Command:** update
**Context:** execute-plan command ran 3 times but orchestrator never updated ORCHESTRATOR_LOG.md after spawning Oraca sub-agents
**Learning:**

**Problem:** Orchestrator spawns sub-agents via `claude -p` (one-shot bash) and then terminates. It never:
1. Waits for sub-agent completion
2. Logs the completion event
3. Continues to next phase

**Evidence:**
- ORCHESTRATOR_LOG.md stopped at `[SPAWN] Oraca[0] dispatched`
- Oraca[0] actually completed all 5 tasks (evidence files exist)
- But orchestrator exited before receiving results

**Root Cause:** Fire-and-forget spawn pattern. Bash `claude -p` returns immediately when backgrounded or when the parent doesn't wait.

**Solution Pattern:**

1. **Synchronous Sub-Agent Execution:**
   ```bash
   # WRONG - fire and forget
   claude -p "..." &

   # RIGHT - wait for completion
   result=$(claude -p "...")
   echo "$result"  # Now log the result
   ```

2. **Log AFTER Each Operation:**
   ```
   [SPAWN] Oraca[X] dispatched
   ... wait for completion ...
   [PHASE] Oraca[X] returned. Status: COMPLETE.
   ```

3. **State File Communication:**
   - Sub-agent writes PHASE_REPORT.md when complete
   - Orchestrator polls for PHASE_REPORT.md existence
   - Or uses command substitution to capture output

4. **Background Orchestrator with Sync Sub-Agents:**
   - Orchestrator runs in background (HD can continue)
   - But sub-agents run SYNCHRONOUSLY relative to orchestrator
   - This allows orchestrator to log each completion

**Recurrence:** 3 (happened 3 times per user)
**Promotion Ready:** YES - Promote to template section for spawn patterns

---

### Pattern: Background Orchestrator Communication

**Problem:** HD wants to send messages to running orchestrator

**Solution:**

1. **COMMANDS.md Communication Channel:**
   ```
   SESSION_PATH/COMMANDS.md  # HD writes here
   ```
   - Orchestrator polls this file between phases
   - Format: `[TIMESTAMP] [COMMAND] message`
   - Commands: PAUSE, RESUME, ABORT, STATUS, FOCUS_ON_TASK

2. **Orchestrator Polling Loop:**
   ```bash
   # After each phase completion:
   if [ -f "${SESSION_PATH}/COMMANDS.md" ]; then
       process_commands
   fi
   ```

3. **Bidirectional Status:**
   - EXECUTION_STATE.md: Orchestrator writes (current status)
   - COMMANDS.md: HD writes (commands to orchestrator)

**Recurrence:** 1
**Promotion Ready:** NO - needs more validation

---

## Promoted Patterns

(Patterns with 3+ occurrences get promoted here)

### Synchronous Sub-Agent Spawn (Promoted: 2025-12-30)

**Use Case:** Any orchestrator that spawns sub-agents and needs their results

**Template:**
```bash
# Spawn sub-agent and wait for result
log_event "SPAWN" "Spawning ${AGENT_NAME} for ${DESCRIPTION}"

AGENT_OUTPUT=$(ANTHROPIC_API_BASE_URL=http://localhost:${PORT} claude --dangerously-skip-permissions -p "
${PROMPT}
" 2>&1)

# Capture exit status
AGENT_EXIT=$?

# Log the result immediately after return
if [ $AGENT_EXIT -eq 0 ]; then
    log_event "COMPLETE" "${AGENT_NAME} returned successfully"
else
    log_event "ERROR" "${AGENT_NAME} failed with exit code $AGENT_EXIT"
fi

# Parse result and continue
```

**Anti-Pattern (DO NOT USE):**
```bash
# WRONG: Fire and forget - orchestrator exits before sub-agent completes
ANTHROPIC_API_BASE_URL=http://localhost:${PORT} claude --dangerously-skip-permissions -p "..." &
```

---

## Template Updates Queue

| Learning | Target Template | Status |
|----------|-----------------|--------|
| Sync sub-agent spawn | execute-plan/oraca-prompt.md | DONE (2025-12-30) |
| Sync sub-agent spawn | _base.md orchestrator section | PENDING |
| COMMANDS.md channel | execute-plan.md | DONE (2025-12-30) |

## Applied Across Commands (2025-12-30)

The synchronous spawn pattern was added to all orchestration commands:

| Command | Version | Status |
|---------|---------|--------|
| execute-plan.md | V2.2.0 | ✅ Updated |
| hc-plan.md | V2.2.0 | ✅ Updated |
| glass.md | V1.2.0 | ✅ Updated |
| init-sim.md | V1.1.0 | ✅ Updated |
| red-team.md | V2.1.0 | ✅ Updated |

Each command now includes:
- `## CRITICAL: Sub-Agent Spawn Rules` section in orchestrator prompt
- Correct synchronous spawn code pattern
- Anti-pattern warning (fire-and-forget)
- Note for nested sub-agent spawns (Pro→Flash)

---

*Last Updated: 2025-12-30*
*Format: Append new learnings at top of Learning Log section*
