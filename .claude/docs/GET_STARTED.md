# H-Claude Installation Guide

AI agent orchestration template for Claude Code projects. Provides structured workflows for planning (think-tank councils) and execution (parallel workers with QA).

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Claude CLI** | Installed and authenticated (`claude --version`) |
| **Node.js** | >= 18.0.0 |
| **Google AI API Key** | For Gemini proxies (CG-Flash, CG-Pro) |
| **git** | For version control |
| **curl** | For installer script |

---

## Installation Methods

### Method 1: One-Command Global Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/HyerAI/H-Claude/main/install.sh | bash
```

This installs H-Claude globally to `~/.claude/`:

| Component | Location | Purpose |
|-----------|----------|---------|
| Proxies | `~/.claude/HC-Proxies/` | CG-Flash, CG-Pro, CC-Claude |
| Scripts | `~/.claude/bin/` | start-proxies.sh, stop-proxies.sh |
| Templates | `~/.claude/h-claude-template/` | Workflow files for /hc-init |

**After install:**
1. Configure API keys (see below)
2. Start proxies: `~/.claude/bin/start-proxies.sh`
3. In any project: `claude` → `/hc-init`

---

### Method 2: Clone to ~/.claude/H-Claude (Recommended for Dev)

```bash
git clone https://github.com/HyerAI/H-Claude.git ~/.claude/H-Claude
cd ~/.claude/H-Claude
.claude/scripts/setup.sh
```

The setup script will:
- Install proxy dependencies
- Copy `/hc-init` command to `~/.claude/commands/`
- Create symlink `~/.claude/H-Claude` (for template access)

**After setup**, in any project run:
```bash
claude
/hc-init
```

---

## Configure API Keys

### For Global Install

```bash
# Edit these files:
~/.claude/HC-Proxies/CG-Flash/.env
~/.claude/HC-Proxies/CG-Pro/.env

# Add your Google AI API key:
GOOGLE_AI_API_KEY=your-key-here
```

### For Template Clone

```bash
# Edit these files:
HC-Proxies/CG-Flash/.env
HC-Proxies/CG-Pro/.env
```

Get your Google AI API key at: https://aistudio.google.com/apikey

**CC-Claude proxy** uses Claude CLI authentication (no API key needed).

---

## Start Proxies

### Global Install

```bash
~/.claude/bin/start-proxies.sh
```

### Template Clone

```bash
.claude/scripts/start-proxies.sh
```

To stop proxies:

```bash
~/.claude/bin/stop-proxies.sh          # Global
.claude/scripts/stop-proxies.sh        # Template clone
```

---

## Initialize a Project

After global install, initialize H-Claude in any project:

```bash
# Navigate to your project
cd my-project

# Open Claude Code
claude

# Run initialization skill
/hc-init
```

This copies workflow files to your project:
- `.claude/commands/` - Orchestration commands
- `.claude/agents/` - Agent definitions
- `.claude/skills/` - Reusable skills
- `.claude/templates/` - Prompt templates
- `.claude/PM/` - Project management state
- `CLAUDE.md` - Project instructions

---

## Proxy Reference

| Proxy | Port | Backend | Use Case |
|-------|------|---------|----------|
| CG-Flash | 2405 | Gemini Flash | Fast workers, code writing |
| CG-Pro | 2406 | Gemini Pro | Reasoning, QA, analysis |
| CG-Image | 2407 | Gemini Image | Image generation |
| CC-Claude | 2408 | Claude CLI | Complex reasoning |

---

## Verify Installation

Check proxy health:

```bash
curl http://localhost:2405/health  # Flash
curl http://localhost:2406/health  # Pro
curl http://localhost:2408/health  # Claude
```

Expected response: `{"status":"ok"}`

Test a sub-agent spawn:

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude -p "echo 'Hello from Flash proxy'"
```

---

## First Steps

1. **Edit NORTHSTAR.md** - Define your project goals, requirements, constraints

2. **Create roadmap**:
   ```
   /think-tank --roadmap
   ```

3. **Plan a phase**:
   ```
   /think-tank "Phase Name" --phase=PHASE-001
   ```

4. **Execute the plan**:
   ```
   /hc-execute
   ```

See `WORKFLOW_GUIDE.md` for complete workflow documentation.

---

## View PM Dashboard (Optional)

Monitor your project via the local wiki:

```bash
.claude/PM/PM-View/start-wiki.sh
```

Open http://127.0.0.1:8003 to see:
- Command flowcharts (think-tank, hc-execute, hc-glass, red-team)
- Session history and artifacts
- ADRs and SSoT documents

**Stop the wiki:**
```bash
.claude/PM/PM-View/stop-wiki.sh
```

**Multiple projects:** Edit `.claude/PM/PM-View/.env` to use different ports:
```bash
PM_VIEW_HOST=127.0.0.1
PM_VIEW_PORT=8004  # Change per project
```

**First-time setup:**
```bash
pipx install mkdocs-material --include-deps
pipx inject mkdocs-material mkdocs-awesome-pages-plugin
```

---

## Troubleshooting

### Installer Failed

```bash
# Check prerequisites
node --version    # Should be >= 18
git --version
curl --version

# Run installer with debug
bash -x install.sh
```

### Proxy Connection Refused

```bash
# Check if proxies are running
curl http://localhost:2405/health

# Start proxies (global install)
~/.claude/bin/start-proxies.sh

# Check logs
cat /tmp/h-claude/cg-flash.log
```

### Port Already in Use

```bash
# Stop existing proxies
~/.claude/bin/stop-proxies.sh

# Or kill by port
lsof -ti:2405 | xargs kill -9
```

### /hc-init Not Working

```bash
# Verify command exists
ls ~/.claude/commands/hc-init.md

# Verify template exists
ls ~/.claude/H-Claude/.claude/

# If missing, run setup again
cd ~/.claude/H-Claude && .claude/scripts/setup.sh
```

### Invalid Google API Key

```bash
# Verify key works
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY"
```

If error: regenerate at https://aistudio.google.com/apikey

---

## File Structure

### Global Installation (`~/.claude/`)

```
~/.claude/
├── commands/               # Global slash commands
│   └── hc-init.md          # Project initialization command
├── H-Claude/               # Template source (symlink or clone)
│   └── .claude/            # Template files copied by /hc-init
├── HC-Proxies/             # Proxy servers (if installed globally)
└── CLAUDE.md               # User's global instructions
```

### Per-Project (after /hc-init)

```
your-project/
├── .claude/                # Workflow files
│   ├── commands/           # think-tank, hc-execute, etc.
│   ├── agents/             # git-engineer, hc-scout
│   ├── skills/             # adr-writer, hc-init, etc.
│   ├── templates/          # Prompt templates
│   ├── context.yaml        # Session state
│   └── PM/                 # Project management
│       ├── SSoT/           # NORTHSTAR.md, ROADMAP.yaml
│       ├── think-tank/     # Planning sessions
│       └── hc-execute/  # Execution artifacts
├── src/                    # Your code
└── CLAUDE.md               # Project instructions
```

---

## Updating H-Claude

To update workflow files in a project:

```bash
claude
/hc-init --update
```

To update global installation:

```bash
curl -fsSL https://raw.githubusercontent.com/HyerAI/H-Claude/main/install.sh | bash
```

---

## Next Steps

→ Read **WORKFLOW_GUIDE.md** for complete workflow documentation

---

*Version: 0.5.0 | Updated: 2026-01-09*
