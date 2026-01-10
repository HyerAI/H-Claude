---
version: V3.0.0
status: current
timestamp: 2026-01-10
description: "Council-based decision support - Dynamic experts collaborate to map options and help you think"

# =============================================================================
# CONFIGURATION
# =============================================================================

templates_path: .claude/templates/template-prompts/think-tank/

session_types:
  roadmap:
    flag: "--roadmap"
    output: "ROADMAP.yaml"
    purpose: "Define/update project phases"
    output_path: ".claude/PM/SSoT/ROADMAP.yaml"
  phase:
    flag: "--phase=PHASE-XXX"
    output: "execution-plan.yaml"
    purpose: "Plan specific phase (links to ROADMAP)"
  side_quest:
    flag: null
    output: "STATE.yaml"
    purpose: "Ad-hoc research (may feed into phases)"

flags:
  session:
    - {name: "--roadmap", desc: "Create/update ROADMAP.yaml with project phases"}
    - {name: "--phase=PHASE-XXX", desc: "Plan specific phase → execution-plan.yaml"}
    - {name: "--add-phase", desc: "Add new phase to existing ROADMAP.yaml"}
    - {name: "--remove-phase=PHASE-XXX", desc: "Archive/remove a phase from ROADMAP"}
  resume:
    - {name: "--new-info", desc: "Resume with new information"}
    - {name: "--redirect", desc: "Change discussion direction"}
    - {name: "--what-if", desc: "Explore hypothetical"}
  validation:
    - {name: "--skip-validation", desc: "Accept map without validation"}
    - {name: "--override", desc: "Force approval despite issues"}
    - {name: "--no-gauntlet", desc: "Skip Gauntlet adversarial loop (for simple plans)"}

proxies:
  HC_REAS_A: {port: 2410, model: "Claude Opus", use: "Heavy reasoning, complex analysis"}
  HC_REAS_B: {port: 2411, model: "Gemini Pro", use: "QA, challenger reasoning"}
  HC_WORK:   {port: 2412, model: "Gemini Flash", use: "Workers, code writing, scouts"}
  HC_WORK_R: {port: 2413, model: "Gemini Flash", use: "Workers with extended thinking"}
  HC_ORCA:   {port: 2414, model: "Gemini Flash", use: "Light orchestration"}
  HC_ORCA_R: {port: 2415, model: "Gemini Pro", use: "Heavy orchestration"}

council:
  chair: {role: "You (HC)", purpose: "The Chair", type: "Human"}
  orchestrator: {role: "Orchestrator", purpose: "Moderator", proxy: "HC_ORCA_R", port: 2415}
  domain_expert: {role: "Domain Expert", purpose: "Deep subject knowledge", proxy: "HC_REAS_A", port: 2410}
  pragmatist: {role: "Pragmatist", purpose: "Guardian of Resources", proxy: "HC_REAS_B", port: 2411}
  flash_scouts:
    role: "Flash Scouts"
    purpose: "On-demand research"
    proxy: "HC_WORK"
    port: 2412
    count: 3
    focus_areas: ["Commands & orchestration", "Templates & prompts", "State & PM workflows"]

gauntlet:
  enabled_by_default: true
  bypass_flag: "--no-gauntlet"
  max_iterations: 5
  roles:
    writer: {model: "Opus", port: 2410, template: "gauntlet_writer.md", responses: ["ACCEPTED", "REJECTED"]}
    critic: {model: "Pro", port: 2411, template: "gauntlet_critic.md", responses: ["BLOCKING_ISSUES", "APPROVED"]}
    arbiter: {model: "Flash", port: 2412, template: "gauntlet_arbiter.md", responses: ["WRITER_WINS", "CRITIC_WINS", "ESCALATE_USER"]}
  flow: "Draft → Critic → Writer → [repeat] → APPROVED"

diffusion:
  philosophy: "We do not guess the future. We simulate it, lock the foundation, and render the reality one phase at a time."
  triangulated_context:
    past: {name: "Bedrock", source: "Actual code analysis"}
    present: {name: "Plan", source: "Phase Roadmap / Task Plan"}
    future: {name: "Vision", source: "NORTHSTAR.md"}
  resolution_stack: [NORTHSTAR, ROADMAP, Phase_Roadmap, Task_Plan, Ticket, Code]
  validation_gates:
    step_6: {template: "validator_simulation.md", checks: "Phase vs NS + codebase"}
    step_7: {template: "validator_physics.md", checks: "Traceability, no bloat"}
    step_8: {template: "validator_resolution.md", checks: "Ticket determinism"}
  lookahead:
    track_a: {name: "Reality", agents: "WR builds, QA tests"}
    track_b: {name: "Horizon", agents: "VA checks NS alignment"}
    rule: "If Today's Code blocks Tomorrow's Vision, change Today's Code."

timeouts:
  orchestrator: {default: 2700, desc: "45 min"}
  scout: {default: 600, desc: "10 min"}
  generator: {default: 900, desc: "15 min"}

validation:
  consensus: {validators: 4, composition: "2 Pro + 2 Opus", max_rounds: 5}
  aggregation: {must_fix: "3-4 agree", tiebreaker: "2 agree", ignore: "1 only"}

state_schema:
  topic: "${TOPIC_SLUG}"
  created: "${YYYYMMDD}"
  status: "active"  # active | paused | decided | archived
  lifecycle: {type: "standard", status: "active"}  # standard | roadmap | phase | side_quest
  current_session: {number: 1, step: 1}
  validation: {current_round: 0, max_rounds: 5, status: "pending"}
  cost_tracking: {agent_spawns: 0, estimated_tokens: 0, session_duration_min: 0}

templates:
  research: [scout_facts.md, merge_facts.md, arbiter_conflict.md, fact_validator.md, synthesizer_briefing.md]
  council: [council_domain_expert.md, council_pragmatist.md]
  synthesis: [synthesizer_decision_map.md, validator.md, synthesizer_consensus.md, correction_directive.md]
  generation: [generator_adr.md, generator_spec.md, generator_execution_plan.md, generator_action_items.md, generator_phase_roadmap.md, generator_task_plan.md, generator_tickets.md]
  gauntlet: [gauntlet_writer.md, gauntlet_critic.md, gauntlet_arbiter.md]
  validators: [validator_simulation.md, validator_physics.md, validator_resolution.md, validator_lookahead.md]
  schemas: [PHASE_ROADMAP_SCHEMA.md, TASK_PLAN_SCHEMA.md, TICKET_SCHEMA.md]
  deprecated: {scout_codebase.md: "scout_facts.md", scout_docs.md: "scout_facts.md", scout_web.md: "scout_facts.md", scout_consensus.md: "fact_validator.md"}

---

# /think-tank - The Council

**Philosophy:** Help YOU think, not tell you what to think.

**Purpose:** Convene a council of dynamically-cast experts who collaborate to map the decision space, surface trade-offs, and illuminate blind spots.

---

## The SSoT Hierarchy

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

## Workspace

`.claude/PM/think-tank/{topic_slug}_{YYYYMMDD}/`

```
00_BRIEFING.md              # Problem statement
01_CAST.md                  # Expert personas
02_KNOWLEDGE_BASE/          # Fact-based research
   facts_scout_N.yaml       # Raw scout outputs
   facts_merged.yaml        # Merged + deduped
   facts.yaml               # Final validated facts
03_SESSIONS/                # Transcripts + SUMMARY_LATEST.md
04_DECISION_MAP.md          # Living document
05_SPEC.md                  # Technical feasibility spec
STATE.yaml                  # Session tracking
execution-plan.yaml         # After DECIDE (test-driven)
```

---

## Workflow

```
INTAKE → CASTING → RESEARCH → COUNCIL → DECISION MAP → VALIDATION → REVIEW → ADR → SPEC → PLAN
```

---

## Orchestrator Protocol

### STEP 1: INTAKE

1. Parse PROBLEM, MY_LEAN, CONSTRAINTS, CONTEXT
2. Check for existing workspace → offer RESUME or FRESH
3. Create workspace, write `00_BRIEFING.md`
4. Initialize `STATE.yaml`

### STEP 2: CASTING

Analyze problem domain. Define two personas in `01_CAST.md`:
- **Domain Expert**: Deepest SUBJECT MATTER knowledge
- **Pragmatist**: REALITY CHECKS (cost, time, difficulty, team, ops)

If confidence is MEDIUM, ask user approval.

### STEP 3: FACT-BASED RESEARCH

**Philosophy:** Collect structured facts, not prose analysis. Validate before Council consumes.

**3.1 Fact Collection** - Spawn 3 Flash scouts with `scout_facts.md`:
- Scout 1: Commands, agents & orchestration patterns
- Scout 2: Templates, prompts & prompt engineering
- Scout 3: State management, PM workflows & session artifacts

**3.2 Fact Merge** - Spawn Flash with `merge_facts.md` → `facts_merged.yaml`

**3.3 Conflict Resolution** - If conflicts, spawn Flash with `arbiter_conflict.md`

**3.4 Fact Validation** - Spawn 2 Flash validators with `fact_validator.md`:
- Both VERIFIED → trusted | One flags → investigate | Both flag → remove

### STEP 3.5: BRIEFING PACK (Optional)

If Council needs prose summary, spawn Pro with `synthesizer_briefing.md`.
Otherwise, Council reads `facts.yaml` directly (preferred).

### STEP 4: COUNCIL SESSION

Spawn agents sequentially for each round using `council_domain_expert.md` and `council_pragmatist.md`.

**Transcript Capture (MANDATORY):** Every exchange → `03_SESSIONS/session_NNN.md`

**Handle signals:**
- `RESEARCH_REQUEST:` → spawn 3 Flash scouts
- `USER_QUESTION:` → log to STATE.yaml

**Convergence:** 2-3 paths with trade-offs understood. Max 6 rounds.

### STEP 5: DECISION MAP

Spawn Pro with `synthesizer_decision_map.md` → `04_DECISION_MAP.md`

Output: Core Tension, Constraints, Blind Spots, 3 Paths with Pre-Mortems.

### STEP 5.5: CONSENSUS VALIDATION

Spawn 4 validators (2 Pro + 2 Opus) using `validator.md`.

**Aggregation:** 3-4 agree → MUST_FIX | 2 agree → TIEBREAKER | 1 only → ignore

If issues, send `correction_directive.md` → re-validate (max 5 rounds).

### STEP 6: USER REVIEW

Present Decision Map summary. Options:
- **DECIDE** → ADR → SPEC → Plan
- **REDIRECT/WHAT IF/EXPAND** → back to COUNCIL
- **PAUSE** → save state

### STEP 6.5: ADR CREATION

**Mandatory:** Every decision recorded as ADR using `generator_adr.md`.

### STEP 6.75: TECHNICAL SPECIFICATION

Spawn Pro with `generator_spec.md` → `05_SPEC.md`

**Verdicts:** FEASIBLE | FEASIBLE_WITH_RISKS | NOT_FEASIBLE

### STEP 7: PLAN GENERATION (with Gauntlet)

**Requires:** SPEC exists with FEASIBLE verdict.

**Two validation layers:**
- **Gauntlet:** Writer + Critic + Arbiter (adversarial stress-testing)
- **Diffusion:** validator_physics.md (traceability + bloat check)

**The Gauntlet Loop:**
```
Draft (Flash) → Critic (Pro) → Writer (Opus) → [repeat max 5x] → APPROVED
```

1. **Critic** simulates execution → `BLOCKING_ISSUES` or `APPROVED`
2. **Writer** responds → `ACCEPTED` (fix) or `REJECTED` (cite evidence)
3. If contested → **Arbiter** rules: `WRITER_WINS`, `CRITIC_WINS`, `ESCALATE_USER`

**Bypass:** Use `--no-gauntlet` for simple plans.

**Output:** `execution-plan.yaml` with trace_req, definition_of_done, risks.

---

## ROADMAP SESSION (--roadmap)

**Purpose:** Define the development story - HOW we build the project.

### Step 0: NORTHSTAR Validation

Read `.claude/PM/SSoT/NORTHSTAR.md` and verify:
- Purpose is not placeholder text
- Vision is not placeholder text
- Goals have real content

**If placeholders found → ABORT:** "Please fill out NORTHSTAR.md first"

### Process

1. Read NORTHSTAR.md for the WHAT
2. Council breaks down into logical phases
3. Define phase dependencies
4. Output ROADMAP.yaml

**User options:** APPROVE | ADJUST | ADD_PHASE

---

## PHASE SESSION (--phase=PHASE-XXX)

**Purpose:** Create detailed execution plan for a specific phase.

### Step 1: Validate Phase

1. Read ROADMAP.yaml
2. Verify phase exists
3. If not found → **ABORT** with available phases
4. If complete → **WARN** and offer re-plan
5. If deps unmet → **WARN** and ask to continue

### Progressive Resolution (Diffusion)

**Step 6:** Spawn `generator_phase_roadmap.md` → validate with `validator_simulation.md`
**Step 7:** Spawn `generator_task_plan.md` → validate with `validator_physics.md`
**Step 8:** Spawn `generator_tickets.md` → validate with `validator_resolution.md`
**Step 9:** Link execution-plan.yaml to ROADMAP.yaml

---

## SIDE-QUEST (no flag)

**Purpose:** Ad-hoc research not tied to a specific phase.

Normal think-tank flow. On completion, optionally link to ROADMAP side_quests.

### Promoting to Phase

- **Option A:** Link to existing phase (`relates_to_phase: PHASE-XXX`)
- **Option B:** Create backlog item in `context.yaml`
- **Option C:** Run `--add-phase` to create new phase

---

## DYNAMIC PHASE MANAGEMENT

**Philosophy:** Roadmaps evolve. Phase count is DYNAMIC.

### --add-phase "Title"

1. Read existing ROADMAP.yaml
2. Generate next phase ID
3. Ask user for description, dependencies, priority
4. Validate fit with NORTHSTAR
5. Add to ROADMAP.yaml

### --remove-phase=PHASE-XXX

1. Validate phase exists
2. Check dependents
3. If deps exist → CASCADE | REASSIGN | CANCEL
4. Archive to `archived_phases[]`

### Scope Change Protocol

1. **Assess:** NORTHSTAR affected? Add work? Remove work? Change order?
2. **Update:** `/think-tank --roadmap --new-info "description"`
3. **Communicate:** Log in changelog, create ADR if major

---

## ARCHIVE PROTOCOL

**Triggers:** Complete | Manual `--archive` | Stale 30+ days

Update `lifecycle.status: archived`, move to `archive/`.

---

## RESUME PROTOCOL

1. Find workspace: `ls -d .claude/PM/think-tank/${TOPIC_SLUG}_*`
2. Load STATE.yaml
3. Present options: NEW_INFO | ISSUE | REEVALUATE | FRESH

---

## Proxy Spawn Pattern

```bash
TIMEOUT=${TIMEOUT:-2700}
timeout --foreground --signal=TERM --kill-after=60 $TIMEOUT \
  bash -c 'ANTHROPIC_API_BASE_URL=http://localhost:PORT claude --dangerously-skip-permissions -p "PROMPT"'

EXIT_CODE=$?
if [ $EXIT_CODE -eq 124 ]; then
  echo "[CRITICAL] Orchestrator killed after timeout"
fi
```

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

**V3.0.0** | YAML config format, all council/gauntlet/diffusion logic preserved
