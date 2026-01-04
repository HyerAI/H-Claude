# Session Context

**Current session state and focus.**

---

!!! info "Local File"
    Open `.claude/context.yaml` in your editor to view/edit session state.

    This file is outside the PM docs folder and cannot be rendered here.

---

## What context.yaml Contains

```yaml
meta:
  last_modified: timestamp

project:
  name: project-name

focus:
  current_objective: what we're working on

recent_actions:
  - '[DATE] what was done'

tasks:
  active: []

blockers: []
backlog: []

think_tank:
  - topic: topic_name
    path: session_path
    status: active | paused | decided
```

!!! tip "Quick Access"
    ```bash
    cat .claude/context.yaml
    ```
