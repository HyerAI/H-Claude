# H-Claude

AI agent orchestration template for Claude Code projects.

## What You Get

- **Multi-agent planning councils** (`/think-tank`) - Expert personas collaborate to map decisions
- **Parallel execution with QA gates** (`/hc-execute`) - Workers implement, QA verifies, Sweeper catches the 20% missed
- **Code review audits** (`/hc-glass`) - Comprehensive codebase analysis
- **Checkpoint/rollback** - Safe execution with git-based recovery

## Installation

### One-Command Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/HyerAI/H-Claude/main/install.sh | bash
```

This installs H-Claude globally to `~/.claude/`:
- Proxy infrastructure (shared across all projects)
- Helper scripts (`start-proxies.sh`, `stop-proxies.sh`)
- Workflow templates for project initialization

### Configure API Keys

```bash
# Edit these files and add your Google AI API key:
~/.claude/HC-Proxies/CG-Flash/.env
~/.claude/HC-Proxies/CG-Pro/.env
```

Get your API key at: https://aistudio.google.com/apikey

### Start Proxies

```bash
~/.claude/bin/start-proxies.sh
```

## Quick Start (New Project)

```bash
# 1. Create your project
mkdir my-project && cd my-project
git init

# 2. Open Claude Code
claude

# 3. Initialize H-Claude workflow
/hc-init

# 4. Follow the workflow
# Edit NORTHSTAR.md → /think-tank --roadmap → /hc-execute
```

## The Workflow

```
NORTHSTAR.md (WHAT)     →  Your goals, requirements, constraints
     ↓
ROADMAP.yaml (HOW)      →  Development phases, execution order
     ↓
/think-tank --phase     →  Plan each phase with expert council
     ↓
/hc-execute        →  Parallel workers implement with QA
```

## File Structure

### Template Files (`*.example`)

Files ending in `.example` are templates. Copy them (removing `.example`) to create your live files:

| Template | Live File | Purpose |
|----------|-----------|---------|
| `context.yaml.example` | `context.yaml` | Session state |
| `CHANGELOG.md.example` | `CHANGELOG.md` | Project changelog |
| `BACKLOG.yaml.example` | `BACKLOG.yaml` | Work tracking |
| `.env.example` | `.env` | API keys |

### SSoT Files

Files in `.claude/PM/SSoT/` are YOUR project's single source of truth:
- `NORTHSTAR.md` - Customize with your project goals
- `ROADMAP.yaml` - Define your development phases

See `.claude/examples/` for filled-in examples.

### Session Artifacts

When you run commands like `/think-tank` or `/hc-execute`, session folders are created:
- `.claude/PM/think-tank/your_session_YYYYMMDD/`
- `.claude/PM/hc-execute/your_session_YYYYMMDD/`

These are **gitignored by default**. Your workflow decisions stay local.

## Documentation

| Doc | Purpose |
|-----|---------|
| [GET_STARTED.md](.claude/docs/GET_STARTED.md) | Full installation guide |
| [WORKFLOW_GUIDE.md](.claude/docs/WORKFLOW_GUIDE.md) | How to use the workflow |
| [CLAUDE.md](CLAUDE.md) | Project context for Claude |

## Examples

See `.claude/examples/` for filled-out examples:
- `NORTHSTAR-example.md` - Complete project goals document
- `ROADMAP-example.yaml` - Multi-phase development roadmap
- `execution-plan-example.yaml` - Detailed phase execution plan

## Requirements

- [Claude Code CLI](https://claude.ai/code) installed and authenticated
- Node.js >= 18
- Google AI API key (for Gemini proxies)

## License

[MIT](docs/LICENSE) - [HyerAI](https://github.com/HyerAI)
