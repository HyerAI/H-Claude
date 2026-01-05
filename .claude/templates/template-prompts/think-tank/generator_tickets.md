# Generator: Sub-Task Tickets

> Converts Task Plan items into atomic, executable Tickets with triangulated context.

---

## Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{SESSION_PATH}}` | Think-tank session folder | `.claude/PM/think-tank/auth_20260103/` |
| `{{TASK_PLAN_PATH}}` | Path to Task Plan YAML | `{{SESSION_PATH}}/task_plan.yaml` |

---

## Agent Instructions

You are a Ticket Generator agent. Your job is to decompose Task Plan items into atomic tickets that workers can execute deterministically.

### Step 1: Read Context

```
Read {{TASK_PLAN_PATH}}
Read .claude/templates/think-tank/TICKET_SCHEMA.md
```

Extract from Task Plan:
- `phase_id` and `task_id` for traceability
- Each task's `goal`, `scope`, and `acceptance_criteria`
- Any `dependencies` between tasks

### Step 2: Generate Tickets

For EACH task in the Task Plan, create one or more tickets:

**Triangulated Context Requirements:**

| Field | Source | Purpose |
|-------|--------|---------|
| `goal` | Task Plan → Phase → NORTHSTAR | WHY this matters |
| `bedrock[]` | Codebase analysis | WHAT to read first |
| `instruction` | Task decomposition | HOW to execute |

**Ticket Creation Process:**

1. **Analyze Task Scope**
   - How many files are affected?
   - Can a single worker complete this atomically?
   - Are there natural breakpoints?

2. **Identify Bedrock Files**
   - Use Glob/Grep to find relevant source files
   - Include interfaces, types, existing implementations
   - Add relevant ADRs or documentation
   - Each bedrock entry needs `path` + `relevance`

3. **Write Clear Instructions**
   - Unambiguous: only one interpretation possible
   - Actionable: starts with a verb
   - Scoped: worker knows exactly where to work

4. **Define Acceptance Criteria**
   - Observable outcomes (not process)
   - Testable conditions
   - Include validation commands where applicable

### Step 3: Resolution Check

Before finalizing each ticket, validate:

```
┌─────────────────────────────────────────────────────────┐
│ RESOLUTION CHECK - Is this ticket ready for execution?  │
├─────────────────────────────────────────────────────────┤
│ □ Single Worker: Can one agent complete this alone?     │
│ □ Deterministic: Would two workers produce same result? │
│ □ Bedrock Sufficient: Is context complete for the task? │
│ □ Clear Acceptance: Can we objectively verify "done"?   │
│ □ Scope Bounded: ≤5 files, ≤100 lines estimated?        │
└─────────────────────────────────────────────────────────┘
```

**If any check fails:**
- Too broad → Split into multiple tickets
- Ambiguous → Rewrite instruction with specifics
- Missing context → Add bedrock files
- Vague acceptance → Define observable outcomes

### Step 4: Write Output

Create ticket files in `{{SESSION_PATH}}/tickets/`:

```
{{SESSION_PATH}}/
├── task_plan.yaml          # Input
└── tickets/                 # Output
    ├── TKT-YYYYMMDD-001.yaml
    ├── TKT-YYYYMMDD-002.yaml
    └── ...
```

**Naming Convention:** `TKT-{date}-{sequence}` (e.g., `TKT-20260103-001`)

---

## Output Format

Each ticket file follows TICKET_SCHEMA.md:

```yaml
ticket_id: TKT-YYYYMMDD-NNN
task_id: TASK-XXX

status: pending

triangulated_context:
  goal: |
    # Trace back to NS/Phase goal
    # Answer: "Why does this matter to the user?"

  bedrock:
    - path: <file_path>
      relevance: "<why worker needs this>"
    - path: <file_path>
      relevance: "<why worker needs this>"

  instruction: |
    # Specific, unambiguous action
    # One clear interpretation only

acceptance_criteria:
  - "<observable outcome 1>"
  - "<observable outcome 2>"

complexity: simple | medium | complex

estimated_scope:
  files_affected: N
  lines_estimated: N

validation:
  - type: test | lint | build | manual
    command: "<validation command>"  # or description for manual

dependencies:
  - TKT-YYYYMMDD-NNN  # if any

notes: |
```

---

## Complexity Guidelines

| Complexity | Files | Lines | Ticket Count per Task |
|------------|-------|-------|----------------------|
| simple | 1 | <50 | Usually 1 ticket |
| medium | 2-3 | 50-100 | 1-2 tickets |
| complex | 4-5 | 100+ | 2-3+ tickets (split!) |

**Rule:** If a task would produce a `complex` ticket affecting >5 files, it MUST be split.

---

## Example Transformation

**Input Task (from Task Plan):**
```yaml
- id: TASK-002
  title: "Implement session persistence"
  goal: "Enable user sessions to survive page refresh"
  scope:
    files: ["src/services/auth.ts", "src/types/session.d.ts"]
  acceptance_criteria:
    - "Session restored on refresh"
    - "Logout clears persisted data"
```

**Output Tickets:**

`tickets/TKT-20260103-001.yaml`:
```yaml
ticket_id: TKT-20260103-001
task_id: TASK-002

status: pending

triangulated_context:
  goal: |
    Enable session persistence so users don't lose their
    authenticated state on page refresh (NS: Seamless UX).

  bedrock:
    - path: src/services/auth.ts
      relevance: "Current SessionManager implementation"
    - path: src/types/session.d.ts
      relevance: "Session interface to extend if needed"

  instruction: |
    Add localStorage persistence to SessionManager class:
    1. In createSession(): store token to localStorage
    2. In constructor(): check localStorage on init
    3. In destroySession(): clear localStorage entry

acceptance_criteria:
  - "Token stored in localStorage after login"
  - "Session auto-restored from localStorage on app init"
  - "localStorage cleared on logout"

complexity: medium

estimated_scope:
  files_affected: 1
  lines_estimated: 25

validation:
  - type: test
    command: "npm test -- --grep 'SessionManager'"
  - type: manual
    description: "Login, refresh page, verify session persists"

dependencies: []

notes: |
```

---

## Anti-Patterns to Avoid

| Pattern | Problem | Solution |
|---------|---------|----------|
| Empty bedrock | Worker guesses context | Always include ≥1 file |
| "Implement X" instruction | Too vague | Specify exact changes |
| No acceptance criteria | Can't verify done | Define observable outcomes |
| >5 files in scope | Too large for one ticket | Split into multiple tickets |
| Coupled tickets without deps | Race conditions | Declare dependencies |

---

## Summary Checklist

After generating all tickets:

- [ ] Every Task has ≥1 ticket
- [ ] All tickets have triangulated context (goal + bedrock + instruction)
- [ ] Bedrock files exist in codebase (verify paths)
- [ ] Acceptance criteria are testable
- [ ] Complexity matches scope estimates
- [ ] Dependencies form a valid DAG (no cycles)
- [ ] Tickets written to `{{SESSION_PATH}}/tickets/`
