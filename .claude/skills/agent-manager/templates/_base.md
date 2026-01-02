---
name: {agent-name}
description: Invoke when {trigger} - {one-line purpose}
tools: Read, Glob, Grep{, additional tools}
model: flash|pro|opus
proxy: http://localhost:{port}
skills: {skill-1}, {skill-2}
alias: {optional - sim-* prefix for Genesis simulators}
phase: {optional - P0-P4 for Genesis agents}
gate: {optional - *_gate suffix}
patterns: {optional - CSV string, each must exist}
related_adr: {optional - array of ADR-XXXX format}
loop: {optional - P1|P2|P3|P4|INIT|SUPPORT}
---

# {Agent Display Name}

> **SSoT:** This agent's persona is defined here. Skills are loaded from `.claude/skills/`.

## Personality

- {Trait 1}: {Description}
- {Trait 2}: {Description}
- {Trait 3}: {Description}
- {Trait 4}: {Description}

## Philosophy

> "{Core principle quoted here}"

## Protocol

### Stage 0: Receive Context
{What the agent receives as input from caller}

### Stage 1: {First Action}
{Steps for first action}

### Stage 2: {Second Action}
{Steps for second action}

### Stage N: Deliver Output
{What the agent produces as output}

## Constraints

- CANNOT: {tool1} (enforced by loop permissions)
- CANNOT: {behavior1} (design choice)
- CANNOT: {behavior2} (design choice)

## State Transitions

| Input State | Output State | Condition |
|-------------|--------------|-----------|
| {FROM} | {TO} | {When/under what condition} |

## MCP Tools

### Context Tools
- `kap get-context` - Load current story/phase/tasks

### {Category} Tools
- `{tool-1}` - {Purpose and when to use}
- `{tool-2}` - {Purpose and when to use}

### {Another Category} Tools
- `{tool-3}` - {Purpose and when to use}

## Spawning Command

```bash
ANTHROPIC_API_BASE_URL=http://localhost:{port} claude --dangerously-skip-permissions -p "
{Agent Name} executing task

CONTEXT:
{Key context variable 1}: {example value}
{Key context variable 2}: {example value}

PROTOCOL:
{Stage breakdown for clarity}

CONSTRAINTS:
{List of what agent CANNOT do}

Working directory: {workspace path}
"
```

---

*{Agent Display Name} | {Loop} | Last Updated: {YYYY-MM-DD}*
