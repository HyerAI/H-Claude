---
version: V2.2.0
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

## The Cycle (7 Core Steps Per Phase)

```
┌─────────────────────────────────────────────────────────────┐
│  1. EXECUTE     Spawn /hc-execute (background)              │
│  2. AUDIT       Spawn /red-team (background)                │
│  3. FIXES       Spawn FLASH workers (background)            │
│  4. CHECKPOINT  git commit + update $CTX                    │
│  5. VALIDATE    Spawn /hc-glass (background)                │
│  6. PLAN        Spawn /think-tank (background)              │
│  7. CHECKPOINT  git commit + complete_cycle                 │
├─────────────────────────────────────────────────────────────┤
│  [GATE] User confirms before next phase (if N > 1)          │
└─────────────────────────────────────────────────────────────┘
```

> **Note:** Step 2 checkpoint (after execute) was removed in V2.2.0.
> Execute output isn't validated until Audit completes - checkpointing
> incomplete work has no recovery value. First meaningful recovery
> point is Step 4 (after fixes are applied and verified).

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
N = 1:  7 steps
N = 2:  7 + 1 (gate) + 7 = 15 steps
N = 3:  7 + 1 + 7 + 1 + 7 = 23 steps
N:      7*N + (N-1) gates
```

#### Pattern: Single Phase (N=1)

```json
[
  {"content": "[1/7] Execute phase", "status": "in_progress", "activeForm": "Spawning /hc-execute"},
  {"content": "[2/7] Audit phase", "status": "pending", "activeForm": "Spawning /red-team"},
  {"content": "[3/7] Fixes: spawn FLASH workers", "status": "pending", "activeForm": "Spawning fix workers"},
  {"content": "[4/7] Checkpoint: commit + state", "status": "pending", "activeForm": "Committing fixes"},
  {"content": "[5/7] Validate phase", "status": "pending", "activeForm": "Spawning /hc-glass"},
  {"content": "[6/7] Plan next phase", "status": "pending", "activeForm": "Spawning /think-tank"},
  {"content": "[7/7] Final checkpoint + complete", "status": "pending", "activeForm": "Final commit + complete_cycle"}
]
```

#### Pattern: Multi-Phase (N=2, 3, 5, 10...)

For N phases, generate todos following this structure:

```
For phase P in 1..N:
  [P{P} 1/7] Execute phase
  [P{P} 2/7] Audit phase
  [P{P} 3/7] Fixes: FLASH workers
  [P{P} 4/7] Checkpoint
  [P{P} 5/7] Validate phase
  [P{P} 6/7] Plan next phase
  [P{P} 7/7] Checkpoint (or "Final checkpoint + complete" if last phase)

  If P < N:
    [GATE] Confirm before P{P+1}
```

**Example: N=3 (23 steps)**

```json
[
  {"content": "[P1 1/7] Execute", "status": "in_progress", "activeForm": "Spawning /hc-execute (P1)"},
  {"content": "[P1 2/7] Audit", "status": "pending", "activeForm": "Spawning /red-team (P1)"},
  {"content": "[P1 3/7] Fixes", "status": "pending", "activeForm": "Spawning fix workers (P1)"},
  {"content": "[P1 4/7] Checkpoint", "status": "pending", "activeForm": "Committing P1 fixes"},
  {"content": "[P1 5/7] Validate", "status": "pending", "activeForm": "Spawning /hc-glass (P1)"},
  {"content": "[P1 6/7] Plan", "status": "pending", "activeForm": "Spawning /think-tank (P1)"},
  {"content": "[P1 7/7] Checkpoint", "status": "pending", "activeForm": "Committing P1 complete"},
  {"content": "[GATE] Confirm P2", "status": "pending", "activeForm": "User gate: continue to P2?"},
  {"content": "[P2 1/7] Execute", "status": "pending", "activeForm": "Spawning /hc-execute (P2)"},
  {"content": "[P2 2/7] Audit", "status": "pending", "activeForm": "Spawning /red-team (P2)"},
  {"content": "[P2 3/7] Fixes", "status": "pending", "activeForm": "Spawning fix workers (P2)"},
  {"content": "[P2 4/7] Checkpoint", "status": "pending", "activeForm": "Committing P2 fixes"},
  {"content": "[P2 5/7] Validate", "status": "pending", "activeForm": "Spawning /hc-glass (P2)"},
  {"content": "[P2 6/7] Plan", "status": "pending", "activeForm": "Spawning /think-tank (P2)"},
  {"content": "[P2 7/7] Checkpoint", "status": "pending", "activeForm": "Committing P2 complete"},
  {"content": "[GATE] Confirm P3", "status": "pending", "activeForm": "User gate: continue to P3?"},
  {"content": "[P3 1/7] Execute", "status": "pending", "activeForm": "Spawning /hc-execute (P3)"},
  {"content": "[P3 2/7] Audit", "status": "pending", "activeForm": "Spawning /red-team (P3)"},
  {"content": "[P3 3/7] Fixes", "status": "pending", "activeForm": "Spawning fix workers (P3)"},
  {"content": "[P3 4/7] Checkpoint", "status": "pending", "activeForm": "Committing P3 fixes"},
  {"content": "[P3 5/7] Validate", "status": "pending", "activeForm": "Spawning /hc-glass (P3)"},
  {"content": "[P3 6/7] Plan", "status": "pending", "activeForm": "Spawning /think-tank (P3)"},
  {"content": "[P3 7/7] Final checkpoint + complete", "status": "pending", "activeForm": "Final commit + complete_cycle"}
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

## /hc-glass Output Consumption (Step 6 → Step 7)

After Step 6 (Validate), `/hc-glass` produces `SYSTEM_REVIEW_GLASS.md` with four lists:

| List | Severity | What HC Does |
|------|----------|--------------|
| **PANIC** | Critical | **IMMEDIATE.** Pause cycle, spawn FLASH workers to fix before Step 7 |
| **LIE** | Major | Document in AUDIT_REPORT, feed to next cycle's /red-team |
| **KILL** | Minor | Spawn FLASH worker to delete dead code |
| **DEBT** | Info | Add to `$BACKLOG` for future phases |

**HC's Responsibilities Between Step 6 and Step 7:**

1. **Read** `SYSTEM_REVIEW_GLASS.md`
2. **Triage:**
   - PANIC? → Spawn fix workers NOW, do NOT proceed to Step 7 until resolved
   - KILL? → Spawn FLASH worker to delete the files
   - LIE/DEBT? → Log for downstream (LIE → next audit, DEBT → backlog)
3. **Update $CTX** with glass_findings summary
4. **Proceed to Step 7** (Plan) only when PANIC list is empty

```bash
# Example: Step 6 complete, reviewing GLASS output
# Check PANIC list
PANIC_COUNT=$(grep -c "## PANIC" "${GLASS_SESSION}/SYSTEM_REVIEW_GLASS.md" || echo 0)

if [[ $PANIC_COUNT -gt 0 ]]; then
  echo "[CRITICAL] PANIC findings - must fix before proceeding"
  # Spawn FLASH workers for each PANIC item
  # ... then revalidate
else
  echo "[OK] No PANIC findings - proceeding to Step 7"
fi
```

**Note:** GLASS output is NOT consumed by `/think-tank` directly. HC reviews and triages, ensuring PANIC items are resolved before planning begins.

---

## Key Rules

| Rule | Why |
|------|-----|
| **Background spawns** | HC stays available for user |
| **FLASH for fixes** | Protect HC context window |
| **Checkpoints** | Commit after fixes (validated work), and final |
| **Gates between phases** | User controls pace |
| **Full todos upfront** | Clear progress visibility |
| **Pre-cycle validation** | Check proxies + prereqs before starting |

---

## Mantra

```
HC orchestrates. Agents execute.
Background spawns. HC stays available.
Checkpoint after validated work (fixes + final).
FIXES = FLASH workers, never inline.
State is sacred. Pre-validate always.
```

---

**V2.2.0** | Removed redundant checkpoint, added pre-cycle validation, 7-step cycle

