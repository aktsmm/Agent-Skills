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

| Template               | Purpose                     | Layouts   |
| ---------------------- | --------------------------- | --------- |
| `assets/template.pptx` | デフォルト (Japanese, 16:9) | 4 layouts |

### template レイアウト詳細

| Index | Name                    | Category | 用途                   |
| ----- | ----------------------- | -------- | ---------------------- |
| 0     | タイトル スライド       | title    | プレゼン冒頭           |
| 1     | タイトルとコンテンツ    | content  | 標準コンテンツ         |
| 2     | 1\_タイトルとコンテンツ | content  | 標準コンテンツ（別版） |
| 3     | セクション見出し        | section  | セクション区切り       |

**使用例:**

```bash
python scripts/create_from_template.py assets/template.pptx content.json output.pptx --config assets/template_layouts.json
```

### テンプレート管理のベストプラクティス

#### 複数デザイン（スライドマスター）の整理

テンプレートPPTXに複数のスライドマスターが含まれている場合、出力が不安定になることがあります。

**確認方法:**

```bash
python scripts/create_from_template.py assets/template.pptx --list-layouts
```

**対処法:**

1. PowerPointでテンプレートを開く
2. [表示] → [スライドマスター] を選択
3. 不要なスライドマスターを削除
4. 保存後、`template_layouts.json` を再生成

```bash
python scripts/analyze_template.py assets/template.pptx
```

#### content.json の階層構造

箇条書きに階層構造（インデント）を持たせる場合は `items` ではなく `bullets` 形式を使用：

```json
// ❌ フラットな表示になる
{"type": "content", "items": ["項目1", "  詳細1", "項目2"]}

// ✅ 階層構造が効く
{"type": "content", "bullets": [
  {"text": "項目1", "level": 0},
  {"text": "詳細1", "level": 1},
  {"text": "項目2", "level": 0}
]}
```

### テンプレート管理のベストプラクティス

#### 複数デザイン（スライドマスター）の整理

テンプレートPPTXに複数のスライドマスターが含まれている場合、出力が不安定になることがあります。

**確認方法:**

```bash
python scripts/create_from_template.py assets/template.pptx --list-layouts
```

**対処法:**

1. PowerPointでテンプレートを開く
2. [表示] → [スライドマスター] を選択
3. 不要なスライドマスターを削除
4. 保存後、template_layouts.json を再生成

```bash
python scripts/analyze_template.py assets/template.pptx
```

#### content.json の階層構造

箇条書きに階層構造（インデント）を持たせる場合は items ではなく bullets 形式を使用：

```json
// ❌ フラットな表示になる
{"type": "content", "items": ["項目1", "  詳細1", "項目2"]}

// ✅ 階層構造が効く
{"type": "content", "bullets": [
  {"text": "項目1", "level": 0},
  {"text": "詳細1", "level": 1},
  {"text": "項目2", "level": 0}
]}
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

## URL Format in Slides

Reference URLs must use **"Title - URL"** format for APPENDIX slides:

```
VPN Gateway の新機能 - https://learn.microsoft.com/ja-jp/azure/vpn-gateway/whats-new
```

→ **[references/content-guidelines.md](references/content-guidelines.md)** for details

## References

| File                                                      | Content              |
| --------------------------------------------------------- | -------------------- |
| [SCRIPTS.md](references/SCRIPTS.md)                       | Script documentation |
| [USE_CASES.md](references/USE_CASES.md)                   | Workflow examples    |
| [content-guidelines.md](references/content-guidelines.md) | URL format, bullets  |
| [agents/](references/agents/)                             | Agent definitions    |
| [schemas/](references/schemas/)                           | JSON schemas         |

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

## Post-Processing (URL Linkification)

> ⚠️ `create_from_template.py` does not process `footer_url`. Post-processing required.

### Items Requiring Post-Processing

| Item            | Processing                         |
| --------------- | ---------------------------------- |
| `footer_url`    | Add linked textbox at slide bottom |
| URLs in bullets | Convert to hyperlinks              |
| Reference URLs  | Linkify URLs in Appendix           |

### Save with Different Name (File Lock Workaround)

PowerPoint locks open files. Always save with a different name:

```python
# ❌ Fails if file is open
prs.save('file.pptx')  # PermissionError

# ✅ Save with different name
prs.save('file_withURL.pptx')
```

| Processing    | Suffix     |
| ------------- | ---------- |
| URL added     | `_withURL` |
| Final version | `_final`   |
| Fixed version | `_fixed`   |

## Done Criteria

- [ ] `content.json` generated and validated
- [ ] PPTX file created successfully
- [ ] No text overflow detected
- [ ] User confirmed output quality
