---
version: V2.0.0
alias: hc-phase-cycle-yaml
description: "Phase cycle orchestrator (YAML config) - HC orchestrates, agents execute"

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

defaults:
  N: 1
  phase: next
  skip_audit: false

steps_per_phase:
  - execute
  - checkpoint_exec
  - audit
  - fixes
  - checkpoint_fixes
  - validate
  - plan
  - checkpoint_final

between_phases: "[GATE] User confirms"
final: "[DONE] complete_cycle()"

# ═══════════════════════════════════════════════════════════════════
# HC ROLE
# ═══════════════════════════════════════════════════════════════════

hc_role:
  does:
    - Spawn agents (background)
    - Review results
    - Update state ($CTX, commits)
    - Talk to user while agents work
  does_not:
    - Write code inline
    - Apply fixes directly
    - Block on long operations

# ═══════════════════════════════════════════════════════════════════
# PROXY PORTS
# ═══════════════════════════════════════════════════════════════════

proxies:
  execute:          { port: 2414, timeout: 960, name: HC-Orca, background: true }
  checkpoint_exec:  { port: null, timeout: 30,  name: HC-Direct }
  audit:            { port: 2414, timeout: 960, name: HC-Orca, background: true }
  fixes:            { port: 2412, timeout: 480, name: HC-Work, background: true }
  checkpoint_fixes: { port: null, timeout: 30,  name: HC-Direct }
  validate:         { port: 2414, timeout: 960, name: HC-Orca, background: true }
  plan:             { port: 2415, timeout: 960, name: HC-Orca-R, background: true }
  checkpoint_final: { port: null, timeout: 30,  name: HC-Direct }

# ═══════════════════════════════════════════════════════════════════
# TODO PATTERNS (JSON for TodoWrite)
# ═══════════════════════════════════════════════════════════════════

patterns:
  N1: |
    [
      {"content": "[1/8] Execute phase", "status": "in_progress", "activeForm": "Spawning /hc-execute"},
      {"content": "[2/8] Checkpoint: commit + state", "status": "pending", "activeForm": "Committing execution"},
      {"content": "[3/8] Audit phase", "status": "pending", "activeForm": "Spawning /red-team"},
      {"content": "[4/8] Fixes: spawn FLASH workers", "status": "pending", "activeForm": "Spawning fix workers"},
      {"content": "[5/8] Checkpoint: commit + state", "status": "pending", "activeForm": "Committing fixes"},
      {"content": "[6/8] Validate phase", "status": "pending", "activeForm": "Spawning /hc-glass"},
      {"content": "[7/8] Plan next phase", "status": "pending", "activeForm": "Spawning /think-tank"},
      {"content": "[8/8] Final checkpoint + complete", "status": "pending", "activeForm": "Final commit + complete_cycle"}
    ]

  N2: |
    [
      {"content": "[P1 1/8] Execute", "status": "in_progress", "activeForm": "Spawning /hc-execute (P1)"},
      {"content": "[P1 2/8] Checkpoint", "status": "pending", "activeForm": "Committing P1 execution"},
      {"content": "[P1 3/8] Audit", "status": "pending", "activeForm": "Spawning /red-team (P1)"},
      {"content": "[P1 4/8] Fixes", "status": "pending", "activeForm": "Spawning fix workers (P1)"},
      {"content": "[P1 5/8] Checkpoint", "status": "pending", "activeForm": "Committing P1 fixes"},
      {"content": "[P1 6/8] Validate", "status": "pending", "activeForm": "Spawning /hc-glass (P1)"},
      {"content": "[P1 7/8] Plan", "status": "pending", "activeForm": "Spawning /think-tank (P1)"},
      {"content": "[P1 8/8] Checkpoint", "status": "pending", "activeForm": "Committing P1 complete"},
      {"content": "[GATE] Confirm P2", "status": "pending", "activeForm": "User gate: continue?"},
      {"content": "[P2 1/8] Execute", "status": "pending", "activeForm": "Spawning /hc-execute (P2)"},
      {"content": "[P2 2/8] Checkpoint", "status": "pending", "activeForm": "Committing P2 execution"},
      {"content": "[P2 3/8] Audit", "status": "pending", "activeForm": "Spawning /red-team (P2)"},
      {"content": "[P2 4/8] Fixes", "status": "pending", "activeForm": "Spawning fix workers (P2)"},
      {"content": "[P2 5/8] Checkpoint", "status": "pending", "activeForm": "Committing P2 fixes"},
      {"content": "[P2 6/8] Validate", "status": "pending", "activeForm": "Spawning /hc-glass (P2)"},
      {"content": "[P2 7/8] Plan", "status": "pending", "activeForm": "Spawning /think-tank (P2)"},
      {"content": "[P2 8/8] Final checkpoint", "status": "pending", "activeForm": "Final commit + complete_cycle"}
    ]

# ═══════════════════════════════════════════════════════════════════
# SPAWN TEMPLATES
# ═══════════════════════════════════════════════════════════════════

spawn:
  execute: |
    ANTHROPIC_API_BASE_URL=http://localhost:2414 claude --dangerously-skip-permissions -p "
    Run /hc-execute. Read: .claude/commands/hc-execute.md
    PLAN_PATH: $PLAN_PATH | MODE: standard | WORKSPACE: $(pwd)
    " &

  audit: |
    ANTHROPIC_API_BASE_URL=http://localhost:2414 claude --dangerously-skip-permissions -p "
    Run /red-team. Read: .claude/commands/red-team.md
    AUDIT_SCOPE: core | WORKSPACE: $(pwd)
    " &

  fixes: |
    # CRITICAL: Spawn FLASH worker for EACH fix item
    # DO NOT apply fixes inline - protect HC context
    ANTHROPIC_API_BASE_URL=http://localhost:2412 claude --dangerously-skip-permissions -p "
    WORKSPACE: $(pwd)
    AUDIT_REPORT: $AUDIT_REPORT

    Read the audit report. For each Kill/Fix item:
    - Apply the fix
    - Use TDD if applicable
    - Commit each fix separately
    " &

  validate: |
    ANTHROPIC_API_BASE_URL=http://localhost:2414 claude --dangerously-skip-permissions -p "
    Run /hc-glass. Read: .claude/commands/hc-glass.md
    DEPTH: quick | FOCUS: all | WORKSPACE: $(pwd)
    " &

  plan: |
    ANTHROPIC_API_BASE_URL=http://localhost:2415 claude --dangerously-skip-permissions -p "
    Run /think-tank. Read: .claude/commands/think-tank.md
    Read ROADMAP.yaml, plan next phase | WORKSPACE: $(pwd)
    " &

# ═══════════════════════════════════════════════════════════════════
# CHECKPOINT TEMPLATES
# ═══════════════════════════════════════════════════════════════════

checkpoint:
  exec: |
    git add -A && git commit -m "checkpoint: $PHASE execution complete"
    update_cycle_state "$PHASE" "execute" "complete"
    # Update $CTX recent_actions

  fixes: |
    git add -A && git commit -m "checkpoint: $PHASE fixes applied"
    update_cycle_state "$PHASE" "fixes" "complete"
    # Update $CTX recent_actions

  final: |
    git add -A && git commit -m "checkpoint: $PHASE cycle complete"
    complete_cycle "complete" 1 0
    # Update $CTX focus, recent_actions

# ═══════════════════════════════════════════════════════════════════
# GATE CONFIG
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

# /hc-cy - Phase Cycle (YAML Config)

**HC orchestrates. Agents execute. State is sacred.**

## Usage

```
/hc-cy [N]        # N = number of phases (default: 1)
```

## Protocol

### 1. Initialize

```bash
source .claude/lib/agent-spawn.sh
recover_cycle
init_cycle_session "cycle_$(date +%Y%m%d_%H%M)" "PHASE-XXX"
sync_gate
```

### 2. Generate Todos

**CRITICAL:** Call TodoWrite with pattern from `patterns.N1` or `patterns.N2` above.

Copy the JSON array directly into TodoWrite tool call.

### 3. Execute Loop

```
For each todo:
  1. Mark in_progress
  2. If SPAWN step: Run template from spawn.{step} (background &)
  3. If CHECKPOINT step: Run template from checkpoint.{step}
  4. Mark completed
  5. Next
```

### 4. At [GATE]

Run `gate.commands`, ask user `gate.options`.

## Key Rules

| Rule | Description |
|------|-------------|
| **Background spawns** | All heavy work runs with `&` - HC stays available |
| **FLASH for fixes** | Fixes delegate to 2412, never inline |
| **Checkpoints** | Commit + state after execute, fixes, and final |
| **HC available** | Can answer user while agents work |

## Mantra

```
HC orchestrates. Agents execute.
Background spawns. HC stays available.
Checkpoint after every work block.
FIXES = FLASH workers, never inline.
```

---

**V2.0.0** | Background execution, checkpoint steps, FLASH fixes
