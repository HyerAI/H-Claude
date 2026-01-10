---
version: V3.0.0
status: DEPRECATED
timestamp: 2026-01-10
description: "Phase cycle orchestrator - HC orchestrates, agents execute"
deprecated: true
superseded_by: /hc-cy
---

# /hc-phase-cycle - DEPRECATED

> **DEPRECATED:** This command has been superseded by `/hc-cy`.
> Use `/hc-cy` instead. This file will be removed in a future version.
>
> Migration: Replace `/hc-phase-cycle` with `/hc-cy` - identical functionality.

---

# /hc-phase-cycle - Phase Cycle Orchestrator (DEPRECATED)

**HC orchestrates. Agents execute. State is sacred.**

---

## Quick Start

```bash
/hc-phase-cycle [N]

/hc-phase-cycle           # 1 phase (default)
/hc-phase-cycle 2         # 2 phases
/hc-phase-cycle 3         # 3 phases
```

---

## The Cycle (Per Phase)

```text
┌─────────────────────────────────────────────────────────────┐
│  1. EXECUTE     Spawn /hc-execute (background)              │
│  2. CHECKPOINT  git commit + update $CTX                    │
│  3. AUDIT       Spawn /red-team (background)                │
│  4. FIXES       Spawn FLASH workers (background)            │
│  5. CHECKPOINT  git commit + update $CTX                    │
│  6. VALIDATE    Spawn /hc-glass (background)                │
│  7. PLAN        Spawn /think-tank (background)              │
│  8. CHECKPOINT  git commit + update $CTX + complete_cycle   │
├─────────────────────────────────────────────────────────────┤
│  [GATE] User confirms before next phase                     │
└─────────────────────────────────────────────────────────────┘
```

---

## HC's Role

```
┌─────────────────────────────────────────────────────────────┐
│  HC = ORCHESTRATOR + USER LIAISON                           │
│                                                             │
│  HC DOES:                                                   │
│    - Spawn agents (background)                              │
│    - Review results                                         │
│    - Update state ($CTX, commits)                           │
│    - Talk to user while agents work                         │
│                                                             │
│  HC DOES NOT:                                               │
│    - Write code inline                                      │
│    - Apply fixes directly                                   │
│    - Block on long operations                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Protocol

### STEP 0: Initialize

```bash
source .claude/lib/agent-spawn.sh

# Check for interrupted cycles
recover_cycle

# Init session (exports CYCLE_SESSION_PATH)
init_cycle_session "cycle_$(date +%Y%m%d_%H%M)" "PHASE-001"

# Verify clean state
sync_gate
```

### STEP 1: Generate ALL Todos Upfront

**CRITICAL:** Call TodoWrite immediately with ALL steps for ALL phases.

---

#### Pattern: N=1 (Single Phase - 8 steps)

```json
[
  {"content": "[1/8] Execute phase", "status": "in_progress", "activeForm": "Spawning /hc-execute"},
  {"content": "[2/8] Checkpoint: commit + state", "status": "pending", "activeForm": "Committing execution work"},
  {"content": "[3/8] Audit phase", "status": "pending", "activeForm": "Spawning /red-team"},
  {"content": "[4/8] Fixes: spawn FLASH workers", "status": "pending", "activeForm": "Spawning fix workers"},
  {"content": "[5/8] Checkpoint: commit + state", "status": "pending", "activeForm": "Committing fixes"},
  {"content": "[6/8] Validate phase", "status": "pending", "activeForm": "Spawning /hc-glass"},
  {"content": "[7/8] Plan next phase", "status": "pending", "activeForm": "Spawning /think-tank"},
  {"content": "[8/8] Final checkpoint + complete", "status": "pending", "activeForm": "Final commit + complete_cycle"}
]
```

---

#### Pattern: N=2 (Two Phases - 17 steps)

```json
[
  {"content": "[P1 1/8] Execute phase", "status": "in_progress", "activeForm": "Spawning /hc-execute (P1)"},
  {"content": "[P1 2/8] Checkpoint", "status": "pending", "activeForm": "Committing P1 execution"},
  {"content": "[P1 3/8] Audit phase", "status": "pending", "activeForm": "Spawning /red-team (P1)"},
  {"content": "[P1 4/8] Fixes: FLASH workers", "status": "pending", "activeForm": "Spawning fix workers (P1)"},
  {"content": "[P1 5/8] Checkpoint", "status": "pending", "activeForm": "Committing P1 fixes"},
  {"content": "[P1 6/8] Validate phase", "status": "pending", "activeForm": "Spawning /hc-glass (P1)"},
  {"content": "[P1 7/8] Plan next phase", "status": "pending", "activeForm": "Spawning /think-tank (P1)"},
  {"content": "[P1 8/8] Checkpoint", "status": "pending", "activeForm": "Committing P1 complete"},
  {"content": "[GATE] Confirm before P2", "status": "pending", "activeForm": "User gate: continue to P2?"},
  {"content": "[P2 1/8] Execute phase", "status": "pending", "activeForm": "Spawning /hc-execute (P2)"},
  {"content": "[P2 2/8] Checkpoint", "status": "pending", "activeForm": "Committing P2 execution"},
  {"content": "[P2 3/8] Audit phase", "status": "pending", "activeForm": "Spawning /red-team (P2)"},
  {"content": "[P2 4/8] Fixes: FLASH workers", "status": "pending", "activeForm": "Spawning fix workers (P2)"},
  {"content": "[P2 5/8] Checkpoint", "status": "pending", "activeForm": "Committing P2 fixes"},
  {"content": "[P2 6/8] Validate phase", "status": "pending", "activeForm": "Spawning /hc-glass (P2)"},
  {"content": "[P2 7/8] Plan next phase", "status": "pending", "activeForm": "Spawning /think-tank (P2)"},
  {"content": "[P2 8/8] Final checkpoint + complete", "status": "pending", "activeForm": "Final commit + complete_cycle"}
]
```

---

### Todo Rules

| Rule | Description |
|------|-------------|
| **Full upfront** | Generate ALL todos for ALL phases at init |
| **One active** | Exactly one todo `in_progress` at a time |
| **Immediate completion** | Mark done right after step completes |
| **Background spawns** | Heavy work runs async, HC stays available |
| **Checkpoints** | Commit after Execute, after Fixes, after Plan |

---

### STEP 2: Execute Each Todo

#### For SPAWN steps (Execute, Audit, Fixes, Validate, Plan):

```bash
# Run in background - HC stays available to user
ANTHROPIC_API_BASE_URL=http://localhost:$PORT claude --dangerously-skip-permissions -p "PROMPT" &

# Or use spawn_agent with run_in_background
spawn_agent "name" "prompt" "http://localhost:$PORT" &
```

**Check progress:** Read agent log or use `tail -f`
**HC stays available:** Can answer user questions while agents work

#### For CHECKPOINT steps:

```bash
# HC does this directly (quick, no delegation needed)
git add -A && git commit -m "checkpoint: [step description]"
update_cycle_state "$PHASE" "$STEP" "complete"

# Update context.yaml with current focus
```

#### For FIXES step (CRITICAL):

```text
┌─────────────────────────────────────────────────────────────┐
│  FIXES = DELEGATE TO FLASH WORKERS                          │
│                                                             │
│  HC reads the audit report (Kill/Fix list)                  │
│  HC spawns FLASH workers for EACH fix                       │
│  HC does NOT apply fixes inline                             │
│                                                             │
│  Why: Protect HC context window for orchestration           │
└─────────────────────────────────────────────────────────────┘
```

```bash
# For each fix item, spawn a FLASH worker:
ANTHROPIC_API_BASE_URL=http://localhost:2412 claude --dangerously-skip-permissions -p "
WORKSPACE: $(pwd)
FIX: [description from audit report]
FILE: [target file]

Apply this fix. Use TDD if applicable.
" &
```

---

## Spawn Templates

| Step | Port | Agent | Command |
|------|------|-------|---------|
| Execute | 2414 | HC-Orca | `/hc-execute` |
| Audit | 2414 | HC-Orca | `/red-team` |
| Fixes | 2412 | HC-Work (FLASH) | Individual fix tasks |
| Validate | 2414 | HC-Orca | `/hc-glass` |
| Plan | 2415 | HC-Orca-R | `/think-tank` |

---

## [GATE] Protocol

At each `[GATE]` todo:

```bash
sync_gate        # Verify state committed
cycle_status     # Show progress
```

Ask user: **CONTINUE | PAUSE | ABORT**

- CONTINUE → Proceed to next phase
- PAUSE → Save state, exit (resume with `recover_cycle`)
- ABORT → Stop, keep completed work

---

## Checkpoint Template

```bash
# After each major work block
git add -A
git commit -m "$(cat <<'EOF'
checkpoint: [PHASE] [STEP] complete

- [Brief description of work done]
- State: $CTX updated

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"

# Update context.yaml
# - recent_actions: add this step
# - focus: update if changed
```

---

## Mantra

```
HC orchestrates. Agents execute.
Background spawns. HC stays available.
Checkpoint after every work block.
FIXES = FLASH workers, never inline.
State is sacred.
```

---

## Related

| Command | When |
|---------|------|
| `/hc-execute` | Single phase, no cycle |
| `/think-tank --phase` | Plan only |
| `/red-team` | Audit only |
| `/hc-glass` | Validate only |

---

**V3.0.0** | Background execution, checkpoint steps, FLASH fixes
