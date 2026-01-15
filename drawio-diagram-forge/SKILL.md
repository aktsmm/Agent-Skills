---
name: drawio-diagram-forge
description: Generate draw.io editable diagrams (.drawio, .drawio.svg) from text, images, or Excel. Orchestrates 3-agent workflow (Analysis → Manifest → SVG generation) with quality gates. Use when creating architecture diagrams, flowcharts, sequence diagrams, or converting existing images to editable format. Supports Azure/AWS cloud icons.
license: CC BY-NC-SA 4.0
---

# Draw.io Diagram Forge

Generate **draw.io editable diagrams** using AI-powered orchestrated workflow.

## When to Use

- **General diagram requests** - "Create a diagram", "Draw me a chart", etc.
- Creating architecture diagrams (Azure, AWS, on-premises)
- Converting flowcharts, system diagrams from text descriptions
- Transforming existing images/screenshots into editable draw.io format
- Generating swimlane diagrams, sequence diagrams from Excel/Markdown

## Prerequisites

| Tool                    | Purpose            | Required |
| ----------------------- | ------------------ | -------- |
| **VS Code**             | IDE                | ✅       |
| **Draw.io Integration** | Edit .drawio files | ✅       |
| **GitHub Copilot**      | AI generation      | ✅       |

**Install extension**: [Draw.io Integration](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio)

## Quick Start

### Basic Usage

```
Create a login flow diagram
```

```
Generate an Azure architecture diagram with Hub-Spoke topology
```

```
Convert this Excel file to a flowchart
```

### With Input Files

```
From inputs/requirements.md, create a system architecture diagram
```

```
Recreate this image (inputs/architecture.png) as an editable draw.io file
```

## Output Formats

| Extension      | Description            | When to Use                      |
| -------------- | ---------------------- | -------------------------------- |
| `*.drawio`     | Native draw.io format  | ⭐ **Recommended** - Most stable |
| `*.drawio.svg` | SVG + draw.io metadata | Embedding in Markdown/Web        |
| `*.drawio.png` | PNG + draw.io metadata | Image with edit capability       |

**Output directory**: `outputs/`

## Workflow Overview

```
USER INPUT
    │
    ▼
┌─────────────────────────────────────────────────┐
│           FLOW ORCHESTRATOR                      │
│  ┌─────────────────────────────────────────┐    │
│  │ Internal Modules:                        │    │
│  │ • Analysis (input classification)        │    │
│  │ • Review (quality scoring)               │    │
│  │ • State (context management)             │    │
│  │ • Timeout (watchdog)                     │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
    │
    ├──► MANIFEST GATEWAY (create manifest)
    │
    └──► SVG FORGE (generate diagram + validation)
    │
    ▼
COMPLETED (.drawio file)
```

### Quality Gates

| Score  | Action      | Description                |
| ------ | ----------- | -------------------------- |
| 90-100 | ✅ Proceed  | High quality, continue     |
| 85-89  | ⚠️ Note     | Minor issues noted         |
| 70-84  | 🔄 Fix      | Auto-fix and retry         |
| 50-69  | 📉 Simplify | Reduce complexity          |
| 30-49  | 📦 Partial  | Deliver partial result     |
| 0-29   | ❌ Escalate | Ask user for clarification |

### Iteration Limits

| Limit             | Value | On Exceed                  |
| ----------------- | ----- | -------------------------- |
| Manifest revision | 2     | Force proceed with warning |
| SVG revision      | 2     | Partial success            |
| Total revisions   | 4     | Partial success            |
| Total timeout     | 45min | Checkpoint-based decision  |

## Advanced: Agent Delegation

For complex diagrams, explicitly invoke the orchestrator:

```
@flow-orchestrator Create a detailed microservices architecture from inputs/requirements.md
```

This triggers the full manifest → review → generation → review cycle.

## Resources

### References

| File                                                  | Description                      |
| ----------------------------------------------------- | -------------------------------- |
| [mxcell-structure.md](references/mxcell-structure.md) | mxCell XML structure for draw.io |
| [cloud-icons.md](references/cloud-icons.md)           | Azure/AWS icon usage guide       |
| [style-guide.md](references/style-guide.md)           | Node colors, edge styles         |

### Scripts

| File                                             | Description               |
| ------------------------------------------------ | ------------------------- |
| [validate_drawio.py](scripts/validate_drawio.py) | Validate mxCell structure |

## Cloud Icons (Azure/AWS)

To enable cloud icons in generated diagrams:

1. Open generated `.drawio` file in VS Code
2. Click **"+ More Shapes"** (bottom-left)
3. Enable: ✅ **Azure**, ✅ **AWS**
4. Click **Apply**

## Troubleshooting

| Issue             | Cause                 | Solution                  |
| ----------------- | --------------------- | ------------------------- |
| Blank in draw.io  | Missing mxCell        | Check `content` attribute |
| Edges not visible | Invalid source/target | Verify node IDs           |
| Icons missing     | Library not enabled   | Enable Azure/AWS shapes   |

## Technical Details

### How It Works

AI generates **XML/SVG text** that renders as editable diagrams:

```
Natural Language  →  XML/mxGraphModel  →  Rendered Diagram
     ↑                    ↑                      ↑
  Human input        AI generates          SVG rendering
```

### mxCell Completeness Rule

```
Required mxCells >= 2 + nodes + edges
```

- `mxCell id="0"` (root)
- `mxCell id="1"` (default parent)
- One mxCell per node (`vertex="1"`)
- One mxCell per edge (`edge="1"`)
