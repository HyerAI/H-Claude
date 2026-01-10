---
version: V2.1.0
status: current
timestamp: 2026-01-10
description: "Phase cycle orchestrator with resilient spawns (ADR-007)"
---

# /hc-phase-cycle - Phase Cycle Orchestrator

Delegate to agents, track via todo, checkpoint automatically.

---

## Quick Start

```bash
/hc-phase-cycle [N]

/hc-phase-cycle           # 1 phase (default)
/hc-phase-cycle 2         # 2 phases
/hc-phase-cycle 3         # 3 phases
```

| Param | Default | Description |
|-------|---------|-------------|
| N | 1 | Number of phases to run |
| PHASE | next | Starting phase (or specific PHASE-XXX) |
| SKIP_AUDIT | false | Skip red-team (not recommended) |

---

## The Cycle (Per Phase)

```text
┌────────────────────────────────────────────────────┐
│  1. EXECUTE    /hc-execute --phase=PHASE-XXX       │
│  2. AUDIT      /red-team AUDIT_SCOPE: core         │
│  3. FIXES      Apply Kill/Fix list items           │
│  4. VALIDATE   Tests + /hc-glass DEPTH: quick      │
│  5. PLAN       /think-tank --phase=PHASE-NEXT      │
├────────────────────────────────────────────────────┤
│  [GATE] sync_gate() before next phase              │
└────────────────────────────────────────────────────┘
         ↓
    If N > 1: Loop with next phase
```

---

## Protocol

### STEP 0: Initialize

```bash
source .claude/lib/agent-spawn.sh

# Check for interrupted cycles
recover_cycle

# Init session (exports CYCLE_SESSION_PATH)
init_cycle_session "cycle_$(date +%Y%m%d_%H%M)" "PHASE-001" "PHASE-002"

# Verify clean state
sync_gate
```

### STEP 1: Generate ALL Todos Upfront

**CRITICAL:** Generate todos for ALL phases at init, not incrementally.

---

#### Pattern: N=1 (Single Phase)

```yaml
todos:
  - content: "[1/1] PHASE-001: Execute"
    status: in_progress
    activeForm: "Executing PHASE-001"
  - content: "[1/1] PHASE-001: Audit"
    status: pending
    activeForm: "Auditing PHASE-001"
  - content: "[1/1] PHASE-001: Fixes"
    status: pending
    activeForm: "Fixing PHASE-001"
  - content: "[1/1] PHASE-001: Validate"
    status: pending
    activeForm: "Validating PHASE-001"
  - content: "[1/1] PHASE-001: Plan next"
    status: pending
    activeForm: "Planning next phase"
  - content: "[DONE] Cycle complete"
    status: pending
    activeForm: "Completing cycle"
```

---

#### Pattern: N=2 (Two Phases)

```yaml
todos:
  # ═══ PHASE 1 of 2 ═══
  - content: "[1/2] PHASE-001: Execute"
    status: in_progress
    activeForm: "Executing PHASE-001 (1/2)"
  - content: "[1/2] PHASE-001: Audit"
    status: pending
    activeForm: "Auditing PHASE-001"
  - content: "[1/2] PHASE-001: Fixes"
    status: pending
    activeForm: "Fixing PHASE-001"
  - content: "[1/2] PHASE-001: Validate"
    status: pending
    activeForm: "Validating PHASE-001"
  - content: "[1/2] PHASE-001: Plan PHASE-002"
    status: pending
    activeForm: "Planning PHASE-002"
  - content: "[GATE] sync_gate before PHASE-002"
    status: pending
    activeForm: "Sync gate 1→2"

  # ═══ PHASE 2 of 2 ═══
  - content: "[2/2] PHASE-002: Execute"
    status: pending
    activeForm: "Executing PHASE-002 (2/2)"
  - content: "[2/2] PHASE-002: Audit"
    status: pending
    activeForm: "Auditing PHASE-002"
  - content: "[2/2] PHASE-002: Fixes"
    status: pending
    activeForm: "Fixing PHASE-002"
  - content: "[2/2] PHASE-002: Validate"
    status: pending
    activeForm: "Validating PHASE-002"
  - content: "[2/2] PHASE-002: Plan next"
    status: pending
    activeForm: "Planning next phase"
  - content: "[DONE] Cycle complete"
    status: pending
    activeForm: "Final sync gate"
```

---

#### Pattern: N=3 (Three Phases)

```yaml
todos:
  # ═══ PHASE 1 of 3 ═══
  - content: "[1/3] PHASE-001: Execute"
    status: in_progress
    activeForm: "Executing PHASE-001 (1/3)"
  - content: "[1/3] PHASE-001: Audit"
    status: pending
    activeForm: "Auditing PHASE-001"
  - content: "[1/3] PHASE-001: Fixes"
    status: pending
    activeForm: "Fixing PHASE-001"
  - content: "[1/3] PHASE-001: Validate"
    status: pending
    activeForm: "Validating PHASE-001"
  - content: "[1/3] PHASE-001: Plan PHASE-002"
    status: pending
    activeForm: "Planning PHASE-002"
  - content: "[GATE] sync_gate before PHASE-002"
    status: pending
    activeForm: "Sync gate 1→2"

  # ═══ PHASE 2 of 3 ═══
  - content: "[2/3] PHASE-002: Execute"
    status: pending
    activeForm: "Executing PHASE-002 (2/3)"
  - content: "[2/3] PHASE-002: Audit"
    status: pending
    activeForm: "Auditing PHASE-002"
  - content: "[2/3] PHASE-002: Fixes"
    status: pending
    activeForm: "Fixing PHASE-002"
  - content: "[2/3] PHASE-002: Validate"
    status: pending
    activeForm: "Validating PHASE-002"
  - content: "[2/3] PHASE-002: Plan PHASE-003"
    status: pending
    activeForm: "Planning PHASE-003"
  - content: "[GATE] sync_gate before PHASE-003"
    status: pending
    activeForm: "Sync gate 2→3"

  # ═══ PHASE 3 of 3 ═══
  - content: "[3/3] PHASE-003: Execute"
    status: pending
    activeForm: "Executing PHASE-003 (3/3)"
  - content: "[3/3] PHASE-003: Audit"
    status: pending
    activeForm: "Auditing PHASE-003"
  - content: "[3/3] PHASE-003: Fixes"
    status: pending
    activeForm: "Fixing PHASE-003"
  - content: "[3/3] PHASE-003: Validate"
    status: pending
    activeForm: "Validating PHASE-003"
  - content: "[3/3] PHASE-003: Plan next"
    status: pending
    activeForm: "Planning next phase"
  - content: "[DONE] Cycle complete"
    status: pending
    activeForm: "Final sync gate"
```

---

### Todo Rules

| Rule | Description |
|------|-------------|
| **Full upfront** | Generate ALL todos for ALL phases at init |
| **One active** | Exactly one todo `in_progress` at a time |
| **Immediate completion** | Mark done right after finishing, don't batch |
| **[X/N] prefix** | Shows phase progress (e.g., [2/3]) |
| **[GATE] checkpoint** | Run `sync_gate()`, user confirms before next phase |
| **[DONE] final** | Last todo marks cycle complete |

---

### STEP 2: Execute Each Todo

```text
For each todo:
1. Mark in_progress
2. spawn_agent_resilient() with PHASE and STEP
   └── AUTO: pre-checkpoint, run agent, post-checkpoint
3. Review output
4. Mark completed
5. Next todo
```

---

## Command Templates

| Step | Command | Proxy | Timeout |
|------|---------|-------|---------|
| Execute | `spawn_agent_resilient "executor" "Run /hc-execute..." 2414 PHASE execute 960` | HC-Orca | 16m |
| Audit | `spawn_agent_resilient "auditor" "Run /red-team..." 2414 PHASE audit 960` | HC-Orca | 16m |
| Fixes | `spawn_agent_resilient "fixer" "Apply fixes..." 2412 PHASE fixes 480` | HC-Work | 8m |
| Validate | `spawn_agent_resilient "validator" "Run /hc-glass..." 2414 PHASE validation 960` | HC-Orca | 16m |
| Plan | `spawn_agent_resilient "planner" "Run /think-tank..." 2415 PHASE planning 960` | HC-Orca-R | 16m |

Full templates: `.claude/docs/hc-phase-cycle-reference.md`

---

## [GATE] Protocol

At each `[GATE]` todo:

```bash
sync_gate        # Verify state committed
cycle_status     # Show progress
```

Ask user: **CONTINUE | PAUSE | ABORT**

- CONTINUE → Proceed to next phase
- PAUSE → Save state, exit (resume later with `recover_cycle`)
- ABORT → Stop, keep completed work

---

## Integration

| Command | Role |
|---------|------|
| `/hc-execute` | Step 1: Execute phase |
| `/red-team` | Step 2: Audit |
| `/hc-glass` | Step 4: Validation |
| `/think-tank` | Step 5: Plan next |

---

## Mantra

```
Generate ALL todos upfront.
One in_progress at a time.
Mark complete immediately.
[GATE] = user confirms.
spawn_agent_resilient() handles state.
```

---

## Related

| Instead | When |
|---------|------|
| `/hc-execute` | Single phase, no cycle |
| `/think-tank --phase` | Plan only, no execute |
| `/red-team` | Audit only |

Reference: `.claude/docs/hc-phase-cycle-reference.md`

---

**V2.1.0** | Multi-phase todo fix, trimmed to ~250 lines
