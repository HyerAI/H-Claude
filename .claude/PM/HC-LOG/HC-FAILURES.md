# HC Failures Log

Incidents and lessons learned. Triage reads last 5 at session start.
Add entry when: command fails, workflow breaks, audit finds gaps.

---

## Incident Log

### [2026-01-04] INIT-001: Log initialized

- **What happened:** HC-FAILURES.md created as part of HC System Prompt Design
- **Evidence:** Think-tank session hc_system_prompt_design_20260104
- **Lesson:** Real systems have failures - logging them enables learning
- **Prevention:** This log exists; incidents will be captured going forward

### [2026-01-04] HIST-001: 100% success paradox identified

- **What happened:** ADR-004 found 36 tasks, 0 failures across 3 sessions
- **Evidence:** .claude/PM/SSoT/ADRs/ADR-004-hc-execute-improvements.md
- **Root cause:** Either QA not running, or failures not logged
- **Lesson:** Perfect scores indicate broken logging, not perfect execution
- **Prevention:** SWEEP must create SWEEP_REPORT.md even when CLEAN

### [2026-01-04] HIST-002: Artifact trail broken

- **What happened:** No PHASE_X folders, WORKER_OUTPUTS in hc-execute sessions
- **Evidence:** ADR-004 findings
- **Root cause:** Orchestrator not creating folder structure before execution
- **Lesson:** Design vs reality gaps accumulate silently
- **Prevention:** Phase 1 of orchestrator now creates full folder structure

---

Keep last 20 incidents. Archive older to HC-FAILURES-ARCHIVE.md
