#!/bin/bash
# H-Claude Setup Script
# Run this once after cloning the template

set -e

echo "=== H-Claude Setup ==="
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is required but not installed."
    echo "Install from: https://nodejs.org/"
    exit 1
fi

echo "Node.js: $(node --version)"

# Check Claude CLI
if ! command -v claude &> /dev/null; then
    echo "WARNING: Claude CLI not found. Install from: https://claude.ai/code"
else
    echo "Claude CLI: Found"
fi

echo ""

# Install proxy dependencies
echo "Installing proxy dependencies..."
for dir in HC-Proxies/CG-Flash HC-Proxies/CG-Pro HC-Proxies/CC-Claude HC-Proxies/CG-Image; do
    if [ -d "$dir" ]; then
        echo "  $dir..."
        (cd "$dir" && npm install --silent 2>/dev/null || npm install)
    fi
done

echo ""

# Copy .env.example files if .env doesn't exist
echo "Checking .env files..."
for dir in HC-Proxies/CG-Flash HC-Proxies/CG-Pro HC-Proxies/CC-Claude HC-Proxies/CG-Image; do
    if [ -f "$dir/.env.example" ] && [ ! -f "$dir/.env" ]; then
        cp "$dir/.env.example" "$dir/.env"
        echo "  Created $dir/.env (needs API key)"
    elif [ -f "$dir/.env" ]; then
        echo "  $dir/.env exists"
    fi
done

echo ""

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Make scripts executable
chmod +x "$SCRIPT_DIR/start-proxies.sh" "$SCRIPT_DIR/stop-proxies.sh" 2>/dev/null || true
chmod +x "$PROJECT_ROOT/hc-init" 2>/dev/null || true

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit HC-Proxies/CG-Flash/.env - add GOOGLE_AI_API_KEY"
echo "  2. Edit HC-Proxies/CG-Pro/.env - add GOOGLE_AI_API_KEY"
echo "  3. Run: .claude/scripts/start-proxies.sh"
echo "  4. Run: claude"
echo ""
