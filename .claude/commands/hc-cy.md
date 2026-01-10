---
version: V2.1.0
description: "Phase Cycle Orchestrator - HC orchestrates, agents execute"
---

# /hc-cy - Phase Cycle Orchestrator

**HC orchestrates. Agents execute. State is sacred.**

---

## Usage

```
/hc-cy          # 1 phase (default)
/hc-cy 2        # 2 phases with gate between
/hc-cy 5        # 5 phases with gates between each
/hc-cy N        # N phases
```

---

## The Cycle (8 Steps Per Phase)

```
┌─────────────────────────────────────────────────────────────┐
│  1. EXECUTE     Spawn /hc-execute (background)              │
│  2. CHECKPOINT  git commit + update $CTX                    │
│  3. AUDIT       Spawn /red-team (background)                │
│  4. FIXES       Spawn FLASH workers (background)            │
│  5. CHECKPOINT  git commit + update $CTX                    │
│  6. VALIDATE    Spawn /hc-glass (background)                │
│  7. PLAN        Spawn /think-tank (background)              │
│  8. CHECKPOINT  git commit + complete_cycle                 │
├─────────────────────────────────────────────────────────────┤
│  [GATE] User confirms before next phase (if N > 1)          │
└─────────────────────────────────────────────────────────────┘
```

---

## HC Role

```
HC = ORCHESTRATOR + USER LIAISON

HC DOES:
  - Spawn agents (background)
  - Review results
  - Update state ($CTX, commits)
  - Talk to user while agents work

HC DOES NOT:
  - Write code inline
  - Apply fixes directly
  - Block on long operations
```

---

## Protocol

### STEP 0: Initialize

```bash
source .claude/lib/agent-spawn.sh
recover_cycle
init_cycle_session "cycle_$(date +%Y%m%d_%H%M)" "PHASE-XXX"
sync_gate
```

### STEP 1: Generate Todos for N Phases

**CRITICAL:** Generate ALL todos upfront using TodoWrite.

#### Formula: Total Steps

```
N = 1:  8 steps
N = 2:  8 + 1 (gate) + 8 = 17 steps
N = 3:  8 + 1 + 8 + 1 + 8 = 26 steps
N:      8*N + (N-1) gates
```

#### Pattern: Single Phase (N=1)

```json
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
```

#### Pattern: Multi-Phase (N=2, 3, 5, 10...)

For N phases, generate todos following this structure:

```
For phase P in 1..N:
  [P{P} 1/8] Execute phase
  [P{P} 2/8] Checkpoint
  [P{P} 3/8] Audit phase
  [P{P} 4/8] Fixes: FLASH workers
  [P{P} 5/8] Checkpoint
  [P{P} 6/8] Validate phase
  [P{P} 7/8] Plan next phase
  [P{P} 8/8] Checkpoint (or "Final checkpoint + complete" if last phase)

  If P < N:
    [GATE] Confirm before P{P+1}
```

**Example: N=3 (26 steps)**

```json
[
  {"content": "[P1 1/8] Execute", "status": "in_progress", "activeForm": "Spawning /hc-execute (P1)"},
  {"content": "[P1 2/8] Checkpoint", "status": "pending", "activeForm": "Committing P1 execution"},
  {"content": "[P1 3/8] Audit", "status": "pending", "activeForm": "Spawning /red-team (P1)"},
  {"content": "[P1 4/8] Fixes", "status": "pending", "activeForm": "Spawning fix workers (P1)"},
  {"content": "[P1 5/8] Checkpoint", "status": "pending", "activeForm": "Committing P1 fixes"},
  {"content": "[P1 6/8] Validate", "status": "pending", "activeForm": "Spawning /hc-glass (P1)"},
  {"content": "[P1 7/8] Plan", "status": "pending", "activeForm": "Spawning /think-tank (P1)"},
  {"content": "[P1 8/8] Checkpoint", "status": "pending", "activeForm": "Committing P1 complete"},
  {"content": "[GATE] Confirm P2", "status": "pending", "activeForm": "User gate: continue to P2?"},
  {"content": "[P2 1/8] Execute", "status": "pending", "activeForm": "Spawning /hc-execute (P2)"},
  {"content": "[P2 2/8] Checkpoint", "status": "pending", "activeForm": "Committing P2 execution"},
  {"content": "[P2 3/8] Audit", "status": "pending", "activeForm": "Spawning /red-team (P2)"},
  {"content": "[P2 4/8] Fixes", "status": "pending", "activeForm": "Spawning fix workers (P2)"},
  {"content": "[P2 5/8] Checkpoint", "status": "pending", "activeForm": "Committing P2 fixes"},
  {"content": "[P2 6/8] Validate", "status": "pending", "activeForm": "Spawning /hc-glass (P2)"},
  {"content": "[P2 7/8] Plan", "status": "pending", "activeForm": "Spawning /think-tank (P2)"},
  {"content": "[P2 8/8] Checkpoint", "status": "pending", "activeForm": "Committing P2 complete"},
  {"content": "[GATE] Confirm P3", "status": "pending", "activeForm": "User gate: continue to P3?"},
  {"content": "[P3 1/8] Execute", "status": "pending", "activeForm": "Spawning /hc-execute (P3)"},
  {"content": "[P3 2/8] Checkpoint", "status": "pending", "activeForm": "Committing P3 execution"},
  {"content": "[P3 3/8] Audit", "status": "pending", "activeForm": "Spawning /red-team (P3)"},
  {"content": "[P3 4/8] Fixes", "status": "pending", "activeForm": "Spawning fix workers (P3)"},
  {"content": "[P3 5/8] Checkpoint", "status": "pending", "activeForm": "Committing P3 fixes"},
  {"content": "[P3 6/8] Validate", "status": "pending", "activeForm": "Spawning /hc-glass (P3)"},
  {"content": "[P3 7/8] Plan", "status": "pending", "activeForm": "Spawning /think-tank (P3)"},
  {"content": "[P3 8/8] Final checkpoint + complete", "status": "pending", "activeForm": "Final commit + complete_cycle"}
]
```

---

### STEP 2: Execute Each Todo

#### Spawn Steps (Execute, Audit, Fixes, Validate, Plan)

Run in background - HC stays available:

| Step | Port | Command |
|------|------|---------|
| Execute | 2414 | `/hc-execute` |
| Audit | 2414 | `/red-team` |
| Fixes | 2412 | FLASH workers (one per fix) |
| Validate | 2414 | `/hc-glass` |
| Plan | 2415 | `/think-tank` |

```bash
ANTHROPIC_API_BASE_URL=http://localhost:$PORT claude --dangerously-skip-permissions -p "PROMPT" &
```

#### Checkpoint Steps

HC does directly (quick):

```bash
git add -A && git commit -m "checkpoint: P$PHASE step complete"
update_cycle_state "$PHASE" "$STEP" "complete"
```

#### Fixes Step (CRITICAL)

**NEVER apply fixes inline.** Spawn FLASH workers:

```bash
# For EACH fix from audit report:
ANTHROPIC_API_BASE_URL=http://localhost:2412 claude --dangerously-skip-permissions -p "
WORKSPACE: $(pwd)
FIX: [description]
FILE: [target]
Apply this fix. Use TDD if applicable.
" &
```

---

### STEP 3: At [GATE] (Multi-Phase Only)

```bash
sync_gate
cycle_status
```

Ask user: **CONTINUE | PAUSE | ABORT**

| Choice | Action |
|--------|--------|
| CONTINUE | Proceed to next phase |
| PAUSE | Save state, exit (resume with `recover_cycle`) |
| ABORT | Stop, keep completed work |

---

## Key Rules

| Rule | Why |
|------|-----|
| **Background spawns** | HC stays available for user |
| **FLASH for fixes** | Protect HC context window |
| **Checkpoints** | Commit after execute, fixes, final |
| **Gates between phases** | User controls pace |
| **Full todos upfront** | Clear progress visibility |

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

**V2.1.0** | Multi-phase support, clear todo generation, background execution

