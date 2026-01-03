---
version: V2.2.0
status: current
timestamp: 2026-01-03
tags: [command, decision-support, multi-agent, council, planning, adr, roadmap, phases]
description: "Council-based decision support - Dynamic experts collaborate to map options and help you think"
templates: .claude/templates/template-prompts/think-tank/
---

# /think-tank - The Council

**Philosophy:** Help YOU think, not tell you what to think.

**Purpose:** Convene a council of dynamically-cast experts who collaborate to map the decision space, surface trade-offs, and illuminate blind spots.

---

## The SSoT Hierarchy

Think-tank manages the development story through a clear hierarchy:

```
NORTHSTAR.md (WHAT - User Story, Features, Requirements)
     ↓ aligned with
ROADMAP.yaml (HOW - Development Phases, Execution Order)
     ↓ links to
Phase Think-Tanks (Detailed Execution Plans)
     ↓ executed by
/hc-execute (Implementation)
```

---

## Session Types

| Type | Flag | Output | Purpose |
|------|------|--------|---------|
| **Roadmap** | `--roadmap` | `ROADMAP.yaml` | Define/update project phases |
| **Phase** | `--phase=PHASE-XXX` | `execution-plan.yaml` | Plan specific phase (links to ROADMAP) |
| **Side-Quest** | *(no flag)* | `STATE.yaml` | Ad-hoc research (may feed into phases) |

```
ROADMAP.yaml (Project Development Plan)
├── PHASE-001 → Phase Think-Tank → execution-plan.yaml → /hc-execute
├── PHASE-002 (depends_on: PHASE-001) → ...
└── PHASE-003 → ...

Side-Quests (recorded in ROADMAP.yaml side_quests)
└── Research Topic → may inform future phases
```

### Flags

| Flag | Description |
|------|-------------|
| `--roadmap` | Create/update ROADMAP.yaml with project phases |
| `--phase=PHASE-XXX` | Plan specific phase → `execution-plan.yaml`, links to ROADMAP |
| `--add-phase` | Add new phase to existing ROADMAP.yaml |
| `--remove-phase=PHASE-XXX` | Archive/remove a phase from ROADMAP |
| `--new-info` | Resume with new information |
| `--redirect` | Change discussion direction |
| `--what-if` | Explore hypothetical |
| `--skip-validation` | Accept map without validation |
| `--override` | Force approval despite issues |

---

## Quick Start

```markdown
/think-tank

PROBLEM: [What needs thinking through]
MY_LEAN: [Current thinking, if any]
CONSTRAINTS:
- [Budget, time, team, tech stack]
CONTEXT:
- [Relevant background]
```

**Resume:** `/think-tank "topic" --new-info|--redirect|--what-if "context"`

**Batch Mode:** Runs 4 exchanges → Decision Map → exits. Review files, resume with flags.

---

## Core Concept

| Debate Model | Council Model |
|--------------|---------------|
| Agents fight to win | Agents collaborate to map options |
| Output: Winner | Output: Decision Map with trade-offs |
| Fixed adversarial roles | Dynamic personas by domain |

---

## The Cast

| Role | Purpose | Model |
|------|---------|-------|
| **You (HD)** | The Chair | Human |
| **Orchestrator** | Moderator | Opus |
| **Domain Expert** | Deep subject knowledge | Opus (2408) |
| **Pragmatist** | Guardian of Resources | Pro (2406) |
| **Flash Scouts** | On-demand research | Flash (2405) |

---

## Workflow

```
INTAKE → CASTING → RESEARCH (facts + validation) → COUNCIL → DECISION MAP → VALIDATION → REVIEW → ADR → SPEC → PLAN
```

### Workspace: `.claude/PM/think-tank/{topic_slug}_{YYYYMMDD}/`

```
00_BRIEFING.md               # Problem statement
01_CAST.md                   # Expert personas
02_KNOWLEDGE_BASE/           # Fact-based research
    facts_scout_N.yaml       # Raw scout outputs
    facts_merged.yaml        # Merged + deduped
    resolution_*.yaml        # Conflict resolutions (if any)
    validation_N.yaml        # Validator outputs
    facts.yaml               # Final validated facts
    BRIEFING_PACK.md         # Optional prose summary
03_SESSIONS/                 # Transcripts + SUMMARY_LATEST.md
04_DECISION_MAP.md           # Living document
04B_VALIDATION/              # Validator feedback by round
05_SPEC.md                   # Technical feasibility spec
05B_LEARNINGS.md             # Implementation learnings
STATE.yaml                   # Session tracking
action-items.yaml            # Roadmap sessions only
execution-plan.yaml          # After DECIDE (test-driven)
```

---

## Proxy Configuration

```bash
# Flash (2405) | Pro (2406) | Opus (2408)
ANTHROPIC_API_BASE_URL=http://localhost:240X claude --dangerously-skip-permissions -p "PROMPT"
```

---

## Orchestrator Protocol

### STEP 1: INTAKE

1. Parse PROBLEM, MY_LEAN, CONSTRAINTS, CONTEXT
2. Check for existing workspace → offer RESUME or FRESH
3. Create workspace: `mkdir -p .claude/PM/think-tank/${TOPIC_SLUG}_$(date +%Y%m%d)/{02_KNOWLEDGE_BASE,03_SESSIONS}`
4. Write `00_BRIEFING.md` (problem, lean, constraints, context, success criteria)
5. Initialize `STATE.yaml`

**STATE.yaml schema:**
```yaml
topic: ${TOPIC_SLUG}
created: ${YYYYMMDD}
status: active  # active | paused | decided | archived
lifecycle:
  type: standard  # standard | main | sub
  status: active
current_session: {number: 1, step: 1}
sessions: []
decisions: []
validation: {current_round: 0, max_rounds: 5, status: pending}
learnings: []
open_questions: []
# For sub sessions:
parent: {topic: null, path: null, action_item_id: null}
# For escalations:
escalations: []
```

---

### STEP 2: CASTING

Analyze problem domain. Define two personas in `01_CAST.md`:
- **Domain Expert**: Deepest SUBJECT MATTER knowledge
- **Pragmatist**: REALITY CHECKS (cost, time, difficulty, team, ops)

If confidence is MEDIUM, ask user approval.

---

### STEP 3: FACT-BASED RESEARCH

**Philosophy:** Collect structured facts, not prose analysis. Validate before Council consumes.

#### 3.1 Fact Collection (4 Flash Scouts in Parallel)

Spawn 4 Flash scouts with `scout_facts.md`:

| Scout | Focus Area |
|-------|------------|
| 1 | Commands & orchestration |
| 2 | Agents & delegation |
| 3 | Templates & prompts |
| 4 | State & PM workflows |

**Output:** `facts_scout_N.yaml` (structured facts with sources)

Variables: `SESSION_PATH`, `PROBLEM`, `FOCUS_AREA`, `SCOUT_ID`

#### 3.2 Fact Merge (Flash)

Spawn Flash with `merge_facts.md`:
- Combine 4 scout outputs
- Deduplicate (same fact from multiple scouts)
- Flag conflicts for arbitration

**Output:** `facts_merged.yaml`

Variables: `SESSION_PATH`

#### 3.3 Conflict Resolution (Flash Arbiter - if needed)

**If conflicts found:** Spawn Flash with `arbiter_conflict.md`:
- Investigate disagreement
- Go to sources, verify
- Resolve with evidence

**Output:** `resolution_{{CONFLICT_ID}}.yaml`

Variables: `SESSION_PATH`, `CONFLICT_ID`

#### 3.4 Fact Validation (2 Flash Validators in Parallel)

Spawn 2 Flash validators with `fact_validator.md`:
- Verify HIGH relevance facts (source exists, content accurate)
- Spot-check MEDIUM relevance facts
- Skip LOW relevance facts

**Aggregation:**
- Both VERIFIED → fact is trusted
- One flags → investigate
- Both flag → remove fact

**Output:** `validation_N.yaml`, then final `facts.yaml`

Variables: `SESSION_PATH`, `VALIDATOR_ID`

---

### STEP 3.5: BRIEFING PACK (Optional)

If Council needs prose summary, spawn Pro with `synthesizer_briefing.md`.

Otherwise, Council reads `facts.yaml` directly (preferred - less token overhead).

Variables: `SESSION_PATH`

---

### STEP 4: COUNCIL SESSION

Spawn agents sequentially for each round:

| Agent | Template | Key Variables |
|-------|----------|---------------|
| Domain Expert | `council_domain_expert.md` | `SESSION_PATH`, `EXPERT_TITLE`, `EXPERT_FOCUS`, `EXPERT_PERSPECTIVE` |
| Pragmatist | `council_pragmatist.md` | `SESSION_PATH`, `PRAGMATIST_TITLE`, `PRAGMATIST_FOCUS`, `PRAGMATIST_PERSPECTIVE` |

**After each round:**
- Append to `03_SESSIONS/session_NNN.md`
- Every 3-4 exchanges: update `SUMMARY_LATEST.md` (max 2000 tokens)

**Handle signals:**
- `RESEARCH_REQUEST:` → spawn 4 Flash scouts (see STEP 3 for modes)
- `USER_QUESTION:` → log to STATE.yaml

**Research budget:** Up to 3 research rounds per council round. Agents should use this tool proactively.

**Convergence:** 2-3 paths with trade-offs understood. Max 6 rounds.

---

### STEP 5: DECISION MAP

Spawn Pro agent with `synthesizer_decision_map.md` → `04_DECISION_MAP.md`

Variables: `SESSION_PATH`

Output: Core Tension, Constraints, Blind Spots, 3 Paths (A/B/C) with Pre-Mortems, Council Assessment.

---

### STEP 5.5: CONSENSUS VALIDATION

Spawn 4 validators IN PARALLEL (2 Pro + 2 Opus) using `validator.md`:

Variables: `SESSION_PATH`, `OUTPUT_PATH`

Spawn Flash with `synthesizer_consensus.md`:

Variables: `SESSION_PATH`, `ROUND_NUM`

**Aggregation:**
- 3-4 agree → CONSENSUS_MUST_FIX
- 2 agree → TIEBREAKER_NEEDED
- 1 only → NO_CONSENSUS (ignore)

**If CORRECTION_REQUIRED:** Send `correction_directive.md` → re-validate (max 5 rounds)

---

### STEP 6: USER REVIEW

Present Decision Map summary. Options:
- **DECIDE** → STEP 6.5 (ADR) → STEP 7 (Plan)
- **REDIRECT/WHAT IF/EXPAND** → back to STEP 4
- **PAUSE** → save state

---

### STEP 6.5: ADR CREATION

**Mandatory:** Every decision recorded as ADR using `generator_adr.md`.

Variables: `SESSION_PATH`, `TOPIC`, `DECIDED_PATH`, `CONFIDENCE`

Update STATE.yaml with ADR reference.

---

### STEP 6.75: TECHNICAL SPECIFICATION (Feasibility Gate)

**Before planning HOW, prove we CAN.**

Spawn Pro/Sonnet (Architect) with `generator_spec.md`:
- Architecture overview
- Critical path identification
- Technical risks
- Dependencies
- Proof of concept (pseudo-code for critical parts)
- Requirement traceability (link to NORTHSTAR)

**Output:** `05_SPEC.md`

Variables: `SESSION_PATH`, `DECIDED_PATH`

**Feasibility Verdicts:**
| Verdict | Action |
|---------|--------|
| FEASIBLE | Proceed to PLAN |
| FEASIBLE_WITH_RISKS | Proceed, include mitigations in plan |
| NOT_FEASIBLE | Return to USER REVIEW, adjust scope |

---

### STEP 7: PLAN GENERATION

**Requires:** `05_SPEC.md` must exist and verdict must be FEASIBLE or FEASIBLE_WITH_RISKS.

Ask plan scope: FULL | OUTLINE | SKIP

Spawn Pro with `generator_execution_plan.md`:

Variables: `SESSION_PATH`, `DECIDED_PATH`, `CONFIDENCE`, `PLAN_LEVEL`

**Output:** `execution-plan.yaml` with:
- `trace_req` - Every task links to NORTHSTAR requirement
- `definition_of_done` - Explicit success criteria per task
- `target_context` - Files/components affected
- `risks` - Carried forward from SPEC.md

Ready for `/hc-execute`

---

## ROADMAP SESSION PROTOCOL (--roadmap)

**Purpose:** Define the development story - HOW we build the project.

### Step 0: NORTHSTAR Validation

Before creating roadmap:

1. Read `NORTHSTAR.md` from `.claude/PM/SSoT/NORTHSTAR.md`
2. Check sections are NOT placeholder text:
   - Purpose must not contain "What does this project do"
   - Vision must not contain "What will this project become"
   - Goals must have at least one non-template goal (not "Goal 1 - Description")
3. **If placeholders found:**
   - **ABORT** with message: "Please fill out NORTHSTAR.md first"
   - Show which sections need content:
     ```
     ❌ NORTHSTAR.md validation failed:
     - Purpose: Contains placeholder text
     - Vision: Contains placeholder text
     - Goals: Only template goals found

     Please fill out these sections before creating a roadmap.
     ```

### Process

1. Read NORTHSTAR.md to understand the WHAT (user story)
2. Council analyzes and breaks down into logical phases
3. Define phase dependencies (what blocks what)
4. Output ROADMAP.yaml with phases

**Output:** `.claude/PM/SSoT/ROADMAP.yaml`

```yaml
phases:
  - id: PHASE-001
    title: 'Foundation'
    status: planned
    dependencies: []
    plan_path: null  # Populated when phase is planned
  - id: PHASE-002
    title: 'MVP'
    dependencies: [PHASE-001]
    plan_path: null
```

**STATE.yaml additions:**
```yaml
lifecycle:
  type: roadmap
roadmap_path: .claude/PM/SSoT/ROADMAP.yaml
```

**User options:** APPROVE | ADJUST | ADD_PHASE

---

## PHASE SESSION PROTOCOL (--phase=PHASE-XXX)

**Purpose:** Create detailed execution plan for a specific phase.

### Step 1: Validate Phase

Before planning the phase:

1. Read `ROADMAP.yaml` from `.claude/PM/SSoT/ROADMAP.yaml`
2. Check `phases[]` for matching `phase_id` (e.g., PHASE-XXX)
3. **If phase NOT found:**
   - **ABORT** with error:
     ```
     ❌ Phase PHASE-XXX not found in ROADMAP.yaml

     Available phases:
     - PHASE-001: Foundation (status: complete)
     - PHASE-002: MVP (status: planned)
     - PHASE-003: Hardening (status: planned)

     Run /think-tank --roadmap to add new phases.
     ```
4. **If phase found but status is 'complete':**
   - **WARN**:
     ```
     ⚠️ Phase PHASE-XXX is already marked complete.

     Options:
     - Continue anyway (re-plan the phase)
     - Cancel and choose a different phase
     ```
5. **If phase dependencies not met:**
   - **WARN**:
     ```
     ⚠️ Phase PHASE-XXX has unmet dependencies: [PHASE-001]

     These phases must be complete before starting PHASE-XXX.
     Continue planning anyway? (y/n)
     ```

### Process

1. Validate ROADMAP.yaml exists
2. Validate phase exists and dependencies are met (Step 1 above)
3. Read NORTHSTAR.md for alignment
4. Create phase workspace: `${PHASE_TITLE}_${YYYYMMDD}/`
5. Council plans the phase in detail
6. Output execution-plan.yaml
7. **Link back to ROADMAP:** Update phase's `plan_path`

**Output:** `execution-plan.yaml` + ROADMAP.yaml updated

**STATE.yaml additions:**
```yaml
lifecycle:
  type: phase
phase_id: PHASE-XXX
roadmap_path: .claude/PM/SSoT/ROADMAP.yaml
```

**On Completion:**
```yaml
# Update ROADMAP.yaml
phases:
  - id: PHASE-001
    plan_path: .claude/PM/think-tank/foundation_20260102/execution-plan.yaml
```

---

## SIDE-QUEST PROTOCOL (no flag)

**Purpose:** Ad-hoc research not tied to a specific phase.

**Process:**
1. Normal think-tank flow
2. On completion, optionally link to ROADMAP.yaml side_quests
3. Findings may inform future phases

**STATE.yaml additions:**
```yaml
lifecycle:
  type: side_quest
relates_to_phase: null  # Optional: PHASE-XXX if relevant
```

### Promoting Side-Quest to Phase

If side-quest research leads to actionable work:

1. **Option A: Link to Existing Phase**
   - Update STATE.yaml: `relates_to_phase: PHASE-XXX`
   - Add findings to phase's execution-plan as additional tasks

2. **Option B: Create Backlog Item**
   - Add item to `context.yaml` backlog:
     ```yaml
     backlog:
       - id: BACK-001
         description: 'Implement findings from auth research'
         source: '.claude/PM/think-tank/auth_research_20260102/'
         added: '2026-01-02'
     ```
   - Triage agent will surface for phase assignment

3. **Option C: Create New Phase**
   - Run: `/think-tank --roadmap --add-phase "New Phase Title"`
   - Links to side-quest findings
   - Adds phase to ROADMAP.yaml with dependency on current phases

**Promotion Checklist:**
- [ ] Side-quest has actionable findings (not just research)
- [ ] Findings align with NORTHSTAR goals
- [ ] Clear scope for implementation
- [ ] Dependencies identified

---

## DYNAMIC PHASE MANAGEMENT

**Philosophy:** Roadmaps evolve. A project may start with 4 phases and grow to 12 as scope changes, missing info surfaces, or new requirements emerge. The system supports this naturally.

### Adding Phases (--add-phase)

**When to use:** New requirement discovered, scope expansion, side-quest promotes to phase.

**Syntax:**
```
/think-tank --add-phase "Phase Title"
```

**Process:**
1. Read existing ROADMAP.yaml
2. Generate next phase ID (PHASE-XXX)
3. Ask user for:
   - Phase description
   - Dependencies (which phases must complete first)
   - Priority (insert position in sequence)
4. Council briefly validates fit with NORTHSTAR
5. Add phase to ROADMAP.yaml
6. Log: `[ROADMAP] Added PHASE-XXX: ${TITLE}`

**Output:**
```yaml
# ROADMAP.yaml updated
phases:
  - id: PHASE-001
    # existing...
  - id: PHASE-005  # NEW
    title: 'New Phase Title'
    status: planned
    description: 'User-provided description'
    dependencies: [PHASE-002]  # User-specified
    plan_path: null  # Ready for /think-tank --phase
```

### Removing/Archiving Phases (--remove-phase)

**When to use:** Phase no longer needed, scope reduction, duplicate phase.

**Syntax:**
```
/think-tank --remove-phase=PHASE-XXX
```

**Process:**
1. Validate phase exists
2. Check if other phases depend on this one
3. If dependencies exist:
   - **WARN**: "PHASE-002, PHASE-003 depend on PHASE-XXX"
   - Options: CASCADE (remove deps too) | REASSIGN (move deps) | CANCEL
4. Archive phase (move to ROADMAP.yaml `archived_phases[]`)
5. Update dependent phases if reassigned
6. Log: `[ROADMAP] Archived PHASE-XXX: ${REASON}`

**Output:**
```yaml
# ROADMAP.yaml
phases:
  # PHASE-XXX removed from active phases

archived_phases:
  - id: PHASE-XXX
    title: 'Removed Phase'
    archived: '2026-01-02'
    reason: 'Scope reduction'
    had_dependents: [PHASE-002]
```

### Reordering Phases

**When to use:** Dependencies change, priorities shift, new info affects sequence.

**Process:**
1. Run `/think-tank --roadmap` on existing ROADMAP.yaml
2. Council re-analyzes phase dependencies with new context
3. Outputs updated ROADMAP.yaml with reordered phases
4. Preserves completed phases (status: complete)
5. Only reorders planned/active phases

### Phase Count Philosophy

```
Initial ROADMAP: 4 phases (high-level buckets)
After Phase 1:   6 phases (split complex phase, add integration)
After Phase 3:   8 phases (new requirements discovered)
After feedback:  12 phases (scope expanded)
After review:    10 phases (2 phases merged as redundant)
```

**Rules:**
- Phase count is DYNAMIC - it reflects reality, not a fixed plan
- Add phases when work is discovered, not when it's too late
- Remove phases when they're no longer needed
- Dependencies are the constraint, not phase count
- Each phase should be independently executable (1-3 days of work)

### Scope Change Protocol

When user provides new info that changes scope:

1. **Assess Impact:**
   - Does this affect NORTHSTAR? → Update NORTHSTAR first
   - Does this add work? → `--add-phase`
   - Does this remove work? → `--remove-phase`
   - Does this change order? → Re-run `--roadmap`

2. **Update ROADMAP:**
   ```
   /think-tank --roadmap --new-info "Scope change: [description]"
   ```
   Council integrates new info, adjusts phases.

3. **Communicate Change:**
   - Log in ROADMAP.yaml `changelog[]`
   - Update context.yaml `recent_actions`
   - If major: Create ADR documenting decision

---

## ESCALATION PROTOCOL

| Trigger | Action |
|---------|--------|
| SCOPE_EXPANSION | Flag for roadmap review |
| CONFLICT | Escalate to user |
| INFEASIBILITY | Pause and escalate |
| DEPENDENCY_ISSUE | Escalate to roadmap |

Log in STATE.yaml `escalations[]`, pause session, notify user.

---

## ARCHIVE PROTOCOL

**Triggers:** Roadmap complete | Phase complete | Manual `--archive` | Stale 30+ days

**Process:**
1. Validate completeness
2. Update STATE.yaml: `lifecycle.status: archived`
3. Move to `.claude/PM/think-tank/archive/`
4. Update context.yaml

---

## RESUME PROTOCOL

1. Find workspace: `ls -d .claude/PM/think-tank/${TOPIC_SLUG}_*`
2. Load STATE.yaml
3. Present options: NEW_INFO | ISSUE | REEVALUATE | FRESH
4. Continue or archive old and start fresh

---

## The Council Mantra

```
We explore, not fight.
We map, not prescribe.
We surface trade-offs, not hide them.
We ask "what's simplest?" before "what's best?"
We ask "what fails?" before "what succeeds?"
```

---

## Template Reference

All prompts in: `.claude/templates/template-prompts/think-tank/`

### Research Phase (Fact-Based)

| Template | Model | Purpose |
|----------|-------|---------|
| `scout_facts.md` | Flash | Collect structured facts (primary) |
| `merge_facts.md` | Flash | Combine + dedupe scout outputs |
| `arbiter_conflict.md` | Flash | Resolve fact disagreements |
| `fact_validator.md` | Flash | Verify fact accuracy |
| `synthesizer_briefing.md` | Pro | Optional prose summary |

### Council Phase

| Template | Model | Purpose |
|----------|-------|---------|
| `council_domain_expert.md` | Opus | Domain expertise |
| `council_pragmatist.md` | Pro | Reality checks + Pre-Mortem |

### Synthesis & Validation

| Template | Model | Purpose |
|----------|-------|---------|
| `synthesizer_decision_map.md` | Pro | Generate Decision Map |
| `validator.md` | Pro/Opus | Independent review |
| `synthesizer_consensus.md` | Flash | Aggregate feedback |
| `correction_directive.md` | Pro | Fix consensus issues |

### Generation

| Template | Model | Purpose |
|----------|-------|---------|
| `generator_adr.md` | Flash | Create/update ADR |
| `generator_spec.md` | Pro | Technical feasibility spec |
| `generator_execution_plan.md` | Pro | Test-driven execution plan |
| `generator_action_items.md` | Pro | Extract action items (roadmap) |

### Legacy (Deprecated)

| Template | Status | Replaced By |
|----------|--------|-------------|
| `scout_codebase.md` | deprecated | `scout_facts.md` with FOCUS_AREA |
| `scout_docs.md` | deprecated | `scout_facts.md` with FOCUS_AREA |
| `scout_web.md` | deprecated | `scout_facts.md` with FOCUS_AREA |
| `scout_consensus.md` | deprecated | `fact_validator.md` |

---

## Example

```
/think-tank

PROBLEM: Should I migrate our REST API to GraphQL?
MY_LEAN: GraphQL might help with mobile over-fetching
CONSTRAINTS:
- Team of 3 (no GraphQL experience)
- Must maintain REST for existing integrations
- 6-month runway
CONTEXT:
- Mobile app makes 12+ API calls per screen
- Performance complaints from users
```

---

**Version:** V2.2.0 | Fact-based research, SPEC feasibility gate, test-driven execution plans
