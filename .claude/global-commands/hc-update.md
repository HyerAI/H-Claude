# /hc-update - Update H-Claude Framework in Project

Update framework files from the H-Claude template while preserving project-specific files.

---

## What Gets Updated (Framework Files)

These are **replaced** from the template:

| Folder | Contents |
|--------|----------|
| `.claude/commands/` | think-tank, hc-execute, hc-glass, red-team |
| `.claude/agents/` | git-engineer, hc-scout |
| `.claude/templates/` | Prompt templates |
| `.claude/lib/` | Shared libraries (agent-spawn.sh) |
| `.claude/scripts/` | Utility scripts |
| `.claude/skills/` | Reusable skills |
| `.claude/docs/` | Documentation |
| `.claude/examples/` | Example files |

---

## What Gets Preserved (Project Files)

These are **never touched**:

| File/Folder | Reason |
|-------------|--------|
| `.claude/PM/SSoT/NORTHSTAR.md` | Project vision |
| `.claude/PM/SSoT/ROADMAP.yaml` | Project roadmap |
| `.claude/PM/SSoT/ADRs/` | Project decisions |
| `.claude/PM/CHANGELOG.md` | Project history |
| `.claude/PM/BACKLOG.yaml` | Project backlog |
| `.claude/PM/HC-LOG/` | Project learnings |
| `.claude/PM/think-tank/*/` | Session artifacts |
| `.claude/PM/hc-execute/*/` | Session artifacts |
| `.claude/context.yaml` | Session state |
| `CLAUDE.md` | Project instructions |

---

## Workflow

### Step 1: Pre-flight Checks

```bash
TEMPLATE="${HC_TEMPLATE:-$HOME/.claude/H-Claude}"
PROJECT="$(pwd)"

# Verify template exists
if [ ! -d "$TEMPLATE/.claude" ]; then
  echo "ERROR: Template not found at $TEMPLATE"
  echo "Run: git clone https://github.com/HyerAI/H-Claude.git ~/.claude/H-Claude"
  exit 1
fi

# Verify this is an H-Claude project
if [ ! -d "$PROJECT/.claude/PM" ]; then
  echo "ERROR: Not an H-Claude project (no .claude/PM folder)"
  echo "Run /hc-init first to initialize this project"
  exit 1
fi
```

### Step 2: Backup Current State

```bash
BACKUP_DIR="$PROJECT/.claude/PM/TEMP/update-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup framework folders before update
for folder in commands agents templates lib scripts skills docs examples; do
  if [ -d "$PROJECT/.claude/$folder" ]; then
    cp -r "$PROJECT/.claude/$folder" "$BACKUP_DIR/"
  fi
done

echo "Backup created: $BACKUP_DIR"
```

### Step 3: Update Framework Files

```bash
# Remove old framework folders and copy fresh from template
for folder in commands agents templates lib scripts skills docs examples; do
  rm -rf "$PROJECT/.claude/$folder"
  if [ -d "$TEMPLATE/.claude/$folder" ]; then
    cp -r "$TEMPLATE/.claude/$folder" "$PROJECT/.claude/$folder"
    echo "Updated: .claude/$folder"
  fi
done

# Update hooks (as .disabled if new)
mkdir -p "$PROJECT/.claude/hooks"
for hook in "$TEMPLATE/.claude/hooks/"*.sh; do
  if [ -f "$hook" ]; then
    hookname=$(basename "$hook")
    if [ -f "$PROJECT/.claude/hooks/$hookname" ]; then
      # Hook already enabled, update it
      cp "$hook" "$PROJECT/.claude/hooks/$hookname"
      echo "Updated: .claude/hooks/$hookname"
    elif [ ! -f "$PROJECT/.claude/hooks/${hookname}.disabled" ]; then
      # New hook, copy as disabled
      cp "$hook" "$PROJECT/.claude/hooks/${hookname}.disabled"
      echo "Added (disabled): .claude/hooks/${hookname}.disabled"
    fi
  fi
done
cp "$TEMPLATE/.claude/hooks/README.md" "$PROJECT/.claude/hooks/" 2>/dev/null || true
```

### Step 4: Update PM Infrastructure (Non-SSoT)

```bash
# Update PM index files (not user content)
cp "$TEMPLATE/.claude/PM/index.md" "$PROJECT/.claude/PM/" 2>/dev/null || true
cp "$TEMPLATE/.claude/PM/SSoT/AGENT_ROLES.md" "$PROJECT/.claude/PM/SSoT/" 2>/dev/null || true

# Update command folder index files
for folder in think-tank hc-execute hc-glass red-team; do
  if [ -f "$TEMPLATE/.claude/PM/$folder/index.md" ]; then
    cp "$TEMPLATE/.claude/PM/$folder/index.md" "$PROJECT/.claude/PM/$folder/"
  fi
done

# Ensure .gitkeep files exist
for folder in think-tank hc-execute hc-glass red-team SSoT/ADRs TEMP; do
  touch "$PROJECT/.claude/PM/$folder/.gitkeep" 2>/dev/null || true
done
```

### Step 5: Report Changes

```bash
echo ""
echo "=== Update Complete ==="
echo ""
echo "Updated:"
echo "  - commands/, agents/, templates/, lib/, scripts/, skills/, docs/, examples/"
echo "  - PM infrastructure (index files, AGENT_ROLES.md)"
echo ""
echo "Preserved:"
echo "  - NORTHSTAR.md, ROADMAP.yaml, ADRs/"
echo "  - CHANGELOG.md, BACKLOG.yaml, context.yaml"
echo "  - All session artifacts (think-tank/*, hc-execute/*)"
echo "  - CLAUDE.md (project instructions)"
echo ""
echo "Backup at: $BACKUP_DIR"
echo ""
echo "If something broke, restore from backup:"
echo "  cp -r $BACKUP_DIR/* .claude/"
```

---

## Usage

```bash
# Update current project
/hc-update

# Verify before running (dry-run not implemented yet)
# Just review the backup after
```

---

## After Update

1. **Review CHANGELOG** - Check template's `.claude/docs/` for what's new
2. **Test commands** - Run `/think-tank --help` or similar to verify
3. **Check hooks** - Enable new hooks if needed (remove `.disabled` suffix)
4. **Delete backup** - Once verified: `rm -rf .claude/PM/TEMP/update-backup-*`

---

## Troubleshooting

### Command not found after update

```bash
# Verify commands copied
ls .claude/commands/

# If empty, manually copy
cp -r ~/.claude/H-Claude/.claude/commands/ .claude/commands/
```

### Restore from backup

```bash
# Find latest backup
ls .claude/PM/TEMP/update-backup-*

# Restore specific folder
cp -r .claude/PM/TEMP/update-backup-XXXXX/commands/ .claude/commands/
```
