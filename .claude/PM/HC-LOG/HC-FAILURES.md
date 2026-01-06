# HC Failures Log

Incidents and lessons learned. $SCOUT updates after commands (triage).

## When to Add Entry

| Trigger | Example |
|---------|---------|
| **Command failed** | /hc-execute crashed, worker timeout |
| **Workflow broke** | Missing files, wrong state, broken handoff |
| **Audit found gaps** | /hc-glass or /red-team discovered issues |
| **Pattern of errors** | Same mistake repeated across sessions |

**NOT trivial:** Skip typos, one-off glitches. Capture systemic failures with lessons.

**Entry format:**
```
### [DATE] ID: Short title
- **What happened:** Facts only
- **Evidence:** Links to files/sessions
- **Root cause:** Why it failed
- **Lesson:** What to do differently
- **Prevention:** Concrete fix applied
```

---

## Incident Log

### [YYYY-MM-DD] INIT-001: Log initialized

- **What happened:** HC-FAILURES.md created as part of project setup
- **Evidence:** Initial project configuration
- **Lesson:** Real systems have failures - logging them enables learning
- **Prevention:** This log exists; incidents will be captured going forward

---

Keep last 20 incidents. Archive older to HC-FAILURES-ARCHIVE.md
