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

H-Claude uses a **hierarchical workflow** where the development roadmap breaks into phases, each planned and executed independently.

### The Two Sources of Truth

| Document | Contains | Perspective |
|----------|----------|-------------|
| **NORTHSTAR.md** | WHAT - User story, features, requirements | User/Customer |
| **ROADMAP.yaml** | HOW - Development phases, execution order | Developer/Builder |

These MUST stay aligned. NORTHSTAR is the destination; ROADMAP is the route.

### The Pattern: NORTHSTAR → Roadmap → Phases → Execute

```
┌─────────────────────────────────────────────────────────────┐
│  User approve NORTHSTAR.md                                │
│    └── Vision, goals, features, requirements                │
│    └── This is the USER Vision - what they want built       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  /think-tank --roadmap "Project Name"                       │
│    └── Council analyzes NORTHSTAR                           │
│    └── Creates ROADMAP.yaml with phases                     │
│    └── Each phase has dependencies                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  For each phase (respecting dependencies):                  │
│                                                             │
│    /think-tank "Phase Name" --phase=PHASE-XXX               │
│      └── Phase council creates execution-plan.yaml          │
│      └── Links plan back to ROADMAP.yaml                    │
│                              ↓                              │
│    git-engineer: Create rollback point                      │
│                              ↓                              │
│    /hc-execute                                         │
│      └── Workers implement with QA gates                    │
│      └── SWEEP & VERIFY catches 15% missed work             │
│                              ↓                              │
│    /hc-glass (optional)                                     │
│      └── Code review, security audit                        │
│                              ↓                              │
│    Phase complete → ROADMAP.yaml updated                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Side-Quests (ad-hoc research)                              │
│    └── /think-tank "Research Topic" (no flag)               │
│    └── May inform future phases                             │
└─────────────────────────────────────────────────────────────┘
```

### The Hierarchy

```
NORTHSTAR.md (WHAT - User Story)
     ↓ aligned with
ROADMAP.yaml (HOW - Phases)
├── PHASE-001 → Phase Think-Tank → execution-plan.yaml → Execute
├── PHASE-002 (depends on PHASE-001) → ...
└── PHASE-003 → ...

Side-Quests (recorded in ROADMAP.yaml)
└── Research Topic → may inform future phases
```

### Command Roles

| Command | Purpose | Output |
|---------|---------|--------|
| `/think-tank --roadmap` | Define project phases | `ROADMAP.yaml` |
| `/think-tank --phase=X` | Plan specific phase | `execution-plan.yaml` |
| `/think-tank "Topic"` | Side-quest research | `STATE.yaml` |
| `/hc-execute` | Execute approved plans | Implemented code |
| `/hc-glass` | Scan for issues | Issue report |
| `/red-team` | Deep quality review | Root cause analysis |

---

## Success Metrics

1. **Metric 1** - How we measure success
2. **Metric 2** - How we measure success
3. **Metric 3** - How we measure success

---

*Last updated: YYYY-MM-DD*
