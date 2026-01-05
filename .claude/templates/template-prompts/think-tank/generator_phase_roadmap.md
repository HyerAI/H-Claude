# Phase Roadmap Generator

Generates `phase_roadmap.yaml` for a specific phase based on NORTHSTAR vision and codebase reality.

---

## Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SESSION_PATH` | Think-tank session directory | `.claude/PM/think-tank/auth_20260103/` |
| `PHASE_ID` | Phase identifier from ROADMAP.yaml | `PHASE-002` |
| `ROADMAP_PATH` | Path to ROADMAP.yaml | `.claude/PM/SSoT/ROADMAP.yaml` |

---

## Agent Instructions

You are generating a Phase Roadmap that bridges high-level Roadmap phases to concrete Task Plans.

### Step 1: Read Source Documents

```
Read: .claude/PM/SSoT/NORTHSTAR.md
Read: {{ROADMAP_PATH}}
Read: .claude/templates/think-tank/PHASE_ROADMAP_SCHEMA.md
```

Extract:
- **From NORTHSTAR:** Goals, features, success metrics relevant to {{PHASE_ID}}
- **From ROADMAP:** Phase title, description, dependencies, unlock conditions

### Step 2: Perform Bedrock Analysis

**CRITICAL:** You MUST explore the actual codebase. Do NOT assume or guess.

```
# Identify affected areas from phase description
Glob: Relevant file patterns (e.g., "src/**/*.ts", "tests/**/*.test.ts")
Grep: Key terms from phase scope
Read: Core files in affected areas
```

Populate `bedrock_analysis` with VERIFIED facts:

1. **existing_patterns:** What architectural patterns exist in affected areas?
   - Search for: class structures, module patterns, API conventions
   - Document: WHERE you found it, HOW it affects the phase

2. **files_affected:**
   - `modify`: Files that exist and need changes (VERIFY they exist)
   - `create`: New files needed (VERIFY parent directories exist)
   - `delete`: Files to remove (rare - document reasoning)

3. **constraints:**
   - Technical debt that limits options
   - Backward compatibility requirements
   - Performance or security requirements

4. **code_dependencies:**
   - Internal modules the phase builds on
   - External packages needed (check existing package.json/requirements.txt)

### Step 3: Generate Phase Roadmap

Using PHASE_ROADMAP_SCHEMA.md, create the phase roadmap:

```yaml
# Phase Roadmap: {{PHASE_ID}}
# Generated: [timestamp]

meta:
  schema_version: '1.0.0'
  created: '[ISO timestamp]'
  last_modified: '[ISO timestamp]'

phase_id: {{PHASE_ID}}
title: '[From ROADMAP.yaml]'
description: |
  [Expand with specific scope boundaries]

status: active

ns_alignment:
  goals: [...]      # Reference NORTHSTAR goal IDs
  features: [...]   # Specific features
  success_metrics: [...]

bedrock_analysis:
  existing_patterns: [...]
  files_affected:
    modify: [...]
    create: [...]
    delete: []
  constraints: [...]
  code_dependencies:
    internal: [...]
    external: [...]

tasks:
  - id: TASK-XXX-01
    title: ''
    description: ''
    estimated_complexity: low | medium | high
    task_plan_path: null
  # ... more tasks

validation_gates:
  automated: [...]
  manual: [...]
  acceptance: [...]

dependencies:
  phases: [...]
  external: [...]
  blockers: []

outputs:
  artifacts: [...]
  documentation: [...]
  downstream_unlocks: [...]
```

---

## Simulation Check

Before finalizing, validate:

### Vision Alignment (NORTHSTAR)
| Check | Question | Pass? |
|-------|----------|-------|
| Goals | Does every task trace to a NORTHSTAR goal? | |
| Features | Are the features within phase scope? | |
| Success | Can we measure completion against NS metrics? | |

### Reality Alignment (Codebase)
| Check | Question | Pass? |
|-------|----------|-------|
| Patterns | Does this respect existing architecture? | |
| Files | Do all `modify` files actually exist? | |
| Constraints | Are all constraints documented with sources? | |
| Dependencies | Are internal/external deps verified? | |

### Coherence
| Check | Question | Pass? |
|-------|----------|-------|
| Tasks | Are tasks atomic (single session)? | |
| Order | Is task order logical given dependencies? | |
| Validation | Are gates achievable and measurable? | |

**If any check FAILS:** Document the issue and either:
- Adjust the phase roadmap to address it
- Escalate to user as a blocker

---

## Output

Write the completed phase roadmap to:

```
{{SESSION_PATH}}/phase_roadmap.yaml
```

---

## Quality Checklist

Before writing output:

- [ ] `phase_id` matches {{PHASE_ID}} exactly
- [ ] `ns_alignment.goals` reference valid NORTHSTAR goal IDs
- [ ] `bedrock_analysis` contains NO assumptions - only verified facts
- [ ] Every `files_affected.modify` path verified to exist
- [ ] Every `files_affected.create` parent directory verified to exist
- [ ] `tasks` are ordered by dependency (early tasks enable later ones)
- [ ] Each task has clear, testable completion criteria
- [ ] `validation_gates` include both automated and manual checks
- [ ] Simulation Check passed (Vision + Reality + Coherence)

---

## Error Handling

| Situation | Action |
|-----------|--------|
| NORTHSTAR not found | STOP - cannot proceed without vision |
| ROADMAP phase doesn't exist | STOP - invalid PHASE_ID |
| Cannot access codebase | Document as constraint, proceed with available info |
| Conflicting constraints | Document both, recommend resolution, ask user |
| Scope ambiguity | Default to narrower scope, document assumption |
