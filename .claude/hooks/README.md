# H-Claude Hooks

## session-start.sh (V1)

**Purpose:** Quick environment health check at session start.

**What it checks:**
- `.claude/context.yaml` exists
- At least one proxy is responding (2405, 2406, or 2408)

**What it does NOT do:**
- Block session start (runs in background)
- Spawn agents
- Modify files

---

## Disabling

```bash
rm .claude/hooks/session-start.sh
# or remove hook config from .claude/settings.json
```

---

## Testing

```bash
time .claude/hooks/session-start.sh
# Should complete in <2 seconds
```

---

**Version:** V1.0.0
