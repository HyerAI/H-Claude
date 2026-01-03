# H-Claude

AI agent orchestration template for Claude Code projects.

## What You Get

- **Multi-agent planning councils** (`/think-tank`) - Expert personas collaborate to map decisions
- **Parallel execution with QA gates** (`/hc-plan-execute`) - Workers implement, QA verifies, Sweeper catches the 15% missed
- **Code review audits** (`/hc-glass`) - Comprehensive codebase analysis
- **Checkpoint/rollback** - Safe execution with git-based recovery

## Quick Start

```bash
# 1. Clone
git clone https://github.com/HyerAI/H-Claude.git my-project
cd my-project

# 2. Setup (installs dependencies, creates .env files)
./setup.sh

# 3. Configure API keys
# Edit infrastructure/CG-Flash/.env and infrastructure/CG-Pro/.env
# Add your Google AI API key: GOOGLE_AI_API_KEY=your-key

# 4. Start proxies
./start-proxies.sh

# 5. Open Claude Code
claude
```

## The Workflow

```
NORTHSTAR.md (WHAT)     →  Your goals, requirements, constraints
     ↓
ROADMAP.yaml (HOW)      →  Development phases, execution order
     ↓
/think-tank --phase     →  Plan each phase with expert council
     ↓
/hc-plan-execute        →  Parallel workers implement with QA
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

MIT
