# execution-plan.yaml Schema

The execution plan lives in the think-tank subject folder, enabling persistent tracking across sessions.

---

## Schema Definition

```yaml
# execution-plan.yaml - Implementation Plan

# Identity
topic: string              # Links to think-tank topic
created: YYYY-MM-DD        # When plan was drafted
last_updated: YYYY-MM-DD   # Last modification

# Status Flow: draft → review → approved → in_progress → complete
status: enum               # draft | review | approved | in_progress | complete

# Link to decision
decision:
  path: string             # Path chosen from Decision Map
  version: integer         # Decision Map version this implements
  confidence: enum         # HIGH | MEDIUM | LOW

# Implementation phases
phases:
  - id: integer            # Phase number (1, 2, 3...)
    name: string           # Phase title
    status: enum           # pending | in_progress | complete | blocked
    tasks:
      - id: string         # Task ID (e.g., "1.1", "1.2")
        description: string
        files: [string]    # Files to create/modify
        dependencies: [string]  # Task IDs this depends on
        success_criteria: string
        status: enum       # pending | in_progress | complete | blocked
        notes: string      # Optional implementation notes

# Execution tracking
execution:
  started: ISO8601 | null
  completed: ISO8601 | null
  session_path: string     # Path to hc-execute session folder
  completion_report: string | null  # Path to final report

# Review tracking
reviews:
  - date: YYYY-MM-DD
    reviewer: string       # "HD" or agent name
    status: enum           # approved | changes_requested | blocked
    notes: string
```

---

## Example: Draft Plan

```yaml
topic: auth_system
created: 2026-01-02
last_updated: 2026-01-02
status: draft

decision:
  path: "Path B: JWT with refresh tokens"
  version: 1
  confidence: HIGH

phases:
  - id: 1
    name: "Foundation"
    status: pending
    tasks:
      - id: "1.1"
        description: "Create auth module structure"
        files: ["src/auth/index.ts", "src/auth/types.ts"]
        dependencies: []
        success_criteria: "Module exports placeholder functions"
        status: pending
        notes: ""
      - id: "1.2"
        description: "Add JWT dependencies"
        files: ["package.json"]
        dependencies: []
        success_criteria: "jsonwebtoken and types installed"
        status: pending
        notes: ""

  - id: 2
    name: "Core Implementation"
    status: pending
    tasks:
      - id: "2.1"
        description: "Implement token generation"
        files: ["src/auth/tokens.ts"]
        dependencies: ["1.1", "1.2"]
        success_criteria: "generateToken() returns valid JWT"
        status: pending
        notes: ""

execution:
  started: null
  completed: null
  session_path: ""
  completion_report: null

reviews: []
```

---

## Example: Approved Plan Ready for Execution

```yaml
topic: auth_system
created: 2026-01-02
last_updated: 2026-01-02
status: approved

decision:
  path: "Path B: JWT with refresh tokens"
  version: 1
  confidence: HIGH

phases:
  - id: 1
    name: "Foundation"
    status: pending
    tasks:
      - id: "1.1"
        description: "Create auth module structure"
        files: ["src/auth/index.ts", "src/auth/types.ts"]
        dependencies: []
        success_criteria: "Module exports placeholder functions"
        status: pending
        notes: ""
      - id: "1.2"
        description: "Add JWT dependencies"
        files: ["package.json"]
        dependencies: []
        success_criteria: "jsonwebtoken and types installed"
        status: pending
        notes: ""

  - id: 2
    name: "Core Implementation"
    status: pending
    tasks:
      - id: "2.1"
        description: "Implement token generation"
        files: ["src/auth/tokens.ts"]
        dependencies: ["1.1", "1.2"]
        success_criteria: "generateToken() returns valid JWT"
        status: pending
        notes: ""
      - id: "2.2"
        description: "Implement token validation"
        files: ["src/auth/tokens.ts"]
        dependencies: ["2.1"]
        success_criteria: "validateToken() returns decoded payload or throws"
        status: pending
        notes: ""

  - id: 3
    name: "Integration"
    status: pending
    tasks:
      - id: "3.1"
        description: "Add auth middleware"
        files: ["src/middleware/auth.ts"]
        dependencies: ["2.2"]
        success_criteria: "Middleware validates JWT on protected routes"
        status: pending
        notes: ""

execution:
  started: null
  completed: null
  session_path: ""
  completion_report: null

reviews:
  - date: 2026-01-02
    reviewer: "HD"
    status: approved
    notes: "Looks good, proceed with execution"
```

---

## Example: In Progress

```yaml
topic: auth_system
created: 2026-01-02
last_updated: 2026-01-02
status: in_progress

decision:
  path: "Path B: JWT with refresh tokens"
  version: 1
  confidence: HIGH

phases:
  - id: 1
    name: "Foundation"
    status: complete
    tasks:
      - id: "1.1"
        description: "Create auth module structure"
        files: ["src/auth/index.ts", "src/auth/types.ts"]
        dependencies: []
        success_criteria: "Module exports placeholder functions"
        status: complete
        notes: ""
      - id: "1.2"
        description: "Add JWT dependencies"
        files: ["package.json"]
        dependencies: []
        success_criteria: "jsonwebtoken and types installed"
        status: complete
        notes: ""

  - id: 2
    name: "Core Implementation"
    status: in_progress
    tasks:
      - id: "2.1"
        description: "Implement token generation"
        files: ["src/auth/tokens.ts"]
        dependencies: ["1.1", "1.2"]
        success_criteria: "generateToken() returns valid JWT"
        status: complete
        notes: ""
      - id: "2.2"
        description: "Implement token validation"
        files: ["src/auth/tokens.ts"]
        dependencies: ["2.1"]
        success_criteria: "validateToken() returns decoded payload or throws"
        status: in_progress
        notes: ""

  - id: 3
    name: "Integration"
    status: pending
    tasks:
      - id: "3.1"
        description: "Add auth middleware"
        files: ["src/middleware/auth.ts"]
        dependencies: ["2.2"]
        success_criteria: "Middleware validates JWT on protected routes"
        status: pending
        notes: ""

execution:
  started: 2026-01-02T10:30:00Z
  completed: null
  session_path: ".claude/PM/hc-execute/auth_system_20260102/"
  completion_report: null

reviews:
  - date: 2026-01-02
    reviewer: "HD"
    status: approved
    notes: "Looks good, proceed with execution"
```

---

## Status Transitions

```
                    DRAFT PLAN
                        │
                        ▼
                   ┌─────────┐
         ┌────────│  draft  │
         │        └────┬────┘
         │             │
         │   CHANGES   │ SUBMIT FOR REVIEW
         │             │
         ▼             ▼
    ┌─────────┐   ┌─────────┐
    │  draft  │◀──│  review │
    └─────────┘   └────┬────┘
                       │
               HD APPROVES
                       │
                       ▼
                  ┌──────────┐
                  │ approved │
                  └────┬─────┘
                       │
           /hc-execute
                       │
                       ▼
                ┌─────────────┐
                │ in_progress │
                └──────┬──────┘
                       │
              EXECUTION COMPLETE
                       │
                       ▼
                  ┌──────────┐
                  │ complete │
                  └──────────┘
```

---

## Integration with context.yaml

The project `context.yaml` tracks active think-tank sessions with plan status:

```yaml
think_tank:
  - topic: auth_system
    path: .claude/PM/think-tank/auth_system_20260102/
    status: decided                    # Think-tank session status
    plan_status: in_progress           # Execution plan status
    plan_path: .claude/PM/think-tank/auth_system_20260102/execution-plan.yaml
```

This provides at-a-glance visibility into all active work streams.

---

## File Location

```
.claude/PM/think-tank/{topic_slug}_{date}/
├── STATE.yaml              # Think-tank session state
├── execution-plan.yaml     # Implementation plan (THIS FILE)
├── 00_BRIEFING.md
├── 01_CAST.md
├── 02_KNOWLEDGE_BASE/
├── 03_SESSIONS/
├── 04_DECISION_MAP.md
└── 05_LEARNINGS.md
```
