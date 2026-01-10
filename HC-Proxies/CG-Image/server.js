/**
 * KS-Image - Kaprekar Image Generation Router
 *
 * Routes Claude Code / Anthropic API requests to Gemini Image Generation.
 * Translates Anthropic/OpenAI format → Google AI API format.
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

// Configuration - Image uses dedicated key
const GOOGLE_API_KEY = process.env.GOOGLE_API_KEY_IMAGE || process.env.GOOGLE_API_KEY;
if (!GOOGLE_API_KEY) {
    console.error('ERROR: GOOGLE_API_KEY_IMAGE not set in HC-Proxies/.env');
    process.exit(1);
}

const PORT = process.env.CG_IMAGE_PORT || process.env.IMAGE_PROXY_PORT || 2407;
const GEMINI_MODEL = 'gemini-3-pro';
const GEMINI_ENDPOINT = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

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
        model: GEMINI_MODEL,
        port: PORT
    });
});

/**
 * Translate Anthropic/OpenAI message format to Google AI format
 *
 * Role mapping:
 * - system → systemInstruction
 * - user → user
 * - assistant → model
 */
function translateToGeminiFormat(messages) {
    let systemInstruction = null;
    const contents = [];

    for (const msg of messages) {
        if (msg.role === 'system') {
            // System messages become systemInstruction
            systemInstruction = { parts: [{ text: msg.content }] };
        } else {
            // Map roles: user → user, assistant → model
            const role = msg.role === 'assistant' ? 'model' : 'user';
            contents.push({
                role: role,
                parts: [{ text: msg.content }]
            });
        }
    }

    return { systemInstruction, contents };
}

/**
 * Convert Gemini response with image to markdown format
 * Handles base64 inlineData → markdown image
 */
function formatGeminiResponse(geminiResponse) {
    const candidates = geminiResponse.candidates || [];
    if (candidates.length === 0) {
        return { text: '', images: [] };
    }

    const parts = candidates[0].content?.parts || [];
    let textContent = '';
    const images = [];

    for (const part of parts) {
        if (part.text) {
            textContent += part.text;
        }
        if (part.inlineData) {
            // Convert base64 image to data URL markdown
            const mimeType = part.inlineData.mimeType || 'image/png';
            const base64Data = part.inlineData.data;
            const dataUrl = `data:${mimeType};base64,${base64Data}`;
            images.push({
                mimeType,
                dataUrl,
                markdown: `![Generated Image](${dataUrl})`
            });
        }
    }

    return { text: textContent, images };
}

/**
 * Main proxy endpoint - Anthropic/OpenAI format
 * POST /v1/messages (Anthropic style)
 * POST /v1/chat/completions (OpenAI style)
 */
async function handleImageRequest(req, res) {
    const { messages, max_tokens = 8192 } = req.body;

    if (!messages || !Array.isArray(messages)) {
        return res.status(400).json({
            error: 'Invalid request',
            details: 'messages array is required'
        });
    }

    log('info', `Image generation request: ${messages.length} messages`);

    try {
        // Translate to Gemini format
        const { systemInstruction, contents } = translateToGeminiFormat(messages);

        // Build Gemini request
        const geminiRequest = {
            contents,
            generationConfig: {
                maxOutputTokens: max_tokens,
                responseModalities: ['TEXT', 'IMAGE']
            }
        };

        if (systemInstruction) {
            geminiRequest.systemInstruction = systemInstruction;
        }

        log('info', `Sending to Gemini: ${GEMINI_MODEL}`);

        // Call Gemini API
        const response = await axios.post(
            `${GEMINI_ENDPOINT}?key=${GOOGLE_API_KEY}`,
            geminiRequest,
            {
                headers: { 'Content-Type': 'application/json' },
                timeout: 120000 // 2 minute timeout for image generation
            }
        );

        // Format response
        const { text, images } = formatGeminiResponse(response.data);

        // Build combined response text
        let responseText = text;
        if (images.length > 0) {
            responseText += '\n\n' + images.map(img => img.markdown).join('\n\n');
        }

        // Return in Anthropic/OpenAI compatible format
        const formattedResponse = {
            id: `img-${Date.now()}`,
            type: 'message',
            role: 'assistant',
            content: [{ type: 'text', text: responseText }],
            model: GEMINI_MODEL,
            stop_reason: 'end_turn',
            usage: {
                input_tokens: response.data.usageMetadata?.promptTokenCount || 0,
                output_tokens: response.data.usageMetadata?.candidatesTokenCount || 0
            },
            // Include raw image data for clients that want it
            _images: images.map(img => ({
                mimeType: img.mimeType,
                data: img.dataUrl
            }))
        };

        log('info', `Response: ${text.length} chars text, ${images.length} images`);
        res.json(formattedResponse);

    } catch (error) {
        const errorMsg = error.response?.data?.error?.message || error.message;
        log('error', `Gemini API failed: ${errorMsg}`);

        res.status(error.response?.status || 500).json({
            error: 'Image generation failed',
            details: errorMsg,
            model: GEMINI_MODEL
        });
    }
}

// Anthropic-style endpoint
app.post('/v1/messages', handleImageRequest);

// OpenAI-style endpoint (for compatibility)
app.post('/v1/chat/completions', handleImageRequest);

// Simple generate endpoint
app.post('/generate', async (req, res) => {
    const { prompt, system } = req.body;

    if (!prompt) {
        return res.status(400).json({ error: 'prompt is required' });
    }

    // Convert simple prompt to messages format
    const messages = [];
    if (system) {
        messages.push({ role: 'system', content: system });
    }
    messages.push({ role: 'user', content: prompt });

    req.body.messages = messages;
    return handleImageRequest(req, res);
});

// Start server
app.listen(PORT, () => {
    log('info', `CG-Image started on http://localhost:${PORT}`);
    log('info', `Model: ${GEMINI_MODEL}`);
    log('info', `Endpoints: POST /v1/messages, POST /v1/chat/completions, POST /generate`);
});
