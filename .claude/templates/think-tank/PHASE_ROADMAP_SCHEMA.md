# Phase Roadmap Schema

Template for Level 3 (Structure) documentation in the Diffusion hierarchy.

**Hierarchy:** NORTHSTAR → Roadmap → **Phase Roadmap** → Task Plan → Tickets

---

## Schema

```yaml
# ═══════════════════════════════════════════════════════════════
# PHASE ROADMAP
# Level 3: Structure - Bridges Roadmap to Task Plans
# ═══════════════════════════════════════════════════════════════

meta:
  schema_version: '1.0.0'
  created: 'YYYY-MM-DDTHH:MM:SSZ'
  last_modified: 'YYYY-MM-DDTHH:MM:SSZ'

# ───────────────────────────────────────────────────────────────
# PHASE IDENTITY
# ───────────────────────────────────────────────────────────────

phase_id: PHASE-XXX          # Unique identifier (e.g., PHASE-001)
title: ''                    # Phase name
description: |
  What this phase accomplishes. Include:
  - Primary outcome
  - User/system value delivered
  - Scope boundaries (what's in/out)

status: planned              # planned | active | complete | blocked

# ───────────────────────────────────────────────────────────────
# NORTHSTAR ALIGNMENT
# ───────────────────────────────────────────────────────────────
# Which NORTHSTAR goals this phase serves

ns_alignment:
  goals: []                  # List of NORTHSTAR goal IDs this phase advances
  features: []               # Specific features being implemented
  success_metrics: []        # How we measure this phase's contribution

# ───────────────────────────────────────────────────────────────
# BEDROCK ANALYSIS
# ───────────────────────────────────────────────────────────────
# Current codebase state relevant to this phase
# CRITICAL: Must be populated BEFORE task planning

bedrock_analysis:
  # Current architecture patterns in the affected areas
  existing_patterns:
    - pattern: ''            # e.g., "Repository pattern for data access"
      location: ''           # e.g., "src/repositories/"
      relevance: ''          # How this affects the phase

  # Files that will be modified or created
  files_affected:
    modify: []               # Existing files to change
    create: []               # New files to add
    delete: []               # Files to remove (if any)

  # Technical constraints from existing code
  constraints:
    - constraint: ''         # e.g., "Must maintain backward compatibility"
      source: ''             # Where this constraint comes from
      impact: ''             # How it affects implementation

  # Dependencies on existing code
  code_dependencies:
    internal: []             # Internal modules/packages relied upon
    external: []             # External libraries required

# ───────────────────────────────────────────────────────────────
# TASKS
# ───────────────────────────────────────────────────────────────
# High-level task descriptions (detailed in Task Plans)

tasks:
  - id: TASK-XXX-01
    title: ''
    description: ''
    estimated_complexity: low | medium | high
    task_plan_path: null     # Populated when Task Plan created

# ───────────────────────────────────────────────────────────────
# VALIDATION GATES
# ───────────────────────────────────────────────────────────────
# What must pass before phase is complete

validation_gates:
  automated:
    - gate: ''               # e.g., "All unit tests pass"
      command: ''            # e.g., "npm test"
      required: true

  manual:
    - gate: ''               # e.g., "Code review approved"
      reviewer: ''           # Role or person responsible
      required: true

  acceptance:
    - criteria: ''           # User-facing acceptance criteria
      verification: ''       # How to verify

# ───────────────────────────────────────────────────────────────
# DEPENDENCIES
# ───────────────────────────────────────────────────────────────

dependencies:
  phases: []                 # Other phase IDs this depends on
  external: []               # External dependencies (APIs, services)
  blockers: []               # Current blocking issues

# ───────────────────────────────────────────────────────────────
# OUTPUTS
# ───────────────────────────────────────────────────────────────

outputs:
  artifacts: []              # What this phase produces
  documentation: []          # Docs to create/update
  downstream_unlocks: []     # What phases this enables
```

---

## Usage

### When to Create

Create a Phase Roadmap when:
1. A phase is activated in the main ROADMAP.yaml
2. Before starting any implementation work
3. After `/think-tank --phase=X` completes analysis

### Required Sections

All sections are required. Mark as `N/A` or empty array `[]` if not applicable.

### Bedrock Analysis

**CRITICAL:** The `bedrock_analysis` section must be populated through actual codebase exploration, not assumptions. This grounds the phase in reality.

```yaml
# GOOD - Based on actual exploration
bedrock_analysis:
  existing_patterns:
    - pattern: "Event-driven architecture with RxJS"
      location: "src/core/events/"
      relevance: "New features must emit events for consistency"

# BAD - Assumed without verification
bedrock_analysis:
  existing_patterns:
    - pattern: "Probably uses callbacks"  # Don't assume!
```

### Task Breakdown

Tasks should be:
- **Atomic:** Completable in a single work session
- **Testable:** Clear success criteria
- **Independent:** Minimal coupling to other tasks (where possible)

### Validation Gates

Include both:
- **Automated:** Tests, linting, type checking
- **Manual:** Reviews, acceptance testing

---

## Example

```yaml
phase_id: PHASE-002
title: 'User Authentication'
description: |
  Implement secure user authentication with JWT tokens.
  - Login/logout functionality
  - Session management
  - Password reset flow
  Out of scope: OAuth, MFA (future phases)

status: active

ns_alignment:
  goals: [GOAL-001, GOAL-003]
  features: [F-AUTH-001, F-AUTH-002]
  success_metrics:
    - "Users can log in within 2 seconds"
    - "Session timeout after 30 minutes of inactivity"

bedrock_analysis:
  existing_patterns:
    - pattern: "Express middleware chain"
      location: "src/middleware/"
      relevance: "Auth middleware will integrate here"
    - pattern: "Prisma for database access"
      location: "src/db/"
      relevance: "User model already exists, needs password field"

  files_affected:
    modify:
      - src/db/schema.prisma
      - src/middleware/index.ts
      - src/routes/index.ts
    create:
      - src/middleware/auth.ts
      - src/routes/auth.ts
      - src/services/auth.service.ts
    delete: []

  constraints:
    - constraint: "Must use existing User model"
      source: "Database schema already in production"
      impact: "Add fields via migration, don't restructure"
    - constraint: "API response format must match existing"
      source: "Frontend expects { data, error } shape"
      impact: "Auth endpoints follow same pattern"

  code_dependencies:
    internal: [src/db, src/utils/validation]
    external: [bcrypt, jsonwebtoken]

tasks:
  - id: TASK-002-01
    title: 'Database schema update'
    description: 'Add password hash and refresh token fields to User'
    estimated_complexity: low
    task_plan_path: null

  - id: TASK-002-02
    title: 'Auth service implementation'
    description: 'JWT generation, validation, refresh logic'
    estimated_complexity: medium
    task_plan_path: null

  - id: TASK-002-03
    title: 'Auth middleware'
    description: 'Route protection and token extraction'
    estimated_complexity: medium
    task_plan_path: null

  - id: TASK-002-04
    title: 'Auth routes'
    description: 'Login, logout, refresh, password reset endpoints'
    estimated_complexity: high
    task_plan_path: null

validation_gates:
  automated:
    - gate: "Unit tests pass"
      command: "npm test -- --grep auth"
      required: true
    - gate: "No TypeScript errors"
      command: "npm run typecheck"
      required: true

  manual:
    - gate: "Security review"
      reviewer: "Senior developer"
      required: true

  acceptance:
    - criteria: "User can log in with valid credentials"
      verification: "Manual test with test account"
    - criteria: "Invalid credentials show appropriate error"
      verification: "Test with wrong password"

dependencies:
  phases: [PHASE-001]
  external: []
  blockers: []

outputs:
  artifacts:
    - Auth middleware
    - Auth service
    - Auth routes
  documentation:
    - API docs for auth endpoints
    - Security considerations doc
  downstream_unlocks: [PHASE-003, PHASE-004]
```

---

## Checklist

Before marking a Phase Roadmap complete:

- [ ] `phase_id` matches ROADMAP.yaml
- [ ] `ns_alignment` references valid NORTHSTAR goals
- [ ] `bedrock_analysis` based on actual codebase exploration
- [ ] All `files_affected` verified to exist (for modify/delete)
- [ ] `tasks` are atomic and testable
- [ ] `validation_gates` include both automated and manual checks
- [ ] `dependencies` accurately reflect blocking relationships
