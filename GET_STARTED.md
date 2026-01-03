# H-Claude Installation Guide

AI agent orchestration template for Claude Code projects. Provides structured workflows for planning (think-tank councils) and execution (parallel workers with QA).

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Claude CLI** | Installed and authenticated (`claude --version`) |
| **Node.js** | >= 18.0.0 |
| **Google AI API Key** | For Gemini proxies (CG-Flash, CG-Pro) |
| **Claude Subscription** | For CC-Claude proxy (uses CLI auth) |

---

## Installation

### 1. Create Project from Template

**Option A: GitHub "Use this template" button**
1. Go to [HyerAI/H-Claude](https://github.com/HyerAI/H-Claude)
2. Click "Use this template" → "Create a new repository"
3. Clone your new repository:
   ```bash
   git clone https://github.com/your-username/your-project.git
   cd your-project
   ```

**Option B: Clone directly**
```bash
git clone https://github.com/HyerAI/H-Claude.git your-project
cd your-project
rm -rf .git && git init  # Start fresh git history
```

### 2. Run Setup

```bash
./setup.sh
```

This single command:
- Installs all proxy dependencies (npm install)
- Creates `.env` files from templates
- Validates the installation
- Reports any issues

### 3. Configure API Keys

Edit the `.env` files created by setup:

```bash
# Gemini proxies (CG-Flash, CG-Pro)
# Edit: infrastructure/CG-Flash/.env
# Edit: infrastructure/CG-Pro/.env
# Add: GOOGLE_AI_API_KEY=your-key-here
```

Get your Google AI API key at: https://aistudio.google.com/apikey

**Claude Proxy (CC-Claude):** Uses Claude CLI authentication (no API key needed if CLI is authenticated).

---

## Start Proxies

Start all proxies with a single command:

```bash
./start-proxies.sh
```

This starts CG-Flash, CG-Pro, and CC-Claude in the background. To stop them:

```bash
./stop-proxies.sh
```

### Proxy Reference

| Proxy | Port | Backend | Use Case |
|-------|------|---------|----------|
| CG-Flash | 2405 | Gemini Flash | Fast workers, code writing |
| CG-Pro | 2406 | Gemini Pro | Reasoning, QA, analysis |
| CG-Image | 2407 | Gemini Image | Image generation |
| CC-Claude | 2408 | Claude CLI | Complex reasoning |

---

## Verify Installation

Check each running proxy:

```bash
curl http://localhost:2405/health  # Flash
curl http://localhost:2406/health  # Pro
curl http://localhost:2408/health  # Claude
```

Expected response: `{"status":"ok"}` or similar health message.

Test a sub-agent spawn:

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude -p "echo 'Hello from Flash proxy'"
```

---

## First Steps

1. **Start Claude Code** in your project:
   ```bash
   cd your-project
   claude
   ```

2. **Read the workflow guide**: See `WORKFLOW_GUIDE.md` for how to:
   - Define your NORTHSTAR (project goals)
   - Create a ROADMAP (development phases)
   - Plan phases with `/think-tank`
   - Execute plans with `/hc-plan-execute`

3. **Quick start commands**:
   - `/think-tank --roadmap` - Create development phases
   - `/think-tank "Phase Name" --phase=PHASE-XXX` - Plan a specific phase
   - `/hc-plan-execute` - Execute an approved plan
   - `/hc-glass` - Code review and audit

---

## Troubleshooting

### Proxy Connection Refused

```bash
# Check if proxy is running
curl http://localhost:2405/health

# If not, start all proxies
./start-proxies.sh
```

### Port Already in Use

```bash
# Stop all proxies cleanly
./stop-proxies.sh

# Then restart
./start-proxies.sh
```

### Invalid Google API Key

```bash
# Verify key works
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY"
```

Error `API key not valid` → regenerate at https://aistudio.google.com/apikey

### Claude CLI Not Authenticated

```bash
# Check auth status
claude --version

# If not authenticated, run:
claude
# Follow prompts to authenticate
```

### hc-init Permission Denied

```bash
chmod +x ./hc-init
```

### Context Not Loading

```bash
# Verify context.yaml is valid YAML
python3 -c "import yaml; yaml.safe_load(open('.claude/context.yaml'))"
```

---

## File Structure Overview

```
your-project/
├── .claude/                    # Internal config (do not ship)
│   ├── context.yaml            # Session state
│   ├── agents/                 # Agent definitions
│   ├── commands/               # Multi-agent orchestration
│   └── PM/                     # Project Management
│       ├── SSoT/               # Single Source of Truth
│       │   ├── NORTHSTAR.md    # WHAT - Goals, requirements
│       │   └── ROADMAP.yaml    # HOW - Development phases
│       └── think-tank/         # Planning session artifacts
│
├── infrastructure/             # LLM Proxy servers
│   ├── CG-Flash/               # Gemini Flash (port 2405)
│   ├── CG-Pro/                 # Gemini Pro (port 2406)
│   └── CC-Claude/              # Claude CLI (port 2408)
│
├── src/                        # Your production code
├── CLAUDE.md                   # Project instructions
└── GET_STARTED.md              # This file
```

---

## Next Steps

→ Read **WORKFLOW_GUIDE.md** for the complete workflow documentation

---

*Version: 2.1.0 | Updated: 2026-01-02*
