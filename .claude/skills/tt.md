# /tt - Think Tank Router

**Purpose:** Check for existing think-tank sessions before starting new ones.
Preserves topic continuity by leveraging existing Knowledge Base.

## Usage

```
/tt "topic description"
/tt auth           # searches for "auth" in existing sessions
/tt --list         # show all think-tank sessions
```

## Protocol

### Step 1: Parse Input

```
TOPIC = $ARGUMENTS (lowercase, slugified)
```

### Step 2: Check Existing Sessions

```yaml
# Read context.yaml → think_tank section
# Search for matching topic (fuzzy match on topic name)
```

**Match Logic:**
- Exact match on topic slug
- Partial match (topic contains search term)
- Recent sessions (last 30 days) weighted higher

### Step 3: Route Decision

```
IF --list flag:
  → Display all sessions with status
  → EXIT

IF matching session found:
  → Show match with status and path
  → Ask user: RESUME | FRESH | CANCEL

  IF RESUME:
    → /think-tank "${TOPIC}" --resume
  IF FRESH:
    → /think-tank "${TOPIC}"
  IF CANCEL:
    → EXIT

IF no match:
  → /think-tank "${TOPIC}"
```

### Step 4: Update Context

After routing, context.yaml is updated by /think-tank itself.

---

## Output Format

### When Match Found

```
Found existing session: "${topic}"
  Path: ${path}
  Status: ${status}
  Created: ${date}

  [R] Resume with existing KB
  [F] Start fresh (archives old)
  [C] Cancel
```

### When No Match (--list)

```
Think Tank Sessions:

  ACTIVE
  - auth_flow_20260104 (active)
  - api_design_20260103 (paused)

  DECIDED
  - hc_system_prompt_design_20260104
  - agentic_framework_20260103
```

---

## Why This Matters

Think-tank sessions are **persistent context states**:
- Knowledge Base with gathered facts
- Decision history and rationale
- Consistent perspective on the subject

Without checking first, HC loses this continuity and
duplicates research effort.
