# Generator: Execution Plan
# Variables: {{SESSION_PATH}}, {{DECIDED_PATH}}, {{CONFIDENCE}}, {{PLAN_LEVEL}}
# Model: Pro (2406)

# Execution Plan Generator

## Your Mission
Create an implementation plan based on the decided path.

## Context Files (read in order)
1. {{SESSION_PATH}}/00_BRIEFING.md - Original problem and constraints
2. {{SESSION_PATH}}/04_DECISION_MAP.md - The decision made
3. {{SESSION_PATH}}/02_KNOWLEDGE_BASE/BRIEFING_PACK.md - Research findings

## Decision Made
Path: {{DECIDED_PATH}}
Confidence: {{CONFIDENCE}}

## Plan Level
{{PLAN_LEVEL}}  # FULL or OUTLINE

## Your Output
Write to: {{SESSION_PATH}}/execution-plan.yaml

Key requirements:
1. Break into logical phases (Foundation → Core → Integration → Polish)
2. Each task has clear success criteria
3. Dependencies are explicit
4. Files to modify are listed
5. Set status: draft

If OUTLINE: Create phases with placeholder tasks (can be detailed later)
If FULL: Create complete task breakdown
