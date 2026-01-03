# Decision Map: Agentic Framework Migration

## Core Tension

**Exploration vs Determinism** — Current think-tank model encourages creative exploration. Diffusion model demands triangulated context and progressive denoising toward deterministic outcomes.

## Constraints Identified

1. Must work with existing proxy infrastructure (Flash/Pro/Opus)
2. H-Claude is a min repo - surgical changes only
3. Backwards compatibility where possible
4. Practical with current LLM capabilities

## Blind Spots Surfaced

- Current system lacks explicit "bedrock" (codebase reality) input to planning
- No lookahead validation during execution loop
- Tickets don't include triangulated context

## Paths Considered

### Path A: Bolted-On Validation
- Add NS alignment checks without restructuring
- **Rejected:** Addresses symptoms, not philosophy

### Path B: Add Resolution Layers
- Add Phase Roadmap + Task Plan documents
- **Rejected:** Gets structure, misses dual-track loop

### Path C: Full Diffusion Implementation ✓
- Implement complete Diffusion Development Philosophy
- Triangulated Context in every template
- Lookahead Loop in execution
- Progressive Resolution gates

## Decision

**Path C: Full Diffusion Implementation**

Implement the Diffusion Development Philosophy with:
1. New document templates (phase_roadmap, task_plan, ticket with triangulated context)
2. Lookahead validation in execution loop
3. Progressive resolution gates at each level
4. Preserve existing infrastructure (proxies, spawning patterns)

## Confidence

**HIGH** - Philosophy is well-documented, implementation path is clear, existing infrastructure supports it.
