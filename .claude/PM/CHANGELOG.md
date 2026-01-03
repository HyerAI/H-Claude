# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

## [2.1.0] - 2026-01-02 - Global Installer & Enhanced Research

### Added
- install.sh - One-command global installer (`curl ... | bash`)
- /hc-init skill - Initialize H-Claude workflow in any project
- Global infrastructure: proxies install to ~/.claude/infrastructure/
- Enhanced KB research: 4 Flash scouts with DIVERSITY/CONSENSUS modes
- Up to 3 research rounds per think-tank council round
- Agent research signal: `RESEARCH_REQUEST:` with mode selection

### Changed
- README.md - New global install flow with curl command
- GET_STARTED.md - Dual installation methods (global vs clone)
- think-tank.md STEP 3 - Enhanced context gathering with 4 scouts

---

## [2.0.0] - 2026-01-02 - GitHub Release Ready

### Added
- README.md - Repository entry point with quick start
- LICENSE - MIT license (HyerAI)
- setup.sh - One-command installation (npm install + env setup)
- start-proxies.sh - Start all proxies in background with health checks
- stop-proxies.sh - Clean proxy shutdown
- .claude/examples/ - Filled-out example files:
  - NORTHSTAR-example.md - Customer Support Chatbot example
  - ROADMAP-example.yaml - 3-phase project roadmap example
  - execution-plan-example.yaml - 10-task phase plan example
- WORKFLOW_GUIDE.md - Complete workflow documentation
- Resource safety: Background task cleanup documentation in CLAUDE.md
- Session triage resource cleanup in session-triage.md

### Changed
- CLAUDE.md - Reset to clean template with [PROJECT_NAME] placeholder
- context.yaml - Reset to clean template state
- NORTHSTAR.md - Cleaned workflow diagram syntax
- GET_STARTED.md - Updated to reference setup.sh and start-proxies.sh scripts
- .gitignore - Added /tmp/h-claude/ and .claude/plans/

### Fixed
- CLAUDE.md T+16 merge: Changed `block: false` to `block: true` to prevent zombie processes
- WORKFLOW_GUIDE.md: Fixed `/think-tank --roadmap "Project Name"` to `/think-tank --roadmap`

---

## [1.1.0] - 2026-01-02

### Added
- execution-plan.yaml schema for think-tank plan generation
- Plan status tracking in context.yaml (draft → review → approved → in_progress → complete)
- STEP 7: Plan Generation in think-tank command
- STEP 6.5: ADR Creation in think-tank command - decisions now recorded as ADRs
- TOPIC parameter for hc-plan-execute to auto-locate plans

### Changed
- think-tank now outputs execution-plan.yaml after DECIDE
- think-tank now invokes `/adr-writer` skill after DECIDE (STEP 6.5)
- adr-writer skill updated with think-tank integration docs
- hc-plan-execute reads from think-tank subject folders
- NORTHSTAR workflow diagram updated (removed hc-plan step)
- GET_STARTED.md updated with new workflow

### Deprecated
- /hc-plan command (merged into /think-tank)
- .claude/PM/plans/ folder (plans now in think-tank/{topic}/)

---

## [1.0.0] - 2026-01-02

### Added
- Initial H-Claude template release
- 5 orchestration commands: /think-tank, /hc-plan, /hc-plan-execute, /hc-glass, /red-team
- Skills: ADR writer, agent manager, command designer, commit gate, flowchart designer
- Git protocols and reference guide
- Multi-agent proxy infrastructure (CC-Claude, CG-Pro, CG-Flash, CG-Image)
- Template context files with placeholder structure

---
