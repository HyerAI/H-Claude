# H-Claude Hooks

## Overview

This directory contains hooks that Claude Code executes at specific lifecycle events.

## session-start.sh

**Purpose:** Quick environment health check at session start

**What it checks:**
- `.claude/context.yaml` exists
- At least one proxy is responding (2405, 2406, or 2408)

**What it does NOT do:**
- Block session start (runs in background)
- Modify any files
- Read file contents (existence check only)
- Invoke Claude (would cause recursion)

---

## Disabling the Hook

### Quick Disable (remove script)
```bash
rm .claude/hooks/session-start.sh
```

### Via settings.json
Remove or comment out the hook configuration:
```json
{
  "hooks": {
    // "session-start": { ... }
  }
}
```

---

## Symptoms of Hook Issues

| Symptom | Possible Cause |
|---------|----------------|
| Session start hangs | Hook blocking (check for sync operations) |
| Session won't start | Hook returning non-zero |
| Slow session start | Hook doing too much work |
| Recursive Claude spawning | Hook invoking `claude` command |

---

## Safe vs Unsafe Hook Operations

### SAFE (Do These)
```bash
[[ -f "file" ]]           # File existence check
timeout 1 curl ...        # HTTP with timeout
echo "..." >&2            # Output to stderr
exit 0                    # Always exit success
```

### UNSAFE (Never Do These)
```bash
claude -p "..."           # NEVER - causes recursion
npm install               # Too slow
git pull                  # Network, too slow
cat large_file.log        # Could be huge
curl without timeout      # Could hang forever
exit 1                    # Blocks session!
```

---

## Testing the Hook

```bash
# Run in isolation
chmod +x .claude/hooks/session-start.sh
time .claude/hooks/session-start.sh
# Should complete in <2 seconds

# Test failure modes
mv .claude/context.yaml .claude/context.yaml.bak
.claude/hooks/session-start.sh
# Should warn about missing context.yaml, still exit 0
mv .claude/context.yaml.bak .claude/context.yaml
```

---

## Configuration

In `.claude/settings.json`:
```json
{
  "hooks": {
    "session-start": {
      "command": ".claude/hooks/session-start.sh",
      "timeout": 2000,
      "blocking": false
    }
  }
}
```

**Key settings:**
- `timeout`: Max execution time in ms (2000 = 2 seconds)
- `blocking`: false = session continues regardless of hook result
