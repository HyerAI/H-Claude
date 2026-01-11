# /draft-adr

**Purpose:** Create Architecture Decision Records from confirmed decisions.
ADRs lock architectural choices and go directly to SSoT (not drafts).

## Trigger Conditions

Load this skill when:
- User confirms a technical decision during /diamond-synthesize
- Language signals: "must", "always", "never", "the only way", "we decided"
- Technical choice made: framework selection, auth method, database choice
- Pattern established: "we should always X because Y"
- User explicitly requests: "let's make this an ADR"

**Max 3 ADR prompts per interview segment.** Not every decision needs an ADR.

### ADR Prompt Counter

Session tracking in `interview-session.yaml`:
```yaml
adr_prompts_this_segment: N
```

ON adr_prompt:
- IF `session.adr_prompts_this_segment >= 3`:
  → Skip ADR creation, note in session for later
- ELSE:
  → Increment counter, proceed

## State Protocol

### On Entry

1. Read `$TEMP/interview-session.yaml` if exists
2. Load ADR template: `read_file(".claude/templates/ADR.md.template")`
3. Check existing ADRs in `$SSOT/ADRs/` for conflicts or duplicates
4. Identify next ADR number (ADR-XXX format)

**CRITICAL:** Must load template to ensure DoR-compliant format.

**Template Error Handling:**
```
IF template is NULL or file_not_found:
  ERROR: "ADR template not found at .claude/templates/ADR.md.template"
  ABORT: "Cannot proceed without template."
  → Do NOT attempt to generate without template
```

### Conflict Detection

```yaml
FOR each existing_adr in $SSOT/ADRs/:
  1. Extract keywords from new ADR title (nouns, technical terms)
  2. Search existing ADR titles and Decision sections for matching keywords
  3. IF 2+ keywords match in same ADR:
     - Read matched ADR's Decision section
     - Compare: Does new decision contradict old?
     - Contradict signals:
       - Opposite choices for same domain ("use JWT" vs "use sessions")
       - Conflicting verbs ("always X" vs "never X")
       - Different values for same config ("timeout=30s" vs "timeout=5m")
  4. IF potential conflict found:
     - Show both decisions to user
     - Prompt: "This may conflict with ADR-XXX: '[old decision]'. Should we supersede it?"
     - IF supersede: Mark old ADR as Superseded, link to new
     - IF no conflict: Proceed normally
```

### On Exit

1. Update `interview-session.yaml` with artifact link
2. Write session file at checkpoint
3. Output clickable artifact link (mandatory)

## ADR Interview Process

### Step 1: Identify the Decision

Extract from conversation context OR prompt user:

```
I'm hearing a decision being made about [TOPIC].

Let me capture this as an ADR to lock it down.
```

**Gather:**
- What is the decision about? (Subject)
- What did we decide? (Choice)
- What triggered this decision? (Motivation)

### Step 2: Capture Context

**Questions to ask (pick 1-2 relevant ones):**
- "What problem does this solve?"
- "What constraints led to this choice?"
- "What would happen if we didn't decide this now?"

**Map to ADR Context section:**
- The issue motivating the decision
- Forces at play (technical, business, organizational)

### Step 3: Document the Decision

**Must be:**
- Specific and actionable
- Written as "We will..." or "The system must..."
- Not vague ("consider", "might", "perhaps")

```yaml
# Decision capture template
decision: "We will use [X] for [Y]"
rationale: "Because [Z]"
scope: "This applies to [BOUNDARY]"
```

### Step 4: Identify Consequences

**Prompt for each category:**

| Category | Question |
|----------|----------|
| Positive | "What does this enable us to do?" |
| Negative | "What are we giving up or risking?" |
| Neutral | "What changes without being good or bad?" |

At minimum: 1 positive, 1 negative consequence.

### Step 5: Record Alternatives

**Ask:**
- "What other options did we consider?"
- "Why didn't we choose [alternative]?"

If user says "we didn't consider others":
- Note as "No alternatives explicitly evaluated"
- Consider if this is a red flag (might need more diverge)

**No Alternatives Action:**
IF no_alternatives:
  Prompt: "You haven't considered alternatives. Should we briefly explore other options before locking this?"
  IF yes: Return to diverge mode for alternatives
  IF no: Proceed with warning in ADR: "Note: No alternatives formally evaluated"

### Step 6: Generate ADR

Use template structure from `.claude/templates/ADR.md.template`:

```markdown
# ADR-XXX: [Decision Title]

**Status:** Accepted
**Date:** [YYYY-MM-DD]
**Decision Makers:** HeyDude, Claude (HC)

## Context

[Captured context - the problem and forces]

## Decision

[The specific decision statement]

## Consequences

### Positive
- [Benefit captured]

### Negative
- [Cost/risk captured]

### Neutral
- [Trade-off if any]

## Alternatives Considered

### Option A: [Alternative name]
- **Pros:** [if captured]
- **Cons:** [if captured]
- **Why Rejected:** [reason]

## References

- [Related ADRs, source documents]

---

*Created: [DATE]*
*Last Updated: [DATE]*
```

## Output Requirements

### Artifact Link (MANDATORY)

After creating ADR, ALWAYS output:

```
ADR: `.claude/PM/SSoT/ADRs/ADR-XXX-[slug].md`
```

### File Naming

```
ADR-XXX-[kebab-case-title].md

Examples:
  ADR-003-auth-provider-selection.md
  ADR-004-database-choice.md
  ADR-005-api-versioning-strategy.md
```

### Number Assignment

1. Check `$SSOT/ADRs/` for existing ADRs
2. Find highest number
3. Increment by 1
4. If first ADR in project: start at ADR-001

## ADR Status Transitions

VALID_TRANSITIONS:
- Proposed → Accepted | Rejected
- Accepted → Deprecated | Superseded
- Deprecated → (terminal)
- Superseded → (terminal, must link to successor)

**On Supersede:** New ADR must reference the superseded ADR in References section.

## Definition of Ready Validation

ADR MUST have before saving:

| Section | Requirement |
|---------|-------------|
| Context | Non-empty, explains the problem |
| Decision | Specific, actionable statement |
| Consequences | At least 1 positive AND 1 negative |

**If missing any:** Prompt user before saving.

## Exit Conditions

Return control to HD Core when:
- ADR successfully written to `$SSOT/ADRs/`
- User explicitly cancels ("let's not ADR this")
- User needs more exploration ("I'm not sure yet")

**On uncertainty:** Suggest returning to diverge/converge before locking.

### Skill Transition

ON return to interview:
- For uncertainty: HD must `read_file('.claude/skills/diamond-diverge.md')`
- After completion: Return control to HD Core

## Anti-Patterns

| Wrong | Right |
|-------|-------|
| ADR for every small choice | ADR for architectural decisions only |
| Vague context | Specific problem statement |
| "We might..." decision | "We will..." decision |
| No consequences listed | At least positive + negative |
| Creating in `$TEMP` | ADRs go to `$SSOT/ADRs/` |
| No artifact link output | Always show clickable path |
| Over-ADRing (5+ per session) | Max 3 ADR prompts per segment |

## Common Anti-Patterns (per ADR-002)

- Never announce methods ("I'm capturing an ADR...")
- Never announce skills ("Loading draft-adr...")
- ADR for architectural decisions only (not every choice)
- Always output artifact links (never hidden artifacts)
- Never skip template load

## Example Flow

```
User: "We should always use JWT for authentication in this project,
       not session cookies."

HD: I'm capturing this as an architectural decision.

    Decision: Use JWT for authentication

    Quick questions to lock this down:

    1. What drove this choice? (stateless APIs? mobile clients?)
    2. What are we trading off by not using sessions?

User: Stateless APIs and we have mobile clients. Trade-off is
      we can't revoke tokens easily.

HD: Got it. I've created the ADR.

    ADR: `.claude/PM/SSoT/ADRs/ADR-003-jwt-authentication.md`

    - Context: Stateless API design with mobile clients
    - Decision: Use JWT over session cookies
    - Positive: Stateless, mobile-friendly
    - Negative: Token revocation complexity

    Want me to read it back in full?
```

---

## References

- ADR-002: HD Composition Architecture
- Template: `.claude/templates/ADR.md.template`
- DoR: ADR requires Context, Decision, Consequences

---

*Skill Version: 1.0.0*
*Architecture: ADR-002 HD Composition*
