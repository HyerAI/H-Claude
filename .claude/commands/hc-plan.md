---
version: V2.4.0
status: current
timestamp: 2025-12-30
tags: [command, planning, multi-agent, dialectic]
description: "Dialectic Planning with Integrated Research - understand, research, expand, challenge, validate"
---

# /hc-plan - Dialectic Planning

**Philosophy:** Better Data = Better Thinking

**Purpose:** Generate high-quality plans through structured dialogue combining research, additive brainstorming, adversarial challenge, and multi-perspective validation.

---

## Quick Start

```markdown
/hc-plan

TOPIC: [What needs planning]
MODE: [standard|deep]
EXTERNAL_RESEARCH: [true|false]
OUTPUT_NAME: [APPROVED_PLAN.md]  # Optional, defaults to APPROVED_PLAN.md

CONTEXT:
- [Relevant background]
- [Constraints]
- [Goals]
```

This command spawns a background Opus orchestrator that runs the full workflow. You'll be notified when complete.

---

## Architecture Overview

```
HD invokes /hc-plan
     ↓
Spawn OPUS Orchestrator (BACKGROUND)
     ↓
┌────────────────────────────────────────────────────────────────────────┐
│  PHASE 0: UNDERSTAND                                                   │
│  Opus clarifies task → TASK_UNDERSTANDING.md                           │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 1: RESEARCH (Flash agents, parallel)                            │
│  3-4 Flash researchers → RESEARCH_FILES/                               │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 2: SYNTHESIS (Pro agent)                                        │
│  Pro curates research → ANALYSIS/CONTEXT_BRIEF.md                      │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 3: DIALECTIC (Opus Planner ↔ Pro Challenger)                    │
│  3-5 exchange rounds → DIALECTIC_BRIEF/                                │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 4: GAP ANALYSIS (Pro orchestrates mixed validators)             │
│  Pro spawns 2 Flash + 2 Opus validators → ANALYSIS/GAP_ANALYSIS.md     │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 5: CONSENSUS GAP HUNT (Flash triad)                             │
│  3 Flash scouts same prompt → ANALYSIS/CONSENSUS_GAPS.md               │
├────────────────────────────────────────────────────────────────────────┤
│  OUTPUT: ${TASK_SLUG}_PLAN_Session/${OUTPUT_NAME}                      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Session Folder Structure

```
.claude/PM/plans/${session-slug}/
├── ORCHESTRATOR_LOG.md            # Flight Recorder
├── TASK_UNDERSTANDING.md          # Phase 0
├── RESEARCH_FILES/                # Phase 1
│   ├── R1_CODEBASE.md
│   ├── R2_ADR_SSOT.md
│   └── R3_PLANS_HISTORY.md
├── ANALYSIS/                      # Phase 2, 4, 5
│   ├── CONTEXT_BRIEF.md
│   ├── GAP_ANALYSIS.md
│   └── CONSENSUS_GAPS.md
├── GAP_HUNT/                      # Phase 5 raw
│   ├── G1_SCOUT.md
│   ├── G2_SCOUT.md
│   └── G3_SCOUT.md
├── DIALECTIC_BRIEF/               # Phase 3
│   └── DIALOGUE_LOG.md
└── ${OUTPUT_NAME}                 # Final
```

---

## Proxy Configuration

```bash
# Flash agents (research, validation) - Port 2405
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "PROMPT"

# Pro agents (synthesis, challenger) - Port 2406
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "PROMPT"

# Opus agents (orchestrator) - Port 2408
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "PROMPT"
```

---

## Orchestrator Execution

When this command is invoked, spawn a background Opus orchestrator:

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "
# Dialectic Planning Orchestrator

You are the orchestrator for a dialectic planning session.

## Session Parameters
- TOPIC: ${TOPIC}
- MODE: ${MODE}
- EXTERNAL_RESEARCH: ${EXTERNAL_RESEARCH}
- OUTPUT_NAME: ${OUTPUT_NAME:-APPROVED_PLAN.md}
- WORKSPACE: $(pwd)

## IMPORTANT: Execute All Phases Sequentially

You MUST complete ALL phases in order. Do not stop after Phase 0.
After each phase, immediately proceed to the next.

---

## PHASE 0: UNDERSTAND

First, generate TASK_SLUG from TOPIC (lowercase, underscores, no special chars, max 50 chars).

Create session folder:
\`\`\`bash
mkdir -p .claude/PM/plans/\${SESSION_SLUG}/{RESEARCH_FILES,ANALYSIS,DIALECTIC_BRIEF,GAP_HUNT}
\`\`\`

Write TASK_UNDERSTANDING.md with:
- Problem Statement
- Success Criteria (measurable)
- Constraints (MUST/MUST NOT/SHOULD)
- Scope (IN/OUT)
- Key Questions

Initialize ORCHESTRATOR_LOG.md:
\`\`\`
# ORCHESTRATOR FLIGHT LOG
# Session: \${TASK_SLUG}
# Started: [timestamp]

[timestamp] [INIT] Session initialized. Topic: \${TOPIC}
\`\`\`

---

## PHASE 1: RESEARCH (Parallel Flash Agents)

Spawn 3 Flash researchers IN PARALLEL. Use the Bash tool to run all 3 simultaneously.

### R1: Codebase Researcher
\`\`\`bash
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p \"
You are R1_CODEBASE researcher.

TOPIC: \${TOPIC}
SESSION_PATH: .claude/PM/plans/\${SESSION_SLUG}

Read \${SESSION_PATH}/TASK_UNDERSTANDING.md first.

Search the codebase for files relevant to this topic:
1. Find existing implementations, patterns, interfaces
2. Identify code that would be affected by changes
3. Note dependencies and coupling

Write your findings to: \${SESSION_PATH}/RESEARCH_FILES/R1_CODEBASE.md

Format:
## Relevant Files
| File | Why Relevant | Key Functions/Classes |

## Existing Patterns
- Pattern: [description]

## Impact Analysis
- Files that would change: [list]
- Dependencies: [what depends on what]

## Key Code Snippets
[Include relevant code with file:line references]
\"
\`\`\`

### R2: ADR & SSoT Researcher
\`\`\`bash
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p \"
You are R2_ADR_SSOT researcher.

TOPIC: \${TOPIC}
SESSION_PATH: .claude/PM/plans/\${SESSION_SLUG}

Read \${SESSION_PATH}/TASK_UNDERSTANDING.md first.

Find architectural decisions and specifications:
1. Search for ADRs in docs/adr/ or similar locations
2. Check for BACKLOG.md, TODO.md, or project plans
3. Identify constraints from existing decisions

Write your findings to: \${SESSION_PATH}/RESEARCH_FILES/R2_ADR_SSOT.md

Format:
## Relevant ADRs
| ADR | Title | Key Decision | Impact on Topic |

## Architectural Constraints
- MUST: [required - cite source]
- MUST NOT: [forbidden - cite source]
- SHOULD: [recommended - cite source]

## Conflicts or Tensions
[Any conflicts between ADRs]
\"
\`\`\`

### R3: Plans & History Researcher
\`\`\`bash
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p \"
You are R3_PLANS_HISTORY researcher.

TOPIC: \${TOPIC}
SESSION_PATH: .claude/PM/plans/\${SESSION_SLUG}

Read \${SESSION_PATH}/TASK_UNDERSTANDING.md first.

Check project history:
1. BACKLOG.md or TODO.md - backlog items
2. CHANGELOG.md or recent git commits - what changed recently
3. CLAUDE.md or project docs - recent context

Write your findings to: \${SESSION_PATH}/RESEARCH_FILES/R3_PLANS_HISTORY.md

Format:
## Current Work Context
- Active stories: [list]
- Relevant tasks: [list]

## Backlog Items
| Item | Relevance | Priority |

## Historical Context
- Previous attempts: [if any]
- Related changes: [from CHANGELOG]

## Blockers or Dependencies
[Anything that might block this work]
\"
\`\`\`

**WAIT for all 3 researchers to complete before proceeding.**

Log: \`[PHASE] Phase 1 complete. 3 research files written.\`

---

## PHASE 2: SYNTHESIS (Pro Agent)

Spawn a Pro agent to synthesize research:

\`\`\`bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p \"
You are the Research Synthesizer.

SESSION_PATH: .claude/PM/plans/\${SESSION_SLUG}

Read these files:
- \${SESSION_PATH}/TASK_UNDERSTANDING.md
- \${SESSION_PATH}/RESEARCH_FILES/R1_CODEBASE.md
- \${SESSION_PATH}/RESEARCH_FILES/R2_ADR_SSOT.md
- \${SESSION_PATH}/RESEARCH_FILES/R3_PLANS_HISTORY.md

Synthesize into a CONTEXT_BRIEF.md that:
1. Summarizes key findings (not raw data)
2. Highlights constraints and requirements
3. Notes conflicts or tensions
4. Lists open questions

Write to: \${SESSION_PATH}/ANALYSIS/CONTEXT_BRIEF.md

Format:
# Context Brief

## Executive Summary
[2-3 sentences]

## Key Findings
### From Codebase
[Curated highlights]

### From ADRs
[Architectural constraints]

### From History
[Relevant context]

## Constraints Summary
| Constraint | Source | Impact |

## Open Questions
- [Questions the plan must answer]

## Risks Identified
- [Risks found during research]
\"
\`\`\`

Log: \`[SYNTHESIS] Pro completed CONTEXT_BRIEF.md\`

---

## PHASE 3: DIALECTIC (Opus Planner ↔ Pro Challenger)

Now YOU (Opus) read CONTEXT_BRIEF.md and propose an initial plan.

For each exchange round (3-5 rounds):

1. YOU propose/refine the plan in DIALOGUE_LOG.md
2. Spawn Pro challenger:

\`\`\`bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p \"
You are the Devil's Advocate Challenger.

SESSION_PATH: .claude/PM/plans/\${SESSION_SLUG}

Read:
- \${SESSION_PATH}/TASK_UNDERSTANDING.md
- \${SESSION_PATH}/ANALYSIS/CONTEXT_BRIEF.md
- \${SESSION_PATH}/DIALECTIC_BRIEF/DIALOGUE_LOG.md

## Rules
- R1: Expand AND challenge (not just one)
- R2: Cite evidence (file:line or ADR-NNNN)
- R3: Explain disagreements with evidence
- R4: Acknowledge valid points: 'AGREED: [point]'

## Your Task
Challenge the latest plan proposal:
1. What assumptions are untested?
2. What could go wrong?
3. What's missing?
4. What's over-engineered?

Write your challenge. Be constructive but rigorous.
Start with 'AGREED:' for valid points, then 'CHALLENGE:' for concerns.
\"
\`\`\`

3. Read challenger response, update plan, repeat

Stop when: ≥80% agreement OR 5 exchanges reached.

Log each: \`[EXCHANGE] Round N complete. Agreement: X%\`

---

## PHASE 4: GAP ANALYSIS (Pro + Mixed Validators: 2 Flash + 2 Opus)

Spawn a Pro agent to orchestrate validation with mixed model perspectives:

\`\`\`bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p \"
You are the Gap Analysis Orchestrator.

SESSION_PATH: .claude/PM/plans/\${SESSION_SLUG}

Read the current plan in \${SESSION_PATH}/DIALECTIC_BRIEF/DIALOGUE_LOG.md

Your task:
1. Identify 4 validation categories relevant to THIS plan
   (Examples: Breaking Changes, Data Migration, Security, Performance, User Impact, Rollback)
2. Spawn validators IN PARALLEL - use MIXED MODELS for synergy:
   - 2 Flash validators (port 2405) - quick pattern recognition
   - 2 Opus validators (port 2408) - deeper reasoning
3. Collect their findings
4. Write synthesis to \${SESSION_PATH}/ANALYSIS/GAP_ANALYSIS.md

Spawn validators like this:
\\\`\\\`\\\`bash
# Flash validators (2)
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p 'Validate [CATEGORY] for plan at [SESSION_PATH]. Read DIALOGUE_LOG.md. Report gaps, risks, concerns.'

# Opus validators (2) - for deeper analysis on complex categories
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p 'Validate [CATEGORY] for plan at [SESSION_PATH]. Read DIALOGUE_LOG.md. Report gaps, risks, concerns.'
\\\`\\\`\\\`

Output format for GAP_ANALYSIS.md:
# Gap Analysis

## Validation Categories
| Category | Validator (Model) | Finding | Severity |

## Critical Gaps
[High severity items]

## Moderate Concerns
[Medium severity items]

## Minor Notes
[Low severity items]

## Recommendations
[How to address gaps]
\"
\`\`\`

Log: \`[PHASE] Phase 4 complete. Gap analysis written.\`

---

## PHASE 5: CONSENSUS GAP HUNT (Flash Triad)

Spawn 3 Flash scouts IN PARALLEL with the SAME prompt:

\`\`\`bash
# Run all 3 in parallel
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p \"
You are Gap Hunter Scout.

SESSION_PATH: .claude/PM/plans/\${SESSION_SLUG}

Read:
- \${SESSION_PATH}/TASK_UNDERSTANDING.md
- \${SESSION_PATH}/DIALECTIC_BRIEF/DIALOGUE_LOG.md
- \${SESSION_PATH}/ANALYSIS/GAP_ANALYSIS.md

Find gaps, risks, or blind spots that were MISSED.

Focus on:
1. Unstated assumptions - What does this plan assume?
2. Missing error paths - What happens when X fails?
3. Integration gaps - How do pieces connect?
4. Scope creep signals - Growing beyond intent?
5. Testability - Can success criteria be verified?

Output:
gaps_found:
  - gap: [description]
    severity: [high|medium|low]
    evidence: [file:line or quote]

blind_spots:
  - [area under-examined]

concerns:
  - [anything that feels off]

Be brutal. Better to flag too much than miss something.

Write to: \${SESSION_PATH}/GAP_HUNT/G[N]_SCOUT.md (where N is 1, 2, or 3)
\"
\`\`\`

After all 3 complete, synthesize consensus:
- 2+ scouts agree = HIGH CONFIDENCE gap
- 1 scout only = WORTH NOTING
- Contradictions = NEEDS REVIEW

Write to: \${SESSION_PATH}/ANALYSIS/CONSENSUS_GAPS.md

Log: \`[CONSENSUS] Triad complete. X high-confidence, Y unique, Z conflicts.\`

---

## FINAL OUTPUT

Read CONSENSUS_GAPS.md and finalize the plan:

1. Incorporate HIGH CONFIDENCE gaps
2. Note UNIQUE FINDINGS as 'Considerations'
3. Flag CONFLICTS for HD review

Write final plan to: \${SESSION_PATH}/\${OUTPUT_NAME}

Format:
# [Plan Title]

## Summary
[What this plan accomplishes]

## Implementation Steps
| Step | Description | Dependencies | Files Affected |

## Risk Mitigation
| Risk | Mitigation |

## Success Criteria
- [ ] [Measurable criterion]

## Considerations
[From unique findings]

## Open Items for HD
[Conflicts or decisions needed]

---

Log: \`[DONE] Session complete. Output: \${OUTPUT_NAME}\`

Report completion to HD.
"
```

---

## The Dialectic Mantra

```
I understand before I research.
I curate before I reason.
I expand before I challenge.
I steel-man before I critique.
I cite evidence, not opinions.
I synthesize what works.
I validate before I deliver.
Better Data = Better Thinking.
```

---

## Related

| Related | When to Use Instead |
|---------|---------------------|
| Direct implementation | Single-file changes, bug fixes |
| HD story orchestration | Full workflow with multiple stories |

---

**Version:** V2.4.0
**Updated:** 2025-12-30
**Status:** Production-ready (Self-contained prompts)
