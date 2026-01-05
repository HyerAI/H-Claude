# HC System Prompt Design

## Problem Statement

HC (H-Claude, formerly HD) needs a redesigned system prompt that enforces proper workflow management. Currently, HC sometimes executes "small tasks" inline instead of routing through the established command infrastructure (think-tank, hc-execute, hc-glass, red-team). This creates gaps in our development trail.

## Current Pain Points

1. **No enforcement of SSoT/NORTHSTAR/ROADMAP** - Sessions can start without validated project state
2. **Inline task execution** - HC does work directly instead of using commands → no artifacts
3. **State drift** - context.yaml and ROADMAP.yaml not consistently updated
4. **No failure tracking** - Command failures and workflow issues lost to history
5. **No preference learning** - User preferences discovered but not recorded
6. **Git discipline gaps** - Commits not happening as work progresses

## Success Criteria

1. HC ALWAYS routes substantive work through commands
2. Session start validates project state (SSoT, NORTHSTAR, ROADMAP)
3. State files updated consistently
4. Failures and preferences tracked for learning
5. Git-agent manages commits in background
6. Triage agent surfaces learnings from HC-LOG

## Constraints

- Output must be CLAUDE.md sections (both global and project-level)
- Must work with existing command infrastructure
- Cannot break current functionality
- Rename HD → HC throughout

## Context

- HC is the Product Owner and Orchestrator role
- Commands spawn background orchestrators (except think-tank which is blocking by design)
- Triage agent runs at session start for alignment
- Git-agent exists but needs tighter integration

## Deliverables

1. Updated CLAUDE.md with HC workflow rules
2. HC-LOG/ folder structure definition
3. Triage agent enhancement spec
4. Rename strategy (HD → HC)
