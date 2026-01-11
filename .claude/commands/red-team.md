---
version: V3.1.0
status: current
timestamp: 2026-01-10
tags: [command, validation, quality-assurance, audit, adversarial]
description: "Quality Seals Audit - Multi-layer deep-dive audit with configurable sectors"
templates: .claude/templates/template-prompts/red-team/

# Scope options
scopes:
  full: { sectors: [1,2,3,4,5,6], desc: "Comprehensive audit" }
  core: { sectors: [1,2,3], desc: "Quick health check" }
  custom: { sectors: [], desc: "User-specified" }

# Proxy configuration
proxies:
  specialists: { port: 2412, model: "Flash" }
  commanders: { port: 2411, model: "Pro" }
  orchestrator: { port: 2414, model: "Flash" }

# Timeouts (seconds)
timeouts: { orchestrator: 3600, sector_commander: 1200, specialist: 600, kill_after: 60 }

# Session folder
session_root: ".claude/PM/red-team/${session-slug}/"

# Templates
templates_list:
  - { file: orchestrator.md, model: Flash, role: "Main coordination" }
  - { file: sector_commander.md, model: Pro, role: "Sector investigation" }
  - { file: specialist_librarian.md, model: Flash, role: "Doc cross-ref" }
  - { file: specialist_engineer.md, model: Flash, role: "Doc vs code" }
  - { file: specialist_auditor.md, model: Flash, role: "Zombie detection" }
  - { file: synthesizer_sector.md, model: Pro, role: "Cross-sector synthesis" }
---

# /red-team - Quality Seals Audit

**Philosophy:** Trust but Verify. Assume 20% of work and documentation doesn't match reality.

---

## Quick Start

```markdown
/red-team

AUDIT_SCOPE: [full|core|custom]
SECTORS: [1,2,3,4,5,6]           # Only if custom scope
OUTPUT_NAME: [AUDIT_REPORT.md]   # Optional

FOCUS:
- [Optional: specific concerns to investigate]
```

---

## Architecture

```
HC invokes /red-team
     │
     v
Spawn Flash Orchestrator (BACKGROUND)
     │
     v
┌────────────────────────────────────────────────────────────────────────┐
│  PHASE 0: SETUP & PATH VALIDATION                                      │
│  Flash validates sector paths exist, creates session folder            │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 1: SECTOR EXECUTION (Pro Commanders, batched)                   │
│  Each Commander spawns Flash specialists -> SECTOR_REPORTS/            │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 2: SECTOR SYNTHESIS (Pro agent)                                 │
│  Pro curates sector reports -> ANALYSIS/SECTOR_SYNTHESIS.md            │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 3: FINAL AUDIT                                                  │
│  Opus writes AUDIT_REPORT.md with Kill List, Fix List, Gap Table       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Session Folder

```
${session_root}
├── ORCHESTRATOR_LOG.md          # Flight Recorder
├── PATH_VALIDATION.md           # Phase 0 output
├── SECTOR_REPORTS/              # Phase 1 output
│   └── SECTOR_0X_*.md
├── ANALYSIS/
│   └── SECTOR_SYNTHESIS.md      # Phase 2 output
├── AUDIT_FIXES.yaml             # Machine-parseable fixes (NEW)
└── ${OUTPUT_NAME}               # Final deliverable (human-readable)
```

---

## The 6 Audit Sectors

| # | Sector | Focus | Target Paths |
|---|--------|-------|--------------|
| 1 | SSoT Integrity | Doc vs Reality | `docs/adr/`, `.claude/SSoT/ADRs/` ↔ `src/`, `lib/` |
| 2 | Agent Architecture | Constitution Compliance | Agent ADRs ↔ `.claude/agents/`, `.claude/skills/` |
| 3 | API/Tool Contracts | Interface Check | `README.md`, `docs/api/` ↔ `src/` |
| 4 | Workflow Mechanics | State Machine | Workflow ADRs ↔ State machine code |
| 5 | Skills & Commands | Interface Check | `.claude/commands/`, `.claude/skills/` ↔ Implementations |
| 6 | Template Fitness | Artifact Check | `.claude/templates/` ↔ Commands using them |

**Sector Questions (all sectors ask):**
- Does documentation match implementation?
- Are there zombies (defined but unused)?
- Are there ghosts (referenced but undefined)?

---

## Issue Classifications

| Class | Meaning | Action |
|-------|---------|--------|
| **KILL** | Zombie artifacts, orphan files, dead code | Delete file |
| **FIX** | Documented but not implemented, broken refs | Implement |
| **NOTE** | Doc/code mismatches, outdated references | Update |

---

## Timeout Wrapper

```bash
TIMEOUT=${TIMEOUT:-3600}
timeout --foreground --signal=TERM --kill-after=60 $TIMEOUT \
  bash -c 'ANTHROPIC_API_BASE_URL=http://localhost:2414 claude --dangerously-skip-permissions -p "..."'
```

---

## Output Formats

### AUDIT_FIXES.yaml (Machine-Parseable)

For automated fix processing by orchestrator and FLASH workers:

```yaml
meta:
  audit_slug: ${AUDIT_SLUG}
  timestamp: ${ISO-8601}
  health_score: 85

fixes:
  - id: FIX-001
    type: KILL              # KILL | FIX | NOTE
    priority: high          # high | medium | low
    sector: 4
    target: src/deprecated/old_handler.ts
    action: delete_file
    reason: "Orphan file - no imports found"
    confidence: high        # high | medium | low
    estimated_effort: 5     # minutes

  - id: FIX-002
    type: FIX
    priority: high
    sector: 3
    target: src/api/auth.ts
    action: implement_function
    function: validateToken
    spec_ref: "docs/api/auth.md#token-validation"
    reason: "Documented but not implemented"
    confidence: medium
    estimated_effort: 30

  - id: FIX-003
    type: NOTE
    priority: low
    sector: 1
    target: docs/architecture.md
    action: update_doc
    reason: "Mentions deprecated v1 API"
    confidence: high
    estimated_effort: 10

summary:
  total: 3
  by_type: { KILL: 1, FIX: 1, NOTE: 1 }
  by_priority: { high: 2, medium: 0, low: 1 }
  total_effort_minutes: 45
```

**Usage by orchestrator:**
```bash
# Parse fixes and spawn workers
yq '.fixes[] | select(.type == "KILL" or .type == "FIX")' AUDIT_FIXES.yaml | while read fix; do
  spawn_flash_worker "$fix"
done
```

### AUDIT_REPORT.md (Human-Readable)

```markdown
---
audit_slug: ${AUDIT_SLUG}
scope: ${AUDIT_SCOPE}
sectors_run: [N]
timestamp: [ISO-8601]
health_score: [0-100]%
---

## Executive Summary
[2-3 sentences]

## Health Score: [X]%
| Sector | Status | Issues |
|--------|--------|--------|
| 1-6... | PASS/WARN/FAIL | count |

## Kill List
| File | Reason | Sector |

## Fix List
| Missing | Where Documented | Priority |

## Gap Table
| Gap ID | Description | Doc Ref | Code Ref |
```

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

| Command | When to Use Instead |
|---------|---------------------|
| `/think-tank` | Research, decisions, planning |
| `/hc-execute` | Implementing approved plans |
| `/hc-glass` | Quick code review (less deep) |

---

**V3.1.0** | Added AUDIT_FIXES.yaml machine-parseable output for automated fix processing.
