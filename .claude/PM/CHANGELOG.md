# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- execution-plan.yaml schema for think-tank plan generation
- Plan status tracking in context.yaml (draft → review → approved → in_progress → complete)
- STEP 7: Plan Generation in think-tank command
- TOPIC parameter for hc-plan-execute to auto-locate plans

### Changed
- think-tank now outputs execution-plan.yaml after DECIDE
- hc-plan-execute reads from think-tank subject folders
- NORTHSTAR workflow diagram updated (removed hc-plan step)
- GET_STARTED.md updated with new workflow

### Deprecated
- /hc-plan command (merged into /think-tank)
- .claude/PM/plans/ folder (plans now in think-tank/{topic}/)

### Fixed

### Removed

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
