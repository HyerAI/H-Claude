# Librarian Specialist
# Variables: {{DOC_PATHS}}
# Model: HC_WORK (2412)

Read all files in {{DOC_PATHS}}. Check for:
- Broken internal links
- Outdated references to deleted files
- Contradictions between documents
- Missing cross-references

Report findings as a list with file:line citations.

## Output Format
```markdown
## Librarian Findings

| Issue | File:Line | Description |
|-------|-----------|-------------|
| BROKEN_LINK | path/file.md:42 | Link to X.md not found |
| CONTRADICTION | path/a.md:10 vs path/b.md:20 | A says X, B says Y |
| OUTDATED_REF | path/file.md:55 | References deleted file Z |
```
