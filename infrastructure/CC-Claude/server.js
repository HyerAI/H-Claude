/**
 * CC-Claude - Claude Code CLI Proxy
 *
 * Spawns Claude Code CLI for requests, enabling subscription-based access
 * (Claude Max/Pro) instead of API key access.
 *
 * Key difference from API proxy:
 * - Uses `claude -p "prompt" --output-format json` subprocess
 * - No ANTHROPIC_API_KEY required (uses local CLI authentication)
 * - Works with Claude subscription plans
 */

const express = require('express');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Load .env file if exists
const envPath = path.join(__dirname, '.env');
if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf-8');
    envContent.split('\n').forEach(line => {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) return;
        const [key, ...valueParts] = trimmed.split('=');
        if (key && valueParts.length > 0) {
            const value = valueParts.join('=').trim();
            if (!process.env[key.trim()]) {
                process.env[key.trim()] = value;
            }
        }
    });
}

// Configuration
const DEFAULT_MODEL = process.env.CC_CLAUDE_MODEL || 'opus';
const PORT = process.env.CC_CLAUDE_PORT || 2408;
const TIMEOUT_MS = parseInt(process.env.CC_CLAUDE_TIMEOUT || '300000', 10); // 5 min default

const app = express();
app.use(express.json({ limit: '50mb' }));

// Logging utility
const log = (level, message) => {
    const timestamp = new Date().toISOString();
    const prefix = { info: 'INFO', warn: 'WARN', error: 'ERROR' }[level] || 'LOG';
    console.log(`[${timestamp}] [${prefix}] ${message}`);
};

/**
 * Execute Claude CLI command and return parsed result
 */
async function runClaudeCli(prompt, options = {}) {
    const { model = DEFAULT_MODEL, systemPrompt = null, maxTokens = null } = options;

    const args = [
        '-p', prompt,
        '--output-format', 'json',
        '--model', model,
        '--dangerously-skip-permissions'  // Required for non-interactive use
    ];

    if (systemPrompt) {
        args.push('--system-prompt', systemPrompt);
    }

    // Note: Claude CLI doesn't have max_tokens flag - it uses model defaults
    // The --max-turns flag is for conversation turns, not tokens

    log('info', `[cli] Spawning: claude ${args.slice(0, 4).join(' ')}... (model=${model})`);

    return new Promise((resolve, reject) => {
        let stdout = '';
        let stderr = '';

        const proc = spawn('claude', args, {
            timeout: TIMEOUT_MS,
            env: { ...process.env },
            cwd: '/tmp',  // Run from /tmp to avoid loading project CLAUDE.md context
            stdio: ['ignore', 'pipe', 'pipe']  // Detach stdin to prevent hanging
        });

        proc.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        proc.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        proc.on('close', (code) => {
            if (code !== 0) {
                log('error', `[cli] Exit code ${code}: ${stderr}`);
                reject(new Error(`Claude CLI exited with code ${code}: ${stderr}`));
                return;
            }

            try {
                // Parse JSON output from CLI
                const result = JSON.parse(stdout);
                log('info', `[cli] Success: session_id=${result.session_id || 'none'}`);
                resolve(result);
            } catch (parseErr) {
                // Sometimes output has extra content before JSON
                const jsonMatch = stdout.match(/\{[\s\S]*\}$/);
                if (jsonMatch) {
                    try {
                        const result = JSON.parse(jsonMatch[0]);
                        resolve(result);
                        return;
                    } catch (e) {
                        // Fall through to error
                    }
                }
                log('error', `[cli] Failed to parse output: ${parseErr.message}`);
                reject(new Error(`Failed to parse CLI output: ${stdout.substring(0, 200)}`));
            }
        });

        proc.on('error', (err) => {
            log('error', `[cli] Spawn error: ${err.message}`);
            reject(err);
        });
    });
}

/**
 * Convert Anthropic messages format to a single prompt string
 */
function messagesToPrompt(messages) {
    return messages.map(msg => {
        const role = msg.role === 'assistant' ? 'Assistant' : 'Human';
        const content = typeof msg.content === 'string'
            ? msg.content
            : msg.content.map(c => c.text || '').join('\n');
        return `${role}: ${content}`;
    }).join('\n\n');
}

/**
 * Convert CLI result to Anthropic API response format
 */
function cliResultToAnthropicFormat(cliResult, model) {
    // CLI returns: { result: "...", session_id: "...", ... }
    const responseText = cliResult.result || cliResult.response || '';

    return {
        id: `msg_${cliResult.session_id || Date.now()}`,
        type: 'message',
        role: 'assistant',
        content: [{
            type: 'text',
            text: responseText
        }],
        model: model,
        stop_reason: 'end_turn',
        usage: {
            input_tokens: cliResult.input_tokens || 0,
            output_tokens: cliResult.output_tokens || 0
        }
    };
}

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        version: '2.0.0',
        mode: 'cli',  // Changed from 'api'
        model: DEFAULT_MODEL,
        port: PORT,
        description: 'CLI-based proxy (subscription mode)'
    });
});

/**
 * Anthropic Messages API endpoint
 * Translates to CLI call, returns Anthropic format
 */
app.post('/v1/messages', async (req, res) => {
    const { model, messages, system, max_tokens } = req.body;

    const effectiveModel = model || DEFAULT_MODEL;

    // Convert messages array to prompt string
    const prompt = messagesToPrompt(messages || []);

    log('info', `[anthropic] Request: model=${effectiveModel}, messages=${messages?.length || 0}`);

    try {
        const cliResult = await runClaudeCli(prompt, {
            model: effectiveModel,
            systemPrompt: system,
            maxTokens: max_tokens
        });

        const response = cliResultToAnthropicFormat(cliResult, effectiveModel);
        log('info', `[anthropic] Response: ${response.content[0]?.text?.substring(0, 50)}...`);
        res.json(response);

    } catch (error) {
        log('error', `[anthropic] Error: ${error.message}`);
        res.status(500).json({
            type: 'error',
            error: {
                type: 'api_error',
                message: error.message
            }
        });
    }
});

/**
 * OpenAI-style compatibility endpoint
 */
app.post('/v1/chat/completions', async (req, res) => {
    const { model, messages, max_tokens = 8192 } = req.body;

    log('info', `[openai-compat] Request: ${messages?.length || 0} messages`);

    try {
        // Extract system prompt and convert messages
        let systemPrompt = null;
        const chatMessages = [];

        for (const msg of messages || []) {
            if (msg.role === 'system') {
                systemPrompt = msg.content;
            } else {
                chatMessages.push({
                    role: msg.role === 'assistant' ? 'assistant' : 'user',
                    content: msg.content
                });
            }
        }

        const prompt = messagesToPrompt(chatMessages);
        const effectiveModel = model || DEFAULT_MODEL;

        const cliResult = await runClaudeCli(prompt, {
            model: effectiveModel,
            systemPrompt: systemPrompt,
            maxTokens: max_tokens
        });

        // Convert to OpenAI format
        const responseText = cliResult.result || cliResult.response || '';

        const openaiResponse = {
            id: `chatcmpl-${cliResult.session_id || Date.now()}`,
            object: 'chat.completion',
            created: Math.floor(Date.now() / 1000),
            model: effectiveModel,
            choices: [{
                index: 0,
                message: {
                    role: 'assistant',
                    content: responseText
                },
                finish_reason: 'stop'
            }],
            usage: {
                prompt_tokens: cliResult.input_tokens || 0,
                completion_tokens: cliResult.output_tokens || 0,
                total_tokens: (cliResult.input_tokens || 0) + (cliResult.output_tokens || 0)
            }
        };

        res.json(openaiResponse);

    } catch (error) {
        log('error', `[openai-compat] Error: ${error.message}`);
        res.status(500).json({
            error: {
                type: 'api_error',
                message: error.message
            }
        });
    }
});

// Start server
app.listen(PORT, () => {
    log('info', `CC-Claude (CLI mode) started on http://localhost:${PORT}`);
    log('info', `Default model: ${DEFAULT_MODEL}`);
    log('info', `Mode: CLI subprocess (subscription-based, no API key required)`);
    log('info', `Endpoints: POST /v1/messages, POST /v1/chat/completions`);
});
