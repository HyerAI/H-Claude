---
name: adr-writer
description: ADR creation, versioning, and cross-reference management
category: documentation
used_by: [think-tank, architecture-roles]
invoked_by: /think-tank (STEP 6.5 - mandatory after DECIDE)
---

# ADR Writer Skill

## Purpose

Maintain Architecture Decision Records with proper versioning and cross-reference tracking. **Version existing ADRs instead of creating new ones for changes.**

---

## Think-Tank Integration

This skill is **automatically invoked** by `/think-tank` at STEP 6.5 after a decision is made.

**Input from think-tank:**
- `${SESSION_PATH}/00_BRIEFING.md` - Problem context
- `${SESSION_PATH}/04_DECISION_MAP.md` - Decision details
- `${SESSION_PATH}/STATE.yaml` - Decision metadata

**Output:**
- ADR file in `.claude/PM/SSoT/ADRs/[CSXX]-[slug].md`
- Updated cross-references in related ADRs
- ADR reference added to STATE.yaml

**Flow:**
```
think-tank DECIDE → STEP 6.5 → adr-writer → ADR created → STEP 7 PLAN
```

---

## Core Principle: Version, Don't Proliferate

```
WRONG: Create ADR-0099 to update ADR-0073
RIGHT: Bump ADR-1101 from V1.0.0 to V1.1.0
```

---

## ADR Numbering System: `[C][S][XX]`

```
Format: [Category][SubCategory][Sequence]

Example: ADR-3102 V2.1.0
         ││││
         │││└── Sequence 02 (second ADR in sub-cat)
         ││└─── Sub-cat 1 (within Category 3)
         │└──── Category 3 (Requirements)
         └───── "ADR-" prefix
```

### Category Map

| C | Category | Description |
|---|----------|-------------|
| 1 | Foundation | Principles, standards, governance |
| 2 | Infrastructure | Hosting, networking, storage |
| 3 | Requirements | User needs, business rules |
| 4 | Design | Architecture, patterns, interfaces |
| 5 | Implementation | Code, libraries, integrations |
| 6 | Quality | Testing, validation, monitoring |
| 7 | Operations | Deployment, maintenance |
| 8 | Security | Auth, encryption, compliance |
| 9 | Evolution | Deprecation, migration |

*This is a suggested structure. Projects should define categories matching their domain in CLAUDE.md.*

---

## Version Bump Protocol

### Semantic Versioning for ADRs

| Version Part | When to Bump | Cross-Ref Impact |
|--------------|--------------|------------------|
| **Patch** (V1.0.X) | Typos, clarifications, formatting | None required |
| **Minor** (V1.X.0) | New sections, added details, non-breaking changes | Check related ADRs |
| **Major** (VX.0.0) | Breaking changes, restructuring, new requirements | **MUST update ALL related ADRs** |

### Pre-Bump Checklist

Before bumping a version:

1. **Query related ADRs:**
   ```
   Grep for: "ADR-XXXX" or "depends_on:.*XXXX"
   ```

2. **Check version refs:**
   - List all ADRs that reference this one
   - Note their current version refs

3. **After bump:**
   - Update `related_adrs` section in THIS ADR
   - Update version refs in ALL related ADRs
   - Log in CHANGELOG.md

---

## Cross-Reference Format

### In Frontmatter

```yaml
---
id: ADR-4001
version: V2.1.0
depends_on:
  - ADR-1101@V2.0.0   # Universal Graph
  - ADR-2001@V1.3.0   # EventProcessor
extends:
  - ADR-3001@V1.0.0   # Product Owner
---
```

### In Body

```markdown
## Related ADRs

| ADR | Version | Relationship |
|-----|---------|--------------|
| [ADR-1101](./1101-universal-graph.md) | V2.0.0 | Depends on (graph schema) |
| [ADR-2001](./2001-event-processor.md) | V1.3.0 | Implements (EP spawns this) |
| [ADR-6101](./6101-validation.md) | V1.0.0 | Validates against |
```

### Stale Reference Detection

When reading an ADR, check:
```
If ref says "ADR-1101@V1.0.0" but ADR-1101 is now V2.0.0:
  → FLAG as stale reference
  → Add to validation report
```

---

## ADR Template

```markdown
---
id: ADR-[CSXX]
version: V1.0.0
status: Draft | Proposed | Accepted | Deprecated | Superseded
created: YYYY-MM-DD
updated: YYYY-MM-DD
authors: [names]
depends_on: []
extends: []
supersedes: []
tags: [category, subcategory, keywords]
---

# ADR-[CSXX]: [Title]

## Status

**[Status]** - V[X.Y.Z]

## Context

[What problem are we solving? What constraints exist?]

## Decision

[What did we decide? Be specific.]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Tradeoff 1]
- [Tradeoff 2]

### Neutral
- [Observation]

## Related ADRs

| ADR | Version | Relationship |
|-----|---------|--------------|
| [ADR-XXXX](./XXXX-title.md) | VX.Y.Z | [depends_on/extends/supersedes] |

## Implementation Notes

[Optional: Key implementation details, code snippets, examples]

---

*ADR-[CSXX] V[X.Y.Z] | [Status] | Created: [date] | Updated: [date]*
```

---

## Workflow: Creating a New ADR

1. **Determine Category & Sub-Category**
   - Which layer does this belong to?
   - What sub-category within that layer?

2. **Find Next Sequence Number**
   ```bash
   ls docs/adr/ | grep "^[CS]" | sort -n | tail -1
   ```

3. **Check for Existing ADR**
   - Search for similar topics
   - If exists: VERSION IT, don't create new

4. **Draft ADR**
   - Use template above
   - Fill frontmatter completely
   - Include all cross-references with versions

5. **Validate Cross-References**
   - Verify all referenced ADRs exist
   - Check version numbers are current
   - Update related ADRs' `Related ADRs` sections

6. **Submit for Review**
   - Status: `Proposed`
   - Validation systems should check ADR compliance on commit

---

## Workflow: Updating an Existing ADR

1. **Read Current Version**
   - Note current version number
   - List all cross-references

2. **Determine Bump Type**
   - Patch: typo/clarification
   - Minor: new content, non-breaking
   - Major: breaking changes

3. **Query Dependents**
   ```bash
   grep -r "ADR-XXXX" docs/adr/
   ```

4. **Make Changes**
   - Bump version in frontmatter
   - Update `updated` date
   - Update content

5. **If Major Bump:**
   - Update ALL dependent ADRs' version refs
   - Add CHANGELOG entry
   - Consider migration notes

6. **Commit with ADR Ref**
   ```
   docs(adr): Update ADR-XXXX to V2.0.0 - [summary]

   BREAKING: [what changed]
   Related: ADR-YYYY, ADR-ZZZZ (refs updated)
   ```

---

## Anti-Patterns

- ❌ Creating ADR-0099 to "update" ADR-0073 (version it instead)
- ❌ Cross-references without version numbers
- ❌ Major bumps without updating dependents
- ❌ Duplicate ADRs covering same topic
- ❌ ADRs without category alignment

---

## Project Configuration

Override defaults in your project's CLAUDE.md:
- **ADR location:** Add `## ADR Path: docs/decisions/` to specify custom path
- **Category map:** Define custom categories matching your domain
- **Commit format:** Specify your team's commit convention

---

## Quick Reference

**New ADR:** Category → Sub-Cat → Next sequence → Template → Cross-refs

**Update ADR:** Read → Bump type → Query dependents → Update → Update refs

**Stale Ref:** `@V1.0.0` but ADR is now `V2.0.0` → Update ref → Log

---

*Expertise package for ADR management*
