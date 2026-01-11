# HD Integration into H-Claude ROOT

**Status:** COMPLETE (2026-01-10)
**Version:** 1.0.0

---

## Overview

HD (Human-Driven) capabilities have been integrated into H-Claude ROOT. This adds:

1. **HD Skills** - 7 interview skills for requirements extraction
2. **Python Orchestrator** - TDD execution engine
3. **Document Templates** - UserStory, ADR, Spec templates
4. **Enhanced Commands** - Updated commands with HD awareness

---

## What HD Adds

### HD Skills (Interview Flow)

| Skill | Purpose |
|-------|---------|
| `/genesis` | Project bootstrap - detects greenfield/brownfield |
| `/diamond-diverge` | Explore problem space (The Why, What, Edges) |
| `/diamond-converge` | Prioritize via MoSCoW grouping |
| `/diamond-synthesize` | Lock decisions, confirm entities |
| `/draft-userstory` | Create UserStory from requirements |
| `/draft-adr` | Create ADR from decisions |
| `/tt` | Think-tank shortcut |

### Python Orchestrator

Located at `ROOT/orchestrator/`:
- `main.py` - Entry point
- `cli.py` - Command-line interface
- `execution.py` - TDD execution loop
- `dispatcher.py` - Model dispatch (Opus/Pro/Flash)
- `worktree.py` - Git worktree isolation
- `hd/*.py` - HD-specific modules

### Document Templates

Located at `ROOT/templates/documents/`:
- `UserStory.md.template` - User story format
- `ADR.md.template` - Decision record format
- `Spec.md.template` - Specification format

---

## ROOT Structure After Integration

```
~/.claude/H-Claude/                 # H-Claude ROOT
├── commands/                       # 7 slash commands
│   ├── think-tank.md
│   ├── hc-glass.md
│   ├── red-team.md
│   ├── hc-sys.md
│   ├── hc-init.md
│   ├── hc-update.md               # NEW - adds HD to existing projects
│   └── ask.md
│
├── skills/                         # 7 HD interview skills
│   ├── genesis.md
│   ├── diamond-diverge.md
│   ├── diamond-converge.md
│   ├── diamond-synthesize.md
│   ├── draft-userstory.md
│   ├── draft-adr.md
│   └── tt.md
│
├── agents/                         # Agent definitions
│   ├── git-engineer.md
│   └── hc-scout.md
│
├── orchestrator/                   # Python TDD engine
│   ├── *.py                        # 22 modules
│   └── hd/
│       └── *.py                    # 8 HD modules
│
├── templates/
│   ├── template-prompts/           # Agent prompt templates
│   │   ├── think-tank/             # 29 prompts
│   │   ├── hc-glass/               # 11 prompts
│   │   ├── hc-execute/             # 6 prompts
│   │   └── red-team/               # 6 prompts
│   ├── schemas/                    # Output schemas
│   │   └── *.md                    # 8 schemas
│   └── documents/                  # Document templates
│       ├── UserStory.md.template
│       ├── ADR.md.template
│       └── Spec.md.template
│
├── lib/                            # Utilities
│   ├── agent-spawn.sh
│   └── circuit_breaker.py
│
├── docs/                           # Documentation
│   ├── GET_STARTED.md
│   ├── WORKFLOW_GUIDE.md
│   ├── PROXIES.md
│   └── HD_INTEGRATION.md           # This document
│
├── scripts/                        # Setup scripts
│   ├── setup.sh
│   ├── start-proxies.sh
│   └── stop-proxies.sh
│
├── examples/                       # Example files
│   ├── NORTHSTAR-example.md
│   ├── ROADMAP-example.yaml
│   └── ...
│
├── .claude/                        # Factory workspace (development)
│   ├── PM/                         # Project management
│   ├── context.yaml                # Session state
│   └── ...
│
└── VERSION                         # 1.0.0
```

---

## How HD + H-Claude Work Together

```
User starts project
    │
    ├─► /hc-init ──► Creates .claude/ from ROOT (includes skills/)
    │
    ├─► HD Interview ──► User describes what they want
    │   /genesis → /diamond-diverge → /diamond-converge
    │   → /diamond-synthesize → /draft-userstory
    │
    ├─► Artifacts created ──► UserStories, ADRs linked in NORTHSTAR
    │
    ├─► /think-tank --roadmap ──► Plan development phases
    │
    ├─► /hc-execute ──► Workers implement with QA gates
    │
    └─► Python orchestrator (optional) ──► TDD automation
        python ~/.claude/H-Claude/orchestrator/main.py
```

---

## Commands Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/hc-init` | Initialize new project | Start of project |
| `/hc-update` | Add HD to existing project | Upgrading projects |
| `/genesis` | Start HD interview | Beginning requirements |
| `/think-tank` | Research and planning | Design decisions |
| `/hc-execute` | Execute approved plans | Implementation |
| `/hc-glass` | Code audit | Quality check |
| `/red-team` | Deep investigation | Root cause analysis |

---

## For Existing Projects

Use `/hc-update` to add HD capabilities to projects already using H-Claude:

```bash
# In existing project with .claude/ folder
/hc-update

# This copies:
# - skills/ → .claude/skills/
# - templates/documents/ → .claude/templates/
# - Optional: orchestrator/ → .hc/
```

---

## Verification

```bash
# Verify ROOT structure
ls ~/.claude/H-Claude/skills/          # 7 files
ls ~/.claude/H-Claude/commands/        # 7 files
ls ~/.claude/H-Claude/orchestrator/    # 30 files
ls ~/.claude/H-Claude/templates/       # 3 subdirs
cat ~/.claude/H-Claude/VERSION         # 1.0.0
```

---

## Integration History

| Date | Action |
|------|--------|
| 2026-01-10 | Initial HD integration into ROOT |
| 2026-01-10 | Created /hc-update command |
| 2026-01-10 | Removed source .claude/orchestrator/ |
| 2026-01-10 | VERSION set to 1.0.0 |

---

*Last updated: 2026-01-10*
