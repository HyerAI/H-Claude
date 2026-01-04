# Command Index Page Template

Use this template when creating index.md for command output folders (think-tank, hc-execute, hc-glass).

---

## Template Structure

```markdown
# [Command Name]

**[One-line description of what the command does]**

---

## Recent [Sessions/Executions/Audits]

| Date | [Item] | Status |
|------|--------|--------|
| YYYY-MM-DD | [Link](folder/index.md) | Complete |

---

## How `/[command]` Works

```mermaid
flowchart TB
    [Flowchart showing command workflow]
```

---

## [Phases/Roles/Sectors] Table

| [Column1] | [Column2] | [Column3] |
|-----------|-----------|-----------|
| **Item** | Role | Description |

---

!!! tip "Running [Command]"
    Run `/[command]` to [action].
```

---

## Session/Execution Subfolder Template

```markdown
# [Session Name]

**Date:** YYYY-MM-DD | **Status:** Complete

---

## Documents

- [Document 1](file1.md) - Description
- [Document 2](file2.md) - Description

---

**Outcome:** [Summary of what was achieved]
```

---

## .pages File Template

```yaml
title: [Display Name]
nav:
  - index.md
  - session_folder_1
  - session_folder_2
```

---

## Checklist

- [ ] Main index.md with recent items table
- [ ] Flowchart explaining workflow
- [ ] Phases/roles table
- [ ] Tip box with command usage
- [ ] .pages file with nav order (newest first)
- [ ] Each subfolder has .pages + index.md
