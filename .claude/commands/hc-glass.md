---
version: V2.0.0
description: "G.L.A.S.S. - Global Logic & Architecture System Scan"

config:
  templates: .claude/templates/template-prompts/hc-glass/
  session_path: .claude/PM/hc-glass/

proxies:
  orchestrator: { port: 2414, role: HC_ORCA }
  commander: { port: 2411, role: HC_REAS_B }
  scout: { port: 2412, role: HC_WORK }
  board: { port: 2410, role: HC_REAS_A }

sectors:
  1: { codename: Archaeologists, mission: "ADR vs Reality", targets: ["ADRs/", "src/"] }
  2: { codename: Plumbers, mission: "Data Flow & Logic", targets: ["Context", "Events", "Loops"] }
  3: { codename: Critics, mission: "Test Quality", targets: ["tests/", "spec/"] }
  4: { codename: Janitors, mission: "Rot & Dead Code", targets: ["Entire codebase"] }
  5: { codename: Guards, mission: "Permissions & Safety", targets: ["File I/O", "API handling"] }
  6: { codename: Registrars, mission: "SSoT Alignment", targets: ["agents/", "skills/", "ADRs/", "indexes"] }

depth_modes:
  quick: { flash_per_sector: 1, agents: "6 Flash + 8 Pro + 1 Opus" }
  standard: { flash_per_sector: 2, agents: "12 Flash + 8 Pro + 1 Opus" }
  deep: { flash_per_sector: 3, agents: "18 Flash + 8 Pro + 1 Opus" }

focus_modes:
  all: [1,2,3,4,5,6]
  adr: [1]
  flow: [2]
  tests: [3]
  rot: [4]
  security: [5]
  ssot: [6]

timeouts:
  orchestrator: 5400  # 90 min
  sector: 1200        # 20 min
  scout: 600          # 10 min
  kill_after: 60

circuit_breakers:
  three_strike: "Flash cites 3 non-existent files -> discard output"
  sector_timeout: "Commander >20 min -> mark INCOMPLETE, continue"
  orchestrator_timeout: "Full run >90 min -> SIGTERM, SIGKILL after 60s"
  overflow_cap: ">20 findings per sector -> cap to 10"
  token_ceiling: "Session exceeds limit -> abort, save partial"

output_lists:
  panic: { severity: Critical, desc: "Security holes, data loss, infinite loops" }
  lie: { severity: Major, desc: "Documentation doesn't match reality" }
  kill: { severity: Minor, desc: "Dead code to delete" }
  debt: { severity: Info, desc: "Tech debt to address when able" }

templates:
  - orchestrator.md (Flash)
  - sector_archaeologists.md (Pro)
  - sector_plumbers.md (Pro)
  - sector_critics.md (Pro)
  - sector_janitors.md (Pro)
  - sector_guards.md (Pro)
  - sector_registrars.md (Pro)
  - synthesizer_merge.md (Pro)
  - arbiter_classification.md (Pro)
---

# /hc-glass - G.L.A.S.S.

> **G**lobal **L**ogic & **A**rchitecture **S**ystem **S**can

**Philosophy:** "Trust nothing. Verify everything. Cite line numbers or it didn't happen."

---

## Quick Start

```markdown
/hc-glass

TARGET: ${PWD}
DEPTH: [quick|standard|deep]
FOCUS: [all|adr|flow|tests|rot|security|ssot]

CONCERNS:
- [Optional: specific areas to investigate]
```

Spawns background Flash orchestrator coordinating 6 Pro commanders + Flash scouts + Arbiter. Notifies when Board Report ready.

---

## Architecture

```
HC invokes /hc-glass
     |
Spawn Flash Orchestrator (BACKGROUND)
     |
+-----------------------------------------------------------------------------+
|  PHASE 0: SETUP - Create session folder, validate paths, init Flight Recorder
+-----------------------------------------------------------------------------+
|  PHASE 1: SWARM - 6 Pro Sector Commanders (parallel), each spawns Flash scouts
|           -> SECTOR_X_SYNTHESIS.md per sector
+-----------------------------------------------------------------------------+
|  PHASE 2: MERGE GATE (Pro) - Deduplicate, validate citations
|           -> ANALYSIS/CROSS_SECTOR_SYNTHESIS.md
+-----------------------------------------------------------------------------+
|  PHASE 3: ARBITER (Pro) - Verify classification (Doc Lie vs Code Gap)
|           -> ANALYSIS/VERIFIED_SYNTHESIS.md
+-----------------------------------------------------------------------------+
|  PHASE 4: BOARD REPORT (Opus) - Prioritize by severity, final report
|           -> SYSTEM_REVIEW_GLASS.md
+-----------------------------------------------------------------------------+
```

---

## Session Folder

```
.claude/PM/hc-glass/${session-slug}/
|-- ORCHESTRATOR_LOG.md
|-- PATH_VALIDATION.md
|-- SECTOR_1_ARCHAEOLOGISTS/
|   |-- flash_1_adr_reality.md
|   |-- flash_2_transitions.md
|   |-- flash_3_zombies.md
|   +-- SECTOR_1_SYNTHESIS.md
|-- SECTOR_2_PLUMBERS/
|-- SECTOR_3_CRITICS/
|-- SECTOR_4_JANITORS/
|-- SECTOR_5_GUARDS/
|-- SECTOR_6_REGISTRARS/
|-- ANALYSIS/
|   |-- CROSS_SECTOR_SYNTHESIS.md
|   +-- VERIFIED_SYNTHESIS.md
+-- SYSTEM_REVIEW_GLASS.md
```

---

## Spawn Pattern

```bash
TIMEOUT=${TIMEOUT:-5400}

timeout --foreground --signal=TERM --kill-after=60 $TIMEOUT \
  bash -c 'ANTHROPIC_API_BASE_URL=http://localhost:2414 claude --dangerously-skip-permissions -p "..."'

EXIT_CODE=$?
if [ $EXIT_CODE -eq 124 ]; then
  echo "[CRITICAL] Orchestrator killed after timeout"
  echo "status: TIMEOUT_KILLED" > "${SESSION_PATH}/TIMEOUT_INTERRUPTED.md"
fi
```

---

## Comparison: /hc-glass vs /red-team

| Aspect | /hc-glass | /red-team |
|--------|-----------|-----------|
| Focus | Code quality, bugs, security | Documentation accuracy |
| Output | 4 Lists (Panic/Lie/Kill/Debt) | Kill List, Fix List, Gap Table |
| Arbiter | Phase 3 verifies classification | No classification phase |

---

## The Mantra

```
I trust nothing.
I verify everything.
I cite line numbers or it didn't happen.
I hunt the rot, the lies, and the fragile.
I filter hallucinations before I report.
I verify classifications before I accuse.
I am the brutal truth.
```

---

## Related

- `/red-team` - Sister command (doc audit)
- `/hc-execute` - Fix what /hc-glass finds
- `/think-tank` - Research and planning
