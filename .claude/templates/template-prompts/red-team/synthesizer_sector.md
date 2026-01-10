# Sector Synthesis Agent
# Variables: {{SESSION_PATH}}, {{SECTORS_RUN}}
# Model: HC_REAS_B (2411)

Analyze all sector reports to identify cross-cutting patterns and prioritize findings.

## Session Parameters
- SESSION_PATH: {{SESSION_PATH}}
- SECTORS_RUN: {{SECTORS_RUN}}

## Your Inputs
Read all sector reports: {{SESSION_PATH}}/SECTOR_REPORTS/SECTOR_*.md

## Your Analysis

### 1. Pattern Detection
- What issues appear in multiple sectors?
- Are there systemic problems (not just isolated issues)?
- What root causes explain multiple symptoms?

### 2. Priority Assessment
- Critical: blocking functionality
- Important: affect quality
- Minor: cosmetic or low-impact

### 3. Kill List Consolidation
- Merge zombie lists from all sectors
- Remove duplicates
- Verify no false positives (file used by sector not yet analyzed)

### 4. Fix List Consolidation
- Merge all implementation gaps
- Identify dependencies (fix A before B)
- Estimate effort (quick/medium/major)

## Output
Write to: {{SESSION_PATH}}/ANALYSIS/SECTOR_SYNTHESIS.md

Include:
- Sector Health Overview table
- Systemic Patterns Detected
- Consolidated Kill List
- Consolidated Fix List (Critical/Important/Minor)
- Health Score (0-100%)
