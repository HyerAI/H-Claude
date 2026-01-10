# /hc-sys - H-Claude System Health Check

Check system health: proxies, wiki, disk, project structure.

---

## Usage

```
/hc-sys           # Full health check
/hc-sys --start   # Check + start missing services
```

---

## Execution

Run these checks and display results:

### 1. Proxy Health (2410-2415)

```bash
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  H-CLAUDE SYSTEM HEALTH CHECK                                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

echo "## Proxies"
echo ""

check_proxy() {
    local port=$1
    local name=$2
    local status
    if curl -sf --max-time 2 "http://localhost:$port/health" >/dev/null 2>&1; then
        status="✅ UP"
    elif lsof -ti:$port >/dev/null 2>&1; then
        status="⚠️  LISTENING (no /health)"
    else
        status="❌ DOWN"
    fi
    printf "| %-12s | %-5s | %-25s |\n" "$name" "$port" "$status"
}

echo "| Proxy        | Port  | Status                    |"
echo "|--------------|-------|---------------------------|"
check_proxy 2410 "HC-Reas-A"
check_proxy 2411 "HC-Reas-B"
check_proxy 2412 "HC-Work"
check_proxy 2413 "HC-Work-R"
check_proxy 2414 "HC-Orca"
check_proxy 2415 "HC-Orca-R"
check_proxy 2407 "CG-Image"
echo ""
```

### 2. Wiki/PM-View

```bash
echo "## Wiki (PM-View)"
echo ""

WIKI_PORT="${PM_VIEW_PORT:-8003}"
if curl -sf --max-time 2 "http://localhost:$WIKI_PORT" >/dev/null 2>&1; then
    echo "| PM-View | $WIKI_PORT | ✅ UP |"
else
    echo "| PM-View | $WIKI_PORT | ❌ DOWN |"
fi
echo ""
```

### 3. Disk Space

```bash
echo "## Disk Space"
echo ""

DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | tr -d '%')
DISK_AVAIL=$(df -h / | tail -1 | awk '{print $4}')

if [ "$DISK_USAGE" -lt 70 ]; then
    echo "| Root (/) | $DISK_AVAIL free | ✅ OK ($DISK_USAGE% used) |"
elif [ "$DISK_USAGE" -lt 85 ]; then
    echo "| Root (/) | $DISK_AVAIL free | ⚠️  WARNING ($DISK_USAGE% used) |"
else
    echo "| Root (/) | $DISK_AVAIL free | ❌ CRITICAL ($DISK_USAGE% used) |"
fi
echo ""
```

### 4. Project Structure

```bash
echo "## Project Structure"
echo ""

check_file() {
    local file=$1
    local name=$2
    if [ -f "$file" ]; then
        echo "| $name | ✅ exists |"
    else
        echo "| $name | ❌ missing |"
    fi
}

check_file ".claude/context.yaml" "context.yaml"
check_file ".claude/PM/SSoT/NORTHSTAR.md" "NORTHSTAR.md"
check_file ".claude/PM/SSoT/ROADMAP.yaml" "ROADMAP.yaml"
check_file "CLAUDE.md" "CLAUDE.md"
echo ""
```

### 5. Summary

```bash
# Count issues
PROXY_DOWN=$(for p in 2410 2411 2412 2413 2414 2415; do
    curl -sf --max-time 1 "http://localhost:$p/health" >/dev/null 2>&1 || echo "down"
done | grep -c "down" || true)

echo "## Summary"
echo ""
if [ "$PROXY_DOWN" -eq 0 ] && [ "$DISK_USAGE" -lt 85 ]; then
    echo "✅ **All systems operational**"
else
    [ "$PROXY_DOWN" -gt 0 ] && echo "⚠️  $PROXY_DOWN proxy(s) down - run: .claude/scripts/start-proxies.sh"
    [ "$DISK_USAGE" -ge 85 ] && echo "⚠️  Disk space critical - cleanup needed"
fi
echo ""
```

---

## With --start Flag

If user passes `--start`, also run:

```bash
# Start proxies if any are down
if [ "$PROXY_DOWN" -gt 0 ]; then
    echo "Starting proxies..."
    .claude/scripts/start-proxies.sh
fi

# Start wiki if down
if ! curl -sf --max-time 1 "http://localhost:${PM_VIEW_PORT:-8003}" >/dev/null 2>&1; then
    echo "Starting wiki (background)..."
    cd .claude/PM/PM-View && nohup mkdocs serve --dev-addr "127.0.0.1:${PM_VIEW_PORT:-8003}" > /tmp/h-claude/pm-view.log 2>&1 &
    cd - > /dev/null
fi
```

---

## Output Format

Display results as a formatted report. No files written.

This is a read-only diagnostic command.
