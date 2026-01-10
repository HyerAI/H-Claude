---
version: V1.4.0
status: current
timestamp: 2026-01-10
tags: [command, orchestration, phase-cycle, automation, todo-driven, multi-phase]
description: "Full phase cycle orchestrator - Execute, Audit, Fix, Validate, Plan Next via Todo-driven agent delegation with multi-phase support"
---

# /hc-phase-cycle - Phase Cycle Orchestrator

**Philosophy:** Context is precious. Delegate to agents, track via todo. Update STATE after EVERY step.

**Purpose:** Execute complete phase development cycles, delegating each stage to specialized agents while preserving HC context through todo-driven orchestration.

---

## Why Proxy Agents + STATE

**The Problem:** Running all steps directly in HC consumes your context window. After 2-3 phases, you lose early context and make mistakes.

**The Solution:** Delegate to proxy agents. They do the heavy lifting in their own context. HC stays light and strategic.

**The Bridge:** STATE is how HC knows what happened. Agents execute, STATE records, HC reads STATE to continue.

```text
HC (preserved context)
 │
 ├──► Spawn Agent (via proxy) ──► Agent executes in own context
 │                                      │
 │◄── Read STATE ◄──────────────────────┘
 │         ↑
 │    Agent writes results to STATE before exit
 │
 └──► Next step (HC still has full context)
```

**CRITICAL:** Always use proxy agents for execution. Always update STATE after each step. This is how multi-phase runs work without losing context.

---

## Quick Start

```bash
/hc-phase-cycle [N]

# Examples:
/hc-phase-cycle           # Run 1 phase cycle (default)
/hc-phase-cycle 3         # Run 3 phase cycles in sequence
/hc-phase-cycle 5         # Run 5 phase cycles
```

### Parameters

| Parameter | Default | Description |
| --------- | ------- | ----------- |
| `N` | 1 | Number of phases to complete in sequence |
| `PHASE` | next | Starting phase (or 'next' for auto-detect) |
| `MODE` | standard | Execution mode: standard or careful |
| `SKIP_AUDIT` | false | Skip red-team audit (NOT recommended) |

**Red-team audit runs by default.** User must explicitly set `SKIP_AUDIT: true` to skip.

---

## The Cycle (Per Phase)

```text
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: EXECUTE PHASE                                          │
│  Agent: /hc-execute --phase=PHASE-XXX                           │
│  Outcome: Phase code implemented                                │
│  >>> UPDATE STATE <<<                                           │
├─────────────────────────────────────────────────────────────────┤
│  STEP 2: RED-TEAM AUDIT (default: ON)                           │
│  Agent: /red-team AUDIT_SCOPE: core                             │
│  Outcome: AUDIT_REPORT.md with Kill/Fix/Gap lists               │
│  >>> UPDATE STATE <<<                                           │
├─────────────────────────────────────────────────────────────────┤
│  STEP 3: APPLY FIXES                                            │
│  Agent: /hc-execute --fixes (from audit findings)               │
│  Outcome: Issues resolved, code improved                        │
│  >>> UPDATE STATE <<<                                           │
├─────────────────────────────────────────────────────────────────┤
│  STEP 4: E2E VALIDATION                                         │
│  Agent: Run project tests + /hc-glass DEPTH: quick              │
│  Outcome: Validation report, confidence score                   │
│  >>> UPDATE STATE <<<                                           │
├─────────────────────────────────────────────────────────────────┤
│  STEP 5: PLAN NEXT PHASE                                        │
│  Agent: /think-tank --phase=PHASE-NEXT                          │
│  Outcome: execution-plan.yaml for next phase                    │
│  >>> UPDATE STATE <<<                                           │
└─────────────────────────────────────────────────────────────────┘
         ↓
    If N > 1: Loop to STEP 1 with next phase
```

---

## CRITICAL: STATE Updates

**UPDATE STATE AFTER EVERY STEP.** This is non-negotiable.

After each step completes:

1. Update `CYCLE_STATE.yaml` with step status
2. Update todo list (mark complete, set next in_progress)
3. Log outcome to `ORCHESTRATOR_LOG.md`

**Why this matters:**

- Enables recovery if session crashes
- Tracks progress across multi-phase runs
- Provides audit trail for what happened
- Allows pause/resume at any point

### State Update Protocol

```yaml
# After each step, update CYCLE_STATE.yaml:
steps:
  execute:
    status: complete          # Was: in_progress
    completed_at: '2026-01-09T10:15:00Z'
    session_path: .claude/PM/hc-execute/phase001_20260109/
    outcome: success          # success | partial | failed

# And update current_step:
current_step: 2               # Now on audit step
```

```bash
# Then commit state to git (checkpoint for recovery):
git add .claude/PM/phase-cycles/ .claude/PM/SSoT/
git commit -m "[PHASE-XXX] Step N complete: step_name"
```

---

## How It Works

This command does NOT spawn agents directly. Instead, it:

1. **Reads** ROADMAP.yaml to identify target phase(s)
2. **Generates** a structured todo list with exact agent commands
3. **Updates STATE** after each step (MANDATORY)
4. **Loops** for multi-phase runs (N > 1)

**Why todo-driven?**

- Preserves HC context (agents run in separate sessions)
- Full visibility into progress
- Can pause/resume between steps
- Each step can be adjusted based on previous outcomes
- STATE tracking enables crash recovery

---

## Protocol

### STEP 0: INITIALIZATION

1. Read `.claude/PM/SSoT/ROADMAP.yaml`
2. Parse N (number of phases, default 1)
3. Identify starting phase:
   - If `PHASE: next` -> find first phase with status `planned` and all dependencies `complete`
   - If `PHASE: PHASE-XXX` -> validate phase exists
4. Validate N phases are available (warn if fewer exist)
5. Create session: `.claude/PM/phase-cycles/cycle_${YYYYMMDD}_${HHmm}/`
6. Initialize `CYCLE_STATE.yaml`
7. Create git checkpoint

### STEP 1: GENERATE TODO LIST FOR CURRENT PHASE

For phase X of N, generate todos:

```yaml
todos:
  - content: "[Phase X/N] Execute PHASE-XXX with /hc-execute"
    status: in_progress
    activeForm: "Executing phase PHASE-XXX (X of N)"

  - content: "[Phase X/N] Update STATE after execute"
    status: pending
    activeForm: "Updating STATE after execute"

  - content: "[Phase X/N] Run red-team audit"
    status: pending
    activeForm: "Running red-team audit"

  - content: "[Phase X/N] Update STATE after audit"
    status: pending
    activeForm: "Updating STATE after audit"

  - content: "[Phase X/N] Apply fixes from audit"
    status: pending
    activeForm: "Applying audit fixes"

  - content: "[Phase X/N] Update STATE after fixes"
    status: pending
    activeForm: "Updating STATE after fixes"

  - content: "[Phase X/N] Run E2E validation"
    status: pending
    activeForm: "Running E2E validation"

  - content: "[Phase X/N] Update STATE after validation"
    status: pending
    activeForm: "Updating STATE after validation"

  - content: "[Phase X/N] Plan next phase"
    status: pending
    activeForm: "Planning next phase"

  - content: "[Phase X/N] Update STATE after planning"
    status: pending
    activeForm: "Updating STATE after planning"

  # If X < N, add:
  - content: "[Phase X/N] CHECKPOINT: Proceed to phase X+1?"
    status: pending
    activeForm: "Checkpoint before next phase"
```

### STEP 2: EXECUTE WITH STATE TRACKING

For each action step, the pattern is:

```text
1. Run agent command
2. Review output
3. UPDATE STATE (write to CYCLE_STATE.yaml)
4. Mark todo complete
5. Proceed to next
```

**STATE update is between action and completion.** Never skip it.

---

## Multi-Phase Execution

When `N > 1`, the cycle repeats:

```text
Phase 1: Execute -> Audit -> Fix -> Validate -> Plan Phase 2
         >>> CHECKPOINT: Continue? <<<
Phase 2: Execute -> Audit -> Fix -> Validate -> Plan Phase 3
         >>> CHECKPOINT: Continue? <<<
Phase 3: Execute -> Audit -> Fix -> Validate -> Plan Phase 4
         ...
Phase N: Execute -> Audit -> Fix -> Validate -> COMPLETE
```

### Checkpoint Protocol

Between phases, pause and ask:

- Phase X completed successfully?
- Any blockers for Phase X+1?
- Continue, Pause, or Abort?

**Options:**

- `CONTINUE` -> Proceed to next phase
- `PAUSE` -> Save state, exit (resume later)
- `ABORT` -> Stop cycle, keep completed work

---

## Agent Commands Reference

### Required: Agent Spawn Library

All agent spawns use `spawn_agent()` from ADR-001. Source it at the start of each step:

```bash
source .claude/lib/agent-spawn.sh
SESSION_PATH=".claude/PM/phase-cycles/cycle_${YYYYMMDD}_${HHmm}/phase_${X}"
```

This enables stall-based timeouts (kill agents that stop logging, not just slow ones).

### Proxy Ports

| Port | Proxy     | Use Case                   |
| ---- | --------- | -------------------------- |
| 2410 | HC-Reas-A | Domain reasoning           |
| 2411 | HC-Reas-B | Challenger reasoning       |
| 2412 | HC-Work   | Workers, execution         |
| 2413 | HC-Work-R | Workers with reasoning     |
| 2414 | HC-Orca   | Light orchestration        |
| 2415 | HC-Orca-R | Orchestration with reasoning |

### Command Templates

**Execute Phase:**

```bash
source .claude/lib/agent-spawn.sh
SESSION_PATH=".claude/PM/phase-cycles/cycle_${YYYYMMDD}_${HHmm}/phase_${X}"

spawn_agent "phase_executor" "
You are running /hc-execute.
Read: .claude/commands/hc-execute.md for your protocol.
PLAN_PATH: ${PLAN_PATH}
MODE: standard
WORKSPACE: $(pwd)
" "http://localhost:2414" 960
```

**Red-Team Audit:**

```bash
spawn_agent "red_team_audit" "
You are running /red-team.
Read: .claude/commands/red-team.md for your protocol.
AUDIT_SCOPE: core
WORKSPACE: $(pwd)
" "http://localhost:2414" 960
```

**Apply Fixes (Flash Worker - preserves HC context):**

```bash
# Source agent spawn library (ADR-001)
source .claude/lib/agent-spawn.sh

# Set session path for logging
SESSION_PATH=".claude/PM/phase-cycles/cycle_${YYYYMMDD}_${HHmm}/phase_${X}"

# Spawn Flash worker to execute fixes (HC stays light, Flash does heavy lifting)
spawn_agent "fix_executor" "
Read audit report: ${AUDIT_REPORT_PATH}
Create execution plan from Kill List and Fix List items.
Execute fixes using TDD: test first, then implement.
Log every fix applied to your agent log.
WORKSPACE: $(pwd)
" "http://localhost:2412" 480
```

**Why Flash for fixes?** HC orchestrates the cycle, Flash executes. This preserves HC's context for multi-phase runs. Flash workers are disposable; HC context is precious.

**E2E Validation:**

```bash
# Run tests first (direct, not agent)
python -m pytest tests/ -v --tb=short

# Then quick glass audit via agent
spawn_agent "validation_glass" "
You are running /hc-glass.
Read: .claude/commands/hc-glass.md for your protocol.
DEPTH: quick
FOCUS: all
WORKSPACE: $(pwd)
" "http://localhost:2414" 960
```

**Plan Next Phase:**

```bash
spawn_agent "phase_planner" "
You are running /think-tank.
Read: .claude/commands/think-tank.md for your protocol.
Read: .claude/PM/SSoT/ROADMAP.yaml to find next unplanned phase.
Execute --phase=PHASE-XXX for the next phase.
WORKSPACE: $(pwd)
" "http://localhost:2415" 960
```

**Update STATE (after each step):**

```bash
# This is done by HC directly, not an agent
# 1. Update CYCLE_STATE.yaml with step outcome
# 2. Update todo list (mark complete, set next in_progress)
# 3. Log to ORCHESTRATOR_LOG.md
# 4. Git commit the state change

# Example state commit:
git add .claude/PM/phase-cycles/ .claude/PM/SSoT/ROADMAP.yaml
git commit -m "$(cat <<'EOF'
[PHASE-XXX] Step Y complete: STEP_NAME

- Status: success|partial|failed
- Session: .claude/PM/phase-cycles/cycle_YYYYMMDD_HHmm/

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

**Why commit state?** Enables recovery if session crashes. Each step is a checkpoint we can rollback to.

---

## Session Artifacts

```text
.claude/PM/phase-cycles/cycle_${YYYYMMDD}_${HHmm}/
├── CYCLE_STATE.yaml           # Progress tracking (update after EVERY step)
├── ORCHESTRATOR_LOG.md        # Flight recorder
├── CHECKPOINT.md              # Git checkpoint info
├── phase_1/
│   ├── STEP_1_EXECUTE/        # hc-execute session link
│   ├── STEP_2_AUDIT/          # red-team session link
│   ├── STEP_3_FIXES/          # Fix execution log
│   ├── STEP_4_VALIDATION/     # E2E results
│   └── STEP_5_PLANNING/       # think-tank session link
├── phase_2/
│   └── ...
├── phase_N/
│   └── ...
└── CYCLE_REPORT.md            # Final summary
```

### CYCLE_STATE.yaml Schema

```yaml
meta:
  created: '2026-01-09T10:00:00Z'
  total_phases: 3              # N from command
  current_phase: 1             # Which phase we're on
  checkpoint_hash: abc123

phases:
  - id: PHASE-001
    title: "Foundation"
    status: in_progress        # pending | in_progress | complete | failed
    started_at: '2026-01-09T10:00:00Z'
    steps:
      execute:
        status: complete
        completed_at: '2026-01-09T10:15:00Z'
        session_path: .claude/PM/hc-execute/...
      audit:
        status: in_progress
        started_at: '2026-01-09T10:16:00Z'
        findings_count: null
      fixes:
        status: pending
      validation:
        status: pending
      planning:
        status: pending

  - id: PHASE-002
    title: "Git Worktree"
    status: pending
    steps:
      execute: { status: pending }
      audit: { status: pending }
      fixes: { status: pending }
      validation: { status: pending }
      planning: { status: pending }

current_step:
  phase: 1
  step: audit                  # execute | audit | fixes | validation | planning
  started_at: '2026-01-09T10:16:00Z'

outcome:
  status: in_progress          # in_progress | complete | failed | paused
  phases_completed: 0
  phases_failed: 0
```

---

## Decision Points

### After Step 2 (Audit)

If audit finds critical issues:

- **PROCEED**: Continue with fixes (default)
- **ROLLBACK**: Revert and re-plan
- **SKIP_FIXES**: Accept tech debt, continue

### After Step 4 (Validation)

If validation fails:

- **RETRY**: Re-run failed tests
- **FIX**: Create fix tasks, run Step 3 again
- **ACCEPT**: Document known issues, proceed

### After Step 5 (Planning) / Between Phases

For multi-phase runs:

- **CONTINUE**: Proceed to next phase
- **PAUSE**: Save state, resume later
- **ABORT**: Stop, keep completed work

### If No Next Phase Exists

- **COMPLETE**: Cycle done, roadmap finished
- **ADD_PHASE**: Run `/think-tank --add-phase` to extend

---

## Integration with Existing Commands

| Command        | Role in Cycle              |
| -------------- | -------------------------- |
| `/hc-execute`  | Step 1: Execute phase plan |
| `/red-team`    | Step 2: Audit implementation (default ON) |
| `/hc-glass`    | Step 4: Quick validation   |
| `/think-tank`  | Step 5: Plan next phase    |

---

## The Cycle Mantra

```text
I preserve context by delegating to agents.
I UPDATE STATE after EVERY step.
I track progress through the todo list.
I execute in sequence: build, audit, fix, validate, plan.
I checkpoint before I execute.
I never skip the audit (unless explicitly told).
Each phase ends with the next phase planned.
For multi-phase: I pause between phases to confirm.
```

---

## Related

| Command              | When to Use Instead                 |
| -------------------- | ----------------------------------- |
| `/hc-execute`        | Execute single phase without cycle  |
| `/think-tank --phase`| Plan phase without executing        |
| `/red-team`          | Audit without full cycle            |

---

**Version:** V1.4.0 | Added git commits on state updates for crash recovery; spawn_agent() (ADR-001) across all steps
