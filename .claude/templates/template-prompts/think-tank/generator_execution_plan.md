# Generator: Execution Plan
# Variables: {{SESSION_PATH}}, {{DECIDED_PATH}}, {{CONFIDENCE}}, {{PLAN_LEVEL}}, {{CRITIQUE_INPUT}}
# Model: HC_REAS_B (2411) for draft, HC_REAS_A (2410) for Gauntlet Writer role

## Your Mission

Create a test-driven, traceable execution plan based on the decided path and validated spec.

## Gauntlet Context (if in iteration)

If `{{CRITIQUE_INPUT}}` is provided, you are in **Writer mode**:
- Review each critique issue
- Respond with ACCEPTED (integrate fix) or REJECTED (cite evidence)
- Update the plan with ACCEPTED changes
- See `gauntlet_writer.md` for response protocol

## Context Files (read in order)

1. {{SESSION_PATH}}/00_BRIEFING.md - Original problem and constraints
2. {{SESSION_PATH}}/04_DECISION_MAP.md - The decision made
3. {{SESSION_PATH}}/05_SPEC.md - Technical feasibility spec (MUST exist)
4. {{SESSION_PATH}}/02_KNOWLEDGE_BASE/facts.yaml - Validated facts
5. .claude/PM/SSoT/NORTHSTAR.md - Requirements to trace

## Decision Made

Path: {{DECIDED_PATH}}
Confidence: {{CONFIDENCE}}

## Plan Level

{{PLAN_LEVEL}}  # FULL or OUTLINE

## Critical Requirements

1. **Traceability** - Every task links to NORTHSTAR requirement (trace_req)
2. **Definition of Done** - Every task has explicit success criteria
3. **Target Context** - Specify files/components affected
4. **Dependencies** - Explicit task dependencies

## Output

Write to: {{SESSION_PATH}}/execution-plan.yaml

### Schema

```yaml
meta:
  created: "{{TIMESTAMP}}"
  decided_path: "{{DECIDED_PATH}}"
  confidence: "{{CONFIDENCE}}"
  spec_path: "{{SESSION_PATH}}/05_SPEC.md"
  northstar_path: ".claude/PM/SSoT/NORTHSTAR.md"
  status: draft  # draft | approved | in_progress | complete

phases:
  - id: PHASE-01
    title: "Foundation"
    description: "Core infrastructure and setup"
    tasks:
      - id: P1-TASK-01
        action: "What to do"
        trace_req: "REQ-XXX"  # Link to NORTHSTAR requirement
        definition_of_done:
          - "Specific measurable outcome 1"
          - "Specific measurable outcome 2"
        target_context:
          - "src/path/to/file.ts"
          - "src/another/file.ts"
        dependencies: []  # Task IDs this depends on
        status: pending

      - id: P1-TASK-02
        action: "Next task"
        trace_req: "REQ-YYY"
        definition_of_done:
          - "Clear success criterion"
        target_context:
          - "src/component/"
        dependencies: [P1-TASK-01]
        status: pending

  - id: PHASE-02
    title: "Core Implementation"
    description: "..."
    tasks: [...]

risks:
  # Carry forward from SPEC.md
  - id: R1
    description: "Risk description"
    mitigation: "How we'll handle it"

validation:
  # How we know the whole plan succeeded
  - "Integration test passes"
  - "Performance target met"
```

## Rules

- **No orphan tasks** - Every task must trace to a requirement
- **No vague DoD** - "Works correctly" is not acceptable; be specific
- **Respect SPEC** - If SPEC.md flagged risks, include mitigations
- **If OUTLINE**: Create phases with 1-2 representative tasks each
- **If FULL**: Complete task breakdown with all fields populated

## Validation Before Output

- [ ] Every task has trace_req linking to NORTHSTAR
- [ ] Every task has at least one definition_of_done item
- [ ] Every task has target_context (even if "TBD" for OUTLINE)
- [ ] Dependencies form a valid DAG (no cycles)
- [ ] Risks from SPEC.md are addressed
