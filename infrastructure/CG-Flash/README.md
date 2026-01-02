---
version: V2.0.0
status: current
timestamp: 2025-12-17
tags: [readme, proxy, documentation, gemini, gemini-flash]
description: "CG-Flash comprehensive documentation for Gemini Flash Preview gateway API translation, configuration, and endpoints."
---





# CG-Flash - Claude Gateway for Gemini Flash

Routes Claude Code (Anthropic API format) requests to Google AI Gemini Flash Preview.

## Overview

CG-Flash translates between Anthropic/OpenAI API format and Google AI API format, allowing Claude Code to use Gemini Flash Preview for L5 worker tasks (atomic implementation, documentation, simple coding).

## Features

- **Anthropic/OpenAI API compatibility**: Drop-in replacement for Claude Code
- **Google AI translation**: Automatic request/response format conversion
- **Zero external dependencies**: Only Express and Axios
- **Simple configuration**: Single .env file

## Installation

```bash
cd mf-agents/CG-Flash
npm install
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# Required
GOOGLE_AI_API_KEY=your-google-ai-key-here

# Optional
CG_FLASH_MODEL=gemini-3-flash-preview    # Default model
CG_FLASH_PORT=2405                        # Default port
```

**Note:** Uses same `GOOGLE_AI_API_KEY` as CG-Pro by default. Set a separate key if needed for quota management.

## Usage

### Start the Server

```bash
npm start
```

Server starts on `http://localhost:2405`

### Health Check

```bash
curl http://localhost:2405/health
```

Response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "model": "gemini-3-flash-preview",
  "port": 2405,
  "api_key_configured": true
}
```

### Use with Claude Code

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude -p "Write a hello world function in Python"
```

## API Translation

### Request (Anthropic/OpenAI → Google AI)

**Input (Anthropic format):**
```json
{
  "model": "claude-3-sonnet-20240229",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello"}
  ],
  "max_tokens": 1024
}
```

**Translated to Google AI:**
```json
{
  "contents": [
    {"role": "user", "parts": [{"text": "Hello"}]}
  ],
  "systemInstruction": {
    "parts": [{"text": "You are a helpful assistant"}]
  },
  "generationConfig": {
    "maxOutputTokens": 1024
  }
}
```

### Response (Google AI → Anthropic/OpenAI)

**Google AI Response:**
```json
{
  "candidates": [{
    "content": {
      "parts": [{"text": "Hello! How can I help?"}]
    },
    "finishReason": "STOP"
  }],
  "usageMetadata": {
    "promptTokenCount": 10,
    "candidatesTokenCount": 20,
    "totalTokenCount": 30
  }
}
```

**Translated to Anthropic format:**
```json
{
  "id": "msg-1234567890",
  "type": "message",
  "role": "assistant",
  "content": [{
    "type": "text",
    "text": "Hello! How can I help?"
  }],
  "model": "gemini-3-flash-preview",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 20
  }
}
```

## Endpoints

| Endpoint | Method | Purpose | Format |
|----------|--------|---------|--------|
| `/health` | GET | Health check with config info | - |
| `/v1/messages` | POST | **Primary endpoint** (Anthropic-style) | Anthropic Message API |
| `/v1/chat/completions` | POST | Compatibility endpoint (OpenAI-style) | OpenAI Chat Completions |

### Endpoint Details

**`/v1/messages` (Anthropic-style - RECOMMENDED)**

This is what Claude Code uses by default. Response format:

```json
{
  "id": "msg-1234567890",
  "type": "message",
  "role": "assistant",
  "content": [{"type": "text", "text": "Response text"}],
  "model": "gemini-3-flash-preview",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 20
  }
}
```

**`/v1/chat/completions` (OpenAI-style - for compatibility)**

Legacy endpoint for OpenAI-compatible clients. Response format:

```json
{
  "id": "chatcmpl-1234567890",
  "object": "chat.completion",
  "model": "gemini-3-flash-preview",
  "choices": [{
    "message": {"role": "assistant", "content": "Response text"},
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

## Architecture

```
Claude Code → Anthropic API format
      ↓
  CG-Flash (port 2405)
      ↓
  Google AI API (Gemini Flash Preview)
      ↓
  CG-Flash (translate response)
      ↓
Claude Code ← Anthropic API format
```

## Use Case: L5 Workers

CG-Flash is optimized for **L5 Worker** tasks in Kaprekar:
- Atomic implementation tasks
- Documentation generation
- Simple code generation
- File operations
- Infrastructure scripts

**Why Gemini Flash Preview?**
- **Speed**: Faster response times than Gemini Pro
- **Cost**: Lower cost per token
- **Quality**: Sufficient for well-defined worker tasks

## Troubleshooting

### API Key Not Set

```
ERROR: GOOGLE_AI_API_KEY not set.
```

**Solution**: Set `GOOGLE_AI_API_KEY` in `.env` file or export as environment variable.

### Port Already in Use

```
Error: listen EADDRINUSE: address already in use :::2405
```

**Solution**: Change port in `.env`:
```bash
CG_FLASH_PORT=2408
```

Or kill the process using port 2405:
```bash
lsof -ti:2405 | xargs kill
```

### Connection Refused

**Solution**: Ensure server is running:
```bash
npm start
```

## Development

Watch mode (auto-restart on changes):

```bash
npm run dev
```

## Migration from KIMI-K2

If upgrading from CG-Flash v1.x (KIMI-K2):

1. **Remove OpenRouter dependency**: No longer needed
2. **Update API key**: Change `OPENROUTER_API_KEY` → `GOOGLE_AI_API_KEY`
3. **New endpoints**: Now supports `/v1/messages` (Anthropic format)
4. **No config.json**: All configuration via `.env` or environment variables

## License

MIT
