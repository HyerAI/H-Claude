---
title: Git Improvement Plan
version: 1.0.0
current_maturity: L1
target_maturity: L2
updated: YYYY-MM-DD
---

# Git Improvement Plan - [PROJECT_NAME]

---

## Overview

This plan tracks incremental improvements to the project's git workflow. Each improvement is small, achievable per-commit, and builds toward the target maturity level.

---

## Current State Assessment

**Repository:** [repo-name]
**Commit Quality Score:** [X/10]
**Last Audit:** [DATE]

### Strengths
- [What's working well]
- [Existing good practices]

### Gaps
- [Missing conventions]
- [Inconsistencies found]
- [Opportunities for improvement]

---

## Improvement Backlog

### Priority 1: Quick Wins (1-2 commits to implement)

| ID | Improvement | Status | Commit |
|----|-------------|--------|--------|
| G001 | Adopt Conventional Commits format | [ ] Pending | - |
| G002 | Add commit type to all messages | [ ] Pending | - |
| G003 | Create .gitignore for secrets | [ ] Pending | - |

### Priority 2: Process Improvements (Requires workflow change)

| ID | Improvement | Status | Notes |
|----|-------------|--------|-------|
| G010 | Enable branch protection on main | [ ] Pending | Requires repo admin |
| G011 | Add pre-commit hook for linting | [ ] Pending | Team buy-in needed |
| G012 | Document branching strategy | [ ] Pending | - |

### Priority 3: Advanced (Maturity level jump)

| ID | Improvement | Status | Prerequisite |
|----|-------------|--------|--------------|
| G020 | Implement Stacked Diffs workflow | [ ] Pending | L3 maturity |
| G021 | Enable Merge Queue | [ ] Pending | CI gates stable |
| G022 | Add SLSA attestations | [ ] Pending | Build pipeline ready |

---

## Completed Improvements

| ID | Improvement | Completed | Commit | Impact |
|----|-------------|-----------|--------|--------|
| [ID] | [Description] | [DATE] | [hash] | [Measured impact] |

---

## Per-Commit Integration

**How improvements are applied:**

1. **Every commit:** Check for opportunities from Priority 1
2. **Every PR:** Check for opportunities from Priority 2
3. **Sprint planning:** Review Priority 3 for roadmap

**Git Engineer applies improvements by:**
- Adding scope to commit messages (when missing)
- Suggesting better descriptions (during review)
- Updating PROTOCOLS.md (when pattern emerges)
- Logging improvements (here)

---

## Audit Schedule

| Audit Type | Frequency | Last Run | Next Run |
|------------|-----------|----------|----------|
| Commit message quality | Weekly | [DATE] | [DATE] |
| Branch hygiene | Bi-weekly | [DATE] | [DATE] |
| Full protocol review | Monthly | [DATE] | [DATE] |

---

## Metrics Tracking

### Commit Message Quality

| Metric | Baseline | Current | Target |
|--------|----------|---------|--------|
| Conventional format compliance | [X]% | [X]% | 100% |
| Meaningful descriptions | [X]% | [X]% | 95% |
| Proper scoping | [X]% | [X]% | 90% |

### Workflow Health

| Metric | Current | Target |
|--------|---------|--------|
| Average PR size (lines) | [X] | <400 |
| Time to merge | [X] days | <1 day |
| Failed CI rate | [X]% | <5% |

---

## Learning Log

Track what we learn from each improvement cycle:

### [DATE] - [Improvement ID]
**What we tried:** [Description]
**Result:** [Success/Partial/Failed]
**Learning:** [What we'll do differently]

---

## Notes

- Improvements should be invisible to developers when possible
- Start with the easiest wins to build momentum
- Don't try to jump maturity levels; iterate incrementally
- Document exceptions; rigid rules break in edge cases

---

*Plan maintained by git-engineer agent. Review monthly.*
