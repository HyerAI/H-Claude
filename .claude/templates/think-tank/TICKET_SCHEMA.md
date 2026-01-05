# TICKET_SCHEMA.md

> Level 5 (Instruction) in Diffusion Hierarchy: NS → Roadmap → Phase Roadmap → Task Plan → **Ticket**

A Ticket is the atomic unit of work. It must be small enough for a single worker to execute deterministically without ambiguity.

---

## Schema

```yaml
ticket_id: TKT-YYYYMMDD-NNN  # e.g., TKT-20260103-001
task_id: TASK-XXX            # Parent Task Plan item

status: pending | in_progress | complete | blocked

triangulated_context:
  goal: |
    # What outcome this achieves (traced from NS/Phase)
    # Answer: "Why does this matter?"

  bedrock:
    # Files/code the worker MUST read before starting
    - path: src/module/existing.ts
      relevance: "Contains interface to implement"
    - path: .claude/PM/SSoT/ADRs/ADR-001.md
      relevance: "Decision on approach"

  instruction: |
    # The specific action to take
    # Must be unambiguous - one clear interpretation
    # Example: "Add validateInput() method to UserService class"

acceptance_criteria:
  # Mandatory: What 'done' looks like
  - "Function returns boolean"
  - "Handles null input gracefully"
  - "Unit test covers happy path"

complexity: simple | medium | complex
# simple: Single file, <50 lines changed
# medium: 2-3 files, clear pattern to follow
# complex: Multiple files, requires careful coordination

estimated_scope:
  files_affected: 1-3
  lines_estimated: 50

validation:
  # Checks that must pass before marking complete
  - type: test
    command: "npm test -- --grep 'UserService'"
  - type: lint
    command: "npm run lint src/module/"
  - type: manual
    description: "Verify function appears in API docs"

dependencies:
  # Other tickets that must complete first
  - TKT-20260103-000  # Optional

notes: |
  # Worker notes, blockers encountered, decisions made
```

---

## Rules

1. **Single Responsibility**: One ticket = one discrete change
2. **Deterministic**: Any competent worker should produce same result
3. **Bedrock Required**: Never start without reading context files
4. **Acceptance Criteria**: If you can't define done, ticket is too vague
5. **Scope Limit**: If >5 files affected, split into multiple tickets

---

## Example

```yaml
ticket_id: TKT-20260103-001
task_id: TASK-002

status: pending

triangulated_context:
  goal: |
    Enable session persistence across browser refreshes
    (NS Feature: "Seamless user experience")

  bedrock:
    - path: src/services/auth.ts
      relevance: "Current session handling logic"
    - path: src/types/session.d.ts
      relevance: "Session interface definition"

  instruction: |
    Add localStorage persistence to SessionManager:
    1. On session create: store token in localStorage
    2. On app init: check localStorage for existing session
    3. On logout: clear localStorage

acceptance_criteria:
  - "Session survives page refresh"
  - "Logout clears stored session"
  - "Invalid stored token triggers re-auth"

complexity: medium

estimated_scope:
  files_affected: 2
  lines_estimated: 35

validation:
  - type: test
    command: "npm test -- session"
  - type: manual
    description: "Refresh page while logged in, verify session persists"

dependencies: []

notes: |
```

---

## Anti-Patterns

| Problem | Fix |
|---------|-----|
| "Implement authentication" | Too broad → split into tickets |
| Empty bedrock array | Worker will guess → add context files |
| "Make it work" acceptance | Vague → define observable outcome |
| >5 files in scope | Split ticket or promote to Task |
