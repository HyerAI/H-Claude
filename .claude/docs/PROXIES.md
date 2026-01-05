# Proxy Architecture

H-Claude uses **proxy servers** to route Claude Code sub-agent requests to different LLM backends. This enables cost optimization and model specialization.

---

## How It Works

```
Claude Code (main)
       │
       ▼
┌──────────────────┐
│ ANTHROPIC_API_   │  Environment variable tells Claude
│ BASE_URL=...     │  which proxy to use
└──────────────────┘
       │
       ▼
┌──────────────────┐     ┌──────────────────┐
│  HC-Work:2412    │     │  Gemini Flash    │
│  (Anthropic API) │ ──► │  (Google AI API) │
└──────────────────┘     └──────────────────┘
```

Each proxy:
1. Receives requests in **Anthropic API format** (what Claude Code speaks)
2. Translates to the **backend's native format** (Google AI, Claude CLI)
3. Forwards to the backend LLM
4. Translates the response back to Anthropic format
5. Returns to Claude Code

---

## Role-Based Proxy Architecture

Proxies are named by **role**, not model. This decouples documentation from specific models.

| Proxy | Port | Default Model | Purpose |
|-------|------|---------------|---------|
| **HC-Reas-A** | 2410 | Claude Opus (via CLI) | Heavy reasoning, complex orchestration |
| **HC-Reas-B** | 2411 | Gemini Pro | Challenger reasoning, QA commanders |
| **HC-Work** | 2412 | Gemini Flash | Execution workers, scouts |
| **HC-Work-R** | 2413 | Gemini Flash | Execution with extended thinking |
| **HC-Orca** | 2414 | Gemini Flash | Light coordination |
| **HC-Orca-R** | 2415 | Gemini Pro | Heavy coordination |
| **CG-Image** | 2407 | Gemini Pro (Banana) | Native image generation |

### Proxy Naming Convention

- **HC-Reas-** = Reasoning proxies (heavy thinking)
- **HC-Work-** = Worker proxies (task execution)
- **HC-Orca-** = Orchestration proxies (coordination)
- **-R suffix** = Enhanced reasoning/thinking variant

---

## Agent-to-Proxy Mapping

| Agent Role | Proxy | Port | Why |
|------------|-------|------|-----|
| Orchestrators | HC-Orca | 2414 | Light coordination |
| Heavy Orchestrators | HC-Orca-R | 2415 | Complex coordination |
| QA/Commanders | HC-Reas-B | 2411 | Challenger reasoning |
| Complex Reasoning | HC-Reas-A | 2410 | Heavy analysis |
| Workers/Scouts | HC-Work | 2412 | Fast execution |
| Workers (thinking) | HC-Work-R | 2413 | Extended reasoning |

---

## Spawning Sub-Agents

To spawn a sub-agent through a proxy:

```bash
# Worker (fast execution)
ANTHROPIC_API_BASE_URL=http://localhost:2412 claude --dangerously-skip-permissions -p "task"

# Reasoning/QA
ANTHROPIC_API_BASE_URL=http://localhost:2411 claude --dangerously-skip-permissions -p "task"

# Heavy reasoning (Claude)
ANTHROPIC_API_BASE_URL=http://localhost:2410 claude --dangerously-skip-permissions -p "task"

# Light orchestration
ANTHROPIC_API_BASE_URL=http://localhost:2414 claude --dangerously-skip-permissions -p "task"

# Heavy orchestration
ANTHROPIC_API_BASE_URL=http://localhost:2415 claude --dangerously-skip-permissions -p "task"
```

---

## Configuration

### API Keys

Gemini proxies require a Google AI API key:

```bash
# Edit the .env file for each proxy
~/.claude/HC-Proxies/HC-Work/.env
~/.claude/HC-Proxies/HC-Reas-B/.env
# etc.

# Content:
GOOGLE_AI_API_KEY=your-key-here
```

Get your key at: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)

**HC-Reas-A** uses your existing Claude CLI authentication (no API key needed).

### Environment Variables

Each proxy can be configured via its `.env` file:

| Variable | Example | Description |
|----------|---------|-------------|
| `GOOGLE_AI_API_KEY` | (required for Gemini) | Your Google AI API key |
| `MODEL` | `gemini-3-flash-preview` | Backend model to use |
| `PORT` | `2412` | Port number |

---

## Changing Models

The power of role-based proxies: change the model without updating any docs.

### Edit Proxy .env File

```bash
# Example: Change HC-Work from Flash to Pro
# Edit ~/.claude/HC-Proxies/HC-Work/.env
MODEL=gemini-3-pro  # was gemini-3-flash-preview
```

Restart the proxy. All commands using HC-Work now use Pro.

### Available Models

**Gemini (Google AI):**
- `gemini-3-flash-preview` (default for HC-Work, HC-Orca)
- `gemini-3-pro` (default for HC-Reas-B, HC-Orca-R)
- `gemini-2.5-pro-preview`
- `gemini-2.0-flash-exp`

**Claude (via CLI):**
- `opus` (default for HC-Reas-A)
- `sonnet`

---

## Starting/Stopping Proxies

### Project Scripts

```bash
# Start all proxies
.claude/scripts/start-proxies.sh

# Stop all proxies
.claude/scripts/stop-proxies.sh
```

### Global Install

```bash
# Start all proxies
~/.claude/bin/start-proxies.sh

# Stop all proxies
~/.claude/bin/stop-proxies.sh
```

---

## Health Checks

Verify proxies are running:

```bash
curl http://localhost:2410/health  # HC-Reas-A
curl http://localhost:2411/health  # HC-Reas-B
curl http://localhost:2412/health  # HC-Work
curl http://localhost:2413/health  # HC-Work-R
curl http://localhost:2414/health  # HC-Orca
curl http://localhost:2415/health  # HC-Orca-R

# Expected: {"status":"ok"}
```

---

## Troubleshooting

### Proxy Connection Refused

```bash
# Check if running
curl http://localhost:2412/health

# Start proxies
.claude/scripts/start-proxies.sh

# Check logs
cat /tmp/h-claude/hc-work.log
```

### Invalid API Key

```bash
# Test your key directly
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY"
```

If error, regenerate at [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### Port Already in Use

```bash
# Stop existing proxies
.claude/scripts/stop-proxies.sh

# Or kill by port
lsof -ti:2412 | xargs kill -9
```

---

## Cost Optimization

The proxy architecture enables significant cost savings:

| Role | Proxy | Model | Why |
|------|-------|-------|-----|
| Scouts (research) | HC-Work | Flash | High volume, simple tasks |
| Workers (code) | HC-Work | Flash | Fast iteration |
| QA/Commanders | HC-Reas-B | Pro | Needs reasoning |
| Orchestrators | HC-Orca | Flash | Light coordination |
| Complex reasoning | HC-Reas-A | Claude | Heavy analysis |

**Typical savings:** 60-80% vs using Claude for everything.

---

## Proxy Types

### Google AI Proxies (axios)

HC-Work, HC-Work-R, HC-Reas-B, HC-Orca, HC-Orca-R all use the Google AI API:

- Translate Anthropic format → Google generativelanguage.googleapis.com
- Support streaming responses
- Handle tool use translation

### Claude CLI Proxy (child_process)

HC-Reas-A spawns Claude CLI as a subprocess:

- Uses your existing Claude authentication
- Full Claude Opus capability
- Higher latency, higher cost

---

## Security Notes

1. **API keys** are stored in `.env` files (gitignored)
2. **Proxies bind to localhost** by default (not exposed to network)
3. **`--dangerously-skip-permissions`** is required for non-interactive sub-agents

---

*See also: [GET_STARTED.md](GET_STARTED.md) for installation, [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) for usage*
