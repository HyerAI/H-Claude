/**
 * HC-Orca - Light Coordination Proxy (Google AI)
 *
 * Routes to Gemini Flash for straightforward orchestration.
 * Used by: Orchestrator (hc-execute, hc-glass, red-team)
 */

const express = require('express');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Load env files: shared first, then local for overrides
function loadEnv(envPath) {
    if (fs.existsSync(envPath)) {
        fs.readFileSync(envPath, 'utf-8').split('\n').forEach(line => {
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
}

loadEnv(path.join(__dirname, '..', '.env'));  // Shared config
loadEnv(path.join(__dirname, '.env'));         // Local overrides

// Use primary key (Flash orchestrators use primary)
const GOOGLE_AI_API_KEY = process.env.GOOGLE_AI_API_KEY_PRIMARY || process.env.GOOGLE_AI_API_KEY;
if (!GOOGLE_AI_API_KEY) {
    console.error('ERROR: GOOGLE_AI_API_KEY_PRIMARY not set in HC-Proxies/.env');
    process.exit(1);
}

const DEFAULT_MODEL = process.env.MODEL_FLASH || process.env.HC_ORCA_MODEL || 'gemini-2.5-flash-preview-05-20';
const PORT = process.env.HC_ORCA_PORT || 2414;

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

app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        version: '1.0.0',
        proxy: 'HC-Orca',
        model: DEFAULT_MODEL,
        port: PORT,
        purpose: 'Light coordination (execute, glass, red-team)'
    });
});

async function handleCompletionRequest(req, res, style) {
    const { model, messages, max_tokens = 8192, temperature = 1.0 } = req.body;
    log('info', `[${style}] Request: ${messages.length} messages`);

    try {
        const googleRequest = translateToGoogleAI(messages, max_tokens, temperature);
        // Always use our configured Gemini model, ignore Claude model name from client
        const targetModel = DEFAULT_MODEL;
        const googleResponse = await callGoogleAI(targetModel, googleRequest);
        const response = style === 'anthropic'
            ? translateToAnthropicFormat(googleResponse, targetModel)
            : translateToOpenAIFormat(googleResponse, targetModel);
        res.json(response);
    } catch (error) {
        log('error', `Request failed: ${error.message}`);
        const errorResponse = style === 'anthropic'
            ? { type: 'error', error: { type: 'api_error', message: error.response?.data?.error?.message || error.message } }
            : { error: { type: 'api_error', message: error.response?.data?.error?.message || error.message } };
        res.status(error.response?.status || 500).json(errorResponse);
    }
}

app.post('/v1/messages', async (req, res) => { await handleCompletionRequest(req, res, 'anthropic'); });
app.post('/v1/chat/completions', async (req, res) => { await handleCompletionRequest(req, res, 'openai'); });

function translateToGoogleAI(messages, maxTokens, temperature) {
    const contents = [];
    let systemInstruction = null;
    for (const msg of messages) {
        if (msg.role === 'system') {
            systemInstruction = { parts: [{ text: msg.content }] };
        } else {
            contents.push({ role: msg.role === 'assistant' ? 'model' : 'user', parts: [{ text: msg.content }] });
        }
    }
    const request = { contents, generationConfig: { maxOutputTokens: maxTokens, temperature } };
    if (systemInstruction) request.systemInstruction = systemInstruction;
    return request;
}

async function callGoogleAI(model, requestBody) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;
    log('info', `Calling Google AI: ${model}`);
    const response = await axios.post(url, requestBody, {
        params: { key: GOOGLE_AI_API_KEY },
        headers: { 'Content-Type': 'application/json' },
        timeout: 120000
    });
    return response.data;
}

function translateToAnthropicFormat(googleResponse, model) {
    const candidate = googleResponse.candidates?.[0];
    const text = candidate?.content?.parts?.[0]?.text || '';
    const usage = googleResponse.usageMetadata || {};
    return {
        id: `msg-${Date.now()}`, type: 'message', role: 'assistant',
        content: [{ type: 'text', text }], model,
        stop_reason: candidate?.finishReason === 'MAX_TOKENS' ? 'max_tokens' : 'end_turn',
        usage: { input_tokens: usage.promptTokenCount || 0, output_tokens: usage.candidatesTokenCount || 0 }
    };
}

function translateToOpenAIFormat(googleResponse, model) {
    const candidate = googleResponse.candidates?.[0];
    const content = candidate?.content?.parts?.[0]?.text || '';
    const usage = googleResponse.usageMetadata || {};
    return {
        id: `chatcmpl-${Date.now()}`, object: 'chat.completion', created: Math.floor(Date.now() / 1000), model,
        choices: [{ index: 0, message: { role: 'assistant', content }, finish_reason: 'stop' }],
        usage: { prompt_tokens: usage.promptTokenCount || 0, completion_tokens: usage.candidatesTokenCount || 0, total_tokens: usage.totalTokenCount || 0 }
    };
}

app.listen(PORT, () => {
    log('info', `HC-Orca started on http://localhost:${PORT}`);
    log('info', `Model: ${DEFAULT_MODEL}`);
    log('info', `Purpose: Light coordination (execute, glass, red-team)`);
});
