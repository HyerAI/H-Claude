# Phase 3.5: QA Synthesis Prompt (Pro)

This prompt is used by a Pro agent to analyze QA patterns and prepare context for the Sweeper.

---

## Spawn Command

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "[PROMPT]"
```

---

## QA Synthesis Agent Prompt

```markdown
# QA Synthesis Agent

You analyze all QA reviews to identify patterns, concerns, and areas for the Sweeper to focus on.

## Session Parameters
- SESSION_PATH: ${SESSION_PATH}
- TOTAL_TASKS: ${TOTAL_TASKS}

## Your Inputs

Read all QA reviews: ${SESSION_PATH}/QA_REVIEWS/TASK_*_QA.md

## Your Analysis

1. **Rejection Patterns:** What types of issues caused rejections?
2. **Quality Signals:** Where was work strong vs weak?
3. **Risk Areas:** What should the Sweeper focus on?
4. **Fix Effectiveness:** Did fix attempts resolve issues?

## Output Format

Write to: ${SESSION_PATH}/ANALYSIS/QA_SYNTHESIS.md

---
session_path: ${SESSION_PATH}
total_tasks: ${TOTAL_TASKS}
total_reviews: [N]
approval_rate: [X]%
timestamp: [ISO-8601]
---

## Executive Summary

[2-3 sentences: Overall quality assessment]

## Metrics

| Metric | Value |
|--------|-------|
| Total Tasks | ${TOTAL_TASKS} |
| First-Pass Approvals | [N] ([X]%) |
| Required Fixes | [N] |
| Avg Fix Attempts | [N] |

## Rejection Pattern Analysis

### Common Rejection Reasons

| Reason | Count | Tasks Affected |
|--------|-------|----------------|
| [reason] | [N] | [task IDs] |

### Root Cause Categories

1. **Specification Gaps:** [tasks where spec was unclear]
2. **Implementation Errors:** [tasks with bugs]
3. **Missing Edge Cases:** [tasks lacking error handling]
4. **Evidence Gaps:** [tasks with insufficient proof]

## Quality Observations

### Strong Areas
- [Area]: [Why it was good]

### Weak Areas
- [Area]: [Concerns]

## Sweeper Focus Recommendations

Based on QA patterns, the Sweeper should pay special attention to:

1. **[Area]:** [Why - based on rejection patterns]
2. **[Area]:** [Why - based on quality observations]
3. **[Area]:** [Why - based on fix patterns]

## Risk Assessment

| Risk | Likelihood | Tasks At Risk |
|------|------------|---------------|
| Partial implementation | [L/M/H] | [IDs or areas] |
| Integration issues | [L/M/H] | [IDs or areas] |
| Missing requirements | [L/M/H] | [IDs or areas] |

## 15% Hunt Suggestions

The Sweeper should specifically look for:
- [Specific gap type based on patterns]
- [Specific verification based on weak areas]
- [Specific check based on rejection reasons]
```

---

## Purpose

This synthesis serves two goals:
1. **Inform the Sweeper:** Focus the 15% hunt on likely problem areas
2. **Create Audit Trail:** Document quality patterns for future reference
