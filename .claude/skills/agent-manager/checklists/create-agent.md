# Create-Agent Checklist

**Purpose:** Step-by-step guide for creating a new agent with full validation coverage.

**Invocation Command:**
```bash
/agent-manager create <name> --type <template-type>
```

**Supported Templates:** `genesis`, `p2-gauntlet`, `p3-worker`, `p4-validator`, `base`

---

## SECTION 0: Pre-Flight Checks

Before starting agent creation, verify the workspace is ready:

- [ ] Git workspace is clean
  ```bash
  git status --porcelain
  ```
  If dirty, stash or abort.

- [ ] Dependencies installed
  ```bash
  python3 --version  # ≥ 3.11
  pip list | grep pydantic
  ```

- [ ] Validation scripts available
  ```bash
  ls -f scripts/kb_health_check.py  # (workspace root)
  ls -f scripts/validate_agent_variables.py  # (workspace root)
  ```

- [ ] Agent name is valid
  - Matches kebab-case (`my-agent-name`)
  - Unique across `.claude/agents/`
  - Not already in ADR-1201

---

## SECTION 1: Choose Template & Initialize

- [ ] Select appropriate template type:
  - `genesis` → P0 Genesis agents (phase initiators, gates)
  - `p2-gauntlet` → P2 review/planning agents
  - `p3-worker` → P3 execution agents
  - `p4-validator` → P4 QA/validation agents
  - `base` → Minimal starting point

- [ ] Generate agent file from template:
  ```bash
  /agent-manager create my-agent-name --type p3-worker
  ```
  Creates: `.claude/agents/my-agent-name.md`

- [ ] Verify file created:
  ```bash
  ls -f .claude/agents/my-agent-name.md
  ```

---

## SECTION 2: Point 1 - Fill in Agent Definition File

**Location:** `.claude/agents/{agent-name}.md`

### Frontmatter (REQUIRED Fields)

- [ ] **name** field (kebab-case)
  ```yaml
  name: my-agent-name
  ```

- [ ] **description** field
  - Starts with imperative verb: "Invoke when...", "Create...", "Review..."
  - Less than 100 characters
  ```yaml
  description: Invoke when executing code tasks - provides TDD-driven implementation
  ```

- [ ] **tools** field (CSV)
  - Match loop permissions from Point 3 table
  ```yaml
  tools: Read, Glob, Grep, Write, Edit, Bash
  ```

- [ ] **model** field (enum: `opus` | `pro` | `flash`)
  ```yaml
  model: flash
  ```

- [ ] **proxy** field (URL)
  - Must match model (verified in Point 2)
  ```yaml
  proxy: http://localhost:2405
  ```

- [ ] **skills** field (CSV)
  - Each skill must exist in `.claude/skills/{skill}/SKILL.md`
  ```yaml
  skills: code-implementation, test-writing, pre-flight
  ```

### Frontmatter (OPTIONAL Fields)

- [ ] **phase** field (if Genesis agent)
  - Value: `P0`, `P1`, `P2`, `P3`, or `P4`
  ```yaml
  phase: P3
  ```

- [ ] **gate(s)** field (if gatekeeper agent)
  - Suffix with `_gate`
  ```yaml
  gates: qa_gate, commit_gate
  ```

- [ ] **alias** field (if simulator)
  - Prefix with `sim-`
  ```yaml
  alias: sim-code-worker
  ```

- [ ] **patterns** field (CSV)
  - Each pattern must exist in `.claude/SSoT/Patterns/`
  ```yaml
  patterns: TDD-Pattern, Error-Handling-Pattern
  ```

- [ ] **related_adr** field (array)
  - Format: `ADR-XXXX`
  ```yaml
  related_adr:
    - ADR-1201
    - ADR-2001
    - ADR-2201
  ```

- [ ] **loop** field (inferred if absent)
  - Value: `P1`, `P2`, `P3`, `P4`, `INIT`, or `SUPPORT`
  - Auto-inferred from model/tools if not present
  ```yaml
  loop: P3
  ```

### Body Sections (REQUIRED)

- [ ] **# Agent Name** (H1 title)
  - Display name matching `name` field
  - One-line role description in blockquote

- [ ] **## Personality** (4-5 bullet traits)
  - Format: `- {Trait}: {Description}`
  ```markdown
  ## Personality
  - Literal executor: Does what spec says, not what it might mean
  - Test writer: No code ships without coverage
  - Clean coder: Leaves files better than found
  ```

- [ ] **## Philosophy** (core principle in blockquote)
  ```markdown
  ## Philosophy
  > "Atomic, Defensive, & Stateless"
  ```

- [ ] **## Protocol** (numbered workflow stages)
  - Stage 0, Stage 1, ..., Stage N
  - Each stage has clear inputs/outputs
  ```markdown
  ## Protocol

  ### Stage 0: Pre-Flight (MANDATORY)
  [Pre-flight checks]

  ### Stage 1: TDD Implementation
  [Implementation steps]
  ```

- [ ] **## Constraints** (CANNOT list)
  - Logical inverse of `tools` field (validated in Point 7)
  ```markdown
  ## Constraints
  - CANNOT: git commit (enforced by loop)
  - CANNOT: modify SSoT (design choice)
  ```

- [ ] **## State Transitions** (input/output table)
  ```markdown
  ## State Transitions

  | Input State | Output State | Condition |
  |-------------|--------------|-----------|
  | READY | IN_PROGRESS | Task started |
  | IN_PROGRESS | QA_PASSED | All tests pass |
  ```

- [ ] **## MCP Tools** (categorized tool access)
  - Group tools by category (Context, File, Execution, etc.)
  ```markdown
  ## MCP Tools

  ### Context Tools
  - `kap get-context` - Load current story/phase

  ### File Tools
  - `Read` - Load file contents
  ```

- [ ] **## Spawning Command** (at end of file)
  - Shows how to invoke agent
  ```markdown
  ## Spawning Command

  \`\`\`bash
  ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "task"
  \`\`\`
  ```

- [ ] **Footer** (agent metadata)
  ```markdown
  ---

  *Code Worker | P3 | Last Updated: 2025-12-28*
  ```

---

## SECTION 3: Point 2 - Verify Model-Proxy Alignment

**Validation Rule:** Model and proxy MUST match.

| Model | Port | Proxy URL |
|-------|------|-----------|
| `flash` | 2405 | `http://localhost:2405` |
| `pro` | 2406 | `http://localhost:2406` |
| `opus` | 2408 | `http://localhost:2408` |

- [ ] Extract `model` from frontmatter
- [ ] Extract `proxy` from frontmatter
- [ ] Verify alignment:
  ```python
  model_to_proxy = {
    "flash": "http://localhost:2405",
    "pro": "http://localhost:2406",
    "opus": "http://localhost:2408"
  }

  if proxy != model_to_proxy[model]:
    FAIL: "Model/proxy mismatch"
  ```

**Validation Result:**
- [ ] ✅ **PASS** - Model and proxy aligned
- [ ] ❌ **FAIL** - Mismatch (fix before proceeding)

---

## SECTION 4: Point 3 - Verify Loop-Tool Permissions

**Validation Rule:** Tools must align with loop permissions.

**Permission Matrix:**

| Tool | P1 | P2 | P3 | P4 | INIT | SUPPORT |
|------|:--:|:--:|:--:|:--:|:----:|:-------:|
| Read | Y | Y | Y | Y | Y | Y |
| Glob | Y | Y | Y | Y | Y | Y |
| Grep | Y | Y | Y | Y | Y | Y |
| Write | x | Y | Y | x | Y | Y |
| Edit | x | Y | Y | x | Y | Y |
| Bash | x | x | Y | Y | x | Y |
| LSP | x | Y | Y | x | Y | Y |
| git | x | x | x | Y | x | Y |
| WebSearch | Y | x | Y* | x | Y | Y |
| WebFetch | x | x | Y* | x | Y | Y |

*P3: Research Scout only

- [ ] Infer agent loop:
  - From `loop` field in frontmatter, OR
  - From `model` + tools combination

- [ ] Extract tools from `tools` field
  ```yaml
  tools: Read, Glob, Grep, Write, Edit, Bash
  ```

- [ ] Validate against permission matrix:
  - For each tool, check if loop permits it
  - If tool not permitted, log **WARN**

**Validation Result:**
- [ ] ✅ **PASS** - All tools permitted for loop
- [ ] ⚠️ **WARN** - Tool divergence detected (proceed with notice)
  - User must manually reconcile

---

## SECTION 5: Point 4 - Link Skills Bidirectionally

**Validation Rule:** Bidirectional linkage required.

### Forward Validation (Agent → Skills)

- [ ] Extract `skills` from frontmatter
  ```yaml
  skills: code-implementation, test-writing, pre-flight
  ```

- [ ] For each skill, verify file exists:
  ```bash
  ls .claude/skills/{skill}/SKILL.md
  ```

- [ ] If skill doesn't exist:
  - ❌ **FAIL** - Block agent creation

### Reverse Validation (Skills → Agent)

- [ ] For each skill file, open `SKILL.md`
  ```bash
  cat .claude/skills/{skill}/SKILL.md | grep "used_by"
  ```

- [ ] Add agent name to `used_by` field:
  ```yaml
  used_by: code-worker, other-agent, new-agent
  ```

- [ ] Maintain alphabetical order in `used_by`

**Validation Result:**
- [ ] ✅ **PASS** - All skills exist and bidirectional links created
- [ ] ❌ **FAIL** - Missing skill file (fix before proceeding)

---

## SECTION 6: Point 5 - Update SKILLS_INDEX.md

**Location:** `.claude/skills/SKILLS_INDEX.md`

- [ ] Open the index file:
  ```bash
  cat .claude/skills/SKILLS_INDEX.md
  ```

- [ ] For each skill referenced by agent:
  - Check if skill row exists in index
  - If new skill, add row

- [ ] Update `used_by` column for modified skills:
  ```markdown
  | [code-implementation](code-implementation/SKILL.md) | Execution | code-worker, other-agent, new-agent |
  ```

- [ ] Maintain table formatting:
  - Alphabetical order by skill name
  - CSV format in `used_by` column
  - Hyperlinks to skill SKILL.md files

**Validation Result:**
- [ ] ✅ **PASS** - Skills Index updated
- [ ] ❌ **FAIL** - Index entry missing (fix before proceeding)

---

## SECTION 7: Point 6 - Register in ADR-1201

**Location:** `.claude/PM/SSoT/ADRs/1201-functional-agent-roster.md`

### Bidirectional Validation

- [ ] Extract agent name (from frontmatter)
- [ ] Extract loop (from frontmatter or inferred)
- [ ] Open ADR-1201 and locate loop table (P1, P2, P3, P4, INIT, SUPPORT)
- [ ] Check if agent name appears in table:
  - **If yes:** Agent already registered ✅
  - **If no:** Add agent to appropriate table

### Adding New Agent to ADR-1201

- [ ] Find the correct loop section (P3, etc.)
- [ ] Locate the agent roster table
- [ ] Add row with agent details:
  ```markdown
  | code-worker | P3 | Execution | code-implementation, test-writing | TDD, atomic tasks |
  ```

- [ ] Update other fields as needed:
  - Signature (S), Proxy (P), Model (M) columns
  - Maintain consistent formatting

- [ ] Verify no orphan agents:
  ```python
  agent_files = glob(".claude/agents/*.md")
  adr_agents = parse_adr_1201_roster_tables()

  orphan_agents = agent_files - adr_agents
  if orphan_agents:
    WARN: f"Agent files without ADR entry: {orphan_agents}"
  ```

**Validation Result:**
- [ ] ✅ **PASS** - Agent registered in ADR-1201
- [ ] ⚠️ **WARN** - Orphan agents detected (fix before commit)
- [ ] ❌ **FAIL** - ADR entries without files (fix before proceeding)

---

## SECTION 8: Point 7 - Ensure Tool-Constraint Consistency

**Validation Rule:** Constraints section must be logical inverse of tools field.

```
IF "Write" NOT IN tools THEN "CANNOT use Write" MUST be in Constraints
IF "Bash" IN tools THEN "CANNOT use Bash" MUST NOT be in Constraints
```

### Standard Constraints by Loop

| Loop | Required Constraints |
|------|---------------------|
| P1 | CANNOT: Write, Edit, Bash, git commit, modify SSoT |
| P2 | CANNOT: Bash, git commit, talk to user, modify SSoT |
| P3 | CANNOT: git commit, modify SSoT, self-approve |
| P4 | CANNOT: Write, Edit (fix bugs directly), modify SSoT |
| INIT | CANNOT: git commit, modify SSoT |
| SUPPORT | CANNOT: modify SSoT |

### Validation Steps

- [ ] Extract `tools` field:
  ```yaml
  tools: Read, Glob, Grep, Write, Edit, Bash
  ```

- [ ] Extract `Constraints` section:
  ```markdown
  ## Constraints

  - CANNOT: git commit
  - CANNOT: modify SSoT
  ```

- [ ] For each tool NOT in tools list:
  - Check if "CANNOT use {tool}" appears in Constraints
  - If absent, log **WARN**

- [ ] For each tool IN tools list:
  - Check if "CANNOT use {tool}" appears in Constraints
  - If present, log **FAIL** (contradiction)

**Validation Result:**
- [ ] ✅ **PASS** - Constraints correctly reflect tool exclusions
- [ ] ⚠️ **WARN** - Missing recommended constraint (fix for robustness)
- [ ] ❌ **FAIL** - Constraint contradicts tools (fix before proceeding)

---

## SECTION 9: Point 8 - Generate Flowchart Payload

**IMPORTANT:** Flowchart updates are NOT performed by agent-manager directly. Instead:
1. Generate JSON payload with agent node data
2. Spawn worker via `flowchart-designer` skill
3. Worker integrates node into appropriate flowchart

### Payload Generation

- [ ] Extract agent metadata:
  - name, description, model, proxy, tools, skills, loop

- [ ] Generate node JSON payload:
  ```json
  {
    "agent": "code-worker",
    "operation": "create",
    "target_flowchart": "docs/GETTING_STARTED/Workflow_Flowchart.html",
    "node_data": {
      "id": "code-worker",
      "label": "Code Worker",
      "loop": "P3",
      "model": "flash",
      "proxy": "2405",
      "tools": ["Read", "Glob", "Grep", "Write", "Edit", "Bash"],
      "skills": ["code-implementation", "test-writing", "pre-flight"],
      "triggers": ["task.status = ready"],
      "outputs": ["task.status = qa_passed | blocked"]
    }
  }
  ```

- [ ] Identify target flowchart:
  - P1-P4 agents → `docs/GETTING_STARTED/Workflow_Flowchart.html`
  - INIT agents → `docs/GETTING_STARTED/FC_Assets/Flowchart_INIT.html`
  - SUPPORT agents → `docs/GETTING_STARTED/FC_Assets/Flowchart_SUPPORT.html`

### Spawning Flowchart Worker

- [ ] Save payload to temp file:
  ```bash
  cat > /tmp/agent_node.json << 'EOF'
  {payload}
  EOF
  ```

- [ ] Spawn flowchart-designer worker:
  ```bash
  ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "
  /flowchart-designer

  OPERATION: create
  TARGET: docs/GETTING_STARTED/Workflow_Flowchart.html
  PAYLOAD: [Read payload from /tmp/agent_node.json]
  "
  ```

**Validation Result:**
- [ ] ✅ **PASS** - Payload generated and worker spawned
- [ ] ⚠️ **WARN** - Worker returned warnings (review before commit)
- [ ] ❌ **FAIL** - Worker reported errors (fix before proceeding)

---

## SECTION 10: Point 9 - Run Validation Scripts

**IMPORTANT:** This step is MANDATORY only in `--strict` mode for commits.
In standard mode, this is informational.

### Validation Scripts

| Script | Location | Purpose |
|--------|----------|---------|
| `kb_health_check.py` | `scripts/` (workspace root) | Cross-reference validation |
| `validate_agent_variables.py` | `scripts/` (workspace root) | Variable consistency |
| `layer_validator.py` | `scripts/` (workspace root) | Layer hierarchy |

### Execution

- [ ] Run kb_health_check:
  ```bash
  python3 scripts/kb_health_check.py
  ```
  Expected exit code: `0`

- [ ] Run agent variable validator:
  ```bash
  python3 scripts/validate_agent_variables.py --check-all
  ```
  Expected exit code: `0`

- [ ] Run layer validator:
  ```bash
  python3 scripts/layer_validator.py
  ```
  Expected exit code: `0`

- [ ] If any script returns non-zero:
  - Review error output
  - Fix issues (typically in ADR-1201, Skills Index, or agent file)
  - Re-run scripts until all pass

**Validation Result:**
- [ ] ✅ **PASS** - All scripts exit 0 (ready for commit)
- [ ] ❌ **FAIL** - One or more scripts failed (fix before commit)

---

## SECTION 11: Point 10 - Add KB Context Section

**Purpose:** Define dynamic KB context for agent initialization.

**Recommendation:** Load only relevant ADRs (from `related_adr` field), not all ADRs.

### KB Context Section

- [ ] Add section to agent file (before footer):
  ```markdown
  ## KB Context

  ### Required Reading
  - ADR-1201: Functional Agent Roster (constitution)
  - ADR-2001: Graph-Driven Execution
  - ADR-2201: Quad-Loop Orchestration

  ### Skills Loaded
  - code-implementation: TDD-driven code implementation
  - test-writing: Test methodology and patterns
  - pre-flight: Pre-flight checks and validation
  ```

- [ ] Reference `related_adr` field:
  - Use ADRs listed in frontmatter
  - Add ADR-1201 always (constitution)
  - Keep list concise (3-5 ADRs maximum)

- [ ] Reference `skills` field:
  - List each skill from frontmatter
  - Add one-line purpose for each skill
  - Keep descriptions brief

**Validation Result:**
- [ ] ✅ **PASS** - KB Context section added and relevant

---

## SECTION 12: Post-Creation Validation Command

**Run after all 10 points completed:**

```bash
/agent-manager validate my-agent-name
```

**Expected Output (L2 validation - default):**

```json
{
  "agent": "my-agent-name",
  "timestamp": "2025-12-28T21:00:00Z",
  "status": "PASS",
  "level": "L2",
  "points": [
    {"id": 1, "name": "agent_definition", "status": "PASS"},
    {"id": 2, "name": "model_proxy", "status": "PASS"},
    {"id": 3, "name": "loop_tools", "status": "PASS"},
    {"id": 4, "name": "skill_linkage", "status": "PASS"},
    {"id": 5, "name": "skills_index", "status": "PASS"},
    {"id": 6, "name": "adr_1201_registration", "status": "PASS"},
    {"id": 7, "name": "tool_constraint_consistency", "status": "PASS"},
    {"id": 8, "name": "flowchart_payload", "status": "PASS"},
    {"id": 9, "name": "validation_scripts", "status": "SKIPPED"},
    {"id": 10, "name": "kb_context", "status": "PASS"}
  ],
  "errors": [],
  "warnings": []
}
```

### Strict Validation (for commits)

```bash
/agent-manager validate my-agent-name --strict
```

This adds L3 validation:
- Runs all validation scripts
- Requires exit code 0 for all
- Blocks validation if scripts fail

---

## SECTION 13: Common Mistakes to Avoid

| Mistake | Why Bad | Fix |
|---------|---------|-----|
| **Model/proxy mismatch** | Agent won't spawn at correct port | Verify Point 2 table during frontmatter fill |
| **Missing skill file** | Bidirectional link breaks | Check `.claude/skills/{skill}/SKILL.md` exists |
| **Constraints contradict tools** | Confusing developer, could allow forbidden operations | Review Point 7 validation matrix |
| **Tool not in loop permissions** | Agent spawns with incorrect capability | Use Point 3 matrix to validate tools for loop |
| **Agent not in ADR-1201** | Orphan agent, missing from roster | Manually add row to ADR-1201 if validation warns |
| **Skills Index not updated** | Discovery tools won't find agent-skill relationships | Update `used_by` column in SKILLS_INDEX.md |
| **Flowchart worker not spawned** | Visual flowchart out of sync with agent roster | Use provided spawning command in Point 8 |
| **Validation scripts skipped** | Broken cross-references not caught | Run scripts in Point 9 before commit |
| **KB Context missing** | Agent lacks context for initialization | Add Section 11 before footer |
| **Inconsistent frontmatter** | Schema validation fails | Verify all REQUIRED fields present; validate YAML |

---

## Checklist Summary

**Total Items:** 87 checkboxes

**By Section:**
- Pre-Flight: 4 items
- Section 1 (Template): 3 items
- Section 2 (Point 1): 21 items
- Section 3 (Point 2): 3 items
- Section 4 (Point 3): 4 items
- Section 5 (Point 4): 5 items
- Section 6 (Point 5): 4 items
- Section 7 (Point 6): 5 items
- Section 8 (Point 7): 6 items
- Section 9 (Point 8): 6 items
- Section 10 (Point 9): 5 items
- Section 11 (Point 10): 4 items
- Section 12 (Validation): 3 items
- Common Mistakes: Reference only

---

## Integration with SKILL.md

This checklist is invoked by `/agent-manager create <name>` command. See `SKILL.md` for:
- Full 10-point framework
- Validation levels (L0-L3)
- Error severity definitions
- Design decisions and rationale

---

*Create-Agent Checklist V1.0.0 | Agent Manager Skill | Last Updated: 2025-12-28*
