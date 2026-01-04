# Red Team (QA/Review)

**Quality Seals - Compare SSoT docs vs actual implementation to find drift.**

Trust but Verify. Assume 20% of work and documentation doesn't match reality.

---

## Recent Audits

| Date | Audit | Scope |
|------|-------|-------|
| *No audits yet* | - | - |

---

## How `/red-team` Works

```mermaid
flowchart TB
    subgraph INPUT
        A[User invokes /red-team]
        B[Audit Scope]
    end

    subgraph SETUP[Phase 0: Setup]
        C[Opus Orchestrator]
        D[Path Validation]
    end

    subgraph SECTORS[Phase 1: Sector Execution]
        E[Pro Sector Commanders]
        F[Flash Specialists]
        G[Sector Reports]
    end

    subgraph SYNTHESIS[Phase 2: Synthesis]
        H[Pro Synthesizer]
        I[Cross-Sector Patterns]
    end

    subgraph OUTPUT[Phase 3: Final Audit]
        J[Kill List + Fix List + Gap Table]
    end

    A --> C
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
```

---

## Audit Sectors

| Sector | Name | Focus |
|--------|------|-------|
| **1** | SSoT Integrity | Documentation vs reality, ADR compliance |
| **2** | Agent Architecture | Constitution compliance, role boundaries |
| **3** | API/Tool Contracts | Interface signatures, implementation gaps |
| **4** | Workflow Mechanics | State machines, transition validity |
| **5** | Skills & Commands | Zombie skills, ghost commands, prompt vs behavior |
| **6** | Template Fitness | Orphan templates, usage validation, output formats |

---

## Scope Options

| Scope | Sectors | Use Case |
|-------|---------|----------|
| **full** | All 6 sectors | Comprehensive audit |
| **core** | Sectors 1-3 | Quick health check |
| **custom** | User-specified | Targeted investigation |

---

!!! tip "Running Audits"
    Run `/red-team` to execute a quality seals audit.
