# PM-View

MkDocs Material wiki viewer for PM folder observability.

## Structure

```
PM-View/
├── mkdocs.yml          # MkDocs config
├── assets/
│   └── logo.png        # Project logo
├── stylesheets/
│   └── custom.css      # Brand colors
└── README.md           # This file
```

## Usage

```bash
cd .claude/PM/PM-View
mkdocs serve --dev-addr 127.0.0.1:8003
```

Open http://127.0.0.1:8003

## Adding to Another Project

1. Copy `PM-View/` folder to `other-project/.claude/PM/PM-View/`

2. Install dependencies (one-time):
   ```bash
   pipx install mkdocs-material --include-deps
   pipx inject mkdocs-material mkdocs-awesome-pages-plugin
   ```

3. Create `.pages` files in PM subfolders for navigation:
   ```yaml
   # .claude/PM/.pages
   nav:
     - index.md
     - dashboard.md
     - SSoT
     - ...
   ```

4. Create `index.md` and `dashboard.md` in PM folder

5. Replace `assets/logo.png` with your project logo

6. Run: `cd .claude/PM/PM-View && mkdocs serve`

## Customization

- **Colors**: Edit `stylesheets/custom.css`
- **Logo**: Replace `assets/logo.png`
- **Site name**: Edit `site_name` in `mkdocs.yml`
- **Navigation**: Create `.pages` files in folders

## Brand Colors

```css
--md-primary-fg-color: #4a90a4;   /* Teal blue */
--md-accent-fg-color: #d4a04a;    /* Gold/amber */
--md-default-bg-color: #0d1421;   /* Dark navy */
```
