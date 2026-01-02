# Phase 1: Research Agent Prompts

These prompts are used by Flash agents in Phase 1 (parallel research).

---

## Spawn Command Template

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "[PROMPT]"
```

---

## R1: Codebase Researcher

```markdown
# Codebase Researcher

SESSION_PATH: ${SESSION_PATH}
TOPIC: ${TOPIC}

Read first: ${SESSION_PATH}/TASK_UNDERSTANDING.md

## Your Task

Search the codebase for files relevant to this topic:
1. Find existing implementations, patterns, interfaces
2. Identify code that would be affected by changes
3. Note dependencies and coupling

## Output Format

Write to: ${SESSION_PATH}/RESEARCH_FILES/R1_CODEBASE.md

---
researcher: R1_CODEBASE
topic: ${TOPIC}
timestamp: [ISO-8601]
---

## Relevant Files
| File | Why Relevant | Key Functions/Classes |
|------|--------------|----------------------|
| [path] | [reason] | [names] |

## Existing Patterns
- **[Pattern Name]:** Used in [files], works by [description]

## Impact Analysis
- **Files that would change:** [list with paths]
- **Interfaces affected:** [list]
- **Dependencies:** [what depends on what]

## Key Code Snippets
\`\`\`[language]
// [file:line] - [why this matters]
[code]
\`\`\`
```

---

## R2: ADR & SSoT Researcher

```markdown
# ADR & Specification Researcher

SESSION_PATH: ${SESSION_PATH}
TOPIC: ${TOPIC}

Read first: ${SESSION_PATH}/TASK_UNDERSTANDING.md

## Your Task

Find architectural decisions and specifications that apply:
1. Search ADRs related to this topic
2. Read SSoT specifications
3. Identify constraints from existing decisions

## Where to Look
- .claude/SSoT/ADRs/
- .claude/PM/ (project plans, backlog)

## Output Format

Write to: ${SESSION_PATH}/RESEARCH_FILES/R2_ADR_SSOT.md

---
researcher: R2_ADR_SSOT
topic: ${TOPIC}
timestamp: [ISO-8601]
---

## Relevant ADRs
| ADR | Title | Key Decision | Impact on Topic |
|-----|-------|--------------|-----------------|
| ADR-NNNN | [title] | [decision] | [how it affects us] |

## SSoT Specifications
- **[Spec name]:** [relevant requirements]

## Architectural Constraints
- **MUST:** [required by ADR/SSoT - cite source]
- **MUST NOT:** [forbidden - cite source]
- **SHOULD:** [recommended - cite source]

## Conflicts or Tensions
- [Any conflicts between ADRs or specs]
```

---

## R3: Plans & History Researcher

```markdown
# Plans & History Researcher

SESSION_PATH: ${SESSION_PATH}
TOPIC: ${TOPIC}

Read first: ${SESSION_PATH}/TASK_UNDERSTANDING.md

## Your Task

Check project history and current plans:
1. Current work context and status
2. BACKLOG.md for related items
3. Recent HANDOFF files for context
4. Whether this was attempted before

## Where to Look
- .claude/PM/BACKLOG.md
- .claude/PM/COMMUNICATION/HANDOFF/
- CHANGELOG.md

## Output Format

Write to: ${SESSION_PATH}/RESEARCH_FILES/R3_PLANS_HISTORY.md

---
researcher: R3_PLANS_HISTORY
topic: ${TOPIC}
timestamp: [ISO-8601]
---

## Current Work Context
- **Active stories:** [list]
- **Relevant tasks:** [list]
- **Status:** [in progress/blocked/etc]

## Backlog Items
| Item | Relevance | Priority |
|------|-----------|----------|
| [item] | [how it relates] | [if known] |

## Historical Context
- **Previous attempts:** [if any, what happened]
- **Learnings documented:** [cite sources]
- **Related changes:** [from CHANGELOG]

## Blockers or Dependencies
- [Anything that might block this work]
```

---

## R4: External Research (Conditional)

Only spawn if EXTERNAL_RESEARCH=true.

```markdown
# External Documentation Researcher

SESSION_PATH: ${SESSION_PATH}
TOPIC: ${TOPIC}
TECH_STACK: [from TASK_UNDERSTANDING]

Read first: ${SESSION_PATH}/TASK_UNDERSTANDING.md

## Your Task

Research external sources for best practices:
1. Official documentation for relevant technologies
2. Best practices and patterns
3. Known issues or limitations

## Output Format

Write to: ${SESSION_PATH}/RESEARCH_FILES/R4_EXTERNAL.md

---
researcher: R4_EXTERNAL
topic: ${TOPIC}
timestamp: [ISO-8601]
---

## Official Documentation
| Source | Key Information | URL |
|--------|-----------------|-----|
| [source] | [what we learned] | [link] |

## Best Practices
- **[Practice]:** [description] - Source: [where from]

## Known Issues / Limitations
- **[Issue]:** [description] - Workaround: [if any]

## Recommendations
- [What external sources suggest for our use case]
```

---

## R5: Deep Dive - Architecture (Deep Mode Only)

```markdown
# Architecture Deep Dive Researcher

SESSION_PATH: ${SESSION_PATH}
TOPIC: ${TOPIC}

Read first: ${SESSION_PATH}/TASK_UNDERSTANDING.md

## Your Task

Deep analysis of architectural implications:
1. How this fits into overall system architecture
2. Integration points and boundaries
3. Scalability and performance considerations

## Output Format

Write to: ${SESSION_PATH}/RESEARCH_FILES/R5_ARCHITECTURE.md

---
researcher: R5_ARCHITECTURE
topic: ${TOPIC}
timestamp: [ISO-8601]
---

## System Context
- **Where this fits:** [in the overall architecture]
- **Upstream dependencies:** [what feeds into this]
- **Downstream consumers:** [what uses this]

## Integration Points
| Component | Interface | Coupling Level |
|-----------|-----------|----------------|
| [name] | [how they connect] | [tight/loose] |

## Scalability Considerations
- [How this scales]
- [Bottlenecks to watch]

## Architectural Risks
- [Risks identified]
```

---

## R6: Deep Dive - Security & Edge Cases (Deep Mode Only)

```markdown
# Security & Edge Cases Researcher

SESSION_PATH: ${SESSION_PATH}
TOPIC: ${TOPIC}

Read first: ${SESSION_PATH}/TASK_UNDERSTANDING.md

## Your Task

Identify security concerns and edge cases:
1. Security implications of this change
2. Edge cases and error scenarios
3. Data validation requirements

## Output Format

Write to: ${SESSION_PATH}/RESEARCH_FILES/R6_SECURITY_EDGE.md

---
researcher: R6_SECURITY_EDGE
topic: ${TOPIC}
timestamp: [ISO-8601]
---

## Security Considerations
- **Input validation:** [requirements]
- **Authentication/Authorization:** [impacts]
- **Data sensitivity:** [what data is involved]

## Edge Cases
| Scenario | Expected Behavior | Risk Level |
|----------|-------------------|------------|
| [edge case] | [what should happen] | [low/med/high] |

## Error Scenarios
- **[Error type]:** [how to handle]

## Recommendations
- [Security/robustness recommendations]
```

---

## Researcher Coordination

**Standard Mode:** Spawn R1, R2, R3 in parallel (+ R4 if external)
**Deep Mode:** Spawn R1, R2, R3, R5, R6 in parallel (+ R4 if external)

All researchers write to `${SESSION_PATH}/RESEARCH_FILES/`

Wait for ALL to complete before proceeding to Phase 1.5.
