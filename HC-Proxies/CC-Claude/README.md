---
version: V2.0.0
status: current
timestamp: 2025-12-26
tags: [readme, proxy, documentation, claude, cli, subscription]
description: "CC-Claude CLI proxy for accessing Claude via subscription (no API key required)"
---

# CC-Claude - Claude Code CLI Proxy

CLI-based proxy that spawns Claude Code subprocess for requests, enabling **subscription-based access** (Claude Max/Pro) instead of API key access.

## Purpose

Enables **any agent** (including Gemini-based L3-L5 workers) to call Claude for reasoning tasks. When your orchestrator is running on CG-Flash or CG-Pro, you can still leverage Claude's reasoning power by calling through this proxy.

**Use Cases:**
- L5 Gemini worker needs complex reasoning assistance
- Testing different orchestrator models while keeping Claude for thinking tasks
- Hybrid workflows where Gemini handles execution but Claude handles planning
- Consensus validation with mixed model types

## Architecture

```
Gemini Agent (via CG-Flash/CG-Pro)
          |
          | Needs Claude reasoning
          v
    CC-Claude (port 2408)
          |
          | Spawns CLI subprocess
          v
    claude -p "prompt" --output-format json
          |
          | Local CLI (subscription auth)
          v
    CC-Claude (parse JSON, wrap response)
          |
          v
    Gemini Agent receives Claude response
```

**Key Difference from API Mode:**
- No `ANTHROPIC_API_KEY` required
- Uses local Claude CLI authentication (subscription)
- Works with Claude Max/Pro plans

## Installation

```bash
cd ks-agents/CC-Claude
npm install
```

## Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# No API key required - uses CLI authentication

# Default model (alias like 'sonnet', 'opus' or full name)
CC_CLAUDE_MODEL=sonnet

# Port
CC_CLAUDE_PORT=2408

# Timeout for CLI subprocess (ms)
CC_CLAUDE_TIMEOUT=300000
```

**Prerequisites:**
- Claude CLI installed and authenticated (`claude` command available)
- Active Claude subscription (Max/Pro)

## Usage

### Start the Server

```bash
npm start
```

Server starts on `http://localhost:2408`

### Health Check

```bash
curl http://localhost:2408/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model": "claude-sonnet-4-20250514",
  "port": 2408,
  "api_key_configured": true,
  "target": "https://api.anthropic.com"
}
```

### Use with Claude Code

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude -p "Help me reason through this architecture decision..."
```

### Use from a Gemini Agent Script

When your orchestrator is Gemini (via CG-Flash), you can spawn a Claude reasoning call:

```bash
# Main orchestrator using Gemini Flash
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude -p "
You are an L5 worker. For complex decisions, call Claude via:
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude -p 'reasoning task'
"
```

## Endpoints

| Endpoint | Method | Purpose | Translation |
|----------|--------|---------|-------------|
| `/health` | GET | Health check | None |
| `/v1/messages` | POST | **Primary** - Anthropic format | **Pass-through** (no translation) |
| `/v1/chat/completions` | POST | OpenAI compatibility | Translates to/from Anthropic |

### `/v1/messages` (Pass-Through)

The primary endpoint. Forwards requests directly to Anthropic API:

**Request (sent by Claude Code):**
```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 8192,
  "messages": [
    {"role": "user", "content": "Explain quantum computing"}
  ]
}
```

**Response (from Anthropic, forwarded as-is):**
```json
{
  "id": "msg_...",
  "type": "message",
  "role": "assistant",
  "content": [{"type": "text", "text": "Quantum computing..."}],
  "model": "claude-sonnet-4-20250514",
  "stop_reason": "end_turn",
  "usage": {"input_tokens": 10, "output_tokens": 500}
}
```

## Model Selection

Override the default model per-request or via environment:

```bash
# Via environment
CC_CLAUDE_MODEL=claude-opus-4-20250514 npm start

# Via request body (Claude Code passes model in request)
# The proxy uses whatever model the client specifies
```

**Available Models:**
- `claude-sonnet-4-20250514` (default) - Fast, capable
- `claude-opus-4-20250514` - Most capable, slower
- `claude-3-5-sonnet-20241022` - Previous generation

## Proxy Comparison

| Proxy | Port | Target | Translation | Use Case |
|-------|------|--------|-------------|----------|
| CG-Flash | 2405 | Gemini Flash | Anthropic <-> Google AI | L5 workers, fast tasks |
| CG-Pro | 2406 | Gemini Pro | Anthropic <-> Google AI | L3/L4 QA, consensus |
| CG-Image | 2407 | Gemini Image | Anthropic <-> Google AI | Image generation |
| **CC-Claude** | **2408** | **Anthropic** | **None (pass-through)** | **Reasoning from any agent** |

## Troubleshooting

### API Key Not Set

```
ERROR: ANTHROPIC_API_KEY not set.
```

**Solution**: Set `ANTHROPIC_API_KEY` in `.env` or export as environment variable.

### Port Already in Use

```
Error: listen EADDRINUSE: address already in use :::2408
```

**Solution**: Change port in `.env`:
```bash
CC_CLAUDE_PORT=2409
```

Or kill the process:
```bash
lsof -ti:2408 | xargs kill
```

### Rate Limits

If you hit Anthropic rate limits, the proxy forwards the error response:

```json
{
  "type": "error",
  "error": {
    "type": "rate_limit_error",
    "message": "Rate limit exceeded"
  }
}
```

**Solution**: Implement backoff in your calling agent, or upgrade your Anthropic plan.

## License

MIT
