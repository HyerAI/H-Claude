# H-Claude

AI agent orchestration template for Claude Code projects.

## What You Get

- **Multi-agent planning councils** (`/think-tank`) - Expert personas collaborate to map decisions
- **Parallel execution with QA gates** (`/hc-execute`) - Workers implement, QA verifies, Sweeper catches the 15% missed
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
~/.claude/infrastructure/CG-Flash/.env
~/.claude/infrastructure/CG-Pro/.env
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

## Documentation

| Doc | Purpose |
|-----|---------|
| [GET_STARTED.md](GET_STARTED.md) | Full installation guide |
| [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) | How to use the workflow |
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

MIT - [HyerAI](https://github.com/HyerAI)
