# Task Plan Generator Template

> **Diffusion Phase 4, Step 7**: Break Phase Roadmap deliverables into concrete tasks

---

## Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{SESSION_PATH}}` | Think-tank session directory | `.claude/PM/think-tank/auth_20260103/` |
| `{{PHASE_ROADMAP_PATH}}` | Path to Phase Roadmap | `{{SESSION_PATH}}/phase_roadmap.yaml` |

---

## Agent Instructions

You are generating a **Task Plan** - the blueprint level of the Diffusion hierarchy.

### Step 1: Read Inputs

```
Read {{PHASE_ROADMAP_PATH}}
Read .claude/PM/SSoT/NORTHSTAR.md (alignment reference)
Read .claude/templates/think-tank/TASK_PLAN_SCHEMA.md (output schema)
```

### Step 2: Extract Deliverables

From the Phase Roadmap, identify:
- All deliverables (`deliverables:` section)
- Their IDs (e.g., `DELIV-001`, `DELIV-002`)
- Success criteria for each
- Dependencies between deliverables

### Step 3: Decompose into Tasks

For each deliverable, create tasks that:

1. **Produce concrete artifacts** - files, functions, components
2. **Are independently testable** - clear acceptance criteria
3. **Have bounded scope** - specific files affected
4. **Fit the architecture** - align with established patterns

**Task Sizing Guideline:**
- 1 task = 1-3 tickets when implemented
- If a task would produce >5 tickets, split it

### Step 4: Scope & Physics Check (CRITICAL)

Before finalizing, validate EVERY task:

#### 4.1 Traceability Check
```
For each task:
  - Does trace_req point to a valid DELIV-XXX from Phase Roadmap?
  - If NO → REJECT task (bloat detected)
```

#### 4.2 Architecture Fit Check
```
For each task:
  - Does it use established patterns from the codebase?
  - Does it introduce new patterns?
    - If new: Document in rationale, flag for review
  - Does it conflict with existing architecture?
    - If conflict: STOP, create Decision Brief
```

#### 4.3 Scope Drift Check
```
Compare Task Plan scope vs Phase Roadmap scope:
  - Are we building MORE than Phase Roadmap requires? → Bloat
  - Are we building LESS than Phase Roadmap requires? → Gap
  - Are we building DIFFERENT than Phase Roadmap requires? → Drift
```

### Step 5: Generate physics_summary

Summarize validation results:

```yaml
physics_summary:
  architecture_fit: true | false
  scope_drift_check: true | false
  notes: 'Summary of concerns or confirmations'
```

**If either check is false:**
- Document specific concerns
- Flag for human review before proceeding
- Do NOT proceed to ticket generation

---

## Output Format

Write `task_plan.yaml` to `{{SESSION_PATH}}/task_plan.yaml`

Use schema from `.claude/templates/think-tank/TASK_PLAN_SCHEMA.md`

---

## Validation Checklist

Before writing output, confirm:

- [ ] **Every task has trace_req** → Points to Phase Roadmap deliverable
- [ ] **No orphan tasks** → Nothing exists without traceability
- [ ] **Every task has physics_check** → Architecture alignment documented
- [ ] **files_affected is specific** → No wildcards, actual paths
- [ ] **acceptance_criteria are testable** → Can verify completion
- [ ] **dependencies form valid DAG** → No circular dependencies
- [ ] **physics_summary is accurate** → Reflects overall assessment

---

## Anti-Bloat Rules

### Rule 1: No Task Without Traceability
```yaml
# VALID
trace_req: 'DELIV-003'

# INVALID - REJECT
trace_req: null
trace_req: 'nice-to-have'
trace_req: 'future-enhancement'
```

### Rule 2: No Scope Expansion
```
Phase Roadmap says: "User authentication"
Task Plan should NOT include:
  - "Admin dashboard" (not in scope)
  - "Email notifications" (not in scope)
  - "Analytics tracking" (not in scope)
```

### Rule 3: Architecture Must Fit
```yaml
# If introducing new pattern
physics_check:
  fits_architecture: false
  rationale: 'New state management approach - requires Decision Brief'
# → STOP and escalate
```

---

## Example Output Structure

```yaml
meta:
  schema_version: '1.0.0'
  created: '{{TIMESTAMP}}'
  author: 'think-tank'

phase_id: '{{PHASE_ID}}'
phase_roadmap_path: '{{PHASE_ROADMAP_PATH}}'

physics_summary:
  architecture_fit: true
  scope_drift_check: true
  notes: 'All tasks trace to Phase Roadmap deliverables'

tasks:
  - task_id: 'TASK-001'
    title: 'Descriptive title'
    trace_req: 'DELIV-001'
    physics_check:
      fits_architecture: true
      rationale: 'Uses existing pattern'
    deliverable: 'Concrete artifact'
    files_affected:
      create: ['specific/path.ts']
      modify: ['existing/file.ts']
      delete: []
    acceptance_criteria:
      - 'Testable condition 1'
      - 'Testable condition 2'
    dependencies: []
    status: 'pending'
    estimated_tickets: 2
```

---

## Error Conditions

| Condition | Action |
|-----------|--------|
| Task without trace_req | REJECT task, do not include |
| Architecture conflict | STOP, create Decision Brief |
| Scope drift detected | Flag in physics_summary, note concerns |
| Circular dependencies | Restructure task order |
| Phase Roadmap not found | ABORT, report missing input |
