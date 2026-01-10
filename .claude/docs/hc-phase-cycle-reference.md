# hc-phase-cycle Reference

Reference material for `/hc-phase-cycle`. See main command for operational instructions.

---

## Why Proxy Agents + STATE

**Problem:** Running all steps directly in HC consumes context. After 2-3 phases, you lose early context.

**Solution:** Delegate to proxy agents. They work in their own context. HC stays light and strategic.

**Bridge:** STATE records what happened. Agents execute → STATE records → HC reads STATE to continue.

```text
HC (preserved context)
 │
 ├──► PRE-CHECKPOINT: STATE=in_progress, git commit
 ├──► Spawn Agent (via proxy) ──► Agent executes
 ├──► POST-CHECKPOINT: STATE=result, git commit
 └──► Next step (HC still has full context)
```

---

## Session Artifacts

```text
.claude/PM/phase-cycles/cycle_${YYYYMMDD}_${HHmm}/
├── CYCLE_STATE.yaml           # Progress tracking
├── ORCHESTRATOR_LOG.md        # Flight recorder
├── CHECKPOINT.md              # Git checkpoint info
├── phase_1/
│   ├── STEP_1_EXECUTE/
│   ├── STEP_2_AUDIT/
│   ├── STEP_3_FIXES/
│   ├── STEP_4_VALIDATION/
│   └── STEP_5_PLANNING/
├── phase_2/
│   └── ...
└── CYCLE_REPORT.md            # Final summary
```

---

## CYCLE_STATE.yaml Schema

```yaml
meta:
  created: '2026-01-09T10:00:00Z'
  total_phases: 3
  current_phase: 1
  checkpoint_hash: abc123

phases:
  - id: PHASE-001
    title: "Foundation"
    status: in_progress    # pending | in_progress | complete | failed
    started_at: '2026-01-09T10:00:00Z'
    steps:
      execute:
        status: complete
        completed_at: '2026-01-09T10:15:00Z'
        session_path: .claude/PM/hc-execute/...
      audit:
        status: in_progress
        started_at: '2026-01-09T10:16:00Z'
      fixes: { status: pending }
      validation: { status: pending }
      planning: { status: pending }

  - id: PHASE-002
    status: pending
    steps:
      execute: { status: pending }
      audit: { status: pending }
      fixes: { status: pending }
      validation: { status: pending }
      planning: { status: pending }

current_step:
  phase: 1
  step: audit
  started_at: '2026-01-09T10:16:00Z'

outcome:
  status: in_progress    # in_progress | complete | failed | paused
  phases_completed: 0
  phases_failed: 0
```

---

## Decision Points

### After Audit (Step 2)

If critical issues found:
- **PROCEED** - Continue with fixes (default)
- **ROLLBACK** - Revert and re-plan
- **SKIP_FIXES** - Accept tech debt

### After Validation (Step 4)

If validation fails:
- **RETRY** - Re-run failed tests
- **FIX** - Create fix tasks, run Step 3 again
- **ACCEPT** - Document known issues, proceed

### Between Phases

- **CONTINUE** - Proceed to next phase
- **PAUSE** - Save state, resume later
- **ABORT** - Stop, keep completed work

### If No Next Phase

- **COMPLETE** - Roadmap finished
- **ADD_PHASE** - Run `/think-tank --add-phase`

---

## Full Command Templates

### Execute Phase

```bash
spawn_agent_resilient "phase_executor" "
You are running /hc-execute.
Read: .claude/commands/hc-execute.md for your protocol.
PLAN_PATH: ${PLAN_PATH}
MODE: standard
WORKSPACE: $(pwd)
" "http://localhost:2414" "PHASE-XXX" "execute" 960
```

### Red-Team Audit

```bash
spawn_agent_resilient "red_team_audit" "
You are running /red-team.
Read: .claude/commands/red-team.md for your protocol.
AUDIT_SCOPE: core
WORKSPACE: $(pwd)
" "http://localhost:2414" "PHASE-XXX" "audit" 960
```

### Apply Fixes

```bash
spawn_agent_resilient "fix_executor" "
Read audit report: ${AUDIT_REPORT_PATH}
Create execution plan from Kill List and Fix List items.
Execute fixes using TDD: test first, then implement.
WORKSPACE: $(pwd)
" "http://localhost:2412" "PHASE-XXX" "fixes" 480
```

### E2E Validation

```bash
# Run tests first (direct)
python -m pytest tests/ -v --tb=short

# Then quick glass audit
spawn_agent_resilient "validation_glass" "
You are running /hc-glass.
Read: .claude/commands/hc-glass.md for your protocol.
DEPTH: quick
FOCUS: all
WORKSPACE: $(pwd)
" "http://localhost:2414" "PHASE-XXX" "validation" 960
```

### Plan Next Phase

```bash
spawn_agent_resilient "phase_planner" "
You are running /think-tank.
Read: .claude/commands/think-tank.md for your protocol.
Read: .claude/PM/SSoT/ROADMAP.yaml to find next unplanned phase.
Execute --phase=PHASE-XXX for the next phase.
WORKSPACE: $(pwd)
" "http://localhost:2415" "PHASE-XXX" "planning" 960
```

---

## Recovery

If crash occurs mid-cycle:

```bash
source .claude/lib/agent-spawn.sh
recover_cycle   # Detects interrupted cycles
sync_gate       # Verify state consistency
cycle_status    # Show current status
```

Manual state update (if needed):

```bash
update_cycle_state "PHASE-002" "execute" "complete" "success"
git_checkpoint "[PHASE-002] Manual state update"
```
