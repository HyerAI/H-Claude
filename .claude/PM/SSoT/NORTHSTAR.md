# Project NORTHSTAR

**The guiding document for all agents working on this project.**

---

## Purpose

H-Claude is a **methodology framework** for Claude Code projects. It provides:

1. **Orchestration patterns** for multi-agent workflows
2. **Command infrastructure** for structured development cycles
3. **State management** for crash recovery and session continuity
4. **Quality assurance** through adversarial audit commands

The framework exists because raw Claude Code sessions lack:
- Persistent state across sessions
- Coordinated multi-agent workflows
- Structured planning-to-execution pipelines
- Systematic quality verification

H-Claude solves this by providing a "Factory" layer that orchestrates work while keeping the "Product" clean and deployable.

---

## Vision

H-Claude will become the **standard methodology** for enterprise Claude Code projects, providing:

1. **Predictable workflows** - From idea to implementation with checkpoints
2. **Crash-resilient execution** - Resume from any failure point
3. **Quality guarantees** - Multi-layer verification before deployment
4. **Context protection** - Sub-agent delegation preserves main session context

The framework should feel like having a well-organized development team: plan, execute, verify, repeat.

---

## Goals

1. **Reliable Phase Cycles** - Execute multi-phase development with automatic checkpoints, recovery, and quality gates
2. **Adversarial Quality** - Trust but Verify philosophy: assume 20% of work has gaps, actively hunt for them
3. **Clean Separation** - Factory (orchestration) never pollutes Product (shipped code)
4. **Self-Documenting** - ADRs, changelogs, and state files capture all decisions
5. **Zero-Config Start** - New projects get working infrastructure with `hc-init`

---

## Constraints

1. **KISS** - Keep it simple. Avoid unnecessary complexity.
2. **YAGNI** - Build only what is required now.
3. **Single Source of Truth** - One place for each piece of information.
4. **Context is precious** - Delegate to sub-agents to preserve main context window.
5. **Decisions are sacred** - Document in ADRs; changes require explicit pivot.
6. **No magic** - All behavior is explicit in commands and templates.
7. **Proxies required** - Multi-agent features depend on proxy infrastructure.

---

## Non-Goals

- **Not an IDE** - H-Claude enhances Claude Code, doesn't replace it
- **Not a code generator** - Focus is orchestration, not implementation
- **Not cloud-native** - Runs locally with Claude Code CLI
- **Not a testing framework** - Provides QA patterns, not test runners
- **Defer: GUI/dashboard** - CLI-first for now

---

## Quality Standards

| Aspect | Standard |
|--------|----------|
| Documentation | Clear, concise, actionable |
| Commands | Self-documenting, predictable |
| Context files | Valid YAML, regularly updated |
| Decisions | Documented as ADRs |
| Changes | Logged in CHANGELOG.md |
| Shell scripts | Timeout-wrapped, error-handled |
| Templates | Version-tagged, tested |

---

## Validation Checklist

When reviewing work, validate against:

- [ ] Does it follow KISS/YAGNI principles?
- [ ] Is context.yaml updated?
- [ ] Are decisions documented as ADRs?
- [ ] Is CHANGELOG.md updated?
- [ ] Does it break existing workflow?
- [ ] Are new functions in agent-spawn.sh tested?
- [ ] Do timeout wrappers prevent zombies?

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
│  User approve NORTHSTAR.md                                  │
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
│    /hc-execute                                              │
│      └── Workers implement with QA gates                    │
│      └── SWEEP & VERIFY catches 20% missed work             │
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
| `orchestrator/` | Execute approved plans (Python TDD) | Implemented code |
| `/hc-glass` | Scan for issues | Issue report |
| `/red-team` | Deep quality review | Root cause analysis |

---

## Success Metrics

1. **Recovery Rate** - 95%+ of crashed cycles recoverable from checkpoint
2. **Quality Gate Pass** - 80%+ phases pass GLASS audit first time
3. **Context Protection** - Main session context usage <50% after delegation
4. **Documentation Coverage** - 100% of decisions have ADRs
5. **Template Accuracy** - <10% false positives in audit findings

---

*Last updated: 2026-01-10*
