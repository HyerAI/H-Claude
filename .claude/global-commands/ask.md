# /ask - Get Pro Agent Feedback

Get critical feedback from Pro Agent on a document. **Feedback only - no file edits.**

---

## Usage

```
/ask <file>              # Single review cycle
/ask <N> <file>          # N review cycles (max 5)
```

**Examples:**
```
/ask .claude/PM/SSoT/NORTHSTAR.md
/ask 3 ./docs/architecture.md
```

---

## Execution Protocol

### Step 1: Gather Context

1. Read the target file
2. Read `$SSOT/NORTHSTAR.md` - extract Goals and Constraints sections only
3. Check `$SSOT/ROADMAP.yaml` - get current phase name

### Step 2: Send to Pro Agent

Use the proxy command with the prompt below. Inject file content and context.

```bash
ANTHROPIC_API_BASE_URL=http://localhost:2406 claude --dangerously-skip-permissions -p "<prompt>"
```

---

## Pro Agent Prompt

```
# SYSTEM INSTRUCTION

**Role:** Critical reviewer. Feedback only - do NOT edit or create files.
**Tone:** Direct, technical, no fluff.
**Output:** Structured list format only. No essays.

# PROJECT CONTEXT

**Goals:** [Insert NORTHSTAR goals - 2-3 lines max]
**Constraints:** [Insert NORTHSTAR constraints - 2-3 lines max]
**Current Phase:** [Insert from ROADMAP]

# REVIEW INSTRUCTIONS

Analyze the content below. For each dimension, list max 3 issues.

**Output Format (strict):**
```
## [Dimension Name]
1. **[Issue Title]** - [One sentence description] | Severity: HIGH/MED/LOW
2. ...
```

If a dimension has no issues, write: "No issues found."

## Dimensions

### 1. Pre-Mortem
If this failed in 6 months, what caused it? Identify fragile assumptions.

### 2. Logic Gaps
Missing premises, contradictions, undefined terms, impossible constraints.

### 3. Edge Cases
Happy-path bias, unhandled failures, adversarial scenarios.

### 4. Ambiguity
Vague verbs (ensure, manage, oversee), unclear ownership, undefined processes.

### 5. Counter-Argument
Strongest objection to this approach. What would a critic attack first?

---

# CONTENT TO REVIEW

[FILE CONTENT HERE]
```

---

## Step 3: Evaluate Feedback

Review Pro's response:
- **HIGH severity:** Must address before proceeding
- **MED severity:** Should address, use judgment
- **LOW severity:** Nice-to-have, defer if needed

Update the file based on valid HIGH/MED feedback only.

---

## Loop Behavior (Multi-Cycle)

When running N cycles:

1. After each update, send the revised file with the same prompt
2. **Stop early if:** Pro returns no HIGH or MED issues
3. **Stop early if:** Pro repeats previous feedback (no new insights)
4. Report to user: "Completed N cycles. Final state: X HIGH, Y MED remaining."

---

## Anti-Patterns

- Do NOT let Pro edit files directly
- Do NOT paste entire NORTHSTAR (extract relevant sections)
- Do NOT continue loops when only LOW issues remain
- Do NOT accept feedback without validating against project goals
