---
name: drawio-diagram-forge
description: Generate draw.io editable diagrams (.drawio, .drawio.svg) from text, images, or Excel. Orchestrates 3-agent workflow (Analysis → Manifest → SVG generation) with quality gates. Use when creating architecture diagrams, flowcharts, sequence diagrams, or converting existing images to editable format. Supports Azure/AWS cloud icons.
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

| Issue             | Solution                  |
| ----------------- | ------------------------- |
| Blank in draw.io  | Check `content` attribute |
| Edges not visible | Verify node IDs           |
| Icons missing     | Enable Azure/AWS shapes   |

## Done Criteria

- [ ] `.drawio` or `.drawio.svg` file generated
- [ ] Diagram opens correctly in VS Code Draw.io extension
- [ ] All nodes and edges visible
- [ ] Quality gate score ≥ 85
