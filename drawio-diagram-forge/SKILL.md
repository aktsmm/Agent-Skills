---
name: drawio-diagram-forge
description: Generate draw.io editable diagrams (.drawio, .drawio.svg) from text, images, or Excel. Orchestrates 3-agent workflow (Analysis → Manifest → SVG generation) with quality gates. Use when creating architecture diagrams, flowcharts, sequence diagrams, or converting existing images to editable format. Supports Azure/AWS cloud icons.
argument-hint: "図にしたい文章・画像・Excel、図の種類"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Draw.io Diagram Forge

Generate **draw.io editable diagrams** using AI-powered workflow.

## When to Use

- Creating architecture diagrams (Azure, AWS)
- Converting flowcharts from text descriptions
- Transforming images/screenshots into editable format
- Generating swimlane, sequence diagrams

Choose this skill when the result will need later **GUI editing** in draw.io, cloud icons, or documentation-facing diagram assets.

## When NOT to Use

- Quick inline diagrams that are easier to keep as Mermaid in README or Markdown
- One-off text-native diagrams where manual GUI adjustment is not expected

## Prerequisites

| Tool                                                                                            | Required |
| ----------------------------------------------------------------------------------------------- | -------- |
| VS Code                                                                                         | Yes      |
| [Draw.io Integration](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio) | Yes      |
| GitHub Copilot                                                                                  | Yes      |

## Quick Start

```
Create a login flow diagram
```

```
Generate an Azure Hub-Spoke architecture diagram
```

```
From inputs/requirements.md, create a system diagram
```

## Output Formats

| Extension      | Description    | When to Use     |
| -------------- | -------------- | --------------- |
| `*.drawio`     | Native format  | **Recommended** |
| `*.drawio.svg` | SVG + metadata | Markdown/Web    |
| `*.drawio.png` | PNG + metadata | Image with edit |

**Output**: `outputs/`

### Recommended Delivery Pattern

For documentation-facing diagrams, generate outputs as a pair:

- `name.drawio` for editing in VS Code Draw.io
- `name.drawio.svg` for README / web embedding

If the visible asset started from manual SVG cleanup or hand-authored layout tweaks, still keep a matching `name.drawio` as the editable SSOT. Do not leave documentation diagrams as SVG-only when future edits are expected.

Recommended markdown pattern:

```markdown
![Architecture Diagram](outputs/name.drawio.svg)

- [outputs/name.drawio.svg](outputs/name.drawio.svg)
- [outputs/name.drawio](outputs/name.drawio)
```

If multilingual variants are needed, keep parallel filenames instead of overwriting a single asset:

- `name.drawio` / `name.drawio.svg`
- `name-ja.drawio` / `name-ja.drawio.svg`

This keeps the editable source, the embeddable image, and the language variants aligned.

For local article drafting, if the Markdown preview surface does not reliably render the SVG variant, it is acceptable to:

- keep `.drawio` as the editable source
- keep `.drawio.svg` as the web / embeddable artifact
- temporarily reference a generated `*.png` from the draft article for local preview stability

At publish time, replace local relative preview paths with the final hosted asset URL.

## Workflow

```
USER INPUT → ORCHESTRATOR → MANIFEST GATEWAY → SVG FORGE → COMPLETED
```

### Quality Gates

| Score  | Action        |
| ------ | ------------- |
| 90-100 | Proceed       |
| 70-84  | Fix and retry |
| 50-69  | Simplify      |
| 0-29   | Ask user      |

### Limits

| Limit             | Value |
| ----------------- | ----- |
| Manifest revision | 2     |
| SVG revision      | 2     |
| Total timeout     | 45min |

## Cloud Icons

→ **[references/cloud-icons.md](references/cloud-icons.md)**

For Azure-centric diagrams, proactively use the official Azure icon set when a verified Azure2 icon exists. Prefer icon + short label over plain rounded boxes for first-class Azure services. Fall back to generic boxes only when the icon is missing, misleading, or would hurt readability.

### Enable in VS Code

1. Open `.drawio` file
2. Click **"+ More Shapes"** (bottom-left)
3. Enable: Azure, AWS
4. Apply

### Azure Format (Critical)

```xml
<!-- WRONG -->
<mxCell style="shape=mxgraph.azure.front_door;..." />

<!-- CORRECT -->
<mxCell style="aspect=fixed;image=img/lib/azure2/networking/Front_Doors.svg;..." />
```

### Azure Icon Preference

- Use Azure service icons aggressively for Azure architecture diagrams when the service has a verified Azure2 path.
- Keep the service name as a short text label even when the icon is obvious.
- Do not mix verified Azure2 icons with generic blue boxes for the same diagram layer unless there is a clear reason.
- If only some services have official icons, use icons for those services and use neutral fallback boxes for the rest.

## References

| File                                                  | Description              |
| ----------------------------------------------------- | ------------------------ |
| [mxcell-structure.md](references/mxcell-structure.md) | mxCell XML structure     |
| [cloud-icons.md](references/cloud-icons.md)           | Azure/AWS icon guide     |
| [style-guide.md](references/style-guide.md)           | Node colors, edge styles |

## Scripts

| Script                       | Description               |
| ---------------------------- | ------------------------- |
| `scripts/validate_drawio.py` | Validate mxCell structure |

## Troubleshooting

| Issue                             | Solution                                                                                       |
| --------------------------------- | ---------------------------------------------------------------------------------------------- |
| Blank in draw.io                  | Check `content` attribute                                                                      |
| Edges not visible                 | Verify node IDs                                                                                |
| Icons missing                     | Enable Azure/AWS shapes                                                                        |
| Text overlaps near outer frame    | Inset top note/callout boxes 16-24px from the panel border, increase box height, and wrap to 3-4 lines. Review at actual embed width before finishing. See [style-guide.md](references/style-guide.md) Top Callouts / Note Boxes |
| README image only links to source | Generate `*.drawio.svg` and embed that instead of linking only to `*.drawio`                   |
| SVG is viewable but hard to edit later | Keep a paired `*.drawio` source and treat it as the editable SSOT; use SVG as delivery output, not as the only source file |
| Local Markdown preview does not show the expected diagram | Export `*.png` from `.drawio` and use that in the draft article preview. Keep `.drawio` and `*.drawio.svg` as the editable and embeddable pair for final delivery |
| Too many crossing arrows          | Align source/target y to make edges horizontal; spread `entryY` on shared targets. See [style-guide.md](references/style-guide.md) Edge Crossing Prevention |
| Legend inside a container          | Move legend outside the outermost box. See [style-guide.md](references/style-guide.md) Nested Containers |
| Diagonal edge crosses a box        | Move annotation boxes below diagonal endpoints. See [style-guide.md](references/style-guide.md) Flow Diagrams |
| Title duplicated in PDF/HTML        | Remove title mxCell from diagram; let the document layer handle captions |
| PNG export blurry or cropped        | Use `draw.io --export --format png --scale 2` instead of browser screenshot. See [style-guide.md](references/style-guide.md) Export for PDF Pipelines |

## Done Criteria

- [ ] `.drawio` or `.drawio.svg` file generated
- [ ] Diagram opens correctly in VS Code Draw.io extension
- [ ] All nodes and edges visible
- [ ] Quality gate score ≥ 85
- [ ] If diagram is referenced from documentation, both editable source and embeddable image are provided
- [ ] Render review completed at the target embed width with no text overlap, clipping, or border collisions
