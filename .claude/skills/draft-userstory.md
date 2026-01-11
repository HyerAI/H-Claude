# /draft-userstory

**Purpose:** Create UserStory documents from extracted entities and confirmed groups.
Produces DoR-compliant drafts ready for user review.

## Trigger

Load this skill when:
- Entity/group has been confirmed during interview
- User says "let's document this" or "create a user story"
- Converge/synthesize phase completes with confirmed requirements
- Recognition pattern: "The user should be able to..."

## State Protocol

### On Entry

```
1. read_file("$TEMP/interview-session.yaml")
   → Load current phase, entities, groups, pending decisions
   → IF file_not_found: Initialize empty session state

2. read_file(".claude/templates/documents/UserStory.md.template")
   → CRITICAL: Load template to ensure DoR-compliant format
   → Without template, agent will hallucinate structure

   ERROR HANDLING:
   IF template is NULL or file_not_found:
     ERROR: "UserStory template not found at .claude/templates/documents/UserStory.md.template"
     ABORT: "Cannot proceed without template. Create it first or use /genesis."
     → Do NOT attempt to generate without template

3. Identify target entity/group for documentation:
   → Filter entities where status = "confirmed"
   → Filter groups where priority is set (must/should/could)
```

### On Exit

```
1. Update interview-session.yaml:
   → Add to artifacts_created[]
   → Update entity status to "documented"

2. Track incomplete drafts (if [TODO] placeholders exist):
   → Add to session.drafts_with_todos:
     - path: $TEMP/drafts/US-XXX.md
       missing_sections: ["so that", "Assumptions", ...]
       created: <timestamp>

3. Output artifact link (MANDATORY):
   → "📄 Draft: `.claude/PM/TEMP/drafts/US-XXX.md`"

4. Write session file BEFORE asking user for review
```

## Drafting Process

### Step 1: Select Target

```yaml
# From session state, identify what to document

IF user specified target:
  → Use named entity/group

ELSE IF single confirmed group exists:
  → Use that group

ELSE IF multiple confirmed groups:
  → Present numbered list with priorities:
    'Which group should I document first?'
    '1. [group_name_a] (must-have) - N entities'
    '2. [group_name_b] (should-have) - N entities'
    '3. [group_name_c] (could-have) - N entities'
  → Parse response:
    - IF user says number (1, 2, 3...): Select that group
    - IF user says 'all' or 'both' or 'everything': Process in priority order (must → should → could)
    - IF user names a group by name: Match to group list (case-insensitive)
    - IF user names non-existent group: 'I don't see that group. Here are the available options:' + re-list
    - IF response unclear after 2 attempts: Default to highest priority group with notice

ELSE:
  → No confirmed content to document
  → Return to converge/synthesize phase
```

### Step 2: Generate Story ID

```
# Pattern: US-XXX-slug
# XXX = sequential number (check existing US-* files)
# slug = 2-4 word kebab-case from primary entity

ID Assignment (collision-safe):
1. proposed_id = next_available_id() based on existing US-* files
2. IF file_exists(proposed_id): increment and retry (max 10 attempts)
3. IF attempts >= 10:
   ERROR: "Unable to assign unique ID after 10 attempts."
   Prompt: "Please provide a custom ID suffix (e.g., 'special-login'):"
   → Use user-provided suffix: US-XXX-{user_suffix}.md
4. Write file immediately after ID assignment to claim it

EXAMPLE:
  Entity: "user_login"
  → US-001-user-login.md

EXAMPLE:
  Group: "order_management" (order_create, order_cancel, order_view)
  → US-002-order-management.md
```

### Step 3: Map to Template

```yaml
# Template sections and their sources

Description:
  "As a":
    - FIRST STORY in session: Always ask user for user type
    - SUBSEQUENT: Use cached user type from session.default_user_type
    - ON AMBIGUITY (multiple user types): Ask "Who is the primary user for this feature?"
  "I want": Primary entity description
  "so that": Derive benefit from source quotes or ask
  Context: Combine source quotes and session notes

Acceptance Criteria:
  - Derive from entity descriptions in group
  - One criterion per testable behavior
  - Must be specific and verifiable
  - Format: "[ ] When X, then Y"

Boundaries:
  In Scope:
    - Entities explicitly in the group
    - Behaviors confirmed during interview
  Out of Scope:
    - Related entities in other groups
    - Features explicitly deferred
  Dependencies:
    - Cross-references to other groups
    - Technical prerequisites mentioned
  Assumptions:
    - Inferred from "user said" context
    - Technical assumptions made
```

### Step 4: Write Draft

```
1. Generate content following template structure
2. Fill all DoR-required sections (Description, Acceptance Criteria, Boundaries)
3. Set Status: Draft
4. Set Priority: From group.priority (must/should/could/won't)
5. Set Source: Link to session or origin
6. Add timestamps
```

### Step 5: Output and Link

```
# Write file
write_file("$TEMP/drafts/US-XXX-slug.md")

# Update session state
artifacts_created:
  - path: "$TEMP/drafts/US-XXX-slug.md"
    type: userstory
    status: draft
    entity_ids: [list of documented entities]

# MANDATORY output format
"📄 Draft: `.claude/PM/TEMP/drafts/US-XXX-slug.md`"
```

## Output Format

### Successful Draft

```
I've drafted the user story based on our confirmed requirements.

📄 Draft: `.claude/PM/TEMP/drafts/US-001-user-login.md`

The draft covers:
- [Brief summary of what's included]
- [Key acceptance criteria count]

Would you like to review it, or shall I continue with [next group]?
```

### Missing Information

```
I need a bit more context to complete the user story:

- [Specific question about missing "As a" or "so that"]
- [Question about unclear acceptance criteria]

Once clarified, I'll generate the draft.
```

### No Confirmed Content

```
I don't see any confirmed entities ready for documentation.

Current session has [N] raw entities and [M] groups.
Would you like to:
- Review and confirm a group first?
- Document a specific entity anyway?
```

## Definition of Ready Validation

Before finalizing draft, verify:

```yaml
DoR Checklist:
  Description:
    - [ ] Has "As a [user type]"
    - [ ] Has "I want [goal]"
    - [ ] Has "so that [benefit]"
    - [ ] Has expanded context

  Acceptance Criteria:
    - [ ] At least 2 criteria present
    - [ ] Each criterion is testable
    - [ ] Criteria are specific (no vague terms)

  Boundaries:
    - [ ] In Scope section populated
    - [ ] Out of Scope section populated
    - [ ] Dependencies listed (or "None")
    - [ ] Assumptions listed (or "None")

IF any check fails:
  → Mark section with [TODO] placeholder
  → Note in output what needs completion
```

## Exit Conditions

Return control to HD Core when:
- Draft successfully written and linked
- User confirms review complete
- User requests different action (back to interview, different story)
- Global Override triggered (user introduces new scope)

## Common Anti-Patterns (per ADR-002)

- Never announce methods ("I'm creating a user story...")
- Never announce skills ("Loading draft-userstory...")
- Never dump entire content in chat - summarize and link
- Always output artifact links (never hidden artifacts)
- Never skip template load

| Don't | Do Instead |
|-------|------------|
| "I'm creating a user story..." | Just write it, output the link |
| Dump entire content in chat | Summarize, provide clickable link |
| Skip template load | Always read template first |
| Overwrite existing US with same ID | Check for existing files, increment |
| Leave sections empty | Use [TODO] placeholders, note in output |
| Forget session state update | Update artifacts_created before output |

## Skill Transition

```yaml
ON return_to_interview:
  - For new scope: HD must read_file(".claude/skills/diamond-diverge.md")
  - For more grouping: HD must read_file(".claude/skills/diamond-converge.md")

ON completion:
  - Return control to HD Core
  - User directs next action
```

---

*Skill Version: 1.0.0*
*Architecture: ADR-002 HD Composition*
*Specification: `$SSOT/HD_INTERFACE.md`*
*Requires: interview-session.yaml, UserStory.md.template*
