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

## 4. Start Working

### Session Start Protocol

1. **Open project in Claude Code**
   ```bash
   cd /path/to/your/project
   claude
   ```

2. **Claude reads context.yaml** automatically and resumes from last state

3. **Git agent launches** and watches for commit triggers

### Using Commands

```bash
# Research, decide, and plan (the brain)
/think-tank

# Execute an approved plan
/hc-plan-execute

# Code/system review
/hc-glass

# Deep dive into issue/bug
/red-team
```

### Spawning Sub-Agents

Use proxies to spawn sub-agents for parallel work:

```bash
# Fast worker (Gemini Flash)
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "task description"

# Reasoning agent (Gemini Pro)
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "task description"

# Complex reasoning (Claude)
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "task description"
```

---

## 5. Session End Protocol

1. **Update context.yaml** with current state
2. **Update CHANGELOG.md** with changes
3. **Set git trigger** in context.yaml:
   ```yaml
   git:
     status: ready
     note: 'Description of changes to commit'
   ```
4. **Git agent commits** including context.yaml

---

## Workflow Example

```
1. /think-tank "Authentication system design"
   → Council investigates options
   → You DECIDE on a path
   → Think-tank generates execution-plan.yaml
   → Artifacts saved to .claude/PM/think-tank/auth_system_{date}/

2. /hc-plan-execute TOPIC: auth_system
   → Workers implement the approved plan
   → QA verifies each phase
   → Sweeper hunts for gaps

3. /hc-glass
   → Review implementation for issues
   → Security audit

4. If bugs found: /red-team "Investigate token refresh bug"
   → Deep dive analysis
   → Findings feed back to /hc-plan-execute for fixes
```

### Key Files

| File | Location | Purpose |
|------|----------|---------|
| `STATE.yaml` | think-tank/{topic}/ | Session state, decisions |
| `execution-plan.yaml` | think-tank/{topic}/ | Implementation plan |
| `context.yaml` | .claude/ | Project-wide status tracking |

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
