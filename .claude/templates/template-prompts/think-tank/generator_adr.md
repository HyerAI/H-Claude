# Generator: ADR (Architectural Decision Record)
# Variables: {{SESSION_PATH}}, {{TOPIC}}, {{DECIDED_PATH}}, {{CONFIDENCE}}
# Model: Flash (2405)

# ADR Writer - Record Think-Tank Decision

You are recording an architectural decision made by the think-tank council.

## Skill Reference
Read and follow: .claude/skills/adr-writer/SKILL.md

## Decision Context
Read these files:
1. {{SESSION_PATH}}/00_BRIEFING.md - Original problem
2. {{SESSION_PATH}}/04_DECISION_MAP.md - Decision details
3. {{SESSION_PATH}}/STATE.yaml - Decision metadata

## Decision Summary
- **Topic:** {{TOPIC}}
- **Decided Path:** {{DECIDED_PATH}}
- **Confidence:** {{CONFIDENCE}}
- **Session:** {{SESSION_PATH}}

## Tasks

### 1. Check for Existing ADR
Search .claude/PM/SSoT/ADRs/ for ADRs related to this topic.
- If found: Prepare VERSION BUMP
- If not found: Prepare NEW ADR

### 2. Determine Category
| C | Category | Use When |
|---|----------|----------|
| 1 | Foundation | Principles, standards, governance |
| 2 | Infrastructure | Hosting, networking, storage |
| 3 | Requirements | User needs, business rules |
| 4 | Design | Architecture, patterns, interfaces |
| 5 | Implementation | Code, libraries, integrations |
| 6 | Quality | Testing, validation, monitoring |
| 7 | Operations | Deployment, maintenance |
| 8 | Security | Auth, encryption, compliance |
| 9 | Evolution | Deprecation, migration |

### 3. Create/Update ADR
Write to: .claude/PM/SSoT/ADRs/[CSXX]-[slug].md

Use template with:
- **Context:** From 00_BRIEFING.md
- **Decision:** From 04_DECISION_MAP.md (chosen path)
- **Consequences:** Trade-offs and risks

### 4. Update Cross-References
If related ADRs exist, update their 'Related ADRs' sections.

### 5. Report
Output:
- ADR path: [path]
- Version: [VX.Y.Z]
- Category: [C] - [name]
- Cross-references: [list or 'none']
