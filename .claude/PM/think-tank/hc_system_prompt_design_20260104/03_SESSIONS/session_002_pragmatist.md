# Session 002: Pragmatist - Developer Experience Guardian

**Expert:** Developer Experience Guardian
**Focus:** Over-engineering detection, real-world survivability, implementation friction
**Date:** 2026-01-04

---

## Executive Summary

The Domain Expert proposal is academically sound but **operationally bloated**. It creates new maintenance burdens (HC-LOG), introduces cognitive overhead (mode-switching), and relies on HC self-policing behaviors it currently ignores. The proposal treats symptoms (missing artifacts) with process (more logging) when the root cause is simpler: **HC doesn't use the commands because they're slower than inline execution.**

Fix the incentive structure, not the monitoring structure.

---

## 1. Role Clarity: The Reality Check

### What the Proposal Says

HC is "both" Product Owner and Architect, switching based on `task_type`.

### What Will Actually Happen

HC won't reliably switch. Every session will look like this:

```
User: "Fix this bug"
HC (thinking): "Is this Architect mode or PO mode?"
HC (thinking): "It's just a bug fix... probably Architect?"
HC (acting): Fixes inline
HC (not doing): Logging to HC-LOG, checking routing rules
```

**The mode concept is cognitive overhead that HC will discard under time pressure.**

### My Counter-Proposal

Drop the dual-mode abstraction. Instead, one rule:

```markdown
## HC's Single Rule

If you're about to write code → check if this should be `/hc-execute`.

**Use /hc-execute when:**
- Touching 3+ files
- Creating new files
- Part of a ROADMAP phase
- User said "track this" or "do this properly"

**Everything else:** inline is fine, no logging required.
```

Why this works: Binary decision (command or not), no modes to track, no logging overhead for small tasks.

---

## 2. Routing Thresholds: Unrealistic

### The Proposal's Thresholds

| Category | Threshold | Action |
|----------|-----------|--------|
| Trivial | < 5 lines, 1 file | Inline + log |
| Small | 5-20 lines, 1-2 files | Inline + commit with evidence |
| Medium | 20+ lines OR 3+ files | MUST route |
| Large | New feature OR phase | MUST plan first |

### What's Wrong

1. **Line counts are hard to predict.** HC doesn't know it's a 25-line change until it's done. By then, the routing decision is moot.

2. **"Log to HC-LOG" for trivial tasks = never happens.** HC executes a 3-line fix, moves on. It won't stop to log.

3. **"Commit with evidence" for small tasks is undefined.** What evidence? Where?

### My Counter-Proposal

```markdown
## Routing Rule (Simplified)

**Route to /hc-execute if ANY is true:**
- 3+ files touched
- New file created
- Part of active ROADMAP phase
- User explicitly requested tracking

**Everything else: inline, no paperwork.**

Don't guess line counts. Count files—you know those upfront.
```

---

## 3. HC-LOG: The Maintenance Trap

### What the Proposal Wants

```
.claude/PM/HC-LOG/
├── USER-PREFERENCES.md   # Learned preferences
├── HC-FAILURES.md        # Incidents
└── ROUTING-STATS.md      # Optional metrics
```

### What Will Actually Happen

**Week 1:** HC diligently logs.
**Week 2:** USER-PREFERENCES.md has 3 entries. HC-FAILURES.md has 2.
**Week 3:** Logs become stale. HC forgets to update.
**Week 4:** Triage reads stale HC-LOG, presents outdated preferences.
**Week 5:** User notices stale data, loses trust.
**Week 6:** HC stops maintaining it entirely.

### Why HC-LOG Will Fail

1. **No enforcement.** Who checks if HC logged? Nobody.
2. **Low signal.** Most inline executions aren't worth logging.
3. **Double work.** context.yaml already has `recent_actions`. Why duplicate?
4. **Staleness is invisible.** How do you know preferences are outdated?

### My Counter-Proposal

**Kill HC-LOG entirely.** Instead:

1. **Failures:** Go in `BACKLOG.yaml` under a `# Incidents` section. Already tracked, already read at session start.

2. **Preferences:** Go in project CLAUDE.md under `## User Preferences`. Static, not log-style. Updated only when user explicitly states a preference.

3. **Routing stats:** Don't track. If you need metrics, you've already over-engineered.

```yaml
# In BACKLOG.yaml
incidents:
  - date: '2026-01-04'
    what: 'Inline execution bypassed audit trail'
    lesson: 'Route 3+ file changes to /hc-execute'
```

```markdown
# In CLAUDE.md
## User Preferences (Explicitly Stated)
- Prefers direct correction over diplomatic hedging
- Wants decisions surfaced via Decision Brief format
- Friction in validation is intentional
```

---

## 4. Triage Enhancement: Unnecessary Complexity

### What the Proposal Wants

Triage reads 5 files, outputs 7 fields, includes recent failures and preferences.

### What Will Actually Happen

Triage takes 8 seconds instead of 3. HC context gets polluted with old incident descriptions. User waits longer for greeting.

### My Counter-Proposal

**Don't enhance triage.** Current triage is fine:

- Reads context.yaml, ROADMAP.yaml, STATE.yaml
- Outputs: Last Session, Roadmap Status, Recommended Action

If you want failure awareness, HC reads BACKLOG.yaml anyway. Don't duplicate in triage.

---

## 5. Git Discipline: Already Good Enough

### What the Proposal Wants

- Pre-commit checklist (4 items)
- Checkpoint protocol before /hc-execute
- "HC NEVER runs raw git commit"

### What's Wrong

1. **Checkpoints before /hc-execute:** Over-engineering. If execution fails, `git reset --hard HEAD~1` works fine. You don't need a "checkpoint protocol."

2. **Pre-commit checklist:** HC already includes context.yaml (git-engineer does this). The rest is nice-to-have that HC will skip.

3. **"Never raw git commit":** Unenforceable. If HC does `git commit`, nothing stops it.

### My Counter-Proposal

Keep existing git-engineer behavior. Add one rule:

```markdown
## Git Rule

Always spawn git-engineer for commits. If you're tempted to run raw `git commit`, that's a sign you're in a hurry—stop and delegate.
```

Drop the checkpoint protocol. It's ceremony without value.

---

## 6. Pre-Flight Validation: Acceptable

### What the Proposal Says

Step 0: Check NORTHSTAR.md, ROADMAP.yaml, context.yaml exist.

### My Verdict

**This one's fine.** Low cost, prevents confusion on fresh projects. Keep it.

But simplify:

```bash
# Pre-flight (3 lines, not 7)
for f in NORTHSTAR.md ROADMAP.yaml context.yaml; do
  [ -f ".claude/PM/SSoT/$f" ] || [ -f ".claude/$f" ] || echo "Missing: $f"
done
```

Actually wait—context.yaml is at `.claude/context.yaml`, not SSoT. The proposal's paths are inconsistent. Fix that.

---

## 7. The "Just Do This Quickly" Problem

### What Happens When User Says This

```
User: "Just quickly add a log statement to debug this"
```

Under the proposal:
1. HC checks if it's research or implementation (mode-switch overhead)
2. HC counts files (1 file = OK)
3. HC estimates lines (<5 = trivial)
4. HC executes inline
5. HC logs to HC-LOG/INLINE-EXECUTIONS.md (friction)
6. HC moves on

**Reality:** HC does step 4, skips everything else.

### My Counter-Proposal

Acknowledge that "just quickly" is a valid escape hatch:

```markdown
## Escape Hatch: User Says "Quickly"

If user explicitly says "just do this quickly" or similar:
- Execute inline regardless of routing rules
- No logging required
- Trust the user knows what they want
```

The system should accommodate urgency, not fight it.

---

## 8. What Survives Real-World Use

| Proposal Item | Survives? | Why |
|---------------|-----------|-----|
| Dual mode (Architect/PO) | ❌ | Too abstract, forgotten under pressure |
| Line-count thresholds | ❌ | Unpredictable, creates decision fatigue |
| File-count threshold (3+) | ✅ | Simple, knowable upfront |
| HC-LOG folder | ❌ | Maintenance burden, will go stale |
| USER-PREFERENCES.md | ⚠️ | Move to CLAUDE.md as static section |
| HC-FAILURES.md | ⚠️ | Move to BACKLOG.yaml as incidents |
| Enhanced triage | ❌ | Over-complicated, slower |
| Pre-flight validation | ✅ | Low cost, high value |
| Git checkpoint protocol | ❌ | Ceremony without value |
| "Never raw git commit" | ⚠️ | Good intent, unenforceable |

---

## 9. My Simplified Counter-Proposal

### To Add to CLAUDE.md

```markdown
---

## HC Routing Rule

**Route to /hc-execute when ANY is true:**
- Touching 3+ files
- Creating new files
- Part of active ROADMAP phase
- User requested tracking

**Everything else: inline execution is fine.**

No logging required for inline work. No mode-switching. Count files, make decision.

### Escape Hatch

If user says "quickly" or "just do this"—execute inline regardless.

### Pre-Flight (Session Start)

Before triage, verify:
```bash
[ -f .claude/PM/SSoT/NORTHSTAR.md ] && [ -f .claude/PM/SSoT/ROADMAP.yaml ] && [ -f .claude/context.yaml ]
```
If missing, prompt user before proceeding.

---

## User Preferences (Explicitly Stated)

Update this section when user explicitly states a preference.

- Prefers direct correction over diplomatic hedging
- Wants decisions surfaced via Decision Brief format
- Friction in validation is intentional ("friction is the feature")
```

### What Not to Add

- HC-LOG folder (use BACKLOG.yaml for incidents, CLAUDE.md for preferences)
- Dual modes (Architect/PO)
- Line-count thresholds
- Triage enhancements
- Checkpoint protocol
- ROUTING-STATS.md

---

## 10. Summary: Cut the Fat

The Domain Expert built a monitoring system. What we need is a simpler decision rule.

**Root cause:** HC doesn't use commands because it's faster not to.

**Wrong fix:** Add logging so we know when HC skipped commands.

**Right fix:** Make the routing decision trivial (file count), accept that small work doesn't need tracking.

**The 100% success paradox** isn't about broken logging—it's about HC correctly identifying that most tasks don't need the heavy process. Let small tasks be small. Focus enforcement on the big stuff: 3+ file changes, phase work, new features.

---

*Pragmatist: Developer Experience Guardian*
*Session: hc_system_prompt_design_20260104*
