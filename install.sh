#!/bin/bash
#
# H-Claude Global Installer
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/HyerAI/H-Claude/main/install.sh | bash
#
# What it does:
#   1. Creates ~/.claude/ directory structure
#   2. Clones proxy infrastructure to ~/.claude/infrastructure/
#   3. Installs proxy dependencies (npm install)
#   4. Creates helper scripts in ~/.claude/bin/
#   5. Caches workflow templates for /hc-init
#
# After install:
#   1. Add API keys to ~/.claude/infrastructure/*/.env
#   2. Run: ~/.claude/bin/start-proxies.sh
#   3. In your project: claude → /hc-init
#

set -e

# =============================================================================
# CONFIG
# =============================================================================

GITHUB_REPO="HyerAI/H-Claude"
GITHUB_BRANCH="main"
INSTALL_DIR="$HOME/.claude"
INFRASTRUCTURE_DIR="$INSTALL_DIR/infrastructure"
BIN_DIR="$INSTALL_DIR/bin"
TEMPLATE_DIR="$INSTALL_DIR/h-claude-template"
TEMP_DIR=$(mktemp -d)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# HELPERS
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

cleanup() {
    rm -rf "$TEMP_DIR"
}

trap cleanup EXIT

# =============================================================================
# CHECKS
# =============================================================================

check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing=0

    # Node.js
    if command -v node &> /dev/null; then
        local node_version=$(node --version)
        log_success "Node.js $node_version"
    else
        log_error "Node.js is required. Install from: https://nodejs.org/"
        missing=1
    fi

    # npm
    if command -v npm &> /dev/null; then
        log_success "npm $(npm --version)"
    else
        log_error "npm is required (comes with Node.js)"
        missing=1
    fi

    # git
    if command -v git &> /dev/null; then
        log_success "git $(git --version | cut -d' ' -f3)"
    else
        log_error "git is required"
        missing=1
    fi

    # curl
    if command -v curl &> /dev/null; then
        log_success "curl available"
    else
        log_error "curl is required"
        missing=1
    fi

    if [ $missing -eq 1 ]; then
        log_error "Missing prerequisites. Please install them and try again."
        exit 1
    fi

    echo ""
}

# =============================================================================
# INSTALLATION
# =============================================================================

create_directories() {
    log_info "Creating directory structure..."

    mkdir -p "$INFRASTRUCTURE_DIR"
    mkdir -p "$BIN_DIR"
    mkdir -p "$TEMPLATE_DIR"

    log_success "Created $INSTALL_DIR/"
}

download_repository() {
    log_info "Downloading H-Claude from GitHub..."

    cd "$TEMP_DIR"

    # Clone repository
    git clone --depth 1 --branch "$GITHUB_BRANCH" \
        "https://github.com/$GITHUB_REPO.git" h-claude \
        2>/dev/null || {
            log_error "Failed to clone repository"
            exit 1
        }

    log_success "Downloaded H-Claude"
}

install_infrastructure() {
    log_info "Installing proxy infrastructure..."

    local proxies=("CG-Flash" "CG-Pro" "CC-Claude")

    for proxy in "${proxies[@]}"; do
        local src="$TEMP_DIR/h-claude/infrastructure/$proxy"
        local dest="$INFRASTRUCTURE_DIR/$proxy"

        if [ -d "$src" ]; then
            # Copy proxy
            cp -r "$src" "$dest"

            # Install dependencies
            log_info "  Installing $proxy dependencies..."
            cd "$dest"
            npm install --silent 2>/dev/null || npm install

            # Create .env from example if needed
            if [ -f ".env.example" ] && [ ! -f ".env" ]; then
                cp .env.example .env
            fi

            log_success "  $proxy installed"
        fi
    done

    echo ""
}

install_workflow_templates() {
    log_info "Caching workflow templates..."

    local src="$TEMP_DIR/h-claude/.claude"

    # Copy workflow files (commands, agents, skills, templates)
    cp -r "$src/commands" "$TEMPLATE_DIR/" 2>/dev/null || true
    cp -r "$src/agents" "$TEMPLATE_DIR/" 2>/dev/null || true
    cp -r "$src/skills" "$TEMPLATE_DIR/" 2>/dev/null || true
    cp -r "$src/templates" "$TEMPLATE_DIR/" 2>/dev/null || true

    # Copy PM structure (SSoT only, not session artifacts)
    mkdir -p "$TEMPLATE_DIR/PM/SSoT/ADRs"
    mkdir -p "$TEMPLATE_DIR/PM/GIT"
    cp -r "$src/PM/SSoT/"* "$TEMPLATE_DIR/PM/SSoT/" 2>/dev/null || true
    cp -r "$src/PM/GIT/"* "$TEMPLATE_DIR/PM/GIT/" 2>/dev/null || true

    # Copy .example files as templates
    cp "$src/context.yaml.example" "$TEMPLATE_DIR/context.yaml" 2>/dev/null || true
    cp "$src/PM/CHANGELOG.md.example" "$TEMPLATE_DIR/PM/CHANGELOG.md" 2>/dev/null || true

    # Copy root files
    cp "$TEMP_DIR/h-claude/CLAUDE.md" "$TEMPLATE_DIR/" 2>/dev/null || true

    log_success "Workflow templates cached"
}

create_bin_scripts() {
    log_info "Creating helper scripts..."

    # start-proxies.sh
    cat > "$BIN_DIR/start-proxies.sh" << 'SCRIPT'
#!/bin/bash
# Start H-Claude proxy servers (global)

INFRASTRUCTURE_DIR="$HOME/.claude/infrastructure"
LOG_DIR="/tmp/h-claude"

mkdir -p "$LOG_DIR"

echo "=== Starting H-Claude Proxies ==="
echo ""

check_port() {
    lsof -ti:$1 > /dev/null 2>&1
}

# Start CG-Flash (2405)
if check_port 2405; then
    echo "CG-Flash (2405): Already running"
else
    cd "$INFRASTRUCTURE_DIR/CG-Flash"
    nohup npm start > "$LOG_DIR/cg-flash.log" 2>&1 &
    echo "CG-Flash (2405): Started (PID: $!)"
fi

# Start CG-Pro (2406)
if check_port 2406; then
    echo "CG-Pro (2406): Already running"
else
    cd "$INFRASTRUCTURE_DIR/CG-Pro"
    nohup npm start > "$LOG_DIR/cg-pro.log" 2>&1 &
    echo "CG-Pro (2406): Started (PID: $!)"
fi

# Start CC-Claude (2408)
if check_port 2408; then
    echo "CC-Claude (2408): Already running"
else
    cd "$INFRASTRUCTURE_DIR/CC-Claude"
    nohup npm start > "$LOG_DIR/cc-claude.log" 2>&1 &
    echo "CC-Claude (2408): Started (PID: $!)"
fi

echo ""
echo "Waiting for proxies to initialize..."
sleep 3

echo ""
echo "=== Health Check ==="

check_health() {
    local port=$1
    local name=$2
    if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "$name ($port): OK"
    else
        echo "$name ($port): FAILED"
    fi
}

check_health 2405 "CG-Flash"
check_health 2406 "CG-Pro"
check_health 2408 "CC-Claude"

echo ""
echo "Logs: $LOG_DIR/"
echo "Stop: ~/.claude/bin/stop-proxies.sh"
SCRIPT

    chmod +x "$BIN_DIR/start-proxies.sh"

    # stop-proxies.sh
    cat > "$BIN_DIR/stop-proxies.sh" << 'SCRIPT'
#!/bin/bash
# Stop H-Claude proxy servers

echo "=== Stopping H-Claude Proxies ==="
echo ""

stop_port() {
    local port=$1
    local name=$2
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill 2>/dev/null
        echo "$name ($port): Stopped"
    else
        echo "$name ($port): Not running"
    fi
}

stop_port 2405 "CG-Flash"
stop_port 2406 "CG-Pro"
stop_port 2408 "CC-Claude"

echo ""
echo "All proxies stopped."
SCRIPT

    chmod +x "$BIN_DIR/stop-proxies.sh"

    log_success "Created start-proxies.sh and stop-proxies.sh"
}

show_completion() {
    echo ""
    echo "=============================================="
    echo -e "${GREEN}H-Claude installed successfully!${NC}"
    echo "=============================================="
    echo ""
    echo "Installation directory: $INSTALL_DIR/"
    echo ""
    echo "Next steps:"
    echo ""
    echo "  1. Add your Google AI API key:"
    echo "     Edit: ~/.claude/infrastructure/CG-Flash/.env"
    echo "     Edit: ~/.claude/infrastructure/CG-Pro/.env"
    echo ""
    echo "  2. Start the proxies:"
    echo "     ~/.claude/bin/start-proxies.sh"
    echo ""
    echo "  3. In your project directory, run:"
    echo "     claude"
    echo "     /hc-init"
    echo ""
    echo "Get your API key at: https://aistudio.google.com/apikey"
    echo ""
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    echo ""
    echo "=============================================="
    echo "       H-Claude Global Installer"
    echo "=============================================="
    echo ""

    check_prerequisites
    create_directories
    download_repository
    install_infrastructure
    install_workflow_templates
    create_bin_scripts
    show_completion
}

main "$@"
