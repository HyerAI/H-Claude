# Task Worker
# Variables: {{SESSION_PATH}}, {{PHASE_NUM}}, {{TASK_ID}}, {{TASK_DESCRIPTION}}, {{SUCCESS_CRITERIA}}, {{FILES}}, {{RELEVANT_INTERFACES}}
# Model: Flash (2405)

# Task Worker

## Your Task
Task ID: {{TASK_ID}}
Description: {{TASK_DESCRIPTION}}
Success Criteria: {{SUCCESS_CRITERIA}}
Files to modify: {{FILES}}

## Interfaces You Must Follow
{{RELEVANT_INTERFACES}}

## Your Output
1. Execute the task completely
2. Write evidence to: {{SESSION_PATH}}/PHASE_{{PHASE_NUM}}/WORKER_OUTPUTS/TASK_{{TASK_ID}}_EVIDENCE.md

## Evidence Format
```markdown
# Task {{TASK_ID}} Evidence

## Task: {{TASK_DESCRIPTION}}

## Changes Made
- [File]: [What changed]

## Verification
- [How to verify this works]

## Status: COMPLETE | PARTIAL | BLOCKED
```

Be thorough. Your work will be verified by QA.
