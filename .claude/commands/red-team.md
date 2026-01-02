---
version: V2.2.0
status: current
timestamp: 2025-12-30
tags: [command, validation, quality-assurance, audit]
description: "Quality Seals Audit - Multi-layer deep-dive audit with configurable sectors"
---

# /red-team - Quality Seals Audit

**Philosophy:** Trust but Verify. Assume 15% of documentation doesn't match reality.

**Purpose:** Execute a multi-layer audit of any codebase, comparing SSoT documentation against actual implementation to find gaps, contradictions, and zombie artifacts.

---

## Quick Start

```markdown
/red-team

AUDIT_SCOPE: [full|core|custom]
SECTORS: [1,2,3,4,5,6]           # Only if custom scope
OUTPUT_NAME: [AUDIT_REPORT.md]   # Optional, defaults to AUDIT_REPORT.md

FOCUS:
- [Optional: specific concerns to investigate]
```

This command spawns a background Opus orchestrator that runs the full audit workflow. You'll be notified when complete.

---

## Architecture Overview

```
HD invokes /red-team
     ↓
Spawn OPUS Orchestrator (BACKGROUND)
     ↓
┌────────────────────────────────────────────────────────────────────────┐
│  PHASE 0: SETUP & PATH VALIDATION                                      │
│  Opus validates sector paths exist, creates session folder             │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 1: SECTOR EXECUTION (Pro Commanders, batched)                   │
│  Each Commander spawns Flash specialists → SECTOR_REPORTS/             │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 2: SECTOR SYNTHESIS (Pro agent)                                 │
│  Pro curates sector reports → ANALYSIS/SECTOR_SYNTHESIS.md             │
│  WHY: Preserves Opus context, identifies cross-sector patterns         │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 3: FINAL AUDIT                                                  │
│  Opus writes AUDIT_REPORT.md with Kill List, Fix List, Gap Table       │
├────────────────────────────────────────────────────────────────────────┤
│  OUTPUT: .claude/PM/red-team/${session-slug}/AUDIT_REPORT.md              │
│  HD notified when complete                                             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Session Folder Structure

All artifacts live in one self-contained folder:

```
.claude/PM/red-team/${session-slug}/
├── ORCHESTRATOR_LOG.md          # Flight Recorder: Append-only event history
├── PATH_VALIDATION.md           # Phase 0: Which paths exist/missing
├── SECTOR_REPORTS/              # Phase 1: Commander reports
│   ├── SECTOR_01_HIERARCHY.md
│   ├── SECTOR_02_WORKFLOW.md
│   └── ...
├── ANALYSIS/
│   └── SECTOR_SYNTHESIS.md      # Phase 2: Cross-sector patterns
└── ${OUTPUT_NAME}               # Final deliverable
```

**WHY this structure:**
- **Self-contained:** One folder = one audit session
- **Traceable:** Path validation → Sector reports → Synthesis → Final
- **Debuggable:** ORCHESTRATOR_LOG.md shows agent spawns and completions
- **Archivable:** Move whole folder when done

---

## Session Identity

```yaml
AUDIT_SCOPE: "${AUDIT_SCOPE}"      # full|core|custom
SESSION_SLUG: "YYYY-MM-DD_HHmmss-audit"
SESSION_PATH: ".claude/PM/red-team/${SESSION_SLUG}/"

# Example:
# AUDIT_SCOPE: "core"
# SESSION_SLUG: "2025-12-30_143022-core-audit"
# SESSION_PATH: ".claude/PM/red-team/2025-12-30_143022-core-audit/"
```

---

## Scope Selection

| Scope | Sectors | Use Case |
|-------|---------|----------|
| **full** | All 6 sectors | Comprehensive audit |
| **core** | Sectors 1-3 | Quick health check |
| **custom** | User-specified | Targeted investigation |

---

## Proxy Configuration

```bash
# Sector Commanders (Pro) - investigation coordination
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions

# Specialists (Flash) - document/code review
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions

# Orchestrator (Opus) - coordination, runs in background
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions
```

---

## Orchestrator Execution

When this command is invoked, spawn a background Opus orchestrator:

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "
$(cat <<'ORCHESTRATOR_PROMPT'

# Quality Seals Audit Orchestrator

You are the orchestrator for a multi-layer audit. Your adversarial prior: 15% of documentation doesn't match reality. Your job is to find the gaps.

## Session Parameters
- AUDIT_SCOPE: ${AUDIT_SCOPE:-full}
- SECTORS: ${SECTORS:-all}
- OUTPUT_NAME: ${OUTPUT_NAME:-AUDIT_REPORT.md}
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
    log_event "[COMPLETE] Sector X complete."
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

**Pro Commanders Spawning Flash Specialists:** Each Pro Commander must also spawn Flash specialists SYNCHRONOUSLY and wait for their completion before writing the sector report.

## IMPORTANT: Execute All Phases Sequentially

You MUST complete ALL phases in order. Do not stop after Phase 0.
After each phase, immediately proceed to the next.

## Session Setup

1. Generate SESSION_SLUG (e.g., 2025-12-30_143022-audit)
2. Create session folder:
   \`\`\`bash
   mkdir -p .claude/PM/red-team/\${SESSION_SLUG}/{SECTOR_REPORTS,ANALYSIS}
   \`\`\`
3. Initialize ORCHESTRATOR_LOG.md (Flight Recorder)
4. Log: \`[INIT] Audit initialized. Scope: \${AUDIT_SCOPE}.\`

## Flight Recorder: ORCHESTRATOR_LOG.md

Append-only event log. Format: \`[TIMESTAMP] [EVENT_TYPE] Message\`

Event Types:
- \`[INIT]\` - Session start
- \`[VALIDATE]\` - Path validation result
- \`[SECTOR]\` - Sector started/completed
- \`[SPAWN]\` - Commander/Specialist dispatched
- \`[COMPLETE]\` - Agent returned
- \`[SKIP]\` - Sector skipped (paths missing)
- \`[WARN]\` - Concerns or issues
- \`[SYNTHESIS]\` - Synthesis phase
- \`[DONE]\` - Audit complete

## Phase 0: Setup & Path Validation

Before running sectors, validate that target paths exist:

1. For each sector, check if its doc/code paths exist
2. **If paths are missing, list EXACTLY which paths were sought vs what was found**
3. Write to: \${SESSION_PATH}/PATH_VALIDATION.md with structured table:
   \`\`\`markdown
   | Sector | Expected Path | Status | Notes |
   |--------|---------------|--------|-------|
   | 1 | docs/adr/ (or .claude/SSoT/ADRs/) | FOUND | 47 files |
   | 1 | src/ | FOUND | exists |
   | 2 | .claude/agents/ | MISSING | not found |
   | 2 | .claude/skills/ | FOUND | 12 files |
   \`\`\`
4. Log: \`[VALIDATE] Sector X: Y/Z paths exist\`
5. If a sector has 0 valid paths, mark it SKIP and log: \`[SKIP] Sector X: No valid paths\`

**WHY this format:** "Validation failed" is useless for debugging. The table shows exactly what was expected vs reality - typo in path? Directory renamed? File deleted?

## Phase 1: Sector Execution

For each active sector (max 2 Commanders in parallel), spawn Pro Commander SYNCHRONOUSLY:

\`\`\`bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "
# Sector Commander

You are leading the investigation for one sector of the Quality Seals Audit.

## Your Sector
- SECTOR_ID: \${SECTOR_ID}
- SECTOR_NAME: \${SECTOR_NAME}
- SESSION_PATH: \${SESSION_PATH}

## Target Paths
Documentation: \${TARGET_DOCS}
Code: \${TARGET_CODE}

## Crucial Questions
\${CRUCIAL_QUESTIONS}

## Your Team - Spawn These Flash Specialists SYNCHRONOUSLY

### 1. Librarian (Required)
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p \"
Read all files in [doc paths]. Check for:
- Broken internal links
- Outdated references to deleted files
- Contradictions between documents
- Missing cross-references
Report findings as a list with file:line citations.\"

### 2. Engineer (Required)
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p \"
Compare [doc paths] against [code paths]. Check for:
- Features documented but not implemented
- Features implemented but not documented
- API signatures that don't match
- Configuration options that differ
Report each gap with doc:line vs code:line citations.\"

### 3. Auditor (Optional - spawn if scope warrants)
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p \"
Scan [paths] for:
- Files referenced in docs but don't exist
- Files that exist but aren't referenced anywhere
- Dead code paths
- Orphan configurations
Create a Kill List of files that should be deleted.\"

## Execution
1. Spawn specialists in parallel
2. Wait for all to complete
3. Synthesize their findings
4. Write sector report

## Output
Write to: \${SESSION_PATH}/SECTOR_REPORTS/SECTOR_\${SECTOR_ID}_\${SECTOR_NAME}.md

Format:
- Executive Summary (2-3 sentences)
- Health Assessment (PASS/WARN/FAIL)
- Findings table with file:line citations
- Recommendations

## Health Scoring
- PASS: 0-2 minor issues, no gaps
- WARN: 3-5 issues OR 1 significant gap
- FAIL: >5 issues OR critical gap
"
\`\`\`

## Phase 2: Sector Synthesis

After all sectors complete, spawn Pro synthesizer SYNCHRONOUSLY:

\`\`\`bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "
# Sector Synthesis Agent

Analyze all sector reports to identify cross-cutting patterns and prioritize findings.

## Session Parameters
- SESSION_PATH: \${SESSION_PATH}
- SECTORS_RUN: \${SECTORS_RUN}

## Your Inputs
Read all sector reports: \${SESSION_PATH}/SECTOR_REPORTS/SECTOR_*.md

## Your Analysis

1. **Pattern Detection**
   - What issues appear in multiple sectors?
   - Are there systemic problems (not just isolated issues)?
   - What root causes explain multiple symptoms?

2. **Priority Assessment**
   - Critical: blocking functionality
   - Important: affect quality
   - Minor: cosmetic or low-impact

3. **Kill List Consolidation**
   - Merge zombie lists from all sectors
   - Remove duplicates
   - Verify no false positives (file used by sector not yet analyzed)

4. **Fix List Consolidation**
   - Merge all implementation gaps
   - Identify dependencies (fix A before B)
   - Estimate effort (quick/medium/major)

## Output
Write to: \${SESSION_PATH}/ANALYSIS/SECTOR_SYNTHESIS.md

Include:
- Sector Health Overview table
- Systemic Patterns Detected
- Consolidated Kill List
- Consolidated Fix List (Critical/Important/Minor)
- Health Score (0-100%)
"
\`\`\`

## Phase 3: Final Audit

1. Read synthesis and all sector reports
2. Generate final audit with:
   - Executive Summary (0-100% health)
   - Kill List (files to delete)
   - Fix List (missing implementations)
   - Gap Table (sector status grid)
3. Write to: \${SESSION_PATH}/\${OUTPUT_NAME}

## Error Handling

### Commander Times Out
1. Log: \`[WARN] Sector X Commander timeout\`
2. Mark sector as INCOMPLETE
3. Continue with other sectors
4. Include in final report

### Path Validation Fails for All Sectors
1. Log: \`[CRITICAL] No valid paths found for any sector\`
2. Write minimal report explaining issue
3. Exit with recommendation to update sector definitions

ORCHESTRATOR_PROMPT
)"
```

---

## The 6 Audit Sectors

Sectors are updated to match current codebase structure.

### SECTOR 1: SSoT Integrity (Documentation vs Reality)

**Target Paths:**
- Docs: `docs/adr/` (or `.claude/SSoT/ADRs/`)
- Code: `src/`, `lib/`

**Crucial Questions:**
- Do ADR decisions match actual implementation?
- Are there features described in ADRs that don't exist in code?
- Are there code features not documented in ADRs?

### SECTOR 2: Agent Architecture (Constitution Compliance)

**Target Paths:**
- Docs: Agent constitution ADR (if exists)
- Code: `.claude/agents/`, `.claude/skills/`

**Crucial Questions:**
- Do agents follow defined hierarchies (if documented)?
- Are role boundaries enforced?
- Do agent definitions match their implementations?

### SECTOR 3: API/Tool Contracts (Interface Check)

**Target Paths:**
- Docs: `README.md`, `docs/api/`
- Code: `src/`, API implementation files

**Crucial Questions:**
- Do API/tool signatures match documentation?
- Are there functions defined but not implemented?
- Are there implemented functions not documented?

### SECTOR 4: Workflow Mechanics (State Machine)

**Target Paths:**
- Docs: Workflow/state machine ADRs (if exist)
- Code: State machine or workflow implementation files

**Crucial Questions:**
- Is the state machine implemented as documented?
- Are state transitions validated?
- Are there dead states or unreachable transitions?

### SECTOR 5: Skills & Commands (Interface Check)

**Target Paths:**
- Docs: `.claude/commands/`, `.claude/skills/`
- Code: Corresponding implementation files

**Crucial Questions:**
- Are there zombie skills (defined but not used)?
- Are there ghost commands (referenced but not defined)?
- Do skill prompts match actual behavior?

### SECTOR 6: Template Fitness (Artifact Check)

**Target Paths:**
- Docs: `.claude/templates/`
- Code: Commands/skills that use them

**Crucial Questions:**
- Are templates actually used by commands?
- Are there orphan templates?
- Do template outputs match expected formats?

---

## Sector Commander Prompt Structure

Each Commander receives:

```yaml
sector_id: [1-6]
sector_name: [Name]
target_docs: [list of doc paths]
target_code: [list of code paths]
crucial_questions: [list]
session_path: ${SESSION_PATH}
```

Commander spawns 2-3 Flash Specialists:
- **Librarian:** Cross-reference docs vs docs (broken links, outdated refs)
- **Engineer:** Compare docs vs code (implementation gaps)
- **Optional Auditor:** Check for zombie/ghost artifacts

Commander synthesizes specialist findings into Sector Report.

---

## Output Artifacts

| Artifact | Location | Creator |
|----------|----------|---------|
| ORCHESTRATOR_LOG.md | `${SESSION_PATH}/` | Opus (append-only) |
| PATH_VALIDATION.md | `${SESSION_PATH}/` | Opus (Phase 0) |
| SECTOR_XX_*.md | `${SESSION_PATH}/SECTOR_REPORTS/` | Pro Commanders (Phase 1) |
| SECTOR_SYNTHESIS.md | `${SESSION_PATH}/ANALYSIS/` | Pro (Phase 2) |
| ${OUTPUT_NAME} | `${SESSION_PATH}/` | Opus (Phase 3) |

---

## Audit Report Format

```markdown
---
audit_slug: ${AUDIT_SLUG}
scope: ${AUDIT_SCOPE}
sectors_run: [N]
timestamp: [ISO-8601]
health_score: [0-100]%
---

## Executive Summary

[2-3 sentences: Overall system health assessment]

## Health Score: [X]%

| Sector | Status | Issues Found |
|--------|--------|--------------|
| 1. SSoT Integrity | [PASS/WARN/FAIL] | [count] |
| 2. Agent Architecture | [PASS/WARN/FAIL] | [count] |
| ... | ... | ... |

## Kill List (Files to Delete)

| File | Reason | Sector |
|------|--------|--------|
| [path] | [zombie/ghost/outdated] | [X] |

## Fix List (Missing Implementations)

| What's Missing | Where Documented | Priority |
|----------------|------------------|----------|
| [feature] | [ADR/doc path] | [HIGH/MED/LOW] |

## Gap Table

| Gap ID | Description | Doc Reference | Code Reference |
|--------|-------------|---------------|----------------|
| GAP-01 | [what's misaligned] | [doc:line] | [code:line] |

## Detailed Sector Reports

[Links to individual sector reports in SECTOR_REPORTS/]

## Recommendations

1. [Priority action]
2. [Secondary action]
```

---

## Templates

Templates live in: `.claude/templates/red-team/`

| Template | Purpose |
|----------|---------|
| `sector-commander-prompt.md` | Pro commander instructions |
| `specialist-prompts.md` | Flash specialist role definitions |
| `synthesis-prompt.md` | Pro cross-sector synthesis |

---

## The Audit Mantra

```
I validate paths before I spawn.
I compare docs to reality.
I hunt for zombies and ghosts.
I synthesize before I conclude.
Trust but Verify.
```

---

## Related

| Related | When to Use Instead |
|---------|---------------------|
| `/hc-plan` | Planning new features |
| `/hc-plan-execute` | Implementing approved plans |
| Direct code review | Single file investigation |

---

**Version:** V2.2.0
**Updated:** 2025-12-30
**Status:** Production-ready (stall detection removed, templates inlined)
