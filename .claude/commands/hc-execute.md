---
version: V3.1.0
status: current
timestamp: 2026-01-10
tags: [command, execution, orchestration, plan, oraca, think-tank]
description: "SWEEP & VERIFY plan execution protocol with Oraca Phase Orchestrators"
templates_path: .claude/templates/template-prompts/hc-execute/
adr: ADR-004-hc-execute-improvements.md
session_base: .claude/PM/hc-execute/

# Execution Modes
modes:
  standard: { parallel: 3, qa_rigor: normal }
  careful: { parallel: 2, qa_rigor: enhanced }

# Proxies (port → role)
proxies:
  2414: orchestrator  # HC-Orca (Flash), light coordination
  2415: oraca         # HC-Orca-R (Pro), phase execution - upgraded for complex coordination
  2412: worker        # HC-Work (Flash), task execution, git-engineer
  2411: qa            # HC-Reas-B (Pro), Phase QA, QA Synthesis, Sweeper

# Timeouts (seconds)
timeouts: { orchestrator: 3600, oraca: 1200, worker: 600, qa: 900 }

# Rules
rules:
  parallel_limit: 3
  dependency_lock: "Task B waits for Task A VERIFIED"
  done_definition: "QA APPROVED (not worker claim)"
  micro_retry_limit: 3

# Templates (all in templates_path except noted)
templates:
  - orchestrator.md      # Flash - Main coordination
  - oraca_phase.md       # Pro - Phase orchestration (upgraded for complex coordination)
  - worker_task.md       # Flash - Task execution (triangulated context)
  - qa_phase.md          # Pro - Phase QA review
  - synthesizer_qa.md    # Pro - Cross-phase analysis
  - sweeper.md           # Pro - 20% gap hunting
  - validator_lookahead.md  # Flash - Track B horizon (in think-tank/)

# Recovery options
recovery:
  retry_failed: "Re-run failed tasks only, re-sweep after"
  rollback: "git reset --hard to checkpoint via git-engineer"
  manual: "Preserve state, user fixes, re-run continues"
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
│  PHASE 0: PRE-EXECUTION CHECKPOINT                                      │
│  → Create rollback point                                                │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 1: PARSE, BATCH & CONTRACT                                      │
│  → INTERFACES.md                                                       │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 2: PHASED EXECUTION (via Oraca[X] Phase Orchestrators)          │
│    Oraca[X] (Pro) → Workers (Flash) → Phase QA (Pro) → Report          │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 3: QA SYNTHESIS (Pro) → QA_SYNTHESIS.md                         │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 4: SWEEP (Pro - "20% Hunter") → SWEEP_REPORT.md                 │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 5: VALIDATION & REPORT → COMPLETION_REPORT.md                   │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 6: ROADMAP SYNC → Update ROADMAP.yaml on success                │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Oraca[X]: Phase Orchestrators

**Oraca** = **Ora**cle + **Ca**ptain. Pro agents that own one phase (upgraded from Flash for complex coordination).

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

**Variables passed on retry:** `PREVIOUS_ERROR`, `ATTEMPT_NUMBER`, `RETRY_GUIDANCE`

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
current_phase: 2
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

last_action:
  timestamp: '2026-01-02T14:36:00Z'
  action: 'Task 2.1 completed'
  next: 'Task 2.2'

tickets:
  current_ticket: 'TICKET-2.1.3'
  completed: ['TICKET-1.1.1', 'TICKET-1.1.2']
  failed: []

lookahead:
  last_check: '2026-01-02T14:35:00Z'
  status: PASS  # PASS | WARN | FAIL
  warnings: []
  blocks: []
```

---

## Orchestrator Protocol

Spawn background Flash orchestrator using template `orchestrator.md`:

| Variable | Value |
|----------|-------|
| PLAN_PATH | Path to execution-plan.yaml |
| MODE | standard or careful |
| WORKSPACE | $(pwd) |

### Spawn Pattern with Timeout

```bash
TIMEOUT=${TIMEOUT:-3600}
timeout --foreground --signal=TERM --kill-after=60 $TIMEOUT \
  bash -c 'ANTHROPIC_API_BASE_URL=http://localhost:2414 claude --dangerously-skip-permissions -p "..."'

EXIT_CODE=$?
if [ $EXIT_CODE -eq 124 ]; then
  echo "[CRITICAL] Orchestrator killed after timeout"
  echo "status: TIMEOUT_KILLED" > "${SESSION_PATH}/TIMEOUT_INTERRUPTED.md"
fi
```

---

## Phase 0: PRE-EXECUTION CHECKPOINT

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
3. Store `ROLLBACK_HASH` in EXECUTION_STATE.md
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

Oraca spawns workers (`worker_task.md`) and Phase QA (`qa_phase.md`).

**Wait for each Oraca before proceeding.**

### Triangulated Context for Workers

```yaml
triangulated_context:
  goal: "The specific outcome from NS/Phase"
  bedrock:
    - "path/to/file1.md"  # Worker MUST read before executing
  instruction: "The specific action to take"
```

### Lookahead Loop (Dual-Track Execution)

After each ticket, run `validator_lookahead.md` (in think-tank/):

| Track A: Reality | Track B: Horizon |
|------------------|------------------|
| WR builds code | VA checks NS alignment |
| QA tests output | VA checks future blocking |

**PASS** → proceed | **WARN** → document, proceed | **FAIL** → pause, escalate

---

## Phase 3: QA Synthesis

Spawn Pro agent with `synthesizer_qa.md`. Analyzes all phase QA reports, identifies patterns.

---

## Phase 4: Sweep

Spawn Pro agent with `sweeper.md`. If GAPS_FOUND → create fix tasks → Oraca[FIX] → re-sweep.

---

## Phase 5: Validation & Report

1. Run automated checks (tests, linting)
2. Generate COMPLETION_REPORT.md
3. Log: `[DONE] Status: [STATUS]`
4. Report to HC

---

## Phase 6: ROADMAP SYNC

**On Success:**
1. Read ROADMAP.yaml from `.claude/PM/SSoT/ROADMAP.yaml`
2. Find phase by matching `plan_path`
3. Update `phase.status` → `'complete'`
4. Unlock phases where all deps are complete
5. Log: `[ROADMAP] Phase PHASE-XXX marked complete. N phases unlocked.`

**On Failure:**
1. Do NOT update ROADMAP.yaml status
2. Present COMPLETION_REPORT.md with failures
3. Offer recovery options: `RETRY_FAILED` | `ROLLBACK` | `MANUAL`

**ROLLBACK:** Spawn git-engineer with `OPERATION: rollback, ROLLBACK_HASH: ${ROLLBACK_HASH}`

---

## Edge Cases

### Parallel Phase Execution
Execute sequentially by default (safer). Future: `--parallel` flag.

### Execution Failure Recovery
1. COMPLETION_REPORT shows partial status
2. `RETRY_FAILED`: Re-spawns failed tasks only, re-runs SWEEP
3. `ROLLBACK`: Restores to checkpoint via git-engineer
4. `MANUAL`: Preserves state, user fixes, re-run continues

### Session Crash Recovery
1. EXECUTION_STATE.md shows last known state
2. Resume: `/hc-execute --resume ${SESSION_SLUG}`
3. Already-completed tasks are skipped

### Hotfix During Execution
1. Complete current task (don't interrupt)
2. Create hotfix commit outside flow
3. Resume - hotfix won't be rolled back

---

## RETRY_FAILED Test Procedure (ADR-004)

### Test Steps
1. Create synthetic failure (reference non-existent file)
2. Verify failure capture in EXECUTION_STATE.md, ORACA_LOG.md, PHASE_REPORT.md
3. Run RETRY_FAILED - verify ONLY failed task re-spawns
4. Verify SWEEP re-runs after

### Success Criteria
- [ ] Failed task identified correctly
- [ ] Only failed task re-runs
- [ ] SWEEP re-runs after retry
- [ ] State updates correctly

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

**V3.0.1** | Trimmed YAML bloat, consolidated from V3.0.0
