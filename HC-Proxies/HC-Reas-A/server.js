/**
 * HC-Reas-A - Heavy Reasoning Proxy (Claude CLI)
 *
 * Routes to Claude Opus for complex reasoning tasks.
 * Used by: Domain Expert, Writer roles in dialectic
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
const DEFAULT_MODEL = process.env.HC_REAS_A_MODEL || 'opus';
const PORT = process.env.HC_REAS_A_PORT || 2410;
const TIMEOUT_MS = parseInt(process.env.HC_REAS_A_TIMEOUT || '300000', 10);

const app = express();
app.use(express.json({ limit: '50mb' }));

// CORS for wiki status page
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type');
    if (req.method === 'OPTIONS') return res.sendStatus(200);
    next();
});

const log = (level, message) => {
    const timestamp = new Date().toISOString();
    const prefix = { info: 'INFO', warn: 'WARN', error: 'ERROR' }[level] || 'LOG';
    console.log(`[${timestamp}] [${prefix}] ${message}`);
};

async function runClaudeCli(prompt, options = {}) {
    const { model = DEFAULT_MODEL, systemPrompt = null, maxTokens = null } = options;

    const args = [
        '-p', prompt,
        '--output-format', 'json',
        '--model', model,
        '--dangerously-skip-permissions'
    ];

    if (systemPrompt) {
        args.push('--system-prompt', systemPrompt);
    }

    log('info', `[cli] Spawning: claude ${args.slice(0, 4).join(' ')}... (model=${model})`);

    return new Promise((resolve, reject) => {
        let stdout = '';
        let stderr = '';

        const proc = spawn('claude', args, {
            timeout: TIMEOUT_MS,
            env: { ...process.env },
            cwd: '/tmp',
            stdio: ['ignore', 'pipe', 'pipe']
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
                const result = JSON.parse(stdout);
                log('info', `[cli] Success: session_id=${result.session_id || 'none'}`);
                resolve(result);
            } catch (parseErr) {
                const jsonMatch = stdout.match(/\{[\s\S]*\}$/);
                if (jsonMatch) {
                    try {
                        const result = JSON.parse(jsonMatch[0]);
                        resolve(result);
                        return;
                    } catch (e) {}
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

function messagesToPrompt(messages) {
    return messages.map(msg => {
        const role = msg.role === 'assistant' ? 'Assistant' : 'Human';
        const content = typeof msg.content === 'string'
            ? msg.content
            : msg.content.map(c => c.text || '').join('\n');
        return `${role}: ${content}`;
    }).join('\n\n');
}

function cliResultToAnthropicFormat(cliResult, model) {
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

app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        version: '1.0.0',
        proxy: 'HC-Reas-A',
        mode: 'cli',
        model: DEFAULT_MODEL,
        port: PORT,
        purpose: 'Heavy reasoning (Claude Opus)'
    });
});

app.post('/v1/messages', async (req, res) => {
    const { model, messages, system, max_tokens } = req.body;
    const effectiveModel = model || DEFAULT_MODEL;
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
            error: { type: 'api_error', message: error.message }
        });
    }
});

app.post('/v1/chat/completions', async (req, res) => {
    const { model, messages, max_tokens = 8192 } = req.body;

    log('info', `[openai-compat] Request: ${messages?.length || 0} messages`);

    try {
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

        const responseText = cliResult.result || cliResult.response || '';

        res.json({
            id: `chatcmpl-${cliResult.session_id || Date.now()}`,
            object: 'chat.completion',
            created: Math.floor(Date.now() / 1000),
            model: effectiveModel,
            choices: [{
                index: 0,
                message: { role: 'assistant', content: responseText },
                finish_reason: 'stop'
            }],
            usage: {
                prompt_tokens: cliResult.input_tokens || 0,
                completion_tokens: cliResult.output_tokens || 0,
                total_tokens: (cliResult.input_tokens || 0) + (cliResult.output_tokens || 0)
            }
        });

    } catch (error) {
        log('error', `[openai-compat] Error: ${error.message}`);
        res.status(500).json({
            error: { type: 'api_error', message: error.message }
        });
    }
});

app.listen(PORT, () => {
    log('info', `HC-Reas-A (CLI mode) started on http://localhost:${PORT}`);
    log('info', `Default model: ${DEFAULT_MODEL}`);
    log('info', `Purpose: Heavy reasoning tasks (Domain Expert, Writer)`);
});
