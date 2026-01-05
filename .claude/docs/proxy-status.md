# Proxy Status

<div id="proxy-controls">
    <span id="proxy-summary">Checking...</span>
    <span class="proxy-timestamp">Last check: <span id="proxy-timestamp">-</span></span>
    <button onclick="refreshProxyStatus()" class="proxy-refresh-btn" title="Refresh status">Refresh Status</button>
</div>

<table id="proxy-status-table">
<thead>
<tr>
<th>Status</th>
<th>Proxy</th>
<th>Port</th>
<th>Model</th>
<th>Purpose</th>
</tr>
</thead>
<tbody>
<tr><td colspan="5">Loading...</td></tr>
</tbody>
</table>

---

## Quick Actions

### Start All Proxies

```bash
.claude/scripts/start-proxies.sh
```

### Stop All Proxies

```bash
.claude/scripts/stop-proxies.sh
```

### Restart All Proxies

```bash
.claude/scripts/stop-proxies.sh && sleep 1 && .claude/scripts/start-proxies.sh
```

---

## Proxy Architecture

| Category | Proxies | When to Use |
|----------|---------|-------------|
| **Reasoning** | HC-Reas-A, HC-Reas-B | Complex analysis, QA, critics |
| **Workers** | HC-Work, HC-Work-R | Code execution, scouts, validators |
| **Orchestration** | HC-Orca, HC-Orca-R | Command coordination |
| **Specialized** | CG-Image | Image generation |

See [PROXIES.md](PROXIES.md) for full documentation.

---

## Troubleshooting

### Proxy Offline?

1. Check if Node.js is installed: `node --version`
2. Check logs: `cat /tmp/h-claude/hc-work.log`
3. Restart: `.claude/scripts/stop-proxies.sh && .claude/scripts/start-proxies.sh`

### Port in Use?

```bash
# Find what's using the port
lsof -i:2412

# Kill it
lsof -ti:2412 | xargs kill -9
```
