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
│  CG-Flash:2405   │     │  Gemini Flash    │
│  (Anthropic API) │ ──► │  (Google AI API) │
└──────────────────┘     └──────────────────┘
```

Each proxy:
1. Receives requests in **Anthropic API format** (what Claude Code speaks)
2. Translates to the **backend's native format** (Google AI, etc.)
3. Forwards to the backend LLM
4. Translates the response back to Anthropic format
5. Returns to Claude Code

---

## Available Proxies

| Proxy | Port | Backend Model | Use Case |
|-------|------|---------------|----------|
| **CG-Flash** | 2405 | Gemini 3 Flash | Fast workers, code writing, scouts |
| **CG-Pro** | 2406 | Gemini 3 Pro | Reasoning, QA, analysis, commanders |
| **CG-Image** | 2407 | Nano Banana (Gemini 3 Pro) | Native image generation |
| **CC-Claude** | 2408 | Claude Opus | Complex reasoning, orchestrators |

---

## Spawning Sub-Agents

To spawn a sub-agent through a proxy:

```bash
# Flash agent (fast, cheap)
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "task"

# Pro agent (reasoning)
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "task"

# Claude agent (complex)
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "task"
```

---

## Configuration

### API Keys

Each Gemini proxy requires a Google AI API key:

```bash
# Edit the .env file for each proxy
~/.claude/infrastructure/CG-Flash/.env
~/.claude/infrastructure/CG-Pro/.env
~/.claude/infrastructure/CG-Image/.env

# Content:
GOOGLE_AI_API_KEY=your-key-here
```

Get your key at: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)

**CC-Claude** uses your existing Claude CLI authentication (no API key needed).

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_AI_API_KEY` | (required) | Your Google AI API key |
| `KS_PROXY_MODEL` | `gemini-3-flash-preview` | Flash proxy model |
| `CG_PRO_MODEL` | `gemini-3-pro` | Pro proxy model |
| `CC_CLAUDE_MODEL` | `opus` | Claude CLI model (opus recommended) |
| `KS_PROXY_PORT` | `2405` | Flash port |
| `CG_PRO_PORT` | `2406` | Pro port |
| `CC_CLAUDE_PORT` | `2408` | Claude port |

---

## Changing Models

To use a different model, edit the proxy's `.env` file:

### Option 1: Change Gemini Model

```bash
# In ~/.claude/infrastructure/CG-Flash/.env
GOOGLE_AI_API_KEY=your-key
KS_PROXY_MODEL=gemini-2.0-flash-exp  # or gemini-1.5-flash, etc.
```

Available Gemini models:
- `gemini-3-flash-preview` (default for Flash)
- `gemini-3-pro` (default for Pro)
- `gemini-2.5-pro-preview`
- `gemini-2.0-flash-exp`
- `gemini-1.5-flash`
- `gemini-1.5-pro`

**Note:** H-Claude defaults to Gemini 3 family for best performance.

### Option 2: Use Different Provider

To use a different LLM provider (e.g., OpenAI, Anthropic direct), you would need to:

1. Create a new proxy server that translates Anthropic API → your provider's API
2. Update the port mapping
3. Set `ANTHROPIC_API_BASE_URL` to your new proxy

The proxy code is in `infrastructure/CG-Flash/server.js` - use it as a template.

---

## Starting/Stopping Proxies

### Global Install

```bash
# Start all proxies
~/.claude/bin/start-proxies.sh

# Stop all proxies
~/.claude/bin/stop-proxies.sh
```

### Template Clone

```bash
# Start
.claude/scripts/start-proxies.sh

# Stop
.claude/scripts/stop-proxies.sh
```

---

## Health Checks

Verify proxies are running:

```bash
curl http://localhost:2405/health  # Flash
curl http://localhost:2406/health  # Pro
curl http://localhost:2408/health  # Claude

# Expected: {"status":"ok"}
```

---

## Troubleshooting

### Proxy Connection Refused

```bash
# Check if running
curl http://localhost:2405/health

# Start proxies
~/.claude/bin/start-proxies.sh

# Check logs
cat /tmp/h-claude/cg-flash.log
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
~/.claude/bin/stop-proxies.sh

# Or kill by port
lsof -ti:2405 | xargs kill -9
```

---

## Cost Optimization

The proxy architecture enables significant cost savings:

| Agent Role | Proxy | Why |
|------------|-------|-----|
| Scouts (research) | Flash | High volume, simple tasks |
| Workers (code) | Flash | Fast iteration |
| QA/Commanders | Pro | Needs reasoning |
| Orchestrators | Claude | Complex coordination |

**Typical savings:** 60-80% vs using Claude for everything.

---

## Security Notes

1. **API keys** are stored in `.env` files (gitignored)
2. **Proxies bind to localhost** by default (not exposed to network)
3. **`--dangerously-skip-permissions`** is required for non-interactive sub-agents

---

*See also: [GET_STARTED.md](GET_STARTED.md) for installation, [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) for usage*
