# CG-Pro Quick Start Guide

## What is CG-Pro?

CG-Pro routes Claude Code requests to Google AI's Gemini Pro, translating between Anthropic API format and Google AI format.

## Setup (One-Time)

1. **Install dependencies:**
   ```bash
   cd HC-Proxies/CG-Pro
   npm install
   ```

2. **Configure API key:**
   ```bash
   cp .env.example .env
   # Edit .env and set your GOOGLE_AI_API_KEY
   ```

3. **Start the server:**
   ```bash
   npm start
   ```

   Or run in background:
   ```bash
   nohup node server.js > cg-pro.log 2>&1 &
   ```

## Usage with Claude Code

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude -p "Your task"
```

## Health Check

```bash
curl http://localhost:2406/health
```

## Stop Server

```bash
lsof -ti:2406 | xargs kill
```

## Configuration

Edit `.env`:
```bash
GOOGLE_AI_API_KEY=your-key-here    # Required
CG_PRO_PORT=2406                    # Optional (default: 2406)
```

---

**Full documentation:** See `README.md`
