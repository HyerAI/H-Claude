---
sector: 6
target: Diffusion Templates
status: WARN
issues_found: 5
---

# SECTOR 06: Template Fitness Audit

**Auditor:** Opus 4.5 Sector Commander
**Date:** 2026-01-03
**Focus:** Diffusion Development templates for think-tank V2.3.0

---

## Template Inventory

### Schema Templates (`.claude/templates/think-tank/`)

| Template | Status | Notes |
|----------|--------|-------|
| `PHASE_ROADMAP_SCHEMA.md` | EXISTS | Schema v1.0.0, comprehensive |
| `TASK_PLAN_SCHEMA.md` | EXISTS | Schema v1.0.0, includes physics_check |
| `TICKET_SCHEMA.md` | EXISTS | Level 5 Instruction format |

### Generator Templates (`.claude/templates/template-prompts/think-tank/`)

| Template | Status | Notes |
|----------|--------|-------|
| `generator_phase_roadmap.md` | EXISTS | References PHASE_ROADMAP_SCHEMA.md |
| `generator_task_plan.md` | EXISTS | References TASK_PLAN_SCHEMA.md |
| `generator_tickets.md` | EXISTS | References TICKET_SCHEMA.md |

### Validator Templates (`.claude/templates/template-prompts/think-tank/`)

| Template | Status | Notes |
|----------|--------|-------|
| `validator_simulation.md` | EXISTS | Step 6 gate - Phase Roadmap vs NS + Codebase |
| `validator_physics.md` | EXISTS | Step 7 gate - Task Plan traceability |
| `validator_resolution.md` | EXISTS | Step 8 gate - Ticket determinism |
| `validator_lookahead.md` | EXISTS | Step 9 gate - Horizon check |

---

## Cross-Reference Check

### Schema → Generator Chain

| Schema | Generator | Status |
|--------|-----------|--------|
| `PHASE_ROADMAP_SCHEMA.md` | `generator_phase_roadmap.md` | PASS - Line 27: `Read: .claude/templates/think-tank/PHASE_ROADMAP_SCHEMA.md` |
| `TASK_PLAN_SCHEMA.md` | `generator_task_plan.md` | PASS - Line 26: `Read .claude/templates/think-tank/TASK_PLAN_SCHEMA.md` |
| `TICKET_SCHEMA.md` | `generator_tickets.md` | PASS - Line 24: `Read .claude/templates/think-tank/TICKET_SCHEMA.md` |

### Generator → Validator Chain

| Generator Output | Validator | Status |
|-----------------|-----------|--------|
| `phase_roadmap.yaml` | `validator_simulation.md` | PASS - Validates Phase Roadmap |
| `task_plan.yaml` | `validator_physics.md` | PASS - Validates Task Plan |
| `tickets/*.yaml` | `validator_resolution.md` | PASS - Validates Tickets |
| Post-execution | `validator_lookahead.md` | PASS - Validates horizon alignment |

### think-tank.md Command References

| Template Reference | Status |
|-------------------|--------|
| Line 849: `generator_phase_roadmap.md` | VALID |
| Line 850: `generator_task_plan.md` | VALID |
| Line 851: `generator_tickets.md` | VALID |
| Line 857: `validator_simulation.md` | VALID |
| Line 858: `validator_physics.md` | VALID |
| Line 859: `validator_resolution.md` | VALID |
| Line 860: `validator_lookahead.md` | VALID |
| Lines 866-868: Schema references | VALID |

---

## Findings

### CRITICAL (0)

None.

### HIGH (2)

#### F-001: Inconsistent Variable Naming Convention
**Severity:** HIGH
**Location:** Across generators

| Template | Variable Format | Issue |
|----------|-----------------|-------|
| `generator_phase_roadmap.md` | `{{PHASE_ID}}`, `{{ROADMAP_PATH}}` | Double-brace |
| `generator_task_plan.md` | `{{SESSION_PATH}}`, `{{PHASE_ROADMAP_PATH}}` | Double-brace |
| `generator_tickets.md` | `{{SESSION_PATH}}`, `{{TASK_PLAN_PATH}}` | Uses both single and double conventions |

**Recommendation:** Standardize on `{{VARIABLE}}` format consistently.

#### F-002: Path Inconsistency in Task Plan Generator
**Severity:** HIGH
**Location:** `generator_task_plan.md:12-13`

The generator references `{{SESSION_PATH}}/phase-roadmap.yaml` but `generator_phase_roadmap.md:163` outputs to `{{SESSION_PATH}}/phase_roadmap.yaml` (underscore vs hyphen).

**Impact:** Chain break - Task Plan generator may not find Phase Roadmap.

**Recommendation:** Standardize to `phase_roadmap.yaml` (underscore) across all templates.

### MEDIUM (2)

#### F-003: Validator Input Path References May Mismatch
**Severity:** MEDIUM
**Location:** `validator_simulation.md:127-129`

Validator expects research files at:
- `{SESSION_PATH}/research/northstar_analysis.md`
- `{SESSION_PATH}/research/bedrock_analysis.md`

But `generator_phase_roadmap.md` doesn't create these files - it reads NORTHSTAR.md directly and performs bedrock analysis inline.

**Impact:** Validator may not find expected input files.

**Recommendation:** Either:
1. Update generator to output analysis files, OR
2. Update validator to read from actual sources (NORTHSTAR.md, phase_roadmap.yaml)

#### F-004: Validator Resolution Path Variable
**Severity:** MEDIUM
**Location:** `validator_resolution.md:6`

Variable `TICKETS_PATH` expects single file (`tickets.yaml`) but `generator_tickets.md:91-99` outputs to folder structure (`tickets/TKT-YYYYMMDD-NNN.yaml`).

**Impact:** Validator may not correctly iterate over ticket files.

**Recommendation:** Update validator to glob `${SESSION_PATH}/tickets/*.yaml` instead of expecting single file.

### LOW (1)

#### F-005: Orphan Legacy Templates
**Severity:** LOW
**Location:** `template-prompts/think-tank/`

Legacy templates still exist but marked deprecated in think-tank.md (lines 874-878):
- `scout_codebase.md`
- `scout_docs.md`
- `scout_web.md`
- `scout_consensus.md`

**Impact:** Potential confusion; no active use.

**Recommendation:** Either remove or move to `archive/` subfolder.

---

## Variable Naming Audit

### Generators

| Template | Variables Used |
|----------|----------------|
| `generator_phase_roadmap.md` | `SESSION_PATH`, `PHASE_ID`, `ROADMAP_PATH` |
| `generator_task_plan.md` | `SESSION_PATH`, `PHASE_ROADMAP_PATH`, `PHASE_ID`, `TIMESTAMP` |
| `generator_tickets.md` | `SESSION_PATH`, `TASK_PLAN_PATH` |

### Validators

| Template | Variables Used |
|----------|----------------|
| `validator_simulation.md` | `SESSION_PATH`, `PHASE_ROADMAP_PATH` |
| `validator_physics.md` | `SESSION_PATH`, `TASK_PLAN_PATH`, `PHASE_ROADMAP_PATH` |
| `validator_resolution.md` | `SESSION_PATH`, `TICKETS_PATH` |
| `validator_lookahead.md` | `SESSION_PATH`, `COMPLETED_TICKET_PATH`, `NS_PATH` |

**Assessment:** Variable naming is reasonably consistent across templates. `SESSION_PATH` is universal anchor.

---

## Recommendations

### Priority 1 (Fix Before Use)

1. **Standardize `phase_roadmap.yaml` filename** across all templates (underscore, not hyphen)
2. **Update `validator_resolution.md`** to glob ticket folder instead of expecting single file

### Priority 2 (Improve Quality)

3. **Align `validator_simulation.md`** input expectations with generator outputs
4. **Document variable injection mechanism** in think-tank.md or a VARIABLES.md reference

### Priority 3 (Cleanup)

5. **Archive deprecated scout templates** to `archive/` subfolder
6. **Add schema version checks** to generators (ensure schema version compatibility)

---

## Summary

| Check | Result |
|-------|--------|
| All templates exist | PASS |
| Generator→Schema references correct | PASS |
| Validator→Gate mapping correct | PASS |
| Cross-reference integrity | WARN (path inconsistencies) |
| Variable naming consistency | WARN (minor variations) |
| Orphan templates | LOW (deprecated templates remain) |

**Overall Status:** WARN

The Diffusion template set is functionally complete but has path/naming inconsistencies that could cause chain breaks during execution. F-002 (path inconsistency) is the most critical issue to resolve before production use.

---

## Audit Trail

- Templates audited: 10 (3 schemas, 4 generators, 4 validators)
- Cross-references verified: 14
- Issues found: 5 (0 CRITICAL, 2 HIGH, 2 MEDIUM, 1 LOW)
