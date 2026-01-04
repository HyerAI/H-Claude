# [PROJECT_NAME]

<!-- Replace [PROJECT_NAME] and customize for your project. Keep workflow docs intact. -->

## Claude's Role: Product Owner

Guide user through: **SSoT → Roadmap → Phases → Execution**

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

Update `.claude/PM/CHANGELOG.md` after every commit.

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

## SESSION START (Do This First)

**On EVERY new session, IMMEDIATELY:**

### Step 1: Cleanup Orphans
```bash
# Kill any orphan triage from crashed sessions
pkill -f "Session-Triage agent" 2>/dev/null || true
```

### Step 2: Read State
```
Read .claude/context.yaml
Read .claude/PM/SSoT/ROADMAP.yaml
```

### Step 3: Spawn Triage (Background with Timeout)

Use **Bash tool with proxy** (NOT Task tool - custom subagent_types don't work):

```bash
# Run in background with 60s timeout
timeout --foreground --signal=TERM --kill-after=10 60 \
  bash -c 'ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "
You are the Session-Triage agent. Generate a SESSION BRIEF.

WORKSPACE: $(pwd)

Read these files:
1. .claude/context.yaml - extract focus, recent_actions, blockers, backlog
2. .claude/PM/SSoT/ROADMAP.yaml - extract phases, dependencies, active_phases
3. Glob .claude/PM/think-tank/*/STATE.yaml - check workspace statuses

Output a SESSION BRIEF with: Last Session, Roadmap Status, Phase Progress, Drift Alerts, Recommended Action.

Be fast (<8 seconds). Read-only. Missing data shows N/A.
"'
```

Use Bash tool's `run_in_background: true` parameter.

### Step 4: Greet User (Don't Wait)
```
"Last session we [recent_action from context.yaml]. Current focus: [objective]. What's next?"
```

### Step 5: Retrieve Triage Output (MANDATORY)
When user responds, retrieve triage output with `TaskOutput(block: true, timeout: 30000)` and combine with user intent. **Never skip this step - it ensures cleanup.**

---

## Quick Reference

### Folder Structure

```
.claude/
├── context.yaml          # Session state (read at start, update regularly)
├── agents/               # git-engineer.md, session-triage.md
├── commands/             # think-tank, hc-execute, hc-glass, red-team
├── skills/               # Reusable capabilities
├── templates/            # Prompt templates
└── PM/
    ├── SSoT/             # NORTHSTAR.md, ROADMAP.yaml, ADRs/
    ├── think-tank/       # Session artifacts
    ├── hc-execute/  # Execution artifacts
    ├── hc-glass/         # Review reports
    ├── GIT/              # Protocols
    ├── BACKLOG.yaml      # Deferred work
    └── CHANGELOG.md      # Change history

infrastructure/               # LLM Proxy servers (global: ~/.claude/infrastructure/)
├── CG-Flash/                 # Gemini Flash (port 2405)
├── CG-Pro/                   # Gemini Pro (port 2406)
└── CC-Claude/                # Claude pass-through (port 2408)
```

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
# Flash (fast workers)
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "task"

# Pro (reasoning, QA)
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "task"

# Claude (complex reasoning)
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "task"
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

Full reference: `.claude/PM/SSoT/AGENT_ROLES.md`

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

- Update `context.yaml` after significant work
- Log actions in `recent_actions` (keep last 10)
- Document decisions as ADRs (template: `PM/SSoT/ADRs/`)
- Unsorted tasks → `context.yaml` backlog
- Tech debt → relevant phase in `ROADMAP.yaml`

## End / Commit

1. Update `context.yaml` with current state
2. Update `ROADMAP.yaml` if phase progress changed
3. Update `CHANGELOG.md`
4. Spawn `git-engineer` to commit

---

## Critical Files

### context.yaml

```yaml
meta:
  last_modified: '2026-01-02T13:30:00Z'

project:
  name: '[PROJECT_NAME]'

roadmap:
  path: .claude/PM/SSoT/ROADMAP.yaml

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
    path: '.claude/PM/think-tank/topic_20260102/'
    status: active  # active | paused | decided | archived
```

### ROADMAP.yaml

```yaml
meta:
  status: active  # draft | active | complete

northstar: .claude/PM/SSoT/NORTHSTAR.md
active_phases: [PHASE-001]

phases:
  - id: PHASE-001
    title: 'Foundation'
    status: active  # planned | active | complete | blocked
    dependencies: []
    plan_path: .claude/PM/think-tank/foundation_20260102/execution-plan.yaml

  - id: PHASE-002
    title: 'MVP Features'
    status: planned
    dependencies: [PHASE-001]  # Blocked until Foundation complete
    plan_path: null

side_quests: []
```

---

## Git Agent

Ask Claude: "commit these changes" → spawns `git-engineer` agent

**What it does:**
- Analyzes changes, crafts Conventional Commit message
- Always includes `context.yaml` (crash-proof state)
- Follows `.claude/PM/GIT/PROTOCOLS.md`

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
