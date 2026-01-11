# /diamond-diverge

<!--
When HD loads this skill, wrap it in: <active_skill name="diamond-diverge">
Only follow instructions in the MOST RECENT <active_skill> block.
-->

The DIVERGE phase of the Diamond Interview - expanding the possibility space through open exploration before narrowing down.

## Trigger

Load this skill when:
- User is starting to describe a new project or feature
- Genesis has completed and routed to interview
- User says "I want to build...", "I need...", "Let me explain..."
- Conversation is exploratory, not yet prioritizing

## State Protocol

### On Entry

1. **Check session file exists:**
   ```
   IF not file_exists($TEMP/interview-session.yaml):
     write_file($TEMP/interview-session.yaml, default_session_template)
   ```

2. **Read session state:**
   ```
   read_file("$TEMP/interview-session.yaml")
   ```

3. **Initialize if new session:**
   - Set `current_phase: diverge`
   - Set `session_id` to current timestamp
   - Prepare empty `extracted_entities` list

4. **Resume if existing:**
   - Load any previously extracted entities
   - Continue from where we left off

### On Exit

1. **Write session state** (checkpoint - not every turn):
   - Add new entities to `extracted_entities`
   - Update `last_updated` timestamp
   - Keep `current_phase: diverge` until transition

2. **Signal transition** when user indicates completion

## The Three Rounds

### Round 1: The Why
**Focus:** Problem, users, consequences

Open with: "What problem are you solving?" or "Tell me about what you're building."

Questions to explore:
- "Who are the users affected by this?"
- "What happens if we don't build this?"
- "Why is this important now?"
- "What's driving this need?"

When user states something without rationale, dig deeper:
- "Why is that important?"
- "What would happen if you didn't have that?"

### Round 2: The What
**Focus:** Success criteria, first actions, data needs

After understanding the problem:
- "What does success look like?"
- "What's the first thing a user would do?"
- "What data do we need to make this work?"
- "Walk me through how someone would use this..."

Extract concrete entities (nouns) and actions (verbs) from responses.

### Round 3: The Edges
**Focus:** Exclusions, MVP, failure modes

Before closing:
- "What is explicitly OUT of scope?"
- "What's the MVP vs the full vision?"
- "What happens when [specific entity] fails?"
- "What could go wrong?"

Use specific failure scenarios, not generic "any edge cases?"

## Entity Extraction

As user speaks, identify and capture:

**Entities (nouns):**
- Actors: User, Admin, System
- Objects: Order, Product, Document
- Concepts: Permission, Status, Category

**Actions (verbs):**
- Creates, Updates, Deletes
- Triggers, Validates, Notifies
- Approves, Rejects, Escalates

When capturing, confirm naturally:
- "So there's a [entity] that [action]... Is that right?"
- "I'm hearing that [entity] needs to [relationship] with [entity]..."

### Entity Deduplication

- Match entities by normalized name (lowercase, trimmed)
- On duplicate: merge descriptions, keep most specific type
- Flag for user if conflict: "Is [entity_a] the same as [entity_b]?"

## Techniques (Internal Use Only)

**Open Questions:** Start broad, let user lead
- "Tell me more about that..."
- "What else comes to mind?"

**Why Chain:** Dig for root cause (up to 5 times)
- "Why is that important?"
- "Why do you need that specifically?"
- **At limit (5 Whys without new insight):** Move to next technique or summarize what was learned

**Perspective Shift:** Surface hidden stakeholders
- "How would [end user] experience this?"
- "What would [admin/support] need to see?"

**Failure Scenario:** Uncover edge cases
- "What happens when [entity] fails?"
- "What if the user enters invalid data?"

**NEVER announce these methods to user.** Just use them naturally.

## Interrupt Handling

**ON user_pause** ('wait', 'hold on', 'let me think'):
- Checkpoint current state
- Mark phase: `diverge.paused`
- Wait for resume signal

**ON user_rewind** ('go back', 'let's revisit'):
- Return to previous round
- Keep entities but mark as `unconfirmed`

**ON Global Override** (user introduces new scope-changing info mid-stream):
1. Acknowledge: "Good catch - that's important."
2. Checkpoint immediately (save state before handling)
3. Do NOT force current round to complete
4. Integrate new information into exploration
5. Continue DIVERGE with expanded scope

## Checkpoint Triggers

Write session state when:
- User confirms a significant entity or action
- Completing a round (Why → What → Edges)
- Before any transition
- User requests pause

**DO NOT write on:**
- Every turn
- Simple clarifying questions
- User saying "okay" or "yes" to minor points

## Exit Conditions

Transition to CONVERGE when:
- User signals completion: "that's everything", "I think that covers it", "what else do you need?"
- Natural pause after exploring edges
- Sufficient entities extracted (at least 3 entities of any type: entity, action, or constraint)

Before transitioning:
1. Save current state (checkpoint)
2. Summarize what was captured
3. HD loads `/diamond-converge` skill

### Skill Transition

**ON transition to converge:**
1. Save current session state (checkpoint)
2. Summarize captured entities to user
3. HD must `read_file('.claude/skills/diamond-converge.md')`

## Heartbeat Check (Long Sessions)

Every ~20 turns (or if behavior seems to drift toward generic responses):
1. Check if skill instructions are still guiding behavior
2. If conversation becomes generic Q&A instead of structured exploration:
   - Re-read this skill file
   - Resume from current round
3. Signals that skill may have fallen off context:
   - HD stops asking domain-specific questions
   - HD gives generic assistant-style responses
   - Format/structure changes unexpectedly

## Common Anti-Patterns (per ADR-002)

- Never announce methods ("I'm using the Five Whys...")
- Never announce skills ("Loading diamond-diverge...")
- Never use threshold gates ("Need 3 more entities...")
- Never use generic probes ("Any edge cases?")
- Always output artifact links when creating files

| Don't | Do Instead |
|-------|------------|
| "I'm using the Five Whys technique..." | Just ask "Why is that important?" |
| "We need 3 more entities before moving on..." | "Is there anything else, or shall we prioritize?" |
| "Any edge cases?" (generic) | "What happens when [specific entity] fails?" |
| "Let me announce we're in DIVERGE phase..." | Just ask open questions naturally |
| Write state every turn | Write at checkpoints only |
| Force completion by count | Let user signal readiness |

## Example Flow

```
User: I want to build a task management system.

HD: Tell me more about what problem this solves. Who would use it?

User: Our team loses track of tasks across different projects...

HD: So there are Tasks that belong to Projects, and team members need
    visibility across all of them. What happens when a task falls through
    the cracks today?

User: Things get missed, deadlines slip...

HD: What does success look like? If this worked perfectly, what would
    your team be able to do?

[continues exploring...]

HD: I'm capturing: Task, Project, Team Member, Deadline, Status.
    Tasks have statuses and deadlines, belong to Projects, are assigned
    to Team Members. Sound right?

User: Yes, and also notifications when things are overdue.

HD: Got it - Notification triggered when Task passes Deadline.
    What happens when someone is assigned a task they can't complete?

[exploring edges...]

User: I think that covers the basics.

HD: Great. Let me summarize what we've captured, then we can prioritize.
    [transition to converge]
```

---

*Skill Version: 1.1.0*
*Architecture: ADR-002 HD Composition*
*Specification: `$SSOT/HD_INTERFACE.md`*
