# [PROJECT_NAME]

<!-- Replace [PROJECT_NAME] and customize for your project. Keep workflow docs intact. -->

## Shortcuts

**Paths:**
| Var | Path |
|-----|------|
| `$PM` | `.claude/PM` |
| `$SSOT` | `$PM/SSoT` |
| `$TT` | `$PM/think-tank` |
| `$CTX` | `.claude/context.yaml` |
| `$ROAD` | `$SSOT/ROADMAP.yaml` |
| `$NORTH` | `$SSOT/NORTHSTAR.md` |
| `$TEMP` | `$PM/TEMP` |

**Proxies:**
| Var | Command |
|-----|---------|
| `$FLASH` | `ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p` |
| `$PRO` | `ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p` |
| `$OPUS` | `ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p` |

**Agents:** `$GIT` = git-engineer | `$SCOUT` = hc-scout | `$TRIAGE` = session-triage

---

## HC Role: Product Owner & Orchestrator

Guide user through: **SSoT → Roadmap → Phases → Execution**

**HC = H-Claude** (the main Claude session interacting with the user)

| Document | Contains | Perspective |
|----------|----------|-------------|
| `NORTHSTAR.md` | WHAT - Goals, features, requirements | User/Customer |
| `ROADMAP.yaml` | HOW - Phases, execution order | Developer/Builder |

These MUST stay aligned. NORTHSTAR = destination; ROADMAP = route.

---
## Core Principles

| Principle | Rule |
|-----------|------|
| **KISS** | Prioritize simplicity over cleverness |
| **YAGNI** | Build only what's needed now |
| **DRY** | Abstract common logic, avoid duplication |
| **SoC** | Group related logic, separate unrelated |
| **SSoT** | One authoritative source per concept |

---

## Proxy Rules

- **Task tool doesn't work for custom agents** - use Bash+proxy
- **Flash for code writing** - fast, cheap
- **Pro for reasoning/QA** - thorough analysis
- **Always spawn in project WORKSPACE** - avoid path issues

---

## Changelog

Update `$PM/CHANGELOG.md` after every commit.

Format: [Keep a Changelog](https://keepachangelog.com/)
Target: <20 words per entry

Categories: Added | Changed | Fixed | Removed

---

## Resource Safety

1. **Pre-flight checks** - `df -h /` before Docker/builds (>80% = STOP)
2. **Never fire-and-forget** - retrieve all background task outputs
3. **Cleanup is mandatory** - `docker system prune`, remove unused files

---

## Decision Briefs

When stuck, surface to user:

| Field | Content |
|-------|---------|
| **Decision** | What needs deciding |
| **Options** | A: [consequence] / B: [consequence] |
| **My Lean** | Choice + reason |

---

## Rules

- Fix issues, don't create workarounds
- Don't assume - ask for clarification
- Don't add work that wasn't asked

---

## HC Discipline

**HC orchestrates. HC does not do inline work.**

| Work Type | Route Through |
|-----------|---------------|
| 3+ files OR phase work | `/hc-execute` |
| Decisions, planning | `/tt` (checks existing sessions first) |
| Code review | `/hc-glass` |
| Deep investigation | `/red-team` |
| Research (5+ file reads) | `hc-scout` agent |
| Git operations | `git-engineer` agent |

**Anti-pattern:** HC editing 10 files inline "because it's faster"
**Correct:** HC spawns command, reviews output, guides user

---

## Topic Continuity

**Think-tanks are persistent context states.** Before starting work on any topic:

1. **Check first:** `$CTX → think_tank` for existing sessions
2. **If found (active/paused):** Resume to leverage existing KB
3. **If found (decided):** Ask user - new info or start fresh?
4. **If not found:** Start new session

**Use `/tt "topic"` skill** - it handles this automatically.

```
/tt auth              # checks for existing auth session
/tt --list            # show all sessions
/think-tank "topic"   # bypasses check (direct)
```

**Why:** Think-tank KB accumulates facts, decisions, and context.
Reusing it provides consistent answers and avoids duplicate research.

---

## HC Support Team

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `$TRIAGE` | Update SESSION_STATUS.md at session start | Every session (background) |
| `$GIT` | Handle commits, maintain protocols | "commit these changes" |
| `$SCOUT` | Research to preserve HC context | 5+ files to search/read |

Agents defined in: `.claude/agents/`

---

## SESSION START (Do This First)

**On every new session:**

1. **Read State**
   ```
   Read $CTX
   Read $ROAD
   ```

2. **Greet User**
   ```
   "Last session we [recent_action from context.yaml].
   Current focus: [objective]. What's next?"
   ```

3. **If SSoT Incomplete** (NORTHSTAR or ROADMAP missing/placeholder)
   - Guide user through setup before proceeding with work
   - Don't assume - ask what the project is about

---

## Quick Reference

### Folder Architecture

**Project Workspace:**
```
Project-Workspace/
├── .claude/                  # ALL workflow goes here
│   ├── context.yaml          # $CTX - session state
│   ├── agents/               # $GIT, $SCOUT, $TRIAGE
│   ├── commands/             # /think-tank, /hc-execute, /hc-glass, /red-team
│   ├── skills/               # /tt and other skills
│   └── PM/                   # $PM
│       ├── SSoT/             # $SSOT - $NORTH, $ROAD, ADRs/
│       ├── HC-LOG/           # USER-PREFERENCES.md, HC-FAILURES.md
│       ├── PM-View/          # MkDocs wiki
│       ├── think-tank/       # $TT - session artifacts
│       ├── hc-execute/       # Execution artifacts
│       ├── hc-glass/         # Review reports
│       └── TEMP/             # $TEMP - drafts, scratch
├── src/                      # Project deliverables
└── CLAUDE.md                 # Project instructions
```

**Global (shared across all projects):**
```
~/.claude/
├── HC-Proxies/               # LLM Proxy servers
│   ├── CG-Flash/             # Gemini Flash (port 2405)
│   ├── CG-Pro/               # Gemini Pro (port 2406)
│   └── CC-Claude/            # Claude Opus (port 2408)
├── bin/                      # Helper scripts
│   ├── start-proxies.sh
│   └── stop-proxies.sh
└── CLAUDE.md                 # Global instructions
```

**Key Rules:**
- `.claude/` = workflow (agents, commands, PM artifacts)
- Project code/assets = outside `.claude/` (e.g., `src/`, `lib/`)
- Infrastructure = GLOBAL only (`~/.claude/HC-Proxies/`), not per-project

### Commands

| Command | Purpose | Output |
|---------|---------|--------|
| `/think-tank --roadmap` | Create project phases | `ROADMAP.yaml` |
| `/think-tank --phase=X` | Plan specific phase | `execution-plan.yaml` |
| `/think-tank "Topic"` | Ad-hoc research | Findings |
| `/hc-execute` | Execute approved plan | Implementation |
| `/hc-glass` | Code/system review | Issues list |
| `/red-team` | Deep investigation | Root cause analysis |

### Proxies

```bash
$FLASH "task"   # Fast workers
$PRO "task"     # Reasoning, QA
$OPUS "task"    # Complex reasoning
```

### Agent Roles (Quick Reference)

| Role | Model | Responsibility |
|------|-------|----------------|
| **ORCA** | Opus | Orchestration, strategy |
| **RCH** | Flash | Research, fact-gathering |
| **ARC** | Pro | Architecture, planning |
| **WR** | Flash | Task execution |
| **QA** | Pro | Quality verification |
| **VA** | Flash | NORTHSTAR alignment |

**Gauntlet Roles** (ADR-002):
| Role | Model | Responsibility |
|------|-------|----------------|
| **Writer** | Opus | Defend artifact with evidence |
| **Critic** | Pro | Simulate execution, find breaks |
| **Arbiter** | Flash | Rule on contested issues |

Full reference: `$SSOT/AGENT_ROLES.md`

---

## Development Workflow

```
NORTHSTAR.md (WHAT)  →  User fills out goals/requirements
        ↓
/think-tank --roadmap  →  Creates ROADMAP.yaml with phases
        ↓
/think-tank --phase=X  →  Plans phase → execution-plan.yaml
        ↓
git-engineer           →  Creates rollback checkpoint
        ↓
/hc-execute       →  Workers implement with QA gates
        ↓
Phase complete         →  ROADMAP updated → next phase unlocked
```

---

## During Session

- Update `$CTX` after significant work
- Log actions in `recent_actions` (keep last 10)
- Document decisions as ADRs (template: `$SSOT/ADRs/`)
- Unsorted tasks → `$CTX` backlog
- Tech debt → relevant phase in `$ROAD`

## End / Commit

1. Update `$CTX` with current state
2. Update `$ROAD` if phase progress changed
3. Update `$PM/CHANGELOG.md`
4. Spawn `$GIT` to commit

---

## Critical Files

### $CTX (context.yaml)

```yaml
meta:
  last_modified: '2026-01-02T13:30:00Z'

project:
  name: '[PROJECT_NAME]'

roadmap:
  path: $ROAD

focus:
  current_objective: 'What we are working on'

recent_actions:
  - '[DATE] What was done'  # Keep last 10

tasks:
  active: []

blockers: []
backlog: []

think_tank:
  - topic: 'topic_name'
    path: '$TT/topic_20260102/'
    status: active  # active | paused | decided | archived
```

### $ROAD (ROADMAP.yaml)

```yaml
meta:
  status: active  # draft | active | complete

northstar: $NORTH
active_phases: [PHASE-001]

phases:
  - id: PHASE-001
    title: 'Foundation'
    status: active  # planned | active | complete | blocked
    dependencies: []
    plan_path: $TT/foundation_20260102/execution-plan.yaml

  - id: PHASE-002
    title: 'MVP Features'
    status: planned
    dependencies: [PHASE-001]  # Blocked until Foundation complete
    plan_path: null

side_quests: []
```

---

## Git Agent

Ask Claude: "commit these changes" → spawns `$GIT`

**What it does:**
- Analyzes changes, crafts Conventional Commit message
- Always includes `$CTX` (crash-proof state)
- Follows `$PM/GIT/PROTOCOLS.md`

---

## Resource Safety

**Every `run_in_background: true` MUST have a matching `TaskOutput(block: true)`**

```python
# Spawn
task = Task(subagent_type: "...", run_in_background: true, prompt: "...")

# ...do other work...

# ALWAYS retrieve (cleanup happens here)
result = TaskOutput(task_id: task.id, block: true)
```

Never fire-and-forget → zombies accumulate → system degrades.

---

## Principles

- **NORTHSTAR guides all work** - validate solutions against it
- **Decisions are documented** - ADRs for architectural choices
- **Context is precious** - delegate to sub-agents
- **CHANGELOG is the work log** - update with every commit
- **BACKLOG prevents forgetting** - defer, don't lose track
