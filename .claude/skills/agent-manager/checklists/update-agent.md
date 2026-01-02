# Update-Agent Checklist

**Purpose:** Step-by-step guide for modifying an existing agent with full validation coverage.

**Invocation Commands:**
```bash
# Step 1: Validate before making changes
/agent-manager validate <name>

# Step 2: Make changes to the agent file
# (Edit .claude/agents/<name>.md directly)

# Step 3: Validate after changes
/agent-manager update <name>
```

---

## SECTION 0: Pre-Flight Checks

Before starting agent modifications, verify the workspace is ready:

- [ ] Git workspace is clean
  ```bash
  git status --porcelain
  ```
  If dirty, stash or abort.

- [ ] Current agent state is validated
  ```bash
  /agent-manager validate <agent-name>
  ```
  Review any warnings before proceeding.

- [ ] Agent file exists
  ```bash
  ls -f .claude/agents/<agent-name>.md
  ```

- [ ] Backup of original file
  - Keep mental note of original state for comparison
  - Optional: Copy file for manual diffing

---

## SECTION 1: Choose Update Scenario

Identify which update scenario applies to your change:

- [ ] **Scenario A: Adding/Removing a Tool**
  - Affected Points: 1, 3, 7
  - Affects: frontmatter, loop permissions, constraints
  - Go to Section A

- [ ] **Scenario B: Changing the Model**
  - Affected Points: 1, 2
  - Affects: frontmatter, proxy alignment
  - Go to Section B

- [ ] **Scenario C: Adding/Removing a Skill**
  - Affected Points: 1, 4, 5
  - Affects: frontmatter, bidirectional links, skills index
  - Go to Section C

- [ ] **Scenario D: Changing Loop Assignment**
  - Affected Points: 3, 6, 8
  - Affects: tool permissions, ADR-1201, flowchart
  - Go to Section D

- [ ] **Scenario E: Modifying Constraints**
  - Affected Points: 1, 7
  - Affects: frontmatter, tool-constraint consistency
  - Go to Section E

- [ ] **Scenario F: Multiple Changes**
  - Combine relevant sections below
  - Example: Adding skill + changing loop = Sections C + D

---

## SECTION A: Scenario - Adding/Removing a Tool

**Affected Points:** 1, 3, 7

### A1: Point 1 - Update Agent Definition File

**Location:** `.claude/agents/{agent-name}.md`

- [ ] Open the agent file
  ```bash
  cat .claude/agents/<agent-name>.md
  ```

- [ ] **If ADDING a tool:**
  - Add tool to `tools` field (CSV list)
  - Maintain alphabetical order
  - Example: `tools: Read, Glob, Grep, Write, Edit, Bash`

- [ ] **If REMOVING a tool:**
  - Remove tool from `tools` field
  - Ensure remaining tools still valid for loop (see Point 3)

### A2: Point 3 - Verify Loop-Tool Permissions

**Validation Rule:** New/removed tool must be permitted for agent's loop.

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

- [ ] Identify agent's loop (from `loop` field or inferred)

- [ ] **If ADDING a tool:**
  - Check if tool is permitted for loop
  - If not permitted: STOP - tool not allowed in this loop
  - If permitted: Proceed to A3

- [ ] **If REMOVING a tool:**
  - No loop validation needed (removing fewer restrictions)
  - Proceed to A3

- [ ] Validation Result:
  - [ ] ✅ **PASS** - Tool change valid for loop
  - [ ] ❌ **FAIL** - Tool not permitted (revert change, re-plan)

### A3: Point 7 - Update Tool-Constraint Consistency

**Validation Rule:** Constraints section must be logical inverse of tools field.

```
IF "Write" NOT IN tools THEN "CANNOT use Write" MUST be in Constraints
IF "Bash" IN tools THEN "CANNOT use Bash" MUST NOT be in Constraints
```

- [ ] Extract updated `tools` field

- [ ] Locate `## Constraints` section in agent file

- [ ] **If ADDING a tool:**
  - Review Constraints section
  - Remove any "CANNOT use {tool}" statement if present
  - Maintain other constraints unchanged
  - Example: Remove "CANNOT use Write" if adding Write tool

- [ ] **If REMOVING a tool:**
  - Add corresponding "CANNOT use {tool}" statement
  - Follow loop-specific constraint patterns
  - Example: Add "CANNOT use Bash" if removing Bash tool

- [ ] Standard Constraints by Loop:

| Loop | Required Constraints |
|------|---------------------|
| P1 | CANNOT: Write, Edit, Bash, git commit, modify SSoT |
| P2 | CANNOT: Bash, git commit, talk to user, modify SSoT |
| P3 | CANNOT: git commit, modify SSoT, self-approve |
| P4 | CANNOT: Write, Edit (fix bugs directly), modify SSoT |
| INIT | CANNOT: git commit, modify SSoT |
| SUPPORT | CANNOT: modify SSoT |

- [ ] Validation Result:
  - [ ] ✅ **PASS** - Constraints correctly reflect tool changes
  - [ ] ❌ **FAIL** - Constraint contradicts tools (fix before proceeding)

---

## SECTION B: Scenario - Changing the Model

**Affected Points:** 1, 2

### B1: Point 1 - Update Frontmatter

**Location:** `.claude/agents/{agent-name}.md`

- [ ] Open the agent file

- [ ] Locate `model` field in frontmatter:
  ```yaml
  model: flash
  ```

- [ ] Update `model` to new value:
  - Valid values: `opus` | `pro` | `flash`
  - Example: Change from `flash` to `pro`

### B2: Point 2 - Update Proxy Alignment

**Validation Rule:** Model and proxy MUST match.

| Model | Port | Proxy URL |
|-------|------|-----------|
| `flash` | 2405 | `http://localhost:2405` |
| `pro` | 2406 | `http://localhost:2406` |
| `opus` | 2408 | `http://localhost:2408` |

- [ ] Locate `proxy` field in frontmatter:
  ```yaml
  proxy: http://localhost:2405
  ```

- [ ] Update `proxy` to match new model:
  - If model is `flash` → proxy: `http://localhost:2405`
  - If model is `pro` → proxy: `http://localhost:2406`
  - If model is `opus` → proxy: `http://localhost:2408`

- [ ] Validation Result:
  - [ ] ✅ **PASS** - Model and proxy aligned
  - [ ] ❌ **FAIL** - Mismatch (fix before proceeding)

---

## SECTION C: Scenario - Adding/Removing a Skill

**Affected Points:** 1, 4, 5

### C1: Point 1 - Update Agent Definition File

**Location:** `.claude/agents/{agent-name}.md`

- [ ] Open the agent file

- [ ] Locate `skills` field in frontmatter:
  ```yaml
  skills: code-implementation, test-writing, pre-flight
  ```

- [ ] **If ADDING a skill:**
  - Add skill name to `skills` field (CSV list)
  - Maintain alphabetical order
  - Example: `skills: code-implementation, new-skill, pre-flight, test-writing`

- [ ] **If REMOVING a skill:**
  - Remove skill name from `skills` field
  - Maintain alphabetical order in remaining list

### C2: Point 4 - Update Bidirectional Skill Links

**Forward Validation (Agent → Skills):**

- [ ] **If ADDING a skill:**
  - Verify skill file exists:
    ```bash
    ls .claude/skills/{skill}/SKILL.md
    ```
  - If skill doesn't exist: STOP - skill not found, revert change
  - If exists: Proceed to reverse validation

**Reverse Validation (Skills → Agent):**

- [ ] Open the skill's SKILL.md file:
  ```bash
  cat .claude/skills/{skill}/SKILL.md | grep "used_by"
  ```

- [ ] **If ADDING a skill:**
  - Locate `used_by` field in skill file
  - Add agent name to the CSV list
  - Maintain alphabetical order
  - Example: `used_by: code-worker, new-agent, other-agent`
  - Edit the skill file to update `used_by`

- [ ] **If REMOVING a skill:**
  - Locate `used_by` field in skill file
  - Remove agent name from CSV list
  - Edit the skill file to update `used_by`

- [ ] Validation Result:
  - [ ] ✅ **PASS** - All skills exist and bidirectional links updated
  - [ ] ❌ **FAIL** - Missing skill file (revert change)

### C3: Point 5 - Update SKILLS_INDEX.md

**Location:** `.claude/skills/SKILLS_INDEX.md`

- [ ] Open the skills index file:
  ```bash
  cat .claude/skills/SKILLS_INDEX.md
  ```

- [ ] **If ADDING a skill:**
  - Locate the skill's row in the index table
  - Update `used_by` column with agent name
  - Maintain alphabetical order in `used_by` list
  - Example: `code-worker, new-agent, other-agent`

- [ ] **If REMOVING a skill:**
  - Locate the agent name in skill's `used_by` column
  - Remove agent name from CSV list
  - Maintain formatting

- [ ] Validation Result:
  - [ ] ✅ **PASS** - Skills Index updated
  - [ ] ❌ **FAIL** - Index entry missing (fix before proceeding)

---

## SECTION D: Scenario - Changing Loop Assignment

**Affected Points:** 3, 6, 8

### D1: Point 3 - Verify Tool Permissions for New Loop

**Validation Rule:** All tools must be permitted for new loop.

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

- [ ] Extract agent's current tools:
  ```yaml
  tools: Read, Glob, Grep, Write, Edit
  ```

- [ ] Identify new loop assignment (from plan or decision)

- [ ] Validate each tool against new loop:
  - For each tool, check if new loop permits it
  - If any tool NOT permitted: STOP - replan required
  - If all tools permitted: Proceed to D2

- [ ] Validation Result:
  - [ ] ✅ **PASS** - All tools permitted for new loop
  - [ ] ❌ **FAIL** - Tool divergence (replan with different tools)

### D2: Point 6 - Update ADR-1201 Registration

**Location:** `.claude/PM/SSoT/ADRs/1201-functional-agent-roster.md`

- [ ] Open ADR-1201:
  ```bash
  cat .claude/PM/SSoT/ADRs/1201-functional-agent-roster.md
  ```

- [ ] Locate agent's row in current loop table:
  - Find the agent in P1, P2, P3, P4, INIT, or SUPPORT roster
  - Identify the full row

- [ ] **If changing loop:**
  - Remove agent row from old loop table
  - Add agent row to new loop table
  - Maintain consistent formatting and columns

- [ ] Update all affected columns:
  - Name, Model (M), Proxy (P), Signature (S), Skills
  - Keep other ADR content unchanged

- [ ] Validation Result:
  - [ ] ✅ **PASS** - Agent registered in correct loop
  - [ ] ❌ **FAIL** - Registration error (fix ADR-1201)

### D3: Point 8 - Generate Flowchart Payload (Update Operation)

**IMPORTANT:** Flowchart updates are performed by a worker agent via `flowchart-designer` skill.

### Payload Generation

- [ ] Extract updated agent metadata:
  - name, description, model, proxy, tools, skills, loop

- [ ] Identify target flowchart based on NEW loop:
  - P1-P4 agents → `docs/GETTING_STARTED/Workflow_Flowchart.html`
  - INIT agents → `docs/GETTING_STARTED/FC_Assets/Flowchart_INIT.html`
  - SUPPORT agents → `docs/GETTING_STARTED/FC_Assets/Flowchart_SUPPORT.html`

- [ ] **If loop changed:**
  - Generate UPDATE payload with operation: `"update"`
  - Include both old and new loop for worker reference

- [ ] Generate node JSON payload:
  ```json
  {
    "agent": "code-worker",
    "operation": "update",
    "old_loop": "P2",
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

- [ ] Spawn flowchart-designer worker:
  ```bash
  ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "
  /flowchart-designer

  OPERATION: update
  TARGET: docs/GETTING_STARTED/Workflow_Flowchart.html
  PAYLOAD: [JSON payload]
  "
  ```

- [ ] Validation Result:
  - [ ] ✅ **PASS** - Payload generated and worker spawned
  - [ ] ⚠️ **WARN** - Worker returned warnings (review before commit)
  - [ ] ❌ **FAIL** - Worker reported errors (fix before proceeding)

---

## SECTION E: Scenario - Modifying Constraints

**Affected Points:** 1, 7

### E1: Point 1 - Agent Definition File

**Location:** `.claude/agents/{agent-name}.md`

- [ ] No changes needed to frontmatter for this scenario
  - Constraints are NOT in frontmatter
  - They live in the `## Constraints` section of agent body

- [ ] Proceed directly to E2

### E2: Point 7 - Update Tool-Constraint Consistency

**Validation Rule:** Constraints section must be logical inverse of tools field.

- [ ] Extract agent's `tools` field:
  ```yaml
  tools: Read, Glob, Grep, Write, Edit, Bash
  ```

- [ ] Locate `## Constraints` section in agent file

- [ ] Review existing constraints and decide on changes

- [ ] Standard Constraints by Loop (reference):

| Loop | Required Constraints |
|------|---------------------|
| P1 | CANNOT: Write, Edit, Bash, git commit, modify SSoT |
| P2 | CANNOT: Bash, git commit, talk to user, modify SSoT |
| P3 | CANNOT: git commit, modify SSoT, self-approve |
| P4 | CANNOT: Write, Edit (fix bugs directly), modify SSoT |
| INIT | CANNOT: git commit, modify SSoT |
| SUPPORT | CANNOT: modify SSoT |

- [ ] **Validation:**
  - For each tool NOT in tools list: Must have corresponding "CANNOT" constraint
  - For each tool IN tools list: Must NOT have "CANNOT use {tool}" constraint
  - Design choice constraints (non-tool) are optional

- [ ] **When modifying constraints:**
  - Do NOT add constraint that contradicts tools
  - Do NOT remove required constraint from loop pattern
  - Maintain logical consistency

- [ ] Validation Result:
  - [ ] ✅ **PASS** - Constraints logically consistent
  - [ ] ❌ **FAIL** - Constraint contradicts tools (fix before proceeding)

---

## SECTION 2: Post-Update Validation Command

**Run after ALL relevant scenario sections completed:**

```bash
/agent-manager update <agent-name>
```

**Expected Output (L2 validation - default):**

The validator checks all 10 points and reports status:

```json
{
  "agent": "code-worker",
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

- [ ] Validation Result:
  - [ ] ✅ **PASS** - All points validated successfully
  - [ ] ⚠️ **WARN** - Review warnings before commit
  - [ ] ❌ **FAIL** - Fix errors before proceeding

### Strict Validation (for commits)

```bash
/agent-manager update <agent-name> --strict
```

This adds L3 validation (validation scripts). Requires all scripts to exit 0.

---

## SECTION 3: Diff Command - Compare with ADR-1201

**After validation passes, review changes:**

```bash
/agent-manager diff <agent-name>
```

**Output includes:**

- Agent file state vs ADR-1201 state
- Identifies discrepancies in:
  - Model, proxy, tools, skills
  - Loop assignment
  - Constraint definitions
  - Registration status

- [ ] Review diff output for accuracy:
  - [ ] All changes intentional
  - [ ] No unintended modifications
  - [ ] Diff shows expected deltas only

---

## SECTION 4: Common Mistakes During Update

| Mistake | Why Bad | Fix |
|---------|---------|-----|
| **Changing model but not proxy** | Agent won't spawn at correct port | Update both together (Point 2) |
| **Adding tool not permitted for loop** | Agent gets invalid capability | Validate against permission matrix (Point 3) |
| **Not updating bidirectional skill links** | Relationship breaks, discovery fails | Update both agent and skill files (Point 4) |
| **Forgetting to update Skills Index** | Index out of sync | Manually update SKILLS_INDEX.md (Point 5) |
| **Not updating ADR-1201** | Orphan agent, roster out of sync | Add/move agent row in ADR-1201 (Point 6) |
| **Constraints contradict tools** | Confusing developer | Review Point 7 matrix |
| **Flowchart worker not spawned** | Visual flowchart out of sync | Use provided command in D3 |
| **Running validate instead of update** | May skip relevant checks | Use `/agent-manager update` for changes |
| **Not running validation after changes** | Silent errors not caught | Always run final validation command |
| **Removing required loop constraint** | Agent behavior undefined | Maintain standard constraints from loop pattern |

---

## SECTION 5: Scenario Quick-Reference

**Quick lookup for which sections to follow:**

| Update Type | Go to Section |
|-------------|---------------|
| Add/remove a tool | A |
| Change model | B |
| Add/remove a skill | C |
| Change loop | D |
| Modify constraints | E |
| Add tool + update constraints | A + E |
| Add skill + change loop | C + D |
| Change model + loop | B + D |
| Multiple changes | Combine relevant sections |

---

## SECTION 6: Pre-Commit Checklist

Before committing your agent update:

- [ ] All relevant scenario sections completed
- [ ] `/agent-manager update <name>` returns PASS status
- [ ] No validation errors or unresolved warnings
- [ ] Changes match original intent (no accidental edits)
- [ ] Affected files modified:
  - [ ] Agent file: `.claude/agents/<name>.md`
  - [ ] Skill files: Any bidirectional link changes (Point 4)
  - [ ] Skills Index: If skills changed (Point 5)
  - [ ] ADR-1201: If loop changed (Point 6)
  - [ ] Flowchart: Worker agent handles (Point 8)

- [ ] Run validation one more time:
  ```bash
  /agent-manager update <name> --strict
  ```

- [ ] All validation scripts exit 0 (if using --strict)

---

## Integration with SKILL.md

This checklist is invoked by `/agent-manager update <name>` command. See `SKILL.md` for:
- Full 10-point framework overview
- Validation levels (L0-L3)
- Error severity definitions
- Design decisions and rationale

---

*Update-Agent Checklist V1.0.0 | Agent Manager Skill | Last Updated: 2025-12-28*
