# Task Plan Schema (Level 4: Blueprint)

> **Hierarchy:** NORTHSTAR → ROADMAP → Phase Roadmap → **Task Plan** → Tickets

## Purpose

Break Phase Roadmap deliverables into concrete, traceable tasks. Each task produces a specific artifact and must pass physics checks to prevent scope bloat.

---

## Schema

```yaml
meta:
  schema_version: '1.0.0'
  created: 'YYYY-MM-DDTHH:MM:SSZ'
  author: 'agent | user'

# Parent reference - every task traces upward
phase_id: 'PHASE-XXX'
phase_roadmap_path: '.claude/PM/think-tank/{session}/phase-roadmap.yaml'

# Validation gates
physics_summary:
  architecture_fit: true | false  # Does this align with established patterns?
  scope_drift_check: true | false # Are we building only what Phase Roadmap requires?
  notes: 'Any concerns or clarifications'

tasks:
  - task_id: 'TASK-001'
    title: 'Short descriptive title'

    # Anti-bloat traceability (REQUIRED)
    trace_req: 'DELIV-001'  # Which Phase Roadmap deliverable this implements

    # Physics check (REQUIRED)
    physics_check:
      fits_architecture: true | false
      rationale: 'Why this belongs / concern if false'

    # What gets built
    deliverable: 'Concrete output (file, function, component)'

    # Scope boundaries
    files_affected:
      create:
        - 'path/to/new/file.ts'
      modify:
        - 'path/to/existing/file.ts'
      delete: []  # Rarely used, document why

    # Definition of Done
    acceptance_criteria:
      - 'Criterion 1: Specific, testable condition'
      - 'Criterion 2: Another measurable outcome'

    # Execution order
    dependencies: []  # Task IDs this depends on: ['TASK-001']

    # Progress tracking
    status: 'pending'  # pending | in_progress | complete | blocked

    # Optional: complexity signal for ticket splitting
    estimated_tickets: 1  # How many tickets this might become

  - task_id: 'TASK-002'
    # ... additional tasks
```

---

## Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| `phase_id` | Yes | Parent Phase Roadmap identifier |
| `trace_req` | Yes | Deliverable ID from Phase Roadmap (anti-bloat) |
| `physics_check` | Yes | Architecture alignment validation |
| `deliverable` | Yes | Concrete artifact produced |
| `files_affected` | Yes | Specific files to create/modify |
| `acceptance_criteria` | Yes | Testable completion conditions |
| `dependencies` | Yes | Task execution ordering (can be empty) |
| `status` | Yes | Current state |
| `estimated_tickets` | No | Complexity hint for next level |

---

## Anti-Bloat Rules

### 1. Every Task Traces Upward
```yaml
# GOOD - traces to Phase Roadmap deliverable
trace_req: 'DELIV-003'

# BAD - no traceability
trace_req: null  # REJECTED: Cannot justify existence
```

### 2. Physics Check Gate
```yaml
# GOOD - fits established patterns
physics_check:
  fits_architecture: true
  rationale: 'Uses existing auth middleware pattern'

# CONCERN - may need review
physics_check:
  fits_architecture: false
  rationale: 'Introduces new state management approach'
  # → Requires Decision Brief before proceeding
```

### 3. Scope Boundaries
- `files_affected` must be specific, not wildcards
- New files require justification in `physics_check.rationale`
- Deletions require explicit documentation

---

## Status Transitions

```
pending → in_progress → complete
    ↓
  blocked (document blocker, create Decision Brief if needed)
```

---

## Example

```yaml
meta:
  schema_version: '1.0.0'
  created: '2026-01-03T14:00:00Z'
  author: 'think-tank'

phase_id: 'PHASE-002'
phase_roadmap_path: '.claude/PM/think-tank/mvp_20260103/phase-roadmap.yaml'

physics_summary:
  architecture_fit: true
  scope_drift_check: true
  notes: 'All tasks align with established patterns from Phase 1'

tasks:
  - task_id: 'TASK-001'
    title: 'Create user model'
    trace_req: 'DELIV-001'  # "User data structure" from Phase Roadmap
    physics_check:
      fits_architecture: true
      rationale: 'Follows existing model patterns in src/models/'
    deliverable: 'User model with validation'
    files_affected:
      create:
        - 'src/models/user.ts'
        - 'src/models/user.test.ts'
      modify:
        - 'src/models/index.ts'
      delete: []
    acceptance_criteria:
      - 'User model exports from src/models/index.ts'
      - 'Validation rejects invalid email format'
      - 'Unit tests pass with >80% coverage'
    dependencies: []
    status: 'pending'
    estimated_tickets: 2

  - task_id: 'TASK-002'
    title: 'Implement auth endpoints'
    trace_req: 'DELIV-002'  # "Authentication API" from Phase Roadmap
    physics_check:
      fits_architecture: true
      rationale: 'Uses existing Express router pattern'
    deliverable: 'Login/logout/register endpoints'
    files_affected:
      create:
        - 'src/routes/auth.ts'
        - 'src/routes/auth.test.ts'
      modify:
        - 'src/routes/index.ts'
      delete: []
    acceptance_criteria:
      - 'POST /auth/register creates user'
      - 'POST /auth/login returns JWT'
      - 'POST /auth/logout invalidates session'
      - 'Integration tests pass'
    dependencies: ['TASK-001']
    status: 'pending'
    estimated_tickets: 3
```

---

## Validation Checklist

Before finalizing Task Plan:

- [ ] Every task has `trace_req` pointing to Phase Roadmap deliverable
- [ ] Every task has `physics_check` with rationale
- [ ] `files_affected` lists specific paths (no wildcards)
- [ ] `acceptance_criteria` are testable
- [ ] `dependencies` form valid DAG (no cycles)
- [ ] No orphan tasks (tasks not traced to Phase Roadmap)
- [ ] `physics_summary` reflects overall assessment
