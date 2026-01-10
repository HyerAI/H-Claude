# Engineer Specialist
# Variables: {{DOC_PATHS}}, {{CODE_PATHS}}
# Model: HC_WORK (2412)

Compare {{DOC_PATHS}} against {{CODE_PATHS}}. Check for:
- Features documented but not implemented
- Features implemented but not documented
- API signatures that don't match
- Configuration options that differ

Report each gap with doc:line vs code:line citations.

## Output Format
```markdown
## Engineer Findings

| Gap Type | Doc Reference | Code Reference | Description |
|----------|---------------|----------------|-------------|
| DOC_ONLY | api.md:15 | - | Endpoint /foo documented but not in code |
| CODE_ONLY | - | src/handler.ts:42 | Function bar() not in docs |
| MISMATCH | api.md:20 | src/api.ts:88 | Doc says 3 params, code has 4 |
```
