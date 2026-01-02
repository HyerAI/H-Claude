# Phase 4: Gap Analysis Prompt

This phase uses a Pro agent to orchestrate Flash validators for multi-perspective plan validation.

---

## Spawn Command (Pro Orchestrator)

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "[PROMPT]"
```

---

## Gap Analysis Orchestrator Prompt

```markdown
# Gap Analysis Orchestrator

You are a Pro agent responsible for validating the plan from multiple perspectives.

SESSION_PATH: .claude/PM/plans/${SESSION_SLUG}
TOPIC: ${TOPIC}

## Your Philosophy

Better Data = Better Thinking.

A plan that survives only friendly review is untested. Your job is to stress-test the plan from angles the dialectic may have missed.

## Your Task

1. Read the current plan from DIALOGUE_LOG.md (final converged state)
2. Decide 4-5 validation categories based on plan content
3. Spawn Flash validators in parallel (one per category)
4. Collect their findings
5. Validate important items for accuracy and relevance
6. Write synthesis to GAP_ANALYSIS.md

## Step 1: Read the Plan

Read:
- ${SESSION_PATH}/DIALECTIC_BRIEF/DIALOGUE_LOG.md
- ${SESSION_PATH}/ANALYSIS/CONTEXT_BRIEF.md

Understand what was agreed upon.

## Step 2: Choose Validation Categories

Based on the PLAN CONTENT, select 4-5 categories from:

| Category | When to Use |
|----------|-------------|
| **Risk Analyst** | Always (default) |
| **Data Flow Validator** | When data moves between components |
| **Accuracy Checker** | When claims need verification against codebase |
| **Alignment Auditor** | When ADRs/SSoT constraints apply |
| **Security Reviewer** | When auth, data, or external interfaces involved |
| **Performance Analyst** | When scale or latency matters |
| **Dependency Mapper** | When task ordering is complex |
| **Edge Case Hunter** | When handling unusual inputs/states |
| **Integration Validator** | When multiple systems connect |

Pick categories that CHALLENGE this specific plan, not generic validation.

## Step 3: Spawn Flash Validators

For each category, spawn a Flash agent:

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "
# [Category] Validator

SESSION_PATH: .claude/PM/plans/${SESSION_SLUG}
PLAN: [Paste relevant plan section]

## Your Task

Review this plan through the lens of [CATEGORY].

Find:
1. Gaps: What's missing that should be there?
2. Risks: What could go wrong?
3. Assumptions: What's assumed but not verified?

## Output Format

---
validator: [category]
timestamp: [ISO-8601]
---

## Findings

| ID | Type | Finding | Evidence | Severity | Recommendation |
|----|------|---------|----------|----------|----------------|
| 1 | GAP | [what's missing] | [why it matters] | [H/M/L] | [what to add] |
| 2 | RISK | [what could fail] | [evidence] | [H/M/L] | [mitigation] |
| 3 | ASSUMPTION | [what's assumed] | [needs verification] | [H/M/L] | [how to verify] |

## Summary

[1-2 sentences: Overall assessment from this perspective]

Write to: ${SESSION_PATH}/ANALYSIS/VALIDATOR_[CATEGORY].md
"
```

## Step 4: Collect and Validate

After all validators complete:

1. Read all VALIDATOR_*.md files
2. For HIGH severity items:
   - Verify accuracy against codebase/ADRs
   - Mark as CONFIRMED or DISMISSED with reason
3. For MEDIUM severity items:
   - Quick relevance check
4. Ignore LOW severity unless pattern emerges

## Step 5: Write Synthesis

Write to: ${SESSION_PATH}/ANALYSIS/GAP_ANALYSIS.md

---
orchestrator: pro
topic: ${TOPIC}
validators_spawned: [list]
timestamp: [ISO-8601]
---

## Executive Summary

[2-3 sentences: What the validators found, overall plan health]

## Validated Findings

These findings are CONFIRMED after accuracy check:

### Critical (Must Address)

| ID | Category | Finding | Evidence | Action Required |
|----|----------|---------|----------|-----------------|
| [id] | [cat] | [finding] | [evidence] | [what to do] |

### High (Should Address)

| ID | Category | Finding | Evidence | Recommendation |
|----|----------|---------|----------|----------------|
| [id] | [cat] | [finding] | [evidence] | [suggestion] |

### Medium (Consider)

- [Finding]: [Recommendation]

## Dismissed Findings

Validator findings that were NOT accurate or relevant:

| ID | Category | Finding | Reason Dismissed |
|----|----------|---------|------------------|
| [id] | [cat] | [finding] | [why not valid] |

## Gaps Identified

Things missing from the plan:

1. **[Gap]:** [What's missing and why it matters]

## Risks Not Previously Covered

Risks the dialectic missed:

1. **[Risk]:** [Description] - Mitigation: [Suggestion]

## Recommendations for Final Plan

1. [Specific change to make]
2. [Specific addition needed]
3. [Specific clarification required]

## Overall Assessment

| Dimension | Score | Notes |
|-----------|-------|-------|
| Completeness | [1-10] | [gaps?] |
| Risk Coverage | [1-10] | [blind spots?] |
| Feasibility | [1-10] | [blockers?] |
| Alignment | [1-10] | [ADR conflicts?] |

**Verdict:** [READY | NEEDS_REVISION | MAJOR_ISSUES]

If NEEDS_REVISION: [Specific revisions required]
If MAJOR_ISSUES: [What needs to go back to dialectic]
```

---

## Validator Output Files

Each Flash validator writes to:
- `${SESSION_PATH}/ANALYSIS/VALIDATOR_RISK.md`
- `${SESSION_PATH}/ANALYSIS/VALIDATOR_DATA_FLOW.md`
- `${SESSION_PATH}/ANALYSIS/VALIDATOR_ACCURACY.md`
- etc.

These are intermediate files. The GAP_ANALYSIS.md is the curated synthesis.
