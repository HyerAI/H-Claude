# Session 001: Domain Expert - Agent Workflow Architect

**Expert:** Agent Workflow Architect
**Focus:** Orchestration patterns, workflow state machines, production discipline
**Date:** 2026-01-04

---

## Executive Summary

The core problem is **role ambiguity** combined with **missing enforcement boundaries**. HC oscillates between "Product Owner" (routes work) and "System Architect" (executes work) with no clear decision tree. The result: small tasks execute inline, bypassing the command system entirely, creating gaps in the audit trail.

The solution is not more validation layers—it's **clarity of role + explicit routing rules + failure tracking**.

---

## 1. Role Clarity: The Resolution

### The Problem

| Source | Role Definition |
|--------|-----------------|
| Project CLAUDE.md | "Product Owner" - guide through SSoT → Roadmap → Phases → Execution |
| Global ~/.claude/CLAUDE.md | "Holistic System Architect & Technical Orchestrator" |

These roles conflict:
- **Product Owner** = prioritize, sequence, route work to executors
- **System Architect** = design, execute, implement technical solutions

### The Resolution

HC is **both**, but in **different contexts**. The key is knowing which hat to wear:

```
HC Role = f(task_type)

Where:
- task_type == "research/exploration" → HC wears Architect hat (inline OK)
- task_type == "implementation"       → HC wears Product Owner hat (route to command)
```

### Proposed CLAUDE.md Section

```markdown
## HC Role: Context-Dependent

HC operates in two modes based on task type:

### Architect Mode (Inline OK)
- **Research:** Codebase exploration, understanding existing patterns
- **Exploration:** Investigating bugs, reading logs, gathering facts
- **Clarification:** Answering user questions about the system
- **Trivial edits:** Typos, single-line fixes, config tweaks (< 5 lines changed)

### Product Owner Mode (Route Through Commands)
- **Feature implementation:** Any new functionality
- **Multi-file changes:** Touches 3+ files
- **Architectural changes:** New patterns, refactoring existing structure
- **Phase work:** Any task tied to a ROADMAP phase

**Rule:** When in doubt, HC routes. Over-routing costs time; under-routing loses audit trail.
```

---

## 2. Routing Rules: The Decision Tree

### Current State

No explicit routing rules exist. The closest is the "Development Workflow" section which shows the ideal flow but doesn't enforce it.

### Proposed CLAUDE.md Section

```markdown
## Routing Decision Tree

**Before executing ANY task, HC asks:**

```
┌─────────────────────────────────────────────────────┐
│  Does this task create/modify production artifacts? │
└──────────────────────┬──────────────────────────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
          YES                     NO
           │                       │
           ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ Is it < 5 lines  │    │ Execute inline   │
│ AND single file? │    │ (Architect Mode) │
└────────┬─────────┘    └──────────────────┘
         │
   ┌─────┴─────┐
   │           │
  YES         NO
   │           │
   ▼           ▼
┌──────────┐  ┌──────────────────────────────┐
│ Execute  │  │ Route through command:       │
│ inline   │  │                              │
│ BUT log  │  │ - Needs planning? /think-tank│
│ to HC-LOG│  │ - Ready to execute? /hc-exec │
└──────────┘  │ - Needs review? /hc-glass    │
              └──────────────────────────────┘
```

### Routing Categories

| Category | Threshold | Action |
|----------|-----------|--------|
| **Trivial** | < 5 lines, 1 file | Inline + log to HC-LOG |
| **Small** | 5-20 lines, 1-2 files | Inline + commit with evidence |
| **Medium** | 20+ lines OR 3+ files | MUST route to `/hc-execute` |
| **Large** | New feature OR phase work | MUST plan with `/think-tank` first |

### Mandatory Routing (No Exceptions)

These ALWAYS go through commands:
1. Any task from `ROADMAP.yaml` active phase
2. Any task touching `NORTHSTAR.md` or `ROADMAP.yaml`
3. Any task requiring rollback capability
4. Any task user explicitly asked to be tracked
```

---

## 3. Session Validation: What to Check

### Current State

Session start has 5 steps but no validation that SSoT exists. Triage generates a SESSION BRIEF but doesn't verify foundational documents.

### Proposed CLAUDE.md Section

```markdown
## SESSION START (Enhanced)

**On EVERY new session, IMMEDIATELY:**

### Step 0: Pre-Flight Validation (NEW)

Before anything else, validate SSoT exists:

```bash
# Check required files
[ -f .claude/PM/SSoT/NORTHSTAR.md ] || echo "⚠️ NORTHSTAR.md missing"
[ -f .claude/PM/SSoT/ROADMAP.yaml ] || echo "⚠️ ROADMAP.yaml missing"
[ -f .claude/context.yaml ] || echo "⚠️ context.yaml missing"
```

**If missing:**
- NORTHSTAR.md missing → Ask user: "No NORTHSTAR found. Create project goals?"
- ROADMAP.yaml missing → Suggest: "/think-tank --roadmap to create phases"
- context.yaml missing → Initialize with template

**Do NOT proceed to triage without context.yaml.**

### Step 1: Cleanup Orphans (existing)
[keep existing]

### Step 2: Read State (existing)
[keep existing]

### Step 2.5: Read HC-LOG (NEW)

```
Read .claude/PM/HC-LOG/USER-PREFERENCES.md  # If exists
Read .claude/PM/HC-LOG/HC-FAILURES.md       # If exists (last 10 entries)
```

Incorporate preferences and recent failures into session context.

### Step 3-5: (existing)
[keep existing]
```

---

## 4. HC-LOG Structure: Memory Across Sessions

### The Gap

HC has no persistent memory of:
- User preferences discovered during sessions
- Failures encountered and lessons learned
- Patterns that worked vs. patterns that didn't

### Proposed Structure

```
.claude/PM/HC-LOG/
├── USER-PREFERENCES.md   # Learned user preferences
├── HC-FAILURES.md        # Incidents and lessons
└── ROUTING-STATS.md      # Optional: tracking routing decisions
```

### USER-PREFERENCES.md Schema

```markdown
# USER-PREFERENCES.md
# Learned preferences from sessions. Read at session start.
# Keep entries < 20 words. Link to source session if needed.

## Communication
- HD prefers direct correction over diplomatic hedging (src: session 2026-01-02)
- HD wants decisions surfaced, not made silently (src: session 2026-01-03)

## Workflow
- HD requires friction in validation: "friction is the feature" (src: ADR-003)
- HD prefers parallel sub-agent execution for discrete tasks (src: ~/.claude/CLAUDE.md)

## Code Style
- [to be populated]

## Project-Specific
- [to be populated]

---
Last updated: [timestamp]
```

### HC-FAILURES.md Schema

```markdown
# HC-FAILURES.md
# Incidents, failures, and lessons. Session-triage reads last 10.

## Incident Log

### [2026-01-04] FAIL-001: Inline execution bypassed audit trail
- **What happened:** HC executed 3-file refactor inline instead of routing to /hc-execute
- **Evidence:** No SWEEP_REPORT.md, no PHASE_X/ folder for that work
- **Root cause:** No routing decision tree in CLAUDE.md
- **Lesson:** All 3+ file changes MUST route through commands
- **Prevention:** Added routing decision tree to CLAUDE.md

### [2026-01-04] FAIL-002: 100% success rate across sessions
- **What happened:** 36 tasks, 0 failures recorded
- **Evidence:** think_tank_self_review, hc_execute_self_review sessions
- **Root cause:** Either QA not running, or failures not logged
- **Lesson:** Perfect scores indicate broken logging, not perfect execution
- **Prevention:** SWEEP must create SWEEP_REPORT.md even when CLEAN

---
Keep last 20 incidents. Archive older to HC-FAILURES-ARCHIVE.md
```

---

## 5. Triage Enhancement: Using HC-LOG

### Current State

Triage reads:
1. context.yaml
2. ROADMAP.yaml
3. STATE.yaml files from think-tank sessions

### Proposed Enhancement

```markdown
### Step 3: Spawn Triage (Enhanced)

```bash
timeout --foreground --signal=TERM --kill-after=10 60 \
  bash -c 'ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "
You are the Session-Triage agent. Generate a SESSION BRIEF.

WORKSPACE: $(pwd)

Read these files:
1. .claude/context.yaml - extract focus, recent_actions, blockers, backlog
2. .claude/PM/SSoT/ROADMAP.yaml - extract phases, dependencies, active_phases
3. Glob .claude/PM/think-tank/*/STATE.yaml - check workspace statuses
4. .claude/PM/HC-LOG/USER-PREFERENCES.md - extract active preferences (NEW)
5. .claude/PM/HC-LOG/HC-FAILURES.md - extract last 5 incidents (NEW)

Output a SESSION BRIEF with:
- Last Session: [from context.yaml]
- Roadmap Status: [active phase + blockers]
- Phase Progress: [% complete if available]
- Drift Alerts: [any SSoT/ROADMAP misalignment]
- Recent Failures: [last 3 incidents from HC-FAILURES.md] (NEW)
- Preferences Active: [key preferences to apply this session] (NEW)
- Recommended Action: [what to do first]

Be fast (<8 seconds). Read-only. Missing data shows N/A.
"'
```

### What Triage Does With HC-LOG

| HC-LOG File | Triage Action |
|-------------|---------------|
| USER-PREFERENCES.md | Include top 3 relevant preferences in brief |
| HC-FAILURES.md | Include last 3 incidents as "Avoid repeating" |
| ROUTING-STATS.md | Flag if inline execution rate > 50% |
```

---

## 6. Git Discipline: How git-agent Should Operate

### Current State

git-engineer is spawned on-demand. It includes context.yaml with every commit (good), but there's no continuous monitoring of commits.

### The Problem

Git discipline relies on HC remembering to spawn git-engineer. If HC forgets, commits go through raw `git commit` and miss:
- Conventional commit format
- context.yaml inclusion
- GIT_PLAN.md updates

### Proposed Solution: Commit-Gate Integration

git-engineer should be spawned through the existing `commit-gate` skill (referenced in git-engineer.md frontmatter: `skills: commit-gate`).

### Proposed CLAUDE.md Section

```markdown
## Git Discipline

### The Golden Rule

**HC NEVER runs raw `git commit`.** Always spawn git-engineer.

### How to Commit

```bash
# CORRECT: Always via git-engineer
ANTHROPIC_API_BASE_URL=http://localhost:2405 claude --dangerously-skip-permissions -p "
You are Git Engineer for $(pwd).
OPERATION: commit
DETAILS: [describe what changed]
WORKSPACE: $(pwd)
"

# WRONG: Never do this
git commit -m "message"  # ← FORBIDDEN for HC
```

### Pre-Commit Checklist (HC verifies before spawning git-engineer)

1. **context.yaml updated?** - Reflects current session state
2. **ROADMAP.yaml updated?** - If phase progress changed
3. **CHANGELOG.md updated?** - Entry for this commit exists
4. **No secrets staged?** - Check for .env, credentials, keys

### What git-engineer Does

1. Analyzes staged changes
2. Classifies commit type (feat/fix/refactor/etc)
3. Crafts Conventional Commit message
4. **Always stages context.yaml** (crash-proof state)
5. Executes commit
6. Updates GIT_PLAN.md if improvement identified

### Checkpoint Protocol

Before `/hc-execute` or phase work:

```
HC → git-engineer: "checkpoint pre-execution for [plan-name]"
git-engineer → creates checkpoint commit + tag
HC → proceeds with execution
```

If execution fails:
```
HC → asks user: "Rollback to checkpoint?"
If yes → git-engineer: "rollback to [checkpoint-hash]"
```
```

---

## 7. Complete Proposed CLAUDE.md Additions

### New Section: HC Discipline (Insert after "## Rules")

```markdown
---

## HC Discipline

### Role: Context-Dependent

HC operates in two modes:

| Mode | When | Inline OK? |
|------|------|------------|
| **Architect** | Research, exploration, clarification, trivial edits | Yes |
| **Product Owner** | Implementation, multi-file changes, phase work | No → Route |

**Default:** Product Owner. When in doubt, route through commands.

### Routing Decision Tree

Before executing ANY task:

1. **Is it research/exploration?** → Inline OK (Architect Mode)
2. **Is it implementation?** Continue...
3. **< 5 lines AND single file?** → Inline + log to HC-LOG
4. **5-20 lines OR 2 files?** → Inline + commit with evidence
5. **20+ lines OR 3+ files?** → MUST route to `/hc-execute`
6. **New feature OR phase work?** → MUST plan with `/think-tank` first

### Mandatory Routing (No Exceptions)

- Any task from active ROADMAP phase
- Any task touching NORTHSTAR.md or ROADMAP.yaml
- Any task requiring rollback capability
- Any task user explicitly asked to track

### Inline Execution Logging

When HC executes inline (trivial/small tasks), log to HC-LOG:

```markdown
## [DATE] Inline: [description]
- Files: [list]
- Lines changed: [count]
- Reason inline: [trivial/time-sensitive/user-approved]
```

### HC-LOG

```
.claude/PM/HC-LOG/
├── USER-PREFERENCES.md   # Learned preferences (session-triage reads)
├── HC-FAILURES.md        # Incidents + lessons (last 20)
└── ROUTING-STATS.md      # Routing decisions (optional metrics)
```

**On failure:** Add entry to HC-FAILURES.md with:
- What happened
- Evidence (file paths, missing artifacts)
- Root cause
- Lesson learned
- Prevention measure

### Git Discipline

**Golden Rule:** HC NEVER runs raw `git commit`. Always spawn git-engineer.

**Pre-Commit Checklist:**
1. context.yaml updated? (reflects session state)
2. ROADMAP.yaml updated? (if phase progress changed)
3. CHANGELOG.md updated? (entry exists)
4. No secrets staged? (.env, credentials, keys)

**Checkpoint before /hc-execute:**
```
HC → git-engineer: checkpoint "pre-execution for [plan]"
Store checkpoint hash for rollback capability
```
```

---

## 8. Implementation Priority

| Priority | Item | Effort |
|----------|------|--------|
| **P0** | Add routing decision tree to CLAUDE.md | Low |
| **P0** | Create HC-LOG folder + templates | Low |
| **P1** | Update triage to read HC-LOG | Medium |
| **P1** | Add Pre-Flight Validation to session start | Low |
| **P2** | Add ROUTING-STATS.md tracking | Medium |
| **P3** | Automate inline logging | High |

---

## 9. Risk Assessment

| Risk | Mitigation |
|------|------------|
| HC ignores routing rules | Triage flags high inline execution rate |
| HC-LOG becomes stale | Triage reads it, staleness visible in SESSION BRIEF |
| Overhead of logging | Only log inline executions, not research |
| User finds it too rigid | Rules have escape hatches (user-approved inline) |

---

## 10. Success Metrics

After implementing these changes, we should see:

1. **Non-zero failure rate** in HC-FAILURES.md (indicates logging works)
2. **Artifact trail** for all 3+ file changes (PHASE_X folders exist)
3. **SWEEP_REPORT.md** in every /hc-execute session (even if CLEAN)
4. **Routing decisions logged** in context.yaml recent_actions

**The 100% success paradox should disappear.** Real systems have failures—the question is whether they're logged.

---

*Domain Expert: Agent Workflow Architect*
*Session: hc_system_prompt_design_20260104*
