---
name: drawio-diagram-forge
description: Generate draw.io editable diagrams (.drawio, .drawio.svg) from text, images, or Excel. Orchestrates 3-agent workflow (Analysis → Manifest → SVG generation) with quality gates. Use when creating architecture diagrams, flowcharts, sequence diagrams, or converting existing images to editable format. Supports Azure/AWS cloud icons. Triggers on draw.io, drawio, ダイアグラム, 図解, アーキ図, フローチャート, シーケンス図.
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
- Editing Azure/AWS icons in existing .drawio files

Choose this skill when the result will need later **GUI editing** in draw.io, cloud icons, or documentation-facing diagram assets.

## When NOT to Use

- Quick inline diagrams that are easier to keep as Mermaid in README or Markdown
- One-off text-native diagrams where manual GUI adjustment is not expected
- Charts or infographics that require exact axes, data binding, typography, or scripted regeneration
- Large multilingual label sets whose font rendering must be identical across platforms

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

If the user asks for an editable diagram, make `*.drawio` the primary deliverable. Do not let a plain SVG or preview artifact become the file the user is expected to edit.

### Recommended Delivery Pattern

ドキュメント向けは `name.drawio` (editable) + `name.drawio.svg` (embed) を対で出す。多言語変体・Qiita への掲載・ローカル preview 脱出手順は → [references/delivery-patterns.md](references/delivery-patterns.md)。

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

Use [Cloud Icons Reference](references/cloud-icons.md). Azure diagrams must use verified `img/lib/azure2/**/*.svg` image paths, retain short service labels, and fall back to neutral boxes only when an icon is missing or misleading.

## References

| File                                                  | Description              |
| ----------------------------------------------------- | ------------------------ |
| [mxcell-structure.md](references/mxcell-structure.md) | mxCell XML structure     |
| [cloud-icons.md](references/cloud-icons.md)           | Azure/AWS icon guide     |
| [style-guide.md](references/style-guide.md)           | Node colors, edge styles |
| [delivery-patterns.md](references/delivery-patterns.md) | Editable + embed pair, Qiita, multilingual |
| [troubleshooting.md](references/troubleshooting.md)   | Full troubleshooting (14 items) |

## Scripts

| Script                       | Description               |
| ---------------------------- | ------------------------- |
| `scripts/validate_drawio.py` | Validate mxCell structure |

## Troubleshooting

頻度高トップ 4 件を下記に掲載。全一覧（フレーム/エッジ/余白/PDF 出力、レジェンド位置 等 14 項目）は [references/troubleshooting.md](references/troubleshooting.md)。

| Issue | Solution |
| --- | --- |
| Blank in draw.io | Check `content` attribute |
| Edges not visible | Verify node IDs |
| Icons missing | Enable Azure/AWS shapes (+ More Shapes → Azure / AWS) |
| Text overlaps near outer frame | Inset top callout 16–24px, increase height, wrap to 3–4 lines; review at actual embed width |

## Done Criteria

- [ ] `.drawio` or `.drawio.svg` file generated
- [ ] Diagram opens correctly in VS Code Draw.io extension
- [ ] All nodes and edges visible
- [ ] User-facing links point to the editable `.drawio` when editability is expected
- [ ] Decision flows avoid long return/merge lines that bundle branch outputs back into one sink
- [ ] Quality gate score ≥ 85
- [ ] If diagram is referenced from documentation, both editable source and embeddable image are provided
- [ ] Render review completed at the target embed width with no text overlap, clipping, or border collisions
