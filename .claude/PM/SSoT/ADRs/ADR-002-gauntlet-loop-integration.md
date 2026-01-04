# ADR-002: Adopt Gauntlet Loop for Planning & Execution

**Status:** Accepted
**Date:** 2026-01-04
**Decision Makers:** HD, Claude Council
**Source:** `.claude/PM/think-tank/ralph_loop_integration_20260104/`

## Context

H-Claude's current workflow uses linear validation (Generator → Validator → PASS/FAIL). This misses opportunities for iterative refinement where Writers defend decisions and Critics stress-test plans before execution.

The "Ralph Loop" pattern (autonomous iteration until completion) was evaluated, but full implementation adds complexity. A bounded "Gauntlet" approach provides adversarial refinement without infinite loops.

## Decision

Adopt the **Gauntlet Loop** pattern with **Principled Friction** - bounded adversarial iteration where both Writer and Critic have failure conditions.

### Core Principles

1. **The Gauntlet (3-5 Turn Loop)**
   - Draft (Flash): Rapid v1 generation
   - Loop: Critic reviews → Writer responds (ACCEPTED/REJECTED) → repeat
   - Exit: Critic APPROVED, contested pass with evidence, or max iterations

2. **Principled Friction**
   - Writer Failure: Accepting bad advice degrades the plan
   - Critic Failure: Nitpicking without substance wastes cycles
   - Both agents accountable, neither rubber-stamps

3. **Evidence-Based Responses**
   - ACCEPTED: Valid critique, integrating fix
   - REJECTED: Cite specific evidence why critique is wrong
   - NORTHSTAR/ADR citations required for contested positions

4. **Micro-Level Retry (hc-execute)**
   - Worker fails → Oraca feeds error + context → Worker retries (max 3)
   - Only escalate to Orchestrator after local retry exhausted

### Agent Roles

| Role | Model | Responsibility |
|------|-------|----------------|
| Writer (Principled Architect) | Claude 4.5 (2408) | Own the plan, defend NORTHSTAR |
| Critic (High-Stakes Auditor) | Gemini 3 Pro (2406) | Simulate execution, find breaks |
| Draft Generator | Gemini 3 Flash (2405) | Rapid v1 creation |

### Integration Points

1. **think-tank STEP 7**: The Gauntlet replaces linear plan generation
2. **hc-execute Oraca**: Micro-retry before escalation
3. **Diffusion Gates (Steps 6-8)**: Optional Gauntlet for complex phases

## Consequences

### Positive
- Plans stress-tested before execution
- Fewer NOT_FEASIBLE specs and failed tasks
- Both agents accountable (no rubber-stamp, no nitpicking)
- Bounded complexity (3-5 turns, not infinite)

### Negative
- Added latency in planning phase (~2-5 min per Gauntlet)
- New templates to maintain (gauntlet_writer, gauntlet_critic)
- Requires model coordination (Claude + Gemini)

### Neutral
- Cost increase ~$0.20-0.40 per planning artifact
- Can disable with `--no-gauntlet` flag if needed

## Implementation

See: `execution-plan.yaml` in think-tank workspace

## References

- Ralph Loop Research: `.claude/PM/think-tank/ralph_loop_integration_20260104/`
- ADR-001: Diffusion Development Framework
- Decision Map: `04_DECISION_MAP.md`
