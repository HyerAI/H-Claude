# Flowchart Templates

> **Purpose:** Reusable patterns, snippets, and starting points for common chart types.

---

## Template Structure

```
templates/
├── README.md              # This file
├── _base.html             # Base HTML skeleton for any chart
├── layouts/               # Common layout configurations
│   ├── linear-flow.js     # A → B → C → D
│   ├── hub-spoke.js       # Central node with radiating connections
│   └── grid-matrix.js     # Rows × Columns organization
├── snippets/              # Reusable code fragments
│   ├── edge-routing.js    # Border intersection + bezier curves
│   ├── node-styles.css    # Standard node styling
│   └── interactivity.js   # Hover, select, filter behaviors
└── presets/               # Complete chart configurations
    ├── workflow-4loop.json    # P1-P4 quad-loop layout
    └── agent-network.json     # Agent relationship map
```

---

## Usage

Templates are loaded and adapted at the start of each chart task:

1. **Identify chart type** from user request
2. **Load matching preset** or compose from layout + snippets
3. **Apply user-specific modifications**
4. **Record adaptations** to learnings for future improvement

---

## Template Promotion

Patterns from `learnings/FLOWCHART_LEARNINGS.md` are promoted to templates when:

- **Recurrence ≥ 3**: Pattern appears in 3+ separate chart tasks
- **User explicit approval**: User says "save this as a template"
- **Quality threshold**: Pattern produces consistently good results

---

*Templates grow organically from actual usage patterns.*
