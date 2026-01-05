# Decision Map: HC System Prompt Design

**Session:** hc_system_prompt_design_20260104
**Date:** 2026-01-04
**Status:** AWAITING USER DECISION

---

## Core Tension

| Expert | Position |
|--------|----------|
| **Domain Expert** | Build monitoring infrastructure (HC-LOG, enhanced triage, logging protocols) |
| **Pragmatist** | Simplify decision rules, cut overhead, accept small work is small |

The Pragmatist raises valid concerns about maintenance burden, but user explicitly requested HC-LOG and triage enhancements.

---

## Agreements (No Contest)

Both experts agree on:

1. **Pre-flight validation** - Check NORTHSTAR.md, ROADMAP.yaml, context.yaml exist at session start
2. **File-count routing threshold** - 3+ files = MUST route to /hc-execute
3. **Phase work routing** - Active ROADMAP phase work MUST route
4. **Rename HD → HC** - Straightforward find/replace
5. **git-engineer for commits** - HC should not run raw `git commit`

---

## Contested Areas

### 1. HC-LOG Folder

| Option | Description | Trade-off |
|--------|-------------|-----------|
| **A. Full HC-LOG** | USER-PREFERENCES.md + HC-FAILURES.md + ROUTING-STATS.md | More tracking, maintenance burden |
| **B. Minimal HC-LOG** | USER-PREFERENCES.md + HC-FAILURES.md only | User request honored, reduced scope |
| **C. No HC-LOG** | Preferences in CLAUDE.md, failures in BACKLOG.yaml | Simpler, but loses dedicated tracking |

**User expressed intent:** Create HC-LOG folder with these files.

**Recommendation:** **Option B** - Minimal HC-LOG. Skip ROUTING-STATS.md (metrics overhead not worth it).

---

### 2. Dual Mode (Architect vs Product Owner)

| Option | Description | Trade-off |
|--------|-------------|-----------|
| **A. Dual mode** | HC switches between Architect (inline OK) and PO (route) based on task type | Conceptually clean, but cognitive overhead |
| **B. Single rule** | Route if 3+ files OR phase work OR new file. Everything else inline. | Simple, but no conceptual framework |

**Recommendation:** **Option B** - Single rule. The mode abstraction adds overhead without clear benefit.

---

### 3. Triage Enhancement

| Option | Description | Trade-off |
|--------|-------------|-----------|
| **A. Full enhancement** | Triage reads HC-LOG, outputs failures + preferences in SESSION BRIEF | More context, slower triage (~8s vs ~5s) |
| **B. Light enhancement** | Triage only reads HC-FAILURES.md (last 3), adds one line to brief | Minimal overhead, surfaces critical info |
| **C. No enhancement** | Triage stays as-is | Simplest, but HC-LOG goes unread |

**User expressed intent:** Triage should review HC-LOG and provide recommendations.

**Recommendation:** **Option B** - Light enhancement. Only failures matter for preventing repeats.

---

### 4. Line Count vs File Count Thresholds

| Option | Description | Trade-off |
|--------|-------------|-----------|
| **A. Both** | < 5 lines = trivial, 5-20 = small, 20+ = medium, file count on top | Detailed but complex |
| **B. File count only** | 3+ files = route. Period. | Simple, knowable upfront |

**Recommendation:** **Option B** - File count only. Line counts are unknowable until after the change.

---

### 5. Inline Execution Logging

| Option | Description | Trade-off |
|--------|-------------|-----------|
| **A. Log all inline** | Every inline execution logged to HC-LOG | Completeness, but maintenance burden |
| **B. Log only "should have routed"** | Log when inline was done but 3+ files touched (mistake) | Catches errors only |
| **C. No logging** | Don't track inline executions | Simplest, no overhead |

**Recommendation:** **Option B** - Only log mistakes. If HC goes inline on 3+ files, that's an incident for HC-FAILURES.md.

---

## Proposed Path Forward

Based on analysis and user intent:

### What We'll Implement

1. **HC Discipline section** in CLAUDE.md with:
   - Unified role: HC is Product Owner/Orchestrator (not dual-mode)
   - Single routing rule: 3+ files OR phase work OR new feature → route
   - Escape hatch: User says "quickly" → inline regardless

2. **Pre-flight validation** at session start:
   - Check NORTHSTAR.md, ROADMAP.yaml, context.yaml exist
   - Prompt if missing

3. **HC-LOG folder** (minimal):
   ```
   .claude/PM/HC-LOG/
   ├── USER-PREFERENCES.md   # Learned preferences
   └── HC-FAILURES.md        # Incidents + lessons
   ```

4. **Triage enhancement** (light):
   - Read HC-FAILURES.md (last 3 incidents)
   - Add "Recent Failures" line to SESSION BRIEF

5. **Git discipline**:
   - HC never runs raw `git commit`
   - git-engineer checkpoint before /hc-execute

6. **Rename HD → HC** throughout

### What We'll Skip

- ROUTING-STATS.md (unnecessary metrics)
- Line-count thresholds (unpredictable)
- Dual-mode abstraction (cognitive overhead)
- Full triage enhancement (overkill)

---

## User Decision Needed

**Approve the proposed path above?** Or adjust any contested area?

Specific questions:
1. HC-LOG: Full (A), Minimal (B), or None (C)?
2. Triage: Full enhancement (A), Light (B), or None (C)?
3. Any other adjustments?

---

*Decision Map generated by Council*
*Session: hc_system_prompt_design_20260104*
