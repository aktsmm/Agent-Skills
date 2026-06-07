# Style Guide

## Node Colors

| Purpose           | fillColor | strokeColor | Example Use          |
| ----------------- | --------- | ----------- | -------------------- |
| **Standard**      | `#dae8fc` | `#6c8ebf`   | Default nodes        |
| **Start/End**     | `#d5e8d4` | `#82b366`   | Process start/end    |
| **Decision**      | `#fff2cc` | `#d6b656`   | Conditions, branches |
| **Error/Warning** | `#f8cecc` | `#b85450`   | Error states         |
| **External**      | `#e1d5e7` | `#9673a6`   | External systems     |
| **Neutral**       | `#f5f5f5` | `#666666`   | Groups, containers   |

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

### Title / Caption

- **Do NOT embed title text in the diagram** (e.g., "図1-1 ..."). Captions belong in the document layer (Markdown `![caption](...)`, Re:VIEW `//image[id][caption]`, etc.).
- Embedding titles causes duplication when the document already renders a figure caption.
- If the exported image is likely to circulate **standalone** (chat, slide, ticket, SNS, pasted image), use the diagram title/subtitle to identify the **feature or topic name** directly. Avoid generic headings like `before / after` alone.
- Good: `Summarized Gateway Prefixes の before / after`
- Weak: `ExpressRoute の広告ルート数を before / after でみる` when the feature name is missing from the image itself.

### Spacing

| Element          | Recommended Gap |
| ---------------- | --------------- |
| Horizontal nodes | 50-80px         |
| Vertical nodes   | 40-60px         |
| Group padding    | 20px            |
| Edge clearance   | 10px minimum    |

### Top Callouts / Note Boxes

For explanatory note boxes placed near the top of a panel or container:

- **Inset from the outer frame** by at least 16-24px. Do not let the note box kiss or visually merge with the panel border.
- **Prefer 3-4 short lines** over 2 long lines. If Japanese text feels tight, reduce line length before reducing font size.
- **Increase note box height first** when text feels crowded. Do not solve crowding only by shrinking fonts.
- **Keep arrow labels on a separate Y band** from the note box. Labels that sit at the same height tend to look overlapped in exports.
- **Review at actual embed width** after export. A diagram that looks fine at full canvas size can still collide when embedded in Markdown or docs.

### Article Concept / Lifecycle Diagrams

For article-facing concept diagrams that explain a repeated workflow:

- Use a single visible start point. If the flow begins from multiple places, readers often cannot tell what to follow first.
- For metric diagrams such as usage rate, show denominator and numerator explicitly, then summarize the formula in one final node. Avoid long dashed aggregation lines that make the diagram feel like a wiring diagram.
- **Keep the main cycle to 3-4 primary nodes**. Support tools, marketplaces, and implementation aids should be a footer note or side callout, not peer nodes in the main loop.
- **Use outcome-oriented node titles** such as `Skill を改善`, not implementation-detail titles such as `Gotchas に戻す`. Highlight the important detail (`Gotchas`) inside the node body instead.
- **Split long slash-separated phrases** into separate short lines. If a line like `description / Gotchas / references` feels tight at embed width, rewrite it as `description を整える` + `Gotchas / references に分ける`.
- **Shrink-wrap the canvas after layout changes**. If footer notes move up, reduce page height so exported assets do not carry large dead whitespace.
- **Validate both source and delivery artifacts** after wording tweaks: `.drawio` is the editable SSOT, and `.drawio.svg` is the Markdown/web artifact.

### Edge Crossing Prevention

For complex diagrams (>15 nodes) with many-to-one or fan-out edges:

- **Align source and target y** — place each agent/processor at the same y as its output node. Lines stay horizontal, crossing drops to near zero.
- **Avoid swimlane-relative coordinates** — when edges cross swimlane boundaries, `exitX`/`entryY` resolve to group-relative positions that are hard to predict. Use absolute positioning (`parent="1"`) for all nodes instead.
- **Spread entryY on shared targets** — when multiple edges enter the same node, enlarge the node height and assign distinct `entryY` values (e.g., 0.1 / 0.5 / 0.9) so lines arrive at different vertical points.
- **Collapse fan-out into one edge** — instead of N individual arrows from an orchestrator to N children, draw a single dashed arrow to a group outline and label it (e.g., "delegates").
- **Separate auxiliary elements** — legends, data stores, and footnotes must sit below the main flow with ≥40px vertical gap from the lowest flow node. Never place them at the same y as flow outputs.

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

### Icons On Connectors

When a small service icon sits close to a busy connector or arrow:

- **Prefer icon-only** and let the nearby node / edge label carry the meaning. Do not force a second label under the icon if it creates collisions.
- **Move the icon 10-20px away from the connector centerline** before shrinking it further.
- **Keep the icon above the connector in z-order / draw order** so the arrow does not cut through the symbol.
- If the connector already has a readable label, avoid repeating the same service name under the icon.

### Alignment

- Align nodes in grid (gridSize=10)
- Center labels in nodes
- Use consistent node sizes
- **Container with children** → `verticalAlign=top;spacingTop=5;` to keep the label above child nodes
- **Standalone box (no children)** → `verticalAlign=middle;` to center text and avoid lopsided whitespace

### Public-safe Labels

- For diagrams that may be published externally, avoid customer-specific or vendor-internal acronyms unless the acronym itself is the subject of the diagram.
- Prefer generic labels such as `On-premises gateway`, `On-premises router`, or `Edge network` over terms that only make sense in one customer's environment.
- If an internal acronym must appear somewhere, keep it in the surrounding article text, not as the primary label inside the figure.

### Diagram Size

| Complexity            | Recommended Canvas   |
| --------------------- | -------------------- |
| Simple (≤5 nodes)     | 800–900 × 400–500    |
| Moderate (6-15 nodes) | 1000–1200 × 500–700  |
| Complex (>15 nodes)   | 1200–1600 × 700–1000 |

Always shrink-wrap: set page width/height to tightest bounding box + 20px margin.

## Editable Source Policy

- Treat `.drawio` as the editable source of truth for documentation diagrams.
- Treat `.drawio.svg` as the delivery/render artifact for Markdown and web embedding.
- Do not label a plain SVG as `.drawio.svg`. That suffix is reserved for metadata-embedded SVG exports that Draw.io can reopen.
- If a diagram required manual SVG-level cleanup, recreate or preserve the equivalent `.drawio` source before calling it done.
- Do not leave a documentation diagram as SVG-only unless the user explicitly asked for a disposable one-off artifact.
- If the editor keeps resolving a stale path or refuses to open a file that exists, it is acceptable to create short alias filenames such as `current-understanding.drawio` and `current-understanding.svg`, then repoint local links to the alias pair.

## Font Settings

```
fontSize=12;fontStyle=0;fontFamily=Helvetica;
```

| Element     | Font Size |
| ----------- | --------- |
| Node label  | 12px      |
| Edge label  | 10px      |
| Group title | 14px      |

## Export for PDF Pipelines

When diagrams are embedded in PDF (via Re:VIEW, LaTeX, Pandoc, etc.):

- **Export directly from `.drawio` to PNG** using the draw.io desktop CLI:
  ```
  draw.io --export --format png --scale 2 --output out.png source.drawio
  ```
- **Do NOT use browser/Edge `--screenshot` on SVG** — this produces a fixed-viewport capture (e.g., 756×488) regardless of diagram size, causing blurriness and cropping.
- `--scale 2` produces 2× resolution for crisp text at print DPI.
- The exported SVG from draw.io CLI is "plain SVG" (not re-editable in the VS Code Draw.io extension). Keep the `.drawio` as the editable source.
- For Markdown preview, reference `*.drawio.svg`. For PDF build, use the PNG export.
