# STATE.yaml Schema

The state file enables persistent topic workspaces that can be resumed days or weeks later as you implement and learn.

---

## Schema Definition

```yaml
# STATE.yaml - Topic Workspace State

# Identity
topic: string              # Slug identifying the topic
created: YYYY-MM-DD        # Date workspace created (ISO 8601)
last_active: YYYY-MM-DD    # Date of most recent session (ISO 8601)
status: enum               # active | paused | decided | archived

# Lifecycle tracking (V2.0.0+)
lifecycle:
  type: enum               # roadmap | phase | side_quest | legacy
                           # roadmap: Created via --roadmap flag
                           # phase: Created via --phase=PHASE-XXX flag
                           # side_quest: Ad-hoc research (no flag)
                           # legacy: Pre-V2.0.0 sessions (migration support)
  status: enum             # active | paused | completed | archived
  archived_date: YYYY-MM-DD | null  # When archived
  archive_reason: enum | null  # all_items_complete | manual | stale
  pause_reason: string | null  # Why paused (e.g., "escalation")

# Parent reference (SUB sessions only)
parent:
  topic: string | null     # Parent MAIN session topic
  path: string | null      # Path to parent workspace
  action_item_id: string | null  # AI-XXX this addresses

# Escalations (SUB sessions)
escalations:
  - id: string             # ESC-001, ESC-002, etc.
    type: enum             # SCOPE_EXPANSION | CONFLICT | INFEASIBILITY | DEPENDENCY_ISSUE
    description: string
    raised_in_session: integer
    status: enum           # pending | acknowledged | resolved
    resolution: string | null

# Current session tracking (if active)
current_session:
  number: integer          # Session number (1, 2, 3...)
  step: integer            # 1=intake, 2=cast, 3=research, 4=council, 5=map, 6=review
  started: ISO8601         # When this session started
  trigger: enum            # initial | new_info | issue | reevaluate

# Session history
sessions:
  - number: integer
    date: YYYY-MM-DD
    trigger: enum          # What prompted this session
    summary: string        # One-line summary of what was discussed
    outcome: enum          # pending | decision_updated | no_change | deferred
    rounds: integer        # How many council rounds

# Decision evolution
decisions:
  - version: integer
    date: YYYY-MM-DD
    session: integer       # Which session produced this version
    recommendation: string # Path chosen or null
    confidence: enum       # HIGH | MEDIUM | LOW | null
    rationale: string      # Why this was recommended

# Learnings from implementation
learnings:
  - date: YYYY-MM-DD
    finding: string        # What we discovered
    impact: enum           # validates | challenges | neutral
    action: string         # How this affects the decision

# Questions that remain open
open_questions:
  - question: string
    raised_in: integer     # Session number
    answered: boolean
    answer: string | null

# Cast information (may evolve across sessions)
cast:
  domain_expert:
    title: string
    focus: string
  pragmatist:
    title: string
    focus: string
  last_updated: YYYY-MM-DD

# Action items (MAIN sessions only)
action_items:
  - id: string             # AI-001, AI-002, etc.
    status: enum           # pending | in_progress | completed | blocked
    sub_session_path: string | null  # Path to sub think-tank when created
```

---

## Example: New Workspace

```yaml
topic: database_selection
created: 2026-01-01
last_active: 2026-01-01
status: active

current_session:
  number: 1
  step: 4
  started: 2026-01-01T14:30:22Z
  trigger: initial

sessions:
  - number: 1
    date: 2026-01-01
    trigger: initial
    summary: "Initial exploration of database options for user service"
    outcome: pending
    rounds: 3

decisions:
  - version: 1
    date: 2026-01-01
    session: 1
    recommendation: null
    confidence: null
    rationale: null

learnings: []
open_questions: []

cast:
  domain_expert:
    title: "Database Architect"
    focus: "Performance, consistency, scaling patterns"
  pragmatist:
    title: "Startup CTO"
    focus: "Time-to-market, ops burden, team familiarity"
  last_updated: 2026-01-01
```

---

## Example: After Decision

```yaml
topic: database_selection
created: 2026-01-01
last_active: 2026-01-01
status: decided

current_session: null

sessions:
  - number: 1
    date: 2026-01-01
    trigger: initial
    summary: "Initial exploration of database options"
    outcome: decision_updated
    rounds: 5

decisions:
  - version: 1
    date: 2026-01-01
    session: 1
    recommendation: "Path B: PostgreSQL with connection pooling"
    confidence: HIGH
    rationale: "Team familiarity + proven scale path + 6-month runway constraint"

learnings: []

open_questions:
  - question: "How will we handle full-text search if needed?"
    raised_in: 1
    answered: false
    answer: null

cast:
  domain_expert:
    title: "Database Architect"
    focus: "Performance, consistency, scaling patterns"
  pragmatist:
    title: "Startup CTO"
    focus: "Time-to-market, ops burden, team familiarity"
  last_updated: 2026-01-01
```

---

## Example: Multi-Session Workspace

```yaml
topic: database_selection
created: 2026-01-01
last_active: 2026-01-07
status: decided

current_session: null

sessions:
  - number: 1
    date: 2026-01-01
    trigger: initial
    summary: "Initial exploration of database options"
    outcome: decision_updated
    rounds: 5

  - number: 2
    date: 2026-01-03
    trigger: issue
    summary: "Connection pool exhaustion in POC"
    outcome: decision_updated
    rounds: 3

  - number: 3
    date: 2026-01-07
    trigger: new_info
    summary: "Full-text search requirement surfaced"
    outcome: decision_updated
    rounds: 4

decisions:
  - version: 1
    date: 2026-01-01
    session: 1
    recommendation: "Path B: PostgreSQL"
    confidence: HIGH
    rationale: "Team familiarity + proven scale"

  - version: 2
    date: 2026-01-03
    session: 2
    recommendation: "Path B: PostgreSQL + PgBouncer"
    confidence: HIGH
    rationale: "Added connection pooling to handle load"

  - version: 3
    date: 2026-01-07
    session: 3
    recommendation: "Path B: PostgreSQL + PgBouncer + pg_trgm for search"
    confidence: MEDIUM
    rationale: "Native FTS avoids new dependency; revisit if search volume grows"

learnings:
  - date: 2026-01-03
    finding: "Default connection pool size (20) insufficient for async workers"
    impact: challenges
    action: "Added PgBouncer recommendation"

  - date: 2026-01-05
    finding: "PostgreSQL pg_trgm extension handles our search patterns well"
    impact: validates
    action: "Confirmed no need for Elasticsearch yet"

open_questions:
  - question: "At what query volume should we reconsider Elasticsearch?"
    raised_in: 3
    answered: false
    answer: null

cast:
  domain_expert:
    title: "Database Architect"
    focus: "Performance, consistency, scaling patterns"
  pragmatist:
    title: "Startup CTO"
    focus: "Time-to-market, ops burden, team familiarity"
  last_updated: 2026-01-01
```

---

## State Transitions

```
                    NEW TOPIC
                        │
                        ▼
                   ┌─────────┐
         ┌────────│  active │◀──────────────────────┐
         │        └────┬────┘                       │
         │             │                            │
         │   PAUSE     │ DECIDE                     │ RESUME
         │             │                            │ (new_info/issue/reevaluate)
         ▼             ▼                            │
    ┌─────────┐   ┌─────────┐                       │
    │  paused │   │ decided │───────────────────────┘
    └────┬────┘   └────┬────┘
         │             │
         │ RESUME      │ ARCHIVE (manual)
         │             │
         ▼             ▼
    ┌─────────┐   ┌──────────┐
    │  active │   │ archived │
    └─────────┘   └──────────┘
```

---

## File Locations

| File | Purpose | When Created |
|------|---------|--------------|
| `STATE.yaml` | Workspace state | Session 1, Step 1 |
| `00_BRIEFING.md` | Problem statement | Session 1, Step 1 |
| `01_CAST.md` | Expert personas | Session 1, Step 2 |
| `02_KNOWLEDGE_BASE/` | Research artifacts | Session 1+, Step 3 |
| `03_SESSIONS/session_NNN.md` | Session transcripts | Each session, Step 4 |
| `04_DECISION_MAP.md` | Living decision doc | Session 1, Step 5 |
| `05_LEARNINGS.md` | Implementation findings | After DECIDE, ongoing |
| `action-items.yaml` | Action items (MAIN only) | After DECIDE, MAIN sessions |

---

## Example: MAIN Session

MAIN sessions output `action-items.yaml` instead of `execution-plan.yaml`.

```yaml
topic: ecommerce_platform
created: 2026-01-02
last_active: 2026-01-02
status: active

lifecycle:
  type: main
  status: active
  archived_date: null
  archive_reason: null
  pause_reason: null

parent: null  # MAIN sessions have no parent

escalations: []  # Escalations typically occur in SUB sessions

current_session:
  number: 1
  step: 5
  started: 2026-01-02T10:00:00Z
  trigger: initial

sessions:
  - number: 1
    date: 2026-01-02
    trigger: initial
    summary: "Project vision - identified 4 key workstreams"
    outcome: decision_updated
    rounds: 5

decisions:
  - version: 1
    date: 2026-01-02
    session: 1
    recommendation: "4 action items: DB schema, Auth, Catalog API, Order pipeline"
    confidence: HIGH
    rationale: "Clear separation of concerns, manageable dependencies"

learnings: []
open_questions: []

cast:
  domain_expert:
    title: "E-commerce Architect"
    focus: "Scalability, transaction integrity, user experience"
  pragmatist:
    title: "Startup CTO"
    focus: "Time-to-market, team capacity, operational complexity"
  last_updated: 2026-01-02

# MAIN-specific: Track action items
action_items:
  - id: AI-001
    status: completed
    sub_session_path: .claude/PM/think-tank/ecommerce_platform_sub_AI-001_20260103/
  - id: AI-002
    status: in_progress
    sub_session_path: .claude/PM/think-tank/ecommerce_platform_sub_AI-002_20260105/
  - id: AI-003
    status: pending
    sub_session_path: null
  - id: AI-004
    status: blocked
    sub_session_path: null
```

---

## Example: SUB Session

SUB sessions link to their parent MAIN session and specific action item.

```yaml
topic: ecommerce_platform_sub_AI-002
created: 2026-01-05
last_active: 2026-01-05
status: active

lifecycle:
  type: sub
  status: active
  archived_date: null
  archive_reason: null
  pause_reason: null

# Link to parent MAIN session
parent:
  topic: ecommerce_platform
  path: .claude/PM/think-tank/ecommerce_platform_20260102/
  action_item_id: AI-002

escalations: []  # Empty - no escalations yet

current_session:
  number: 1
  step: 4
  started: 2026-01-05T09:00:00Z
  trigger: initial

sessions:
  - number: 1
    date: 2026-01-05
    trigger: initial
    summary: "Deep dive on authentication system - JWT with refresh tokens"
    outcome: pending
    rounds: 3

decisions:
  - version: 1
    date: 2026-01-05
    session: 1
    recommendation: null  # Still in progress
    confidence: null
    rationale: null

learnings: []

open_questions:
  - question: "Should we use httpOnly cookies or localStorage for tokens?"
    raised_in: 1
    answered: false
    answer: null

cast:
  domain_expert:
    title: "Security Engineer"
    focus: "Auth flows, token security, OAuth integration"
  pragmatist:
    title: "Full-stack Developer"
    focus: "Implementation complexity, library choices, testing"
  last_updated: 2026-01-05

action_items: []  # SUB sessions don't have their own action items
```

---

## Example: SUB Session with Escalation

When a SUB session encounters issues requiring MAIN review:

```yaml
topic: ecommerce_platform_sub_AI-002
created: 2026-01-05
last_active: 2026-01-06
status: paused  # Paused due to escalation

lifecycle:
  type: sub
  status: paused
  archived_date: null
  archive_reason: null
  pause_reason: escalation

parent:
  topic: ecommerce_platform
  path: .claude/PM/think-tank/ecommerce_platform_20260102/
  action_item_id: AI-002

# Escalation that caused the pause
escalations:
  - id: ESC-001
    type: SCOPE_EXPANSION
    description: "Auth system requires user profile schema changes not covered by AI-001 (DB schema)"
    raised_in_session: 1
    status: pending
    resolution: null

current_session:
  number: 1
  step: 4
  started: 2026-01-05T09:00:00Z
  trigger: initial

sessions:
  - number: 1
    date: 2026-01-05
    trigger: initial
    summary: "Auth implementation - discovered schema dependency"
    outcome: deferred  # Deferred due to escalation
    rounds: 4

decisions:
  - version: 1
    date: 2026-01-05
    session: 1
    recommendation: "JWT with refresh tokens"
    confidence: MEDIUM
    rationale: "Blocked by schema dependency - needs AI-001 update"

learnings:
  - date: 2026-01-06
    finding: "User roles and permissions need schema support"
    impact: challenges
    action: "Escalated to MAIN for AI-001 scope update"

open_questions: []

cast:
  domain_expert:
    title: "Security Engineer"
    focus: "Auth flows, token security, OAuth integration"
  pragmatist:
    title: "Full-stack Developer"
    focus: "Implementation complexity, library choices, testing"
  last_updated: 2026-01-05

action_items: []
```

---

## Example: Archived Session

When a session is complete and archived:

```yaml
topic: ecommerce_platform
created: 2026-01-02
last_active: 2026-01-15
status: archived

lifecycle:
  type: main
  status: archived
  archived_date: 2026-01-16
  archive_reason: all_items_complete
  pause_reason: null

parent: null

escalations: []

current_session: null  # No active session

sessions:
  - number: 1
    date: 2026-01-02
    trigger: initial
    summary: "Project vision - identified 4 key workstreams"
    outcome: decision_updated
    rounds: 5

decisions:
  - version: 1
    date: 2026-01-02
    session: 1
    recommendation: "4 action items completed successfully"
    confidence: HIGH
    rationale: "All workstreams delivered"
    adr: "ADR-0501"
    adr_version: "V1.0.0"

learnings:
  - date: 2026-01-10
    finding: "PostgreSQL full-text search sufficient for MVP"
    impact: validates
    action: "Documented in ADR, deferred Elasticsearch"

open_questions: []

cast:
  domain_expert:
    title: "E-commerce Architect"
    focus: "Scalability, transaction integrity, user experience"
  pragmatist:
    title: "Startup CTO"
    focus: "Time-to-market, team capacity, operational complexity"
  last_updated: 2026-01-02

action_items:
  - id: AI-001
    status: completed
    sub_session_path: .claude/PM/think-tank/archive/ecommerce_platform_sub_AI-001_20260103/
  - id: AI-002
    status: completed
    sub_session_path: .claude/PM/think-tank/archive/ecommerce_platform_sub_AI-002_20260105/
  - id: AI-003
    status: completed
    sub_session_path: .claude/PM/think-tank/archive/ecommerce_platform_sub_AI-003_20260106/
  - id: AI-004
    status: completed
    sub_session_path: .claude/PM/think-tank/archive/ecommerce_platform_sub_AI-004_20260111/
```

---

## Lifecycle Type Reference

| Type | Description | Flag | Output |
|------|-------------|------|--------|
| `roadmap` | Creates/updates ROADMAP.yaml | `--roadmap` | `ROADMAP.yaml` phases |
| `phase` | Plans specific phase | `--phase=PHASE-XXX` | `execution-plan.yaml` |
| `side_quest` | Ad-hoc research | (no flag) | `STATE.yaml` + findings |
| `legacy` | Pre-V2.0.0 sessions | N/A | Migration support |

**Migration Note:** Sessions with `type: main | sub | standard` are pre-V2.0.0 sessions. Set `type: legacy` when encountered.

---

## Lifecycle Status Reference

| Status | Description | Can Resume |
|--------|-------------|------------|
| `active` | Currently in use | N/A |
| `paused` | Temporarily stopped | Yes |
| `completed` | Successfully finished | No (use --from-archive) |
| `archived` | Moved to archive folder | Yes (creates new linked session) |
