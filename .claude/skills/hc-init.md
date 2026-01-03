# /hc-init - H-Claude Project Initialization

Initialize an H-Claude workflow in the current project directory.

---

## What This Skill Does

Copies H-Claude workflow files from the global cache (`~/.claude/h-claude-template/`) to your project's `.claude/` folder, setting up:

- **Commands**: think-tank, hc-plan-execute, hc-glass, red-team
- **Agents**: git-engineer, session-triage
- **Skills**: adr-writer, command-designer, commit-gate, update-context
- **Templates**: Prompt templates for all commands
- **PM Structure**: SSoT folder with NORTHSTAR.md, ROADMAP.yaml
- **Context**: Initial context.yaml

---

## Usage

```
/hc-init [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| (none) | Full initialization with all files |
| `--update` | Update workflow files to latest version |
| `--check` | Check what would be installed (dry run) |

---

## Execution Steps

When invoked, perform these steps:

### 1. Check Prerequisites

```bash
# Verify global install exists
if [ ! -d "$HOME/.claude/h-claude-template" ]; then
    echo "H-Claude not installed globally. Run:"
    echo "curl -fsSL https://raw.githubusercontent.com/HyerAI/H-Claude/main/install.sh | bash"
    exit 1
fi
```

### 2. Create Project Structure

```bash
# Create .claude folder structure
mkdir -p .claude/commands
mkdir -p .claude/agents
mkdir -p .claude/skills
mkdir -p .claude/templates
mkdir -p .claude/PM/SSoT/ADRs
mkdir -p .claude/PM/think-tank
mkdir -p .claude/PM/hc-plan-execute
mkdir -p .claude/PM/hc-glass
mkdir -p .claude/PM/red-team
mkdir -p .claude/PM/TEMP
mkdir -p .claude/PM/GIT
mkdir -p .claude/hooks
```

### 3. Copy Workflow Files

```bash
TEMPLATE_DIR="$HOME/.claude/h-claude-template"

# Commands
cp -r "$TEMPLATE_DIR/commands/"* .claude/commands/

# Agents
cp -r "$TEMPLATE_DIR/agents/"* .claude/agents/

# Skills
cp -r "$TEMPLATE_DIR/skills/"* .claude/skills/

# Templates
cp -r "$TEMPLATE_DIR/templates/"* .claude/templates/

# PM structure (SSoT files)
cp -r "$TEMPLATE_DIR/PM/SSoT/"* .claude/PM/SSoT/

# Context
cp "$TEMPLATE_DIR/context.yaml" .claude/context.yaml

# CLAUDE.md (if not exists)
if [ ! -f "CLAUDE.md" ]; then
    cp "$TEMPLATE_DIR/CLAUDE.md" ./CLAUDE.md
fi
```

### 4. Verify Installation

Run validation:

```bash
# List installed components
echo "Installed:"
echo "  Commands: $(ls .claude/commands/ | wc -l)"
echo "  Agents: $(ls .claude/agents/ | wc -l)"
echo "  Skills: $(ls .claude/skills/ | wc -l)"
```

### 5. Show Next Steps

After successful initialization:

```
H-Claude initialized successfully!

Files created:
  .claude/commands/     - Orchestration commands
  .claude/agents/       - Agent definitions
  .claude/skills/       - Reusable skills
  .claude/templates/    - Prompt templates
  .claude/PM/           - Project management state
  .claude/context.yaml  - Session context
  CLAUDE.md             - Project instructions

Next steps:
  1. Edit CLAUDE.md with your project name
  2. Fill out .claude/PM/SSoT/NORTHSTAR.md with your goals
  3. Run: /think-tank --roadmap to create development phases
```

---

## Update Mode

When `--update` is passed:

1. Backup existing commands, agents, skills, templates to `.claude/backup/`
2. Copy fresh files from template cache
3. Preserve PM folder (state files)
4. Preserve context.yaml (session state)
5. Show diff summary

---

## Notes

- Does NOT overwrite existing PM state files
- Does NOT overwrite existing context.yaml (unless empty)
- CLAUDE.md only created if missing
- Run `--update` to get latest workflow improvements

---

## Proxy Check

After initialization, remind user:

```
Ensure proxies are running:
  ~/.claude/bin/start-proxies.sh

Check health:
  curl http://localhost:2405/health
  curl http://localhost:2406/health
  curl http://localhost:2408/health
```
