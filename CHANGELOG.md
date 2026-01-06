# Changelog

All notable changes to H-Claude will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.4.1] - 2026-01-05

### Changed
- **hc-scout V2.0.0** - Consolidated state-agent into scout (dual role: research + triage)
- **CLAUDE.md** - Removed $STATE references, scout now handles post-execution triage
- **HC-LOG files** - Updated to reference $SCOUT for triage updates

### Removed
- **state-agent.md** - Consolidated into hc-scout (KISS: one agent, two jobs)

---

## [0.4.0] - 2026-01-05

### Changed
- **Proxy Architecture Refactor** (ADR-005) - Migrated from 3 model-coupled to 6 role-based proxies
  - Old: CG-Flash (2405), CG-Pro (2406), CC-Claude (2408)
  - New: HC-Reas-A (2410), HC-Reas-B (2411), HC-Work (2412), HC-Work-R (2413), HC-Orca (2414), HC-Orca-R (2415)
- **Port references updated** - session-start.sh, hc-scout.md, session-triage.md, git-engineer.md
- **PROXIES.md** - Updated to new architecture

### Added
- **Proxy status dashboard** - Live health indicators on PM Dashboard (index.md)
- **proxy-status.js** - Browser-based proxy health checking
- **CORS headers** - All proxy server.js files now allow wiki status checks

### Removed
- **Old proxy folders** - CG-Flash, CG-Pro, CC-Claude (kept CG-Image for image generation)

---

## [0.3.2] - 2026-01-04

### Changed
- **Orchestrator models optimized** - Reduced Claude Opus usage to preserve limits
  - `/think-tank` → Pro (2406) - needs reasoning for dialectic
  - `/hc-execute` → Flash (2405) - coordination only
  - `/hc-glass` → Flash (2405) - coordination only
  - `/red-team` → Flash (2405) - coordination only
- **AGENT_ROLES.md** - Updated ORCA to context-dependent model (Pro/Flash)
- **Model philosophy** - Reserve Opus for dialectic roles (Domain Expert, Writer)

---

## [0.3.1] - 2026-01-04

### Changed
- **infrastructure/ → HC-Proxies/** - Renamed folder to avoid system naming conflicts
- **hc-init V1.2.0** - Added `--init` flag for project initialization with name prompt
- **Global install path** - Now `~/.claude/HC-Proxies/` instead of `~/.claude/infrastructure/`

### Added
- **hc-init --init** - Prompts for project name, updates CLAUDE.md, offers src/ creation

---

## [0.3.0] - 2026-01-04

### Added
- **Gauntlet Loop** (ADR-002) - Adversarial plan refinement with Writer/Critic roles
- **Gauntlet Templates** - gauntlet_writer.md, gauntlet_critic.md, gauntlet_arbiter.md
- **Micro-Retry Protocol** - Error-feedback retry at Oraca level before escalation
- **AGENT_ROLES.md** - Formal documentation of all agent roles and responsibilities

### Changed
- **think-tank.md** V2.4.0 - Added Gauntlet Loop to Step 7, --no-gauntlet flag
- **hc-execute.md** V2.8.0 - Added Micro-Retry Protocol documentation
- **oraca_phase.md** - Added retry logic with PREVIOUS_ERROR, ATTEMPT_NUMBER, RETRY_GUIDANCE

---

## [0.2.0] - 2026-01-03

### Added
- **Diffusion Development Philosophy** - Progressive "denoising" from vision to reality
- **Document Schemas** - PHASE_ROADMAP_SCHEMA.md, TASK_PLAN_SCHEMA.md, TICKET_SCHEMA.md
- **Generator Templates** - generator_phase_roadmap.md, generator_task_plan.md, generator_tickets.md
- **Validation Templates** - validator_simulation.md, validator_physics.md, validator_resolution.md
- **ADR-001** - Diffusion Development Framework decision

### Changed
- **think-tank.md** V2.3.0 - Added Diffusion Philosophy section, Progressive Resolution steps
- **hc-execute.md** V2.7.0 - Added Lookahead Loop, Triangulated Context for Workers

---

## [0.1.0] - 2026-01-02

### Added
- Initial H-Claude structure
- `/think-tank` - Multi-agent planning councils with fact-based research
- `/hc-execute` - Parallel execution with Oraca orchestrators and QA gates
- `/hc-glass` - Code review audits
- `/red-team` - Deep investigation audits
- Global installer (`curl` one-liner)
- Per-project initialization (`/hc-init`)
- Checkpoint/rollback for safe execution
- Example files (NORTHSTAR, ROADMAP, execution-plan)
- Proxy infrastructure (Flash, Pro, Opus)

---

<!--
Entry template:

## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature

### Changed
- Updated behavior

### Fixed
- Bug fix

### Removed
- Deleted feature
-->
