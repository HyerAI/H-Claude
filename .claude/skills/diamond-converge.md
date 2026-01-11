# /diamond-converge

**Purpose:** Focus and prioritize extracted entities from diverge phase.
Clusters related entities, establishes MoSCoW priorities, surfaces constraints.

## Trigger

Load this skill when:
- User signals readiness to prioritize: "let's prioritize", "what's most important", "let's focus"
- Natural transition from diverge: user said "that's everything" or equivalent
- HD detects conversation shifting from exploration to evaluation

## State Protocol

### On Entry

```yaml
# MANDATORY: Read session state before ANY action
1. read_file("$TEMP/interview-session.yaml")
2. Validate current_phase == "diverge" or "converge"
3. Load extracted_entities list
4. If no entities exist → ABORT:
      a. Output: "No confirmed entities found. Let's explore first."
      b. Set: current_phase = "diverge"
      c. HD must read_file(".claude/skills/diamond-diverge.md")
```

**Present diverge summary to user:**

```
"From our discussion I captured:

Entities: [list entity.description for type=entity]
Actions: [list entity.description for type=action]
Constraints: [list entity.description for type=constraint]

Let's organize these. What's absolutely critical for success?"
```

### On Exit

```yaml
# CHECKPOINT: Write before user confirmation prompt
1. Read existing interview-session.yaml
2. MERGE (don't overwrite):
   - Update entity status: raw → grouped
   - Add group assignments to entities
   - Add new groups with priority levels
   - Update current_phase: "converge"
   - Update last_updated timestamp
3. Write session file
```

## Activities

### 1. Grouping (Affinity Clusters)

**Technique:** Cluster related entities by natural relationships.

```
INTERNAL: Identify patterns across extracted entities
OUTPUT: "These three seem related to [theme]..."

Propose groupings:
- "I see [entity_a], [entity_b], [entity_c] all relate to [theme].
   Should I group them?"
```

**User confirms → update entity.group field**

**IF user rejects all groupings:**
```
Prompt: "Should each item be handled separately?"
IF yes: Create individual groups for each entity
IF no: Return to diverge for more context
```

### 2. Priority Ranking (MoSCoW)

**Technique:** Force-rank groups by business criticality.

```
After grouping, ask:
- "If you could only launch with THREE of these groups, which three?"
- "What's non-negotiable for the first version?"
- "What could wait for version 2?"
```

**Priority Levels:**

| Level | Meaning | Question |
|-------|---------|----------|
| must | Non-negotiable for launch | "System fails without this?" |
| should | Important, strong case | "Significant pain if missing?" |
| could | Desirable if time permits | "Nice-to-have?" |
| wont | Explicitly out of scope now | "Deferred to later?" |

**User ranks → update group.priority field**

### Dependency-Aware Priority

```
IF group_a.depends_on includes group_b AND group_a.priority == group_b.priority:
  Prompt: "Both [A] and [B] are same priority, but [A] depends on [B].
           Should [B] be executed first?"
```

### 3. Constraint Surfacing

**Technique:** Uncover technical and business limitations before finalizing.

```
Probe for constraints:
- "Are there technical limitations we should capture?"
- "Any budget, timeline, or compliance realities?"
- "What's fixed that we can't change?"
```

**New constraints → add to extracted_entities with type=constraint**

### 4. Dependency Flagging

**Technique:** Identify which groups depend on others.

```
Review groups and ask:
- "Does [group_b] require [group_a] to work first?"
- "Are any of these independent, can be built in parallel?"
```

**Dependencies → add depends_on field to groups**

## Validation Check

Before transitioning to synthesize, verify:

```yaml
converge_complete:
  - [ ] All entities assigned to groups OR explicitly rejected (entity.status = "rejected", entity.rejection_note = "user reason")
  - [ ] Each group has a priority (must/should/could/wont)
  - [ ] User has confirmed groupings: "Does this grouping make sense?"
  - [ ] No orphan entities with status=raw remaining (user may refuse to group some - mark as rejected)
  - [ ] Constraints surfaced and captured
```

**If validation fails:** "Before we lock this down, [missing item]. Can you help clarify?"

## Exit Conditions

Return control to HD Core when:

1. User explicitly approves groupings: "yes, that's right", "looks good"
2. All validation checks pass
3. User signals readiness for next phase: "let's finalize", "ready to lock it in"

**On exit, probe once:**
```
"Anything we grouped wrong or missed?"
```

If user adds new items → capture them, re-validate (may need brief diverge)

**Transition phrase:**
```
"Groups confirmed. Ready to synthesize these into structured artifacts."
```

**Transition:** HD must read_file(".claude/skills/diamond-synthesize.md")

## Session State Updates

### Entity Status Flow

```
raw → grouped → confirmed | rejected
```

### Group Schema

```yaml
groups:
  - id: "user_auth"
    name: "User Authentication"
    entities: ["user_login", "user_logout", "password_reset"]
    priority: must
    depends_on: []

  - id: "order_mgmt"
    name: "Order Management"
    entities: ["order_create", "order_view", "order_cancel"]
    priority: should
    depends_on: ["user_auth"]
```

### Checkpoint Triggers

Write session state when:
- User confirms a grouping
- Priority assigned to a group
- New constraint captured
- Before asking "anything we missed?"

## Common Anti-Patterns (per ADR-002)

- Never announce methods ("I'm using MoSCoW prioritization...")
- Never announce skills ("Loading diamond-converge...")
- Never use threshold gates ("We need 5 groups before proceeding...")
- Never use generic probes ("Any constraints?" - too vague)
- Always output artifact links when creating files

| Avoid | Instead |
|-------|---------|
| "I'm using MoSCoW prioritization..." | Just ask priority questions naturally |
| "We need 5 groups before proceeding..." | User-driven, no arbitrary thresholds |
| Grouping without showing user | Propose groupings, get confirmation |
| "Any constraints?" (too vague) | "Are there technical limitations around [specific area]?" |
| Forcing priority on single items | Group first, then prioritize groups |
| Ignoring new information | Capture it, even if means brief return to diverge |

## Skill Transition

```yaml
ON transition_to_synthesize:
  1. Save current session state (checkpoint)
  2. Output: "Groups confirmed. Ready to synthesize these into structured artifacts."
  3. HD must read_file(".claude/skills/diamond-synthesize.md")

ON return_to_diverge (user adds new scope):
  1. Save checkpoint with: converge.interrupted_for_scope = true
  2. HD must read_file(".claude/skills/diamond-diverge.md")
```

## Example Flow

```
HD: "From our discussion I captured:
     - User login, logout, password reset
     - Order creation, viewing, cancellation
     - Admin dashboard, reporting

     Let me group these. I see authentication items together,
     order management together, and admin features together.
     Does that structure make sense?"

User: "Yes, but dashboard and reporting are different things."

HD: "Good catch. So: Auth, Orders, Dashboard, Reporting - four groups.
     If you could only have two of these for launch, which two?"

User: "Auth and Orders. Dashboard can wait."

HD: "So Auth and Orders are must-haves, Dashboard and Reporting
     are could-haves for later. Any technical constraints around
     the authentication - like existing systems to integrate with?"

User: "We need to use our company SSO."

HD: [Captures constraint]
    "Noted - SSO integration is a constraint.
     Let me confirm: Auth (must), Orders (must), Dashboard (could),
     Reporting (could). SSO required. Anything grouped wrong?"
```

---
*Skill Version: 1.0.0*
*Architecture: ADR-002 HD Composition*
