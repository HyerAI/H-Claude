---
version: V1.0.0
status: current
timestamp: 2025-12-14
tags: [readme, proxy, documentation]
description: CG-Image server documentation for routing Claude Code requests to Gemini image generation API.
---





# CG-Image - Claude Gateway for Gemini Image

Routes Claude Code / Anthropic API requests to Gemini Image Generation.

## Quick Start

```bash
# Install dependencies
npm install

# Start server
npm start
```

Server runs on `http://localhost:2407`

## Configuration

Create `.env` file (copy from `.env.example`):

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| GOOGLE_AI_API_KEY_IMAGE | Yes | Google AI API key for Gemini 3 Pro Image. Get at: https://aistudio.google.com/apikey |
| IMAGE_PROXY_MODEL | No | Override default model (default: gemini-3-pro) |
| IMAGE_PROXY_PORT | No | Override default port (default: 2407) |

Example:
```
GOOGLE_AI_API_KEY_IMAGE=your-google-ai-key-here
IMAGE_PROXY_PORT=2407
IMAGE_PROXY_MODEL=gemini-3-pro
```

## API Endpoints

### POST /v1/messages (Anthropic-style)

```json
{
  "messages": [
    {"role": "system", "content": "You are an image generation assistant"},
    {"role": "user", "content": "Generate an image of a sunset over mountains"}
  ],
  "max_tokens": 8192
}
```

### POST /v1/chat/completions (OpenAI-style)

Same format as above.

### POST /generate (Simple)

```json
{
  "prompt": "Generate an image of a sunset over mountains",
  "system": "You are an image generation assistant"
}
```

### GET /health

Returns server status.

## Response Format

```json
{
  "id": "img-1733567890123",
  "type": "message",
  "role": "assistant",
  "content": [{"type": "text", "text": "Here's your image:\n\n![Generated Image](data:image/png;base64,...)"}],
  "model": "gemini-3-pro",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 50,
    "output_tokens": 1000
  },
  "_images": [{"mimeType": "image/png", "data": "data:image/png;base64,..."}]
}
```

## Role Mapping

| Input (Anthropic/OpenAI) | Output (Gemini) |
|--------------------------|-----------------|
| system | systemInstruction |
| user | user |
| assistant | model |

## Usage with Claude Code

```bash
# Point Claude Code to CG-Image
ANTHROPIC_API_BASE_URL=http://localhost:2407 claude -p "Generate an image of..."
```

## Model

Uses `gemini-3-pro` for image generation.
