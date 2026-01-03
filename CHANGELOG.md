# Changelog

All notable changes to the H-Claude template will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/).

---

## [Unreleased]

### Added
- **WORKFLOW_GUIDE.md** - Complete workflow documentation (NORTHSTAR → ROADMAP → phases → execution)
- **Resource Safety: Background Task Cleanup** - Critical section in CLAUDE.md preventing zombie processes
- **ROADMAP.yaml** - New SSoT document for development phases at `.claude/PM/SSoT/ROADMAP.yaml`
- **Pre-Execution Checkpoint Protocol** - git-engineer can now create rollback points before major executions
- **Rollback Protocol** - git-engineer can restore to checkpoints if execution fails
- **Dynamic Phase Management** - `--add-phase`, `--remove-phase` flags for evolving roadmaps
- **Phase 0: CHECKPOINT** in hc-execute.md - Mandatory checkpoint before execution
- **Phase 6: ROADMAP SYNC** in hc-execute.md - Auto-update ROADMAP.yaml on completion
- **EXECUTION_STATE.md schema** - Formal schema for crash recovery and status tracking
- **NORTHSTAR validation** - think-tank --roadmap validates NORTHSTAR before creating roadmap
- **Phase existence validation** - think-tank --phase validates phase exists before planning
- **Edge Cases section** - Parallel phases, failure recovery, crash recovery, hotfix handling
- **Side-quest promotion protocol** - Clear paths to promote research to phases
- **Scope Change Protocol** - Documented process for handling requirement changes

### Changed
- **GET_STARTED.md** (V2.0.0) - Rewritten as installation-only guide, workflow moved to WORKFLOW_GUIDE.md
- **think-tank.md** (V2.1.0) - Added Dynamic Phase Management section, updated flags table
- **CLAUDE.md** - Added Claude's Role: Product Owner, updated workflow hierarchy
- **NORTHSTAR.md** - Added Core Workflow section with NORTHSTAR/ROADMAP hierarchy
- **session-triage.md** (V2.0.0) - Now reads ROADMAP.yaml, shows phase progress, validates dependencies
- **context.yaml** - Added roadmap reference, removed active_phases duplication
- **git-engineer.md** (V1.2.0) - Added checkpoint/rollback operations
- **hc-execute.md** - Added Phases 0 and 6, EXECUTION_STATE.md schema, edge cases
- **ROADMAP.yaml** - Added `archived_phases[]` and `changelog[]` for phase history
- **STATE_SCHEMA.md** - lifecycle.type now: roadmap | phase | side_quest | legacy

### Fixed
- Command name consistency: All refs now use `/hc-execute` (not /execute-plan)
- Removed active_phases duplication between context.yaml and ROADMAP.yaml

### Removed
- `.claude/commands/session-triage.md` - Redundant; agent file is sufficient

---

## [1.0.0] - 2026-01-02

### Added
- Initial H-Claude template structure
- Session Start Protocol with triage agent
- Think-tank council-based decision support
- Execute-plan with SWEEP & VERIFY workflow
- Multi-agent proxy infrastructure (Flash/Pro/Opus)
