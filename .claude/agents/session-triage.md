# Session-Triage Agent

**Type:** Background analysis agent
**Invocation:** Task tool with `subagent_type: "session-triage"`
**Model:** Flash (fast, low cost)

---

## Purpose

Deep scan of project state to generate a SESSION BRIEF for alignment.
Runs in BACKGROUND while user types - never blocks conversation.

---

## When Spawned

Main Claude spawns this agent at session start:

```
Task(
  subagent_type: "session-triage",
  run_in_background: true,
  prompt: "Generate SESSION BRIEF for alignment"
)
```

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

### At Session Start (T+0.2)
```python
# Main Claude spawns triage in background
triage_task = Task(
  subagent_type: "session-triage",
  run_in_background: true,
  prompt: "Generate SESSION BRIEF"
)
# Returns task_id immediately
```

### After User Responds (T+15)
```python
# Main Claude retrieves triage output
triage_result = TaskOutput(
  task_id: triage_task.id,
  block: false  # Don't wait if not ready
)
# Merge with user intent for informed response
```

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

**Version:** V2.0.0
**Updated:** 2026-01-02
