# Style Guide

## Node Colors

| Purpose | fillColor | strokeColor | Example Use |
|---------|-----------|-------------|-------------|
| **Standard** | `#dae8fc` | `#6c8ebf` | Default nodes |
| **Start/End** | `#d5e8d4` | `#82b366` | Process start/end |
| **Decision** | `#fff2cc` | `#d6b656` | Conditions, branches |
| **Error/Warning** | `#f8cecc` | `#b85450` | Error states |
| **External** | `#e1d5e7` | `#9673a6` | External systems |
| **Neutral** | `#f5f5f5` | `#666666` | Groups, containers |

## Edge Styles

### Orthogonal (Recommended)

```
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;
```

### Curved

```
edgeStyle=elbowEdgeStyle;elbow=horizontal;rounded=1;
```

### Straight

```
endArrow=classic;html=1;
```

## Shape Styles

### Rounded Rectangle

```
rounded=1;whiteSpace=wrap;html=1;
```

### Ellipse

```
ellipse;whiteSpace=wrap;html=1;
```

### Diamond

```
rhombus;whiteSpace=wrap;html=1;
```

### Swimlane/Container

```
swimlane;horizontal=1;startSize=30;
```

## Layout Recommendations

### Spacing

| Element | Recommended Gap |
|---------|-----------------|
| Horizontal nodes | 50-80px |
| Vertical nodes | 40-60px |
| Group padding | 20px |
| Edge clearance | 10px minimum |

### Nested Containers (Hierarchy Diagrams)

When using nested rectangles to show hierarchy (e.g., Enterprise > Org > Team > Repo):

- **Container height** = content bottom edge + 15–20px padding. Do not use large fixed heights when children are few.
- **Legend placement** = always outside the outermost container. Never inside a child container — it reads as part of that group.
- **Page size** = tightest bounding box of all elements + 20px margin. Avoid "generous" pages that create dead whitespace.
- **Edges are optional** — spatial containment already conveys hierarchy. Only add arrows when showing data/control flow across containers.

### Flow Diagrams (Branch/Merge Lines)

When combining diagonal branch/merge lines with annotation boxes (e.g., GitHub Flow step labels):

- **Place step boxes below the diagonal endpoints** — if a diagonal goes from (x1,y1) to (x2,y2), boxes must have `y > max(y1, y2)` to avoid crossing.
- **Dashed connectors** starting from a box edge should begin at `y - 2px` (not exactly at the top edge) to avoid false overlap in validators.
- **Keep horizontal feature branch and step row on separate Y bands** — minimum 40px gap between the branch line Y and the top of step boxes.

### Alignment

- Align nodes in grid (gridSize=10)
- Center labels in nodes
- Use consistent node sizes

### Diagram Size

| Complexity | Recommended Canvas |
|------------|---------------------|
| Simple (≤5 nodes) | 800x600 |
| Moderate (6-15 nodes) | 1200x800 |
| Complex (>15 nodes) | 1600x1200 |

## Font Settings

```
fontSize=12;fontStyle=0;fontFamily=Helvetica;
```

| Element | Font Size |
|---------|-----------|
| Node label | 12px |
| Edge label | 10px |
| Group title | 14px |
| Diagram title | 16-18px |
