---
version: V1.3.0
status: current
timestamp: 2026-01-02
tags: [command, audit, red-team, multi-agent, system-review]
description: "G.L.A.S.S. - Global Logic & Architecture System Scan with 6 sector Pro commanders, Flash swarm, and Classification Arbiter"
templates: .claude/templates/template-prompts/hc-glass/
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
FOCUS: [all|adr|flow|tests|rot|security|ssot]

CONCERNS:
- [Optional: specific areas to investigate]
```

This command spawns a background Opus orchestrator that coordinates 6 sector Pro commanders (each with Flash scouts), a Merge Gate synthesizer, and a Classification Arbiter. You'll be notified when the Board Report is ready.

---

## Architecture Overview

```
HD invokes /hc-glass
     |
Spawn OPUS Orchestrator (BACKGROUND)
     |
+-----------------------------------------------------------------------------+
|  PHASE 0: SETUP & VALIDATION                                                |
|  - Create session folder, validate paths, init Flight Recorder              |
+-----------------------------------------------------------------------------+
|  PHASE 1: THE SWARM (6 Pro Sector Commanders, parallel)                     |
|  Each Commander spawns Flash scouts (sequential) → SECTOR_X_SYNTHESIS.md    |
+-----------------------------------------------------------------------------+
|  PHASE 2: MERGE GATE (Pro Synthesizer)                                      |
|  - Deduplicates, validates citations, identifies patterns                   |
|  - Outputs: ANALYSIS/CROSS_SECTOR_SYNTHESIS.md                              |
+-----------------------------------------------------------------------------+
|  PHASE 3: CLASSIFICATION ARBITER (Pro)                                      |
|  - Verifies classification (Doc Lie vs Code Gap)                            |
|  - Outputs: ANALYSIS/VERIFIED_SYNTHESIS.md                                  |
+-----------------------------------------------------------------------------+
|  PHASE 4: THE BOARD REPORT (Opus)                                           |
|  - Prioritizes by severity, writes final report                             |
|  - Outputs: SYSTEM_REVIEW_GLASS.md                                          |
+-----------------------------------------------------------------------------+
```

---

## Session Folder Structure

```
.claude/PM/hc-glass/${session-slug}/
|-- ORCHESTRATOR_LOG.md              # Flight Recorder
|-- PATH_VALIDATION.md               # Phase 0: Path checks
|
|-- SECTOR_1_ARCHAEOLOGISTS/
|   |-- flash_1_adr_reality.md
|   |-- flash_2_transitions.md
|   |-- flash_3_zombies.md
|   +-- SECTOR_1_SYNTHESIS.md
|
|-- SECTOR_2_PLUMBERS/
|-- SECTOR_3_CRITICS/
|-- SECTOR_4_JANITORS/
|-- SECTOR_5_GUARDS/
|-- SECTOR_6_REGISTRARS/
|
|-- ANALYSIS/
|   |-- CROSS_SECTOR_SYNTHESIS.md    # Phase 2
|   +-- VERIFIED_SYNTHESIS.md        # Phase 3
|
+-- SYSTEM_REVIEW_GLASS.md           # Final Board Report
```

---

## Proxy Configuration

```bash
# Orchestrator (Opus)
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions

# Sector Commanders, Synthesizer, Arbiter (Pro)
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions

# Scouts (Flash)
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions
```

---

## Orchestrator Protocol

Spawn background Opus orchestrator using template `orchestrator.md`:

| Variable | Value |
|----------|-------|
| TARGET | Target codebase path |
| DEPTH | quick, standard, or deep |
| FOCUS | all, adr, flow, tests, rot, security, ssot |
| WORKSPACE | $(pwd) |

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

Each sector commander spawns 1-3 Flash scouts (based on DEPTH) to execute specific search missions.

---

## Depth Modes

| Depth | Flash per Sector | Total Agents | Use Case |
|-------|------------------|--------------|----------|
| `quick` | 1 | 6 Flash + 8 Pro + 1 Opus | Quick health check |
| `standard` | 2 | 12 Flash + 8 Pro + 1 Opus | Regular audit |
| `deep` | 3 | 18 Flash + 8 Pro + 1 Opus | Comprehensive review |

*Pro count: 6 Sector Commanders + 1 Synthesizer + 1 Arbiter = 8*

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

## Output: The 4 Lists

| List | Severity | Description |
|------|----------|-------------|
| **Panic List** | Critical | Security holes, data loss, infinite loops |
| **Lie List** | Major | Documentation that doesn't match reality |
| **Kill List** | Minor | Dead code to delete |
| **Debt List** | Info | Tech debt to address when able |

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
|--------|-----------|-----------|
| Focus | Code quality, bugs, security | Documentation accuracy |
| Sectors | 6 (code-focused) | 6 (doc-focused) |
| Output | The 4 Lists (Panic/Lie/Kill/Debt) | Kill List, Fix List, Gap Table |
| Classification | Phase 3 Arbiter verifies | No classification verification |
| Use Case | Pre-release code audit | Documentation governance |

---

## Template Reference

All prompts in: `.claude/templates/template-prompts/hc-glass/`

| Template | Model | Purpose |
|----------|-------|---------|
| `orchestrator.md` | Opus | Main coordination |
| `sector_archaeologists.md` | Pro | ADR vs Reality |
| `sector_plumbers.md` | Pro | Data Flow & Logic |
| `sector_critics.md` | Pro | Test Quality |
| `sector_janitors.md` | Pro | Rot & Dead Code |
| `sector_guards.md` | Pro | Permissions & Safety |
| `sector_registrars.md` | Pro | SSoT Alignment |
| `synthesizer_merge.md` | Pro | Cross-sector merge |
| `arbiter_classification.md` | Pro | Classification verification |

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
```

---

## Related

| Document | Purpose |
|----------|---------|
| `/red-team` | Sister command (doc audit) |
| `/hc-plan-execute` | Fix what /hc-glass finds |
| `/think-tank` | Research and planning |

---

**Version:** V1.3.0 | Extracted prompts to templates (~65% token reduction)
