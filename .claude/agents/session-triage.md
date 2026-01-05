# Session-Triage Agent

**Type:** Background analysis agent
**Invocation:** Bash tool with Flash proxy (port 2405)
**Model:** Flash (fast, low cost)

---

## Purpose

Deep scan of project state to update SESSION_STATUS.md for HC alignment.
Runs in BACKGROUND while user types - never blocks conversation.

**Output:** Writes to `.claude/PM/SESSION_STATUS.md` (live document, not stdout).

---

## When Spawned

Main Claude spawns this agent at session start using **Bash tool with proxy**.

### Step 0: Cleanup Previous Triage (MANDATORY)

**Before spawning a new triage agent, kill any orphans from crashed sessions:**

```bash
# Kill any orphan session-triage processes from previous sessions
pkill -f "Session-Triage agent" 2>/dev/null || true
```

This prevents zombie accumulation from crashed sessions.

### Step 1: Spawn with Timeout

```bash
# Use Bash tool with run_in_background: true
# Timeout: 60s (triage should complete in 5-8s, 60s is generous safety margin)
timeout --foreground --signal=TERM --kill-after=10 60 \
  bash -c 'ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "
You are the Session-Triage agent. Generate a SESSION BRIEF.
WORKSPACE: $(pwd)
[... triage prompt ...]
"'
```

**Note:** Task tool's `subagent_type` parameter only recognizes hardcoded values (general-purpose, Explore, Plan, etc.). Custom agents must use the Bash+proxy approach.

---

## Execution Steps

### Step 1: Load Context (~1s)
```
Read .claude/context.yaml
Extract:
  - meta.last_modified
  - focus.current_objective
  - recent_actions (last 10)
  - blockers
  - backlog (unsorted tasks)
  - think_tank list

Read .claude/PM/SSoT/ROADMAP.yaml
Extract:
  - active_phases
  - phases[].status
  - phases[].dependencies
  - phases[].plan_path
  - side_quests

Read .claude/PM/HC-LOG/HC-FAILURES.md
Extract:
  - Last 5 incidents (for Recent Failures section)
```

### Step 2: Scan Think-Tank Workspaces (~2s)
```
Glob .claude/PM/think-tank/*/STATE.yaml

For each workspace:
  - Read STATE.yaml
  - Check lifecycle.type: roadmap | phase | side_quest
  - Check status: active | paused | decided | archived
  - If active/paused → flag as PENDING
  - Count open_questions
```

### Step 3: Validate Phase Dependencies (~1s)
```
For each phase in ROADMAP.yaml:
  If dependencies[] is empty → READY
  If all dependencies complete → READY
  If dependencies incomplete → BLOCKED
  If circular dependency → Flag as DRIFT
```

### Step 4: Check Drift Signals (~1s)
```
□ last_modified > 7 days ago?           → STALE_CONTEXT
□ Active phase with no recent progress? → STUCK_PHASE
□ Phase blocked > 3 days?               → BLOCKED_PHASE
□ Think-tank active > 5 days?           → ORPHAN_DECISION
□ Unsorted backlog items > 5?           → UNSORTED_BACKLOG
□ NORTHSTAR-ROADMAP misalignment?       → ALIGNMENT_DRIFT
```

### Step 5: Write SESSION_STATUS.md (~1s)

**Output target:** `.claude/PM/SESSION_STATUS.md`

---

## Output Format

Write to `.claude/PM/SESSION_STATUS.md`:

```markdown
# Session Status

Updated by session-triage agent at session start.
HC reviews this instead of ephemeral triage output.

---

last_updated: [ISO timestamp]

## Last Session

- [First 3 recent_actions, one per line]

## Roadmap Status

- Active: [active phase names]
- Next: [next unblocked phase]

## Phase Progress

| Phase | Status | Notes |
|-------|--------|-------|
| [PHASE-001] Title | [status] | [plan_path or 'not planned'] |
| [PHASE-002] Title | [status] | [blocked by X] |

## Unsorted Backlog

- [Count of backlog items needing assignment, or "None"]

## Decisions Pending

- [Count and list of active think-tank sessions, or "None"]

## Recent Failures (from HC-FAILURES.md)

- [Last 3-5 incidents from HC-FAILURES.md, or "None"]

## Drift Alerts

- [List of drift signals detected, or "None detected"]

## Recommended Action

- [Single concrete next step based on analysis]

---

*This file is a live document updated by session-triage at each session start.*
```

---

## Constraints

- **Target time:** 5-8 seconds total
- **Write target:** Only writes to `.claude/PM/SESSION_STATUS.md`
- **Background:** Main Claude continues without waiting
- **Graceful degradation:** Missing files → show "N/A", don't crash

---

## Agent Prompt (for Task tool)

When Main Claude spawns this agent, use this prompt:

```
You are the Session-Triage agent. Update SESSION_STATUS.md for HC.

WORKSPACE: [project root]

## Your Tasks
1. Read .claude/context.yaml - extract focus, recent_actions, blockers, backlog
2. Read .claude/PM/SSoT/ROADMAP.yaml - extract phases, dependencies, active_phases
3. Read .claude/PM/HC-LOG/HC-FAILURES.md - extract last 5 incidents
4. Glob .claude/PM/think-tank/*/STATE.yaml - check each workspace status
5. Validate phase dependencies - which phases are READY vs BLOCKED
6. Check drift signals - stale context, stuck phases, unsorted backlog
7. Write SESSION_STATUS.md with all findings

## Output Target
Write to: .claude/PM/SESSION_STATUS.md

## Rules
- Write ONLY to SESSION_STATUS.md
- Graceful - missing data shows "N/A"
- Fast - target <8 seconds
- One recommended action only
```

---

## Integration with Main Claude

### Session Start Protocol

**Step 1: Cleanup orphans (T+0)**
```bash
# Kill any orphan triage from crashed sessions
pkill -f "Session-Triage agent" 2>/dev/null || true
```

**Step 2: Spawn with timeout (T+0.2)**
```bash
# Use Bash tool with run_in_background: true
# 60s timeout (generous margin for 5-8s expected runtime)
timeout --foreground --signal=TERM --kill-after=10 60 \
  bash -c 'ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "
You are the Session-Triage agent. Update SESSION_STATUS.md for HC.
WORKSPACE: $(pwd)
Read: .claude/context.yaml, .claude/PM/SSoT/ROADMAP.yaml, .claude/PM/HC-LOG/HC-FAILURES.md
Write to: .claude/PM/SESSION_STATUS.md with Last Session, Roadmap Status, Phase Progress, Recent Failures, Drift Alerts, Recommended Action.
"'
# Returns shell_id immediately
```

**Step 3: Retrieve output (T+15 or after user responds)**
```python
# MUST block to ensure cleanup
triage_result = TaskOutput(
  task_id: shell_id,
  block: true,
  timeout: 30000  # 30s max wait
)
# Merge with user intent for informed response
```

### CRITICAL: Resource Cleanup

**ALWAYS retrieve TaskOutput with `block: true` after background tasks complete.**

Why:
- Background agents spawn as subprocesses
- Unretrieved tasks may become zombie processes
- Zombies consume system resources indefinitely

**The Three Safety Layers:**

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| **1. Orphan cleanup** | `pkill` at session start | Kill zombies from crashed sessions |
| **2. Timeout wrapper** | `timeout 60` on spawn | Prevent indefinite runs |
| **3. TaskOutput retrieval** | `block: true` | Ensure subprocess cleanup |

Pattern:
```python
# 1. Cleanup orphans first
Bash("pkill -f 'Session-Triage agent' 2>/dev/null || true")

# 2. Spawn in background with timeout
task = Bash(run_in_background: true, command: "timeout 60 bash -c '...'")

# 3. Do other work while agent runs
# ...

# 4. ALWAYS retrieve with block: true when done
result = TaskOutput(task_id: task.id, block: true, timeout: 30000)
# This ensures subprocess cleanup
```

**Never fire-and-forget background tasks.** Always retrieve their output.

---

## Example Execution

**Input:** User opens session with "Hi Claude"

**Background Processing:**
1. Reads context.yaml → Current focus on roadmap implementation
2. Reads ROADMAP.yaml → PHASE-001 active, PHASE-002 blocked
3. Scans think-tank workspaces → 1 phase session active
4. Checks drift → 2 unsorted backlog items

**Output:**
```
═══════════════════════════════════════════════════════════════════
SESSION BRIEF                                          2026-01-02
═══════════════════════════════════════════════════════════════════

LAST SESSION
  Implemented ROADMAP.yaml hierarchy system
  Updated think-tank.md with --roadmap and --phase flags
  Updated CLAUDE.md with Product Owner workflow

───────────────────────────────────────────────────────────────────
ROADMAP STATUS
  Active: Foundation (PHASE-001)
  Next:   MVP (PHASE-002) - blocked by PHASE-001

───────────────────────────────────────────────────────────────────
PHASE PROGRESS
  [PHASE-001] Foundation   active - execution-plan.yaml ready
  [PHASE-002] MVP          planned - blocked by PHASE-001
  [PHASE-003] Hardening    planned - blocked by PHASE-002

───────────────────────────────────────────────────────────────────
UNSORTED BACKLOG
  2 items need assignment to phases

───────────────────────────────────────────────────────────────────
DECISIONS PENDING
  None - all think-tank sessions complete

───────────────────────────────────────────────────────────────────
DRIFT ALERTS
  UNSORTED_BACKLOG: 2 items in context.yaml backlog

───────────────────────────────────────────────────────────────────
RECOMMENDED ACTION
  Assign backlog items to phases, then continue PHASE-001 execution.

═══════════════════════════════════════════════════════════════════
```

---

**Version:** V2.1.0
**Updated:** 2026-01-04
**Changes:** Added orphan cleanup, timeout wrapper, three safety layers (BUG-001)
