# /diamond-synthesize

**Purpose:** Lock decisions - crystallize extracted entities into structured artifacts.
Present grouped summary, get final confirmation, trigger artifact creation.

## Trigger

HD loads this skill when:
- Converge phase complete (groups confirmed, priorities established)
- Session has `current_phase: converge` and user approved groupings
- User signals readiness: "let's finalize", "lock it in", "ready to proceed"

## State Protocol

### On Entry

```yaml
# 1. Load session state
READ: $TEMP/interview-session.yaml

# 2. Verify preconditions
REQUIRE:
  - current_phase: converge (or synthesize if resuming)
  - groups: at least 1 confirmed group
  - entities: at least 1 entity with status: grouped

# 3. If preconditions fail
IF missing groups:
  1. Save state: attempted_synthesize = true
  2. Output: "We haven't grouped entities yet. Let's do that first."
  3. HD must read_file('.claude/skills/diamond-converge.md')
  → EXIT
```

### On Exit

```yaml
# 1. Update session state
UPDATE interview-session.yaml:
  current_phase: complete
  last_updated: <timestamp>

# 2. Write session file BEFORE asking user for confirmation

# 3. Output artifact links (mandatory)
FORMAT: "Draft: `<path>`"
```

## Synthesize Flow

### Step 1: Present Grouped Summary

**Pattern (from ADR-002):**
```
Core entities: [list from groups].
Main flows: [flow from actions/verbs].
Key constraints: [constraints captured].

Does this capture what we discussed?
```

**Example:**
```
Core entities: User, Order, Product, Payment.
Main flows: User creates Order, adds Products, submits Payment.
Key constraints: Must support offline mode, max 10s response time.

Does this capture what we discussed?
```

**Rules:**
- Present as grouped summary, NOT entity-by-entity dump
- Keep it scannable (one line per category)
- Don't ask about each entity individually

### Step 2: Handle Response

```yaml
IF user approves ("yes", "looks good", "correct"):
  → Proceed to Step 3 (ADR identification)

IF user hesitates ("mostly", "I think so", "sort of", "yeah", "kinda", "more or less"):
  → "I want to be sure I captured this correctly. Is anything missing or wrong?"
  → Wait for explicit yes/no or specific concern
  → Address ONLY that concern
  → Re-confirm just the changed part
  → **Hesitation limit:** Track hesitation_count per confirmation item
  → IF hesitation_count >= 3 for same item:
    → "It sounds like there might be something unclear. Let me note this as needing clarification."
    → Mark item with flag: needs_clarification = true
    → Move to next item (do not block on this item)
  → At end of confirmation pass: IF any items flagged needs_clarification:
    → "Some items need more discussion. Should we explore these further now, or proceed with what we have?"
    → IF explore: Return to diverge for targeted clarification
    → IF proceed: Continue with flagged items marked as "tentative"

IF user rejects ("no", "that's wrong"):
  → "What needs to change?"
  → Capture correction
  → Update session state
  → Re-present corrected summary
```

### Step 3: ADR Identification

Scan confirmed entities for architectural decision signals:

**ADR Signals:**
- "must", "always", "never", "the only way"
- Technical stack choices (database, framework, language)
- Security/compliance requirements
- Cross-cutting constraints

**Pattern:**
```
IF signal detected:
  → "You mentioned [constraint]. Should I lock that as an architectural decision?"
  → IF yes: Track in session state
  → IF no: Continue without ADR

LIMIT: Max 3 ADR prompts per synthesis session

# Track ADR candidates in session state:
adr_candidates:
  - signal: '[the constraint mentioned]'
    user_confirmed: true|false
    drafted: false  # Cleared when /draft-adr runs
```

### Step 4: Final Confirmation

```yaml
# Present final STATE-0
Core: [entities]
Flows: [actions]
Constraints: [limits]
Decisions to lock: [ADR candidates, if any]

Ready to create artifacts?
```

### Step 5: Handoff to Drafting

```yaml
ON user approval:
  # 1. Update session
  current_phase: complete

  # 2. Determine artifact types needed
  artifacts_to_create:
    - UserStories: For each confirmed group with user-facing behavior
    - ADRs: For each confirmed architectural decision
    - Specs: For technical requirements without user stories

  # 3. Handoff Order (ADRs first - constraints inform stories)
  order:
    1. ADRs first (architectural constraints inform stories)
    2. User Stories by group.priority (must → should → could)

  # 4. Handoff message
  "I'll draft [count] artifacts:
   - [N] ADRs for [decisions]
   - [N] User Stories for [groups]

   Starting with [first artifact by order]..."

  # 5. Invoke drafting skills (see Skill Transition below)
  → /draft-adr (for each decision, first)
  → /draft-userstory (for each user story, by priority)
```

## Exit Conditions

Skill completes when ALL are true:
- User explicitly approves final summary
- Session `current_phase` set to `complete`
- Handoff initiated to drafting skills

**Early Exit Triggers:**
- User requests pause: Save state, mark `current_phase: synthesize`
- User introduces new scope: GLOBAL OVERRIDE (see below)
- User rejects fundamental grouping: Back to converge

**Global Override - State Preservation:**
```yaml
ON global_override (user introduces new scope):
  1. Write checkpoint: synthesize.interrupted_by_scope_change = true
  2. Preserve existing groups in session (do NOT clear)
  3. Return to diverge for NEW entities only
  4. On re-converge: merge new entities with existing groups
  5. HD must read_file('.claude/skills/diamond-diverge.md')
```

## Anti-Patterns

| Wrong | Right |
|-------|-------|
| Dump entire session as bulleted list | Grouped one-liner summary |
| "Is everything correct?" (vague) | "Does this capture what we discussed?" |
| Ask about each entity separately | Drill only on explicit concern |
| Force ADR for every constraint | Max 3 ADR prompts, only on signals |
| Announce "Now synthesizing..." | Just present the summary |
| Hide draft locations | Always output clickable paths |

## Common Anti-Patterns (per ADR-002)

- Never announce methods or phases
- Never announce skills
- Never use generic probes
- Always output artifact links (never hidden artifacts)

## Conversation Examples

### Happy Path

```
HD: Core entities: User, Order, Product.
    Main flows: User browses Products, creates Order, pays.
    Key constraints: Must work on mobile, sub-3s load times.

    Does this capture what we discussed?

User: Yes, that's it.

HD: You mentioned "must work on mobile" - should I lock that as
    an architectural decision?

User: Yes, that's a hard requirement.

HD: Got it. I'll draft:
    - 1 User Story for the Order flow
    - 1 ADR for mobile-first constraint

    Starting with the Order user story...

    Draft: `.claude/PM/TEMP/drafts/US-001-order-flow.md`
```

### Hesitation Path

```
HD: Core entities: User, Order, Product.
    Main flows: User browses Products, creates Order, pays.
    Key constraints: Must work on mobile.

    Does this capture what we discussed?

User: Mostly, but...

HD: What's missing or wrong?

User: We also talked about inventory tracking.

HD: Right - adding Inventory to core entities.

    Updated: Core entities include Inventory.
    The flow now includes: check Inventory before Order confirmation.

    Correct?

User: Yes.
```

### Scope Change (Global Override)

```
HD: Core entities: User, Order, Product.
    Main flows: User browses Products, creates Order, pays.

    Does this capture what we discussed?

User: Wait, I forgot - we also need a wishlist feature.

HD: Good catch. That changes our scope.
    Let me save where we are and capture the wishlist properly.

    [State saved]

    Tell me about the wishlist - what should users be able to do with it?

    [Returns to diverge phase for wishlist exploration]
```

## State Schema Reference

```yaml
# Expected session state on entry
current_phase: converge
groups:
  - id: order_management
    entities: [order_create, order_view, order_cancel]
    priority: must
extracted_entities:
  - id: order_create
    status: grouped
    group: order_management

# Session state on exit
current_phase: complete
artifacts_created:
  - path: $TEMP/drafts/US-001-order-flow.md
    type: userstory
    status: draft
```

## Minimum Viable STATE-0

Before handoff, verify:
- [ ] At least 1 entity confirmed
- [ ] At least 1 group with priority
- [ ] User explicitly approved summary
- [ ] `current_phase: complete` written to session

## Skill Transition

To draft artifacts, HD must explicitly load the drafting skill:
- `read_file('.claude/skills/draft-userstory.md')` for user stories
- `read_file('.claude/skills/draft-adr.md')` for architectural decisions

---
*Skill Version: 1.0.0*
*Architecture: ADR-002 HD Composition*
