# action-items.yaml Schema

Output from MAIN Think-Tank sessions. Defines 3-7 discrete action items with dependencies.

---

## Schema Definition

```yaml
# action-items.yaml - Output from MAIN Think-Tank sessions

# Identity
topic: string              # MAIN session topic slug
created: YYYY-MM-DD        # When action items were defined
last_updated: YYYY-MM-DD   # Last modification
status: enum               # draft | approved | in_progress | complete

# Link to MAIN session
main_session:
  path: string             # Path to MAIN think-tank workspace
  decision_map_version: integer  # Decision Map version this is based on

# Action items (3-7 items required)
action_items:
  - id: string             # AI-001, AI-002, etc.
    title: string          # Brief title (max 50 chars)
    context: string        # Context from MAIN discussion
    constraints: [string]  # List of constraints for this item
    success_criteria: string  # How we know this is complete
    depends_on: [string]   # AI-XXX references (empty if no dependencies)
    status: enum           # pending | in_progress | completed | blocked
    sub_session_path: string | null  # Path to sub think-tank when created
    execution_plan_path: string | null  # Path to execution-plan.yaml when generated
    completed_date: YYYY-MM-DD | null  # When marked complete
    notes: string          # Additional notes or blockers

# Summary
summary:
  total: integer           # Total action items (3-7)
  pending: integer
  in_progress: integer
  completed: integer
  blocked: integer
```

---

## Example: Draft Action Items

```yaml
topic: ecommerce_platform
created: 2026-01-02
last_updated: 2026-01-02
status: draft

main_session:
  path: .claude/PM/think-tank/ecommerce_platform_20260102/
  decision_map_version: 1

action_items:
  - id: AI-001
    title: "Database Schema Design"
    context: "Council identified PostgreSQL as the database. Need to design schema for products, users, orders."
    constraints:
      - "Must support multi-currency"
      - "Must handle 10k concurrent users"
    success_criteria: "Schema documented in ADR, migrations ready"
    depends_on: []
    status: pending
    sub_session_path: null
    execution_plan_path: null
    completed_date: null
    notes: ""

  - id: AI-002
    title: "Authentication System"
    context: "JWT with refresh tokens chosen. Need to implement secure auth flow."
    constraints:
      - "Must integrate with Google OAuth"
      - "Session timeout: 24 hours"
    success_criteria: "Auth endpoints functional, tests passing"
    depends_on: ["AI-001"]  # Needs user schema first
    status: pending
    sub_session_path: null
    execution_plan_path: null
    completed_date: null
    notes: ""

  - id: AI-003
    title: "Product Catalog API"
    context: "REST API for product CRUD operations with search."
    constraints:
      - "Must support pagination"
      - "Full-text search required"
    success_criteria: "API endpoints documented, 80% test coverage"
    depends_on: ["AI-001"]
    status: pending
    sub_session_path: null
    execution_plan_path: null
    completed_date: null
    notes: ""

  - id: AI-004
    title: "Order Processing Pipeline"
    context: "Order creation, payment integration, fulfillment tracking."
    constraints:
      - "Must integrate with Stripe"
      - "Must handle failed payments gracefully"
    success_criteria: "End-to-end order flow working"
    depends_on: ["AI-002", "AI-003"]  # Needs auth and products
    status: pending
    sub_session_path: null
    execution_plan_path: null
    completed_date: null
    notes: ""

summary:
  total: 4
  pending: 4
  in_progress: 0
  completed: 0
  blocked: 0
```

---

## Example: In Progress

```yaml
topic: ecommerce_platform
created: 2026-01-02
last_updated: 2026-01-05
status: in_progress

main_session:
  path: .claude/PM/think-tank/ecommerce_platform_20260102/
  decision_map_version: 1

action_items:
  - id: AI-001
    title: "Database Schema Design"
    context: "Council identified PostgreSQL as the database."
    constraints:
      - "Must support multi-currency"
      - "Must handle 10k concurrent users"
    success_criteria: "Schema documented in ADR, migrations ready"
    depends_on: []
    status: completed
    sub_session_path: .claude/PM/think-tank/ecommerce_platform_sub_AI-001_20260103/
    execution_plan_path: .claude/PM/think-tank/ecommerce_platform_sub_AI-001_20260103/execution-plan.yaml
    completed_date: 2026-01-04
    notes: "Completed ahead of schedule"

  - id: AI-002
    title: "Authentication System"
    context: "JWT with refresh tokens chosen."
    constraints:
      - "Must integrate with Google OAuth"
      - "Session timeout: 24 hours"
    success_criteria: "Auth endpoints functional, tests passing"
    depends_on: ["AI-001"]
    status: in_progress
    sub_session_path: .claude/PM/think-tank/ecommerce_platform_sub_AI-002_20260105/
    execution_plan_path: null  # Still in think-tank phase
    completed_date: null
    notes: "Sub think-tank session active"

  - id: AI-003
    title: "Product Catalog API"
    context: "REST API for product CRUD operations with search."
    constraints:
      - "Must support pagination"
      - "Full-text search required"
    success_criteria: "API endpoints documented, 80% test coverage"
    depends_on: ["AI-001"]
    status: pending
    sub_session_path: null
    execution_plan_path: null
    completed_date: null
    notes: "Can start in parallel with AI-002"

  - id: AI-004
    title: "Order Processing Pipeline"
    context: "Order creation, payment integration, fulfillment tracking."
    constraints:
      - "Must integrate with Stripe"
      - "Must handle failed payments gracefully"
    success_criteria: "End-to-end order flow working"
    depends_on: ["AI-002", "AI-003"]
    status: blocked
    sub_session_path: null
    execution_plan_path: null
    completed_date: null
    notes: "Waiting for AI-002 and AI-003"

summary:
  total: 4
  pending: 1
  in_progress: 1
  completed: 1
  blocked: 1
```

---

## Example: Complete

```yaml
topic: ecommerce_platform
created: 2026-01-02
last_updated: 2026-01-15
status: complete

main_session:
  path: .claude/PM/think-tank/ecommerce_platform_20260102/
  decision_map_version: 2  # Updated during implementation

action_items:
  - id: AI-001
    title: "Database Schema Design"
    context: "Council identified PostgreSQL as the database."
    constraints:
      - "Must support multi-currency"
      - "Must handle 10k concurrent users"
    success_criteria: "Schema documented in ADR, migrations ready"
    depends_on: []
    status: completed
    sub_session_path: .claude/PM/think-tank/ecommerce_platform_sub_AI-001_20260103/
    execution_plan_path: .claude/PM/think-tank/ecommerce_platform_sub_AI-001_20260103/execution-plan.yaml
    completed_date: 2026-01-04
    notes: ""

  - id: AI-002
    title: "Authentication System"
    context: "JWT with refresh tokens chosen."
    constraints:
      - "Must integrate with Google OAuth"
      - "Session timeout: 24 hours"
    success_criteria: "Auth endpoints functional, tests passing"
    depends_on: ["AI-001"]
    status: completed
    sub_session_path: .claude/PM/think-tank/ecommerce_platform_sub_AI-002_20260105/
    execution_plan_path: .claude/PM/think-tank/ecommerce_platform_sub_AI-002_20260105/execution-plan.yaml
    completed_date: 2026-01-08
    notes: ""

  - id: AI-003
    title: "Product Catalog API"
    context: "REST API for product CRUD operations with search."
    constraints:
      - "Must support pagination"
      - "Full-text search required"
    success_criteria: "API endpoints documented, 80% test coverage"
    depends_on: ["AI-001"]
    status: completed
    sub_session_path: .claude/PM/think-tank/ecommerce_platform_sub_AI-003_20260106/
    execution_plan_path: .claude/PM/think-tank/ecommerce_platform_sub_AI-003_20260106/execution-plan.yaml
    completed_date: 2026-01-10
    notes: ""

  - id: AI-004
    title: "Order Processing Pipeline"
    context: "Order creation, payment integration, fulfillment tracking."
    constraints:
      - "Must integrate with Stripe"
      - "Must handle failed payments gracefully"
    success_criteria: "End-to-end order flow working"
    depends_on: ["AI-002", "AI-003"]
    status: completed
    sub_session_path: .claude/PM/think-tank/ecommerce_platform_sub_AI-004_20260111/
    execution_plan_path: .claude/PM/think-tank/ecommerce_platform_sub_AI-004_20260111/execution-plan.yaml
    completed_date: 2026-01-15
    notes: ""

summary:
  total: 4
  pending: 0
  in_progress: 0
  completed: 4
  blocked: 0
```

---

## Dependency Rules

1. **No Circular Dependencies:** AI-001 cannot depend on AI-002 if AI-002 depends on AI-001
2. **Transitive Dependencies:** If AI-003 depends on AI-002 and AI-002 depends on AI-001, AI-003 implicitly depends on AI-001
3. **Status Blocking:** Cannot set status to `in_progress` if any dependency has status other than `completed`
4. **Parallel Execution:** Items with no shared dependencies can be worked on in parallel

---

## Status Transitions

```
                    NEW ITEM
                        │
                        ▼
                   ┌─────────┐
         ┌────────│ pending │◀──────────────────────┐
         │        └────┬────┘                       │
         │             │                            │
         │   BLOCKED   │ DEPS MET                   │ BLOCKED (dep failed)
         │             │                            │
         ▼             ▼                            │
    ┌─────────┐   ┌─────────────┐                   │
    │ blocked │──▶│ in_progress │──────────────────▶│
    └─────────┘   └──────┬──────┘                   │
                         │                          │
                   WORK COMPLETE                    │
                         │                          │
                         ▼                          │
                   ┌───────────┐                    │
                   │ completed │                    │
                   └───────────┘
```

---

## Validation Rules

| Rule | Description |
|------|-------------|
| **Count** | Must have 3-7 action items |
| **IDs** | Must follow AI-XXX format, sequential |
| **Dependencies** | Must reference valid AI-XXX IDs |
| **No Self-Reference** | Item cannot depend on itself |
| **Acyclic** | Dependency graph must be acyclic |
| **Context** | Each item must have non-empty context |
| **Criteria** | Each item must have success_criteria |

---

## Integration with context.yaml

When MAIN session produces action items:

```yaml
think_tank:
  - topic: ecommerce_platform
    type: main
    path: .claude/PM/think-tank/ecommerce_platform_20260102/
    status: in_progress
    action_items_path: .claude/PM/think-tank/ecommerce_platform_20260102/action-items.yaml
    action_items_summary:
      total: 4
      completed: 1
```

---

## File Location

```
.claude/PM/think-tank/{topic_slug}_{date}/
├── STATE.yaml              # Think-tank session state
├── action-items.yaml       # THIS FILE (MAIN sessions only)
├── 00_BRIEFING.md
├── 01_CAST.md
├── 02_KNOWLEDGE_BASE/
├── 03_SESSIONS/
├── 04_DECISION_MAP.md
└── 05_LEARNINGS.md
```
