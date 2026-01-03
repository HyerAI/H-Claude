# Project NORTHSTAR

**The guiding document for all agents working on this project.**

---

## Purpose

<!-- What does this project do and why does it exist? -->

---

## Vision

<!-- What will this project become? What value will it provide? -->

---

## Goals

1. **Goal 1** - Description
2. **Goal 2** - Description
3. **Goal 3** - Description

---

## Constraints

1. **KISS** - Keep it simple. Avoid unnecessary complexity.
2. **YAGNI** - Build only what is required now.
3. **Single Source of Truth** - One place for each piece of information.
4. **Context is precious** - Delegate to sub-agents to preserve main context window.
5. **Decisions are sacred** - Document in ADRs; changes require explicit pivot.

---

## Non-Goals

- What we explicitly will NOT do
- Features we are deferring
- Out of scope items

---

## Quality Standards

| Aspect | Standard |
|--------|----------|
| Documentation | Clear, concise, actionable |
| Commands | Self-documenting, predictable |
| Context files | Valid YAML, regularly updated |
| Decisions | Documented as ADRs |
| Changes | Logged in CHANGELOG.md |

---

## Validation Checklist

When reviewing work, validate against:

- [ ] Does it follow KISS/YAGNI principles?
- [ ] Is context.yaml updated?
- [ ] Are decisions documented as ADRs?
- [ ] Is CHANGELOG.md updated?
- [ ] Does it break existing workflow?

---

## Core Workflow

```
/think-tank      → Research, decisions, AND planning
       ↓              (outputs execution-plan.yaml)
/hc-plan-execute → Execute plan with worker agents
       ↓
/hc-glass        → Code review, find issues
       ↓
/red-team        → Deep dive on specific bugs/issues
```

### Command Roles

| Command | Purpose |
|---------|---------|
| `/think-tank` | The Brain - research, decide, plan |
| `/hc-plan-execute` | The Hands - execute approved plans |
| `/hc-glass` | The Eyes - scan for issues |
| `/red-team` | The Auditor - deep quality review |

---

## Success Metrics

1. **Metric 1** - How we measure success
2. **Metric 2** - How we measure success
3. **Metric 3** - How we measure success

---

*Last updated: YYYY-MM-DD*
