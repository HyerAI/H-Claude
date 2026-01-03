# Think-Tank Briefing: Agentic Framework Migration

## Problem Statement

How should we update our H-Claude multi-agent system to implement the new Agentic Framework architecture?

## Current Lean

The current system (think-tank → hc-execute) may need restructuring to match the proposed 5-phase workflow with specialized agents (PO, ORCA, RCH, ARC, WR, QA, VA) and the clearer document hierarchy (NS → RM → Phase Roadmap → Task Plan → Sub-Task Tickets).

## Constraints

1. Must work with existing proxy infrastructure (Flash/Pro/Opus)
2. Keep surgical changes - H-Claude is a min repo
3. Maintain backwards compatibility where possible
4. Must be practical to implement with current LLM capabilities

## Context

### Current System
```
/think-tank (council) → ADR → SPEC → execution-plan.yaml → /hc-execute
```

### Proposed Framework
```
PO[1] defines NS → RCH[1] validates → ARC[1] creates RM → ORCA[1] drills down → WR[x]/QA[x]/VA[x] execute loop
```

### Key Differences

| Aspect | Current | Proposed |
|--------|---------|----------|
| Agent Roles | Flexible council (Domain Expert, Pragmatist) | Explicit roles (PO, ORCA, RCH, ARC, WR, QA, VA) |
| Document Hierarchy | NS → RM → execution-plan.yaml | NS → RM → Phase Roadmap → Task Plan → Sub-Task Tickets |
| Focus | Exploration & decision mapping | Anti-bloat, strict NS alignment |
| Execution | Batch execution via hc-execute | Sequential loop with validation gates |

### Proposed 5-Phase Workflow

1. **Discovery & Definition** - PO + User create Northstar
2. **Targeted Research & Validation** - RCH researches, VA validates
3. **Architecture & Roadmap** - ARC creates master roadmap
4. **Granular Planning** - ORCA drills down (Phase → Task → Sub-Task)
5. **Execution Loop** - WR executes, QA tests, VA validates, ORCA orchestrates

## Success Criteria

- Clear mapping from current to proposed architecture
- Identified what stays, what changes, what's new
- Practical implementation path
- Minimal disruption to existing workflows
