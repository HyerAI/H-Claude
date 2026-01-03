---
version: V2.5.0
status: current
timestamp: 2026-01-02
tags: [command, execution, orchestration, plan, oraca, think-tank]
description: "SWEEP & VERIFY plan execution protocol with Oraca Phase Orchestrators"
---

# /hc-plan-execute - SWEEP & VERIFY Execution

**Philosophy:** Trust but Verify. Assume 15% of tasks will be missed or partially implemented.

**Purpose:** Execute an approved plan with rigorous QA loops, independent verification, and adversarial sweep to catch what workers miss.

---

## Quick Start

```markdown
/hc-plan-execute

PLAN_PATH: [path to execution-plan.yaml from think-tank, e.g., .claude/PM/think-tank/{topic}_{date}/execution-plan.yaml]
MODE: [standard|careful]
```

Or reference by topic name (will auto-locate approved plan):
```markdown
/hc-plan-execute TOPIC: auth_system
```

This command spawns a background Opus orchestrator that runs the full execution workflow. You'll be notified when complete.

---

## Architecture Overview

```
HD invokes /hc-plan-execute
     ↓
Spawn OPUS Orchestrator (BACKGROUND)
     ↓
┌────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: PARSE, BATCH & CONTRACT                                      │
│  Opus reads plan, extracts phases/tasks, generates INTERFACES.md       │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 2: PHASED EXECUTION (via Oraca[X] Phase Orchestrators)          │
│  For each phase in plan:                                               │
│    ┌──────────────────────────────────────────────────────────────┐    │
│    │  Oraca[X] (Flash) - Phase Orchestrator                       │    │
│    │    ↓                                                         │    │
│    │  Spawn Workers (Flash) for phase tasks (max 3 parallel)      │    │
│    │    ↓                                                         │    │
│    │  Collect evidence → PHASE_X/ folder                          │    │
│    │    ↓                                                         │    │
│    │  Spawn Phase QA (Pro) to review phase work                   │    │
│    │    ↓                                                         │    │
│    │  Report phase completion to Opus                             │    │
│    └──────────────────────────────────────────────────────────────┘    │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 3: QA SYNTHESIS (Pro agent)                                     │
│  Pro analyzes all phase QA reports, curates findings for Sweeper       │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 4: SWEEP (Pro agent - "15% Hunter")                             │
│  Pro compares plan vs result, hunts for gaps and partial work          │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 5: VALIDATION & REPORT                                          │
│  Run automated checks, generate completion report                      │
├────────────────────────────────────────────────────────────────────────┤
│  OUTPUT: .claude/PM/hc-plan-execute/${session-slug}/COMPLETION_REPORT.md  │
│  HD notified when complete                                             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Oraca[X]: Phase Orchestrators

**Oraca** = **Ora**cle + **Ca**ptain. Flash agents that own one phase of execution.

**WHY Oraca?**
- **Context Protection:** Opus stays clean, doesn't accumulate all task details
- **Phase Isolation:** Failures in Phase 2 don't pollute Phase 3's context
- **Scalability:** Plans with 50+ tasks won't overwhelm a single orchestrator
- **Built-in QA Gate:** Each phase gets its own QA before proceeding

**Oraca Responsibilities:**
1. Receive phase spec from Opus (tasks, interfaces, dependencies)
2. Spawn Flash workers for each task (max 3 parallel)
3. Collect worker evidence
4. Handle worker retries (up to 2 per task)
5. Spawn Pro Phase QA to review all phase work
6. Report phase status: `COMPLETE` | `PARTIAL` | `BLOCKED`

**Oraca Boundaries:**
- Oraca CANNOT spawn other Oraca agents (no recursion)
- Oraca CANNOT modify tasks outside its phase
- Oraca MUST write all artifacts to its `PHASE_X/` folder
- Oraca MUST report back to Opus (no silent completion)

---

## Session Folder Structure

```
.claude/PM/hc-plan-execute/${session-slug}/
├── EXECUTION_STATE.md              # Dashboard: Current status snapshot
├── ORCHESTRATOR_LOG.md             # Flight Recorder: Append-only event history
├── COMMANDS.md                     # HD→Orchestrator: Command channel (HD writes)
├── INTERFACES.md                   # Phase 1: Shared contracts for parallel workers
├── PHASE_1/                        # Oraca[1] artifacts
│   ├── ORACA_LOG.md                # Phase-level flight recorder
│   ├── WORKER_OUTPUTS/             # Flash worker evidence
│   │   ├── TASK_001_EVIDENCE.md
│   │   └── ...
│   ├── PHASE_QA.md                 # Pro phase QA verdict
│   └── PHASE_REPORT.md             # Oraca summary for Opus
├── PHASE_2/                        # Oraca[2] artifacts
│   └── ...                         # Same structure
├── PHASE_N/                        # One folder per plan phase
│   └── ...
├── ANALYSIS/                       # Cross-phase analysis
│   ├── QA_SYNTHESIS.md             # Phase 3: All phase QA patterns
│   └── SWEEP_REPORT.md             # Phase 4: Gap analysis
└── COMPLETION_REPORT.md            # Final deliverable
```

---

## Mode Selection

| Mode | Parallel Workers | QA Rigor | Use Case |
|------|------------------|----------|----------|
| **Standard** | 3 | Normal | Most executions |
| **Careful** | 2 | Enhanced (Pro reviews twice) | High-risk, critical changes |

**Default:** Standard

---

## Execution Rules

| Rule | Requirement |
|------|-------------|
| **Parallel Limit** | Never run more than 3 workers simultaneously |
| **State Isolation** | Each worker gets clean context: task spec + necessary interfaces only |
| **Dependency Lock** | Task B cannot start until dependency Task A is VERIFIED |
| **Done Definition** | Task is NOT done when worker claims. Done = QA APPROVED |
| **Evidence Required** | Every worker must produce artifacts (files, code, data) as proof |

---

## Proxy Configuration

```bash
# Oraca[X] Phase Orchestrators (Flash) - phase management
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions

# Worker agents (Flash) - task execution (spawned by Oraca)
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions

# Phase QA / QA Synthesis / Sweeper (Pro) - verification
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions

# Opus Orchestrator - coordination, runs in background
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions
```

---

## Orchestrator Execution

When this command is invoked, spawn a background Opus orchestrator:

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "
$(cat <<'ORCHESTRATOR_PROMPT'

# SWEEP & VERIFY Execution Orchestrator

You are the orchestrator for plan execution. Your adversarial prior: 15% of tasks will be missed or partially implemented. Your job is to catch them.

## CRITICAL: Sub-Agent Spawn Rules

**NEVER use fire-and-forget spawning.** Every sub-agent must be spawned SYNCHRONOUSLY:

\`\`\`bash
# CORRECT: Synchronous spawn - wait for completion
AGENT_OUTPUT=\$(ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "PROMPT" 2>&1)
AGENT_EXIT=\$?

# Log IMMEDIATELY after sub-agent returns
if [ \$AGENT_EXIT -eq 0 ]; then
    echo "[PHASE] Oraca[X] returned. Status: COMPLETE."
else
    echo "[ERROR] Oraca[X] failed with exit code \$AGENT_EXIT"
fi
\`\`\`

**WHY:** Fire-and-forget spawning causes the orchestrator to exit before sub-agents complete.

**Anti-Pattern (DO NOT USE):**
\`\`\`bash
# WRONG: Spawns and exits immediately
claude -p "..." &  # Fire and forget - NEVER DO THIS
\`\`\`

## IMPORTANT: Execute All Phases Sequentially

You MUST complete ALL phases in order. Do not stop after Phase 1.
After each phase, immediately proceed to the next.

## Session Parameters
- PLAN_PATH: ${PLAN_PATH}
- MODE: ${MODE:-standard}
- WORKSPACE: $(pwd)

## Your First Task: Generate PLAN_SLUG

Extract from PLAN_PATH or plan title:
- Lowercase
- Replace spaces with underscores
- Remove special characters
- Max 50 chars

## Session Setup

1. Generate PLAN_SLUG
2. Create session folder:
   \`\`\`bash
   mkdir -p .claude/PM/hc-plan-execute/\${SESSION_SLUG}/{ANALYSIS}
   \`\`\`
3. Initialize ORCHESTRATOR_LOG.md (Flight Recorder)
4. Initialize EXECUTION_STATE.md (Dashboard)
5. Log: \`[INIT] Session initialized. Mode: \${MODE}.\`

---

## Phase 1: Parse, Batch & Contract

1. Read the plan at PLAN_PATH
2. **Extract phases** from the plan:
   - Plans should have explicit phases (e.g., "Phase 1: Setup", "Phase 2: Core Implementation")
   - If no phases defined, group tasks by dependencies into logical phases
3. For each phase, extract tasks with:
   - Task ID
   - Description
   - Dependencies (within-phase and cross-phase)
   - Success criteria
   - Files to modify/create
4. **Generate INTERFACES.md** with shared contracts for parallel workers
5. Create phase folders: \${SESSION_PATH}/PHASE_1/, PHASE_2/, etc.
6. Write initial state to EXECUTION_STATE.md
7. Log: \`[PARSE] Plan parsed. Found N phases, M tasks total.\`

---

## Phase 2: Phased Execution (via Oraca)

For each phase in sequential order, spawn Oraca[X] SYNCHRONOUSLY:

\`\`\`bash
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "
# Oraca[X] - Phase Orchestrator

You are Oraca[\${PHASE_NUM}], the Phase Orchestrator for Phase \${PHASE_NUM}.

## Your Mission
Execute all tasks in Phase \${PHASE_NUM} and report back to Opus.

## Session Info
- SESSION_PATH: \${SESSION_PATH}
- PHASE_FOLDER: \${SESSION_PATH}/PHASE_\${PHASE_NUM}/
- WORKSPACE: \$(pwd)

## Your Phase Tasks
\${PHASE_TASKS}

## Interfaces (from INTERFACES.md)
\${RELEVANT_INTERFACES}

## Execution Rules
1. **Max 3 parallel workers** - Never spawn more than 3 workers at once
2. **Sync spawns only** - Wait for each worker batch to complete
3. **Evidence required** - Each worker writes TASK_[ID]_EVIDENCE.md
4. **Retry limit** - Max 2 retries per task before marking BLOCKED

## Your Workflow

### Step 1: Create Phase Folder Structure
\\\`\\\`\\\`bash
mkdir -p \${SESSION_PATH}/PHASE_\${PHASE_NUM}/WORKER_OUTPUTS
\\\`\\\`\\\`

### Step 2: Initialize ORACA_LOG.md
Write to \${SESSION_PATH}/PHASE_\${PHASE_NUM}/ORACA_LOG.md

### Step 3: Execute Tasks
For each task (or batch of up to 3 parallel tasks):

Spawn Flash worker:
\\\`\\\`\\\`bash
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p '
# Task Worker

## Your Task
Task ID: [TASK_ID]
Description: [TASK_DESCRIPTION]
Success Criteria: [SUCCESS_CRITERIA]
Files to modify: [FILES]

## Interfaces You Must Follow
[RELEVANT_INTERFACES]

## Your Output
1. Execute the task completely
2. Write evidence to: \${SESSION_PATH}/PHASE_\${PHASE_NUM}/WORKER_OUTPUTS/TASK_[ID]_EVIDENCE.md

Evidence format:
\\\\\\\`\\\\\\\`\\\\\\\`markdown
# Task [ID] Evidence

## Task: [Description]

## Changes Made
- [File]: [What changed]

## Verification
- [How to verify this works]

## Status: COMPLETE | PARTIAL | BLOCKED
\\\\\\\`\\\\\\\`\\\\\\\`

Be thorough. Your work will be verified by QA.
'
\\\`\\\`\\\`

### Step 4: Spawn Phase QA
After all tasks complete, spawn Pro Phase QA:

\\\`\\\`\\\`bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p '
# Phase QA Reviewer

## Your Mission
Review ALL work done in Phase \${PHASE_NUM} and provide a verdict.

## Files to Review
- All evidence in: \${SESSION_PATH}/PHASE_\${PHASE_NUM}/WORKER_OUTPUTS/
- Phase tasks were: \${PHASE_TASKS}

## Review Checklist
1. **Completeness**: Was each task fully implemented?
2. **Correctness**: Does the implementation match the task description?
3. **Interface Compliance**: Do outputs match INTERFACES.md contracts?
4. **Evidence Quality**: Is evidence sufficient to verify work?

## Your Output
Write verdict to: \${SESSION_PATH}/PHASE_\${PHASE_NUM}/PHASE_QA.md

Format:
\\\\\\\`\\\\\\\`\\\\\\\`markdown
# Phase \${PHASE_NUM} QA Review

## Summary
[Overall assessment]

## Task Reviews
| Task ID | Status | Issues |
|---------|--------|--------|
| ... | PASS/FAIL | ... |

## Verdict: APPROVED | NEEDS_FIXES | BLOCKED
[If NEEDS_FIXES, list specific issues to address]
\\\\\\\`\\\\\\\`\\\\\\\`
'
\\\`\\\`\\\`

### Step 5: Handle QA Result
- If APPROVED: Write PHASE_REPORT.md with status COMPLETE
- If NEEDS_FIXES: Spawn fix workers, re-run Phase QA (max 2 iterations)
- If BLOCKED: Write PHASE_REPORT.md with status BLOCKED, document blockers

### Step 6: Write Phase Report
Write to \${SESSION_PATH}/PHASE_\${PHASE_NUM}/PHASE_REPORT.md:
\\\`\\\`\\\`markdown
# Phase \${PHASE_NUM} Report

## Status: COMPLETE | PARTIAL | BLOCKED

## Tasks Summary
| Task ID | Status | Evidence File |
|---------|--------|---------------|
| ... | ... | ... |

## QA Verdict: [APPROVED/etc]

## Issues (if any)
[List any issues or blockers]

## Files Modified
[List all files changed in this phase]
\\\`\\\`\\\`

Report back to Opus when complete.
"
\`\`\`

**WAIT for Oraca[X] to complete, then log and continue to next phase.**

---

## Phase 3: QA Synthesis

After all phases complete, spawn Pro QA Synthesizer:

\`\`\`bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "
# QA Synthesis Agent

## Your Mission
Analyze ALL phase QA reports and identify cross-phase patterns.

## Files to Read
- All PHASE_X/PHASE_QA.md files
- All PHASE_X/PHASE_REPORT.md files

## Analysis Tasks
1. **Common Issues**: What problems appeared across multiple phases?
2. **Quality Patterns**: Which phases had cleanest execution?
3. **Interface Compliance**: Any cross-phase integration issues?
4. **Risk Areas**: What should the Sweeper focus on?

## Your Output
Write to: \${SESSION_PATH}/ANALYSIS/QA_SYNTHESIS.md

Format:
\\\`\\\`\\\`markdown
# QA Synthesis Report

## Cross-Phase Patterns
[Common issues, quality observations]

## Phase Quality Summary
| Phase | Quality Score | Key Issues |
|-------|---------------|------------|
| ... | ... | ... |

## Integration Concerns
[Any cross-phase compatibility issues]

## Sweeper Focus Areas
[What the 15% hunter should look for]
\\\`\\\`\\\`
"
\`\`\`

---

## Phase 4: Sweep (The 15% Hunter)

Spawn Pro Sweeper:

\`\`\`bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "
# Sweeper Agent - The 15% Hunter

## Your Adversarial Mission
Assume 15% of tasks were missed or partially implemented. Find them.

## Files to Read
1. Original plan: \${PLAN_PATH}
2. All phase reports: PHASE_X/PHASE_REPORT.md
3. All worker evidence: PHASE_X/WORKER_OUTPUTS/
4. QA synthesis: ANALYSIS/QA_SYNTHESIS.md

## Hunt For
1. **Missing Tasks**: Tasks in plan that have no evidence
2. **Partial Work**: Tasks claimed complete but missing pieces
3. **Integration Gaps**: Cross-phase connections that don't work
4. **Edge Cases**: Error handling, validation, boundary conditions
5. **File Verification**: Do claimed files actually exist with expected content?

## Your Output
Write to: \${SESSION_PATH}/ANALYSIS/SWEEP_REPORT.md

Format:
\\\`\\\`\\\`markdown
# Sweep Report

## Verdict: CLEAN | GAPS_FOUND

## Findings
| ID | Type | Description | Severity | Fix Required |
|----|------|-------------|----------|--------------|
| ... | MISSING/PARTIAL/INTEGRATION | ... | HIGH/MEDIUM/LOW | Yes/No |

## Verification Results
- Files checked: [N]
- Files missing: [list]
- Files incomplete: [list]

## Recommended Fixes
[If GAPS_FOUND, list specific fix tasks]
\\\`\\\`\\\`

Be adversarial. Your job is to find what was missed.
"
\`\`\`

If GAPS_FOUND:
1. Create fix tasks from Sweeper recommendations
2. Spawn Oraca[FIX] to execute fixes
3. Re-sweep after fixes

---

## Phase 5: Validation & Report

1. Run automated checks (if applicable):
   \`\`\`bash
   # Tests
   uv run pytest tests/ -v 2>&1 | head -50

   # Linting (if applicable)
   # Build verification (if applicable)
   \`\`\`

2. Generate COMPLETION_REPORT.md:

\`\`\`markdown
# Execution Completion Report

## Plan: \${PLAN_SLUG}
## Status: COMPLETE | PARTIAL | FAILED

## Execution Summary
| Phase | Status | Tasks | Issues |
|-------|--------|-------|--------|
| ... | ... | ... | ... |

## Sweep Result: CLEAN | GAPS_FOUND
[Summary of sweep findings]

## Automated Checks
- Tests: PASS/FAIL
- Linting: PASS/FAIL/N/A

## Files Modified
[Complete list of all files changed]

## Remaining Issues (if any)
[List any unresolved issues]

## Recommendations
[Any follow-up actions needed]
\`\`\`

3. Log: \`[DONE] Execution complete. Status: [STATUS]\`
4. Report to HD

---

ORCHESTRATOR_PROMPT
)"
```

---

## Output Artifacts

| Artifact | Location | Creator |
|----------|----------|---------|
| EXECUTION_STATE.md | `${SESSION_PATH}/` | Opus (updated each phase) |
| ORCHESTRATOR_LOG.md | `${SESSION_PATH}/` | Opus (append-only) |
| INTERFACES.md | `${SESSION_PATH}/` | Opus (Phase 1) |
| ORACA_LOG.md | `${SESSION_PATH}/PHASE_X/` | Oraca (append-only) |
| TASK_*_EVIDENCE.md | `${SESSION_PATH}/PHASE_X/WORKER_OUTPUTS/` | Flash Workers |
| PHASE_QA.md | `${SESSION_PATH}/PHASE_X/` | Pro Phase QA |
| PHASE_REPORT.md | `${SESSION_PATH}/PHASE_X/` | Oraca (summary for Opus) |
| QA_SYNTHESIS.md | `${SESSION_PATH}/ANALYSIS/` | Pro (Phase 3) |
| SWEEP_REPORT.md | `${SESSION_PATH}/ANALYSIS/` | Pro (Phase 4) |
| COMPLETION_REPORT.md | `${SESSION_PATH}/` | Opus (Phase 5) |

---

## The Execution Mantra

```
I parse phases before I execute.
I delegate to Oraca, not workers.
I isolate each phase's context.
I verify at phase boundaries.
I synthesize before I sweep.
I hunt the 15% that was missed.
Trust but Verify.
```

---

## Integration with Think-Tank

This command executes plans generated by `/think-tank`:

```
/think-tank → DECIDE → execution-plan.yaml
                           ↓
/hc-plan-execute TOPIC: {topic}
                           ↓
                COMPLETION_REPORT.md
```

**Unified Workspace:** All artifacts live in the think-tank folder:
```
.claude/PM/think-tank/{topic}_{date}/
├── STATE.yaml              # Think-tank session state
├── execution-plan.yaml     # The plan (status: approved)
├── 04_DECISION_MAP.md      # Decision context
└── ...                     # Other think-tank artifacts
```

**Execution Output:** Stored in hc-plan-execute folder:
```
.claude/PM/hc-plan-execute/{topic}_{date}/
├── EXECUTION_STATE.md
├── PHASE_*/
└── COMPLETION_REPORT.md
```

The execution-plan.yaml `execution.session_path` links to the execution folder.

---

## Related

| Related | When to Use Instead |
|---------|---------------------|
| `/think-tank` | Research, decisions, AND plan generation (produces the plan) |
| Direct implementation | Single small task, no QA needed |
| Manual execution | When you want HeyDude in the loop for each task |

---

**Version:** V2.5.0
**Updated:** 2026-01-02
**Status:** Production-ready (Self-contained prompts, no template indirection)

## V2.5.0 Changelog
- Updated to read execution-plan.yaml from think-tank folders
- Added TOPIC parameter for auto-locating approved plans
- Integrated with think-tank plan_status tracking in context.yaml
- Removed dependency on deprecated /hc-plan command
