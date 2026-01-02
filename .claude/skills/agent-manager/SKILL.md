---
name: agent-manager
description: Invoke to create, validate, and update agent definitions - enforces agent constitution patterns
triggers: "/agent-manager create|validate|update|audit|diff|orphans|learnings|promote"
used_by: [orchestrator-roles, architect-roles, qa-roles]
self_improves: true
auto_learn: true
learnings_path: learnings/AGENT_LEARNINGS.md
---

# Agent Manager Skill

> **Core Purpose:** Enforce agent constitution patterns. Verify agents exist as proper artifacts with consistent definition, tools, skills, and registry. Fast feedback (L0-L2) for iteration; strict mode (L0-L3) for commit gates.

---

## Overview

The `agent-manager` skill codifies a **10-point verification framework** for creating and updating agents in any multi-agent system. It ensures:

1. **Agent definition files exist** with required YAML frontmatter and body sections
2. **Model-proxy alignment** is correct (flash→2405, pro→2406, opus→2408)
3. **Role-tool permissions** match authorization matrix (if defined in constitution)
4. **Skill linkage is bidirectional** (agent→skills, skills→agent used_by)
5. **Skills index is updated** when agents reference new skills
6. **Registry is synchronized** (no orphans, no missing files)
7. **Tool-constraint consistency** is enforced (tools field ↔ Constraints section)
8. **Flowchart integration** is triggered via flowchart-designer skill (if applicable)
9. **Validation scripts execute** cleanly in strict mode (if configured)
10. **Dynamic context** is generated per agent (related ADRs, loaded skills)

**Design Principle:** Validation-first with fast feedback loop (L0-L2 default) and optional strict mode (L0-L3) for pre-commit gates.

---

## Invocation Commands

### Creation

```bash
/agent-manager create <name> --type p3-worker    # Generate from type-specific template
/agent-manager create <name>                      # Generate from _base.md template
```

**Returns:** Agent skeleton with YAML frontmatter, all required sections, template comments.

---

### Validation

```bash
/agent-manager validate <name>                    # L0-L2 validation (fast, no scripts)
/agent-manager validate <name> --strict           # L0-L3 validation (with script execution)
```

**Returns:** JSON validation report with 10-point breakdown, pass/warn/fail status.

---

### Update & Maintenance

```bash
/agent-manager update <name>                      # Re-validate after manual edits
/agent-manager audit                              # Validate ALL agents, full l2
/agent-manager diff <name>                        # Compare agent vs registry entry
/agent-manager orphans                            # Find skills without used_by + unregistered agents
```

---

### Self-Improvement

```bash
/agent-manager learnings                          # View recent learnings summary
/agent-manager promote                            # Promote recurring learnings (3+) to templates/checklists
```

**Automatic:** Learning is built into every `create`, `update`, and `validate` command. No manual step required.

---

## Self-Improvement Protocol

> **Principle:** The agent-manager gets better with every task by recording patterns, mistakes, and improvements. **Learning is automatic, not optional.**

### Automatic Learning Cycle

```
┌─────────────────────────────────────────────────────────────┐
│                 AUTOMATIC LEARNING CYCLE                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  COMMAND START                                               │
│       ↓                                                      │
│  1. LOAD CONTEXT    Read learnings/AGENT_LEARNINGS.md       │
│       ↓             Apply recent patterns, avoid mistakes    │
│                                                              │
│  2. EXECUTE TASK    Run create/update/validate              │
│       ↓             Track what works and what fails          │
│                                                              │
│  3. AUTO-RECORD     Append learning entry (AUTOMATIC)       │
│       ↓             Categorize: Pattern/Mistake/Gap/etc.    │
│                                                              │
│  COMMAND END        Return result + learning recorded        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Built Into Every Command

Every agent-manager command includes these automatic steps:

| Step | When | What Happens |
|------|------|--------------|
| **Load** | Command start | Read `AGENT_LEARNINGS.md`, apply to current task |
| **Track** | During execution | Note patterns, mistakes, gaps discovered |
| **Record** | Command end | Append learning entry with context |
| **Check Promotion** | After record | If pattern count ≥3, flag for promotion |

### Learning Categories

| Category | What to Record | Promotes To |
|----------|----------------|-------------|
| **Pattern** | Recurring structure or approach that works | Template section |
| **Mistake** | Error that should be avoided | Checklist "Common Mistakes" |
| **Template Improvement** | Better default or placeholder | Template update |
| **Checklist Gap** | Missing step discovered during task | Checklist step |
| **Tool Discovery** | New tool an agent type commonly needs | Permission matrix |
| **Cross-Ref Issue** | Bidirectional link problem | Validation logic |

### Promotion Threshold

A learning is promoted when it appears **3+ times** in `AGENT_LEARNINGS.md`. Use `/agent-manager promote` to apply.

### Auto-Recorded Entry Format

Each command automatically appends:

```markdown
### [DATE] - [AGENT_NAME] - [CATEGORY]

**Command:** create|update|validate
**Context:** What task was being performed
**Learning:** What was discovered (pattern, mistake, gap)
**Recurrence:** [N] times seen
**Promotion Ready:** [YES/NO]
```

The agent-manager tracks recurrence automatically and flags entries ready for promotion.

---

## The 10-Point Verification Framework

### Validation Pyramid

```
┌─────────────────────┐
│ L3: Scripts         │ kb_health_check.py (slow)
├─────────────────────┤
│ L2: Cross-Refs      │ File reads only (fast)
├─────────────────────┤
│ L1: Schema          │ Required fields (instant)
├─────────────────────┤
│ L0: Syntax          │ YAML parse (instant)
└─────────────────────┘
```

**Default:** L0-L2 (fast feedback for iteration)
**--strict mode:** L0-L3 (all validation including scripts, for commit gates)

---

### Point 1: Agent Definition File (MANDATORY)

**Validation Level:** L0-L1

**Location:** `.claude/agents/{agent-name}.md`

**Required Frontmatter:**

| Field | Type | Validation | Example |
|-------|------|------------|---------|
| `name` | string | kebab-case, unique across roster | `code-worker` |
| `description` | string | Starts with "Invoke" verb, <100 chars | `Invoke to implement task specs into code` |
| `tools` | CSV string | Tools match loop permissions (Point 3) | `Read, Glob, Grep, Bash` |
| `model` | enum | `opus` \| `pro` \| `flash` | `flash` |
| `proxy` | URL | Must match model (Point 2) | `http://localhost:2405` |
| `skills` | CSV string | Each skill must exist in `.claude/skills/` | `code-implementation, test-writing` |

**Optional Frontmatter:**

| Field | Type | Notes | Example |
|-------|------|-------|---------|
| `alias` | string | Alternative invocation name | `code-impl` |
| `phase` | string | Workflow phase identifier | `implementation` |
| `gate(s)` | string or array | Quality gates this agent serves | `['review_gate', 'test_gate']` |
| `patterns` | CSV string | Each pattern file must exist | `atomic-decision, kernel-spec` |
| `related_adr` | array | `ADR-XXXX` format, must exist | `['ADR-1201', 'ADR-2001']` |
| `role` | string | Role category for permission matrix | `worker` |

**Required Body Sections:**

1. **`# Agent Name`** (H1 title with role description)
   - Exact match: `name` field from frontmatter

2. **`## Personality`** (4-5 bullet traits defining persona)
   - Format: `- {Trait}: {Description}`

3. **`## Protocol`** (Numbered workflow stages)
   - Format: `### Stage N: {Name}` with step-by-step execution

4. **`## Constraints`** (CANNOT list)
   - Format: `- CANNOT: {tool|behavior}` (must match inverse of tools)

5. **`## State Transitions`** (Input/output states)
   - Format: Table with columns `[Input State | Output State | Condition]`

6. **`## MCP Tools`** (Categorized tool access)
   - Grouped by category: Context Tools, File Tools, Task Tools, etc.

---

### Point 2: Model-Proxy Alignment (MANDATORY)

**Validation Level:** L0-L1

**Authorized Mappings:**

| Model | Port | Proxy URL | Validation |
|-------|------|-----------|------------|
| `flash` | 2405 | `http://localhost:2405` | REJECT if model=flash but proxy ≠ 2405 |
| `pro` | 2406 | `http://localhost:2406` | REJECT if model=pro but proxy ≠ 2406 |
| `opus` | 2408 | `http://localhost:2408` | REJECT if model=opus but proxy ≠ 2408 |

**Action:** FAIL validation if mismatch detected.

---

### Point 3: Role-Tool Permissions (CONFIGURABLE)

**Validation Level:** L1 (cross-reference with constitution if defined)

**Example Authorization Matrix:**

> *Define your project's permission matrix in CLAUDE.md or a constitution ADR. Below is an example structure.*

| Tool | Research | Planning | Execution | Validation | Support |
|------|:--------:|:--------:|:---------:|:----------:|:-------:|
| Read | ✓ | ✓ | ✓ | ✓ | ✓ |
| Glob | ✓ | ✓ | ✓ | ✓ | ✓ |
| Grep | ✓ | ✓ | ✓ | ✓ | ✓ |
| Write | ✗ | ✓ | ✓ | ✗ | ✓ |
| Edit | ✗ | ✓ | ✓ | ✗ | ✓ |
| Bash | ✗ | ✗ | ✓ | ✓ | ✓ |
| Task | ✓ | ✓ | ✓ | ✓ | ✓ |

**Validation:** WARN (not FAIL) on tool divergence. User must manually reconcile. (Matrix is reference, not absolute law - exceptions exist by design.)

---

### Point 4: Skill Linkage (MANDATORY)

**Validation Level:** L2 (file existence check)

**Bidirectional Validation:**

1. **Agent → Skills:** Every skill listed in `agent.skills` must have a file at `.claude/skills/{skill-name}/SKILL.md`

2. **Skills → Agent:** Update target skill's `used_by` field to include this agent name

**Validation:** FAIL if skill file doesn't exist at expected path.

**Action on skill creation:** Auto-append agent to skill's `used_by` (or prompt user).

---

### Point 5: Skills Index Update (MANDATORY)

**Validation Level:** L2 (file format check)

**Location:** `.claude/skills/SKILLS_INDEX.md` (if exists)

**Update Required When:**
- New skill created
- Skill `used_by` field changes
- Skill category changes

**Entry Format:**

```markdown
| [{skill-name}]({skill-name}/SKILL.md) | {Category} | {Agent1}, {Agent2}, ... |
```

**Action:** FAIL validation if agent references skill not in SKILLS_INDEX.

---

### Point 6: Registry Synchronization (MANDATORY for new agents)

**Validation Level:** L2 (roster sync check)

**Location:** Agent constitution ADR or registry file (e.g., `docs/adr/agent-roster.md` or `.claude/agents/AGENTS_INDEX.md`)

**Bidirectional Sync:**

```python
agent_files = glob(".claude/agents/*.md")
registry_agents = parse_agent_registry()

orphan_agents = agent_files - registry_agents   # Files without registry entry
missing_agents = registry_agents - agent_files  # Registry entries without files

if orphan_agents:   WARN "Files without registry entry: {orphan_agents}"
if missing_agents:  FAIL "Registry entries without files: {missing_agents}"
```

**Action:**
- WARN on orphan agent files (file exists, not registered yet)
- FAIL on missing agent files (registry lists agent, file doesn't exist)

**New Agent Workflow:** Agent-manager can auto-append new agent to registry (user approval required).

---

### Point 7: Tool-Constraint Consistency (MANDATORY)

**Validation Level:** L1 (logical inference)

**Rule:** Agent's `Constraints` section must be the logical inverse of `tools` field.

**Examples:**

```
IF "Write" NOT IN agent.tools THEN "CANNOT use Write" MUST be in Constraints
IF "Bash" NOT IN agent.tools THEN "CANNOT use Bash" MUST be in Constraints
IF "Bash" IN agent.tools THEN "CANNOT use Bash" MUST NOT be in Constraints
```

**Common Constraint Patterns by Role:**

| Role | Typical Constraints |
|------|---------------------|
| Research | CANNOT: Write, Edit, Bash, git commit |
| Planning | CANNOT: Bash, git commit, direct user interaction |
| Execution | CANNOT: git commit without review |
| Validation | CANNOT: Write, Edit (fix bugs directly) |

**Validation:** FAIL if inconsistency detected (tool listed but constraint says can't use, or vice versa).

---

### Point 8: Flowchart Integration (OPTIONAL)

**Validation Level:** L2-L3 (depends on scope)

**Scope:** If project uses visual flowcharts, agents should be represented.

**Flowchart Location:** Project-defined (e.g., `docs/[ProjectName]_Flowchart.html`)

**CRITICAL:** Flowchart updates are NOT performed by agent-manager directly. Instead:

**Workflow:**

1. **Agent-manager detects** flowchart update needed (new agent or updated agent)
2. **Agent-manager generates** JSON payload with agent node data
3. **Agent-manager spawns worker** via `flowchart-designer` skill (with detailed prompt)
4. **Worker integrates** node into appropriate flowchart HTML
5. **Worker commits** changes with `docs(flowchart):` prefix

**Node JSON Payload (Generated by agent-manager):**

```json
{
  "agent": "{agent-name}",
  "operation": "create|update|delete",
  "target_flowchart": "{flowchart-path}",
  "node_data": {
    "id": "{agent-name}",
    "label": "{Agent Display Name}",
    "role": "{research|planning|execution|validation|support}",
    "model": "{opus|pro|flash}",
    "proxy": "{port}",
    "tools": [...],
    "skills": [...],
    "triggers": [...],
    "outputs": [...]
  }
}
```

**Spawning the flowchart worker:**

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "
/flowchart-designer

OPERATION: {create|update|delete}
TARGET: {flowchart-path}
PAYLOAD: {JSON payload above}
"
```

**Validation:** Check that flowchart file exists and contains agent (L2 check, not strict). Skip if no flowcharts configured.

---

### Point 9: Validation Scripts (OPTIONAL in --strict mode)

**Validation Level:** L3 (script execution)

**Scripts to Execute:** Configure in project's CLAUDE.md or `.claude/config.yaml`

| Script | Purpose | Timeout |
|--------|---------|---------|
| Health check script | Cross-reference validation (ADRs, agents, skills) | 30s |
| Variable validator | Variable name consistency across artifacts | 20s |
| Permission validator | Role hierarchy and tool permissions | 15s |

**Example Execution Command:**

```bash
python3 scripts/validate_agents.py --check-all
```

**Rule:** All scripts must exit with status 0. Any non-zero exit = FAIL validation.

**When to Use --strict:**
- Before committing agent changes to git
- During pre-deployment checks
- Manual audit mode (`/agent-manager audit --strict`)

---

### Point 10: Dynamic Context (RECOMMENDED)

**Validation Level:** L0 (no validation, reference only)

**Per-Agent Context Definition:**

Every agent definition should include a section:

```markdown
## Context

### Required Reading
- Agent constitution ADR (if exists)
- [List other relevant ADRs from related_adr field]

### Skills Loaded
- {skill-1}: {purpose}
- {skill-2}: {purpose}
```

**Recommendation:** Load only relevant ADRs (from `related_adr` field), not entire ADR corpus. Reduces token cost while maintaining context precision.

---

## Validation Output Format

**Default output:** JSON validation report

```json
{
  "agent": "code-worker",
  "timestamp": "2025-12-28T21:00:00Z",
  "status": "PASS|WARN|FAIL",
  "validation_level": "L2",
  "points": [
    {
      "id": 1,
      "name": "agent_definition",
      "status": "PASS",
      "message": null
    },
    {
      "id": 2,
      "name": "model_proxy",
      "status": "PASS",
      "message": null
    },
    {
      "id": 3,
      "name": "loop_tools",
      "status": "WARN",
      "message": "Tool 'WebSearch' in ADR-1201 but omitted from agent.tools"
    },
    {
      "id": 4,
      "name": "skill_linkage",
      "status": "PASS",
      "skills_found": ["code-implementation", "test-writing"],
      "message": null
    },
    {
      "id": 5,
      "name": "skills_index",
      "status": "PASS",
      "message": null
    },
    {
      "id": 6,
      "name": "adr_registration",
      "status": "PASS",
      "adr_location": "ADR-1201:L45",
      "message": null
    },
    {
      "id": 7,
      "name": "tool_constraint",
      "status": "PASS",
      "message": null
    },
    {
      "id": 8,
      "name": "flowchart_integration",
      "status": "PASS",
      "target_flowchart": "docs/GETTING_STARTED/Workflow_Flowchart.html",
      "message": null
    },
    {
      "id": 9,
      "name": "validation_scripts",
      "status": "SKIPPED",
      "message": "L3 validation only in --strict mode"
    },
    {
      "id": 10,
      "name": "kb_context",
      "status": "PASS",
      "related_adrs": ["ADR-1201", "ADR-2001"],
      "skills_loaded": 2
    }
  ],
  "summary": {
    "passed": 9,
    "warned": 1,
    "failed": 0,
    "skipped": 1
  },
  "errors": [],
  "warnings": [
    "Tool divergence: ADR-1201 lists WebSearch but agent file omits it"
  ]
}
```

---

## Error Severity Definitions

| Level | Action | Example | Block Op? |
|-------|--------|---------|-----------|
| **FAIL** | Block operation, return error | Mismatched model/proxy, missing required frontmatter field, skill file doesn't exist, constraint inconsistency | YES |
| **WARN** | Proceed with notice, log warning | Missing optional section (KB Context), tool divergence from ADR (reference only), ADR entry not found | NO |
| **INFO** | Log information only | Style recommendations, optional improvements | NO |

---

## Related Documents

### Architecture & Constitution

- **Agent Constitution ADR** - Define roles, permissions, tools, relationships (project-specific)
- **Orchestration ADR** - Workflow structure and orchestration model (if applicable)
- **Execution Model ADR** - State and dependency model (if applicable)

### Skill Reference

- **SKILLS_INDEX.md** - Central registry of all available skills and their usage (`.claude/skills/SKILLS_INDEX.md`)

### Templates, Checklists & Learnings

Located in `.claude/skills/agent-manager/`:

```
agent-manager/
├── SKILL.md                      # This file (10-point framework)
├── templates/                    # Agent templates by type
│   ├── _base.md                  # Base template for all agents
│   ├── research-agent.md         # Research/discovery agents
│   ├── planning-agent.md         # Planning/design agents
│   ├── execution-agent.md        # Implementation agents
│   └── validation-agent.md       # QA/validation agents
├── checklists/                   # Create/update workflows
│   ├── create-agent.md           # Step-by-step creation workflow
│   └── update-agent.md           # Modification workflow
└── learnings/                    # Self-improvement knowledge base
    └── AGENT_LEARNINGS.md        # Accumulated patterns and mistakes
```

**Self-Improvement:** The `learnings/` folder is the agent-manager's memory. It reads from here before each task and writes after. Patterns that recur 3+ times get promoted to templates or checklists.

---

## Design Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| **Validation depth** | Hybrid: L0-L2 default, --strict for L0-L3 | Fast feedback loop for iteration; strict for pre-commit gates |
| **Normalization** | Report only, no auto-fix | Prevents silent unexpected changes; user retains control |
| **Flowchart automation** | Worker agent via `flowchart-designer` skill | Separation of concerns: agent-manager generates data, worker handles HTML |
| **Context loading** | Just relevant ADRs | Reduces token cost; `related_adr` field already specifies scope |
| **Template approach** | Templates with placeholders | Maintains human oversight vs full code generation |

---

## Implementation Scope

**P0 (Foundational):**
- ✅ This SKILL.md (10-point framework, invocation commands)
- ✅ `_base.md` template (enables immediate agent creation)

**P1 (Enablement):**
- ✅ Create-agent.md checklist (step-by-step guide)
- ✅ Update-agent.md checklist (modification workflow)

**P2 (Specialization):**
- ✅ Type-specific templates (genesis, p2-gauntlet, p3-worker, p4-validator)

**P3 (Automation):**
- Python validation tool for --strict mode execution
- Flowchart designer skill integration

**P4 (Self-Improvement):**
- ✅ `learnings/AGENT_LEARNINGS.md` - Knowledge base for patterns and mistakes
- ✅ **Automatic learning** built into every create/update/validate command
- ✅ Load→Execute→Record cycle (no manual step required)
- `/agent-manager promote` for promoting 3+ recurring learnings to templates/checklists

---

*Agent Manager Skill | P3 Execution | Version 1.1.0 | Last Updated: 2025-12-28*
