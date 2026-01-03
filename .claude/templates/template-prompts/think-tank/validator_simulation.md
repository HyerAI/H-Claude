# Validator: Simulation Check (Step 6 Gate)

## Variables

- `SESSION_PATH`: Path to think-tank session (e.g., `.claude/PM/think-tank/project_20260103/`)
- `PHASE_ROADMAP_PATH`: Path to phase roadmap being validated (default: `{{SESSION_PATH}}/phase_roadmap.yaml`)
- `NS_PATH`: Path to NORTHSTAR (default: `.claude/PM/SSoT/NORTHSTAR.md`)
- `ROADMAP_PATH`: Path to ROADMAP.yaml (default: `.claude/PM/SSoT/ROADMAP.yaml`)

## Purpose

**Diffusion VA[1] Gate**: Validates that the Phase Roadmap maintains alignment between Vision (NORTHSTAR) and Reality (codebase constraints).

The Simulation Check answers: "If we execute this plan, will we move toward our goals without breaking what exists?"

---

## Validation Protocol

### 1. Vision Alignment (NORTHSTAR → Tasks)

For each task in the Phase Roadmap, verify:

```
□ Task traces to specific NORTHSTAR goal/feature
□ Task contributes measurable progress toward that goal
□ No task exists that contradicts NORTHSTAR priorities
```

**Check**: Read `{{NS_PATH}}` and cross-reference with `phase_roadmap.yaml`
- Every task MUST have a traceable `ns_alignment` (NORTHSTAR reference in roadmap)
- Tasks should align with `ns_alignment.goals` and `ns_alignment.features` in the phase roadmap
- Orphan tasks (no NS link) = FAIL

**Optional Enhancement**: If `{{SESSION_PATH}}/research/northstar_analysis.md` exists, use it for deeper validation.

### 2. Reality Alignment (Bedrock → Constraints)

For each constraint/dependency in the Phase Roadmap, verify:

```
□ bedrock_analysis accurately reflects current codebase state
□ Dependencies reference actual files/systems that exist
□ Constraints are real, not assumed
```

**Check**: Validate the `bedrock_analysis` section within `{{PHASE_ROADMAP_PATH}}`
- Claimed files in `files_affected.modify` MUST exist in codebase
- Claimed files in `files_affected.create` MUST have existing parent directories
- Stated constraints MUST be verifiable
- Phantom dependencies (don't exist) = FAIL

**Optional Enhancement**: If `{{SESSION_PATH}}/research/bedrock_analysis.md` exists, cross-reference for completeness.

### 3. Scope Alignment (Phase Boundaries)

Verify the phase scope is appropriate:

```
□ Phase contains 3-7 coherent tasks (not 1, not 20)
□ All tasks are achievable before next phase dependency
□ No task belongs in a different phase
□ Phase has clear completion criteria
```

**Check**: Review phase structure
- Scope creep (unrelated tasks bundled) = FAIL
- Scope fragmentation (too granular) = FAIL

---

## Anti-Patterns to Catch

| Anti-Pattern | Detection | Severity |
|--------------|-----------|----------|
| **Orphan Task** | Task has no `ns_ref` or traces to deleted NS item | FAIL |
| **Phantom Dependency** | References file/system that doesn't exist | FAIL |
| **Stale Bedrock** | Bedrock analysis contradicts actual codebase | FAIL |
| **Scope Creep** | Tasks unrelated to phase theme bundled in | FAIL |
| **Wishful Constraint** | Assumes capability that doesn't exist | FAIL |
| **Missing Validation** | No success criteria for task | WARN |
| **Circular Dependency** | Task A needs B, B needs A | FAIL |

---

## Output Format

### On PASS

```yaml
validation:
  result: PASS
  confidence: [0.7-1.0]  # How confident in alignment
  phase_id: PHASE-XXX
  validated_at: 'YYYY-MM-DDTHH:MM:SSZ'

alignment_scores:
  vision: [0.0-1.0]   # NORTHSTAR alignment
  reality: [0.0-1.0]  # Bedrock accuracy
  scope: [0.0-1.0]    # Scope appropriateness

notes:
  - 'Optional observations about the plan'

approved_for: execution  # Ready for /hc-execute
```

### On FAIL

```yaml
validation:
  result: FAIL
  phase_id: PHASE-XXX
  validated_at: 'YYYY-MM-DDTHH:MM:SSZ'

failures:
  - type: orphan_task | phantom_dependency | stale_bedrock | scope_creep | ...
    location: 'Where in the roadmap'
    issue: 'What is wrong'
    fix: 'How to fix it'

  - type: ...
    location: ...
    issue: ...
    fix: ...

blocked_until: 'failures resolved'
```

---

## Validation Procedure

```
1. LOAD Phase Roadmap from {{PHASE_ROADMAP_PATH}}
2. LOAD NORTHSTAR from {{NS_PATH}}
3. LOAD ROADMAP from {{ROADMAP_PATH}}
4. (OPTIONAL) If {{SESSION_PATH}}/research/ exists, load any analysis files for enrichment

5. FOR each task in Phase Roadmap:
   - VERIFY ns_alignment references valid NORTHSTAR goals/features
   - VERIFY bedrock_analysis.files_affected.modify paths exist in codebase
   - VERIFY bedrock_analysis.files_affected.create have existing parent directories
   - FLAG any anti-patterns

6. ASSESS overall scope coherence

7. CALCULATE alignment scores

8. IF any FAIL-severity issues:
   - OUTPUT FAIL with failure list
   ELSE:
   - OUTPUT PASS with confidence score
```

---

## Confidence Scoring

| Score | Meaning |
|-------|---------|
| 0.9-1.0 | Excellent alignment, execute with confidence |
| 0.8-0.89 | Good alignment, minor concerns noted |
| 0.7-0.79 | Acceptable, proceed with caution |
| <0.7 | Do not pass - issues must be addressed |

---

## Post-Validation

**On PASS**: Phase Roadmap is approved for execution via `/hc-execute`

**On FAIL**: Return to Generator with specific fixes required. Do not proceed to execution.
