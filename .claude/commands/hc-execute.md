---
version: V2.10.0
status: current
timestamp: 2026-01-04
tags: [command, execution, orchestration, plan, oraca, think-tank]
description: "SWEEP & VERIFY plan execution protocol with Oraca Phase Orchestrators"
templates: .claude/templates/template-prompts/hc-execute/
adr: ADR-004-hc-execute-improvements.md
---

# /hc-execute - SWEEP & VERIFY Execution

**Philosophy:** Trust but Verify. Assume 20% of work and documentation will be missed or incomplete.

**Purpose:** Execute an approved plan with rigorous QA loops, independent verification, and adversarial sweep.

---

## Quick Start

```markdown
/hc-execute

PLAN_PATH: [path to execution-plan.yaml from think-tank]
MODE: [standard|careful]
```

Or by topic name (auto-locates approved plan):
```markdown
/hc-execute TOPIC: auth_system
```

---

## Architecture

```
HC invokes /hc-execute
     ↓
Spawn Flash Orchestrator (BACKGROUND)
     ↓
┌────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: PARSE, BATCH & CONTRACT                                      │
│  → INTERFACES.md                                                       │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 2: PHASED EXECUTION (via Oraca[X] Phase Orchestrators)          │
│    Oraca[X] (Flash) → Workers (Flash) → Phase QA (Pro) → Report        │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 3: QA SYNTHESIS (Pro) → QA_SYNTHESIS.md                         │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 4: SWEEP (Pro - "20% Hunter") → SWEEP_REPORT.md                 │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 5: VALIDATION & REPORT → COMPLETION_REPORT.md                   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Oraca[X]: Phase Orchestrators

**Oraca** = **Ora**cle + **Ca**ptain. Flash agents that own one phase.

**Why Oraca:**
- Context Protection - Opus stays clean
- Phase Isolation - Failures don't pollute other phases
- Scalability - 50+ tasks won't overwhelm
- Built-in QA Gate - Each phase verified before proceeding

**Responsibilities:**
1. Receive phase spec from Opus
2. Spawn Flash workers (max 3 parallel)
3. Collect worker evidence
4. Handle micro-retries (up to 3 per task) with error-feedback
5. Spawn Pro Phase QA
6. Report: `COMPLETE` | `PARTIAL` | `BLOCKED`

### Micro-Retry Protocol (ADR-002)

When a worker fails, Oraca applies local retry before escalating:

```
Attempt 1: Standard execution
Attempt 2: Error + context + "Try different approach"
Attempt 3: Errors + context + "Last attempt - simplify"
Attempt 4+: ESCALATE to Orchestrator
```

**Key principle:** Worker retries at Oraca level (cheap, fast) before escalating to Orchestrator (expensive, context-heavy).

**Variables passed on retry:**
- `PREVIOUS_ERROR`: Error message from failed attempt
- `ATTEMPT_NUMBER`: Current attempt (1, 2, 3)
- `RETRY_GUIDANCE`: Specific guidance for retry approach

**Logged in:** `ORACA_LOG.md` with attempt number, error, and adjustment made

**Boundaries:**
- Cannot spawn other Oraca (no recursion)
- Cannot modify tasks outside its phase
- Must write to `PHASE_X/` folder
- Must report back to Opus

---

## Session Folder Structure

```
.claude/PM/hc-execute/${session-slug}/
├── EXECUTION_STATE.md          # Dashboard
├── ORCHESTRATOR_LOG.md         # Flight Recorder
├── COMMANDS.md                 # HC→Orchestrator channel
├── INTERFACES.md               # Shared contracts
├── PHASE_1/
│   ├── ORACA_LOG.md
│   ├── WORKER_OUTPUTS/
│   │   └── TASK_*_EVIDENCE.md
│   ├── PHASE_QA.md
│   └── PHASE_REPORT.md
├── PHASE_N/
├── ANALYSIS/
│   ├── QA_SYNTHESIS.md
│   └── SWEEP_REPORT.md
└── COMPLETION_REPORT.md
```

### EXECUTION_STATE.md Schema

```yaml
# Current execution status - updated after each phase
session:
  plan_slug: workflow_fixes_20260102
  plan_path: .claude/PM/think-tank/.../execution-plan.yaml
  mode: standard  # standard | careful
  started: '2026-01-02T14:30:00Z'

checkpoint:
  id: chkpt-20260102-143000-workflow-fixes
  commit_hash: abc123
  rollback_cmd: 'git reset --hard abc123'

status: executing  # initializing | executing | paused | complete | failed | rolled_back

current_phase: 2  # Which phase is currently active
total_phases: 6

phases:
  - id: 1
    title: 'Phase Completion Protocol'
    status: complete  # pending | executing | complete | failed | skipped
    started: '2026-01-02T14:31:00Z'
    completed: '2026-01-02T14:35:00Z'
    tasks_total: 2
    tasks_complete: 2
    tasks_failed: 0
  - id: 2
    title: 'Checkpoint Integration'
    status: executing
    started: '2026-01-02T14:35:30Z'
    tasks_total: 2
    tasks_complete: 1
    tasks_failed: 0

# For crash recovery
last_action:
  timestamp: '2026-01-02T14:36:00Z'
  action: 'Task 2.1 completed'
  next: 'Task 2.2'

# Ticket-level tracking (Diffusion Development)
tickets:
  current_ticket: 'TICKET-2.1.3'
  completed: ['TICKET-1.1.1', 'TICKET-1.1.2', 'TICKET-2.1.1', 'TICKET-2.1.2']
  failed: []

# Lookahead status (Track B)
lookahead:
  last_check: '2026-01-02T14:35:00Z'
  status: PASS  # PASS | WARN | FAIL
  warnings: []
  blocks: []
```

---

## Mode Selection

| Mode | Parallel Workers | QA Rigor | Use Case |
|------|------------------|----------|----------|
| **Standard** | 3 | Normal | Most executions |
| **Careful** | 2 | Enhanced | High-risk, critical |

---

## Execution Rules

| Rule | Requirement |
|------|-------------|
| Parallel Limit | Max 3 workers simultaneously |
| State Isolation | Each worker gets clean context |
| Dependency Lock | Task B waits for Task A VERIFIED |
| Done Definition | Done = QA APPROVED (not worker claim) |
| Evidence Required | Every worker produces artifacts |

---

## Proxy Configuration

```bash
# HC-Orca (2414) - Orchestrator (light coordination)
# HC-Work (2412) - Workers, git-engineer
# HC-Work-R (2413) - Oraca (execution with reasoning)
# HC-Reas-B (2411) - Phase QA, QA Synthesis, Sweeper
ANTHROPIC_API_BASE_URL=http://localhost:241X claude --dangerously-skip-permissions -p "PROMPT"
```

---

## Timeout Configuration

Background orchestrators MUST use timeout wrapper to prevent zombie processes.

```bash
# Default: 60 minutes for execution workflow
TIMEOUT=${TIMEOUT:-3600}

# Spawn pattern with timeout
timeout --foreground --signal=TERM --kill-after=60 $TIMEOUT \
  bash -c 'ANTHROPIC_API_BASE_URL=http://localhost:2414 claude --dangerously-skip-permissions -p "..."'

# Check exit code
EXIT_CODE=$?
if [ $EXIT_CODE -eq 124 ]; then
  echo "[CRITICAL] Orchestrator killed after timeout ($TIMEOUT seconds)"
  echo "status: TIMEOUT_KILLED" > "${SESSION_PATH}/TIMEOUT_INTERRUPTED.md"
fi
```

**Timeout Values:**
| Context | Default | Override |
|---------|---------|----------|
| Full orchestrator | 60 min | `--timeout=N` |
| Oraca (phase) | 20 min | (inside orchestrator) |
| Flash Worker | 10 min | (inside orchestrator) |
| Pro QA/Synth | 15 min | (inside orchestrator) |

---

## Orchestrator Protocol

Spawn background Flash orchestrator using template `orchestrator.md` with timeout wrapper:

| Variable | Value |
|----------|-------|
| PLAN_PATH | Path to execution-plan.yaml |
| MODE | standard or careful |
| WORKSPACE | $(pwd) |

---

## Phase 0: PRE-EXECUTION CHECKPOINT

BEFORE any execution begins:

1. Check `git status` - if dirty, prompt to commit first
2. Spawn git-engineer with operation: `checkpoint`
   ```bash
   ANTHROPIC_API_BASE_URL=http://localhost:2412 claude --dangerously-skip-permissions -p "
   You are git-engineer. Create a checkpoint.
   Read: .claude/agents/git-engineer.md for your protocol.
   OPERATION: checkpoint
   DETAILS: pre-execution for ${PLAN_SLUG}
   WORKSPACE: $(pwd)
   "
   ```
3. Store `ROLLBACK_HASH` in EXECUTION_STATE.md:
   ```yaml
   checkpoint:
     hash: ${COMMIT_HASH}
     timestamp: ${ISO_TIMESTAMP}
     plan_slug: ${PLAN_SLUG}
   ```
4. Log: `[CHECKPOINT] Created at ${COMMIT_HASH}. Rollback: git reset --hard ${COMMIT_HASH}`

---

## Phase 1: Parse, Batch & Contract

1. Read plan at PLAN_PATH
2. Extract phases (or group by dependencies)
3. For each phase: Task ID, Description, Dependencies, Success criteria, Files
4. Generate INTERFACES.md
5. Create phase folders
6. Log: `[PARSE] Found N phases, M tasks.`

---

## Phase 2: Phased Execution

For each phase, spawn Oraca[X] using template `oraca_phase.md`:

| Variable | Value |
|----------|-------|
| SESSION_PATH | Session folder path |
| PHASE_NUM | Phase number |
| PHASE_TASKS | Tasks for phase |
| RELEVANT_INTERFACES | Required interfaces |
| GOAL | Overall objective from plan |
| BEDROCK_FILES | Foundational context files |
| WORKSPACE | Current working directory |

Oraca spawns:
- Workers using `worker_task.md` (with triangulated context)
- Phase QA using `qa_phase.md`

**Wait for each Oraca before proceeding.**

### Triangulated Context for Workers

Workers receive context via the ticket's `triangulated_context`:

```yaml
triangulated_context:
  goal: "The specific outcome from NS/Phase"
  bedrock:
    - "path/to/file1.md"  # Worker MUST read before executing
    - "path/to/file2.ts"
  instruction: "The specific action to take"
```

Workers read bedrock files first, then execute instruction to achieve goal.

### Lookahead Loop (Dual-Track Execution)

After each ticket completion, run `validator_lookahead.md`:

| Track A: Reality | Track B: Horizon |
|------------------|------------------|
| WR builds code | VA checks NS alignment |
| QA tests output | VA checks future blocking |

**Process:**
1. Worker completes ticket → writes evidence
2. QA validates ticket requirements (Track A)
3. Spawn `validator_lookahead.md` (Track B):
   - Does this code block future NS features?
   - Does this create conflicting technical debt?
4. **PASS** → proceed to next ticket
5. **WARN** → document, proceed with caution
6. **FAIL** → pause, escalate to Orchestrator

**Lookahead Template:** `.claude/templates/template-prompts/think-tank/validator_lookahead.md`

---

## Phase 3: QA Synthesis

Spawn Pro agent with `synthesizer_qa.md`:

| Variable | Value |
|----------|-------|
| SESSION_PATH | Session folder path |

Analyzes all phase QA reports, identifies patterns.

---

## Phase 4: Sweep

Spawn Pro agent with `sweeper.md`:

| Variable | Value |
|----------|-------|
| SESSION_PATH | Session folder path |
| PLAN_PATH | Original plan path |

If GAPS_FOUND → create fix tasks → Oraca[FIX] → re-sweep.

---

## Phase 5: Validation & Report

1. Run automated checks (tests, linting)
2. Generate COMPLETION_REPORT.md
3. Log: `[DONE] Status: [STATUS]`
4. Report to HC

---

## Phase 6: ROADMAP SYNC

On successful completion (all phases PASS):

1. Read ROADMAP.yaml from `.claude/PM/SSoT/ROADMAP.yaml`
2. Find phase by matching `plan_path` to current execution plan
3. Update `phase.status` → `'complete'`
4. Scan dependencies: unlock any phases where all deps are complete
5. Update `active_phases[]` array (remove completed, add newly unblocked)
6. Write ROADMAP.yaml
7. Log: `[ROADMAP] Phase PHASE-XXX marked complete. N phases unlocked.`

**On Failure (SWEEP finds critical gaps or QA fails):**

1. Do NOT update ROADMAP.yaml status
2. Log: `[ROADMAP] Phase PHASE-XXX execution incomplete. Status unchanged.`
3. Present COMPLETION_REPORT.md with failures
4. Offer recovery options:
   - `RETRY_FAILED` - Re-run only failed tasks
   - `ROLLBACK` - Restore to pre-execution checkpoint
   - `MANUAL` - User fixes issues, runs again

**If ROLLBACK selected:**

1. Spawn git-engineer with rollback operation:
   ```bash
   ANTHROPIC_API_BASE_URL=http://localhost:2412 claude --dangerously-skip-permissions -p "
   You are git-engineer. Perform rollback.
   Read: .claude/agents/git-engineer.md for your protocol.
   OPERATION: rollback
   ROLLBACK_HASH: ${ROLLBACK_HASH}
   WORKSPACE: $(pwd)
   "
   ```
2. Log: `[ROLLBACK] Restored to checkpoint ${ROLLBACK_HASH}`
3. Update EXECUTION_STATE.md: `status: rolled_back`

---

## Edge Cases

### Parallel Phase Execution

If multiple phases have no blocking dependencies:
- Execute sequentially by default (safer, predictable)
- Future: Add `--parallel` flag for concurrent execution

### Execution Failure Recovery

If execution fails mid-phase:

1. COMPLETION_REPORT shows partial status
2. Offer recovery options:
   - `RETRY_FAILED` - Re-run only failed tasks
   - `ROLLBACK` - Restore to checkpoint
   - `MANUAL` - User fixes issues, runs `/hc-execute` again
3. `RETRY_FAILED`:
   - Reads EXECUTION_STATE.md for failed task list
   - Re-spawns workers for those tasks only
   - Re-runs SWEEP after
4. `ROLLBACK`:
   - Spawns git-engineer with rollback operation
   - Restores to pre-execution checkpoint
5. `MANUAL`:
   - Preserves EXECUTION_STATE.md
   - User fixes issues manually
   - Re-run with same PLAN_PATH continues from last state

### Session Crash Recovery

If session crashes during execution:

1. EXECUTION_STATE.md shows last known state:
   ```yaml
   status: in_progress
   current_phase: 2
   completed_tasks: [TASK-1.1, TASK-1.2, TASK-2.1]
   failed_tasks: []
   checkpoint:
     hash: abc123
   ```
2. Resume: `/hc-execute --resume ${SESSION_SLUG}`
3. System reads state, continues from last checkpoint
4. Already-completed tasks are skipped

### Hotfix During Execution

If urgent fix needed while executing:

1. Complete current task (don't interrupt mid-task)
2. Create hotfix commit outside execution flow
3. Resume execution - state is preserved
4. Hotfix changes won't be rolled back if execution fails

---

## RETRY_FAILED Test Procedure (ADR-004)

To validate the RETRY_FAILED recovery path works correctly:

### Test Steps

1. **Create synthetic failure:**
   - Modify one worker task to intentionally fail (e.g., reference non-existent file)
   - Run `/hc-execute` on a small test plan

2. **Verify failure capture:**
   - Check EXECUTION_STATE.md shows the failed task in `failed_tasks[]`
   - Check ORACA_LOG.md shows retry attempts (3 attempts before failure)
   - Check PHASE_REPORT.md shows status: PARTIAL or BLOCKED

3. **Run RETRY_FAILED:**
   - Invoke recovery option when presented
   - Verify ONLY the failed task is re-spawned
   - Verify previously successful tasks are NOT re-run

4. **Verify re-sweep:**
   - After retry completes, SWEEP runs again
   - SWEEP_REPORT.md shows fresh audit

### Expected Behavior

```yaml
# Before RETRY_FAILED
failed_tasks: [TASK-2.3]
completed_tasks: [TASK-1.1, TASK-1.2, TASK-2.1, TASK-2.2]

# RETRY_FAILED spawns worker for TASK-2.3 only

# After successful retry
failed_tasks: []
completed_tasks: [TASK-1.1, TASK-1.2, TASK-2.1, TASK-2.2, TASK-2.3]
```

### Success Criteria

- [ ] Failed task identified correctly
- [ ] Only failed task re-runs
- [ ] SWEEP re-runs after retry
- [ ] State updates correctly

---

## Template Reference

All prompts in: `.claude/templates/template-prompts/hc-execute/`

| Template | Model | Purpose |
|----------|-------|---------|
| `orchestrator.md` | Flash | Main coordination |
| `oraca_phase.md` | Flash | Phase orchestration |
| `worker_task.md` | Flash | Task execution (with triangulated context) |
| `qa_phase.md` | Pro | Phase QA review |
| `synthesizer_qa.md` | Pro | Cross-phase analysis |
| `sweeper.md` | Pro | 20% gap hunting |

### Diffusion Validation (Lookahead Loop)

| Template | Model | Purpose |
|----------|-------|---------|
| `validator_lookahead.md` | Flash | Track B horizon check after each ticket |

**Location:** `.claude/templates/template-prompts/think-tank/validator_lookahead.md`

---

## The Execution Mantra

```
I parse phases before I execute.
I delegate to Oraca, not workers.
I isolate each phase's context.
I verify at phase boundaries.
I synthesize before I sweep.
I hunt the 20% that was missed.
Trust but Verify.
```

---

## Integration with Think-Tank

```
/think-tank → DECIDE → execution-plan.yaml
                           ↓
/hc-execute TOPIC: {topic}
                           ↓
                COMPLETION_REPORT.md
```

---

## Related

| Related | When to Use Instead |
|---------|---------------------|
| `/think-tank` | Research, decisions, plan generation |
| Direct implementation | Single small task, no QA needed |
| Manual execution | HC in loop for each task |

---

**Version:** V2.10.0 | Added timeout wrapper for zombie prevention (BUG-001)
