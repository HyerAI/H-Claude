# ADR-001: Adopt Diffusion Development Philosophy

**Status:** Accepted
**Date:** 2026-01-03
**Decision Makers:** HD, Claude Council
**Source:** `.claude/PM/think-tank/agentic_framework_20260103/`

## Context

H-Claude's current workflow (think-tank → hc-execute) uses a creative exploration model where agents freely explore options before converging on a decision. This works well for decision-making but can lead to:
- Scope creep ("standard industry features" added without request)
- Plans disconnected from codebase reality
- Execution drift from original vision

## Decision

Adopt the **Diffusion Development Philosophy** which treats development as progressive "denoising" from vision to reality.

### Core Principles

1. **Triangulated Context** — Every agent action constrained by:
   - Past (Bedrock): The existing codebase
   - Present (Plan): The specific instruction
   - Future (Vision): The NORTHSTAR goal

2. **Progressive Resolution** — Five-level document hierarchy:
   - NORTHSTAR.md (Vision/Future)
   - ROADMAP.yaml (Sketch/Strategy)
   - phase_roadmap.yaml (Structure/anchored in codebase)
   - task_plan.yaml (Blueprint/deliverables)
   - Sub-Task Tickets (Instructions/triangulated context)

3. **Lookahead Loop** — Dual-track execution:
   - Track A: Reality (WR builds, QA tests)
   - Track B: Horizon (VA validates against NS)

4. **Validation Gates** — At each resolution level:
   - Step 6: Simulation Check (Phase Roadmap)
   - Step 7: Scope & Physics Check (Task Plan)
   - Step 8: Resolution Check (Tickets)

## Consequences

### Positive
- Anti-bloat: Every feature traces to NS
- Determinism: Agents solve differentials, not create from scratch
- Grounded: Plans anchored in codebase reality
- Recoverable: Clear rollback points at each resolution level

### Negative
- More documents to maintain
- Longer planning phase before execution
- Migration required for existing workflows

### Neutral
- Agent naming can stay current (Orchestrator, Scouts, etc.) or adopt new (PO, ORCA, RCH, etc.)
- Proxy infrastructure unchanged

## Implementation

See: `execution-plan.yaml` in think-tank workspace

## References

- Diffusion Development Philosophy: `.claude/PM/think-tank/agentic_framework_20260103/02_KNOWLEDGE_BASE/Diffusion Development Philosophy.md`
- Scout Research: `facts_merged.yaml` (102 facts, no conflicts)
