# H-Claude Project Template

AI agent orchestration template for Claude Code projects.

---

## Quick Start

1. **Session Start**: Claude reads `.claude/context.yaml` to understand current state
2. **Work**: Use commands (`/think-tank`, `/hc-plan`, etc.) to investigate and execute
3. **Commit**: When ready, ask Claude to commit - Claude spawns git-engineer agent
4. **Session End**: Run `/update-context`, then commit

---

## Folder Structure

```
<project_root>/
├── .claude/                    # INTERNAL (do not ship)
│   ├── context.yaml            # Session state (load at start, update regularly)
│   ├── settings.json           # Claude Code settings
│   ├── agents/                 # Agent definitions
│   │   └── git-engineer.md     # Git agent (launches at session start)
│   ├── commands/               # Multi-agent orchestration
│   │   ├── think-tank.md       # Council for deep investigation
│   │   ├── hc-plan.md          # Detailed planning
│   │   ├── hc-plan-execute.md  # Execute plans
│   │   ├── hc-glass.md         # Code/system review
│   │   └── red-team.md         # Deep issue investigation
│   ├── skills/                 # Reusable capabilities
│   ├── templates/              # Prompt templates for commands
│   └── PM/                     # Project Management
│       ├── SSoT/               # Single Source of Truth
│       │   ├── NORTHSTAR.md    # Guiding doc (MUST exist)
│       │   └── ADRs/           # Architectural Decision Records
│       ├── think-tank/         # Think-tank session artifacts
│       ├── plans/              # /hc-plan output artifacts
│       ├── hc-plan-execute/    # /hc-plan-execute artifacts
│       ├── hc-glass/           # /hc-glass report artifacts
│       ├── brainstorm/         # Active brainstorms
│       ├── TEMP/               # Drafts, temporary work
│       ├── GIT/                # Git protocols
│       ├── BACKLOG.yaml        # Deferred work tracking
│       └── CHANGELOG.md        # Change history
│
├── infrastructure/             # LLM Proxy servers (runtime)
│   ├── CC-Claude/              # Claude pass-through (port 2408)
│   ├── CG-Flash/               # Gemini Flash gateway (port 2405)
│   ├── CG-Pro/                 # Gemini Pro gateway (port 2406)
│   └── CG-Image/               # Gemini Image gateway (port 2407)
│
├── src/                        # PRODUCTION CODE (project-specific)
├── CLAUDE.md                   # This file
└── CHANGELOG.md                # Root changelog (optional)
```

| Folder | Ships? | Purpose |
|--------|--------|---------|
| `.claude/` | No | Internal config, agents, PM |
| `infrastructure/` | No | LLM proxy servers |
| `src/` | **Yes** | Production code |

---

## Commands Workflow

```
/think-tank ──→ /hc-plan ──→ /hc-plan-execute
      │              │
      ↓              ↓
 /red-team      /hc-glass
(deep dive)   (code review)
```

### `/think-tank`
Council for deep investigation. Start here when exploring a new subject.
- Creates session state in `.claude/PM/think-tank/`
- Multiple experts discuss and analyze
- Output: Recommendations, decision options

### `/hc-plan`
Detailed planning for implementation. Can consume think-tank output.
- Creates step-by-step implementation plan in `.claude/PM/plans/`
- Identifies risks and dependencies
- Output: Actionable plan ready for execution

### `/hc-plan-execute`
Execute plans with team coordination.
- Takes plan from `/hc-plan` or user-provided plan
- Stores execution artifacts in `.claude/PM/hc-plan-execute/`
- Coordinates workers to implement
- Requires USER approval before applying changes

### `/hc-glass`
Standalone code/system review (G.L.A.S.S. - Global Logic & Architecture System Scan).
- Stores reports in `.claude/PM/hc-glass/`
- Find bugs, conflicts, incomplete work
- Architecture analysis
- Security review
- Output: Issues list with severity

### `/red-team`
Deep investigation of specific issues or bugs.
- Root cause analysis
- Multiple perspectives on the problem
- Output: Findings → can feed into `/hc-plan-execute` for fixes

---

## Critical Files

### `.claude/context.yaml`
**Session persistent context.** Claude reads this at session start.

```yaml
meta:
  last_modified: '2026-01-02T13:30:00Z'
  project_phase: 'Foundation'

project:
  name: 'My Project'
  description: 'What this project does'

focus:
  current_objective: 'What we are working on'
  active_decisions: []

recent_actions:
  - '[DATE] What was done'

tasks:
  active: []
  backlog: []

think_tank: []

git:
  status: ready  # ready | working | blocked
  note: ''
```

**Rules:**
- Read at session start
- Update after significant work
- Commit with every git commit

### `.claude/PM/BACKLOG.yaml`
**Deferred work tracking.** Items we want to do later.

```yaml
items:
  - id: BACK-001
    title: 'Task title'
    context: 'Why deferred, what needs to happen'
    priority: medium
    added: '2026-01-02'
```

**Rules:**
- Add when deferring work
- Remove when done or moved to active
- Include enough context for future-you

### `.claude/PM/CHANGELOG.md`
**Change history.** Updated with every commit.

Format: [Keep a Changelog](https://keepachangelog.com/)
- **Added**: New features
- **Changed**: Updates to existing
- **Fixed**: Bug fixes
- **Removed**: Deleted features

---

## Git Agent

The `git-engineer` agent is spawned on-demand when commits are needed.

**How to commit:**
1. Ask Claude: "commit these changes" or "commit with message X"
2. Claude spawns `git-engineer` agent to handle the commit
3. Git-engineer follows project protocols in `.claude/PM/GIT/PROTOCOLS.md`

**What git-engineer does:**
- Analyzes staged changes
- Crafts proper Conventional Commit message
- Always includes `context.yaml` in commits (crash-proof state)
- Maintains git protocols and improvement plans

**Agent location:** `.claude/agents/git-engineer.md`
**Protocols:** `.claude/PM/GIT/PROTOCOLS.md`

---

## NORTHSTAR & ADRs

### NORTHSTAR.md
**Guiding document for all agents.** Lives in `.claude/PM/SSoT/NORTHSTAR.md`.

- Defines project goals and constraints
- All solutions validated against it
- **MUST exist** - if missing, Claude asks user to create one

### ADRs (Architectural Decision Records)
**Documented decisions.** Live in `.claude/PM/SSoT/ADRs/`.

Created automatically when decisions are made:
```yaml
id: ADR-001
title: 'Decision title'
status: accepted  # proposed | accepted | deprecated | superseded
date: '2026-01-02'
context: 'Why this decision was needed'
decision: 'What we decided'
consequences: 'What this means going forward'
```

---

## Proxy Usage

Use these proxies to spawn sub-agents:

```bash
# Flash (fast workers)
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "task"

# Pro (reasoning, QA)
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "task"

# Claude (pass-through)
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "task"
```

See `GET_STARTED.md` for proxy setup instructions.

---

## Session Protocol

### Start
1. Read `.claude/context.yaml`
2. Check for zombie agents, clean up if needed
3. Launch git-engineer agent
4. Check NORTHSTAR.md exists (create if not)
5. Resume from `focus.current_objective`

### During Work
1. Update `context.yaml` regularly
2. Log significant actions in `recent_actions`
3. Document decisions as ADRs
4. Defer non-critical work to BACKLOG.yaml

### End / Commit
1. Update `context.yaml` with current state
2. Update CHANGELOG.md
3. Set `git.status: ready` with note
4. Commit includes context.yaml

---

## Skills

### `/update-context`
**Update session state.** Run after completing tasks or before commits.

Location: `.claude/skills/update-context.md`

**When to use:**
- After completing a task
- After making a significant decision
- Before any git commit
- When switching focus

**What it does:**
- Updates `meta.last_modified`
- Adds to `recent_actions` (keeps last 5)
- Updates `tasks.active` and `focus`

---

## Principles

- **NORTHSTAR guides all work** - validate solutions against it
- **Decisions are documented** - ADRs for architectural choices
- **Context is precious** - delegate to sub-agents to preserve window
- **CHANGELOG is the work log** - update with every commit
- **BACKLOG prevents forgetting** - defer, don't lose track
- **Use /update-context** - keep session state current
