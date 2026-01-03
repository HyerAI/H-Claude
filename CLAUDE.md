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

## Quick Reference

### Folder Structure

```
.claude/
├── context.yaml          # Session state (read at start, update regularly)
├── agents/               # git-engineer.md, session-triage.md
├── commands/             # think-tank, hc-plan-execute, hc-glass, red-team
├── skills/               # Reusable capabilities
├── templates/            # Prompt templates
└── PM/
    ├── SSoT/             # NORTHSTAR.md, ROADMAP.yaml, ADRs/
    ├── think-tank/       # Session artifacts
    ├── hc-plan-execute/  # Execution artifacts
    ├── hc-glass/         # Review reports
    ├── GIT/              # Protocols
    ├── BACKLOG.yaml      # Deferred work
    └── CHANGELOG.md      # Change history
```

### Commands

| Command | Purpose | Output |
|---------|---------|--------|
| `/think-tank --roadmap` | Create project phases | `ROADMAP.yaml` |
| `/think-tank --phase=X` | Plan specific phase | `execution-plan.yaml` |
| `/think-tank "Topic"` | Ad-hoc research | Findings |
| `/hc-plan-execute` | Execute approved plan | Implementation |
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
/hc-plan-execute       →  Workers implement with QA gates
        ↓
Phase complete         →  ROADMAP updated → next phase unlocked
```

---

## Session Protocol

### Start (T+0)

1. **Read** `.claude/context.yaml` and `ROADMAP.yaml`
2. **Spawn** session-triage agent in background
3. **Greet** user based on context (don't wait for triage)
4. **Merge** triage output when user responds

```
Greet: "Last session we [recent_action]. Current focus: [objective]. What's next?"
```

### During Session

- Update `context.yaml` after significant work
- Log actions in `recent_actions` (keep last 10)
- Document decisions as ADRs
- Unsorted tasks → `context.yaml` backlog
- Tech debt → relevant phase in `ROADMAP.yaml`

### End / Commit

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
