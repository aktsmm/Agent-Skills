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

### XML Direct Hyperlink Insertion (L16)

> `run.hyperlink.address` が機能しない場合（既存 PPTX のレイアウト変更後など）、
> XML 要素 `a:hlinkClick` を直接挿入する方が確実。

```python
from lxml import etree
from pptx.oxml.ns import qn
from pptx.dml.color import RGBColor
import re

url_pattern = re.compile(r'(https?://[^\s\)）」、。]+)')

for slide in prs.slides:
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                if run._r.find(qn('a:hlinkClick')) is not None:
                    continue  # Already has link
                urls = url_pattern.findall(run.text)
                for url in urls:
                    url_clean = url.rstrip('.,;:')
                    # Add external relationship
                    rel = slide.part.relate_to(
                        url_clean,
                        'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',
                        is_external=True)
                    # Get or create rPr element
                    rPr = run._r.find(qn('a:rPr'))
                    if rPr is None:
                        rPr = etree.SubElement(run._r, qn('a:rPr'))
                        t_elem = run._r.find(qn('a:t'))
                        if t_elem is not None:
                            run._r.remove(rPr)
                            run._r.insert(0, rPr)
                    # Add hlinkClick
                    hlinkClick = etree.SubElement(rPr, qn('a:hlinkClick'))
                    hlinkClick.set(qn('r:id'), rel)
                    # Visual styling
                    run.font.underline = True
                    run.font.color.rgb = RGBColor(0x00, 0x78, 0xD4)
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

### Slide Layout Change (Safe Pattern)

python-pptx does NOT safely support direct layout swapping. Use the **add-move-hide-cleanup** pattern:

1. `add_slide(target_layout)` — new slide at the end
2. Set title text on the new slide's placeholder (`placeholder_format.idx == 0`)
3. Move new slide to old slide's position via `sldIdLst` XML manipulation (reverse order)
4. Hide & clear old slide (`show='0'`, remove shapes)
5. Save, re-open, delete hidden slides in a **separate pass**

```python
# Step 3: Move new slide (last) before old slide
sldIdLst = prs.part._element.find(qn('p:sldIdLst'))
slides_list = list(sldIdLst)
new_el = slides_list[-1]
old_el = list(sldIdLst)[target_idx]
sldIdLst.remove(new_el)
sldIdLst.insert(list(sldIdLst).index(old_el), new_el)

# Step 4: Hide old slide (now at target_idx + 1)
old_slide._element.set('show', '0')
for shape in list(old_slide.shapes):
    shape._element.getparent().remove(shape._element)
```

### Forbidden Patterns (★ Critical)

| Pattern | Problem | Result |
|---------|---------|--------|
| `rel._target = new_layout.part` **without ZIP dedup** | Duplicate ZIP entries corrupt layout | PowerPoint repair dialog |
| `prs.part.drop_rel(rId)` for slide deletion | Orphan XML in ZIP | `Duplicate name` warning → corruption |
| `show='0'` while indices shift | Wrong slides hidden | Content silently disappears |
| Changing layout but keeping empty placeholders | Ghost text ("テキストを入力") visible | Unprofessional appearance |

### Layout Change via `rel._target` (Safe Pattern with ZIP Dedup)

> **L12**: `rel._target` 方式は ZIP dedup（LAST 優先）を併用すれば安全に動作する。
> python-pptx の `save()` が重複エントリを生むが、後処理で解決可能。

```python
from collections import Counter
import zipfile

# 1. Change layout relationship
blank_part = layout_parts['Blank']
for rel in slide.part.rels.values():
    if 'slideLayout' in rel.reltype:
        rel._target = blank_part
        break

# 2. Save (will have duplicate ZIP entries)
prs.save(raw_path)

# 3. Dedup ZIP: keep LAST entry for duplicates (has updated rels)
with zipfile.ZipFile(raw_path, 'r') as zin:
    items = zin.infolist()
    counts = Counter(i.filename for i in items)
    dups = {n for n, c in counts.items() if c > 1}
    last_idx = {}
    for idx, item in enumerate(items):
        if item.filename in dups:
            last_idx[item.filename] = idx
    seen = set()
    with zipfile.ZipFile(final_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for idx, item in enumerate(items):
            if item.filename in dups:
                if idx == last_idx[item.filename]:
                    zout.writestr(item, zin.read(item.filename))
            elif item.filename not in seen:
                seen.add(item.filename)
                zout.writestr(item, zin.read(item.filename))
```

> ⚠️ FIRST 優先だと変更前の rels XML が残り、レイアウト変更が反映されない。必ず **LAST 優先**。

### Ghost Placeholder Elimination

> **L13**: 既存 PPTX にスライドを追加する際、`Title and Content` や `Section Title` レイアウトを使うと
> 空のプレースホルダー（「テキストを入力」「タイトルを入力」）がゴースト表示される。

**解決策**: 新規スライドは `Blank` レイアウトを使い、タイトルは既存プレースホルダーに値を入れるか手動配置する。

```python
# Strategy: Fill placeholder with actual title, remove empty ones
ns_p = '{http://schemas.openxmlformats.org/presentationml/2006/main}'

for shape in slide.shapes:
    ph_elem = shape._element.find(f'.//{ns_p}ph')
    if ph_elem is None:
        continue
    ph_type = ph_elem.get('type', 'body')
    if ph_type == 'title' and not shape.text_frame.text.strip():
        # Fill with actual title text
        shape.text_frame.text = slide_title
        for run in shape.text_frame.paragraphs[0].runs:
            run.font.size = Pt(28)
            run.font.bold = True
    elif not shape.text_frame.text.strip():
        # Remove empty placeholder
        shape._element.getparent().remove(shape._element)
```

### Consistent Title Positioning (Cross-slide Alignment)

> **L14**: 新規追加スライドのタイトル位置を既存スライドと揃えるには、
> 基準スライドの位置を計測して全スライドに適用する。

```python
# 1. Measure reference slide (e.g., slide 4)
ref_slide = prs.slides[3]
for shape in ref_slide.shapes:
    ph = shape._element.find(f'.//{ns_p}ph')
    if ph is not None and ph.get('type') == 'title':
        REF_LEFT = shape.left      # 588263
        REF_TOP = shape.top        # 457200
        REF_WIDTH = shape.width    # 11018520
        REF_HEIGHT = shape.height  # 553998
        break

# 2. Apply to all new slides
for slide in new_slides:
    title_ph.left = REF_LEFT
    title_ph.top = REF_TOP
    title_ph.width = REF_WIDTH
    title_ph.height = REF_HEIGHT
```

### Preserving Original Layouts When Modifying Existing PPTX

> **L15**: 既存 PPTX を再構成する際、オリジナルスライドのレイアウトを保持するには
> タイトルテキストをキーにしたマッピングを作成する。

```python
# Build original layout map
prs_orig = Presentation('original.pptx')
orig_layouts = {}
for slide in prs_orig.slides:
    for shape in slide.shapes:
        if shape.has_text_frame and shape.text_frame.text.strip():
            title = shape.text_frame.text.replace('\n', ' ')[:50]
            orig_layouts[title] = slide.slide_layout.name
            break

# Apply: ORIG slides keep original layout, NEW slides use Blank
for slide in prs_edit.slides:
    title = get_slide_title(slide)
    if title in orig_layouts:
        restore_layout(slide, orig_layouts[title])
    else:
        set_layout(slide, 'Blank')
```

### Safe Hidden Slide Cleanup

Delete hidden slides in a **separate script/pass** after saving, in **reverse index order**:

```python
# Cleanup pass (separate from insertion)
prs = Presentation(saved_file)
sldIdLst = prs.part._element.find(qn('p:sldIdLst'))

for i, slide in enumerate(prs.slides):
    if slide._element.get('show') == '0':
        # Verify truly empty before deleting
        has_content = any(
            para.text.strip()
            for shape in slide.shapes if shape.has_text_frame
            for para in shape.text_frame.paragraphs
        )
        if has_content:
            del slide._element.attrib['show']  # Restore, not delete

# Delete empty hidden slides (reverse order)
for idx in reversed(empty_hidden_indices):
    el = list(sldIdLst)[idx]
    rId = el.get(qn('r:id'))
    sldIdLst.remove(el)
    prs.part.drop_rel(rId)

prs.save(output_new_name)  # Always save to NEW filename
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

PowerPoint locks open files.同名保存は `PermissionError` になるため、必ず別名で保存：

```python
prs.save('file_withURL.pptx')
```

| Processing    | Suffix     |
| ------------- | ---------- |
| URL added     | `_withURL` |
| Final version | `_final`   |
| Fixed version | `_fixed`   |

## 16:9 Slide Centering (Known Issue)

> **L9**: `Presentation()` のデフォルトプレースホルダは 4:3 (25.4cm) 基準。
> `slide_width = Cm(33.867)` で 16:9 に変更しても **プレースホルダ位置は 4:3 のまま** → 全スライドが左寄りに表示される。

### 推奨パターン: Blank + 手動配置

```python
prs = Presentation()
prs.slide_width = Cm(33.867)  # 16:9
prs.slide_height = Cm(19.05)
SW = prs.slide_width

# Blank layout (プレースホルダなし) を使う
slide = prs.slides.add_slide(prs.slide_layouts[6])

# SW 基準で中央配置
margin = Cm(3)
tb = slide.shapes.add_textbox(margin, Cm(5), SW - margin * 2, Cm(3))
p = tb.text_frame.paragraphs[0]
p.text = "Centered Title"
p.alignment = PP_ALIGN.CENTER
```

### Anti-patterns

```
❌ Layout 0-5 を 16:9 スライドで使う（プレースホルダが 25.4cm 基準で左寄り）
❌ slide_width 変更後にプレースホルダ位置を未調整のまま使う
✅ Blank レイアウト + add_textbox() で SW 基準の対称マージン配置
✅ テンプレート PPTX 自体が 16:9 で作成されていれば Layout 0-5 も OK
```

## Template Corruption Recovery

> **L10**: `.gitattributes` の `*.pptx binary` が git add **後** に追加された場合、
> CRLF/エンコーディング変換でバイナリが破壊される（UTF-8 replacement char `EF BF BD` が混入）。

### 診断方法

```python
with open('template.pptx', 'rb') as f:
    data = f.read()
count = data.count(b'\xef\xbf\xbd')
print(f'UTF-8 replacement chars: {count}')  # 0 以外なら破損
```

### 復旧方法

```python
# python-pptx で空テンプレートを再生成
from pptx import Presentation
prs = Presentation()
prs.slide_width = Cm(33.867)  # 16:9
prs.slide_height = Cm(19.05)
prs.save('template_new.pptx')
# → 11 layouts が自動生成される（4:3 プレースホルダ注意）
```

### 予防策

- `.gitattributes` は **最初のコミット前** に設定する
- skill-ninja 等の自動インストーラ経由の場合、`.gitignore` による除外とバイナリ管理の整合性を確認

## Video Embedding (ZIP Direct Manipulation)

> **L11**: python-pptx は公式に MP4 埋め込み非対応。
> しかし PPTX は ZIP なので `lxml` + `zipfile` で直接操作すれば埋め込み可能。

### 必要な操作

1. **slide XML**: `p:pic` に `a:videoFile` + `p14:media` を注入
2. **slide rels**: video/image リレーションシップを追加 (rId)
3. **[Content_Types].xml**: `<Default Extension="mp4" ContentType="video/mp4"/>` を追加
4. **ZIP**: `ppt/media/` に MP4 ファイルとポスター画像を格納

### XML パターン

```xml
<p:pic>
  <p:nvPicPr>
    <p:cNvPr id="100" name="Video 1">
      <a:hlinkClick r:id="" action="ppaction://media"/>
    </p:cNvPr>
    <p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>
    <p:nvPr>
      <a:videoFile r:link="rId10"/>
      <p:extLst>
        <p:ext uri="{DAA4B4D4-6D71-4841-9C94-3DE7FCFB9230}">
          <p14:media r:embed="rId11"/>
        </p:ext>
      </p:extLst>
    </p:nvPr>
  </p:nvPicPr>
  <p:blipFill>
    <a:blip r:embed="rId12"/>  <!-- poster image -->
    <a:stretch><a:fillRect/></a:stretch>
  </p:blipFill>
  <p:spPr>
    <a:xfrm>
      <a:off x="720000" y="1260000"/>
      <a:ext cx="10752120" cy="5058000"/>
    </a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
  </p:spPr>
</p:pic>
```

### Slide Rels (3 リレーションシップ必要)

```xml
<Relationship Id="rId10" Type=".../relationships/video"
              Target="../media/video.mp4" TargetMode="Internal"/>
<Relationship Id="rId11" Type=".../2007/relationships/media"
              Target="../media/video.mp4"/>
<Relationship Id="rId12" Type=".../relationships/image"
              Target="../media/poster.png"/>
```

### 注意事項

- PowerPoint が「修復しますか？」と聞く場合がある（軽微な XML 不整合） → 「はい」で自動修復される
- ポスター画像は必須（表示用サムネイル）
- ファイルサイズ注意: 動画を ZIP 圧縮すると PPTX が肥大化。Git 管理には LFS 推奨

## XML Serialization Artifacts (★ Critical)

> **L17**: python-pptx の `save()` は全 XML を再シリアライズする。
> その際 `"` → `'`（属性クォート）、`\r\n` → `\n`（改行）に変換される。
> これだけでレイアウト背景（画像 blipFill）の描画が壊れ、スライドが**真っ白**になることがある。

### 原因

- スライドマスター/レイアウトの `<p:bg>` が `<a:blipFill r:embed="rId2">` で背景画像を参照
- python-pptx がレイアウト XML を再シリアライズ → PowerPoint が微妙な差異を嫌い背景を表示しない

### 解決策: ZIP 再構築パターン（原本復元）

python-pptx でスライド内容を編集した後、レイアウト/マスター/テーマ/メディアファイルは**オリジナル PPTX からバイト単位で復元**する。

```python
import zipfile
from collections import Counter

orig_files = {}
with zipfile.ZipFile('original.pptx', 'r') as z:
    for item in z.infolist():
        fn = item.filename
        if any(p in fn for p in ['slideLayout', 'slideMaster', 'theme', '/media/']):
            orig_files[fn] = z.read(fn)

with zipfile.ZipFile('edited.pptx', 'r') as zin:
    with zipfile.ZipFile('output.pptx', 'w', zipfile.ZIP_DEFLATED) as zout:
        seen = set()
        for item in zin.infolist():
            fn = item.filename
            if fn in seen:
                continue
            seen.add(fn)
            if fn in orig_files:
                zout.writestr(item, orig_files[fn])  # byte-for-byte original
            else:
                zout.writestr(item, zin.read(fn))
        for fn, data in orig_files.items():
            if fn not in seen:
                zout.writestr(fn, data)
                seen.add(fn)
```

### SVG Content Type 欠落 (L18)

> python-pptx は `[Content_Types].xml` から SVG エントリを落とすことがある。
> テーマ/マスターが SVG を参照している場合、表示が壊れる。

```python
ct_data = z.read('[Content_Types].xml').decode('utf-8')
if 'image/svg+xml' not in ct_data:
    ct_data = ct_data.replace(
        '</Types>',
        '<Default Extension="svg" ContentType="image/svg+xml"/></Types>'
    )
```

### 安全な TextBox コンテンツ置換 (L19)

> `text_frame.clear()` は python-pptx 内部の段落リストとの不整合を起こすことがある。
> 代わりに `txBody` の `<a:p>` 要素を直接操作する。

```python
from lxml import etree
from pptx.oxml.ns import qn

def set_textbox_content(shape, lines):
    """Safe textbox rewrite via XML manipulation.
    lines: list of (text, bold, size_pt) tuples.
    """
    txBody = shape._element.find(qn('p:txBody'))
    if txBody is None:
        txBody = shape._element.find(qn('a:txBody'))
    
    # Remove existing paragraphs
    for old_p in txBody.findall(qn('a:p')):
        txBody.remove(old_p)
    
    # Add new paragraphs
    for text, bold, size in lines:
        p = etree.SubElement(txBody, qn('a:p'))
        r = etree.SubElement(p, qn('a:r'))
        rPr = etree.SubElement(r, qn('a:rPr'))
        rPr.set('lang', 'ja-JP')
        rPr.set('sz', str(int(size * 100)))
        if bold:
            rPr.set('b', '1')
        solidFill = etree.SubElement(rPr, qn('a:solidFill'))
        srgbClr = etree.SubElement(solidFill, qn('a:srgbClr'))
        srgbClr.set('val', '333333')
        t = etree.SubElement(r, qn('a:t'))
        t.text = text
```

### 推奨ワークフロー（既存 PPTX 編集時）

```
1. python-pptx でスライド内容 (sp, txBody) を編集
2. prs.save('raw.pptx')
3. ZIP 再構築: layout/master/theme/media を原本から復元
4. [Content_Types].xml で SVG 等の欠落を補完
5. ZIP dedup (LAST 優先) で重複エントリを除去
6. output.pptx を別名で保存
```

## Done Criteria

- [ ] `content.json` generated and validated
- [ ] PPTX file created successfully
- [ ] No text overflow detected
- [ ] User confirmed output quality
