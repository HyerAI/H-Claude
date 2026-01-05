# Flowchart Designer Learnings

> **Purpose:** Automatic knowledge accumulation from every flowchart task. Patterns that recur 3+ times are promoted to templates or checklists.

---

## Learning Categories

| Category | What to Record | Promotes To |
|----------|----------------|-------------|
| **Layout Pattern** | Spacing, positioning that worked well | `templates/` snippet |
| **Visual Preference** | Color, style, font choices user liked | Style guide updates |
| **Feedback Correction** | User-requested changes (what→what) | Checklist item |
| **Edge Routing Fix** | Arrow/path improvements | Best practices |
| **Iteration Note** | What changed between versions | Template refinement |
| **Mind-Change** | User reversed a previous decision | Decision patterns |

---

## Recurrence Tracking

Learnings are tagged with `[N]` indicating how many times the pattern has been seen.

**Promotion Threshold:** 3+ occurrences → auto-flag for template/checklist promotion.

---

## Active Learnings

<!--
ENTRY FORMAT:
### [DATE] - [CHART_NAME] - [CATEGORY]

**Context:** What chart/task this relates to
**Learning:** What was discovered
**User Feedback:** Direct quote or paraphrase if applicable
**Previous Value:** (for corrections/mind-changes)
**New Value:** What it became
**Recurrence:** [N]
**Promotion Ready:** YES/NO
-->

### 2025-12-28 - Workflow_Flowchart - Feedback Correction (UPDATED)

**Context:** HDA Suite agents at colHDA1=420, colHDA2=550 overlapped with workflow edges between Product Owner (x=280) and EventProcessor (x=530). The APPROVED edge and story flow arrows crossed through the HDA nodes.
**Learning:** When positioning auxiliary agents, check for edge paths between major nodes. Place auxiliary groups OUTSIDE the main workflow flow - either far left or far right of the canvas. Using x positions between connected nodes will cause edge overlap.
**User Feedback:** "The HDA agents are in the chart but overlaying other items and make it unreadable"
**Previous Value:** colHDA1=420, colHDA2=550 (between PO and EP - caused overlap)
**New Value:** colHDA1=1100, colHDA2=1230 (far right, past all workflow nodes)
**Recurrence:** 2 (same chart, second correction)
**Promotion Ready:** NO

### 2025-12-28 - Workflow_Flowchart - Layout Pattern (Edge-Aware Positioning)

**Context:** HDA Suite needed to be visible near HD but not blocking workflow edges
**Learning:** CRITICAL: When adding agent groups, calculate edge paths first. Main workflow edges (PO→EP, EP→Agents, Agent→Gatekeeper) form a visual "highway" through the center. Auxiliary agents should be placed in "parking areas" at the edges of the canvas (x > 1000 for right side, x < 0 for left side) to avoid crossing the highway.
**User Feedback:** Visual inspection revealed overlap
**Previous Value:** N/A (new pattern)
**New Value:** Use far-right positioning (colHDA1=1100+) for auxiliary agent groups
**Recurrence:** 1
**Promotion Ready:** NO

---

### 2025-12-28 - Workflow_Flowchart - Layout Pattern (Updated)

**Context:** Adding 4 HDA Suite agents to SUPPORT section
**Learning:** When adding assistant agents that serve a parent, use a 2x2 grid layout adjacent to the parent. Create two columns (colHDA1, colHDA2) and two rows (rowTop, rowHDA2). Connect with bidirectional edges showing spawn/return flow.
**User Feedback:** Corrected after initial implementation
**Previous Value:** Single vertical column
**New Value:** 2x2 grid: (colHDA1, rowTop), (colHDA2, rowTop), (colHDA1, rowHDA2), (colHDA2, rowHDA2)
**Recurrence:** 1
**Promotion Ready:** NO

---

### 2025-12-28 - Workflow_Flowchart - Edge Pattern

**Context:** HDA Suite edges connecting to Product Owner
**Learning:** For ephemeral spawn→task→die agents, use paired edges: outgoing (action label like "search", "brief me") and returning (result label like "results", "summary"). This visualizes the request/response nature of assistant agents.
**User Feedback:** N/A
**Previous Value:** N/A
**New Value:** 8 edges added (4 outgoing from HD, 4 returning)
**Recurrence:** 1
**Promotion Ready:** NO

---

## Promoted Patterns (Applied to Templates)

*Patterns that have been promoted from learnings to templates/checklists.*

---

## Mind-Change Log

> **Purpose:** Track when users reverse decisions to understand design preference evolution.

| Date | Chart | Original Choice | Changed To | Reason |
|------|-------|-----------------|------------|--------|
| *none* | *none* | *none* | *none* | *none* |

---

## Feedback Patterns Summary

> **Auto-generated:** Common feedback themes across charts.

| Pattern | Frequency | Status |
|---------|-----------|--------|
| *none yet* | *-* | *-* |

---

*Last Updated: 2025-12-28*
*Version: 1.0.1*
