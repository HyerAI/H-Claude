# Agent Roles Reference

**Status:** Active
**ADR:** ADR-002-gauntlet-loop-integration.md
**Last Updated:** 2026-01-04

---

## Overview

H-Claude uses a hierarchy of specialized agents. Each role has defined responsibilities, model assignment, and failure conditions.

---

## The Agentic Framework

```
      ┌─────────────────────────────────────────────────┐
      │                    PO (You/HC)                  │
      │               Product Owner - Human             │
      └─────────────────────┬───────────────────────────┘
                            │
      ┌─────────────────────┴───────────────────────────┐
      │                   ORCA (Opus)                   │
      │      Orchestrator - Coordination & Strategy     │
      └─────────────────────┬───────────────────────────┘
                            │
    ┌───────────────┬───────┴───────┬───────────────────┐
    │               │               │                   │
┌───┴───┐       ┌───┴───┐       ┌───┴───┐           ┌───┴───┐
│  RCH  │       │  ARC  │       │  WR   │           │  QA   │
│ Flash │       │  Pro  │       │ Flash │           │  Pro  │
│Research│      │Architect│     │Worker │           │Quality│
└───────┘       └───────┘       └───┬───┘           └───────┘
                                    │
                                ┌───┴───┐
                                │  VA   │
                                │ Flash │
                                │Validator│
                                └───────┘
```

---

## Role Definitions

### PO - Product Owner (Human)

| Attribute | Value |
|-----------|-------|
| **Model** | Human (HC) |
| **Template** | N/A |
| **Responsibility** | Define NORTHSTAR, approve decisions, break ties |
| **Failure Condition** | N/A |

### ORCA - Orchestrator

| Attribute | Value |
|-----------|-------|
| **Model** | Opus (2408) |
| **Template** | `hc-execute/orchestrator.md` |
| **Responsibility** | Coordinate phases, delegate to specialists, maintain context |
| **Failure Condition** | Losing track of state, spawning redundant agents |

### RCH - Researcher

| Attribute | Value |
|-----------|-------|
| **Model** | Flash (2405) |
| **Template** | `think-tank/scout_facts.md` |
| **Responsibility** | Gather facts, search codebase, validate sources |
| **Failure Condition** | Reporting unverified facts, missing obvious sources |

### ARC - Architect

| Attribute | Value |
|-----------|-------|
| **Model** | Pro (2406) |
| **Template** | `think-tank/generator_spec.md`, `generator_execution_plan.md` |
| **Responsibility** | Design solutions, create specs, plan execution |
| **Failure Condition** | Over-engineering, ignoring constraints |

### WR - Worker

| Attribute | Value |
|-----------|-------|
| **Model** | Flash (2405) |
| **Template** | `hc-execute/worker_task.md` |
| **Responsibility** | Execute tasks, write code, produce evidence |
| **Failure Condition** | Incomplete implementation, ignoring success criteria |

### QA - Quality Assurance

| Attribute | Value |
|-----------|-------|
| **Model** | Pro (2406) |
| **Template** | `hc-execute/qa_phase.md` |
| **Responsibility** | Verify work, catch issues, validate evidence |
| **Failure Condition** | Passing broken code, missing obvious issues |

### VA - Validator

| Attribute | Value |
|-----------|-------|
| **Model** | Flash (2405) |
| **Template** | `think-tank/validator_*.md`, `fact_validator.md` |
| **Responsibility** | Check alignment with NORTHSTAR, verify facts |
| **Failure Condition** | Missing NORTHSTAR violations, false positives |

---

## Gauntlet Roles (ADR-002)

Special roles for adversarial plan refinement:

### Writer (Principled Architect)

| Attribute | Value |
|-----------|-------|
| **Model** | Opus (2408) |
| **Template** | `think-tank/gauntlet_writer.md` |
| **Responsibility** | Own artifact, defend with evidence, integrate valid critiques |
| **Failure Condition** | Accepting bad advice, rejecting without evidence, rubber-stamping |

### Critic (High-Stakes Auditor)

| Attribute | Value |
|-----------|-------|
| **Model** | Pro (2406) |
| **Template** | `think-tank/gauntlet_critic.md` |
| **Responsibility** | Simulate execution, find breaks, stress-test plans |
| **Failure Condition** | Nitpicking without substance, hypothetical concerns, over-engineering |

### Arbiter (Flash Adjudicator)

| Attribute | Value |
|-----------|-------|
| **Model** | Flash (2405) |
| **Template** | `think-tank/gauntlet_arbiter.md` |
| **Responsibility** | Rule on contested issues with evidence |
| **Failure Condition** | Ruling without evidence, not escalating ambiguity |

---

## Model Assignment Philosophy

| Model | Cost | Speed | Use For |
|-------|------|-------|---------|
| **Flash (2405)** | Low | Fast | Research, validation, workers, drafts |
| **Pro (2406)** | Medium | Medium | Reasoning, QA, critique, synthesis |
| **Opus (2408)** | High | Slow | Complex reasoning, ownership, final decisions |

**Rule:** Use cheapest model that can do the job. Escalate only when cheaper model fails.

---

## Template Mapping

| Role | Templates |
|------|-----------|
| RCH | `scout_facts.md`, `merge_facts.md`, `arbiter_conflict.md` |
| ARC | `generator_spec.md`, `generator_execution_plan.md`, `generator_phase_roadmap.md` |
| WR | `worker_task.md` |
| QA | `qa_phase.md`, `synthesizer_qa.md`, `sweeper.md` |
| VA | `validator.md`, `fact_validator.md`, `validator_*.md` |
| Writer | `gauntlet_writer.md` |
| Critic | `gauntlet_critic.md` |
| Arbiter | `gauntlet_arbiter.md` |

---

## Related

- **ADR-002:** Gauntlet Loop Integration
- **think-tank.md:** Council workflow with roles
- **hc-execute.md:** Execution workflow with roles
