---
name: commit-gate
description: Pre-commit validation gate for code changes
category: quality
used_by: [quality-gatekeeper, git-engineer]
---

# Commit Gate Skill

## Purpose

This skill provides the protocol for the Quality Gatekeeper to validate and commit code changes.

## Gate Requirements

All MUST pass before commit:

1. **Tests Pass** - All relevant tests green
2. **Lint Clean** - No style violations
3. **No Secrets** - No hardcoded credentials
4. **Docs Updated** - CHANGELOG reflects changes
5. **Story Linked** - Commit references task/story

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

Task: T1.2
Story: STORY-001

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: <Agent Name> <noreply@anthropic.com>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructure (no behavior change)
- `docs`: Documentation only
- `test`: Test additions/changes
- `chore`: Build/tooling changes

## Gate Execution Protocol

```
┌─────────────────────────────────────────┐
│ 1. Run Tests                            │
│    pytest tests/ -v                     │
└─────────────────────────────────────────┘
              │
              ↓ PASS
┌─────────────────────────────────────────┐
│ 2. Run Linter                           │
│    ruff check .                         │
└─────────────────────────────────────────┘
              │
              ↓ PASS
┌─────────────────────────────────────────┐
│ 3. Check for Secrets                    │
│    trufflehog . --json                  │
└─────────────────────────────────────────┘
              │
              ↓ PASS
┌─────────────────────────────────────────┐
│ 4. Verify CHANGELOG Updated             │
│    Check for today's entry              │
└─────────────────────────────────────────┘
              │
              ↓ PASS
┌─────────────────────────────────────────┐
│ 5. Git Add + Commit                     │
│    git add -A                           │
│    git commit -m "..."                  │
└─────────────────────────────────────────┘
              │
              ↓ SUCCESS
┌─────────────────────────────────────────┐
│ 6. Update Task State                    │
│    Task → DONE                          │
│    Story (if all tasks done) → DONE     │
└─────────────────────────────────────────┘
```

## Failure Handling

If any gate fails:
1. **STOP** - Don't commit
2. **Report** - Specific failure reason
3. **Return** - Task stays in QA_PASSED, not DONE

## Separation of Powers

**Quality Gatekeeper:**
- ✅ CAN: Read code, run tests, commit
- ❌ CANNOT: Write/edit code files

If code needs changes → return to Code Worker.

---

*Expertise package for commit validation*
