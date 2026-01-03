# H-Claude Workflow Guide

Practical guide to using H-Claude's planning and execution system.

---

## 1. The Big Picture

H-Claude separates WHAT you're building from HOW you build it:

```
NORTHSTAR.md (WHAT)     →  User story, goals, requirements
     ↓ aligned with
ROADMAP.yaml (HOW)      →  Development phases, execution order
     ↓ links to
Phase Think-Tanks       →  Detailed execution plans
     ↓ executed by
/hc-plan-execute        →  Code implementation with QA
```

**NORTHSTAR** is the destination. **ROADMAP** is the route.

---

## 2. Starting a New Project

### Step 1: Define NORTHSTAR

Fill out `.claude/PM/SSoT/NORTHSTAR.md`:

```markdown
## Purpose
What does this project do and why?

## Vision
What will it become? What value does it provide?

## Goals
1. **User Authentication** - Secure login with OAuth2
2. **API Gateway** - Rate limiting, caching, routing
3. **Dashboard** - Real-time metrics visualization

## Constraints
- Budget: $500/month infrastructure
- Team: Solo developer
- Timeline: MVP needed for investor demo

## Non-Goals
- Mobile app (web-first)
- Multi-tenancy (single org for now)
```

**Required sections:** Purpose, Vision, Goals (with specifics). Without these, `/think-tank --roadmap` will abort.

### Step 2: Create ROADMAP

Run:
```
/think-tank --roadmap
```

The council will:
1. Read your NORTHSTAR
2. Analyze goals and constraints
3. Break down into logical phases
4. Define dependencies (what blocks what)
5. Output `ROADMAP.yaml`

**Example output:**
```yaml
phases:
  - id: PHASE-001
    title: 'Foundation'
    status: planned
    description: 'Core infrastructure - auth, database, base API'
    dependencies: []      # Can start immediately
    plan_path: null       # Populated when phase is planned

  - id: PHASE-002
    title: 'API Gateway'
    status: planned
    dependencies: [PHASE-001]  # Blocked until Foundation done
    plan_path: null

  - id: PHASE-003
    title: 'Dashboard MVP'
    status: planned
    dependencies: [PHASE-002]
    plan_path: null
```

**Review options:**
- `APPROVE` - Accept the roadmap
- `ADJUST` - Modify phases, dependencies, descriptions
- `ADD_PHASE` - Add missing phases

---

## 3. Planning a Phase

### Validate Dependencies First

Before planning PHASE-002, ensure PHASE-001 is complete. The system checks this:

```
❌ Phase PHASE-002 has unmet dependencies: [PHASE-001]
These phases must be complete before starting PHASE-002.
```

### Run Phase Planning

```
/think-tank "API Gateway" --phase=PHASE-002
```

The council will:
1. Validate phase exists in ROADMAP
2. Read NORTHSTAR for context
3. Create workspace: `.claude/PM/think-tank/api_gateway_20260102/`
4. Discuss implementation approach
5. Output `execution-plan.yaml`

**Workspace created:**
```
.claude/PM/think-tank/api_gateway_20260102/
├── 00_BRIEFING.md           # Problem statement
├── 01_CAST.md               # Expert personas
├── 02_KNOWLEDGE_BASE/       # Research
├── 03_SESSIONS/             # Discussion transcripts
├── 04_DECISION_MAP.md       # Options with trade-offs
├── STATE.yaml               # Session tracking
└── execution-plan.yaml      # Ready for execution
```

**ROADMAP gets updated:**
```yaml
- id: PHASE-002
  title: 'API Gateway'
  plan_path: .claude/PM/think-tank/api_gateway_20260102/execution-plan.yaml
```

### execution-plan.yaml Structure

```yaml
plan:
  title: 'API Gateway Implementation'
  phases:
    - id: 1
      title: 'Rate Limiting'
      tasks:
        - id: TASK-1.1
          description: 'Implement token bucket algorithm'
          files: ['src/middleware/rate-limit.ts']
          success_criteria: 'Rate limit tests pass'
          dependencies: []
        - id: TASK-1.2
          description: 'Add Redis backend for distributed limiting'
          files: ['src/services/redis.ts', 'src/middleware/rate-limit.ts']
          dependencies: [TASK-1.1]
    - id: 2
      title: 'Caching Layer'
      tasks:
        - id: TASK-2.1
          description: 'Implement cache middleware'
          dependencies: [TASK-1.2]  # Needs Redis
```

---

## 4. Executing a Phase

### Create Checkpoint First

Before execution, the system creates a rollback point:

```
[CHECKPOINT] Created at abc123. Rollback: git reset --hard abc123
```

### Run Execution

```
/hc-plan-execute PLAN_PATH: .claude/PM/think-tank/api_gateway_20260102/execution-plan.yaml
```

Or by topic:
```
/hc-plan-execute TOPIC: api_gateway
```

**Modes:**
| Mode | Workers | Use Case |
|------|---------|----------|
| `standard` | 3 parallel | Most work |
| `careful` | 2 parallel | High-risk changes |

### Execution Flow

```
Phase 0: CHECKPOINT        →  Git commit for rollback
Phase 1: PARSE & CONTRACT  →  Extract tasks, create INTERFACES.md
Phase 2: EXECUTE           →  Oraca[X] spawns workers, Phase QA
Phase 3: QA SYNTHESIS      →  Cross-phase analysis
Phase 4: SWEEP             →  Hunt the 15% that was missed
Phase 5: VALIDATION        →  Tests, linting, final report
Phase 6: ROADMAP SYNC      →  Mark phase complete, unlock next
```

### Session Folder

```
.claude/PM/hc-plan-execute/api_gateway_20260102/
├── EXECUTION_STATE.md       # Dashboard - current status
├── ORCHESTRATOR_LOG.md      # What happened
├── PHASE_1/
│   ├── WORKER_OUTPUTS/
│   │   ├── TASK_1_1_EVIDENCE.md
│   │   └── TASK_1_2_EVIDENCE.md
│   ├── PHASE_QA.md
│   └── PHASE_REPORT.md
├── ANALYSIS/
│   ├── QA_SYNTHESIS.md
│   └── SWEEP_REPORT.md
└── COMPLETION_REPORT.md
```

### On Success

ROADMAP.yaml auto-updates:
```yaml
- id: PHASE-002
  status: complete  # Was: active

active_phases: [PHASE-003]  # PHASE-003 now unlocked
```

### On Failure

Options presented:
- `RETRY_FAILED` - Re-run only failed tasks
- `ROLLBACK` - Restore to checkpoint
- `MANUAL` - You fix, then re-run

---

## 5. Dynamic Phase Management

Roadmaps evolve. A project might start with 4 phases and grow to 12.

### Adding Phases

**When:** New requirement discovered, scope expansion, side-quest promotes to phase.

```
/think-tank --add-phase "Payment Integration"
```

You'll be asked:
- Phase description
- Dependencies (which phases must complete first)
- Priority (where in sequence)

**ROADMAP updated:**
```yaml
- id: PHASE-005
  title: 'Payment Integration'
  status: planned
  dependencies: [PHASE-002]  # Needs API Gateway first
  plan_path: null
```

### Removing Phases

**When:** Phase no longer needed, scope reduction.

```
/think-tank --remove-phase=PHASE-004
```

**If other phases depend on it:**
```
⚠️ PHASE-002, PHASE-003 depend on PHASE-004

Options:
- CASCADE - Remove dependents too
- REASSIGN - Move deps to another phase
- CANCEL - Keep the phase
```

**Removed phases archive:**
```yaml
archived_phases:
  - id: PHASE-004
    title: 'Removed Feature'
    archived: '2026-01-02'
    reason: 'Scope reduction'
```

### Reordering Phases

Run on existing roadmap:
```
/think-tank --roadmap --new-info "Dependencies changed because..."
```

Council re-analyzes, reorders while preserving completed phases.

### Scope Change Protocol

When new info changes scope:

1. **Affects NORTHSTAR?** → Update NORTHSTAR first
2. **Adds work?** → `--add-phase`
3. **Removes work?** → `--remove-phase`
4. **Changes order?** → Re-run `--roadmap`

```
/think-tank --roadmap --new-info "Scope change: Client now needs OAuth2 instead of API keys"
```

### Phase Count Philosophy

```
Initial:       4 phases  (high-level buckets)
After Phase 1: 6 phases  (split complex phase)
After Phase 3: 8 phases  (new requirements)
After review:  10 phases (scope expanded)
After cut:     8 phases  (2 merged as redundant)
```

Rules:
- Phase count is DYNAMIC - reflects reality
- Add phases when work is discovered
- Remove phases when not needed
- Dependencies are the constraint, not count
- Each phase: 1-3 days of work

---

## 6. Recovery

### Checkpoint / Rollback

Every `/hc-plan-execute` creates a checkpoint BEFORE execution:

```yaml
# EXECUTION_STATE.md
checkpoint:
  id: chkpt-20260102-143000-api-gateway
  commit_hash: abc123
  rollback_cmd: 'git reset --hard abc123'
```

**Manual rollback:**
```bash
git reset --hard abc123
```

**Automated rollback (if execution fails):**
Select `ROLLBACK` option → git-engineer restores checkpoint.

### Crash Recovery

If session crashes mid-execution:

1. EXECUTION_STATE.md shows last state:
   ```yaml
   status: in_progress
   current_phase: 2
   completed_tasks: [TASK-1.1, TASK-1.2, TASK-2.1]
   checkpoint:
     hash: abc123
   ```

2. Resume:
   ```
   /hc-plan-execute --resume api_gateway_20260102
   ```

3. System continues from last checkpoint, skips completed tasks.

### Partial Failure

If SWEEP finds gaps or QA fails:

1. COMPLETION_REPORT shows what failed
2. Options:
   - `RETRY_FAILED` - Re-run only failed tasks
   - `ROLLBACK` - Full restore
   - `MANUAL` - Fix yourself, re-run

ROADMAP status stays unchanged until phase fully passes.

### Hotfix During Execution

If urgent fix needed:

1. Complete current task (don't interrupt)
2. Make hotfix commit outside execution flow
3. Resume execution - state preserved
4. Hotfix changes won't roll back if execution fails

---

## Quick Reference

| Task | Command |
|------|---------|
| Fill out requirements | Edit `.claude/PM/SSoT/NORTHSTAR.md` |
| Create development roadmap | `/think-tank --roadmap` |
| Add a new phase | `/think-tank --add-phase "Title"` |
| Remove a phase | `/think-tank --remove-phase=PHASE-XXX` |
| Plan a specific phase | `/think-tank "Title" --phase=PHASE-XXX` |
| Execute a plan | `/hc-plan-execute PLAN_PATH: ...` |
| Execute by topic | `/hc-plan-execute TOPIC: topic_name` |
| Resume crashed execution | `/hc-plan-execute --resume session_slug` |
| Ad-hoc research | `/think-tank "Research Topic"` |
| Code review | `/hc-glass` |
| Deep investigation | `/red-team` |

---

## File Locations

| File | Purpose |
|------|---------|
| `.claude/PM/SSoT/NORTHSTAR.md` | WHAT - User story |
| `.claude/PM/SSoT/ROADMAP.yaml` | HOW - Development phases |
| `.claude/PM/SSoT/ADRs/` | Architectural decisions |
| `.claude/PM/think-tank/` | Think-tank session workspaces |
| `.claude/PM/hc-plan-execute/` | Execution session artifacts |
| `.claude/context.yaml` | Session state |
| `.claude/PM/CHANGELOG.md` | Change history |

---

*Version: 1.0.0 | Updated: 2026-01-02*
