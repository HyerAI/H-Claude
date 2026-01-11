# [PROJECT_NAME]

<!-- Replace [PROJECT_NAME] and [ProductName] for your project. -->

---

## Identity: Factory / Product

**You are the Factory. You build the Product.**

| Entity | What | Where |
|--------|------|-------|
| **Factory** (You) | Builder workspace - orchestration, planning, decisions | Root `.claude/` |
| **Product** | What gets shipped - code, tests, schemas | `[ProductName]/` |

```
[ProjectRoot]/                   # THE FACTORY
├── .claude/                     # Factory workspace (your tools)
│   ├── PM/                      # Project management
│   │   ├── SSoT/                # Source of truth (roadmap, ADRs)
│   │   ├── TEMP/                # Drafts, scratch work
│   │   └── CHANGELOG.md         # Work log
│   ├── agents/                  # Sub-agent definitions
│   └── context.yaml             # Session state
│
├── [ProductName]/               # THE PRODUCT
│   ├── src/                     # Product source code
│   ├── tests/                   # Product tests
│   └── CLAUDE.md                # Product instructions (optional)
│
└── CLAUDE.md                    # Factory instructions (this file)
```

### The Rule

**Factory orchestrates. Product gets shipped.**

| Layer | Contains | Ships? |
|-------|----------|--------|
| Factory (root) | Roadmaps, decisions, planning, agents, process | No |
| Product (`[ProductName]/`) | Code, tests, schemas, configs | Yes |

### What Goes Where

| Factory Level (root `.claude/`) | Product Level (`[ProductName]/`) |
|---------------------------------|----------------------------------|
| Roadmaps and planning docs | Source code |
| Decision records (ADRs) | Tests |
| Agent definitions | Schemas |
| Session context and state | Package configs |
| Temporary drafts | Product-specific docs |
| Changelog | Anything that ships |

### Why This Matters

1. **Clean deployments** - Copy `[ProductName]/`, nothing else
2. **Clear context** - Builder knows what's process vs product
3. **Git hygiene** - Easy to ignore factory artifacts from releases
4. **Multi-product ready** - One factory can manage multiple products
5. **No pollution** - Planning artifacts don't clutter product code

### Anti-Patterns

```
# BAD - Everything mixed together
Project/
├── .claude/          # Builder stuff
├── src/              # Product code (mixed!)
├── PM/               # Builder stuff (mixed!)
├── roadmap.md        # Builder stuff (mixed!)
└── tests/            # Product code (mixed!)

# GOOD - Clean separation
Project/
├── .claude/          # Builder stuff ONLY
│   └── PM/
├── [ProductName]/    # Product ONLY
│   ├── src/
│   └── tests/
└── CLAUDE.md
```

---

## Shortcuts

**Paths:**
| Var | Path |
|-----|------|
| `$PROD` | `[ProductName]/` |
| `$PM` | `.claude/PM` |
| `$SSOT` | `$PM/SSoT` |
| `$TT` | `$PM/think-tank` |
| `$CTX` | `.claude/context.yaml` |
| `$ROAD` | `$SSOT/ROADMAP.yaml` |
| `$NORTH` | `$SSOT/NORTHSTAR.md` |
| `$TEMP` | `$PM/TEMP` |
| `$PREFS` | `$PM/HC-LOG/USER-PREFERENCES.md` |
| `$FAILS` | `$PM/HC-LOG/HC-FAILURES.md` |
| `$BACKLOG` | `$PM/BACKLOG.yaml` |

**Proxies** (Role-Based Architecture - ADR-005):
| Var | Port | Purpose | Use For |
|-----|------|---------|---------|
| `$HC_REAS_A` | 2410 | Claude Opus | Heavy reasoning, complex analysis |
| `$HC_REAS_B` | 2411 | Gemini Pro | QA, challenger reasoning |
| `$HC_WORK` | 2412 | Gemini Flash | Workers, code writing, scouts |
| `$HC_WORK_R` | 2413 | Gemini Flash | Workers with extended thinking |
| `$HC_ORCA` | 2414 | Gemini Flash | Light orchestration |
| `$HC_ORCA_R` | 2415 | Gemini Pro | Heavy orchestration |

**Quick Aliases** (for direct spawning):
| Alias | Maps To | Example |
|-------|---------|---------|
| `$WORK` | HC_WORK (2412) | Fast tasks, code |
| `$REASON` | HC_REAS_B (2411) | QA, analysis |
| `$HEAVY` | HC_REAS_A (2410) | Complex reasoning |

**Agents:** `$GIT` = git-engineer | `$SCOUT` = hc-scout
--*INTERNAL NOTE: **DO NOT USE git-engineer in the H-Claude Repo!***
---

## Architecture: Orchestrator + HD

H-Claude uses two integrated components. Full specification: `$SSOT/HD_INTERFACE.md`

| Component | Role | Location |
|-----------|------|----------|
| **Orchestrator** | Development engine (Python TDD loop) | `orchestrator/` |
| **HD** | PO/User-Proxy - manages Orchestrator on user's behalf | `.claude/skills/` |

**The Two Loops:**
```
┌─────────────────────────────────────────────────────────────┐
│  DIALOGUE LOOP (HD)           │  WORKFLOW LOOP (Orchestrator)│
│  User-facing conversation     │  Development execution       │
│  - Extract requirements       │  - TDD cycles                │
│  - Lock decisions (ADRs)      │  - Code generation           │
│  - Approve/reject stories     │  - Quality gates             │
│  - Guard user focus           │  - Checkpoint/recovery       │
└─────────────────────────────────────────────────────────────┘
                    ↓ NORTHSTAR handoff ↓
```

**HD is the shield** between user and implementation noise. Development happens in background after HD hands off NORTHSTAR.

**HD Core Goals:**
| Goal | What HD Does |
|------|--------------|
| Soul Extraction | Diamond Interview - "What?" and "Why?" to extract intent |
| SSoT Creation | Produces requirements (User Stories, ADRs, Logic Trees) |
| Drift Detection | Catches pivots ("ADR says X, are we changing?") |
| Question Filter | Checks existing ADRs BEFORE bothering user |
| Focus Guardian | Keeps user on VISION, not watching agents code |

**HD CAN:** Interview, clarify, lock ADRs, approve/reject stories, update state
**HD CANNOT:** Edit code directly - MUST use Orchestrator process

**HD Skills:**
| Skill | Purpose |
|-------|---------|
| `/genesis` | Bootstrap - detect project state, start interview |
| `/diamond-diverge` | Explore problem space (Why, What, Edges) |
| `/diamond-converge` | Prioritize entities (MoSCoW grouping) |
| `/diamond-synthesize` | Lock decisions, create artifacts |
| `/draft-userstory` | Generate UserStory from requirements |
| `/draft-adr` | Generate ADR from decisions |

---

## HC Role: Factory Operator & Orchestrator

**HC = H-Claude** (the main Claude session interacting with the user)

HC operates the Factory to build the Product. Guide user through: **SSoT → Roadmap → Phases → Execution**

| Document | Contains | Perspective |
|----------|----------|-------------|
| `NORTHSTAR.md` | WHAT - Goals, features, requirements | User/Customer |
| `ROADMAP.yaml` | HOW - Phases, execution order | Developer/Builder |

These MUST stay aligned. NORTHSTAR = destination; ROADMAP = route.

**Working in this structure:**
- Planning/decisions → Factory level (`$PM/`, `$SSOT/`)
- Writing code → Product level (`$PROD/src/`)
- Running tests → Product level (`$PROD/tests/`)
- Tracking progress → Factory level (`$PM/CHANGELOG.md`)

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
- **HC_WORK (2412) for code writing** - Gemini Flash, fast
- **HC_REAS_B (2411) for reasoning/QA** - Gemini Pro, thorough
- **HC_REAS_A (2410) for heavy analysis** - Claude Opus
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

**Factory operates machines. Factory does not hand-assemble.**

HC orchestrates the Factory to build the Product. HC does not do inline work.

| Work Type | Route Through |
|-----------|---------------|
| Requirements extraction | HD skills (`/genesis` → `/diamond-*` → `/draft-*`) |
| 3+ files OR phase work | Python Orchestrator (`orchestrator/`) |
| Decisions, planning | `/tt` (checks existing sessions first) |
| Code review | `/hc-glass` |
| Deep investigation | `/red-team` |
| Research (5+ file reads) | `hc-scout` agent |
| Git operations | `git-engineer` agent |

**Anti-pattern:** HC editing 10 Product files inline "because it's faster"
**Correct:** HC spawns command, reviews output, guides user

**Your job:** Use the Factory to build and maintain the Product.

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
| `$SCOUT` | Research, system checks, state triage | Session start, post-command, 5+ file searches |
| `$GIT` | Handle commits, maintain protocols | "commit these changes" |

**$SCOUT lifespan:** 45 minutes max. Respawn as needed.

Agents defined in: `.claude/agents/`

---

## SESSION START

1. **Read State:** `$CTX` (has focus, recent actions, next steps)
2. **Launch $SCOUT (background):** Check proxies, system ready
3. **Greet User:** "Last session: [action]. Focus: [objective]. What's next?"
4. **If SSoT Incomplete:** Guide user through setup first

$SCOUT reports: "Systems ON" or "Issue found, investigating..."
HC continues working while $SCOUT runs.

---

## POST-EXECUTION

After Orchestrator run, `/think-tank`, `/hc-glass`, `/red-team` completion, spawn `$SCOUT` for triage:

```
$SCOUT reviews session and updates:
- $CTX: focus, recent_actions, next steps
- $BACKLOG: tech debt discovered
- $FAILS: notable failures (NOT trivial)
- $PREFS: user preferences surfaced (NOT trivial)
```

**Triage questions:**
1. What tech debt emerged? → $BACKLOG
2. Any failures to learn from? → $FAILS (if notable)
3. Any user preferences revealed? → $PREFS (if notable)
4. What's next? → $CTX focus/next steps

---

## Quick Reference

### Folder Architecture

```
[ProjectRoot]/                    # THE FACTORY
├── .claude/                      # Factory workspace
│   ├── context.yaml              # $CTX - session state
│   ├── agents/                   # $GIT, $SCOUT
│   ├── commands/                 # /think-tank, /hc-execute, /hc-glass, /red-team
│   ├── skills/                   # /tt and other skills
│   └── PM/                       # $PM
│       ├── SSoT/                 # $SSOT - $NORTH, $ROAD, ADRs/
│       ├── HC-LOG/               # USER-PREFERENCES.md, HC-FAILURES.md
│       ├── PM-View/              # MkDocs wiki
│       ├── think-tank/           # $TT - session artifacts
│       ├── hc-execute/           # Execution artifacts
│       ├── hc-glass/             # Review reports
│       └── TEMP/                 # $TEMP - drafts, scratch
│
├── [ProductName]/                # THE PRODUCT (ships)
│   ├── src/                      # Product source code
│   ├── tests/                    # Product tests
│   ├── schemas/                  # Product schemas
│   └── CLAUDE.md                 # Product instructions (optional)
│
└── CLAUDE.md                     # Factory instructions (this file)
```

### Commands

| Command | Purpose | Output |
|---------|---------|--------|
| `/think-tank --roadmap` | Create project phases | `ROADMAP.yaml` |
| `/think-tank --phase=X` | Plan specific phase | `execution-plan.yaml` |
| `/think-tank "Topic"` | Ad-hoc research | Findings |
| `/hc-glass` | Code/system review | Issues list |
| `/red-team` | Deep investigation | Root cause analysis |
| `/ask <file>` | Get Pro agent feedback | Structured review |

### Execution

| Method | When to Use |
|--------|-------------|
| Python Orchestrator | Phase work, TDD execution |
| HD Skills | Requirements extraction |

```bash
# Run orchestrator
python orchestrator/main.py

# Or via HD interview
/genesis → /diamond-diverge → /diamond-converge → /draft-userstory
```

### Proxies

```bash
# Spawn via Bash (Task tool doesn't work for custom proxies)
ANTHROPIC_API_BASE_URL=http://localhost:2412 claude --dangerously-skip-permissions -p "task"  # Workers
ANTHROPIC_API_BASE_URL=http://localhost:2411 claude --dangerously-skip-permissions -p "task"  # QA/Reasoning
ANTHROPIC_API_BASE_URL=http://localhost:2410 claude --dangerously-skip-permissions -p "task"  # Heavy reasoning
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

```mermaid
graph LR
    A[$NORTH] --> B[/tt --roadmap]
    B --> C[$ROAD]
    C --> D[/tt --phase=X]
    D --> E[$GIT checkpoint]
    E --> F[Orchestrator]
    F --> G[Phase complete]
    G --> C
```

**With HD Interview:**
```mermaid
graph LR
    A[/genesis] --> B[/diamond-diverge]
    B --> C[/diamond-converge]
    C --> D[/diamond-synthesize]
    D --> E[/draft-userstory]
    E --> F[$NORTH]
    F --> G[Orchestrator]
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

| File | Purpose | Schema |
|------|---------|--------|
| `$CTX` | Session state, focus, recent actions | See actual file |
| `$ROAD` | Phases, dependencies, plan paths | See actual file |
| `$NORTH` | Goals, features, requirements | See actual file |

---

## Git Agent

Ask Claude: "commit these changes" → spawns `$GIT`

**What it does:**
- Analyzes changes, crafts Conventional Commit message
- Always includes `$CTX` (crash-proof state)
- Follows `$PM/GIT/PROTOCOLS.md`

---

## Principles

- **Factory builds Product** - keep them cleanly separated
- **NORTHSTAR guides all work** - validate solutions against it
- **Decisions are documented** - ADRs for architectural choices
- **Context is precious** - delegate to sub-agents
- **CHANGELOG is the work log** - update with every commit
- **BACKLOG prevents forgetting** - defer, don't lose track
- **Product ships alone** - `[ProductName]/` contains everything deployable
