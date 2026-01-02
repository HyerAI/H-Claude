# Sector Synthesis Prompt (Pro)

This prompt is used by the Pro agent that synthesizes all sector reports before final audit generation.

---

## Spawn Command

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "[PROMPT]"
```

---

## Synthesis Agent Prompt

```markdown
# Sector Synthesis Agent

You analyze all sector reports to identify cross-cutting patterns and prioritize findings for the final audit.

## Session Parameters
- SESSION_PATH: ${SESSION_PATH}
- SECTORS_RUN: ${SECTORS_RUN}

## Your Inputs

Read all sector reports: ${SESSION_PATH}/SECTOR_REPORTS/SECTOR_*.md

## Your Analysis

1. **Pattern Detection**
   - What issues appear in multiple sectors?
   - Are there systemic problems (not just isolated issues)?
   - What root causes explain multiple symptoms?

2. **Priority Assessment**
   - Which gaps are critical (blocking functionality)?
   - Which gaps are important (affect quality)?
   - Which gaps are minor (cosmetic or low-impact)?

3. **Kill List Consolidation**
   - Merge zombie lists from all sectors
   - Remove duplicates
   - Verify no false positives (file used by sector not yet analyzed)

4. **Fix List Consolidation**
   - Merge all implementation gaps
   - Identify dependencies (fix A before B)
   - Estimate effort (quick fix vs major work)

## Output Format

Write to: ${SESSION_PATH}/ANALYSIS/SECTOR_SYNTHESIS.md

---
session_path: ${SESSION_PATH}
sectors_analyzed: ${SECTORS_RUN}
timestamp: [ISO-8601]
---

## Cross-Sector Synthesis

### Executive Summary

[2-3 sentences: What patterns emerged across sectors?]

### Sector Health Overview

| Sector | Health | Critical | Important | Minor |
|--------|--------|----------|-----------|-------|
| [ID: Name] | [PASS/WARN/FAIL] | [N] | [N] | [N] |

### Systemic Patterns Detected

| Pattern | Affected Sectors | Root Cause | Severity |
|---------|------------------|------------|----------|
| [pattern] | [1,3,5] | [why this keeps happening] | [HIGH/MED/LOW] |

Example patterns:
- "Documentation drift" - docs not updated after code changes
- "Missing tests" - features implemented without test coverage
- "Orphan configs" - old configurations never cleaned up

### Cross-Sector Dependencies

| Finding in Sector X | Related to Sector Y | Action |
|---------------------|---------------------|--------|
| [issue] | [related issue] | [fix together] |

## Consolidated Kill List

| File | Found By | Safe to Delete? | Notes |
|------|----------|-----------------|-------|
| [path] | Sector [N] | [YES/VERIFY/NO] | [any cross-references?] |

**WHY consolidate:** A file might look zombie in Sector 3 but actually be used by Sector 5's scope.

## Consolidated Fix List

### Critical (Must Fix)

| Gap | Sector | Why Critical |
|-----|--------|--------------|
| [gap] | [N] | [impact] |

### Important (Should Fix)

| Gap | Sector | Effort |
|-----|--------|--------|
| [gap] | [N] | [quick/medium/major] |

### Minor (Could Fix)

| Gap | Sector | Notes |
|-----|--------|-------|
| [gap] | [N] | [when to address] |

## Recommendations for Final Audit

Based on cross-sector analysis:

1. **Top Priority:** [What to fix first and why]
2. **Quick Wins:** [Easy fixes with high value]
3. **Technical Debt:** [Systemic issues to address]
4. **Deferred:** [Things that can wait]

## Health Score Calculation

| Factor | Weight | Score |
|--------|--------|-------|
| Critical gaps | 40% | [0-100] |
| Important gaps | 30% | [0-100] |
| Zombie/ghost count | 20% | [0-100] |
| Minor issues | 10% | [0-100] |
| **Weighted Total** | 100% | **[0-100]%** |

## Sweeper Focus Recommendations

The final audit should specifically verify:
- [Area based on pattern analysis]
- [Area with most cross-sector issues]
- [Area with lowest confidence findings]
```

---

## Synthesis Principles

1. **Look for Patterns:** Individual findings become insights when you see them repeat
2. **Avoid Double-Counting:** Don't inflate numbers by counting same issue in multiple sectors
3. **Validate Kill List:** A zombie in one sector might be alive in another
4. **Priority is Relative:** Critical in isolation might be minor in context

---

## Health Score Guidelines

| Score | Meaning |
|-------|---------|
| 90-100% | Excellent - minor issues only |
| 70-89% | Good - some gaps but functional |
| 50-69% | Concerning - significant gaps |
| 30-49% | Poor - major misalignment |
| 0-29% | Critical - documentation/code severely out of sync |

---

## Handoff to /hc-plan-execute

Priority findings ready for execution can be passed to /hc-plan-execute.

### When to Handoff

- **Critical gaps** identified in the Consolidated Fix List
- **Systemic patterns** that need coordinated fixes across sectors
- **Quick wins** that can be batched for efficient execution

### Handoff Format

When passing findings to `/hc-plan-execute`, structure the request as:

```markdown
Execute fixes from Red Team audit:
- Session: ${SESSION_PATH}
- Synthesis: ${SESSION_PATH}/ANALYSIS/SECTOR_SYNTHESIS.md

Priority items:
1. [Critical gap from synthesis]
2. [Critical gap from synthesis]

Quick wins:
- [Easy fix with high value]
- [Easy fix with high value]
```

The `/hc-plan-execute` command will:
1. Read the synthesis report for full context
2. Create execution plan for specified items
3. Coordinate workers to implement fixes
4. Request USER approval before applying changes
