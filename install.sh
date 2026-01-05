#!/bin/bash
#
# H-Claude Global Installer
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/HyerAI/H-Claude/main/install.sh | bash
#
# What it does:
#   1. Creates ~/.claude/ directory structure
#   2. Clones HC-Proxies to ~/.claude/HC-Proxies/
#   3. Installs proxy dependencies (npm install)
#   4. Creates helper scripts in ~/.claude/bin/
#   5. Caches workflow templates for /hc-init
#
# After install:
#   1. Add API keys to ~/.claude/HC-Proxies/*/.env
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
HC_PROXIES_DIR="$INSTALL_DIR/HC-Proxies"
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

    # Optional: mkdocs for PM-View wiki
    echo ""
    log_info "Checking optional dependencies..."
    if command -v mkdocs &> /dev/null; then
        log_success "mkdocs $(mkdocs --version | cut -d' ' -f3)"
        MKDOCS_AVAILABLE=1
    else
        log_warn "mkdocs not installed (PM-View wiki unavailable)"
        log_info "  Install: pip install mkdocs-material"
        MKDOCS_AVAILABLE=0
    fi

    echo ""
}

# =============================================================================
# INSTALLATION
# =============================================================================

create_directories() {
    log_info "Creating directory structure..."

    mkdir -p "$HC_PROXIES_DIR"
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

install_hc_proxies() {
    log_info "Installing HC-Proxies..."

    local proxies=("CG-Flash" "CG-Pro" "CC-Claude")

    for proxy in "${proxies[@]}"; do
        local src="$TEMP_DIR/h-claude/HC-Proxies/$proxy"
        local dest="$HC_PROXIES_DIR/$proxy"

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

    # Copy docs (workflow documentation)
    cp -r "$src/docs" "$TEMPLATE_DIR/" 2>/dev/null || true

    # Copy PM structure (SSoT only, not session artifacts)
    mkdir -p "$TEMPLATE_DIR/PM/SSoT/ADRs"
    mkdir -p "$TEMPLATE_DIR/PM/GIT"
    mkdir -p "$TEMPLATE_DIR/PM/HC-LOG"
    cp -r "$src/PM/SSoT/"* "$TEMPLATE_DIR/PM/SSoT/" 2>/dev/null || true
    cp -r "$src/PM/GIT/"* "$TEMPLATE_DIR/PM/GIT/" 2>/dev/null || true
    cp -r "$src/PM/HC-LOG/"* "$TEMPLATE_DIR/PM/HC-LOG/" 2>/dev/null || true

    # Copy PM-View wiki structure
    if [ -d "$src/PM/PM-View" ]; then
        cp -r "$src/PM/PM-View" "$TEMPLATE_DIR/PM/" 2>/dev/null || true
        # Remove session-specific files, keep templates
        rm -rf "$TEMPLATE_DIR/PM/PM-View/.env" 2>/dev/null || true
        log_success "  PM-View wiki cached"
    fi

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

HC_PROXIES_DIR="$HOME/.claude/HC-Proxies"
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
    cd "$HC_PROXIES_DIR/CG-Flash"
    nohup npm start > "$LOG_DIR/cg-flash.log" 2>&1 &
    echo "CG-Flash (2405): Started (PID: $!)"
fi

# Start CG-Pro (2406)
if check_port 2406; then
    echo "CG-Pro (2406): Already running"
else
    cd "$HC_PROXIES_DIR/CG-Pro"
    nohup npm start > "$LOG_DIR/cg-pro.log" 2>&1 &
    echo "CG-Pro (2406): Started (PID: $!)"
fi

# Start CC-Claude (2408)
if check_port 2408; then
    echo "CC-Claude (2408): Already running"
else
    cd "$HC_PROXIES_DIR/CC-Claude"
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

    # pm-view-serve.sh
    cat > "$BIN_DIR/pm-view-serve.sh" << 'SCRIPT'
#!/bin/bash
# Start PM-View wiki for the current project
#
# Usage: pm-view-serve.sh [port]
#
# Must be run from a project directory with .claude/PM/PM-View/

PORT=${1:-8000}
PM_VIEW_DIR=".claude/PM/PM-View"

if [ ! -d "$PM_VIEW_DIR" ]; then
    echo "Error: PM-View not found in current directory"
    echo "Expected: $PM_VIEW_DIR/"
    echo ""
    echo "Run hc-init to set up project structure first."
    exit 1
fi

if ! command -v mkdocs &> /dev/null; then
    echo "Error: mkdocs not installed"
    echo "Install: pip install mkdocs-material"
    exit 1
fi

cd "$PM_VIEW_DIR"

# Check for .env
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Created .env from example"
    fi
fi

echo "=== PM-View Wiki ==="
echo "Starting on: http://localhost:$PORT"
echo "Press Ctrl+C to stop"
echo ""

mkdocs serve -a "localhost:$PORT"
SCRIPT

    chmod +x "$BIN_DIR/pm-view-serve.sh"

    log_success "Created start-proxies.sh, stop-proxies.sh, pm-view-serve.sh"
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
    echo "     Edit: ~/.claude/HC-Proxies/CG-Flash/.env"
    echo "     Edit: ~/.claude/HC-Proxies/CG-Pro/.env"
    echo ""
    echo "  2. Start the proxies:"
    echo "     ~/.claude/bin/start-proxies.sh"
    echo ""
    echo "  3. In your project directory, run:"
    echo "     claude"
    echo "     /hc-init"
    echo ""
    if [ "$MKDOCS_AVAILABLE" -eq 1 ]; then
        echo "  4. Start PM-View wiki (optional):"
        echo "     ~/.claude/bin/pm-view-serve.sh"
        echo ""
    else
        echo "  4. For PM-View wiki observability:"
        echo "     pip install mkdocs-material"
        echo "     ~/.claude/bin/pm-view-serve.sh"
        echo ""
    fi
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
    install_hc_proxies
    install_workflow_templates
    create_bin_scripts
    show_completion
}

main "$@"
