---
version: V1.2.0
status: current
timestamp: 2025-12-30
tags: [command, audit, red-team, multi-agent, system-review]
description: "G.L.A.S.S. - Global Logic & Architecture System Scan with 6 sector Pro commanders, Flash swarm, and Classification Arbiter"
---

# /hc-glass - Global Logic & Architecture System Scan

> **G.L.A.S.S.** = **G**lobal **L**ogic & **A**rchitecture **S**ystem **S**can

**Philosophy:** "Trust nothing. Verify everything. Cite line numbers or it didn't happen."

**Purpose:** Execute a brutal honesty audit of any codebase across 6 specialized fronts. Find the rot, the lies, and the fragile logic.

---

## Quick Start

```markdown
/hc-glass

TARGET: ${PWD}  # Defaults to current project
DEPTH: [quick|standard|deep]
FOCUS: [all|adr|flow|tests|rot|security]

CONCERNS:
- [Optional: specific areas to investigate]
```

This command spawns a background Opus orchestrator that coordinates 6 sector Pro commanders (each with Flash scouts), a Merge Gate synthesizer, and a Classification Arbiter that verifies finding classifications. You'll be notified when the Board Report is ready.

---

## Architecture Overview

```
HD invokes /hc-glass
     |
Spawn OPUS Orchestrator (BACKGROUND)
     |
+-----------------------------------------------------------------------------+
|  PHASE 0: SETUP & VALIDATION                                                |
|  - Create session folder: .claude/PM/hc-glass/${session-slug}/                 |
|  - Validate target paths exist                                              |
|  - Initialize Flight Recorder                                               |
+-----------------------------------------------------------------------------+
|  PHASE 1: THE SWARM (5 Pro Sector Commanders, parallel)                     |
|                                                                             |
|  +------------------+  +------------------+  +------------------+           |
|  | Unit 1:          |  | Unit 2:          |  | Unit 3:          |           |
|  | Archaeologists   |  | Plumbers         |  | Critics          |           |
|  | (Pro)            |  | (Pro)            |  | (Pro)            |           |
|  |   |              |  |   |              |  |   |              |           |
|  |   +-> Flash x3   |  |   +-> Flash x3   |  |   +-> Flash x3   |           |
|  |   |   (seq)      |  |   |   (seq)      |  |   |   (seq)      |           |
|  |   v              |  |   v              |  |   v              |           |
|  | SECTOR_1.md      |  | SECTOR_2.md      |  | SECTOR_3.md      |           |
|  +------------------+  +------------------+  +------------------+           |
|                                                                             |
|  +------------------+  +------------------+                                 |
|  | Unit 4:          |  | Unit 5:          |                                 |
|  | Janitors         |  | Guards           |                                 |
|  | (Pro)            |  | (Pro)            |                                 |
|  |   |              |  |   |              |                                 |
|  |   +-> Flash x3   |  |   +-> Flash x3   |                                 |
|  |   |   (seq)      |  |   |   (seq)      |                                 |
|  |   v              |  |   v              |                                 |
|  | SECTOR_4.md      |  | SECTOR_5.md      |                                 |
|  +------------------+  +------------------+                                 |
+-----------------------------------------------------------------------------+
|  PHASE 2: MERGE GATE (Pro Synthesizer)                                    |
|  - Reads 6 sector syntheses                                                 |
|  - Deduplicates cross-sector findings                                       |
|  - Validates citations exist                                                |
|  - Outputs: CROSS_SECTOR_SYNTHESIS.md                                       |
+-----------------------------------------------------------------------------+
|  PHASE 3: CLASSIFICATION ARBITER (Pro)                                   |
|  - Reads CROSS_SECTOR_SYNTHESIS.md                                          |
|  - Verifies classification of each finding (Doc Lie vs Code Gap)            |
|  - Reclassifies findings as needed using decision tree                      |
|  - Outputs: ANALYSIS/VERIFIED_SYNTHESIS.md                                  |
+-----------------------------------------------------------------------------+
|  PHASE 4: THE BOARD REPORT (Opus)                                           |
|  - Reads VERIFIED_SYNTHESIS.md (NOT raw synthesis)                          |
|  - Prioritizes by severity                                                  |
|  - Writes final report with 4 lists                                         |
|  - Outputs: SYSTEM_REVIEW_GLASS.md                                          |
+-----------------------------------------------------------------------------+
|  OUTPUT: .claude/PM/hc-glass/${session-slug}/SYSTEM_REVIEW_GLASS.md            |
+-----------------------------------------------------------------------------+
```

---

## Session Folder Structure

```
.claude/PM/hc-glass/${session-slug}/
|-- ORCHESTRATOR_LOG.md              # Flight Recorder (append-only)
|-- PATH_VALIDATION.md               # Phase 0: Path existence check
|
|-- SECTOR_1_ARCHAEOLOGISTS/
|   |-- flash_1_adr_reality.md       # ADR vs Implementation check
|   |-- flash_2_transitions.md       # State machine verification
|   |-- flash_3_zombies.md           # TODO/FIXME archaeology
|   +-- SECTOR_1_SYNTHESIS.md        # Pro commander synthesis
|
|-- SECTOR_2_PLUMBERS/
|   |-- flash_1_context_flow.md      # Context object tracing
|   |-- flash_2_timeout_recovery.md  # Timeout/recovery paths
|   |-- flash_3_recursion.md         # Recursion depth limits
|   +-- SECTOR_2_SYNTHESIS.md        # Pro commander synthesis
|
|-- SECTOR_3_CRITICS/
|   |-- flash_1_happy_path.md        # Happy-path-only tests
|   |-- flash_2_mock_abuse.md        # Over-mocking analysis
|   |-- flash_3_fragility.md         # Hardcoded strings/timestamps
|   +-- SECTOR_3_SYNTHESIS.md        # Pro commander synthesis
|
|-- SECTOR_4_JANITORS/
|   |-- flash_1_ghost_features.md    # Unused exports
|   |-- flash_2_log_noise.md         # Unstructured logging
|   |-- flash_3_heavy_deps.md        # Oversized dependencies
|   +-- SECTOR_4_SYNTHESIS.md        # Pro commander synthesis
|
|-- SECTOR_5_GUARDS/
|   |-- flash_1_path_validation.md   # File write path checks
|   |-- flash_2_key_exposure.md      # API key handling
|   |-- flash_3_permissions.md       # Agent permission boundaries
|   +-- SECTOR_5_SYNTHESIS.md        # Pro commander synthesis
|
|-- SECTOR_6_REGISTRARS/
|   |-- flash_1_agent_registry.md    # Agent vs ADR-1201 count
|   |-- flash_2_skill_bidirectional.md # Agent-skill cross-check
|   |-- flash_3_adr_cycles.md        # Dependency cycle detection
|   +-- SECTOR_6_SYNTHESIS.md        # Pro commander synthesis
|
|-- ANALYSIS/
|   |-- CROSS_SECTOR_SYNTHESIS.md    # Phase 2: Merged findings
|   +-- VERIFIED_SYNTHESIS.md        # Phase 3: Classification-verified findings
|
+-- SYSTEM_REVIEW_GLASS.md           # Final Board Report
```

---

## Session Identity

```yaml
GLASS_DEPTH: "${DEPTH}"              # quick|standard|deep
GLASS_FOCUS: "${FOCUS}"              # all|adr|flow|tests|rot|security
SESSION_PATH: ".claude/PM/hc-glass/${SESSION_SLUG}/"

# Flash agents per sector by depth:
# quick: 1 Flash per sector (5 total)
# standard: 2 Flash per sector (10 total)
# deep: 3 Flash per sector (15 total)
```

---

## Proxy Configuration

```bash
# Orchestrator (Opus) - Owns session, writes Board Report
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions

# Sector Commander (Pro) - Coordinates Flash scouts, synthesizes findings
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions

# Scout (Flash) - Executes specific search mission, cites line numbers
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions
```

---

## Orchestrator Execution

When this command is invoked, spawn a background Opus orchestrator:

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "
$(cat <<'ORCHESTRATOR_PROMPT'

# G.L.A.S.S. System Review Orchestrator
# Global Logic & Architecture System Scan

You are the orchestrator for Operation: DEEP DIVE. Your adversarial prior: **15% of this codebase is broken, undocumented, or lying to us.** Your job is to find it.

## Core Philosophy

"Trust nothing. Verify everything. Cite line numbers or it didn't happen."

## Session Parameters

- TARGET: ${TARGET:-$(pwd)}
- DEPTH: ${DEPTH:-standard}
- FOCUS: ${FOCUS:-all}
- WORKSPACE: $(pwd)

## CRITICAL: Sub-Agent Spawn Rules

**NEVER use fire-and-forget spawning.** Every sub-agent must be spawned SYNCHRONOUSLY:

\`\`\`bash
# CORRECT: Synchronous spawn - wait for completion
log_event "[SPAWN] Commander dispatched for Sector X"

AGENT_OUTPUT=\$(ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "PROMPT" 2>&1)
AGENT_EXIT=\$?

# Log IMMEDIATELY after sub-agent returns
if [ \$AGENT_EXIT -eq 0 ]; then
    log_event "[SECTOR] Sector X complete. Findings: N"
else
    log_event "[ERROR] Sector X Commander failed with exit code \$AGENT_EXIT"
fi
\`\`\`

**WHY:** Fire-and-forget spawning causes the orchestrator to exit before sub-agents complete. Logs never get updated, phases never continue.

**Anti-Pattern (DO NOT USE):**
\`\`\`bash
# WRONG: Spawns and exits immediately
claude -p "..." &  # Fire and forget - NEVER DO THIS
\`\`\`

**Pro Commanders Spawning Flash Scouts:** Each Pro Commander must also spawn Flash scouts SYNCHRONOUSLY and wait for their completion before writing the sector synthesis.

## IMPORTANT: Execute All Phases Sequentially

You MUST complete ALL phases in order. Do not stop after Phase 1.
After each phase, immediately proceed to the next.

## PHASE 0: Setup & Validation

1. Create session folder:
   ```bash
   mkdir -p .claude/PM/hc-glass/\${SESSION_SLUG}/{SECTOR_1_ARCHAEOLOGISTS,SECTOR_2_PLUMBERS,SECTOR_3_CRITICS,SECTOR_4_JANITORS,SECTOR_5_GUARDS,SECTOR_6_REGISTRARS,ANALYSIS}
   ```

2. Initialize ORCHESTRATOR_LOG.md (Flight Recorder):
   ```markdown
   # GLASS Operation: DEEP DIVE
   Target: ${TARGET}
   Depth: ${DEPTH}
   Started: [TIMESTAMP]

   ## Event Log
   [INIT] Session initialized. Adversarial prior: 15% is broken.
   ```

3. Validate target paths exist for each sector. Write to PATH_VALIDATION.md:
   ```markdown
   | Sector | Expected Path | Status | Notes |
   |--------|---------------|--------|-------|
   | 1 | docs/adr/ or .claude/SSoT/ADRs/ | [FOUND/MISSING] | [count] |
   | 1 | src/ | [FOUND/MISSING] | |
   | ... | ... | ... | ... |
   ```

4. If a sector has 0 valid paths, mark SKIP and log: `[SKIP] Sector X: No valid paths`

## PHASE 1: The Swarm

Spawn 5 Pro Sector Commanders IN PARALLEL. Each commander owns one sector.

### Sector 1: The Archaeologists (ADR vs Reality)

**Pro Commander Prompt:**
```
You are the Archaeologist Commander for Operation: DEEP DIVE.

MISSION: "Trust nothing. Verify everything."

TARGET PATHS:
- Docs: docs/adr/ (or .claude/SSoT/ADRs/ if exists)
- Code: src/

SPAWN 3 FLASH SCOUTS (sequential):

SCOUT 1 - ADR Reality Check:
"Find and read architectural decision records. Do the implementations ACTUALLY enforce what the ADRs describe, or are they incomplete? Compare the ADR's stated rules to the implementation. CITE LINE NUMBERS for every discrepancy."

SCOUT 2 - Transition Verification:
"Read workflow/state machine ADRs if they exist. Trace state transitions in code. Are there transitions in code that are ILLEGAL according to the docs? Are there documented transitions that are NEVER USED? CITE LINE NUMBERS."

SCOUT 3 - Zombie TODOs:
"Find all TODO and FIXME comments. Cross-reference them with BACKLOG.md or TODO.md if they exist. Which ones are Zombie TODOs (never tracked)? List each with file:line."

OUTPUT: SECTOR_1_ARCHAEOLOGISTS/SECTOR_1_SYNTHESIS.md

Format:
| Finding ID | Type | File:Line | Description | Severity |
|------------|------|-----------|-------------|----------|
| ARCH-001 | ADR vs Code | src/foo.py:42 | ADR says X, code does Y | CRITICAL |

CITATION REQUIRED: No finding counts without a file:line reference.
```

### Sector 2: The Plumbers (Data Flow & Logic)

**Pro Commander Prompt:**
```
You are the Plumber Commander for Operation: DEEP DIVE.

MISSION: "Find the leaks."

TARGET PATHS:
- Code: src/
- Code: lib/ (if exists)

SPAWN 3 FLASH SCOUTS (sequential):

SCOUT 1 - Context Flow:
"Trace the context object from input -> agent -> output. Where is data DROPPED? Where is strict typing LOST (cast to Any, Dict[str, Any])? CITE LINE NUMBERS."

SCOUT 2 - Timeout Recovery:
"Find the main while loops in orchestration code. What happens if an agent TIMES OUT? Is there a recovery path, or does it hang? Look for missing try/except, missing timeout parameters. CITE LINE NUMBERS."

SCOUT 3 - Recursion Check:
"Find recursive function calls. Is there a DEPTH LIMITER? If not, flag as CRITICAL RISK. Look for: recursive spawns, nested agent calls, retry loops without counters. CITE LINE NUMBERS."

OUTPUT: SECTOR_2_PLUMBERS/SECTOR_2_SYNTHESIS.md

CITATION REQUIRED: No finding counts without a file:line reference.
```

### Sector 3: The Critics (Test Quality)

**Pro Commander Prompt:**
```
You are the Critic Commander for Operation: DEEP DIVE.

MISSION: "Expose the fake tests."

TARGET PATHS:
- Tests: tests/, test/, spec/
- Tests: **/test_*.py, **/*_test.py, **/*.test.ts, **/*.spec.ts

SPAWN 3 FLASH SCOUTS (sequential):

SCOUT 1 - Happy Path Audit:
"Identify tests that ONLY test success scenarios. Flag any test file that has 0 tests for failure modes, edge cases, or error paths. List file and what's missing."

SCOUT 2 - Mock Abuse:
"Find tests that mock so heavily they don't test actual code. Look for: >3 mocks in one test, mocking the function being tested, mocking everything except assertions. CITE LINE NUMBERS."

SCOUT 3 - Fragility Check:
"Find tests that rely on: hardcoded strings, precise timestamps, file system paths, environment variables. These break on different machines. CITE LINE NUMBERS."

OUTPUT: SECTOR_3_CRITICS/SECTOR_3_SYNTHESIS.md

CITATION REQUIRED: No finding counts without a file:line reference.
```

### Sector 4: The Janitors (Rot & Dead Code)

**Pro Commander Prompt:**
```
You are the Janitor Commander for Operation: DEEP DIVE.

MISSION: "If it doesn't pay rent, evict it."

TARGET PATHS:
- Entire codebase: ${TARGET}

SPAWN 3 FLASH SCOUTS (sequential):

SCOUT 1 - Ghost Features:
"Find functions that are defined/exported but NEVER imported or called anywhere. These are ghosts. Use grep to verify. CITE LINE NUMBERS."

SCOUT 2 - Log Noise:
"Find print() statements or console.log that are NOT using the structured logger. These pollute the stream and break parsing. CITE LINE NUMBERS."

SCOUT 3 - Heavy Dependencies:
"Read pyproject.toml or package.json. Pick the 5 HEAVIEST-LOOKING packages (large frameworks, data science libs, etc). Then SEARCH the codebase for 'import [package]' or 'from [package]'. If you find FEWER THAN 3 FILES importing it, flag as 'bloat candidate'. CITE the specific import lines found. Do NOT guess usage counts - actually search."

OUTPUT: SECTOR_4_JANITORS/SECTOR_4_SYNTHESIS.md

CITATION REQUIRED: No finding counts without a file:line reference.
```

### Sector 5: The Security Guards (Permissions & Safety)

**Pro Commander Prompt:**
```
You are the Guard Commander for Operation: DEEP DIVE.

MISSION: "Assume the user is trying to break it."

TARGET PATHS:
- Code: src/
- Code: lib/ (if exists)

SPAWN 3 FLASH SCOUTS (sequential):

SCOUT 1 - Path Validation:
"Find all file write operations. Is there a path validation check BEFORE every write? Can a malicious input overwrite ADRs, configs, or .claude/ files? CITE LINE NUMBERS."

SCOUT 2 - Key Exposure:
"Check API key handling. Are keys EVER passed in clear text in logs, contexts, or error messages? Search for: 'api_key', 'secret', 'token' in logs. CITE LINE NUMBERS."

SCOUT 3 - Permission Boundaries:
"Check if agents have bounded permissions. Can a Code Worker agent execute arbitrary bash? Can it modify files outside its scope? CITE LINE NUMBERS of permission checks (or lack thereof)."

OUTPUT: SECTOR_5_GUARDS/SECTOR_5_SYNTHESIS.md

CITATION REQUIRED: No finding counts without a file:line reference.
```

### Sector 6: The Registrars (SSoT Alignment)

**Pro Commander Prompt:**
```
You are the Registrar Commander for Operation: DEEP DIVE.

MISSION: "Every artifact must be registered. Every reference must resolve."

TARGET PATHS:
- ADRs: docs/adr/ (or .claude/SSoT/ADRs/)
- Agents: .claude/agents/ (if exists)
- Skills: .claude/skills/ (if exists)
- Indexes: ADR_INDEX.md, SKILLS_INDEX.md, README.md

TOOLS AVAILABLE: You have Bash, Grep, Glob, Read access. USE THEM.

SPAWN 3 FLASH SCOUTS (sequential):

SCOUT 1 - Agent Registry Check:
"Count all .md files in .claude/agents/ directory (if exists, exclude any README or INDEX files).
Cross-reference against any agent constitution ADR if it exists.
Compare the counts. If they don't match, list WHICH agents are:
  - In agents/ but NOT documented (orphans)
  - Documented but NOT in agents/ (ghosts)
CITE file paths for each discrepancy."

SCOUT 2 - Skill Bidirectional Check:
"For EACH agent file in .claude/agents/ (if exists):
  1. Read its frontmatter 'skills:' field
  2. For each skill listed, verify that skill folder EXISTS in .claude/skills/
  3. Read that skill's SKILL.md and check if 'used_by:' includes this agent

For EACH skill's SKILL.md:
  1. Read its 'used_by:' field
  2. Verify each agent listed actually has this skill in its frontmatter

Flag mismatches:
  - Agent claims skill X, but skill X doesn't exist
  - Agent claims skill X, but skill X's used_by doesn't include agent
  - Skill's used_by claims agent Y, but agent Y doesn't list skill
CITE file:line for each mismatch."

SCOUT 3 - ADR Dependency Cycle Check:
"Parse ALL ADR files in docs/adr/ (or .claude/SSoT/ADRs/).
Extract the 'depends_on:' frontmatter field from each.
Build a dependency graph (adjacency list):
  ADR-1101 -> [ADR-2001, ADR-2201]
  ADR-2001 -> [ADR-1101]  # This would be a cycle!

Run depth-first search to detect cycles.
If cycle found, flag as CRITICAL and report the cycle path.
Example output: 'CYCLE DETECTED: ADR-1101 -> ADR-2001 -> ADR-1101'
CITE the specific ADR files involved."

OUTPUT: SECTOR_6_REGISTRARS/SECTOR_6_SYNTHESIS.md

Format:
| Finding ID | Type | Artifact | Issue | Severity |
|------------|------|----------|-------|----------|
| REG-001 | Orphan Agent | agents/foo.md | Not in ADR-1201 | MAJOR |
| REG-002 | Skill Mismatch | agents/bar.md | Claims skill-x, not in used_by | MINOR |
| REG-003 | ADR Cycle | ADR-1101, ADR-2001 | Circular dependency | CRITICAL |

CITATION REQUIRED: No finding counts without file references.
```

### Commander Parallelism Rules

- Spawn all 6 Pro Commanders in PARALLEL (they don't depend on each other)
- Each Commander spawns Flash scouts SEQUENTIALLY (within sector)
- Wait for ALL 6 Commanders to complete before Phase 2
- Log: `[SECTOR] Sector X complete. Findings: N`

## PHASE 2: Merge Gate

After all 6 sectors complete, spawn Pro Synthesizer:

```
You are the Synthesizer for Operation: DEEP DIVE.

MISSION: Merge 6 sector reports into one coherent analysis.

INPUT FILES:
- SECTOR_1_ARCHAEOLOGISTS/SECTOR_1_SYNTHESIS.md
- SECTOR_2_PLUMBERS/SECTOR_2_SYNTHESIS.md
- SECTOR_3_CRITICS/SECTOR_3_SYNTHESIS.md
- SECTOR_4_JANITORS/SECTOR_4_SYNTHESIS.md
- SECTOR_5_GUARDS/SECTOR_5_SYNTHESIS.md
- SECTOR_6_REGISTRARS/SECTOR_6_SYNTHESIS.md

TASKS:

1. DEDUPLICATE: Same finding reported by multiple sectors? Merge into one.

2. VALIDATE CITATIONS: Every finding claims a file:line. VERIFY the file exists.
   If file doesn't exist -> MARK AS HALLUCINATION -> DISCARD
   If line number out of range -> MARK AS HALLUCINATION -> DISCARD

3. CROSS-SECTOR PATTERNS: Does the same root cause appear across sectors?
   Example: "Missing path validation" appears in Sectors 2, 4, 5 -> Systemic issue

4. PRIORITIZE: Rank by severity
   - CRITICAL: Security holes, data loss, infinite loops
   - MAJOR: ADR lies, missing tests for core paths
   - MINOR: Dead code, style issues
   - INFO: Suggestions, not bugs

OUTPUT: ANALYSIS/CROSS_SECTOR_SYNTHESIS.md

Format:
## Critical Findings (The Panic List)
| ID | Description | Sectors | File:Line | Root Cause |
|----|-------------|---------|-----------|------------|

## Major Findings (The Lie List)
...

## Minor Findings (The Kill List)
...

## Hallucinations Discarded
| Sector | Claimed Finding | Reason Discarded |
|--------|-----------------|------------------|
| 3 | "test_foo.py:999 missing coverage" | File only has 50 lines |
```

## PHASE 3: Classification Arbiter

After Merge Gate completes, spawn Pro Classification Arbiter:

```
You are the Classification Arbiter for Operation: DEEP DIVE.

MISSION: Verify that every finding is correctly classified before the Board Report.

INPUT: ANALYSIS/CROSS_SECTOR_SYNTHESIS.md

CLASSIFICATION DECISION TREE:

For each finding in the Lie List (Major - Documentation is Wrong):
  ASK: "Is the documentation count/claim factually wrong?"
    - If YES → Confirm as DOC LIE (documentation needs update)
    - If NO → ASK: "Is the documentation correct but code incomplete?"
      - If YES → RECLASSIFY as CODE GAP → Move to Panic List
      - If NO → Investigate further

For each finding in the Panic List (Critical):
  ASK: "Is this a missing implementation of documented behavior?"
    - If YES → Confirm as CODE GAP
    - If NO → ASK: "Is this documentation claiming something false?"
      - If YES → RECLASSIFY as DOC LIE → Move to Lie List
      - If NO → Confirm as SECURITY/LOGIC issue

For each finding in the Kill List (Minor - Dead Code):
  ASK: "Is this code actually referenced somewhere we missed?"
    - If YES → DISCARD (false positive)
    - If NO → Confirm as DEAD CODE

For each finding in the Debt List (Tech Debt):
  ASK: "Is this a 'should have' or a 'must have'?"
    - If MUST HAVE → ESCALATE to Panic/Lie List
    - If SHOULD HAVE → Confirm as DEBT

VERIFICATION QUESTIONS BY LIST:

| List | Verify Question |
|------|-----------------|
| Lie | "Does the doc actually say what we claim it says?" |
| Panic | "Does the code actually have this gap?" |
| Kill | "Is this truly unused, or did we miss a reference?" |
| Debt | "Is this cleanup or correctness?" |

OUTPUT: ANALYSIS/VERIFIED_SYNTHESIS.md

FORMAT:
## Verified Critical Findings (The Panic List)
| ID | Description | File:Line | Classification | Verification |
|----|-------------|-----------|----------------|--------------|
| PANIC-001 | [description] | [file:line] | CODE GAP (verified) | [how verified] |

## Verified Major Findings (The Lie List)
| ID | What Doc Says | What Code Does | File:Line | Classification | Verification |
|----|---------------|----------------|-----------|----------------|--------------|
| LIE-001 | [claim] | [reality] | [file:line] | DOC LIE (verified) | [how verified] |

## Verified Minor Findings (The Kill List)
| ID | File:Line | Why Delete | Classification | Verification |
|----|-----------|------------|----------------|--------------|
| KILL-001 | [file:line] | [reason] | DEAD CODE (verified) | [how verified] |

## Verified Debt Findings (The Debt List)
| ID | Description | File:Line | Classification | Verification |
|----|-------------|-----------|----------------|--------------|
| DEBT-001 | [description] | [file:line] | TECH DEBT (verified) | [how verified] |

## Reclassifications Made
| Original ID | Original List | New List | Reason |
|-------------|---------------|----------|--------|
| LIE-003 | Lie List | Panic List | Doc was correct, code incomplete |

## Findings Discarded
| Original ID | Original List | Reason |
|-------------|---------------|--------|
| KILL-005 | Kill List | Actually referenced in tests/ |

CITATION REQUIRED: Include verification notes for each finding.
```

## PHASE 4: The Board Report

Read ANALYSIS/VERIFIED_SYNTHESIS.md and write the final report.

OUTPUT: SYSTEM_REVIEW_GLASS.md

```markdown
---
operation: "DEEP DIVE"
target: ${TARGET}
depth: ${DEPTH}
timestamp: [ISO-8601]
sectors_run: 5
health_score: [0-100]%
---

# SYSTEM_REVIEW_GLASS.md

## Executive Summary

[2-3 sentences: Overall system health. Be brutal. No sugar-coating.]

## Health Score: [X]%

| Sector | Status | Critical | Major | Minor |
|--------|--------|----------|-------|-------|
| 1. Archaeologists (ADR vs Reality) | [PASS/WARN/FAIL] | [N] | [N] | [N] |
| 2. Plumbers (Data Flow) | [PASS/WARN/FAIL] | [N] | [N] | [N] |
| 3. Critics (Test Quality) | [PASS/WARN/FAIL] | [N] | [N] | [N] |
| 4. Janitors (Dead Code) | [PASS/WARN/FAIL] | [N] | [N] | [N] |
| 5. Guards (Security) | [PASS/WARN/FAIL] | [N] | [N] | [N] |
| 6. Registrars (SSoT Alignment) | [PASS/WARN/FAIL] | [N] | [N] | [N] |

---

## The Panic List (Critical - Fix IMMEDIATELY)

| ID | Description | File:Line | Suggested Fixer | Impact |
|----|-------------|-----------|-----------------|--------|
| PANIC-001 | [description] | [file:line] | [Agent Persona] | [what breaks] |

**Fixer Legend:** Archaeologist (ADR sync), Plumber (logic fix), Critic (test gap), Janitor (cleanup), Guard (security patch)

---

## The Lie List (Major - Documentation is Wrong)

| ID | What Doc Says | What Code Does | File:Line |
|----|---------------|----------------|-----------|
| LIE-001 | [ADR claim] | [actual behavior] | [file:line] |

---

## The Kill List (Minor - Delete This Code)

| ID | File:Line | Why Delete | Last Used |
|----|-----------|------------|-----------|
| KILL-001 | [file:line] | [ghost/zombie/unused] | [never/date] |

---

## The Debt List (Tech Debt - Fix When Able)

| ID | Description | File:Line | Effort | Priority |
|----|-------------|-----------|--------|----------|
| DEBT-001 | [description] | [file:line] | [S/M/L] | [1-5] |

---

## Cross-Sector Patterns

[Systemic issues that appear in multiple sectors]

---

## Recommendations

1. **Immediate:** [Critical items]
2. **Short-term:** [Major items]
3. **Backlog:** [Minor items]

---

## Sector Deep-Dives

[Links to SECTOR_X_SYNTHESIS.md files for details]

---

## Hallucinations Filtered

[Count] findings were discarded as hallucinations (cited files/lines that don't exist).

---

*Generated by Operation: DEEP DIVE*
*Philosophy: "Trust nothing. Verify everything."*
```

## Error Handling

### Flash Hallucination Filter (3-Strike Rule)

```
WHEN Flash claims a bug:
  1. REQUIRE file:line citation
  2. IF file doesn't exist -> STRIKE
  3. IF line number out of range -> STRIKE
  4. IF cited code doesn't match description -> STRIKE

ON 3 STRIKES (per Flash agent):
  - Discard all findings from that Flash agent
  - Log: [WARN] Flash agent [ID] produced 3 hallucinations. Discarding output.
  - Continue with remaining agents
```

### Sector Commander Timeout

```
IF sector Commander doesn't respond in 5 minutes:
  1. Log: [WARN] Sector X Commander timeout
  2. Mark sector as INCOMPLETE
  3. Continue with other sectors
  4. Note in final report: "Sector X incomplete due to timeout"
```

### All Paths Missing

```
IF all 5 sectors have 0 valid paths:
  1. Log: [CRITICAL] No valid paths found for any sector
  2. Write minimal report explaining the issue
  3. Recommend checking TARGET path
  4. Exit with error
```

### Sector Overflow

```
IF sector produces >20 findings:
  1. Pro Commander caps at top 10 by severity
  2. Log: [WARN] Sector X overflow: [N] findings capped to 10
  3. Note in synthesis: "Additional findings available in raw Flash output"
```

ORCHESTRATOR_PROMPT
)"
```

---

## The 6 Sectors (Units)

| Sector | Codename | Mission | Targets |
|--------|----------|---------|---------|
| 1 | Archaeologists | ADR vs Reality | ADRs/ vs src/ |
| 2 | Plumbers | Data Flow & Logic | Context, Events, Loops |
| 3 | Critics | Test Quality | tests/, spec/ |
| 4 | Janitors | Rot & Dead Code | Entire codebase |
| 5 | Guards | Permissions & Safety | File I/O, API handling |
| 6 | Registrars | SSoT Alignment | agents/, skills/, ADRs/, indexes |

---

## Depth Modes

| Depth | Flash per Sector | Total Agents | Use Case |
|-------|------------------|--------------|----------|
| `quick` | 1 | 6 Flash + 8 Pro + 1 Opus | Quick health check |
| `standard` | 2 | 12 Flash + 8 Pro + 1 Opus | Regular audit |
| `deep` | 3 | 18 Flash + 8 Pro + 1 Opus | Comprehensive review |

*Pro count: 6 Sector Commanders + 1 Synthesizer (Phase 2) + 1 Arbiter (Phase 3) = 8*

---

## Focus Modes

| Focus | Sectors Run | Use Case |
|-------|-------------|----------|
| `all` | 1-6 | Full audit |
| `adr` | 1 only | Documentation check |
| `flow` | 2 only | Logic audit |
| `tests` | 3 only | Test quality |
| `rot` | 4 only | Dead code cleanup |
| `security` | 5 only | Security review |
| `ssot` | 6 only | Registry alignment check |

---

## Output Artifacts

| Artifact | Location | Creator | Phase |
|----------|----------|---------|-------|
| ORCHESTRATOR_LOG.md | `${SESSION_PATH}/` | Opus | All |
| PATH_VALIDATION.md | `${SESSION_PATH}/` | Opus | 0 |
| flash_*.md | `${SESSION_PATH}/SECTOR_*/` | Flash | 1 |
| SECTOR_*_SYNTHESIS.md | `${SESSION_PATH}/SECTOR_*/` | Pro Commanders | 1 |
| CROSS_SECTOR_SYNTHESIS.md | `${SESSION_PATH}/ANALYSIS/` | Pro Synthesizer | 2 |
| VERIFIED_SYNTHESIS.md | `${SESSION_PATH}/ANALYSIS/` | Pro Arbiter | 3 |
| SYSTEM_REVIEW_GLASS.md | `${SESSION_PATH}/` | Opus | 4 |

---

## Circuit Breakers

| Guard | Trigger | Action |
|-------|---------|--------|
| **3-Strike Rule** | Flash cites 3 non-existent files | Discard that Flash's output |
| **Sector Timeout** | Commander takes >5 min | Mark INCOMPLETE, continue |
| **Overflow Cap** | >20 findings per sector | Cap to 10, note overflow |
| **Token Ceiling** | Session exceeds limit | Abort, save partial report |

---

## Comparison: /hc-glass vs /red-team

| Aspect | /hc-glass | /red-team |
|--------|--------|-----------|
| Focus | Code quality, find bugs + security issues | Documentation accuracy vs implementation |
| Sectors | 6 (code-focused) | 6 (doc-focused) |
| Naming | Military (Units) | Corporate (Sectors) |
| Output | The 4 Lists (Panic/Lie/Kill/Debt) | Kill List, Fix List, Gap Table |
| Tone | Aggressive | Professional |
| Classification | Phase 3 Arbiter verifies Doc Lie vs Code Gap | No classification verification |
| Use Case | Pre-release code audit | Documentation governance |

---

## The G.L.A.S.S. Mantra

```
Global Logic & Architecture System Scan

I trust nothing.
I verify everything.
I cite line numbers or it didn't happen.
I hunt the rot, the lies, and the fragile.
I filter hallucinations before I report.
I verify classifications before I accuse.
I am the brutal truth.
I am transparent. I am sharp. I cut through the noise.
```

---

## Related

| Document | Purpose |
|----------|---------|
| [ORCHESTRATION_PATTERNS.md](../../ORCHESTRATION_PATTERNS.md) | Pattern definitions |
| [red-team.md](../../commands/red-team.md) | Sister command (doc audit) |
| [hc-plan-execute.md](../../commands/hc-plan-execute.md) | Fix what /hc-glass finds |

---

**Version:** V1.2.0
**Updated:** 2025-12-30
**Status:** Production-ready
