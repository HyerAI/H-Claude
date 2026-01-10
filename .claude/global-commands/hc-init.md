# /hc-init - Initialize H-Claude Project

Initialize a new project with the H-Claude framework.

---

## Agent Todo List

**Use TodoWrite immediately with these items:**

```
1. Confirm target folder with user
2. Copy template structure to target
3. Initialize example files
4. Create CLAUDE.md and .gitignore
5. Discovery: Ask about project identity
6. Discovery: Ask about purpose and users
7. Discovery: Ask about vision and goals
8. Discovery: Ask about constraints and non-goals
9. Draft NORTHSTAR.md from answers
10. Update CLAUDE.md with project name
11. Update context.yaml with project info
12. Suggest next steps (/think-tank --roadmap)
```

Mark each todo as you complete it. Update docs as user provides information.

---

## Configuration

```yaml
H_CLAUDE_TEMPLATE: ~/.claude/H-Claude
```

**Dev override:** If `$HC_TEMPLATE` env var is set, use that instead.

---

## Workflow

### Phase 1: Setup

1. **Confirm target folder:**
   - If user provided a path as argument, use it
   - Otherwise, use current working directory
   - Confirm with user before proceeding

2. **Check prerequisites:**
   - Target folder exists (or create it)
   - Target folder is a git repo (or offer to `git init`)
   - No existing `.claude/` folder (or warn about overwrite)

3. **Copy template structure:**
   ```bash
   TEMPLATE="${HC_TEMPLATE:-$HOME/.claude/H-Claude}"
   TARGET="<user-specified-path>"

   # Create base .claude folder
   mkdir -p "$TARGET/.claude"

   # Core folders
   cp -r "$TEMPLATE/.claude/commands/" "$TARGET/.claude/commands/"
   cp -r "$TEMPLATE/.claude/agents/" "$TARGET/.claude/agents/"
   cp -r "$TEMPLATE/.claude/templates/" "$TARGET/.claude/templates/"
   cp -r "$TEMPLATE/.claude/docs/" "$TARGET/.claude/docs/"
   cp -r "$TEMPLATE/.claude/examples/" "$TARGET/.claude/examples/"
   cp -r "$TEMPLATE/.claude/skills/" "$TARGET/.claude/skills/"
   cp -r "$TEMPLATE/.claude/scripts/" "$TARGET/.claude/scripts/"

   # Hooks - copy as DISABLED (require manual enable)
   # H-Claude hooks check for proxies which users may not have
   mkdir -p "$TARGET/.claude/hooks/"
   cp "$TEMPLATE/.claude/hooks/README.md" "$TARGET/.claude/hooks/"
   # Copy hooks with .disabled suffix - user enables manually
   for hook in "$TEMPLATE/.claude/hooks/"*.sh; do
     [ -f "$hook" ] && cp "$hook" "$TARGET/.claude/hooks/$(basename "$hook").disabled"
   done

   # PM structure (empty, ready for use)
   mkdir -p "$TARGET/.claude/PM/"{SSoT/ADRs,GIT,HC-LOG,TEMP,think-tank,hc-execute,hc-glass,red-team}

   # PM infrastructure files
   cp "$TEMPLATE/.claude/PM/index.md" "$TARGET/.claude/PM/"
   cp "$TEMPLATE/.claude/PM/README.md" "$TARGET/.claude/PM/" 2>/dev/null || true
   cp "$TEMPLATE/.claude/PM/SSoT/AGENT_ROLES.md" "$TARGET/.claude/PM/SSoT/"
   cp "$TEMPLATE/.claude/PM/SSoT/NORTHSTAR.md" "$TARGET/.claude/PM/SSoT/"
   cp "$TEMPLATE/.claude/PM/SSoT/ROADMAP.yaml" "$TARGET/.claude/PM/SSoT/"
   cp "$TEMPLATE/.claude/PM/GIT/REFERENCE_GUIDE.md" "$TARGET/.claude/PM/GIT/"

   # Index files for command folders
   cp "$TEMPLATE/.claude/PM/think-tank/index.md" "$TARGET/.claude/PM/think-tank/"
   cp "$TEMPLATE/.claude/PM/hc-execute/index.md" "$TARGET/.claude/PM/hc-execute/"
   cp "$TEMPLATE/.claude/PM/hc-glass/index.md" "$TARGET/.claude/PM/hc-glass/"
   cp "$TEMPLATE/.claude/PM/red-team/index.md" "$TARGET/.claude/PM/red-team/"
   ```

4. **Initialize from examples:**
   ```bash
   # Copy and rename example files (remove .example suffix)
   cp "$TEMPLATE/.claude/context.yaml.example" "$TARGET/.claude/context.yaml"
   cp "$TEMPLATE/.claude/PM/CHANGELOG.md.example" "$TARGET/.claude/PM/CHANGELOG.md"
   cp "$TEMPLATE/.claude/PM/BACKLOG.yaml.example" "$TARGET/.claude/PM/BACKLOG.yaml"
   cp "$TEMPLATE/.claude/PM/GIT/GIT_PLAN.md.example" "$TARGET/.claude/PM/GIT/GIT_PLAN.md"
   cp "$TEMPLATE/.claude/PM/GIT/PROTOCOLS.md.example" "$TARGET/.claude/PM/GIT/PROTOCOLS.md"

   # Initialize HC-LOG files from examples
   cp "$TEMPLATE/.claude/PM/HC-LOG/HC-FAILURES.md.example" "$TARGET/.claude/PM/HC-LOG/HC-FAILURES.md"
   cp "$TEMPLATE/.claude/PM/HC-LOG/USER-PREFERENCES.md.example" "$TARGET/.claude/PM/HC-LOG/USER-PREFERENCES.md"
   ```

5. **Create root files (DO NOT copy H-Claude's root files):**

   **CLAUDE.md** - Copy from template and customize:
   ```bash
   cp "$TEMPLATE/.claude/examples/CLAUDE.md.example" "$TARGET/CLAUDE.md"
   # Then update [PROJECT_NAME] placeholder during discovery phase
   ```

   **.gitignore** - Append H-Claude patterns if .gitignore exists, else create:
   ```bash
   cat >> "$TARGET/.gitignore" << 'EOF'
   # H-Claude
   .claude/context.yaml
   .claude/PM/CHANGELOG.md
   .claude/PM/BACKLOG.yaml
   .claude/PM/SESSION_STATUS.md
   .claude/PM/TEMP/
   .claude/PM/think-tank/*/
   .claude/PM/hc-execute/*/
   .claude/PM/hc-glass/*/
   .claude/PM/red-team/*/
   .claude/PM/SSoT/ADRs/ADR-*.md
   .claude/PM/HC-LOG/*.md
   .claude/PM/GIT/GIT_PLAN.md
   .claude/PM/GIT/PROTOCOLS.md
   EOF
   ```

6. **Report setup complete** with folder structure summary.
   - Note: Hooks are installed as `.disabled` - rename to enable after setting up proxies
   - Note: Edit `CLAUDE.md` to add project-specific instructions

---

### Phase 2: NORTHSTAR Discovery

After setup, guide the user through creating their project's NORTHSTAR.

**Use AskUserQuestion tool for these:**

1. **Project Identity:**
   - "What is this project called?"
   - "In one sentence, what does it do?"

2. **Purpose:**
   - "What problem does this solve?"
   - "Who is this for?" (target users/audience)

3. **Vision:**
   - "What will success look like?"
   - "What value will it provide when complete?"

4. **Goals (pick 3-5):**
   - "What are the key goals or features?"
   - Probe for specifics, avoid vague goals

5. **Constraints:**
   - "Any technical constraints?" (language, framework, platform)
   - "Any scope constraints?" (what's explicitly out of scope)

6. **Non-Goals:**
   - "What will this project NOT do?"
   - "What should we explicitly defer?"

---

### Phase 3: Draft NORTHSTAR

Based on answers, write `$TARGET/.claude/PM/SSoT/NORTHSTAR.md`:

```markdown
# Project NORTHSTAR: [Project Name]

**The guiding document for all agents working on this project.**

---

## Purpose

[One paragraph: what it does and why it exists]

---

## Vision

[One paragraph: what success looks like]

---

## Target Users

[Who this is for]

---

## Goals

1. **[Goal 1]** - [Description]
2. **[Goal 2]** - [Description]
3. **[Goal 3]** - [Description]

---

## Constraints

1. **[Constraint]** - [Reason]
2. ...

---

## Non-Goals

- [What we explicitly will NOT do]
- [Features we are deferring]

---

## Quality Standards

| Aspect | Standard |
|--------|----------|
| Code | Clean, tested, documented |
| Docs | Clear, concise, current |
```

---

### Phase 4: Finalize & Update SSoT

**Update docs as user shares information.** Don't wait until the end.

1. **Show draft to user** - Ask for feedback/edits
2. **Iterate** if needed
3. **Write final NORTHSTAR.md** - The project's guiding document
4. **Update CLAUDE.md:**
   - Replace `[PROJECT_NAME]` with actual project name
   - Add any project-specific instructions the user mentioned
   - Add technical constraints (language, framework, etc.)
5. **Update context.yaml:**
   ```yaml
   project:
     name: '[Project Name]'
     description: '[One-liner from discovery]'
     type: '[app/library/service/etc]'
   focus:
     current_objective: 'Project initialized - ready for roadmap'
   recent_actions:
     - '[Date]: Project initialized with /hc-init'
   ```
6. **Initialize ROADMAP.yaml** (if user provided enough info):
   - Add project name and description
   - Leave phases empty (for `/think-tank --roadmap`)
7. **Suggest next steps:**
   - "Run `/think-tank --roadmap` to create development phases"
   - "Or describe your first feature to start building"

**Key principle:** SSoT docs should reflect everything the user shared. Don't lose context.

---

## Usage

```bash
# Initialize current directory
/hc-init

# Initialize specific folder
/hc-init ~/projects/my-new-app

# Initialize and create folder
/hc-init ~/projects/new-project
```
