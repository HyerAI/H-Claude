# Changelog

All notable changes to H-Claude will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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

## [0.7.2] - 2026-01-04

### Changed
- **docs/ → .claude/docs/** - Moved workflow docs inside .claude/ for consistency
- **hc-init V1.1.0** - Now checks global `~/.claude/infrastructure/` instead of project-local
- **CLAUDE.md** - Added Folder Architecture section documenting project vs global structure
- **install.sh** - Added PM-View caching, mkdocs check, `pm-view-serve.sh` helper script

### Fixed
- **PM-View symlink** - Updated to point to new .claude/docs location
- **mkdocs.yml** - Fixed site_dir path, added README.md to exclude list

---

## [0.7.1] - 2026-01-04

### Added
- **docs/PROXIES.md** - Comprehensive proxy architecture documentation

### Changed
- **CC-Claude default** - Changed from sonnet to opus for best quality
- **Proxy table** - Updated to show Gemini 3 family defaults, Nano Banana for CG-Image

### Fixed
- **CG-Pro .env.example** - Corrected default model documentation (gemini-3-pro)

---

## [0.7.0] - 2026-01-04

### Added
- **HC-LOG folder** - USER-PREFERENCES.md, HC-FAILURES.md for institutional memory
- **SESSION_STATUS.md** - Live document updated by triage (replaces ephemeral output)
- **hc-scout agent** - Research delegation to preserve HC context
- **HC Discipline section** - Routing rules (3+ files → commands) in CLAUDE.md
- **HC Support Team section** - git-engineer, session-triage, hc-scout

### Changed
- **Renamed HD → HC** throughout commands, ADRs, AGENT_ROLES.md
- **session-triage.md** - Now writes SESSION_STATUS.md, reads HC-FAILURES.md
- **CLAUDE.md** - Added session start protocol, HC-LOG reading, hc-scout spawn

---

## [0.6.5] - 2026-01-04

### Added
- **G.L.A.S.S. audit session** - glass_20260104_1534/ with 58% health score, 59 findings
- **BACKLOG.yaml** - 24 items prioritized P1-P4 from audit findings

### Changed
- **context.yaml** - Added hc_glass session tracking, updated recent_actions

### Security
- **Identified** - 3 exposed API keys, command injection risk, model param validation gaps

## [0.6.4] - 2026-01-04

### Fixed
- **BUG-001: Zombie background tasks** - Added timeout wrappers to prevent indefinite orchestrator runs

### Added
- **Timeout Configuration** section in hc-glass.md, hc-execute.md, red-team.md, think-tank.md
- **Timeout wrapper** in orchestrator templates (hc-glass, hc-execute, red-team)
- **Pattern 8 enhancement** - Added Timeout Wrapper as fourth guard in ORCHESTRATION_PATTERNS.md

### Changed
- **Sub-agent spawn pattern** - Now requires `timeout --foreground` wrapper with exit code 124 handling
- Commands: hc-glass V1.4.0, hc-execute V2.10.0, red-team V2.4.0, think-tank V2.6.0
- ORCHESTRATION_PATTERNS.md V1.3.0

## [0.6.3] - 2026-01-04

### Changed
- **20% Rule** - Updated adversarial prior from 15% to 20% across all commands and templates
- **Command labels** - hc-glass is "Audit", red-team is "QA/Review" (was swapped)

### Fixed
- **red-team wiki** - Sectors 5 & 6 were fabricated; now match source (Skills & Commands, Template Fitness)
- **hc-execute wiki** - Added missing Phase 0 (Checkpoint) and Phase 6 (ROADMAP Sync)
- **hc-glass wiki** - Corrected sector focuses (ADR vs Reality, Test quality, etc.)
- **think-tank wiki** - Split Council Roles and Gauntlet Loop Roles into separate tables

### Added
- **Red-team audit session** - pm_view_audit_20260104_1439/ with full PM-View validation

## [0.6.2] - 2026-01-04

### Added
- **YAML view pages** - roadmap-view.md, backlog-view.md, context-view.md for dashboard links
- **pymdownx.snippets** - Auto-include yaml files in markdown pages

### Changed
- **Unified PM Dashboard** - Merged "H-Claude PM Observatory" and "Dashboard" into single index.md
- **Layout** - Commands, Status/Quick Access side-by-side, Active Sessions, Workflow diagram

### Fixed
- **Dashboard 404 errors** - Quick links now point to .md wrapper pages instead of raw yaml

### Removed
- **dashboard.md** - Content merged into index.md

## [0.6.1] - 2026-01-04

### Added
- **PM-View Enhancements** - Command flowcharts, gold styling, refresh button
- **Command index pages** - think-tank, hc-execute, hc-glass, red-team with mermaid diagrams
- **Navigation control** - .pages files for awesome-pages auto-discovery
- **Command template** - `PM-View/templates/command-index.md` for consistency
- **Custom CSS** - Gold H1/H2 titles, active nav underline, brand colors

### Changed
- **mkdocs.yml** - Removed navigation.expand, added navigation.indexes
- **Tab names** - "Execution" (was SWEEP & VERIFY), "G.L.A.S.S." (was Reviews)

## [0.6.0] - 2026-01-04

### Added
- **PM-View Wiki** - MkDocs Material local documentation server for observability
- **Deletion Verification Gate** - 3 Flash agents with unanimous consensus required
- **Quarantine-only deletion** - Agents move to DELETION_FOLDER, user deletes manually
- **Concurrency control** - MAX_CONCURRENT_AGENTS=8 for hc-glass orchestrator
- **deletion_verifier.md** - 7-check verification template
- **deletion_consensus.md** - Unanimous vote aggregation template

### Changed
- **orchestrator.md** - Added Phase 1.5 (Deletion Gate), concurrency management
- **synthesizer_merge.md** - Added Quarantine List and Hold List outputs
- **BACKLOG.yaml** - Added --parallel flag and cost tracking items

### Removed
- **Deprecated templates** - hc-plan/, hc-execute/, red-team/ legacy folders
- **Deprecated scouts** - scout_codebase.md, scout_docs.md, scout_web.md
- **Empty folders** - PM/brainstorm/, PM/execute-plan/

## [0.5.0] - 2026-01-04

### Added
- **SWEEP Observability** (ADR-004) - STDOUT markers and mandatory SWEEP_REPORT.md
- **Artifact Trail Enforcement** - Folder structure created before execution
- **Triangulated Context** - Workers receive GOAL and BEDROCK_FILES
- **RETRY_FAILED Test Procedure** - Documented validation steps
- **ADR-004** - hc-execute Self-Review Improvements

### Changed
- **hc-execute.md** V2.9.0:
  - Added RETRY_FAILED test procedure section
  - Referenced ADR-004
- **orchestrator.md** - Creates full folder structure at Phase 1, passes context
- **oraca_phase.md** - Writes ORACA_LOG.md, passes triangulated context to workers
- **worker_task.md** - Added Triangulated Context section (GOAL, BEDROCK_FILES)
- **qa_phase.md** - Added SUCCESS_CRITERIA variable
- **sweeper.md** - Added start/end markers, mandatory report creation

## [0.4.0] - 2026-01-04

### Added
- **Observability** (ADR-003) - cost_tracking and incident_log in STATE.yaml schema
- **ADR-003** - Think-Tank Workflow Improvements decision record

### Changed
- **think-tank.md** V2.5.0:
  - Reduced scouts from 4 to 3 (focused domains, diminishing returns fix)
  - Made transcript capture mandatory in Step 4
  - Added Validation Integration section clarifying Gauntlet + Diffusion relationship
  - Added cost_tracking and incident_log to STATE.yaml schema

### Removed
- **Escalation Protocol** - 0 uses across all sessions (YAGNI)

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
- **worker_task.md** - Added retry context section
- **generator_execution_plan.md** - Added CRITIQUE_INPUT for Gauntlet Writer mode
- **CLAUDE.md** - Added Agent Roles quick reference table

## [0.2.0] - 2026-01-03

### Added
- **Diffusion Development Philosophy** - Progressive "denoising" from vision to reality
- **Document Schemas** - PHASE_ROADMAP_SCHEMA.md, TASK_PLAN_SCHEMA.md, TICKET_SCHEMA.md
- **Generator Templates** - generator_phase_roadmap.md, generator_task_plan.md, generator_tickets.md
- **Validation Templates** - validator_simulation.md, validator_physics.md, validator_resolution.md, validator_lookahead.md
- **ADR-001** - Diffusion Development Framework decision

### Changed
- **think-tank.md** V2.3.0 - Added Diffusion Philosophy section, Progressive Resolution steps (6-8)
- **hc-execute.md** V2.7.0 - Added Lookahead Loop, Triangulated Context for Workers

## [0.1.0] - 2026-01-02

### Added
- Initial H-Claude min repo structure
- /think-tank command with fact-based research (V2.2.0)
- /hc-execute command with Oraca orchestrators (V2.6.0)
- /hc-glass code review command
- /red-team audit command
- Proxy infrastructure (Flash, Pro, Opus)
