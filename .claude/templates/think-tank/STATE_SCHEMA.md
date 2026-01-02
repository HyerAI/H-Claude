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
