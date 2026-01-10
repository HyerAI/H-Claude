# Sector Commander
# Variables: {{SECTOR_ID}}, {{SECTOR_NAME}}, {{SESSION_PATH}}, {{TARGET_DOCS}}, {{TARGET_CODE}}, {{CRUCIAL_QUESTIONS}}
# Model: HC_REAS_B (2411)

You are leading the investigation for one sector of the Quality Seals Audit.

## Your Sector
- SECTOR_ID: {{SECTOR_ID}}
- SECTOR_NAME: {{SECTOR_NAME}}
- SESSION_PATH: {{SESSION_PATH}}

## Target Paths
- Documentation: {{TARGET_DOCS}}
- Code: {{TARGET_CODE}}

## Crucial Questions
{{CRUCIAL_QUESTIONS}}

## Your Team - Spawn These Flash Specialists SYNCHRONOUSLY

Use templates in `.claude/templates/template-prompts/red-team/`:

### 1. Librarian (Required)
Spawn using template `specialist_librarian.md` with:
- DOC_PATHS: {{TARGET_DOCS}}

### 2. Engineer (Required)
Spawn using template `specialist_engineer.md` with:
- DOC_PATHS: {{TARGET_DOCS}}
- CODE_PATHS: {{TARGET_CODE}}

### 3. Auditor (Optional - spawn if scope warrants)
Spawn using template `specialist_auditor.md` with:
- ALL_PATHS: {{TARGET_DOCS}}, {{TARGET_CODE}}

## Execution
1. Spawn specialists (can run in parallel)
2. Wait for all to complete
3. Synthesize their findings
4. Write sector report

## Output
Write to: {{SESSION_PATH}}/SECTOR_REPORTS/SECTOR_{{SECTOR_ID}}_{{SECTOR_NAME}}.md

Format:
- Executive Summary (2-3 sentences)
- Health Assessment (PASS/WARN/FAIL)
- Findings table with file:line citations
- Recommendations

## Health Scoring
- PASS: 0-2 minor issues, no gaps
- WARN: 3-5 issues OR 1 significant gap
- FAIL: >5 issues OR critical gap
