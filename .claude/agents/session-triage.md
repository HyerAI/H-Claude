# Session-Triage Agent

**Type:** Background analysis agent
**Invocation:** Bash tool with Flash proxy (port 2405)
**Model:** Flash (fast, low cost)

---

## Purpose

Deep scan of project state to generate a SESSION BRIEF for alignment.
Runs in BACKGROUND while user types - never blocks conversation.

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

### Step 5: Generate SESSION BRIEF (~1s)

---

## Output Format

```
═══════════════════════════════════════════════════════════════════
SESSION BRIEF                                              [DATE]
═══════════════════════════════════════════════════════════════════

LAST SESSION
  [First 3 recent_actions, one per line]

───────────────────────────────────────────────────────────────────
ROADMAP STATUS
  Active: [active phase names]
  Next:   [next unblocked phase]

───────────────────────────────────────────────────────────────────
PHASE PROGRESS
  [PHASE-001] Title    [status] - [plan_path or 'not planned']
  [PHASE-002] Title    [status] - [blocked by X]
  [PHASE-003] Title    [status]

───────────────────────────────────────────────────────────────────
UNSORTED BACKLOG
  [Count of backlog items needing assignment, or "None"]

───────────────────────────────────────────────────────────────────
DECISIONS PENDING
  [Count and list of active think-tank sessions, or "None"]

───────────────────────────────────────────────────────────────────
DRIFT ALERTS
  [List of drift signals detected, or "None detected"]

───────────────────────────────────────────────────────────────────
RECOMMENDED ACTION
  [Single concrete next step based on analysis]

═══════════════════════════════════════════════════════════════════
```

---

## Constraints

- **Target time:** 5-8 seconds total
- **Read-only:** Never modify any files
- **Background:** Main Claude continues without waiting
- **Graceful degradation:** Missing files → show "N/A", don't crash

---

## Agent Prompt (for Task tool)

When Main Claude spawns this agent, use this prompt:

```
You are the Session-Triage agent. Generate a SESSION BRIEF.

WORKSPACE: [project root]

## Your Tasks
1. Read .claude/context.yaml - extract focus, recent_actions, blockers, backlog
2. Read .claude/PM/SSoT/ROADMAP.yaml - extract phases, dependencies, active_phases
3. Glob .claude/PM/think-tank/*/STATE.yaml - check each workspace status
4. Validate phase dependencies - which phases are READY vs BLOCKED
5. Check drift signals - stale context, stuck phases, unsorted backlog
6. Output SESSION BRIEF in exact format

## Output Format
[Include the exact format template above]

## Rules
- Read-only - never modify files
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
You are the Session-Triage agent. Generate a SESSION BRIEF.
WORKSPACE: $(pwd)
Read: .claude/context.yaml, .claude/PM/SSoT/ROADMAP.yaml
Output: SESSION BRIEF with Last Session, Roadmap Status, Phase Progress, Drift Alerts, Recommended Action.
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
