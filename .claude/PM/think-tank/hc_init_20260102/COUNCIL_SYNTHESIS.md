# Council Synthesis: Hierarchical Think-Tank Workflow

**Agents:** 2 Pro (2406), 2 Opus (2408)
**Date:** 2026-01-02

---

## CONSENSUS ITEMS (3-4 agents agree)

### Strengths Confirmed

| Strength | Agents | Summary |
|----------|--------|---------|
| **Separation of concerns** | ALL 4 | Vision vs tactics is correct pattern |
| **Traceability/Lineage** | ALL 4 | Audit trail from vision → execution |
| **Scalable parallelism** | ALL 4 | Sub think-tanks can run independently |
| **Scope containment** | 3/4 | Prevents planning sessions from solving everything |

### Risks Confirmed

| Risk | Agents | Summary |
|------|--------|---------|
| **Session proliferation/sprawl** | ALL 4 | Many folders, no cleanup strategy |
| **Execution ordering/dependencies** | 3/4 | Action items may depend on each other |
| **Vision/MAIN drift over time** | 3/4 | Long-horizon docs rot without refresh |
| **Conflict between sub-sessions** | 3/4 | No mechanism to prevent contradictory decisions |

### Gaps Confirmed

| Gap | Agents | Summary |
|-----|--------|---------|
| **No feedback loop to MAIN** | ALL 4 | Sub-session can't escalate back |
| **Parent-child linking undefined** | ALL 4 | How do artifacts reference each other? |
| **hc-init scope unclear** | ALL 4 | Does it scaffold OR plan? Or both? |
| **Lifecycle states missing** | 3/4 | No active/completed/abandoned tracking |
| **Completion criteria absent** | 3/4 | When is MAIN Think-Tank "done"? |

### Suggestions Confirmed

| Suggestion | Agents | Summary |
|------------|--------|---------|
| **Separate hc-init from MAIN Think-Tank** | ALL 4 | Init = scaffold, Think-Tank = plan |
| **Add session lifecycle states** | ALL 4 | active/paused/completed/archived |
| **Archive/cleanup protocol** | ALL 4 | Move completed sessions out of working dir |
| **Define action item schema** | 3/4 | Structured handoff, not free text |
| **Cap action items 3-7** | 3/4 | More than 7 = vision not focused |
| **Add skip/lightweight mode** | 2/4 | Simple projects don't need full hierarchy |

---

## TIEBREAKER ITEMS (2 agents)

| Item | Agents | Orchestrator Decision |
|------|--------|----------------------|
| Add shared decisions registry (ADR-like) | Pro-1, Opus-2 | **INCLUDE** - prevents conflicting choices |
| Add --refresh flag for MAIN | Opus-2, Opus-1 | **INCLUDE** - addresses vision drift |

---

## NO CONSENSUS (1 agent only - IGNORED)

| Item | Agent | Reason Ignored |
|------|-------|----------------|
| Checkpoint ADRs at sub-TT completion | Opus-2 | Already have ADR writer skill |
| Make MAIN validate against NORTHSTAR | Pro-2 | Implied, not separate feature |

---

## RECOMMENDED CHANGES TO PLAN

### 1. Split hc-init (ALL 4 AGREE)

```
hc-init --scaffold    → Create folders, context.yaml, prompt for NORTHSTAR
hc-init --vision      → Launch MAIN Think-Tank (or just /think-tank --main)
```

### 2. Add Parent Reference to Sub-Sessions (ALL 4 AGREE)

```yaml
# In sub think-tank STATE.yaml
parent:
  type: main_think_tank
  path: .claude/PM/think-tank/project_vision_20260102/
  action_item_id: "AI-001"
  action_item_title: "Implement authentication system"
```

### 3. Add action-items.yaml Output from MAIN (3/4 AGREE)

```yaml
# Output from MAIN Think-Tank
action_items:
  - id: AI-001
    title: "Implement authentication system"
    context: "JWT-based, integrate with existing user model"
    constraints: ["Must support refresh tokens", "No third-party auth yet"]
    depends_on: []
    status: pending  # pending | in_progress | completed | abandoned

  - id: AI-002
    title: "Add payment integration"
    context: "Stripe for MVP"
    constraints: ["Test mode only initially"]
    depends_on: ["AI-001"]  # Needs auth first
    status: pending
```

### 4. Add Lifecycle States (ALL 4 AGREE)

```yaml
# In context.yaml think_tank entries
think_tank:
  - topic: project_vision
    type: main
    status: active  # active | paused | completed | archived
    action_items_path: .../action-items.yaml

  - topic: auth_system
    type: sub
    parent: project_vision
    status: completed
    archived: 2026-02-15
```

### 5. Add Escalation Protocol (ALL 4 AGREE)

When sub think-tank encounters:
- Scope expansion needed → Flag for MAIN review
- Blocking conflict with another AI → Escalate to user
- Infeasibility detected → Pause and escalate

---

## UPDATED WORKFLOW

```
hc-init --scaffold
    ↓
    Creates: folders, context.yaml, NORTHSTAR.md template
    ↓
/think-tank --main "Project Vision"
    ↓
    Outputs: action-items.yaml (3-7 items with dependencies)
    ↓
For each action item (respecting dependencies):
    ↓
    /think-tank "AI-001: Auth system" --parent=project_vision
        ↓
        Sub think-tank with parent reference
        ↓
        execution-plan.yaml
        ↓
    /hc-plan-execute
        ↓
    Mark action item complete in action-items.yaml
    ↓
When all items complete:
    ↓
    Archive MAIN session
```

---

## ACTION REQUIRED

Update `execution-plan.yaml` to incorporate:

1. [ ] Split hc-init phases (scaffold vs vision)
2. [ ] Add action-items.yaml schema/template
3. [ ] Add parent reference to STATE.yaml schema
4. [ ] Add lifecycle states to context.yaml tracking
5. [ ] Define escalation protocol in think-tank command
