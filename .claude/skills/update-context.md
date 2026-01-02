---
name: update-context
description: Update the global session state. Run after every significant task completion or before commits.
---

# /update-context - Session State Update

Update `.claude/context.yaml` to reflect current progress. This ensures crash-proof session persistence.

## When to Run

- After completing a task
- After making a significant decision
- Before any git commit
- When switching focus to a different objective

## Protocol

1. **Read** `.claude/context.yaml`

2. **Update `meta`:**
   - Set `last_modified` to current timestamp

3. **Update `recent_actions`:**
   - Add completed task with `[DONE]` prefix
   - Add in-progress task with `[IN_PROGRESS]` prefix
   - Keep only last 5 entries (remove oldest if needed)

4. **Update `tasks.active`:**
   - Mark completed tasks as done (remove from active)
   - Add next logical step if identified
   - Ensure max 3 active tasks

5. **Update `focus`:**
   - Update `current_objective` if changed
   - Add to `active_decisions` if new choices were made

6. **Save** the file

## Example Usage

**Before task:** "Write the context.yaml schema"

**After task:** Run `/update-context`

**Changes made:**
```yaml
recent_actions:
  - "[DONE] Wrote context.yaml schema"  # Added
  - "[IN_PROGRESS] Creating update-context skill"  # Updated
  # ... (keep last 5)

tasks:
  active:
    - id: 1
      title: "Create update-context skill"  # Next task
      status: in_progress
```

## Commit Integration

When committing code, ALWAYS:
1. Run `/update-context` first
2. Stage both work files AND `.claude/context.yaml`
3. Commit together

```bash
git add src/feature.py .claude/context.yaml
git commit -m "feat: add feature"
```

This ensures state is saved with every commit - crash-proof.

## Schema Limits

| Field | Max | Action if exceeded |
|-------|-----|-------------------|
| `recent_actions` | 5 | Remove oldest |
| `tasks.active` | 3 | Move to backlog |
| `tasks.backlog` | 10 | Prompt user to prioritize |
| `active_decisions` | 5 | Remove oldest/obsolete |
