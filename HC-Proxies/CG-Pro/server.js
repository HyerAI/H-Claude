/**
 * CG-Pro - Claude Gateway for Gemini Pro
 *
 * Routes Claude Code (Anthropic API format) to Google AI Gemini Pro.
 * Translates request/response formats between Anthropic and Google AI APIs.
 */

const express = require('express');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Load .env file if exists (simple loader, no dependencies)
const envPath = path.join(__dirname, '.env');
if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf-8');
    envContent.split('\n').forEach(line => {
        const [key, ...valueParts] = line.split('=');
        if (key && valueParts.length > 0) {
            const value = valueParts.join('=').trim();
            if (!process.env[key.trim()]) {
                process.env[key.trim()] = value;
            }
        }
    });
}

// Configuration
const GOOGLE_AI_API_KEY = process.env.GOOGLE_AI_API_KEY;
if (!GOOGLE_AI_API_KEY || GOOGLE_AI_API_KEY === 'your-google-ai-key-here') {
    console.error('ERROR: GOOGLE_AI_API_KEY not set.');
    console.error('  Set in .env file or export GOOGLE_AI_API_KEY=your-key-here');
    process.exit(1);
}

const DEFAULT_MODEL = process.env.CG_PRO_MODEL || 'gemini-3-pro';
const PORT = process.env.CG_PRO_PORT || 2406;

const app = express();
app.use(express.json({ limit: '50mb' }));

// Logging utility
const log = (level, message) => {
    const timestamp = new Date().toISOString();
    const prefix = { info: 'INFO', warn: 'WARN', error: 'ERROR' }[level] || 'LOG';
    console.log(`[${timestamp}] [${prefix}] ${message}`);
};

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        version: '1.0.0',
        model: DEFAULT_MODEL,
        port: PORT,
        api_key_configured: !!GOOGLE_AI_API_KEY
    });
});

/**
 * Shared handler for both Anthropic and OpenAI style requests
 * @param {Object} req - Express request
 * @param {Object} res - Express response
 * @param {String} style - 'anthropic' or 'openai'
 */
async function handleCompletionRequest(req, res, style) {
    const { model, messages, max_tokens = 8192, temperature = 1.0 } = req.body;

    log('info', `[${style}] Received request: ${messages.length} messages, max_tokens: ${max_tokens}`);

    try {
        // Translate Anthropic/OpenAI format to Google AI format
        const googleRequest = translateToGoogleAI(messages, max_tokens, temperature);

        // Send to Google AI API
        const targetModel = model || DEFAULT_MODEL;
        const googleResponse = await callGoogleAI(targetModel, googleRequest);

        // Translate response back to requested format
        const formattedResponse = style === 'anthropic'
            ? translateToAnthropicFormat(googleResponse, targetModel)
            : translateToOpenAIFormat(googleResponse, targetModel);

        res.json(formattedResponse);
    } catch (error) {
        log('error', `Request failed: ${error.message}`);

        // Return error in requested format
        const errorResponse = style === 'anthropic'
            ? {
                type: 'error',
                error: {
                    type: 'api_error',
                    message: error.response?.data?.error?.message || error.message
                }
            }
            : {
                error: {
                    type: 'api_error',
                    message: error.response?.data?.error?.message || error.message
                }
            };

        res.status(error.response?.status || 500).json(errorResponse);
    }
}

// Anthropic-style endpoint (primary - what Claude Code uses)
app.post('/v1/messages', async (req, res) => {
    await handleCompletionRequest(req, res, 'anthropic');
});

// OpenAI-style endpoint (for compatibility)
app.post('/v1/chat/completions', async (req, res) => {
    await handleCompletionRequest(req, res, 'openai');
});

// Translate Anthropic/OpenAI messages to Google AI format
function translateToGoogleAI(messages, maxTokens, temperature) {
    const contents = [];
    let systemInstruction = null;

    for (const msg of messages) {
        if (msg.role === 'system') {
            // Extract system message for systemInstruction
            systemInstruction = {
                parts: [{ text: msg.content }]
            };
        } else {
            // Map roles: user → user, assistant → model
            const role = msg.role === 'assistant' ? 'model' : 'user';
            contents.push({
                role: role,
                parts: [{ text: msg.content }]
            });
        }
    }

    const request = {
        contents: contents,
        generationConfig: {
            maxOutputTokens: maxTokens,
            temperature: temperature
        }
    };

    if (systemInstruction) {
        request.systemInstruction = systemInstruction;
    }

    return request;
}

// Call Google AI API
async function callGoogleAI(model, requestBody) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;

    log('info', `Calling Google AI: ${model}`);

    const response = await axios.post(url, requestBody, {
        params: { key: GOOGLE_AI_API_KEY },
        headers: { 'Content-Type': 'application/json' },
        timeout: 120000 // 2 minute timeout
    });

    return response.data;
}

/**
 * Translate Google AI response to Anthropic format
 * Format: { id, type: "message", role: "assistant", content: [{type: "text", text: "..."}], model, stop_reason, usage }
 */
function translateToAnthropicFormat(googleResponse, model) {
    // Extract text from Google AI response
    const candidate = googleResponse.candidates?.[0];
    const text = candidate?.content?.parts?.[0]?.text || '';

    // Map finish reason (Google AI → Anthropic)
    const finishReasonMap = {
        'STOP': 'end_turn',
        'MAX_TOKENS': 'max_tokens',
        'SAFETY': 'stop_sequence',
        'RECITATION': 'stop_sequence',
        'OTHER': 'end_turn'
    };
    const stopReason = finishReasonMap[candidate?.finishReason] || 'end_turn';

    // Extract token usage
    const usage = googleResponse.usageMetadata || {};

    return {
        id: `msg-${Date.now()}`,
        type: 'message',
        role: 'assistant',
        content: [{
            type: 'text',
            text: text
        }],
        model: model,
        stop_reason: stopReason,
        stop_sequence: null,
        usage: {
            input_tokens: usage.promptTokenCount || 0,
            output_tokens: usage.candidatesTokenCount || 0
        }
    };
}

/**
 * Translate Google AI response to OpenAI format
 * Format: { id, object: "chat.completion", choices: [{message: {role, content}, finish_reason}], usage }
 */
function translateToOpenAIFormat(googleResponse, model) {
    // Extract text from Google AI response
    const candidate = googleResponse.candidates?.[0];
    const content = candidate?.content?.parts?.[0]?.text || '';

    // Map finish reason (Google AI → OpenAI)
    const finishReasonMap = {
        'STOP': 'stop',
        'MAX_TOKENS': 'length',
        'SAFETY': 'content_filter',
        'RECITATION': 'content_filter',
        'OTHER': 'stop'
    };
    const finishReason = finishReasonMap[candidate?.finishReason] || 'stop';

    // Extract token usage
    const usage = googleResponse.usageMetadata || {};

    return {
        id: `chatcmpl-${Date.now()}`,
        object: 'chat.completion',
        created: Math.floor(Date.now() / 1000),
        model: model,
        choices: [{
            index: 0,
            message: {
                role: 'assistant',
                content: content
            },
            finish_reason: finishReason
        }],
        usage: {
            prompt_tokens: usage.promptTokenCount || 0,
            completion_tokens: usage.candidatesTokenCount || 0,
            total_tokens: usage.totalTokenCount || 0
        }
    };
}

// Start server
app.listen(PORT, () => {
    log('info', `CG-Pro started on http://localhost:${PORT}`);
    log('info', `Target model: ${DEFAULT_MODEL}`);
    log('info', `Endpoints: POST /v1/messages (Anthropic), POST /v1/chat/completions (OpenAI)`);
    log('info', `API key configured: ${GOOGLE_AI_API_KEY ? 'Yes' : 'No'}`);
});
