# Content Guidelines

Best practices for creating content.json files.

## URL Format (Required)

### Standard Format: "Title - URL"

Reference URLs in slides must follow this format:

```
{Document Title} - {URL}
```

#### Examples

```
VPN Gateway の新機能 - https://learn.microsoft.com/ja-jp/azure/vpn-gateway/whats-new
Basic IP 移行について - https://learn.microsoft.com/ja-jp/azure/vpn-gateway/basic-public-ip-migrate-about
```

### content.json Example

```json
{
  "type": "content",
  "title": "参考URL一覧",
  "bullets": [
    {
      "text": "VPN Gateway の新機能 - https://learn.microsoft.com/ja-jp/azure/vpn-gateway/whats-new",
      "level": 0
    },
    {
      "text": "Basic IP 移行について - https://learn.microsoft.com/ja-jp/azure/vpn-gateway/basic-public-ip-migrate-about",
      "level": 0
    }
  ]
}
```

### Why This Format?

| Aspect        | Benefit                                 |
| ------------- | --------------------------------------- |
| Readability   | Title provides context before URL       |
| Clickability  | URL is clearly separated and clickable  |
| Consistency   | Uniform style across all presentations  |
| Accessibility | Screen readers can announce title first |

### Anti-patterns (Avoid)

```
❌ https://learn.microsoft.com/... (URL only, no context)
❌ [VPN Gateway の新機能](https://...) (Markdown format doesn't render in PPTX)
❌ VPN Gateway の新機能 (https://...) (Parentheses break some URL parsers)
```

## Bullet Point Guidelines

### Hierarchy Levels

| Level | Use Case       | Example                  |
| ----- | -------------- | ------------------------ |
| 0     | Main points    | Key feature descriptions |
| 1     | Sub-points     | Details, examples        |
| 2     | Nested details | Rare, avoid if possible  |

### Example

```json
{
  "type": "content",
  "title": "Azure VPN Gateway Features",
  "bullets": [
    { "text": "High Availability", "level": 0 },
    { "text": "Active-active configuration", "level": 1 },
    { "text": "Zone-redundant gateways", "level": 1 },
    { "text": "Security", "level": 0 },
    { "text": "IPsec/IKE encryption", "level": 1 }
  ]
}
```

## Image References

### Local Images

```json
{
  "image": {
    "path": "images/architecture.png",
    "position": "right",
    "width_percent": 45
  }
}
```

### Remote Images

```json
{
  "image": {
    "url": "https://example.com/diagram.png",
    "position": "bottom",
    "height_percent": 50
  }
}
```

### Position Options

| Position | Description                  |
| -------- | ---------------------------- |
| `right`  | Image on right, text on left |
| `bottom` | Image below text             |
| `full`   | Full-slide image             |

## URL Priority (Japanese First)

| Priority | URL Format                             |
| -------- | -------------------------------------- |
| 1        | `/ja-jp/` Japanese version (if exists) |
| 2        | `/en-us/` English version (fallback)   |

## URL Hyperlink (Required)

> ⚠️ **Rule**: All URL strings in slides MUST have hyperlinks.

### Target Elements

| Location             | Hyperlink   |
| -------------------- | ----------- |
| `footer_url` field   | ✅ Required |
| URLs in bullets      | ✅ Required |
| Reference URL slides | ✅ Required |
| Appendix URLs        | ✅ Required |

### Link Style

| Attribute | Value                          |
| --------- | ------------------------------ |
| Color     | Blue (`RGBColor(0, 120, 212)`) |
| Underline | Yes                            |
| Hyperlink | Set to URL itself              |

### Anti-patterns

```
❌ Leave URL as plain text
❌ Keep link color as black
❌ URL without hyperlink setting
```

### Batch Hyperlink + Title Assignment

When a presentation has many URLs without hyperlinks, process all at once:

1. **Extract all URLs** from the PPTX using regex
2. **Fetch page titles** for each URL (use `fetch_webpage` or `microsoft_docs_search`)
3. **Build a URL→Title map** and iterate all runs to add hyperlinks + prepend titles

```python
# Step 1: Collect unique URLs
url_pattern = re.compile(r'(https?://[^\s\)）]+)')
all_urls = set()
for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    all_urls.update(url_pattern.findall(run.text))

# Step 2: Build title map (from MCP search results or manual)
URL_TITLES = {}  # populated from docs search

# Step 3: Apply hyperlinks + titles
for slide in prs.slides:
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                urls = url_pattern.findall(run.text)
                for url in urls:
                    url_clean = url.rstrip('/')
                    if not (run.hyperlink and run.hyperlink.address):
                        run.hyperlink.address = url_clean
                    title = URL_TITLES.get(url_clean)
                    if title and title not in run.text:
                        run.text = f'{title}\n{url_clean}'
```

### Verify Hyperlink Count

After processing, always verify:

```python
count = sum(1 for s in prs.slides for sh in s.shapes
            if sh.has_text_frame
            for p in sh.text_frame.paragraphs
            for r in p.runs
            if r.hyperlink and r.hyperlink.address)
print(f'Total hyperlinks: {count}')
```

## GitHub Commit History (Optional)

> Requires GitHub CLI (`gh`) to be installed.

For schedule/deadline information, fetch GitHub commit history:

```powershell
gh api "repos/MicrosoftDocs/azure-docs/commits?path=articles/{service}/{file}.md&per_page=5" \
  --jq '.[] | "\(.commit.author.date | split("T")[0]): \(.commit.message | split("\n")[0])"'
```

### Slide Format

```json
{
  "type": "content",
  "title": "Document Update History (GitHub)",
  "bullets": [
    { "text": "Recent changes to whats-new.md", "level": 0 },
    { "text": "2026-01-30: Active-Passive GA, deadline extended", "level": 1 },
    { "text": "Source: MicrosoftDocs/azure-docs", "level": 0 }
  ]
}
```

## Slide Numbers

### Enable in content.json

```json
{
  "title": "Presentation Title",
  "settings": {
    "slide_numbers": true,
    "date_footer": "2026-02-03"
  },
  "slides": [...]
}
```

> ⚠️ If slide numbers don't appear, enable them in the template via "Insert → Header and Footer".

## Base File Management (★★ Critical)

**Rule**: Always load the **latest user-modified file** as the base for script modifications. Never revert to an earlier version.

**Problem**: If the agent keeps using an old base file (e.g. `v3.pptx`) while the user manually edits later versions (e.g. `v11.pptx`), all manual edits are lost when the agent overwrites the output.

**Correct workflow**:

```
1. User provides initial PPTX → agent saves as working copy
2. Agent modifies → saves as vN.pptx → user reviews
3. User manually edits vN.pptx in PowerPoint → saves
4. Agent loads vN.pptx (NOT the original) → applies next fix → saves as vN+1.pptx
```

## COM Layout: Dynamic Sizing (sw/sh Based)

Fixed pixel values for left/width often overflow on 16:9 slides (sw=720, sh=450).
Always compute widths relative to slide dimensions.

### Anti-pattern

```python
# BAD: right edge = 500 + 420 = 920 > sw(720)
rect(slide, 500, 120, 420, 220, WHITE)
```

### Correct Pattern

```python
ml = 56       # left margin
mr = 48       # right margin
gap = 24
total_w = sw - ml - mr
card_w = (total_w - gap) / 2
left1 = ml
left2 = ml + card_w + gap
```

> Also applies to text width when images occupy part of the slide:
> `text_w = sw - left_margin - image_width - gap`

## Overlay Opacity for Text on Background Images

When placing text over a background image with a semi-transparent overlay:

| Overlay Alpha | Result |
|---|---|
| 0.50–0.60 | Background bleeds through, low contrast |
| **0.70–0.80** | **Recommended for body text** |
| 0.85+ | Background barely visible, may look flat |

- Use `alpha=0.75` as a starting point
- Sub-text (SKY/MUTED colors) needs higher alpha than white headings
- Always verify with a contrast checker

## Mascot / Illustration Placement Variety

Repeating the same character position on every slide looks monotonous.
Vary position and size per slide:

| Slide Purpose | Position | Size |
|---|---|---|
| Cover / Title | Bottom-right | Large (200+) |
| Content | Bottom-right or Top-right | Small (110–160) |
| Closing | Right-center or Center-bottom | Medium (170–200) |
| Appendix | Left side | Large (180+) |

> Always verify the image doesn't overlap text boxes
> (use the overlap detection pattern below).

## Operational Text Goes in Slide Notes

Instructions like 「FIXED」「REPLACE EACH EVENT」「差し替えてください」 must **not** appear on slide faces.
Use `set_notes()` (COM) or `slide.notes_slide.notes_text_frame` (python-pptx)
to store per-slide operational notes:

```python
# COM pattern
slide.NotesPage.Shapes.Placeholders(2).TextFrame.TextRange.Text = (
    "【運営ノート】\n"
    "■ 差し替え箇所: タイトル, 日付\n"
    "■ 固定要素: ブランド画像, 配色\n"
    "■ 進行メモ: 開場BGMを流しながら表示"
)
```

**Anti-pattern**:

```
❌ Always loading v3.pptx as base (ignores all manual edits after v3)
❌ Overwriting the working copy without checking if user modified a later version
```

**Implementation**: Before each script run, ask or detect which file is the latest:

```python
import glob, os
files = sorted(glob.glob('*_v*.pptx'), key=os.path.getmtime, reverse=True)
latest = files[0]  # Use this as base
```

**PowerPoint Sections**: 「セクション」（左ペインの区切り）はPowerPoint独自メタデータ。

- XML直編集は無視されることがあるため、基本はPowerPoint上で追加/編集して確認
- 自動化する場合も「ファイル内でPowerPointが使っているURI」に合わせる（環境差あり）

---

## Run-Level Text Editing (★ Important)

**Problem**: `shape.text_frame` or `paragraph.text` stores text split across multiple "runs" (formatting segments). A simple `replace()` on paragraph text may fail because the target string is split across runs.

**Example**: The text "Active-Active" might be stored as:

```
Run 0: "Active-Acti"
Run 1: "ve"
```

### Correct Approach

1. **Reconstruct full text** by joining all runs: `full = ''.join(r.text for r in para.runs)`
2. **Search in full text**, then **modify individual runs**
3. **Clear extra runs** by setting `run.text = ""`

```python
# ❌ NG: paragraph-level replace (fails on split runs)
for para in tf.paragraphs:
    if old_text in para.text:
        para.text = para.text.replace(old_text, new_text)  # Loses formatting!

# ✅ OK: run-level editing (preserves formatting)
for para in tf.paragraphs:
    full = ''.join(r.text for r in para.runs)
    if old_text in full:
        para.runs[0].text = new_text
        for r in para.runs[1:]:
            r.text = ""
```

### Best Practice: Use Script Files

Inline Python in terminal commands has escaping issues. Always write `.py` files:

```python
# ❌ NG: Inline Python with f-string escaping issues
python -c "print(f'{\"|\".join(items)}')"

# ✅ OK: Write to .py file and execute
python fix_script.py
```

## Factual Accuracy in Technical Content (★ Important)

**Rule**: Do not rephrase technical documentation in a way that changes the meaning. When the original source uses cautious language ("will be available", "anticipated"), preserve that nuance.

| Original Expression             | ❌ NG Interpretation | ✅ OK Interpretation                     |
| ------------------------------- | -------------------- | ---------------------------------------- |
| "will be available March'2026"  | 3月に自動対応        | 3月に自動化機能がリリース予定            |
| "anticipated timelines"         | 確定スケジュール     | 予定（変更の可能性あり）                 |
| "customer-controlled migration" | 自動移行             | お客様操作による移行                     |
| "no action required"            | 完全放置でOK         | お客様操作は不要（スクリプト更新は必要） |

### When in Doubt

1. **Quote the original text** (italic, gray, small font) on the slide
2. **Add "詳細はSRにて"** for items where the exact customer action is unclear
3. **Never assert certainty** when the source says "予定" / "anticipated"

## Layout & Visibility (COM Automation)

COM Automation (`win32com`) でスライドを組むときのレイアウト・視認性ルール。

### Dynamic Sizing — sw/sh ベースで計算する

固定値 (`left=500`, `width=420` 等) はスライドサイズ次第ではみ出す。
`sw` (SlideWidth) と `sh` (SlideHeight) から動的に計算する。

```python
# NG: 固定値 → sw=720 で right=920 にはみ出す
rect(slide, 500, 120, 420, 220, WHITE)

# OK: sw から逆算して右マージン 48pt を確保
card_w = (sw - margin_left - margin_right - gap) / 2
rect(slide, left, 120, card_w, 220, WHITE)
```

### Mascot / Character Placement

全スライドで同じ位置に配置すると単調になる。スライドの役割に応じて位置・サイズを変える。

| スライド種別 | 配置例 | サイズ目安 |
|---|---|---|
| 表紙 | 右下 | 200-220 |
| 情報パネル | 左中央 or 右下 | 150-180 |
| クロージング | 右上 or 中央下 | 180-200 |
| カード 2 列 | 右上（小） or 右下（小） | 100-120 |
| 宣伝 (Appendix) | 左中央（QR の隣など） | 80-100 |

### Overlay Opacity for Background Images

背景画像の上にテキストを載せるとき、半透明オーバーレイが薄いとテキストが溶ける。

| 用途 | 推奨 alpha | 備考 |
|---|---|---|
| タイトル（大きい白文字） | 0.55-0.65 | 44pt+ なら多少薄くても読める |
| 本文・案内テキスト | **0.70-0.80** | 16-18pt で視認性を確保 |
| 小さい補足テキスト | **0.75+** | 13pt は特に注意 |

### Operational Text → Slide Notes

「差し替えてください」「REPLACE EACH EVENT」等の運営向け説明テキストはスライド本文に置かない。
投影で映えるデザインだけをスライド面に残し、運営情報は `slide.NotesPage` に書く。

```python
def set_notes(slide, text):
    slide.NotesPage.Shapes.Placeholders(2).TextFrame.TextRange.Text = text

set_notes(slide, (
    "【運営ノート】\n"
    "■ 差し替え箇所\n"
    "  ・タイトル → 回番号に変更\n"
    "■ 進行メモ\n"
    "  ・BGM を流しながら表示"
))
```

### Automated Quality Checks (Done Criteria)

生成後に以下を自動検証する:

1. **はみ出し検出**: `shape.Left + shape.Width > sw` or `shape.Top + shape.Height > sh`
2. **重なり検出**: 画像の矩形とテキストの矩形が 5% 以上重複
3. **視認性検出**:
   - フォントサイズ < 13pt → NG
   - WCAG コントラスト比 < 3.0:1 → NG
   - コントラスト比 < 4.5:1 かつ フォントサイズ < 18pt → 警告
