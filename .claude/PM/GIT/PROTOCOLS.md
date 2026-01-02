---
title: Git Protocols
version: 1.1.0
maturity: L1
updated: 2026-01-01
---

# Git Protocols

---

## Project Context

**Repository:** Your Project
**Primary Branch:** main
**Branching Strategy:** GitHub Flow (feature branches, PR to main)

---

## Session State Integration (CRITICAL)

### The Golden Rule

> **EVERY commit MUST include `.claude/context.yaml`**

This project uses Continuous State for crash-proof session persistence.

```bash
git add [work-files] .claude/context.yaml
git commit -m "type(scope): description"
```

**Why:** If session crashes, only work since last commit is lost. State persists with code.

---

## Commit Standards

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | When to Use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code restructure (no behavior change) |
| `docs` | Documentation only |
| `test` | Test additions/modifications |
| `chore` | Maintenance, dependencies |
| `style` | Formatting, whitespace |
| `perf` | Performance improvement |
| `ci` | CI/CD changes |

### Scopes (Customize for your project)

| Scope | Component |
|-------|-----------|
| `claude` | .claude/ configuration |
| `docs` | Documentation (ADRs, plans) |
| `pm` | Project management |
| `core` | Core functionality |
| `api` | API layer |
| `ui` | User interface |

### Rules

- [x] Subject line under 72 characters
- [x] Use imperative mood ("Add feature" not "Added feature")
- [x] No period at end of subject
- [x] Body wraps at 72 characters
- [x] Reference issues in footer when applicable
- [x] ALWAYS include .claude/context.yaml in staging

---

## Branch Strategy

### Naming Convention

```
<type>/<short-description>
```

**Examples:**
- `feat/hd-diamond-interview`
- `fix/state-validation`
- `refactor/driftguard-protocol`

### Lifecycle

| Stage | Action |
|-------|--------|
| Create | Branch from `main` |
| Develop | Small, atomic commits |
| Review | Open PR, request review |
| Merge | Squash and merge |
| Cleanup | Delete branch after merge |

---

## Pull Request Standards

### Title Format

```
[TYPE] Brief description
```

### Description Template

```markdown
## Summary
[1-3 bullet points]

## Changes
- [Specific change 1]
- [Specific change 2]

## Test Plan
- [ ] [How to verify]
```

### Review Checklist

- [ ] Conventional commit format
- [ ] Tests pass
- [ ] No secrets committed
- [ ] Documentation updated
- [ ] Breaking changes noted
- [ ] context.yaml included

---

## Forbidden Actions

- [x] Force push to main/master
- [x] Commit secrets (.env, keys, tokens)
- [x] Skip pre-commit hooks (--no-verify)
- [x] Rebase published commits
- [x] Delete remote branches without approval
- [x] Commit generated files (unless intentional)
- [x] Commit without context.yaml (session state)

---

## CI/CD Integration

### Required Checks (if applicable)

- [ ] Tests pass
- [ ] Linting clean
- [ ] Type checking pass

### Merge Requirements

- [ ] At least 1 approval
- [ ] All checks pass
- [ ] No merge conflicts

---

## Maturity Level Progression

| Level | Characteristics | Target |
|-------|-----------------|--------|
| **L1** | Basic commits, direct to main | Adopt conventions |
| **L2** | Conventions, feature branches | Add PR workflow |
| **L3** | Strict conventions, PR + CI gates | Add advanced tooling |
| **L4** | Stacked diffs, merge queues, SLSA | Continuous improvement |

**Current Level:** L1
**Next Milestone:** Establish feature branch workflow (L2)

---

## Exceptions

1. **Context without code:** May commit only context.yaml if session state changed significantly
2. **Documentation sessions:** May skip scope in pure docs commits

---

*Protocols enforced by git-engineer agent. Updates require approval.*
