---
name: powerpoint-automation
description: Create professional PowerPoint presentations from various sources including web articles, blog posts, and existing PPTX files. Use when creating PPTX, converting articles to slides, or translating presentations.
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# PowerPoint Automation

AI-powered PPTX generation using Orchestrator-Workers pattern.

## When to Use

- **PowerPoint**, **PPTX**, **create presentation**, **slides**
- Convert web articles/blog posts to presentations
- Translate English PPTX to Japanese
- Create presentations using custom templates

## Quick Start

**From Web Article:**

```
Create a 15-slide presentation from: https://zenn.dev/example/article
```

**From Existing PPTX:**

```
Translate this presentation to Japanese: input/presentation.pptx
```

## Workflow

```
TRIAGE → PLAN → PREPARE_TEMPLATE → EXTRACT → TRANSLATE → BUILD → REVIEW → DONE
```

| Phase   | Script/Agent              | Description            |
| ------- | ------------------------- | ---------------------- |
| EXTRACT | `extract_images.py`       | Content → content.json |
| BUILD   | `create_from_template.py` | Generate PPTX          |
| REVIEW  | PPTX Reviewer             | Quality check          |

## Key Scripts

→ **[references/SCRIPTS.md](references/SCRIPTS.md)** for complete reference

| Script                    | Purpose                                |
| ------------------------- | -------------------------------------- |
| `create_from_template.py` | Generate PPTX from content.json (main) |
| `reconstruct_analyzer.py` | Convert PPTX → content.json            |
| `extract_images.py`       | Extract images from PPTX/web           |
| `validate_content.py`     | Validate content.json schema           |
| `validate_pptx.py`        | Detect text overflow                   |

## content.json (IR)

All agents communicate via this intermediate format:

```json
{
  "slides": [
    { "type": "title", "title": "Title", "subtitle": "Sub" },
    { "type": "content", "title": "Topic", "items": ["Point 1"] }
  ]
}
```

→ **[references/schemas/content.schema.json](references/schemas/content.schema.json)**

## Templates

| Template              | Purpose                  | Layouts   |
| --------------------- | ------------------------ | --------- |
| `assets/template.pptx` | デフォルト (Japanese, 16:9) | 4 layouts |

### template レイアウト詳細

| Index | Name               | Category | 用途             |
| ----- | ------------------ | -------- | ---------------- |
| 0     | タイトル スライド   | title    | プレゼン冒頭     |
| 1     | タイトルとコンテンツ | content  | 標準コンテンツ   |
| 2     | 1_タイトルとコンテンツ | content | 標準コンテンツ（別版） |
| 3     | セクション見出し    | section  | セクション区切り |

**使用例:**
```bash
python scripts/create_from_template.py assets/template.pptx content.json output.pptx --config assets/template_layouts.json
```

## Agents

→ **[references/agents/](references/agents/)** for definitions

| Agent         | Purpose               |
| ------------- | --------------------- |
| Orchestrator  | Pipeline coordination |
| Localizer     | Translation (EN ↔ JA) |
| PPTX Reviewer | Final quality check   |

## Design Principles

- **SSOT**: content.json is canonical
- **SRP**: Each agent/script has one purpose
- **Fail Fast**: Max 3 retries per phase
- **Human in Loop**: User confirms at PLAN phase

## References

| File                                    | Content              |
| --------------------------------------- | -------------------- |
| [SCRIPTS.md](references/SCRIPTS.md)     | Script documentation |
| [USE_CASES.md](references/USE_CASES.md) | Workflow examples    |
| [agents/](references/agents/)           | Agent definitions    |
| [schemas/](references/schemas/)         | JSON schemas         |

## Technical Content Addition (Azure/MS Topics)

When adding Azure/Microsoft technical content to slides, follow the same verification workflow as QA:

### Workflow

```
[Content Request] → [Researcher] → [Reviewer] → [PPTX Update]
                         ↓              ↓
                   Docs MCP 検索    内容検証
```

### Required Steps

1. **Research Phase**: Use `microsoft_docs_search` / `microsoft_docs_fetch` to gather official information
2. **Review Phase**: Verify the accuracy of content before adding to slides
3. **Build Phase**: Update content.json and regenerate PPTX

### Forbidden

- ❌ Adding technical content without MCP verification
- ❌ Skipping review for "simple additions"
- ❌ Generating PPTX while PowerPoint has the file open

### File Lock Prevention

Before generating PPTX, check if the file is locked:

```powershell
# Check if file is locked
$path = "path/to/file.pptx"
try { [IO.File]::OpenWrite($path).Close(); "File is writable" }
catch { "File is LOCKED - close PowerPoint first" }
```

## Done Criteria

- [ ] `content.json` generated and validated
- [ ] PPTX file created successfully
- [ ] No text overflow detected
- [ ] User confirmed output quality
