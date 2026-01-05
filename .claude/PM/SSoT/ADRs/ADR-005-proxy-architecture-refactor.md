# ADR-005: Proxy Architecture Refactor

**Date:** 2026-01-04
**Status:** Approved
**Deciders:** HeyDude, Council (Infrastructure Architect, Migration Risk Manager)
**Source:** `.claude/PM/think-tank/proxy_architecture_refactor_20260104/`

---

## Context

Current proxy architecture couples documentation to specific models:
- CG-Flash (2405) → Gemini Flash
- CG-Pro (2406) → Gemini Pro
- CC-Claude (2408) → Claude Opus

Problems:
1. Changing models requires updating 52 port references across 23 files
2. Agent roles (Worker, Reasoner, Coordinator) conflated with model names
3. No flexibility to swap models per role without doc changes

---

## Decision

### Migrate to 6 Role-Based Proxies

| Proxy | Port | Type | Default Model | Agents |
|-------|------|------|---------------|--------|
| HC-Reas-A | 2410 | Claude CLI | Claude Opus | Domain Expert, Writer |
| HC-Reas-B | 2411 | Google AI | Gemini Pro | Critic, Pragmatist, Commander, Synthesizer |
| HC-Work | 2412 | Google AI | Gemini Flash | Worker, git-engineer, Specialist |
| HC-Work-R | 2413 | Google AI | Gemini Flash | Oraca (reasoning workers) |
| HC-Orca | 2414 | Google AI | Gemini Flash | Orchestrator (execute, glass, red-team) |
| HC-Orca-R | 2415 | Google AI | Gemini Pro | Orchestrator (think-tank) |

### Keep CG-Image Separate

CG-Image (2407) remains unchanged - specialized for image generation, outside scope.

### Migration Approach: Sequential (No Parallel Period)

1. Create 6 new proxy folders with ports 2410-2415
2. Update all port references in H-Claude files
3. Test and validate all workflows
4. Remove old proxies (2405, 2406, 2408)
5. External projects updated manually by user

**Rationale:** User has full control of environment. No external dependencies requiring compatibility period.

---

## Consequences

### Positive
- **Decoupled:** Docs reference roles, not models
- **Flexible:** Change model via `.env`, no doc edits
- **Clear:** Agent → Proxy mapping is explicit
- **Scalable:** Add new models without architecture changes

### Negative
- **More proxies:** 6 services vs 3 (manageable)
- **One-time effort:** 52 references to update

### Neutral
- Port range shift: 2405-2408 → 2410-2415

---

## Constraints Honored

| Constraint | How |
|------------|-----|
| No broken workflows | Sequential migration, test before removing old |
| Global proxies | Still in `~/.claude/HC-Proxies/` |
| KISS | Same server code, just different configs |
| DRY | Templates reference proxy names, model in one place |

---

## Implementation

See: `execution-plan.yaml` in same session folder

**Files to Update:**
- `~/.claude/HC-Proxies/` - Create 6 new folders
- `.claude/commands/*.md` - Update port references
- `.claude/agents/*.md` - Update port references
- `.claude/templates/**/*.md` - Update port references
- `.claude/docs/PROXIES.md` - Document new architecture
- `.claude/PM/SSoT/AGENT_ROLES.md` - Update proxy mapping
- `~/.claude/bin/start-proxies.sh` - Start new proxies
- `~/.claude/bin/stop-proxies.sh` - Stop new proxies
