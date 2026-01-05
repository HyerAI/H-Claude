# Validator: Resolution Check (VA[1] Gate 8)

## Variables

- `SESSION_PATH`: Path to think-tank session (e.g., `.claude/PM/think-tank/feature_20260103/`)
- `TICKETS_PATH`: Path to tickets folder (e.g., `${SESSION_PATH}/tickets/`)

## Purpose

Validate Sub-Task Tickets before worker execution. Ensures each ticket is deterministic and provides complete bedrock context.

**Gate Question:** Can a worker execute this ticket without guessing?

---

## Validation Protocol

### Input

Read all ticket files from folder: `{{TICKETS_PATH}}`

**File Discovery:**
1. Glob `{{TICKETS_PATH}}/*.yaml` to find all ticket files
2. Each file represents one ticket (e.g., `TICKET-001.yaml`, `TICKET-002.yaml`)
3. Validate each ticket file individually

### Check 1: Determinism

For each ticket, verify:

| Criterion | Pass Condition |
|-----------|----------------|
| Single Responsibility | Ticket does ONE thing |
| Clear Action | Verb is unambiguous (create, add, modify, remove) |
| Explicit Target | File paths or component names specified |
| No Implied Steps | Nothing left for worker to "figure out" |

**FAIL indicators:**
- "and" in title (multiple actions)
- "various", "appropriate", "as needed" (vague)
- Missing file paths
- References to "similar" patterns without specifics

### Check 2: Context Complete

Each ticket MUST have `triangulated_context` with:

```yaml
triangulated_context:
  goal: "WHY this ticket exists (traces to task objective)"
  bedrock:
    - path: "file/to/read.ts"
      what: "Specific thing to extract"
    - path: "another/file.ts"
      what: "Pattern to follow"
  instruction: "EXACTLY what to do"
```

**FAIL indicators:**
- Missing `goal` (worker won't understand purpose)
- Empty `bedrock[]` (worker forced to search)
- `bedrock` references non-existent files
- `instruction` contains assumptions ("should be obvious")

### Check 3: Scope Appropriate

| Criterion | Threshold |
|-----------|-----------|
| Files touched | MAX 3 files per ticket |
| Lines changed (estimate) | MAX 150 lines |
| Dependencies | MAX 2 other tickets |
| Complexity | Single concept |

**FAIL indicators:**
- Ticket spans multiple directories
- Requires understanding 5+ files
- Creates AND tests AND documents (split these)
- "Refactor" without bounded scope

### Check 4: Acceptance Clear

Each `acceptance_criteria` item must be:

- **Testable**: Can verify pass/fail mechanically
- **Specific**: No subjective terms ("good", "clean", "proper")
- **Complete**: Covers the full scope of the ticket

**FAIL indicators:**
- "Works correctly" (not testable)
- "Follows best practices" (subjective)
- Missing error case handling
- No criteria at all

---

## Output Format

### If All Tickets PASS

```yaml
resolution_validation:
  status: PASS
  timestamp: "[ISO timestamp]"
  tickets_validated: [count]

  tickets:
    - id: "TICKET-001"
      status: PASS
      complexity: low  # low | medium | high
      estimated_loc: 45

    - id: "TICKET-002"
      status: PASS
      complexity: medium
      estimated_loc: 120

  summary:
    total_complexity: "medium"
    execution_ready: true
```

### If Any Ticket FAILS

```yaml
resolution_validation:
  status: FAIL
  timestamp: "[ISO timestamp]"
  tickets_validated: [count]
  tickets_failed: [count]

  failures:
    - id: "TICKET-003"
      status: FAIL
      violations:
        - check: "Determinism"
          issue: "Title contains 'and' - multiple actions"
          fix: "Split into TICKET-003a (create) and TICKET-003b (configure)"

        - check: "Context Complete"
          issue: "bedrock[] empty - no reference files"
          fix: "Add bedrock entries for existing patterns in src/utils/"

    - id: "TICKET-005"
      status: FAIL
      violations:
        - check: "Scope Appropriate"
          issue: "Touches 7 files across 4 directories"
          fix: "Split by directory: TICKET-005a (api/), TICKET-005b (ui/)"

  remediation:
    action: "Return to Generator for ticket refinement"
    tickets_to_split: ["TICKET-003", "TICKET-005"]
    context_needed: ["TICKET-003", "TICKET-007"]
```

---

## Complexity Warnings

Flag these even on PASS:

```yaml
warnings:
  - ticket: "TICKET-002"
    type: "file_count"
    message: "Touches 3 files (at threshold)"

  - ticket: "TICKET-004"
    type: "bedrock_minimal"
    message: "Only 1 bedrock reference - consider adding more context"

  - ticket: "TICKET-006"
    type: "dependency_chain"
    message: "Depends on 2 tickets - coordinate execution order"
```

---

## Quick Reference: Common Splits

| Symptom | Split Strategy |
|---------|----------------|
| "Create X and test X" | Separate implementation + test tickets |
| "Update A, B, C files" | One ticket per file (or logical group) |
| "Refactor module" | Break into: extract, rename, reorganize |
| "Add feature with UI" | Backend ticket + Frontend ticket |
| "Fix bug and add logging" | Fix ticket + Enhancement ticket |

---

## Validation Execution

```
1. Discover ticket files: Glob {{TICKETS_PATH}}/*.yaml
2. For each ticket file:
   a. Load ticket YAML
   b. Run Check 1-4
   c. Assign complexity rating
   d. Record violations
3. If any FAIL → return FAIL with remediation
4. If all PASS → return PASS with complexity summary
5. Include warnings regardless of status
```
