# ADR-003: Think-Tank Workflow Improvements

## Status
ACCEPTED

## Date
2026-01-04

## Context

The think-tank workflow was examined through a self-review session where the council analyzed its own process. Key findings from scout research:

1. **Workflow Complexity:** 10+ steps with ~15 agent spawns per session
2. **Unused Features:** Escalation protocol had 0 uses across all sessions
3. **Lost Knowledge:** 03_SESSIONS/ directories consistently empty - no transcripts preserved
4. **Validation Overlap:** Triple validation at Step 7 (generator → Gauntlet → Diffusion) with unclear integration
5. **No Observability:** No cost tracking, no incident log for post-mortems

Council reached consensus on core issues but user (HD) provided key override:

> "If you missed the design of this whole system I do not trust even myself. I want my work, your work, and any work to be looked by a few to catch errors. These validators stay on for now."

This established the principle: **friction is the feature, not the bug.** Validation layers are mandatory.

## Decision

### 1. Delete Escalation Protocol
- **Rationale:** 0 uses = 0 value (YAGNI)
- **Action:** Removed from think-tank.md and STATE.yaml schema

### 2. Reduce Scouts from 4 to 3
- **Rationale:** 4 scouts showed diminishing returns; 3 scouts with focused domains provide sufficient coverage
- **New Focus Areas:**
  - Scout 1: Commands, agents & orchestration patterns
  - Scout 2: Templates, prompts & prompt engineering
  - Scout 3: State management, PM workflows & session artifacts

### 3. Mandatory Transcript Capture
- **Rationale:** Empty 03_SESSIONS/ folders = lost institutional knowledge
- **Action:** Made transcript capture mandatory (not optional) in Step 4
- **Format:** Markdown with agent name, timestamp, full response

### 4. Add Observability
- **Rationale:** Cannot optimize what you don't measure
- **Added to STATE.yaml:**
  ```yaml
  cost_tracking:
    agent_spawns: 0
    estimated_tokens: 0
    session_duration_min: 0
  incident_log: []
  ```

### 5. Clarify Validation Integration
- **Rationale:** Gauntlet and Diffusion validators both operate at Step 7 with unclear relationship
- **Clarification:**
  - Gauntlet catches: execution failures, resource gaps, dependency breaks
  - Diffusion catches: scope creep, orphan tasks, architecture drift
  - Both are complementary, not redundant
  - Execution order: Draft → Gauntlet → Diffusion → Approved

### 6. NO New Bypasses
- **User Override:** All validation layers remain mandatory
- **Rationale:** "Trust but Verify" - friction is intentional
- **Result:** No `--no-diffusion` flag added

## Consequences

### Positive
- Cleaner codebase (dead escalation code removed)
- Better cost awareness (observability added)
- Preserved institutional knowledge (transcripts mandatory)
- Clearer validation flow (integration documented)

### Negative
- Validation still adds latency (accepted tradeoff)
- 3 scouts may occasionally miss edge cases (acceptable risk)

### Risks
- Developers may still skip steps informally (mitigated by making defaults strict)
- Cost tracking is manual estimate (future: add actual API cost tracking)

## Related
- ADR-001: Diffusion Development Philosophy
- ADR-002: Gauntlet Loop Integration
- Think-tank session: think_tank_self_review_20260104

## Version
V2.5.0
