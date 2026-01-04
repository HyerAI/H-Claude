# ADR-004: hc-execute Self-Review Improvements

**Date:** 2026-01-04
**Status:** Approved
**Deciders:** HeyDude, Council (Execution Architect, Operations Guardian)
**Source:** `.claude/PM/think-tank/hc_execute_self_review_20260104/`

---

## Context

Self-review of hc-execute V2.8.0 revealed design-vs-reality gaps:

| Finding | Evidence |
|---------|----------|
| SWEEP may not run | No SWEEP_REPORT.md in any session |
| Artifact trail broken | No PHASE_X/ folders, WORKER_OUTPUTS exist |
| 100% success paradox | 36 tasks, 0 failures across 3 sessions |
| RETRY_FAILED untested | Recovery path never exercised |
| Context gap | Triangulated context documented but not in worker template |

The system appears to succeed by bypassing its own safety layers.

---

## Decision

### P0: SWEEP Verification & Fix

**Action:** Add STDOUT markers + force SWEEP_REPORT.md creation

```markdown
[SWEEP] Starting adversarial audit...
[SWEEP] Checking 5 categories: missing, partial, integration, edge, files
[SWEEP] Complete. Verdict: CLEAN | GAPS_FOUND
```

Force artifact creation even if empty:
```
ANALYSIS/SWEEP_REPORT.md (created even with verdict: CLEAN)
```

### P1: Artifact Trail Enforcement

**Action:** Mandate folder structure creation at Phase 2 start

```
SESSION/
├── PHASE_X/
│   ├── ORACA_LOG.md
│   ├── WORKER_OUTPUTS/
│   │   └── TASK_*_EVIDENCE.md
│   └── PHASE_QA.md
├── ANALYSIS/
│   ├── QA_SYNTHESIS.md
│   └── SWEEP_REPORT.md
```

Orchestrator creates structure BEFORE spawning Oraca.

### P2: Test RETRY_FAILED

**Action:** Create synthetic failure test

1. Modify one task to intentionally fail
2. Verify EXECUTION_STATE.md captures failure
3. Run RETRY_FAILED
4. Verify only failed task re-runs
5. Verify SWEEP re-runs after

Document test results in ADR or remove if broken.

### P3: Triangulated Context

**Action:** Add to worker_task.md template

```markdown
## Triangulated Context

**Goal:** {{GOAL}} (from execution-plan.yaml)
**Bedrock:** {{BEDROCK_FILES}} (foundational knowledge)
**Instruction:** {{TASK_DESCRIPTION}} (what to do)
```

Workers understand WHY, not just WHAT.

---

## Consequences

### Positive
- Observability: Can audit past executions
- Confidence: Know SWEEP actually runs
- Recovery: Validated fallback path
- Context: Workers understand purpose

### Negative
- Slightly more artifacts to manage
- Test adds ~5 minutes to validation

### Neutral
- Version bump to V2.9.0

---

## Constraints Honored

| Constraint | How |
|------------|-----|
| KISS | Markers are simple STDOUT, not new infrastructure |
| YAGNI | Testing existing code, not adding features |
| No new dependencies | Uses existing proxy setup |
| Min repo | Empty artifacts still minimal |

---

## Implementation

See: `execution-plan.yaml` in same session folder

**Version:** V2.9.0
