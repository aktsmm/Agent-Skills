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

箇条書きに階層構造（インデント）を持たせる場合は `items` ではなく `bullets` 形式を使用（`items` はフラット表示になる）：

```json
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

## Shape-based Architecture Diagrams

When creating network/architecture diagrams, use **PowerPoint shapes** instead of ASCII art text boxes. ASCII art is unreadable in presentation mode.

### Design Pattern

```python
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.util import Cm, Pt

# Color scheme
AZURE_BLUE = RGBColor(0, 120, 212)
LIGHT_BLUE = RGBColor(232, 243, 255)
ONPREM_GREEN = RGBColor(16, 124, 65)
LIGHT_GREEN = RGBColor(232, 248, 237)

# Outer frame (Azure VNet)
box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, w, h)
box.fill.solid()
box.fill.fore_color.rgb = LIGHT_BLUE
box.line.color.rgb = AZURE_BLUE

# Dashed connector (tunnel)
conn = slide.shapes.add_connector(1, x1, y1, x2, y2)  # 1 = straight
conn.line.color.rgb = AZURE_BLUE
conn.line.dash_style = 2  # dash
```

### Layout Tips

- Use `Cm()` for positioning (not `Inches()`) — easier to reason about on metric-based slides
- Leave **at least 1.5cm** vertical gap between Azure and on-premises zones for tunnel lines
- Place labels **inside** boxes (not overlapping edges) to avoid visual clutter
- Use **color coding** to distinguish zones: blue = Azure, green = on-premises, orange = cross-connect
- For dual diagrams (side-by-side), split slide into left/right halves with **12cm** left margin for the right diagram

### Anti-patterns

```
❌ ASCII art in textboxes (unreadable in presentation mode)
❌ Overlapping shapes due to insufficient spacing
❌ Placing labels outside their parent containers
❌ Using absolute EMU values without helper functions
```

## Hyperlink Batch Processing

Batch-add hyperlinks and page titles to all URLs in a presentation:

### Workflow

```python
import re
url_pattern = re.compile(r'(https?://[^\s\)）]+)')

# 1. Build URL→Title map (use MCP docs_search or fetch_webpage)
URL_TITLES = {
    'https://learn.microsoft.com/.../whats-new': 'Azure VPN Gateway の新機能',
    ...
}

# 2. Iterate all runs and add hyperlinks
for slide in prs.slides:
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                urls = url_pattern.findall(run.text)
                for url in urls:
                    if not (run.hyperlink and run.hyperlink.address):
                        run.hyperlink.address = url.rstrip('/')
                    # Prepend title if missing
                    title = URL_TITLES.get(url.rstrip('/'))
                    if title and title not in run.text:
                        run.text = f'{title}\n{url}'
```

### Verification

```python
hlink_count = sum(
    1 for slide in prs.slides
    for shape in slide.shapes if shape.has_text_frame
    for para in shape.text_frame.paragraphs
    for run in para.runs
    if run.hyperlink and run.hyperlink.address
)
print(f'Hyperlinks: {hlink_count}')
```

## Font Theme Token Resolution (ZIP-level)

python-pptx sometimes leaves theme tokens (`+mn-ea`, `+mj-lt`) unresolved, causing font fallback. Fix via ZIP-level string replacement:

```python
import zipfile, re, shutil

FONT_JA = 'BIZ UDPゴシック'
FONT_LATIN = 'BIZ UDPGothic'

tmp = out + '.tmp'
shutil.copy2(out, tmp)
with zipfile.ZipFile(tmp, 'r') as zin:
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith('.xml'):
                content = data.decode('utf-8')
                content = content.replace('+mn-ea', FONT_JA)
                content = content.replace('+mj-ea', FONT_JA)
                content = content.replace('+mn-lt', FONT_LATIN)
                content = content.replace('+mj-lt', FONT_LATIN)
                content = re.sub(
                    r'(<a:ea typeface=")[^"]*(")',
                    f'\\g<1>{FONT_JA}\\2', content
                )
                data = content.encode('utf-8')
            zout.writestr(item, data)
os.remove(tmp)
```

> ⚠️ Always do this **after** `prs.save()`, not before.

## Section Management via XML

PowerPoint sections are stored as an extension in `ppt/presentation.xml`. python-pptx has no native section API.

### Adding/Updating Sections

```python
import re, uuid, zipfile

SECTION_URI = '{521415D9-36F7-43E2-AB2F-B90AF26B5E84}'
P14_NS = 'http://schemas.microsoft.com/office/powerpoint/2010/main'

# Read presentation.xml from ZIP
with zipfile.ZipFile(pptx_path) as z:
    pres_xml = z.read('ppt/presentation.xml').decode('utf-8')

# Ensure p14 namespace is declared
if f'xmlns:p14="{P14_NS}"' not in pres_xml:
    pres_xml = pres_xml.replace('<p:presentation',
        f'<p:presentation xmlns:p14="{P14_NS}"', 1)

# Extract slide IDs
slide_ids = re.findall(r'<p:sldId id="(\d+)"', pres_xml)

# Define sections: (name, start_slide_0based)
sections = [("表紙", 0), ("本編", 2), ("Appendix", 15)]

# Build section XML
section_parts = []
for idx, (name, start) in enumerate(sections):
    end = sections[idx+1][1] if idx+1 < len(sections) else len(slide_ids)
    refs = ''.join(f'<p14:sldId id="{slide_ids[i]}"/>'
                   for i in range(start, min(end, len(slide_ids))))
    sec_id = '{' + str(uuid.uuid4()).upper() + '}'
    section_parts.append(
        f'<p14:section name="{name}" id="{sec_id}">'
        f'<p14:sldIdLst>{refs}</p14:sldIdLst></p14:section>'
    )

# Insert into extLst
new_ext = (f'<p:ext uri="{SECTION_URI}">'
           f'<p14:sectionLst xmlns:p14="{P14_NS}">'
           + ''.join(section_parts)
           + '</p14:sectionLst></p:ext>')

# Write back to ZIP
```

### Important Notes

- The URI `{521415D9-36F7-43E2-AB2F-B90AF26B5E84}` is specific to the presenter's PowerPoint version; some versions use different URIs
- Always remove existing section XML before inserting new ones (avoid duplicates)
- Section changes only show in PowerPoint's slide sorter view after re-opening the file

## Post-Processing (URL Linkification)

> ⚠️ `create_from_template.py` does not process `footer_url`. Post-processing required.

### Items Requiring Post-Processing

| Item            | Processing                         |
| --------------- | ---------------------------------- |
| `footer_url`    | Add linked textbox at slide bottom |
| URLs in bullets | Convert to hyperlinks              |
| Reference URLs  | Linkify URLs in Appendix           |

### Save with Different Name (File Lock Workaround)

PowerPoint locks open files.同名保存は `PermissionError` になるため、必ず別名で保存：

```python
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
