# Generator: Action Items (MAIN Session)
# Variables: {{SESSION_PATH}}
# Model: HC_REAS_B (2411)

# Action Items Generator - MAIN Session

## Your Mission
Extract discrete action items from the MAIN think-tank session.

## Context Files
1. {{SESSION_PATH}}/00_BRIEFING.md - Project vision
2. {{SESSION_PATH}}/03_SESSIONS/session_NNN.md - Council discussion
3. {{SESSION_PATH}}/04_DECISION_MAP.md - Options identified

## Requirements
- Extract 3-7 action items (MIN 3, MAX 7)
- Each item must be independent enough for its own sub think-tank
- Identify dependencies between items
- Order by logical sequence (dependencies first)

## Output
Write to: {{SESSION_PATH}}/action-items.yaml

## Schema
```yaml
version: 1
created: YYYY-MM-DD
status: draft  # draft | approved

items:
  - id: AI-001
    title: "[Clear, actionable title]"
    description: "[1-2 sentence description]"
    scope: "[What's included/excluded]"
    success_criteria:
      - "[Measurable outcome]"
    depends_on: []  # List of AI-XXX ids
    estimated_complexity: low|medium|high
    status: pending  # pending | in_progress | completed
    sub_session_path: null

  - id: AI-002
    title: "..."
    depends_on: [AI-001]
    # ...
```

## Guidelines
- Each item should take 1-3 sub think-tank sessions to resolve
- Dependencies should form a DAG (no cycles)
- First items should have no dependencies
- Last items can depend on multiple earlier items
