---
version: V1.2.0
status: current
timestamp: 2026-01-01
tags: [command, decision-support, multi-agent, council, brainstorming, consensus]
description: "Council-based decision support - Dynamic experts collaborate to map options and help you think"
---

# /think-tank - The Council

**Philosophy:** Help YOU think, not tell you what to think.

**Purpose:** Convene a council of dynamically-cast experts who collaborate to map the decision space, surface trade-offs, and illuminate blind spots - so YOU can make an informed decision.

---

## Quick Start

### New Session
```markdown
/think-tank

PROBLEM: [What decision or problem needs thinking through]

MY_LEAN: [What I'm currently thinking, if any]

CONSTRAINTS:
- [Budget, time, team size, tech stack, etc.]
- [Must-haves vs nice-to-haves]

CONTEXT:
- [Relevant background]
- [Why this matters now]
```

### Resume / Redirect Existing Session
```markdown
# Resume with new information
/think-tank "database selection" --new-info "We hit connection pool limits"

# Redirect the discussion
/think-tank "database selection" --redirect "Explore the cost implications more"

# Ask a what-if
/think-tank "database selection" --what-if "Assume we have 2x the budget"
```

### Batch Mode Behavior (Default)
1. Command runs council for 4 exchanges
2. Generates draft Decision Map
3. **Exits** - does not block waiting for input
4. You review files in `.claude/PM/think-tank/{topic-slug}_{date}/`
5. Run with `--redirect` or `--new-info` to continue

---

## Core Concept: The Council (Not a Debate)

| Debate Model | Council Model |
|--------------|---------------|
| Agents fight to win | Agents collaborate to map options |
| Output: Winner's recommendation | Output: Decision Map with trade-offs |
| Fixed adversarial roles | Dynamic personas based on problem domain |
| Convergence = one agrees | Convergence = complete picture |

---

## The Cast

| Role | Purpose | Model |
|------|---------|-------|
| **You (HD)** | The Chair | Human |
| **Orchestrator (Claude)** | Moderator - casts agents, manages flow, injects simplicity/risk prompts | Opus |
| **Domain Expert** | The "What's Possible" - Deep subject knowledge | Opus (2408) |
| **Pragmatist** | The "What's Realistic" - Costs, time, difficulty, hiring | Pro (2406) |
| **Flash Scouts** | The Library - On-demand research | Flash (2405) |

### Dynamic Casting Examples

| Problem | Domain Expert | Pragmatist |
|---------|---------------|------------|
| "Should I switch backend to Rust?" | Senior Systems Architect (Performance, Safety) | Engineering Manager (Hiring, Velocity, Learning Curve) |
| "How should I market this AI tool?" | Brand Strategist (Positioning, Messaging) | Growth Hacker (Acquisition, CAC, Quick Wins) |
| "Should I use microservices or monolith?" | Distributed Systems Engineer (Scalability, Resilience) | Startup CTO (Time-to-market, Team Size, Ops Burden) |
| "Which database for this use case?" | Database Architect (Performance, Consistency) | DevOps Lead (Operations, Backup, Cost) |

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: INTAKE                                                 │
│  You provide: Problem + Constraints + Your current lean         │
│  I ask: Clarifying questions if needed                          │
│  → 00_BRIEFING.md                                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: CASTING                                                │
│  I analyze domain, define 2 expert personas                     │
│  → 01_CAST.md (you approve if I'm uncertain)                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: CONTEXT GATHERING (if needed)                          │
│  Flash scouts gather baseline facts from code/docs/web          │
│  → 02_KNOWLEDGE_BASE/                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: COUNCIL SESSION                                        │
│  "Yes, and..." / "Yes, but..." collaborative exchanges          │
│                                                                 │
│  Every 3-4 turns:                                               │
│    • I summarize the state                                      │
│    • I inject: "Risk?" "Simpler way?" "What if X fails?"        │
│    • I ask YOU: "Any input or redirection?"                     │
│                                                                 │
│  Agents can REQUEST:                                            │
│    • Research → I spawn Flash scout                             │
│    • User clarification → I ask you                             │
│                                                                 │
│  → 03_TRANSCRIPT.md                                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: DECISION MAP                                           │
│  Agents co-author structured output with options + trade-offs   │
│  → 04_DECISION_MAP.md                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5.5: CONSENSUS VALIDATION                                 │
│  4 Independent Validators (2 Pro + 2 Opus) review Decision Map  │
│                                                                 │
│  Feedback Aggregation:                                          │
│    • 3-4 agents same issue → MUST FIX                           │
│    • 2 agents same issue → Orchestrator decides                 │
│    • 1 agent unique issue → IGNORE (no consensus)               │
│                                                                 │
│  If consensus issues found → Council corrects → Loop            │
│  → 04B_VALIDATION_LOG.md                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: YOUR REVIEW                                            │
│                                                                 │
│  You can:                                                       │
│  • DONE - Decision Map complete, archive session                │
│  • REDIRECT - "Consider X constraint" → Back to Step 4          │
│  • WHAT IF - "Assume infinite budget" → Back to Step 4          │
│  • EXPAND - "Dig deeper on Path B" → Back to Step 4             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Topic Workspace Structure

The folder is a **persistent workspace** for a topic, not a one-shot session. You can return days or weeks later to continue exploring as you implement and learn.

**Naming:** `think-tank_{TOPIC_SLUG}_{YYYYMMDD}` (date of first session)

```
.claude/PM/think-tank/database_selection_20260101/
├── 00_BRIEFING.md              # Original problem (can be amended)
├── 01_CAST.md                  # Expert personas (may evolve)
├── 02_KNOWLEDGE_BASE/          # Accumulates over time
│   ├── scout_001_initial.md         # Day 1 research
│   ├── scout_002_postgres_deep.md   # Added later
│   └── scout_003_from_impl.md       # Learnings from implementation
├── 03_SESSIONS/                # Multiple council conversations
│   ├── session_001.md               # Initial exploration
│   ├── session_002.md               # After POC findings
│   └── session_003.md               # New scaling concerns
├── 04_DECISION_MAP.md          # Living document - updated each session
├── 04B_VALIDATION/             # Consensus validation artifacts
│   ├── round_001/                   # Each validation round
│   │   ├── validator_pro_1.md       # Individual validator feedback
│   │   ├── validator_pro_2.md
│   │   ├── validator_opus_1.md
│   │   ├── validator_opus_2.md
│   │   └── SYNTHESIS.md             # Flash-synthesized consensus
│   └── VALIDATION_LOG.md            # Summary of all rounds
├── 05_LEARNINGS.md             # What implementation taught us
└── STATE.yaml                  # Tracks all sessions, decisions, open items
```

### The Lifecycle

```
Day 1: /think-tank "database selection"
       → Initial council session → Decision Map v1
       → You start implementing with PostgreSQL

Day 3: /think-tank "database selection" (RESUME)
       → "We hit connection pool limits in POC"
       → Council reconvenes with new data
       → Decision Map v2: Updated with PgBouncer recommendation

Day 7: /think-tank "database selection" (RESUME)
       → "Found we need full-text search"
       → Scout researches Postgres FTS vs Elasticsearch
       → Decision Map v3: Search considerations added
```

---

## Proxy Configuration

```bash
# Flash agents (research scouts) - Port 2405
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "PROMPT"

# Pro agents (Pragmatist) - Port 2406
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "PROMPT"

# Opus agents (Domain Expert) - Port 2408
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "PROMPT"

# Opus orchestrator (if needed to delegate orchestration) - Port 2408
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "PROMPT"
```

---

## Orchestrator Execution Protocol

When `/think-tank` is invoked, I (HD/Orchestrator) execute the following:

### STEP 1: INTAKE

1. Parse user input for PROBLEM, MY_LEAN, CONSTRAINTS, CONTEXT
2. **Check for existing topic workspace:**
   ```bash
   ls -d .claude/PM/think-tank/${TOPIC_SLUG}_* 2>/dev/null
   ```
   - If found: Ask "Resume existing workspace or start fresh?"
   - If resume: Load STATE.yaml, show last Decision Map version, ask for new context
3. If any critical info missing, ask clarifying questions
4. Generate TOPIC_SLUG (lowercase, underscores, max 30 chars)
5. Create or reuse workspace folder:

```bash
# New workspace (date only, no timestamp)
mkdir -p .claude/PM/think-tank/${TOPIC_SLUG}_$(date +%Y%m%d)/{02_KNOWLEDGE_BASE,03_SESSIONS}
```

6. Write or amend `00_BRIEFING.md`:

```markdown
# Problem Briefing

## The Decision/Problem
[From user input]

## Your Current Lean
[What user is thinking, or "No strong opinion yet"]

## Constraints
| Constraint | Type | Source |
|------------|------|--------|
| [constraint] | MUST/SHOULD/NICE | [user stated] |

## Context
[Background information]

## Success Criteria
[How will we know the Decision Map is useful?]
```

8. Initialize or update `STATE.yaml`:

```yaml
# STATE.yaml - Topic Workspace State

topic: ${TOPIC_SLUG}
created: ${YYYYMMDD}
last_active: ${YYYYMMDD}
status: active  # active | paused | decided | archived

# Current session tracking
current_session:
  number: 1
  step: 1  # 1=intake, 2=cast, 3=research, 4=council, 5=decision_map, 6=review
  started: ${timestamp}

# All sessions in this workspace
sessions:
  - number: 1
    date: ${YYYYMMDD}
    trigger: "initial"  # initial | new_info | implementation_issue | reevaluate
    summary: "Initial exploration of ${TOPIC}"
    outcome: "pending"  # pending | decision_updated | no_change | deferred

# Decision history (living document versions)
decisions:
  - version: 1
    date: ${YYYYMMDD}
    recommendation: null
    confidence: null

# Consensus validation tracking
validation:
  current_round: 0
  max_rounds: 5  # Safety limit before escalating to user
  status: pending  # pending | in_progress | approved | escalated
  rounds: []
  # Each round entry:
  # - round: 1
  #   validators: [pro_1, pro_2, opus_1, opus_2]
  #   consensus_issues: ["issue text"]
  #   ignored_issues: ["unique issue from 1 validator"]
  #   tiebreaker_decisions: ["2/4 issue → orchestrator decision"]
  #   outcome: correction_required | approved

# Learnings captured during implementation
learnings: []

# Open questions carried forward
open_questions: []
```

---

### STEP 2: CASTING

Analyze the problem domain and define two expert personas.

**Casting Criteria:**
- **Domain Expert**: Who has the deepest SUBJECT MATTER knowledge for this topic?
- **Pragmatist**: Who would apply REALITY CHECKS (cost, time, difficulty, team, operations)?

Write `01_CAST.md`:

```markdown
# Council Cast

## Problem Domain Analysis
[Brief analysis of what expertise is needed]

## Domain Expert: [Title]
**Focus:** [What they optimize for]
**Perspective:** [How they see the world]
**Will Challenge:** [What they'll push back on]

## Pragmatist: [Title]
**Focus:** [What they optimize for]
**Perspective:** [How they see the world]
**Will Challenge:** [What they'll push back on]

## Cast Confidence: [HIGH/MEDIUM]
[If MEDIUM, ask user for approval before proceeding]
```

**If confidence is MEDIUM**, ask user:
> "I've cast [Expert A] and [Expert B] for this problem. Does that feel right, or would different perspectives be more useful?"

---

### STEP 3: CONTEXT GATHERING

Determine if research is needed based on the problem type.

**Research Triggers:**
- Technical decision → Search codebase for existing patterns
- Architecture decision → Search ADRs for constraints
- External technology → Web search for comparisons/benchmarks
- Business decision → May skip if user provided enough context

Spawn Flash scouts IN PARALLEL:

```bash
# Scout 1: Codebase (if technical)
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "
You are a research scout for a decision-making council.

SESSION_PATH: ${SESSION_PATH}
PROBLEM: ${PROBLEM}

Read ${SESSION_PATH}/00_BRIEFING.md first.

Search the codebase for:
1. Existing implementations relevant to this decision
2. Patterns that would be affected
3. Dependencies and constraints

Write findings to: ${SESSION_PATH}/02_KNOWLEDGE_BASE/scout_codebase.md

Format:
## Relevant Code
| File | Relevance | Key Finding |

## Existing Patterns
- [Pattern with file:line reference]

## Constraints from Code
- [What the code currently assumes/requires]
"

# Scout 2: Documentation/ADRs (if architectural)
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "
You are a research scout for a decision-making council.

SESSION_PATH: ${SESSION_PATH}
PROBLEM: ${PROBLEM}

Search for architectural decisions and documentation:
1. ADRs in project's docs/adr/ folder or similar
2. Project docs, README files
3. CLAUDE.md for project constraints

Write findings to: ${SESSION_PATH}/02_KNOWLEDGE_BASE/scout_docs.md

Format:
## Relevant ADRs
| ADR | Decision | Impact on Problem |

## Documentation Findings
- [Key info with source]

## Stated Constraints
- [MUST/MUST NOT from docs]
"

# Scout 3: Web (if external technology/comparison needed)
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "
You are a research scout for a decision-making council.

PROBLEM: ${PROBLEM}

Search the web for:
1. Comparisons and benchmarks relevant to this decision
2. Industry best practices
3. Common pitfalls and lessons learned
4. Recent developments (2025-2026)

Write findings to: ${SESSION_PATH}/02_KNOWLEDGE_BASE/scout_web.md

Format:
## Key Findings
| Source | Finding | Relevance |

## Industry Consensus
- [What most sources agree on]

## Contrarian Views
- [Minority opinions worth considering]

## Recent Developments
- [Anything new that changes the calculus]
"
```

Update STATE.yaml: `current_session.step: 3`

---

### STEP 4: COUNCIL SESSION

This is the core collaborative exchange. I orchestrate the conversation between Domain Expert and Pragmatist.

**Initialize session file in 03_SESSIONS/:**

```markdown
# Session ${SESSION_NUMBER}: ${TRIGGER_REASON}

**Date:** ${YYYYMMDD}
**Trigger:** ${TRIGGER}  # initial | new_info | implementation_issue | reevaluate
**New Context:** ${WHAT_CHANGED_SINCE_LAST}

---

## Round 1

### Domain Expert ([Title])
[Their opening perspective]

### Pragmatist ([Title])
[Their response - "Yes, and..." or "Yes, but..."]

### Orchestrator Summary
[Key points, tensions identified]

### Orchestrator Prompts
- [Simplicity check / Risk check / Missing angle]

---
```

**For RESUME sessions**, include context from previous sessions:
- Load `03_SESSIONS/SUMMARY_LATEST.md` (rolling summary of all previous sessions)
- Load `04_DECISION_MAP.md` (current version)
- Load `05_LEARNINGS.md` (if exists)
- Ask: "What's changed since last session? What new info do you have?"

---

### STEP 3.5: BRIEFING PACK SYNTHESIS (Before Council)

**Risk Mitigation:** Flash scouts may return conflicting information. Synthesize before council sees it.

After all scouts complete, spawn a Pro agent to create unified briefing:

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "
You are the Research Synthesizer.

SESSION_PATH: ${SESSION_PATH}

Read all files in ${SESSION_PATH}/02_KNOWLEDGE_BASE/

Your task:
1. Identify AGREEMENTS - findings multiple sources confirm
2. Identify CONFLICTS - where sources contradict
3. Identify GAPS - what wasn't covered
4. Create a unified briefing for the council

Write to: ${SESSION_PATH}/02_KNOWLEDGE_BASE/BRIEFING_PACK.md

Format:
# Research Briefing Pack

## Consensus Findings (High Confidence)
- [Finding]: [Sources that agree]

## Conflicting Information (Needs Council Discussion)
- [Topic]: Source A says X, Source B says Y
- Council should weigh: [what factors matter]

## Research Gaps
- [What wasn't found that might matter]

## Key Data Points
| Metric | Value | Source |
"
```

---

### Council Exchange Protocol

**Context Window Management:** Agents read summaries, not full transcripts.

For each round, spawn agents sequentially:

```bash
# Domain Expert turn (Opus - deeper reasoning)
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "
You are the Domain Expert on the Council: ${EXPERT_TITLE}

SESSION_PATH: ${SESSION_PATH}

## Your Persona
Focus: ${EXPERT_FOCUS}
Perspective: ${EXPERT_PERSPECTIVE}

## Council Rules
1. Use 'Yes, and...' to BUILD on valid points
2. Use 'Yes, but...' to ADD nuance or concerns
3. NEVER fight to win - help map the decision space
4. Reference evidence from BRIEFING_PACK.md
5. Acknowledge good points: 'AGREED: [point]'
6. Surface trade-offs, not just your preference

## Your Task
Read (in this order):
- ${SESSION_PATH}/00_BRIEFING.md (the problem)
- ${SESSION_PATH}/02_KNOWLEDGE_BASE/BRIEFING_PACK.md (synthesized research)
- ${SESSION_PATH}/03_SESSIONS/SUMMARY_LATEST.md (previous session summaries, if exists)
- ${SESSION_PATH}/03_SESSIONS/session_current.md (THIS session's transcript so far)

Provide your perspective. What options exist? What are the trade-offs?

If you need more information: 'RESEARCH_REQUEST: [what you need]'
If you need user clarification: 'USER_QUESTION: [your question]'
"

# Pragmatist turn
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "
You are the Pragmatist on the Council: ${PRAGMATIST_TITLE}

SESSION_PATH: ${SESSION_PATH}

## Your Persona
You are the **Guardian of Resources**. Your job is to protect the user from over-engineering.

Focus: ${PRAGMATIST_FOCUS}
Perspective: ${PRAGMATIST_PERSPECTIVE}

## Council Rules
1. Use 'Yes, and...' to BUILD on valid points
2. Use 'Yes, but...' to ADD practical concerns
3. NEVER fight to win - help map the decision space
4. Whenever the Domain Expert suggests a 'best practice,' ask:
   - 'Do we have the team to maintain this?'
   - 'Is this overkill for the current scale?'
   - 'What is the migration cost?'
5. Be the voice of constraints. Not mean, but ruthlessly practical.

## MANDATORY: Pre-Mortem Analysis
Before responding, answer this internally:
'Assume we chose the Expert's recommended path and it FAILED 6 months from now. Why did it fail?'
Include this failure mode analysis in your response.

## Your Task
Read (in this order):
- ${SESSION_PATH}/00_BRIEFING.md
- ${SESSION_PATH}/02_KNOWLEDGE_BASE/BRIEFING_PACK.md
- ${SESSION_PATH}/03_SESSIONS/SUMMARY_LATEST.md (if exists)
- ${SESSION_PATH}/03_SESSIONS/session_current.md (including Expert's latest)

Respond to the Domain Expert. Apply reality checks. Surface the Pre-Mortem failure modes.

If you need more information: 'RESEARCH_REQUEST: [what you need]'
If you need user clarification: 'USER_QUESTION: [your question]'
"
```

**After every round, I:**

1. Append exchange to `03_SESSIONS/session_NNN.md`
2. After every 3-4 exchanges, write `03_SESSIONS/SUMMARY_LATEST.md`:
   - Rolling summary of ALL sessions (not raw transcript)
   - Max 2000 tokens - curated key points only

**Batch Mode (Default):**
- Run 4 council exchanges automatically
- Generate draft Decision Map
- PAUSE and exit
- User reviews output files
- Resume with: `/think-tank [topic] --redirect "explore cost more"`

**Handle RESEARCH_REQUEST:** Spawn Flash scout, add to BRIEFING_PACK.md, share with both.

**Handle USER_QUESTION:** Log in STATE.yaml `open_questions`, present at session end.

**Convergence Check:**
- Council converges when both agree on the option space
- Target: 2-3 distinct paths with trade-offs understood
- Max rounds: 6 (then force Decision Map generation)

Update STATE.yaml after each round.

---

### STEP 5: DECISION MAP

When council converges OR max rounds reached, co-author the Decision Map.

Spawn Pro agent to synthesize:

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "
You are the Decision Map synthesizer.

SESSION_PATH: ${SESSION_PATH}

Read ALL session files:
- 00_BRIEFING.md (the original problem and constraints)
- 01_CAST.md (who was on the council)
- 02_KNOWLEDGE_BASE/BRIEFING_PACK.md (synthesized research)
- 03_SESSIONS/session_NNN.md (current session transcript)
- 03_SESSIONS/SUMMARY_LATEST.md (previous sessions summary, if exists)

Synthesize into a Decision Map that helps the USER make a decision.

Write to: ${SESSION_PATH}/04_DECISION_MAP.md

Use this EXACT format:

---
# Decision Map: [Problem Title]

> Living document. Version history at top.

| Version | Date | Session | Change |
|---------|------|---------|--------|
| v1 | [date] | 1 | Initial decision |

## The Core Tension
[What's the fundamental trade-off? One sentence.]

## Your Constraints (as understood)
- [Constraint 1 from briefing]
- [Constraint 2]

## Blind Spots Identified
[What did the user forget to consider? What assumptions were challenged?]

## The Options

### Path A: [The Aggressive/Ambitious Approach]
**Summary**: [One sentence]
**Upside**: [What you gain]
**Downside**: [What you give up]
**Risk**: [What could go wrong]
**Reversibility**: [HIGH/MED/LOW] - [Type 1 or Type 2 decision? How hard to undo?]
**Pre-Mortem**: If this fails in 6 months, it's because: [failure mode from Pragmatist analysis]
**When to choose**: [Under what conditions is this best?]

### Path B: [The Conservative/Safe Approach]
**Summary**: [One sentence]
**Upside**: [What you gain]
**Downside**: [What you give up]
**Risk**: [What could go wrong]
**Reversibility**: [HIGH/MED/LOW] - [How hard to undo?]
**Pre-Mortem**: If this fails in 6 months, it's because: [failure mode]
**When to choose**: [Under what conditions is this best?]

### Path C: [The Simple/Minimum Viable Approach]
**Summary**: [The 'just enough' option - simplest way to achieve the goal]
**Upside**: [Lowest complexity, fastest to validate]
**Downside**: [What you defer or sacrifice]
**Risk**: [What could go wrong]
**Reversibility**: HIGH - [Should be easy to pivot from]
**Pre-Mortem**: If this fails in 6 months, it's because: [failure mode]
**When to choose**: [When you need to move fast or validate assumptions first]

## Council's Assessment
Given your stated constraints, the council believes **Path [X]** aligns best because:
1. [Reason tied to your constraint]
2. [Reason tied to your context]

However, if [condition changes], reconsider **Path [Y]**.

## Open Questions
[Questions that only the user can answer - values, priorities, risk tolerance]

## What We Didn't Cover
[Topics that came up but weren't fully explored - potential for EXPAND]
---
"
```

Update STATE.yaml: `current_session.step: 5`, `validation.status: in_progress`

---

### STEP 5.5: CONSENSUS VALIDATION

After the Decision Map is generated, spawn 4 independent validators to review it. This catches blind spots and ensures quality before presenting to the user.

**Validator Composition:**
- 2 Pro agents (Port 2406) - faster, cost-effective
- 2 Opus agents (Port 2408) - deeper reasoning

**Validation Protocol:**

1. **Create validation round folder:**
```bash
ROUND_NUM=$(ls -d ${SESSION_PATH}/04B_VALIDATION/round_* 2>/dev/null | wc -l)
ROUND_NUM=$((ROUND_NUM + 1))
mkdir -p ${SESSION_PATH}/04B_VALIDATION/round_$(printf "%03d" $ROUND_NUM)
```

2. **Spawn all 4 validators IN PARALLEL with identical prompts:**

```bash
# Validator prompt (same for all 4)
VALIDATOR_PROMPT="
You are an Independent Validator reviewing a Decision Map produced by a council.

Your job: Review the Decision Map critically and provide feedback.

## Files to Read (in order):
1. ${SESSION_PATH}/00_BRIEFING.md - The original problem and constraints
2. ${SESSION_PATH}/02_KNOWLEDGE_BASE/BRIEFING_PACK.md - Research findings
3. ${SESSION_PATH}/04_DECISION_MAP.md - The Decision Map to validate

## Validation Criteria:
1. **Completeness** - Does the map address all stated constraints?
2. **Logical Soundness** - Are the trade-offs accurately represented?
3. **Blind Spots** - Did the council miss obvious considerations?
4. **Accuracy** - Are factual claims supported by the research?
5. **Actionability** - Can the user actually make a decision from this?

## Your Response Format:

### VERDICT: [APPROVED | NOT_APPROVED]

### FEEDBACK_ITEMS:
(List specific issues. Be concrete. If APPROVED with no issues, write 'None')

- ISSUE_1: [Category: Completeness|Logic|BlindSpot|Accuracy|Actionability]
  Description: [What's wrong]
  Severity: [CRITICAL|MAJOR|MINOR]
  Suggestion: [How to fix]

- ISSUE_2: ...

### RATIONALE:
[1-2 sentences explaining your verdict]
"

# Pro Validator 1
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "${VALIDATOR_PROMPT}

Write your response to: ${SESSION_PATH}/04B_VALIDATION/round_${ROUND_NUM}/validator_pro_1.md
" &

# Pro Validator 2
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "${VALIDATOR_PROMPT}

Write your response to: ${SESSION_PATH}/04B_VALIDATION/round_${ROUND_NUM}/validator_pro_2.md
" &

# Opus Validator 1
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "${VALIDATOR_PROMPT}

Write your response to: ${SESSION_PATH}/04B_VALIDATION/round_${ROUND_NUM}/validator_opus_1.md
" &

# Opus Validator 2
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "${VALIDATOR_PROMPT}

Write your response to: ${SESSION_PATH}/04B_VALIDATION/round_${ROUND_NUM}/validator_opus_2.md
" &

wait  # Wait for all 4 to complete
```

3. **Spawn Flash agent to synthesize consensus:**

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "
You are the Consensus Synthesizer.

## Task
Read all 4 validator responses and identify which feedback items have CONSENSUS.

## Files to Read:
- ${SESSION_PATH}/04B_VALIDATION/round_${ROUND_NUM}/validator_pro_1.md
- ${SESSION_PATH}/04B_VALIDATION/round_${ROUND_NUM}/validator_pro_2.md
- ${SESSION_PATH}/04B_VALIDATION/round_${ROUND_NUM}/validator_opus_1.md
- ${SESSION_PATH}/04B_VALIDATION/round_${ROUND_NUM}/validator_opus_2.md

## Consensus Rules:
- **3-4 validators** raised same/similar issue → CONSENSUS_MUST_FIX
- **2 validators** raised same/similar issue → TIEBREAKER_NEEDED
- **1 validator** raised unique issue → NO_CONSENSUS (ignore)

'Same/similar' means the CORE CONCERN is the same, even if worded differently.

## Output Format (write to ${SESSION_PATH}/04B_VALIDATION/round_${ROUND_NUM}/SYNTHESIS.md):

# Consensus Synthesis - Round ${ROUND_NUM}

## Summary
- Total validators: 4
- APPROVED count: [N]
- NOT_APPROVED count: [N]

## CONSENSUS_MUST_FIX (3-4 validators agree)
| Issue | Validators | Category | Severity | Action Required |
|-------|------------|----------|----------|-----------------|
| [issue] | pro_1, pro_2, opus_1 | [cat] | [sev] | [fix] |

## TIEBREAKER_NEEDED (2 validators agree)
| Issue | Validators | Category | Severity | Orchestrator Decision Needed |
|-------|------------|----------|----------|------------------------------|
| [issue] | pro_1, opus_2 | [cat] | [sev] | [context for decision] |

## NO_CONSENSUS (1 validator only - IGNORED)
| Issue | Validator | Category | Why Ignored |
|-------|-----------|----------|-------------|
| [issue] | opus_1 | [cat] | No consensus - single voice |

## RECOMMENDATION
[APPROVED | CORRECTION_REQUIRED | ESCALATE_TO_USER]

If CORRECTION_REQUIRED: The council must address the CONSENSUS_MUST_FIX items.
If ESCALATE_TO_USER: Too many rounds or unresolvable conflict.
"
```

4. **Orchestrator reviews SYNTHESIS.md and decides:**

**If APPROVED (no consensus issues):**
- Update STATE.yaml: `validation.status: approved`
- Proceed to STEP 6: USER REVIEW

**If CORRECTION_REQUIRED:**
- Present to user: "Validators found consensus issues. Council is correcting..."
- Update STATE.yaml: increment `validation.current_round`, log round details
- Check: if `current_round >= max_rounds` → ESCALATE
- Send correction directive to Council (STEP 4 agents):

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "
CORRECTION DIRECTIVE - Validation Round ${ROUND_NUM}

The validators found consensus issues with the Decision Map. You must address them.

## Issues to Fix:
[Copy CONSENSUS_MUST_FIX items from SYNTHESIS.md]

## Tiebreaker Decisions (Orchestrator ruled):
[If any TIEBREAKER_NEEDED items, orchestrator adds decision here]

Read the current Decision Map: ${SESSION_PATH}/04_DECISION_MAP.md

Write UPDATED Decision Map addressing all issues. Increment version number.
Note what changed in the version history table.
"
```

- After correction → Loop back to Step 5.5 (re-validate)

**If ESCALATE_TO_USER:**
- Present to user with full context:
  > **Validation Stalled**
  > After ${ROUND_NUM} rounds, the council and validators cannot reach consensus.
  >
  > **Unresolved Issues:**
  > [List from latest SYNTHESIS.md]
  >
  > **Your Options:**
  > - OVERRIDE - Accept current Decision Map despite issues
  > - GUIDE - Send message to council with your direction
  > - RESET - Restart council session with new framing

---

### User Intervention During Validation

The user can intervene at any point during validation loops:

**User sends message during validation:**
- Orchestrator pauses validation loop
- Presents user message to council as CHAIR_DIRECTIVE
- Council incorporates feedback
- Validation loop restarts from round 1

**User explicitly stops validation:**
- `/think-tank [topic] --skip-validation` - Accept current map
- `/think-tank [topic] --override` - Force approval despite issues

---

### Validation Log

Maintain running log at `${SESSION_PATH}/04B_VALIDATION/VALIDATION_LOG.md`:

```markdown
# Validation History

## Session ${SESSION_NUMBER}

### Round 1
- **Date:** ${timestamp}
- **Validators:** pro_1 ✓, pro_2 ✓, opus_1 ✗, opus_2 ✓
- **Consensus Issues:** 1 (missing constraint consideration)
- **Outcome:** CORRECTION_REQUIRED

### Round 2
- **Date:** ${timestamp}
- **Validators:** pro_1 ✓, pro_2 ✓, opus_1 ✓, opus_2 ✓
- **Consensus Issues:** 0
- **Outcome:** APPROVED

## Summary
- Total Rounds: 2
- Final Status: APPROVED
- Key Corrections Applied: [list]
```

---

### STEP 6: USER REVIEW

Present the Decision Map summary to the user:

> **Council Session Complete**
>
> **Core Tension:** [from Decision Map]
>
> **3 Paths Identified:**
> - Path A: [name] - [one line]
> - Path B: [name] - [one line]
> - Path C: [name] - [one line]
>
> **Council leans toward:** Path [X] given your constraints.
>
> **What would you like to do?**
> - **DECIDE** - Accept recommendation, start implementing
> - **REDIRECT** - "Actually, consider [new constraint/angle]"
> - **WHAT IF** - "What if [assumption changed]?"
> - **EXPAND** - "Dig deeper on [specific path or topic]"
> - **PAUSE** - Save state, come back later

**If DECIDE:**
- Update STATE.yaml:
  ```yaml
  status: decided
  decisions:
    - version: N
      recommendation: "Path X"
      confidence: HIGH
  ```
- Create 05_LEARNINGS.md template for capturing implementation learnings
- Report: "Decision captured. As you implement, run `/think-tank [topic]` again if you discover new considerations."

**If REDIRECT/WHAT IF/EXPAND:**
- Log in current session file
- Resume STEP 4 with new context
- Agents continue with preserved context

**If PAUSE:**
- Update STATE.yaml: `status: paused`
- Report: "Workspace saved. Run `/think-tank [topic]` anytime to resume."

---

### RESUME PROTOCOL

When user invokes `/think-tank` with a topic that has existing workspace:

1. Find workspace: `ls -d .claude/PM/think-tank/${TOPIC_SLUG}_*`
2. Load STATE.yaml
3. Present status:
   > **Existing workspace found:** think-tank_database_selection_20260101
   > **Status:** decided (Path B: PostgreSQL with PgBouncer)
   > **Last active:** 3 days ago
   > **Sessions:** 2
   >
   > What brings you back?
   > - **NEW_INFO** - "We discovered something during implementation"
   > - **ISSUE** - "The decision isn't working as expected"
   > - **REEVALUATE** - "Circumstances changed, need to reconsider"
   > - **FRESH** - "Start over with new framing"

4. If NEW_INFO/ISSUE/REEVALUATE:
   - Increment session number
   - Ask: "What's the new context?"
   - Load previous Decision Map and Learnings
   - Spawn council with full history

5. If FRESH:
   - Archive old workspace: rename to `_archived_${timestamp}`
   - Start new workspace

---

## The Council Mantra

```
We explore, not fight.
We map, not prescribe.
We surface trade-offs, not hide them.
We ask "what's simplest?" before "what's best?"
We ask "what fails?" before "what succeeds?"
We serve the Chair's decision, not our egos.
Better options = better decisions.
```

---

## When to Use vs Other Commands

| Use This | Use Instead |
|----------|-------------|
| Decision with trade-offs | `/hc-plan` - for planning HOW to implement |
| Exploring options | Direct implementation - for obvious/simple tasks |
| Need expert perspectives | `/red-team` - for deep investigation of issues |
| Uncertain about approach | Bug fix - when the problem is clear |

---

## Examples

### Example 1: Technical Decision
```
/think-tank

PROBLEM: Should I migrate our REST API to GraphQL?

MY_LEAN: I think GraphQL would help with our mobile app's over-fetching problem

CONSTRAINTS:
- Team of 3 backend devs (none have GraphQL experience)
- Must maintain REST for existing integrations
- 6-month runway before next funding

CONTEXT:
- Mobile app makes 12+ API calls per screen
- Performance complaints from users
```

### Example 2: Architecture Decision
```
/think-tank

PROBLEM: Microservices vs staying monolith for our growing app

MY_LEAN: None - genuinely unsure

CONSTRAINTS:
- 2 full-stack devs
- Running on single AWS instance currently
- Expecting 10x traffic in 6 months (maybe)

CONTEXT:
- Current monolith is getting slow to deploy
- One service (payments) has different scaling needs
```

---

**Version:** V1.2.0
**Created:** 2026-01-01
**Status:** Ready for use

## V1.2.0 Changelog
- Added STEP 5.5: Consensus Validation with 4 independent validators (2 Pro + 2 Opus)
- Added feedback aggregation by similarity (3-4 = must fix, 2 = tiebreaker, 1 = ignore)
- Added Flash agent for consensus synthesis (context window protection)
- Added correction loop with round tracking and max_rounds safety limit
- Added user intervention during validation (`--skip-validation`, `--override`)
- Added 04B_VALIDATION/ folder structure for validation artifacts
- Added validation tracking to STATE.yaml

## V1.1.0 Changelog
- Added BRIEFING_PACK synthesis step to reconcile conflicting research
- Added Pre-Mortem forcing function to Pragmatist prompt
- Added Rolling Summary (SUMMARY_LATEST.md) to manage context window
- Added Reversibility metric to Decision Map paths
- Added batch mode with `--redirect`, `--new-info`, `--what-if` flags
- Sharpened Pragmatist as "Guardian of Resources"
