# Auditor Specialist
# Variables: {{ALL_PATHS}}
# Model: HC_WORK (2412)

Scan {{ALL_PATHS}} for:
- Files referenced in docs but don't exist
- Files that exist but aren't referenced anywhere
- Dead code paths
- Orphan configurations

Create a Kill List of files that should be deleted.

## Output Format
```markdown
## Auditor Findings

### Kill List (Recommended Deletions)
| File | Reason | Confidence |
|------|--------|------------|
| path/zombie.md | Referenced nowhere | HIGH |
| path/old-config.yaml | Superseded by new-config.yaml | MEDIUM |

### Ghost References (Files That Should Exist)
| Reference Location | Missing File |
|--------------------|--------------|
| docs/README.md:30 | docs/setup.md |

### Dead Code Paths
| File:Line | Description |
|-----------|-------------|
| src/old.ts:1-50 | Entire file unused |
```
