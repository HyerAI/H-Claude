---
name: flowchart-designer
description: Create interactive SVG flowcharts with proper edge routing and layout
category: visualization
used_by: [lead-architect, product-owner]
---

# Flowchart Designer Skill

## Purpose

Generate production-quality interactive HTML/SVG flowcharts with proper node spacing, edge routing, and label placement. Based on best practices from D3.js, yWorks, and React Flow.

---

## Best Practices Summary

### 1. Layout Configuration

Use a centralized LAYOUT object for consistent spacing:

```javascript
const LAYOUT = {
    // Columns (horizontal spacing)
    col1: 60,      // Minimum 140px between columns for 140px nodes
    col2: 280,     // nodeWidth + 50px gap
    col3: 500,

    // Rows (vertical spacing)
    row1: 60,      // Minimum 120px between rows for 60px nodes
    row2: 180,     // nodeHeight + 60px gap
    row3: 300,
};
```

**Rules:**
- Horizontal gap: `nodeWidth + 50px` minimum
- Vertical gap: `nodeHeight + 60px` minimum
- Group related nodes in columns/rows

### 2. Arrow Markers (SVG)

```javascript
// Arrow marker that stops at node border
marker.setAttribute('viewBox', '0 0 10 10');
marker.setAttribute('refX', '10');       // Tip at line end
marker.setAttribute('refY', '5');        // Centered
marker.setAttribute('markerWidth', '5'); // Small arrows
marker.setAttribute('markerHeight', '5');
marker.setAttribute('orient', 'auto-start-reverse');
```

**Key Settings:**
- `refX=10`: Places arrow tip at path endpoint
- `markerWidth/Height=5`: Keep arrows small relative to stroke
- `orient=auto-start-reverse`: Auto-rotate with path direction

### 3. Border Intersection Calculation

Edges should connect to node borders, not centers:

```javascript
function getBorderPoint(cx, cy, w, h, targetX, targetY, isCircle, padding = 8) {
    const dx = targetX - cx;
    const dy = targetY - cy;

    if (isCircle) {
        const angle = Math.atan2(dy, dx);
        const r = (w / 2) + padding;
        return {
            x: cx + r * Math.cos(angle),
            y: cy + r * Math.sin(angle)
        };
    }

    // Rectangle intersection using ray-casting
    const halfW = (w / 2) + padding;
    const halfH = (h / 2) + padding;
    const angle = Math.atan2(dy, dx);
    const cornerAngle = Math.atan2(halfH, halfW);

    let x, y;
    if (Math.abs(angle) < cornerAngle || Math.abs(angle) > Math.PI - cornerAngle) {
        // Exit through left/right edge
        x = dx > 0 ? cx + halfW : cx - halfW;
        y = cy + halfW * Math.tan(angle) * (dx > 0 ? 1 : -1);
    } else {
        // Exit through top/bottom edge
        y = dy > 0 ? cy + halfH : cy - halfH;
        x = cx + halfH / Math.tan(angle) * (dy > 0 ? 1 : -1);
    }
    return { x, y };
}
```

**Padding:** Add 4-8px padding to keep arrows from touching node borders.

### 4. Label Positioning

Labels should be offset perpendicular to the edge to avoid overlap:

```javascript
function getPerpendicularOffset(x1, y1, x2, y2, distance) {
    const dx = x2 - x1;
    const dy = y2 - y1;
    const len = Math.sqrt(dx * dx + dy * dy);
    if (len === 0) return { x: 0, y: 0 };
    return {
        x: (-dy / len) * distance,  // Rotate 90 degrees
        y: (dx / len) * distance
    };
}

// Place label at bezier midpoint with offset
const t = 0.5;
const labelX = (1-t)*(1-t)*x1 + 2*(1-t)*t*ctrlX + t*t*x2;
const labelY = (1-t)*(1-t)*y1 + 2*(1-t)*t*ctrlY + t*t*y2;
const offset = getPerpendicularOffset(x1, y1, x2, y2, 12);
const finalX = labelX + offset.x;
const finalY = labelY + offset.y;
```

**Best Practices:**
- Offset 10-15px perpendicular to edge
- Use background rectangles for readability
- Set `text-anchor: middle` and `dominant-baseline: middle`

### 5. Curve Control

Gentle curves prevent overlapping and improve readability:

```javascript
// Calculate curve control point
const dist = Math.sqrt(dx * dx + dy * dy);
const curveOffset = Math.min(dist * 0.15, 40); // Cap at 40px

// Horizontal edge: curve up/down
// Vertical edge: curve left/right
if (Math.abs(dx) > Math.abs(dy)) {
    ctrlX = midX;
    ctrlY = midY - curveOffset;
} else {
    ctrlX = midX + curveOffset;
    ctrlY = midY;
}

// Quadratic bezier
path.setAttribute('d', `M ${x1} ${y1} Q ${ctrlX} ${ctrlY} ${x2} ${y2}`);
```

---

## Node Definition Structure

```javascript
const nodes = {
    nodeId: {
        id: 'nodeId',
        label: 'Display Name',
        sublabel: 'Role/Type',
        category: 'category-name',  // For color coding

        // Position (use LAYOUT constants)
        x: LAYOUT.col1,
        y: LAYOUT.row1,
        width: 140,
        height: 60,

        // Shape
        isCircle: false,     // true for circular nodes
        isHub: false,        // true for larger hub nodes

        // Metadata
        description: 'What this node does',
        metadata: {},        // Additional data
    }
};
```

## Edge Definition Structure

```javascript
const edges = [
    {
        from: 'sourceNodeId',
        to: 'targetNodeId',
        label: 'EDGE_LABEL',      // Optional
        type: 'category-name',    // For color/style
    }
];
```

---

## Color Schemes

Use consistent colors for node categories:

```javascript
const colors = {
    'primary':   '#3498db',   // Blue
    'secondary': '#27ae60',   // Green
    'tertiary':  '#e67e22',   // Orange
    'quaternary':'#9b59b6',   // Purple
    'neutral':   '#636e72',   // Gray
    'alert':     '#e74c3c',   // Red
    'highlight': '#f39c12',   // Yellow/Gold
};
```

Edge colors should match their source/target category.

---

## Interactive Features

### Node Selection

```javascript
function selectNode(nodeId) {
    // Remove previous selection
    document.querySelectorAll('.node.selected')
        .forEach(n => n.classList.remove('selected'));

    // Add selection
    document.getElementById(`node-${nodeId}`)
        .classList.add('selected');

    updateDetailPanel(nodeId);
}
```

### Pan and Zoom

```javascript
let zoom = 1;
let panX = 0, panY = 0;

canvas.addEventListener('wheel', (e) => {
    e.preventDefault();
    zoom *= e.deltaY < 0 ? 1.1 : 0.9;
    zoom = Math.max(0.5, Math.min(3, zoom));
    updateTransform();
});

function updateTransform() {
    canvas.style.transform = `scale(${zoom}) translate(${panX}px, ${panY}px)`;
}
```

### Filtering/Highlighting

```javascript
function highlightCategory(category) {
    Object.values(nodes).forEach(node => {
        const el = document.getElementById(`node-${node.id}`);
        el.style.opacity = (category === 'all' || node.category === category)
            ? '1' : '0.3';
    });
}
```

---

## HTML Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Flowchart Title</title>
    <style>
        body {
            background: #1a1a2e;
            font-family: system-ui;
        }
        .canvas {
            position: relative;
            width: 100%;
            height: 100vh;
        }
        .node {
            position: absolute;
            cursor: pointer;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: #fff;
            font-size: 12px;
        }
        .node:hover { transform: scale(1.05); }
        .node.selected { box-shadow: 0 0 0 3px #fff; }
        .edges-svg {
            position: absolute;
            width: 100%;
            height: 100%;
            pointer-events: none;
        }
        .edge {
            fill: none;
            stroke-width: 2;
            opacity: 0.7;
        }
        .edge-label {
            font-size: 10px;
            fill: #ccc;
        }
        .edge-label-bg {
            fill: rgba(0,0,0,0.85);
        }
    </style>
</head>
<body>
    <div class="canvas">
        <svg class="edges-svg"></svg>
        <!-- Nodes rendered by JS -->
    </div>
    <script>
        // Node/Edge definitions
        // Render functions
        // Event handlers
    </script>
</body>
</html>
```

---

## Advanced Features

### 6. Modal Drill-Down System

For complex flowcharts, implement modal overlays to show loop/group details:

```javascript
const drillDownData = {
    groupId: {
        title: 'Group Name',
        description: 'What this group does...',
        steps: [
            { step: 1, label: 'First step', icon: '📥' },
            { step: 2, label: 'Second step', icon: '⚙️', link: 'detail.html' }
        ],
        agents: ['agent1', 'agent2'],
        patterns: ['pattern-name'],
        entryCondition: 'When X happens',
        exitCondition: 'When Y is complete'
    }
};

function openDrillDown(groupId) {
    const data = drillDownData[groupId];
    document.getElementById('drillTitle').textContent = data.title;
    renderDrillSteps(data.steps);
    document.getElementById('drillModal').style.display = 'flex';
}
```

**Modal CSS:**
```css
.drill-modal {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.8);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 12px;
    width: 90%;
    max-width: 900px;
    max-height: 85vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}
```

### 7. Detail Panel Structure

Rich information panels for node selection:

```html
<div class="detail-panel">
    <h2>Node Name</h2>
    <span class="loop-badge badge-loop1">Loop 1</span>

    <div class="detail-section">
        <h3>Description</h3>
        <p>What this node does...</p>
    </div>

    <div class="detail-section">
        <h3>Capabilities</h3>
        <ul>
            <li class="li-can">Can do this</li>
            <li class="li-cannot">Cannot do that</li>
        </ul>
    </div>

    <div class="docs-section">
        <h3>Documentation</h3>
        <a href="doc.md">Related ADR</a>
    </div>
</div>
```

**Font Sizing (Accessibility):**
- Panel h2: 18px (titles)
- Badge text: 12px
- Section h3: 12px (uppercase)
- Descriptions: 14px
- List items: 13px
- Use 15% larger fonts in info panels than chart labels

### 8. Pattern Nodes

Non-agent workflow elements (queues, protocols):

```css
.pattern-node {
    width: 130px;
    height: 45px;
    border: 2px dashed rgba(255, 255, 255, 0.5);
    background: linear-gradient(135deg, rgba(100, 100, 120, 0.3) 0%, rgba(80, 80, 100, 0.3) 100%);
    border-radius: 12px;
    font-size: 10px;
    color: #fff;
}
```

**Pattern Examples:**
- Queue (intake/processing workflow)
- Holding Pattern (deferred work capture)
- Protocol Node (validation/decision gate)

### 9. Loop Color Palette (Customizable)

> *Customize loop/phase names for your project. Example below uses generic loop numbering.*

```javascript
const loopColors = {
    loop1: { bg: 'linear-gradient(135deg, #3498db 0%, #2980b9 100%)', border: '#74b9ff' },
    loop2: { bg: 'linear-gradient(135deg, #27ae60 0%, #219a52 100%)', border: '#55efc4' },
    loop3: { bg: 'linear-gradient(135deg, #e67e22 0%, #d35400 100%)', border: '#fab1a0' },
    loop4: { bg: 'linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%)', border: '#a29bfe' },
    init: { bg: 'linear-gradient(135deg, #636e72 0%, #555 100%)', border: '#95a5a6' },
    support: { bg: 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)', border: '#ff7675' },
    terminal: { bg: 'linear-gradient(135deg, #f39c12 0%, #e67e22 100%)', border: '#ffeaa7' }
};
```

### 10. Step Rendering with Links

```javascript
const stepsHtml = data.steps.map(s => {
    const labelContent = s.link
        ? `<a href="${s.link}" class="step-link">${s.label} →</a>`
        : `<span class="step-label">${s.label}</span>`;
    return `
    <div class="step-item${s.link ? ' has-link' : ''}">
        <div class="step-number">${s.step}</div>
        <div class="step-content">
            <span class="step-icon">${s.icon}</span>
            ${labelContent}
        </div>
    </div>
`}).join('');
```

**Step Link Styling:**
```css
.step-link {
    font-size: 15px;
    color: #74b9ff;
    text-decoration: none;
    transition: color 0.2s;
}

.step-link:hover {
    color: #a29bfe;
    text-decoration: underline;
}

.step-item.has-link {
    border-left-color: #74b9ff;
    cursor: pointer;
}
```

### 11. Filter Controls

```html
<div class="header-controls">
    <button onclick="filterByLoop('all')" class="active">All</button>
    <button onclick="filterByLoop('loop1')">Loop 1</button>
    <button onclick="filterByLoop('loop2')">Loop 2</button>
    <button onclick="openDrillDown('loop1')">📋 Details</button>
</div>
```

```javascript
function filterByLoop(loop) {
    document.querySelectorAll('.header-controls button').forEach(b => {
        b.classList.remove('active');
    });
    event.target.classList.add('active');

    Object.values(nodes).forEach(node => {
        const el = document.getElementById(`node-${node.id}`);
        el.classList.toggle('disabled',
            loop !== 'all' && node.loop !== loop);
    });
}
```

---

## File Organization

For large flowcharts with drill-down views:

```
docs/
├── [ProjectName]_Flowchart.html    # Main flowchart
└── [ProjectName]_Assets/           # Supporting files
    ├── Detail_Loop1.html
    ├── Detail_Loop2.html
    └── Detail_LoopN.html
```

**Navigation Links:**
- Main → Detail: `href="[ProjectName]_Assets/Detail_Loop1.html"`
- Detail → Main: `href="../[ProjectName]_Flowchart.html"`

---

## Sources & References

- [yWorks Label Placement](https://www.yworks.com/pages/automatic-label-placement-in-diagrams)
- [yFiles Layout Docs](https://docs.yworks.com/yfiles-html/dguide/layout/label_placement.html)
- [D3 Network Gallery](https://d3-graph-gallery.com/network.html)
- [React Flow Markers](https://reactflow.dev/examples/edges/markers)
- [W3C SVG Connector Spec](https://dev.w3.org/SVG/modules/connector/SVGConnector.html)

---

## Checklist

Before generating a flowchart:

**Core Layout:**
- [ ] Define LAYOUT constants with proper spacing
- [ ] Use border intersection for edge endpoints
- [ ] Add padding to prevent arrow-node overlap
- [ ] Offset labels perpendicular to edges
- [ ] Use gentle curves (max 40px offset)
- [ ] Set arrow refX to 10 (tip at line end)

**Interactivity:**
- [ ] Include interactive features (hover, select)
- [ ] Add filter buttons for categories
- [ ] Implement detail panel for node info
- [ ] Add drill-down modals for complex groups

**Visual Design:**
- [ ] Use consistent loop color palette
- [ ] Pattern nodes have dashed borders
- [ ] Info panel fonts 15% larger than chart
- [ ] Test with different node densities

**Navigation:**
- [ ] Add clickable links to detail views
- [ ] Provide back-navigation from detail files
- [ ] Organize supporting files in FC_Assets/

---

*Expertise package for SVG flowchart generation - V2.0*
