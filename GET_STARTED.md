# H-Claude - Getting Started

Complete setup guide for H-Claude project template.

---

## Prerequisites

- Node.js >= 18.0.0
- Claude CLI installed and authenticated
- Google AI API key (for Gemini proxies)

---

## 1. Clone or Copy Template

```bash
# If using as template for new project
cp -r H-Claude /path/to/your/new-project
cd /path/to/your/new-project
```

---

## 2. Setup LLM Proxies

H-Claude uses proxy servers to route requests to different LLMs while maintaining Claude Code compatibility.

### Available Proxies

| Proxy | Port | Backend | Use Case |
|-------|------|---------|----------|
| CG-Flash | 2405 | Gemini Flash | Fast workers, simple tasks |
| CG-Pro | 2406 | Gemini Pro | Reasoning, QA, planning |
| CG-Image | 2407 | Gemini Image | Image generation |
| CC-Claude | 2408 | Claude (pass-through) | Complex reasoning |

### Install Dependencies

```bash
# Install each proxy
cd infrastructure/CG-Flash && npm install && cd ../..
cd infrastructure/CG-Pro && npm install && cd ../..
cd infrastructure/CC-Claude && npm install && cd ../..
# CG-Image if needed
cd infrastructure/CG-Image && npm install && cd ../..
```

### Configure API Keys

Each proxy needs a `.env` file:

**CG-Flash / CG-Pro / CG-Image:**
```bash
cd infrastructure/CG-Flash
cp .env.example .env
# Edit .env:
GOOGLE_AI_API_KEY=your-google-ai-key-here
```

**CC-Claude (optional, uses Claude CLI auth by default):**
```bash
cd infrastructure/CC-Claude
cp .env.example .env
# Edit .env if using API key instead of CLI auth:
ANTHROPIC_API_KEY=your-anthropic-key-here
```

### Start Proxies

Start the proxies you need (in separate terminals or use a process manager):

```bash
# Terminal 1 - Flash (fast workers)
cd infrastructure/CG-Flash && npm start

# Terminal 2 - Pro (reasoning)
cd infrastructure/CG-Pro && npm start

# Terminal 3 - Claude (complex tasks)
cd infrastructure/CC-Claude && npm start
```

### Verify Proxies

```bash
curl http://localhost:2405/health  # Flash
curl http://localhost:2406/health  # Pro
curl http://localhost:2408/health  # Claude
```

---

## 3. Initialize Project

### Create NORTHSTAR.md

The NORTHSTAR document guides all agents. Claude will ask you to create one if missing.

```bash
# Create manually or let Claude prompt you
touch .claude/PM/SSoT/NORTHSTAR.md
```

Minimum content:
```markdown
# Project NORTHSTAR

## Purpose
What this project does and why.

## Goals
- Goal 1
- Goal 2

## Constraints
- Constraint 1
- Constraint 2

## Non-Goals
- What we explicitly won't do
```

### Verify Structure

```bash
ls -la .claude/
# Should see: context.yaml, settings.json, agents/, commands/, PM/, skills/, templates/

ls -la .claude/PM/
# Should see: SSoT/, think-tank/, hc-plan-execute/, hc-glass/, red-team/, TEMP/, BACKLOG.yaml, CHANGELOG.md
```

---

## 4. Run Health Check

Before starting work, verify your environment:

```bash
# Check everything is set up
./hc-init

# Fix issues automatically (creates missing folders, copies .env.example)
./hc-init --fix

# Start proxy servers if not running
./hc-init --start-proxies
```

---

## 5. The Complete Workflow

H-Claude uses a **hierarchical workflow** where big objectives break down into action items, each executed independently.

### Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  ./hc-init --fix                                            │
│    └── Creates folders, validates environment               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  /think-tank --main "Project Vision"                        │
│    └── MAIN session: Council discusses long-horizon goals   │
│    └── Outputs: action-items.yaml (3-7 items)               │
│    └── Artifacts: .claude/PM/think-tank/{session}/          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  For each action item (respect dependencies):               │
│                                                             │
│    /think-tank "AI-001" --parent=main                       │
│      └── Sub-session researches specific item               │
│      └── Council decides approach                           │
│      └── Outputs: execution-plan.yaml                       │
│                              ↓                              │
│    /hc-plan-execute                                         │
│      └── Workers implement plan                             │
│      └── QA verifies each phase                             │
│      └── SWEEP & VERIFY catches missed work                 │
│                              ↓                              │
│    /hc-glass (optional)                                     │
│      └── Code review, security audit                        │
│      └── Find bugs and conflicts                            │
│                              ↓                              │
│    Mark action item complete in MAIN session                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  When all items complete:                                   │
│    └── Archive MAIN session                                 │
│    └── Update context.yaml                                  │
│    └── Commit changes                                       │
└─────────────────────────────────────────────────────────────┘
```

### Session Hierarchy

```
MAIN Think-Tank (Project Vision)
├── Action Item 1 → Sub Think-Tank → execution-plan.yaml → Execute
├── Action Item 2 → Sub Think-Tank → execution-plan.yaml → Execute
├── Action Item 3 → Sub Think-Tank → execution-plan.yaml → Execute
│   ↓
│   Issues found? → /red-team → Fix → Re-execute
│
└── All items complete → Archive MAIN
```

### Step-by-Step

**Step 1: Start MAIN Think-Tank**
```bash
/think-tank --main "Authentication System Design"
```
- Council of experts discusses the objective
- You make key decisions when prompted
- Outputs `action-items.yaml` with 3-7 discrete work items
- Each item has dependencies and acceptance criteria

**Step 2: Execute Each Action Item**
```bash
# For action item AI-001 (respecting dependency order)
/think-tank "AI-001" --parent=main
```
- Creates a sub-session linked to MAIN
- Council researches and plans the specific item
- Outputs `execution-plan.yaml` with implementation steps

**Step 3: Implement the Plan**
```bash
/hc-plan-execute
```
- Workers implement the approved plan
- QA verifies each phase
- SWEEP & VERIFY protocol catches 15% missed work

**Step 4: Quality Check (Optional)**
```bash
/hc-glass
```
- Comprehensive code review
- Security and architecture audit
- Identifies bugs, conflicts, incomplete work

**Step 5: Fix Issues**
```bash
# If bugs found, deep dive
/red-team "Token refresh failing after 24h"
```
- Root cause analysis
- Findings feed back into fixes

**Step 6: Mark Complete**
- Update action item status in MAIN session
- Continue to next action item (respecting dependencies)

**Step 7: Archive**
- When all action items complete, archive MAIN session
- Update context.yaml with outcomes
- Commit changes

---

## 6. Session Protocols

### Session Start

1. **Open project in Claude Code**
   ```bash
   cd /path/to/your/project
   claude
   ```

2. **Claude reads context.yaml** automatically and resumes from last state

3. **Run health check** if needed: `./hc-init`

### Session End

1. **Update context.yaml** with current state
2. **Update CHANGELOG.md** with changes
3. **Set git trigger** in context.yaml:
   ```yaml
   git:
     status: ready
     note: 'Description of changes to commit'
   ```
4. **Commit** (Claude handles this when asked)

---

## 7. Spawning Sub-Agents

Use proxies to spawn sub-agents for parallel work:

```bash
# Fast worker (Gemini Flash) - writing code, simple tasks
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "task"

# Reasoning agent (Gemini Pro) - QA, planning, analysis
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "task"

# Complex reasoning (Claude) - difficult problems
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "task"
```

---

## Key Files

| File | Location | Purpose |
|------|----------|---------|
| `action-items.yaml` | think-tank/{session}/ | MAIN session work items |
| `execution-plan.yaml` | think-tank/{session}/ | Implementation plan |
| `STATE.yaml` | think-tank/{session}/ | Session state, decisions |
| `context.yaml` | .claude/ | Project-wide status tracking |
| `BACKLOG.yaml` | .claude/PM/ | Deferred work items |

---

## Troubleshooting

### Proxy Connection Refused

```bash
# Check if proxy is running
curl http://localhost:2405/health

# If not, start it
cd infrastructure/CG-Flash && npm start
```

### Port Already in Use

```bash
# Find and kill process
lsof -ti:2405 | xargs kill

# Or change port in .env
CG_FLASH_PORT=2409
```

### Context Not Loading

```bash
# Verify context.yaml exists and is valid YAML
cat .claude/context.yaml

# Check for syntax errors
python3 -c "import yaml; yaml.safe_load(open('.claude/context.yaml'))"
```

### Git Agent Not Committing

Check context.yaml:
```yaml
git:
  status: ready  # Must be 'ready', not 'working' or 'blocked'
  note: 'What to commit'
```

---

## Next Steps

1. **Customize CLAUDE.md** for your project specifics
2. **Create project-specific agents** in `.claude/agents/`
3. **Define your NORTHSTAR.md** with project goals
4. **Start a /think-tank** session to explore your first feature

---

## Resources

- `CLAUDE.md` - Complete workflow documentation
- `.claude/PM/SSoT/ADRs/` - Decision records
- `.claude/PM/GIT/` - Git protocols and reference
