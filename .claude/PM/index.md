# H-Claude PM Observatory

**AI-orchestrated project management for agentic coding.**

---

<div class="grid cards" markdown>

-   :material-head-lightbulb:{ .lg .middle } **Plan**

    ---

    `/think-tank` convenes a council of experts to map decisions, surface trade-offs, and create execution plans.

    [:octicons-arrow-right-24: NORTHSTAR](SSoT/NORTHSTAR.md)

-   :material-play-circle:{ .lg .middle } **Execute**

    ---

    `/hc-execute` runs SWEEP & VERIFY with Oraca orchestrators, QA gates, and the "15% Hunter" sweep.

    [:octicons-arrow-right-24: Agent Roles](SSoT/AGENT_ROLES.md)

-   :material-magnify:{ .lg .middle } **Review**

    ---

    `/hc-glass` deploys 6 sector commanders to audit code against docs. Trust nothing.

    [:octicons-arrow-right-24: ADRs](SSoT/ADRs/ADR-001-diffusion-development-framework.md)

-   :material-shield-search:{ .lg .middle } **Audit**

    ---

    `/red-team` performs deep multi-layer quality audits. Find the rot, the lies, the fragile logic.

    [:octicons-arrow-right-24: Changelog](CHANGELOG.md)

</div>

---

## Command Flow

```mermaid
graph LR
    A[NORTHSTAR] --> B[think-tank]
    B --> C[ROADMAP]
    C --> D[hc-execute]
    D --> E[Codebase]
    E --> F[hc-glass]
    E --> G[red-team]
    F --> H[Issues]
    G --> H
    H -.-> B
```

---

## Quick Links

| Document | Purpose |
|----------|---------|
| [:material-compass: **NORTHSTAR**](SSoT/NORTHSTAR.md) | Project goals & requirements |
| [:material-account-group: **Agent Roles**](SSoT/AGENT_ROLES.md) | Role definitions |
| [:material-history: **Changelog**](CHANGELOG.md) | Version history |
| [:material-book-open: **Get Started**](docs/GET_STARTED.md) | Installation guide |

---

<div style="text-align: center; color: #6ba8b9; font-size: 0.85rem; margin-top: 2rem;">

**Agent Hierarchy:** Opus (strategy) → Pro (reasoning) → Flash (execution)

</div>
