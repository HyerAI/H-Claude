# /genesis

Bootstrap skill for new HD sessions. Auto-detects project state and routes to appropriate mode.

## Trigger

HD loads this skill when:
- Session starts and HD needs to establish context
- User says "new project", "start fresh", "let's begin"
- No active interview session exists

## State Protocol

### On Entry

1. **Auto-Detection Scan** (BEFORE any user interaction):
   ```
   Scan for:
   - $SSOT/NORTHSTAR.md → exists? has goals defined?
   - queue.json → exists? has pending tasks?
   - Code files in project root (*.py, *.ts, *.js, etc.)
   - $TEMP/interview-session.yaml → interrupted session?
   ```

   **File Read Validation:**
   - IF NORTHSTAR exists but unreadable/corrupted → treat as BROWNFIELD with warning
   - Warning format: "NORTHSTAR found but unreadable. Treating as BROWNFIELD to reconstruct vision."

2. **Route Selection** (deterministic, no user input needed):

   | Condition | Route | User Interaction |
   |-----------|-------|------------------|
   | NORTHSTAR exists with goals | ACTIVE | Auto-proceed |
   | queue.json has tasks | RECOVERY | Auto-proceed |
   | Code exists, no NORTHSTAR | BROWNFIELD | Auto-proceed |
   | None of above | GREENFIELD | Ask user to confirm |

   **Priority Order** (when multiple conditions match):
   1. **RECOVERY** (queue.json has tasks) - takes precedence (unfinished work)
   2. **ACTIVE** (NORTHSTAR exists with goals) - existing project context
   3. **BROWNFIELD** (code exists, no NORTHSTAR) - needs vision
   4. **GREENFIELD** (none of above) - fresh start

3. **Load existing session** (if exists):
   - Read `$TEMP/interview-session.yaml`
   - Restore phase, entities, pending decisions

4. **Validate session schema**:
   - IF session file exists but `schema_version` missing or != '1.0':
     - Prompt: "Session format outdated or invalid. Reset session? (yes/no)"
     - IF yes: Initialize fresh session, preserve any extractable entities
     - IF no: Attempt best-effort parse with warning: "Proceeding with potentially incompatible session"
   - IF required fields missing (`current_phase`, `genesis` section):
     - Treat as BROWNFIELD with warning: "Corrupted session detected, starting fresh"

### On Exit

1. Update session:
   ```yaml
   genesis:
     mode: <detected_route>
     detected_at: <timestamp>
     auto_proceeded: true|false
   ```
2. Write session file
3. Output summary with next steps

### Skill Transition

ON transition_to(skill_name):
1. Save current session state
2. HD must `read_file('.claude/skills/{skill_name}.md')`
3. Execute loaded skill

---

## Routes

### GREENFIELD (Fresh Start)

**Condition:** No NORTHSTAR, no queue, no significant code.

> **Significant code:** 3+ source files with extensions: `.py`, `.js`, `.ts`, `.tsx`, `.go`, `.rs`, `.java`, `.rb`, `.c`, `.cpp`, `.h`. Config files (`.json`, `.yaml`, `.toml`, `.xml`) do NOT count.

**Behavior:**
1. Confirm with user: "This looks like a fresh start. Ready to define your project vision?"
2. On confirm → transition to `/diamond-diverge` for open exploration
3. On decline:
   - Prompt: "What would you like to do instead?"
   - Options: exit session, specify file to work on, get help
   - Update session: `genesis.declined = true`

**Opening Question:**
> What are you building? Give me the elevator pitch.

**Goals to extract:**
- Project purpose (1 sentence)
- Target users
- Core problem being solved
- Initial scope boundaries

---

### BROWNFIELD (Archaeology Mode)

**Condition:** Code exists but no NORTHSTAR.

**Behavior:** Auto-proceed without asking.

**Archaeology Scan:**
1. Identify project type (Python/JS/TS/Go/etc.)
2. Scan for patterns:
   - README.md → project description
   - package.json / pyproject.toml → dependencies, name
   - Test files → existing coverage
   - Directory structure → architecture clues
3. Generate preliminary entity/action list from code

**Scan Limits:**
- Max files: 1000
- Timeout: 30 seconds
- On scan failure → prompt for manual project description:
  "Scan incomplete. Please describe your project in a few sentences."

**Opening Statement:**
> I see an existing codebase. Let me scan it to understand what you've built.

**Then output:**
```
Found:
- Project: {name from config}
- Type: {language/framework}
- Files: {count}
- Detected entities: {list top 5}
- Detected actions: {list top 5}

I'll draft a NORTHSTAR based on what I found. You can refine it with me.
```

**Next step:** Draft preliminary NORTHSTAR.md → user reviews → then `/diamond-converge` to prioritize.

---

### RECOVERY (Interrupted Session)

**Condition:** queue.json has pending tasks.

**Behavior:** Auto-proceed without asking.

**Recovery Scan:**
1. Load queue.json
2. Identify:
   - Tasks in-progress (stuck?)
   - Tasks pending
   - Tasks completed since last session
3. Check for stale worktrees
   - **Stale definition:** worktree older than 7 days with no commits
   - Action: list stale worktrees, prompt for cleanup

**Opening Statement:**
> I found an interrupted session. Let me show you where we left off.

**Then output:**
```
Session state:
- Pending tasks: {count}
- In-progress: {task_id} - {description}
- Last activity: {timestamp}

Recommendation: {continue / reset specific task / abort}
```

**Options:**
- **Continue** → Resume queue processing via `/hc-execute`
- **Reset task** → Mark stuck task as failed, retry
- **Abort** → Clear queue, return to planning

---

### ACTIVE (Project Has Vision)

**Condition:** NORTHSTAR exists with defined goals.

**Behavior:** Auto-proceed without asking.

**Active Scan:**
1. Load NORTHSTAR.md
2. Parse goals, constraints, non-goals
3. Check ROADMAP.yaml for current phase
4. Check queue.json for active work

**Opening Statement:**
> Project "{name}" is active. Here's the current state.

**Then output:**
```
NORTHSTAR: {project_name}
Current Phase: {from ROADMAP or "not started"}
Queue: {task count pending/in-progress/done}
Last commit: {from git log}

What would you like to do?
```

**Options presented (based on state):**
- Active tasks exist → "Continue execution?"
- No tasks → "Plan next phase?"
- Phase complete → "Review and close phase?"

---

## Detection Techniques

### Code Detection Heuristics

```
Priority order:
1. pyproject.toml / setup.py → Python
2. package.json → JavaScript/TypeScript
3. go.mod → Go
4. Cargo.toml → Rust
5. *.py / *.js / *.ts files in root or src/ → fallback

Minimum threshold: 3+ source files (see GREENFIELD for extension list)
```

### NORTHSTAR Validity Check

NORTHSTAR is considered "valid with goals" if it contains:
- `## Goals` or `## Purpose` section
- At least one non-empty bullet point under that section (not just `- ` or whitespace)

**"Goals defined"** = `## Goals` section exists with at least one non-empty bullet.

Invalid NORTHSTAR (empty template) → treat as GREENFIELD.

### Queue State Classification

```yaml
# queue.json states
empty: []              → No work (ACTIVE but idle)
pending_only:          → Work planned, not started
has_in_progress:       → Work interrupted (RECOVERY)
all_completed:         → Session finished successfully
```

---

## Exit Conditions

Genesis completes when:

1. **GREENFIELD:** User confirms project scope → session updated → hand off to `/diamond-diverge`
2. **BROWNFIELD:** Preliminary NORTHSTAR drafted → user reviewed → hand off to `/diamond-converge`
3. **RECOVERY:** User chose action (continue/reset/abort) → session updated → hand off to appropriate handler
4. **ACTIVE:** User chose action → session updated → hand off to chosen skill/command

---

## Session State Updates

On genesis completion, write to `$TEMP/interview-session.yaml`:

```yaml
session_id: "{ISO timestamp}"
genesis:
  mode: greenfield|brownfield|recovery|active
  detected_at: "{timestamp}"
  auto_proceeded: true|false

  # Mode-specific data:
  brownfield_scan:
    project_type: python
    file_count: 47
    entities_detected: [...]

  recovery_state:
    queue_pending: 3
    stuck_task: "TASK-007"

  active_state:
    current_phase: "Phase-2"
    queue_status: "2 pending, 1 in-progress"

current_phase: diverge|converge|synthesize|complete
extracted_entities: []
last_updated: "{timestamp}"
```

---

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Ask "which mode?" for BROWNFIELD/RECOVERY/ACTIVE | Auto-detect and proceed |
| Announce "running genesis detection..." | Just do it silently, show results |
| Show raw file paths during scan | Summarize findings in human terms |
| Force GREENFIELD interview on BROWNFIELD | Adapt questions to existing context |
| Ignore stuck queue tasks | Surface them prominently in RECOVERY |

### Common Anti-Patterns (per ADR-002)

- Never announce methods ("I'm detecting project type...")
- Never announce skills ("Loading genesis skill...")
- Never use threshold gates ("Need to scan 5 more files...")
- Always output artifact links (never hidden artifacts)

---

## Example Flows

### GREENFIELD Example
```
HD: (scans silently)
HD: This looks like a fresh start. What are you building?
User: A task management app for developers
HD: Got it - task management for devs. Tell me more about the problem you're solving...
→ transitions to /diamond-diverge
```

### BROWNFIELD Example
```
HD: (scans silently)
HD: I see an existing Python project. Let me analyze it.
HD: Found: FastAPI backend with 12 endpoints, SQLAlchemy models for User, Task, Project...
HD: I'll draft a NORTHSTAR from this. Here's what I understand:
    [shows draft]
HD: Does this capture your project's purpose?
→ user refines → transitions to /diamond-converge
```

### RECOVERY Example
```
HD: (scans silently)
HD: Found an interrupted session. Task "TASK-012: Add auth" was in-progress.
HD: Last activity: 2 hours ago. 3 tasks still pending.
HD: Continue where we left off?
User: Yes
→ transitions to /hc-execute
```

### ACTIVE Example
```
HD: (scans silently)
HD: Project "H-Conductor" is active.
    Phase 13 in progress. Queue: 2 pending, 0 in-progress.
HD: Ready to continue Phase 13 execution?
User: Show me the pending tasks first
HD: [shows queue summary]
→ user directs next action
```

---
*Skill Version: 1.0.0*
*Architecture: ADR-002 HD Composition*
*Specification: `$SSOT/HD_INTERFACE.md`*
