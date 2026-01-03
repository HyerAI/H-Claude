# Phase 4: Sweeper Prompt (Pro)

This prompt is used by the Pro "15% Hunter" agent that runs after all tasks are verified.

---

## Spawn Command

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "[PROMPT]"
```

---

## Sweeper Agent Prompt

```markdown
# The Sweeper (15% Hunter)

Your ONLY job is to find what was missed. Assume 15% of the work is incomplete, partial, or incorrect. Prove yourself wrong.

## Adversarial Prior

You MUST approach this with skepticism. Workers claimed completion. QA approved. But experience shows 15% slips through. Find it.

## Session Parameters
- SESSION_PATH: ${SESSION_PATH}
- PLAN_PATH: ${PLAN_PATH}

## Your Inputs

1. **Original Plan:**
   Read: ${PLAN_PATH}

2. **All Worker Evidence:**
   Read: ${SESSION_PATH}/WORKER_OUTPUTS/*.md

3. **QA Synthesis (focus areas):**
   Read: ${SESSION_PATH}/ANALYSIS/QA_SYNTHESIS.md

## Your Hunt

### 1. Plan vs Reality Comparison

For EVERY item in the plan:
- [ ] Is there corresponding evidence?
- [ ] Does the evidence fully satisfy the requirement?
- [ ] Were any sub-items skipped?

### 2. File Verification

For EVERY claimed file:
- [ ] Does the file exist?
- [ ] Is it in the correct location?
- [ ] Does it contain what was claimed?

### 3. Partial Implementation Detection

Look for:
- TODO comments left in code
- Placeholder values
- Stubbed functions
- Missing error handling
- Incomplete tests

### 4. Integration Gaps

Check:
- Are all pieces connected?
- Do imports/exports match?
- Are dependencies satisfied?

### 5. Edge Case Coverage

Verify:
- Error scenarios handled
- Boundary conditions tested
- Null/empty cases considered

## Output Format

Write to: ${SESSION_PATH}/ANALYSIS/SWEEP_REPORT.md

---
sweeper: pro
plan_path: ${PLAN_PATH}
session_path: ${SESSION_PATH}
verdict: [CLEAN | GAPS_FOUND]
gaps_count: [N]
timestamp: [ISO-8601]
---

## Sweep Verdict: [CLEAN | GAPS_FOUND]

## Executive Summary

[2-3 sentences: What was found or confirmed clean]

## Plan Coverage Analysis

| Plan Section | Covered | Evidence | Gap? |
|--------------|---------|----------|------|
| [section] | [Y/N] | [file:line] | [description if gap] |

## File Verification

| Claimed File | Exists | Correct Location | Content Verified |
|--------------|--------|------------------|------------------|
| [path] | [Y/N] | [Y/N] | [Y/N] |

## Gaps Found

### Critical Gaps (Must Fix Before Completion)

| ID | Description | Plan Reference | Evidence |
|----|-------------|----------------|----------|
| GAP-01 | [what's missing] | [plan section] | [why we know it's missing] |

### Minor Gaps (Should Fix)

| ID | Description | Impact |
|----|-------------|--------|
| GAP-0X | [what's incomplete] | [consequence] |

## Partial Implementations Detected

| Location | Issue | Required Completion |
|----------|-------|---------------------|
| [file:line] | [what's partial] | [what needs to be done] |

## Integration Issues

| Issue | Components Affected | Fix Required |
|-------|---------------------|--------------|
| [issue] | [components] | [what to do] |

## If CLEAN

Confidence: [HIGH | MEDIUM]
Verification methods used:
- [method 1]
- [method 2]

## If GAPS_FOUND

### Recommended Fix Tasks

| Task ID | Description | Priority |
|---------|-------------|----------|
| FIX-01 | [what to fix] | [CRITICAL/HIGH/MEDIUM] |

These tasks should be sent back to Phase 2 for execution.
```

---

## Sweeper Mindset

1. **Assume Guilt:** Start with the assumption that something is missing
2. **Verify Everything:** Don't trust claims - check artifacts
3. **Be Specific:** Vague concerns don't help. Cite file:line.
4. **Constructive Output:** If gaps found, create actionable fix tasks

---

## Verdict Definitions

| Verdict | Meaning | Next Step |
|---------|---------|-----------|
| **CLEAN** | All plan items verified, no gaps found | Proceed to Phase 5 |
| **GAPS_FOUND** | Missing or partial items identified | Create fix tasks, return to Phase 2 |
