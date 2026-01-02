---
version: V1.0.0
status: current
timestamp: 2025-12-14
tags: [readme, proxy, documentation, gemini]
description: "CG-Pro comprehensive documentation for Gemini gateway API translation, configuration, and endpoints."
---





# CG-Pro - Claude Gateway for Gemini Pro

Routes Claude Code (Anthropic API format) requests to Google AI Gemini Pro.

## Overview

CG-Pro translates between Anthropic/OpenAI API format and Google AI API format, allowing Claude Code to use Gemini Pro models for simple coding tasks.

## Features

- **Anthropic/OpenAI API compatibility**: Drop-in replacement for Claude Code
- **Google AI translation**: Automatic request/response format conversion
- **Zero external dependencies**: Only Express and Axios
- **Simple configuration**: Single .env file

## Installation

```bash
cd mf-agents/CG-Pro
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
CG_PRO_MODEL=gemini-3-pro    # Default model
CG_PRO_PORT=2406              # Default port
```

## Usage

### Start the Server

```bash
npm start
```

Server starts on `http://localhost:2406`

### Health Check

```bash
curl http://localhost:2406/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model": "gemini-3-pro",
  "port": 2406,
  "api_key_configured": true
}
```

### Use with Claude Code

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude -p "Write a hello world function in Python"
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
  "model": "gemini-3-pro",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 20
  }
}
```

**Translated to OpenAI format:**
```json
{
  "id": "chatcmpl-1234567890",
  "object": "chat.completion",
  "model": "gemini-3-pro",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help?"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### Finish Reason Mapping

| Google AI | Anthropic | OpenAI |
|-----------|-----------|--------|
| STOP | end_turn | stop |
| MAX_TOKENS | max_tokens | length |
| SAFETY | stop_sequence | content_filter |
| RECITATION | stop_sequence | content_filter |
| OTHER | end_turn | stop |

## Role Mapping

| Anthropic Role | Google AI Role |
|----------------|----------------|
| system | systemInstruction |
| user | user |
| assistant | model |

## Error Handling

Errors from Google AI API are translated to Anthropic error format:

```json
{
  "error": {
    "type": "api_error",
    "message": "Error details from Google AI"
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
  "model": "gemini-3-pro",
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
  "model": "gemini-3-pro",
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
  CG-Pro (port 2406)
      ↓
  Google AI API (Gemini Pro)
      ↓
  CG-Pro (translate response)
      ↓
Claude Code ← Anthropic API format
```

## Troubleshooting

### API Key Not Set

```
ERROR: GOOGLE_AI_API_KEY not set.
```

**Solution**: Set `GOOGLE_AI_API_KEY` in `.env` file or export as environment variable.

### Port Already in Use

```
Error: listen EADDRINUSE: address already in use :::2406
```

**Solution**: Change port in `.env`:
```bash
CG_PRO_PORT=2407
```

Or kill the process using port 2406:
```bash
lsof -ti:2406 | xargs kill
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

## License

MIT
