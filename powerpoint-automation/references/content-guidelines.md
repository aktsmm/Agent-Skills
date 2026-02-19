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
