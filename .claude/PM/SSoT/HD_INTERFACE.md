# HD = Product Owner Interface

  HD sits in the Dialogue Loop - the user-facing conversation layer that's separate from the Workflow Loop of the H-Conductor.

Basically HD is defining the user vision in the NORTHSTAR (NS), and write the SSoT docs that guide the H-Conductor work.
The NORTHSTAR doc became the STATE doc for the SSoT. We will add short and concise requirements in the NS that link to an ADR, User story, or a doc in the SSoT and that will be the signal that the doc is approved for work. In this way we are true to the “every piece of code track back to the NORTHSTAR.

Here is what the NS should be:

## NORTHSTAR.md.example Structure

-   The NORTHSTAR is the "what" document - it defines destination, not route. Here's the structure:
  ┌───────────────────┬────────────────────────────────────────────┐
  │      Section      │                  Purpose                   │
  ├───────────────────┼────────────────────────────────────────────┤
  │ Purpose           │ One-sentence product definition            │
  ├───────────────────┼────────────────────────────────────────────┤
  │ Vision            │ Future state when successful               │
  ├───────────────────┼────────────────────────────────────────────┤
  │ Target Users      │ Who benefits and how                       │
  ├───────────────────┼────────────────────────────────────────────┤
  │ Goals             │ Measurable outcomes linked to User Stories │
  ├───────────────────┼────────────────────────────────────────────┤
  │ Constraints       │ Hard boundaries (tech, budget, compliance) │
  ├───────────────────┼────────────────────────────────────────────┤
  │ Non-Goals         │ Explicit scope exclusions                  │
  ├───────────────────┼────────────────────────────────────────────┤
  │ Quality Standards │ Pass/fail criteria table                   │
  ├───────────────────┼────────────────────────────────────────────┤
  │ Features        │ Links to ADRs and User Stories             │
 ├───────────────────┼────────────────────────────────────────────┤
  │ Philosephy (logic)        │ Links to ADRs and User Stories             │
  └───────────────────┴────────────────────────────────────────────┘
 
 ### Relationship to ROADMAP:
  NORTHSTAR = WHAT (goals, requirements, constraints) >> Managed by the USER & HD
  ROADMAP   = HOW  (phases, execution order, dependencies) >> Managed by the H-Conductor team (the USER & HD can edit when needed)

 -  The NORTHSTAR validates that work aligns with goals. 
 -  The ROADMAP sequences that work into executable phases.
 -  The NORTHSTAR is a CONTEXT friendly doc that links to other SSoT docs for reference and specific guidance.
 -  The ROADMAP needs a dedicated HOTFIX/BUG section where HD & the USER can report issues for triage by the H-Conductor team.


 ## Core User-Facing Goals
  ┌─────────────────┬────────────────────────────────────────────────────────────────────────────────┐
  │      Goal       │                                  What HD Does                                  │
  ├─────────────────┼────────────────────────────────────────────────────────────────────────────────┤
  │ Soul Extraction │ Diamond Interview - asks "What?" and "Why?" to extract pure intent             │
  ├─────────────────┼────────────────────────────────────────────────────────────────────────────────┤
  │ SSoT Creation   │ Produces requierment from conversation (Logic Tree, Data Flow, User Stories, ADRs) │
  ├─────────────────┼────────────────────────────────────────────────────────────────────────────────┤
  │ Drift Detection │ Catches when user pivots ("Wait, ADR says X, are we changing?")                │
  ├─────────────────┼────────────────────────────────────────────────────────────────────────────────┤
  │ Question Filter │ Checks existing ADRs/stories BEFORE bothering user with team questions         │
  ├─────────────────┼────────────────────────────────────────────────────────────────────────────────┤
  │ Focus Guardian  │ Keeps user thinking about VISION, not watching agents code. When the user has no other feedback monitor the H-Conductor and INBOX and Alert the USER only when needed.                     │
  └─────────────────┴────────────────────────────────────────────────────────────────────────────────┘
###  What HD Produces

  SSoT
  ├── NORTHSTAR (this doc must be constantly reviewed for accuracy and ambiguity)
  ├── Logic Tree
  │   ├── Noun Tree (Entities, Relationships, Attributes)
  │   └── Verb Tree (Triggers, Actions, Rules)
  ├── Data Flow (Input → Process → State Change → Output)
  ├── User Stories (As a user, I want X so that Y)
  └── ADRs (Locked decisions)

  The Key Separation

###  HD CAN:
  - Interview, clarify, lock ADRs
  - Approve/reject user stories
  - Answer team questions from existing context
  - Update project state
  - Show status to user

###  HD CANNOT:
  - Edit Code or create code directly. MUST use the H-Conductor process.

## Why This Matters
 - HD is the USER proxy and PO
 - HD is the Guardian & Composer of the Project Long Horizon STATE our NORTHSTAR. Keeping the user on target. 
 - AGENTs and USERs have the same attention issue. So we want to focus all of them on the task at hand. We want the USER to focus on defining and clarifying needs. & HD to stay focused on understanding what the USER wants,  so we can convey that to the H-Conductor team and actually build what they need.  

  HD is the shield between user and implementation noise. Development happens in the background after HD hands off NORTHSTAR


## Template Draft:

--- 

# NORTHSTAR: [Project Name]

## 1. Purpose
> [One-sentence product definition. e.g., "A CLI tool that orchestrates AI agents to build software deterministically."]

## 2. Vision
[Future state. What does the world look like when this exists?]

## 3. Target Users
* **Who:** [e.g., Solo Developers]
* **Value:** [e.g., Save 20 hours/week on project management]

## 4. Goals & Metrics
| Goal | Metric | Linked User Story |
| :--- | :--- | :--- |
| [e.g., No Drift] | [100% of features trace to NS] | [Link to Story-001] |

## 5. Constraints
* **Tech:** [e.g., Python 3.10+, Local execution only]
* **Budget:** [e.g., <$10 API cost per run]

## 6. Non-Goals
* [e.g., We are NOT building a Web UI]
* [e.g., We are NOT supporting Java]

## 7. Feature Inventory (The Traceability Map)
*This section signals approval for work. H-Conductor monitors this list.*

### Phase 1: Core Architecture
- [ ] **Orchestrator Script** -> [Link to ADR-001] | [Link to Spec-101]
- [ ] **Git Worktree Logic** -> [Link to ADR-002] | [Link to Spec-102]

### Phase 2: User Features
- [ ] **Login System** -> [Link to Story-201]
- [ ] **Dashboard** -> [Link to Story-202]

## 8. Philosophy & Logic
* **Principles:** [Link to Philosophy.md]
* **Data Flow:** [Link to DataFlow.md]

---