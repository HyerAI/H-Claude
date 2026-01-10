# PM-View

MkDocs Material wiki viewer for PM folder observability.

## Structure

```
PM-View/
├── mkdocs.yml          # MkDocs config
├── .env                # Local host/port config
├── assets/
│   └── logo.png        # Project logo
├── stylesheets/
│   └── custom.css      # Brand colors
└── README.md           # This file
```

## Configuration

Host and port are configured via `.env` file:

```bash
PM_VIEW_HOST=127.0.0.1
PM_VIEW_PORT=8003
```

Modify port if running multiple H-Claude projects simultaneously.

## Usage

```bash
cd .claude/PM/PM-View
source .env
mkdocs serve --dev-addr ${PM_VIEW_HOST}:${PM_VIEW_PORT}
```

Open http://127.0.0.1:8003 (or your configured port)

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

6. Configure `.env` with desired host/port (change port if conflicts exist)

7. Run: `cd .claude/PM/PM-View && source .env && mkdocs serve --dev-addr ${PM_VIEW_HOST}:${PM_VIEW_PORT}`

## Customization

- **Host/Port**: Edit `.env`
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
