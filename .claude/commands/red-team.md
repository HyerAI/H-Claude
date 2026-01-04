---
version: V2.4.0
status: current
timestamp: 2026-01-02
tags: [command, validation, quality-assurance, audit]
description: "Quality Seals Audit - Multi-layer deep-dive audit with configurable sectors"
templates: .claude/templates/template-prompts/red-team/
---

# /red-team - Quality Seals Audit

**Philosophy:** Trust but Verify. Assume 20% of work and documentation doesn't match reality.

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
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 3: FINAL AUDIT                                                  │
│  Opus writes AUDIT_REPORT.md with Kill List, Fix List, Gap Table       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Session Folder Structure

```
.claude/PM/red-team/${session-slug}/
├── ORCHESTRATOR_LOG.md          # Flight Recorder
├── PATH_VALIDATION.md           # Phase 0: Which paths exist/missing
├── SECTOR_REPORTS/              # Phase 1: Commander reports
│   ├── SECTOR_01_HIERARCHY.md
│   ├── SECTOR_02_WORKFLOW.md
│   └── ...
├── ANALYSIS/
│   └── SECTOR_SYNTHESIS.md      # Phase 2: Cross-sector patterns
└── ${OUTPUT_NAME}               # Final deliverable
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
# Specialists (Flash)
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions

# Sector Commanders, Synthesizer (Pro)
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions

# Orchestrator (Opus)
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions
```

---

## Timeout Configuration

Background orchestrators MUST use timeout wrapper to prevent zombie processes.

```bash
# Default: 60 minutes for audit workflow
TIMEOUT=${TIMEOUT:-3600}

# Spawn pattern with timeout
timeout --foreground --signal=TERM --kill-after=60 $TIMEOUT \
  bash -c 'ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "..."'

# Check exit code
EXIT_CODE=$?
if [ $EXIT_CODE -eq 124 ]; then
  echo "[CRITICAL] Orchestrator killed after timeout ($TIMEOUT seconds)"
  echo "status: TIMEOUT_KILLED" > "${SESSION_PATH}/TIMEOUT_INTERRUPTED.md"
fi
```

**Timeout Values:**
| Context | Default | Override |
|---------|---------|----------|
| Full orchestrator | 60 min | `--timeout=N` |
| Sector Commander | 20 min | (inside orchestrator) |
| Flash Specialist | 10 min | (inside orchestrator) |

---

## Orchestrator Protocol

Spawn background Opus orchestrator using template `orchestrator.md` with timeout wrapper:

| Variable | Value |
|----------|-------|
| AUDIT_SCOPE | full, core, or custom |
| SECTORS | List of sector numbers |
| OUTPUT_NAME | Report filename |
| WORKSPACE | $(pwd) |

---

## The 6 Audit Sectors

### SECTOR 1: SSoT Integrity (Documentation vs Reality)

**Target Paths:**
- Docs: `docs/adr/` or `.claude/SSoT/ADRs/`
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
- Do agents follow defined hierarchies?
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
- Docs: Workflow/state machine ADRs
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
| ... | ... | ... |

## Kill List (Files to Delete)
| File | Reason | Sector |
|------|--------|--------|

## Fix List (Missing Implementations)
| What's Missing | Where Documented | Priority |
|----------------|------------------|----------|

## Gap Table
| Gap ID | Description | Doc Reference | Code Reference |
|--------|-------------|---------------|----------------|
```

---

## Template Reference

All prompts in: `.claude/templates/template-prompts/red-team/`

| Template | Model | Purpose |
|----------|-------|---------|
| `orchestrator.md` | Opus | Main coordination |
| `sector_commander.md` | Pro | Sector investigation lead |
| `specialist_librarian.md` | Flash | Doc cross-reference check |
| `specialist_engineer.md` | Flash | Doc vs code comparison |
| `specialist_auditor.md` | Flash | Zombie/ghost detection |
| `synthesizer_sector.md` | Pro | Cross-sector synthesis |

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
| `/think-tank` | Research, decisions, planning |
| `/hc-execute` | Implementing approved plans |
| Direct code review | Single file investigation |

---

**Version:** V2.4.0 | Added timeout wrapper for zombie prevention (BUG-001)
