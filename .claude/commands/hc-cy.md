---
version: V1.0.0
alias: hc-phase-cycle-yaml
description: Phase cycle orchestrator (YAML-first variant)

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

defaults:
  N: 1
  phase: next
  skip_audit: false

steps_per_phase:
  - execute
  - audit
  - fixes
  - validation
  - planning

between_phases: "[GATE] sync_gate"
final: "[DONE] Cycle complete"

# ═══════════════════════════════════════════════════════════════════
# PROXY PORTS
# ═══════════════════════════════════════════════════════════════════

proxies:
  execute:    { port: 2414, timeout: 960, name: HC-Orca }
  audit:      { port: 2414, timeout: 960, name: HC-Orca }
  fixes:      { port: 2412, timeout: 480, name: HC-Work }
  validation: { port: 2414, timeout: 960, name: HC-Orca }
  planning:   { port: 2415, timeout: 960, name: HC-Orca-R }

# ═══════════════════════════════════════════════════════════════════
# TODO RULES
# ═══════════════════════════════════════════════════════════════════

todo_rules:
  strategy: full_upfront          # Generate ALL at init
  active_limit: 1                 # One in_progress at a time
  completion: immediate           # Mark done right after finishing
  prefix_format: "[X/N] PHASE-XXX: Step"
  gate_format: "[GATE] sync_gate before PHASE-XXX"
  done_format: "[DONE] Cycle complete"

# ═══════════════════════════════════════════════════════════════════
# TODO PATTERNS
# ═══════════════════════════════════════════════════════════════════

patterns:
  N1: |
    [1/1] PHASE-001: Execute     | Executing PHASE-001
    [1/1] PHASE-001: Audit       | Auditing PHASE-001
    [1/1] PHASE-001: Fixes       | Fixing PHASE-001
    [1/1] PHASE-001: Validate    | Validating PHASE-001
    [1/1] PHASE-001: Plan next   | Planning next phase
    [DONE] Cycle complete        | Completing cycle

  N2: |
    [1/2] PHASE-001: Execute     | Executing PHASE-001 (1/2)
    [1/2] PHASE-001: Audit       | Auditing PHASE-001
    [1/2] PHASE-001: Fixes       | Fixing PHASE-001
    [1/2] PHASE-001: Validate    | Validating PHASE-001
    [1/2] PHASE-001: Plan P-002  | Planning PHASE-002
    [GATE] sync_gate → P-002     | Sync gate 1→2
    [2/2] PHASE-002: Execute     | Executing PHASE-002 (2/2)
    [2/2] PHASE-002: Audit       | Auditing PHASE-002
    [2/2] PHASE-002: Fixes       | Fixing PHASE-002
    [2/2] PHASE-002: Validate    | Validating PHASE-002
    [2/2] PHASE-002: Plan next   | Planning next phase
    [DONE] Cycle complete        | Final sync gate

  N3: |
    [1/3] PHASE-001: Execute     | Executing PHASE-001 (1/3)
    [1/3] PHASE-001: Audit       | Auditing PHASE-001
    [1/3] PHASE-001: Fixes       | Fixing PHASE-001
    [1/3] PHASE-001: Validate    | Validating PHASE-001
    [1/3] PHASE-001: Plan P-002  | Planning PHASE-002
    [GATE] sync_gate → P-002     | Sync gate 1→2
    [2/3] PHASE-002: Execute     | Executing PHASE-002 (2/3)
    [2/3] PHASE-002: Audit       | Auditing PHASE-002
    [2/3] PHASE-002: Fixes       | Fixing PHASE-002
    [2/3] PHASE-002: Validate    | Validating PHASE-002
    [2/3] PHASE-002: Plan P-003  | Planning PHASE-003
    [GATE] sync_gate → P-003     | Sync gate 2→3
    [3/3] PHASE-003: Execute     | Executing PHASE-003 (3/3)
    [3/3] PHASE-003: Audit       | Auditing PHASE-003
    [3/3] PHASE-003: Fixes       | Fixing PHASE-003
    [3/3] PHASE-003: Validate    | Validating PHASE-003
    [3/3] PHASE-003: Plan next   | Planning next phase
    [DONE] Cycle complete        | Final sync gate

# ═══════════════════════════════════════════════════════════════════
# SPAWN TEMPLATES
# ═══════════════════════════════════════════════════════════════════

spawn:
  execute: |
    spawn_agent_resilient "executor" "
    Run /hc-execute. Read: .claude/commands/hc-execute.md
    PLAN_PATH: $PLAN_PATH | MODE: standard | WORKSPACE: $(pwd)
    " "http://localhost:2414" "$PHASE" "execute" 960

  audit: |
    spawn_agent_resilient "auditor" "
    Run /red-team. Read: .claude/commands/red-team.md
    AUDIT_SCOPE: core | WORKSPACE: $(pwd)
    " "http://localhost:2414" "$PHASE" "audit" 960

  fixes: |
    spawn_agent_resilient "fixer" "
    Read: $AUDIT_REPORT | Apply Kill/Fix items with TDD
    WORKSPACE: $(pwd)
    " "http://localhost:2412" "$PHASE" "fixes" 480

  validation: |
    spawn_agent_resilient "validator" "
    Run /hc-glass. Read: .claude/commands/hc-glass.md
    DEPTH: quick | FOCUS: all | WORKSPACE: $(pwd)
    " "http://localhost:2414" "$PHASE" "validation" 960

  planning: |
    spawn_agent_resilient "planner" "
    Run /think-tank. Read: .claude/commands/think-tank.md
    Read ROADMAP.yaml, plan next phase | WORKSPACE: $(pwd)
    " "http://localhost:2415" "$PHASE" "planning" 960

# ═══════════════════════════════════════════════════════════════════
# GATE ACTIONS
# ═══════════════════════════════════════════════════════════════════

gate:
  commands:
    - sync_gate
    - cycle_status
  options:
    CONTINUE: Proceed to next phase
    PAUSE: Save state, exit (recover_cycle to resume)
    ABORT: Stop, keep completed work
---

# /hc-cy - Phase Cycle (YAML-First)

## Usage

```
/hc-cy [N]        # N = number of phases (default: 1)
```

## Protocol

### 1. Initialize

```bash
source .claude/lib/agent-spawn.sh
recover_cycle
init_cycle_session "cycle_$(date +%Y%m%d_%H%M)" "PHASE-001" "PHASE-002"
sync_gate
```

### 2. Generate Todos

Use pattern from `patterns.N{1,2,3}` above. Format: `content | activeForm`

**Convert to TodoWrite:**
```yaml
- content: "[1/2] PHASE-001: Execute"
  status: in_progress
  activeForm: "Executing PHASE-001 (1/2)"
```

### 3. Execute Loop

```
For each todo:
  1. Mark in_progress
  2. Run spawn template from spawn.{step}
  3. Mark completed
  4. Next
```

### 4. At [GATE]

Run `gate.commands`, ask user `gate.options`.

## Mantra

```
Full upfront. One active. Immediate complete.
[GATE] = user confirms. spawn_agent_resilient() handles state.
```

---

Reference: `.claude/docs/hc-phase-cycle-reference.md`
