# Execution

**Oraca-orchestrated execution with QA gates and 20% Hunter sweep.**

---

## Recent Executions

| Date | Execution | Status |
|------|-----------|--------|
| 2026-01-04 | [Think-Tank Improvements](think_tank_improvements_20260104/index.md) | Complete |
| 2026-01-04 | [Gauntlet Integration](gauntlet_integration_20260104/index.md) | Complete |
| 2026-01-03 | [Diffusion Framework](diffusion_framework_20260103/index.md) | Complete |

---

## How `/hc-execute` Works

```mermaid
flowchart TB
    subgraph INPUT
        A[User invokes /hc-execute]
        B[execution-plan.yaml]
    end

    subgraph PHASE0[Phase 0: Checkpoint]
        C0[git-engineer]
        C1[ROLLBACK_HASH stored]
    end

    subgraph PHASE1[Phase 1: Parse & Contract]
        C[Opus Orchestrator]
        D[INTERFACES.md]
    end

    subgraph PHASE2[Phase 2: Phased Execution]
        E[Oraca Phase Orchestrator]
        F[Flash Workers]
        G[Pro Phase QA]
    end

    subgraph PHASE3[Phase 3-5: Verification]
        H[QA Synthesis]
        I[20% Hunter Sweep]
        J[Validation Report]
    end

    subgraph PHASE6[Phase 6: ROADMAP Sync]
        L[Update ROADMAP.yaml]
        M[Unlock next phases]
    end

    subgraph OUTPUT
        K[COMPLETION_REPORT.md]
    end

    A --> C0
    B --> C0
    C0 --> C1
    C1 --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> L
    L --> M
    M --> K
```

---

## Execution Phases

| Phase | Agent | Purpose |
|-------|-------|---------|
| **0. Checkpoint** | git-engineer | Create rollback point before execution |
| **1. Parse & Contract** | Opus | Batch tasks, define interfaces |
| **2. Phased Execution** | Oraca + Flash | Execute tasks in parallel |
| **3. QA Synthesis** | Pro | Validate all deliverables |
| **4. Sweep** | Pro | 20% Hunter - find missed tasks, edge cases |
| **5. Validation** | Opus | Final report |
| **6. ROADMAP Sync** | Opus | Update ROADMAP.yaml status, unlock next phases |

---

!!! tip "Running Executions"
    Run `/hc-execute` after approving a think-tank plan.
