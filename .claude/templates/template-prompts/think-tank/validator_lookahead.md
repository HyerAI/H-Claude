# Validator: Lookahead (Track B - Horizon Check)

## Purpose

Step 9 horizon validation in Diffusion Development dual-track execution. Runs parallel to Track A (Reality) validators. Ensures current implementation doesn't block the future User Experience defined in NORTHSTAR.

**Core Question:** Does this code block the future?

---

## Variables

```yaml
SESSION_PATH: {{SESSION_PATH}}           # Path to active think-tank session
COMPLETED_TICKET_PATH: {{COMPLETED_TICKET_PATH}}  # Path to completed ticket
NS_PATH: {{NS_PATH}}                     # Path to NORTHSTAR.md
```

---

## When to Trigger

- After each ticket completion (before marking ticket done)
- Before marking any phase complete
- When significant architectural decisions are implemented

---

## Validation Checks

### 1. Vision Compatibility

Does new code support NORTHSTAR goals?

**Check:**
- Read NS_PATH for stated goals and user journeys
- Compare implementation against each relevant goal
- Verify code doesn't contradict stated vision

**Questions:**
- Does this implementation move toward or away from the NS vision?
- Are the patterns used consistent with NS requirements?
- Does this support the target user experience?

### 2. Future Blocking Analysis

Does this implementation block any future features?

**Check:**
- Review remaining phases in ROADMAP.yaml
- Identify features this code might interact with
- Assess if current implementation constrains future options

**Red Flags:**
- Hardcoded values that future features need configurable
- Tight coupling where future features need flexibility
- Data structures that can't accommodate planned expansion
- API contracts that conflict with future requirements

### 3. Technical Debt Assessment

Does this create debt that conflicts with NS?

**Check:**
- Identify shortcuts or compromises in implementation
- Assess if debt is "good" (strategic) or "bad" (accidental)
- Verify debt doesn't compound against future phases

**Acceptable Debt:**
- Explicitly documented trade-offs
- Isolated to current phase scope
- Clear remediation path exists

**Unacceptable Debt:**
- Foundational compromises affecting all future work
- Undocumented assumptions
- Debt that grows with each phase

### 4. Integration Compatibility

Will this integrate with upcoming phases?

**Check:**
- Review dependencies of future phases
- Verify interfaces are extensible
- Confirm data models support planned features

**Questions:**
- Can future phases build on this without refactoring?
- Are extension points available where needed?
- Is the implementation modular enough for planned integrations?

---

## Output Format

### PASS

```yaml
result: PASS
summary: "Implementation aligns with NS horizon"
checks:
  vision_compatibility: PASS
  future_blocking: PASS
  technical_debt: PASS
  integration: PASS
notes: |
  [Brief confirmation of alignment]
```

Code aligns with horizon. Proceed with ticket completion.

### WARN

```yaml
result: WARN
summary: "Potential future issue identified"
checks:
  vision_compatibility: [PASS|WARN]
  future_blocking: [PASS|WARN]
  technical_debt: [PASS|WARN]
  integration: [PASS|WARN]
warnings:
  - area: "[Which check]"
    issue: "[What might be problematic]"
    affected_phases: [PHASE-XXX, PHASE-YYY]
    mitigation: "[How to address if it becomes a problem]"
action: "Document in SESSION_PATH/horizon-notes.md and proceed"
```

Potential future issue detected. Document the concern and continue. Monitor in future phases.

### FAIL

```yaml
result: FAIL
summary: "Code blocks future NS requirements"
checks:
  vision_compatibility: [PASS|WARN|FAIL]
  future_blocking: [PASS|WARN|FAIL]
  technical_debt: [PASS|WARN|FAIL]
  integration: [PASS|WARN|FAIL]
blocking_issue:
  description: "[What is blocked]"
  affected_ns_goals: ["Goal 1", "Goal 2"]
  affected_phases: [PHASE-XXX]
  severity: "[How badly this blocks future work]"
remediation:
  options:
    - "[Option A: What to change]"
    - "[Option B: Alternative approach]"
  recommended: "[Which option and why]"
action: "PAUSE execution. Escalate to user for decision."
```

Code blocks future. Do not proceed. Escalate immediately.

---

## Escalation Protocol

When result is FAIL:

1. **Stop** - Do not mark ticket complete
2. **Document** - Write blocking issue to SESSION_PATH/blockers/
3. **Notify** - Surface to user with Decision Brief format:

```
| Field | Content |
|-------|---------|
| **Decision** | Lookahead detected future blocker |
| **Issue** | [What's blocked] |
| **Options** | A: [Refactor now] / B: [Accept risk, document] |
| **My Lean** | [Recommendation] because [reason] |
```

4. **Wait** - Do not proceed until user decides

---

## Implementation Notes

- Lookahead runs in **parallel** with Track A validators (physics, simulation, resolution)
- Lookahead checks **future state** while Track A checks **current state**
- Both tracks must pass before ticket completion
- WARN results accumulate - too many WARNs may indicate architectural drift
