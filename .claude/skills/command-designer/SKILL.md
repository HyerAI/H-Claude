---
version: V1.0.0
status: stable
timestamp: 2025-12-29
tags: [skill, meta, command-design, orchestration, multi-agent]
description: "Design multi-agent commands using orchestration patterns"
---

# /command-designer - Multi-Agent Command Designer

**Purpose:** Design new commands that require multi-agent orchestration, ensuring they follow proven patterns and maintain consistency with existing commands.

---

## Quick Start

```markdown
/command-designer

COMMAND_NAME: [name of new command, e.g., "code-review"]
PURPOSE: [what problem does it solve]
COMPLEXITY: [simple|moderate|complex]

CONTEXT:
- [What triggers this command]
- [What artifacts it produces]
- [Who consumes the output]
```

---

## What This Skill Does

1. **Analyzes** the command requirements
2. **Recommends** which orchestration patterns apply
3. **Designs** the agent hierarchy and flow
4. **Generates** a complete command specification

---

## Design Process

### Phase 1: Requirements Analysis

Ask these questions:

| Question | Why It Matters |
|----------|----------------|
| What's the input? | Determines if research phase needed |
| What's the output? | Shapes final synthesis |
| How many distinct steps? | Determines if Oraca pattern applies |
| Can steps run in parallel? | Determines if Interface Contracts needed |
| What can go wrong? | Shapes Circuit Breaker rules |
| Who verifies quality? | Determines QA gate structure |

### Phase 2: Pattern Selection

Reference: `.claude/ORCHESTRATION_PATTERNS.md`

| If... | Then Use Pattern... |
|-------|---------------------|
| Command needs research first | **Pattern 1:** Synthesis Before Reasoning |
| Command has 5+ distinct tasks | **Pattern 2:** Oraca Phase Orchestrators |
| Output quality is critical | **Pattern 3:** Adversarial Prior (15% Rule) |
| Command produces artifacts | **Pattern 4:** Session Folders |
| Command is async/background | **Pattern 5:** Flight Recorder |
| Command has domain specialization | **Pattern 6:** Pro as Commander |
| Tasks can run in parallel | **Pattern 7:** Interface Contracts |
| Tasks can fail/retry | **Pattern 8:** Circuit Breaker |

### Phase 3: Agent Hierarchy Design

Design the spawn tree:

```
[Who is the orchestrator?]
    ↓
    ├──→ [Who does Phase 1?] ──→ [Workers?] ──→ [QA?]
    │
    ├──→ [Who does Phase 2?] ──→ [Workers?] ──→ [QA?]
    │
    └──→ [Who synthesizes?]
```

**Model Assignment Rules:**

| Role | Model | Proxy | Why |
|------|-------|-------|-----|
| Orchestrator | Opus | 2408 | High-value reasoning, coordinates everything |
| Synthesizer/QA | Pro | 2406 | Curates, challenges, validates |
| Researcher/Worker | Flash | 2405 | Parallel execution, disposable context |
| Phase Orchestrator (Oraca) | Flash | 2405 | Mechanical coordination, cheaper |

### Phase 4: Session Folder Design

Define the artifact structure:

```
.claude/{command-name}/${session-slug}/
├── ORCHESTRATOR_LOG.md       # Always include (Flight Recorder)
├── [PHASE_1_ARTIFACTS]/      # If multi-phase
├── [PHASE_2_ARTIFACTS]/      # If multi-phase
├── ANALYSIS/                 # If synthesis needed
└── [FINAL_OUTPUT].md         # The deliverable
```

**Session Convention:**
| Element | Pattern |
|---------|---------|
| Base Path | `.claude/{command-name}/` |
| Session Slug | `YYYY-MM-DD_HHmmss-{context}` |
| Example | `.claude/code-review/2025-12-30_143022-initial/` |
| Flight Recorder | `ORCHESTRATOR_LOG.md` (always in session root) |

### Phase 5: Phase & Gate Design

Define the execution flow:

```
PHASE 0: [Setup/Validation]
    ↓
PHASE 1: [First major work]
    ↓ ── QA Gate ──
PHASE 1.5: [Synthesis if needed]
    ↓
PHASE 2: [Second major work]
    ↓ ── QA Gate ──
PHASE N: [Final synthesis/output]
```

**Gate Types:**
| Gate | When to Use |
|------|-------------|
| Pro QA | After worker output, before next phase |
| Sweep | After all work, before final output |
| Human Escalation | On 3-strike or blocked |

### Phase 6: Command Specification

Generate the command markdown with:

1. **Frontmatter** (version, status, tags)
2. **Quick Start** (minimal invocation)
3. **Architecture Overview** (ASCII/Mermaid diagram)
4. **Session Folder Structure**
5. **Proxy Configuration**
6. **Orchestrator Prompt** (the full spawn command)
7. **Phase Definitions** (what each phase does)
8. **Error Handling** (circuit breakers, escalation)
9. **Output Artifacts** (table of what's produced)
10. **The Mantra** (philosophy statement)

---

## Command Specification Template

```markdown
---
version: V1.0.0
status: draft
timestamp: [ISO-8601]
tags: [command, ...]
description: "[One-line description]"
---

# /[command-name] - [Title]

**Philosophy:** [Core principle, e.g., "Trust but Verify"]

**Purpose:** [What problem it solves]

---

## Quick Start

\`\`\`markdown
/[command-name]

PARAM_1: [description]
PARAM_2: [description]
\`\`\`

---

## Architecture Overview

\`\`\`
HD invokes /[command-name]
     ↓
Spawn OPUS Orchestrator (BACKGROUND)
     ↓
┌────────────────────────────────────────────────────────────────────────┐
│  PHASE 0: [Name]                                                       │
│  [What happens]                                                        │
├────────────────────────────────────────────────────────────────────────┤
│  PHASE 1: [Name]                                                       │
│  [What happens]                                                        │
├────────────────────────────────────────────────────────────────────────┤
│  ...                                                                   │
├────────────────────────────────────────────────────────────────────────┤
│  OUTPUT: ${SLUG}_[SUFFIX]_Session/[OUTPUT].md                          │
└────────────────────────────────────────────────────────────────────────┘
\`\`\`

---

## Session Folder Structure

\`\`\`
.claude/{command-name}/${session-slug}/
├── ORCHESTRATOR_LOG.md
├── [artifacts...]
└── [OUTPUT].md
\`\`\`

---

## Proxy Configuration

\`\`\`bash
# [Role] ([Model])
ANTHROPIC_API_BASE_URL=http://localhost:[PORT] claude --dangerously-skip-permissions
\`\`\`

---

## Orchestrator Execution

\`\`\`bash
ANTHROPIC_API_BASE_URL=http://localhost:2408 claude --dangerously-skip-permissions -p "
$(cat <<'ORCHESTRATOR_PROMPT'

# [Command Name] Orchestrator

[Full orchestrator instructions...]

ORCHESTRATOR_PROMPT
)"
\`\`\`

---

## Phase Definitions

### Phase 0: [Name]
[Details]

### Phase 1: [Name]
[Details]

---

## Error Handling

### [Scenario 1]
[How to handle]

### [Scenario 2]
[How to handle]

---

## Output Artifacts

| Artifact | Location | Creator |
|----------|----------|---------|
| ... | ... | ... |

---

## The [Command] Mantra

\`\`\`
[Philosophy statements]
\`\`\`

---

**Version:** V1.0.0
**Updated:** [date]
**Status:** [draft|production-ready]
```

---

## Design Checklist

Before finalizing, verify:

- [ ] **Orchestrator is Opus** (unless simple command)
- [ ] **Synthesis boundaries exist** (Pro curates before Opus reads)
- [ ] **Session folder is self-contained** (one folder = one run)
- [ ] **Flight Recorder included** (ORCHESTRATOR_LOG.md)
- [ ] **Circuit breakers defined** (what triggers escalation)
- [ ] **QA gates at phase boundaries** (not just at end)
- [ ] **Error handling documented** (timeouts, failures, loops)
- [ ] **Mantra captures philosophy** (one-liner guidance)

---

## Examples of Well-Designed Commands

| Command | Patterns Used | Why It Works |
|---------|---------------|--------------|
| `/hc-plan` | 1, 3, 4, 5, 6 | Research → Synthesis → Dialectic → Validation |
| `/hc-execute` | 2, 3, 4, 5, 7, 8 | Oraca phases → QA gates → Sweep → Circuit breakers |
| `/red-team` | 3, 4, 5, 6 | Sector commanders → Synthesis → Final audit |

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Fix |
|--------------|--------------|-----|
| Opus spawns 10+ workers directly | Context pollution | Use Oraca or Pro commanders |
| No synthesis layer | Raw data overwhelms Opus | Add Phase 1.5 Pro synthesis |
| Single QA at end | Errors compound | QA at each phase boundary |
| No circuit breaker | Infinite loops | 3-strike rule + escalation |
| Scattered artifacts | Can't trace decisions | Self-contained session folder |

---

## Invocation

When invoked, this skill will:

1. Read the command requirements from user
2. Ask clarifying questions (complexity, parallelism, QA needs)
3. Recommend patterns from ORCHESTRATION_PATTERNS.md
4. Generate a draft command specification
5. Review against checklist
6. Output to `.claude/{command-name}/{session-slug}/{command-name}_DESIGN.md`

---

## Related

| Document | Purpose |
|----------|---------|
| [ORCHESTRATION_PATTERNS.md](../../ORCHESTRATION_PATTERNS.md) | Pattern definitions |
| [hc-plan.md](../../commands/hc-plan.md) | Example: planning command |
| [hc-execute.md](../../commands/hc-execute.md) | Example: execution command |
| [red-team.md](../../commands/red-team.md) | Example: audit command |

---

**Version:** V1.0.0
**Updated:** 2025-12-29
**Author:** HeyDude
