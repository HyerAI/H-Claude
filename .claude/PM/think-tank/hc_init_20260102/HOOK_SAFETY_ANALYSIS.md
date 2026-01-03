# Hook Safety Analysis

## Critical Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Hook blocks session start** | FATAL | Timeout mechanism, async execution |
| **Hook causes infinite loop** | FATAL | No Claude invocations from hook |
| **Hook fails silently** | HIGH | Explicit error handling, logging |
| **Hook slows every session** | MEDIUM | Fast checks only (<2s total) |
| **Hook overwrites user work** | HIGH | Read-only checks, no writes |

## Hook Types in Claude Code

```
PreToolUse    - Before tool execution (can block)
PostToolUse   - After tool execution
Notification  - Informational only (safest)
```

**Recommendation:** Use `Notification` type if available, or ensure hook is **non-blocking**.

## Safe Hook Design

### Principles

1. **NEVER invoke Claude CLI from hook** - causes recursion
2. **NEVER block on network calls** - use timeout
3. **NEVER write to project files** - read-only checks
4. **ALWAYS exit 0** - never fail the session
5. **ALWAYS be fast** - <2 seconds total
6. **ALWAYS log to stderr** - don't pollute stdout

### Implementation Pattern

```bash
#!/bin/bash
# .claude/hooks/session-start.sh

# SAFETY: Always exit 0 to never block session
trap 'exit 0' ERR

# SAFETY: Timeout entire script (2 seconds max)
TIMEOUT=2

# SAFETY: Run checks in background, don't block
{
    # Quick checks only
    check_result=""

    # Check context.yaml exists (fast, local)
    if [[ ! -f ".claude/context.yaml" ]]; then
        check_result+="⚠ context.yaml missing\n"
    fi

    # Check at least one proxy (with 1s timeout)
    if ! timeout 1 curl -s http://localhost:2405/health >/dev/null 2>&1 && \
       ! timeout 1 curl -s http://localhost:2406/health >/dev/null 2>&1 && \
       ! timeout 1 curl -s http://localhost:2408/health >/dev/null 2>&1; then
        check_result+="⚠ No proxies responding\n"
    fi

    # Output warnings (if any)
    if [[ -n "$check_result" ]]; then
        echo -e "\n[H-Claude] Environment warnings:" >&2
        echo -e "$check_result" >&2
        echo "Run ./hc-init for details" >&2
    fi
} &

# SAFETY: Don't wait for background process
exit 0
```

### What Hook Should NOT Do

```bash
# NEVER DO THIS:
claude -p "check something"     # Recursion!
npm install                     # Too slow
git pull                        # Too slow, network
cat large_file.log              # Could be huge
curl without timeout            # Could hang forever
exit 1                          # Blocks session!
```

### What Hook CAN Do Safely

```bash
# SAFE:
[[ -f ".claude/context.yaml" ]]        # File exists check
timeout 1 curl -s localhost:2405       # Quick health ping
grep -q "key" .env 2>/dev/null         # Quick grep
wc -l < file.txt                       # Fast count
echo "warning" >&2                     # Output to stderr
```

## Testing Strategy

### Before Deploying Hook

1. **Test in isolation:**
   ```bash
   chmod +x .claude/hooks/session-start.sh
   time .claude/hooks/session-start.sh
   # Must complete in <2s
   ```

2. **Test failure modes:**
   ```bash
   # Simulate no proxies
   # Simulate missing context.yaml
   # Verify session still starts
   ```

3. **Test with Claude Code:**
   - Start new session
   - Verify no delays
   - Verify warnings appear (if applicable)

### Rollback Plan

If hook causes issues:
```bash
# Quick disable
rm .claude/hooks/session-start.sh

# Or remove from settings.json
```

## Hook Configuration

### settings.json Structure

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
- `timeout`: Max execution time (ms)
- `blocking`: false = session continues regardless

## Phased Rollout

1. **Phase 1:** Hook with logging only (no output to user)
2. **Phase 2:** Hook with stderr warnings
3. **Phase 3:** Hook integrated with hc-init recommendations

Start conservative, add features once stable.
