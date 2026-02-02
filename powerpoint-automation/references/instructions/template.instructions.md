# Template Instructions

Template-based PPTX generation rules.

> ✅ **Recommended Method**: Create unified presentations quickly.

---

## Split Documents

| Document                                                                       | Content                                              |
| ------------------------------------------------------------------------------ | ---------------------------------------------------- |
| [template-content-json.instructions.md](template-content-json.instructions.md) | content.json format, slide types, image embedding    |
| [template-replacements.instructions.md](template-replacements.instructions.md) | replacements.json format (Localizer method)          |
| [template-advanced.instructions.md](template-advanced.instructions.md)         | analyze_template, diagnose, clean, master generation |

---

## Method Selection

| Method             | Purpose                                         | Recommended     |
| ------------------ | ----------------------------------------------- | --------------- |
| **New generation** | Create new PPTX from content.json with template | ⭐⭐⭐⭐⭐      |
| Localizer method   | Text replacement in existing template           | ⚠️ experimental |

> 📖 See [tools-reference.instructions.md](tools-reference.instructions.md) for method selection details.

---

## Quick Start (New Generation) ★ Recommended

```powershell
$template = "template"  # Filename in assets/ (no extension)
$base = "20241212_project_presentation"

# 1. Analyze layout if settings file doesn't exist (first time only)
if (-not (Test-Path "output_manifest/${template}_layouts.json")) {
    python scripts/analyze_template.py "assets/${template}.pptx"
}

# 2. Generate PPTX from content.json with template design
python scripts/create_from_template.py "assets/${template}.pptx" `
    "output_manifest/${base}_content.json" "output_ppt/${base}.pptx" `
    --config "output_manifest/${template}_layouts.json"

# 3. Verify
Start-Process "output_ppt/${base}.pptx"
```

---

## Basic Flow

### New Generation Method (content.json → PPTX)

```
assets/*.pptx
    ↓
analyze_template.py (layout analysis → layouts.json)
    ↓  ※first time only
output_manifest/{template}_layouts.json
    ↓
create_from_template.py --config
    ↓
output_ppt/{base}.pptx
```

### Localizer Method (Text Replacement) ※ experimental

```
assets/*.pptx
    ↓
reorder_slides.py (reorder/duplicate)
    ↓
extract_shapes.py (structure extraction → inventory.json)
    ↓
[Create replacements.json]
    ↓
apply_content.py (text replacement)
    ↓
output_ppt/{base}.pptx
```

> 📖 See [template-replacements.instructions.md](template-replacements.instructions.md) for details.

---

## content.json Quick Reference

```json
{
  "slides": [
    { "type": "title", "title": "Title", "subtitle": "Subtitle" },
    { "type": "agenda", "title": "Agenda", "items": ["Item 1", "Item 2"] },
    { "type": "content", "title": "Body", "items": ["Bullet 1", "Bullet 2"] },
    { "type": "section", "title": "Section", "subtitle": "Overview" },
    { "type": "summary", "title": "Summary", "items": ["Point 1", "Point 2"] },
    { "type": "closing", "title": "Thank You" }
  ]
}
```

> 📖 See [template-content-json.instructions.md](template-content-json.instructions.md) for complete format.

### Slide Type Quick Reference

| Type         | Purpose          | items      | Notes                 |
| ------------ | ---------------- | ---------- | --------------------- |
| `title`      | Title            | Usually no | First slide           |
| `agenda`     | Contents         | Yes        | After title           |
| `content`    | Body             | Yes        | Standard slide        |
| `section`    | Section divider  | Usually no | subtitle recommended  |
| `photo`      | With image       | Yes        | image field required  |
| `two_column` | 2-column compare | No         | left/right_items used |
| `summary`    | Summary          | Yes        | Before closing        |
| `closing`    | Ending           | **No**     | Short text only       |

---

## Image Embedding (Quick)

```json
{
  "type": "content",
  "title": "Architecture Diagram",
  "items": ["Point 1", "Point 2"],
  "image": {
    "path": "images/architecture.png",
    "position": "right",
    "width_percent": 45
  }
}
```

| position | Behavior              |
| -------- | --------------------- |
| `right`  | Right side, text left |
| `bottom` | Bottom, text above    |
| `center` | Center placement      |
| `full`   | Full screen (no text) |

> 📖 See [template-content-json.instructions.md](template-content-json.instructions.md) for details.

---

## Script List

| Script                    | Purpose              | Details                                                        |
| ------------------------- | -------------------- | -------------------------------------------------------------- |
| `analyze_template.py`     | Layout analysis      | [template-advanced](template-advanced.instructions.md)         |
| `create_from_template.py` | PPTX generation      | This file                                                      |
| `diagnose_template.py`    | Template diagnosis   | [template-advanced](template-advanced.instructions.md)         |
| `clean_template.py`       | Template cleaning    | [template-advanced](template-advanced.instructions.md)         |
| `reorder_slides.py`       | Slide reordering     | [template-replacements](template-replacements.instructions.md) |
| `extract_shapes.py`       | Structure extraction | [template-replacements](template-replacements.instructions.md) |
| `apply_content.py`        | Text replacement     | [template-replacements](template-replacements.instructions.md) |

---

## Template Preparation

### Auto-Template from User's PPTX

When bundled template is unavailable or corrupted, use any PPTX as template:

```powershell
# 1. Analyze user's PPTX → generates layouts.json automatically
python scripts/analyze_template.py "user_presentation.pptx"

# 2. Use analyzed PPTX as template
python scripts/create_from_template.py "user_presentation.pptx" `
    "output_manifest/content.json" "output_ppt/result.pptx" `
    --config "output_manifest/user_presentation_layouts.json"
```

### Layout Detection Keywords

The analyzer detects layouts by name matching:

| Slide Type | English Keywords | Japanese Keywords |
|------------|------------------|-------------------|
| **title** | "Title Slide" | "タイトル スライド", "タイトルスライド" |
| **content** | "Title and Content" | "タイトルとコンテンツ" |
| **section** | "Section Header", "Divider" | "セクション見出し", "セクション" |
| agenda | "Agenda" | "アジェンダ" |
| closing | "Closing" | - |
| two_column | "Two Column", "2 Column" | "2列" |
| code | "Code", "Developer" | - |
| photo | "Photo", "Picture", "50/50" | - |
| blank | "Blank" | "白紙" |

### Placeholder Detection

Layouts are also detected by placeholder types:

| Placeholder | Type Constant | Used For |
|-------------|---------------|----------|
| Title | `TITLE`, `CENTER_TITLE` | All layouts |
| Subtitle | `SUBTITLE` | Title slide |
| Body | `BODY` | Content slides |
| Content | `OBJECT`, `CONTENT` | Two-column |
| Picture | `PICTURE` | Photo layouts |

### Verification

```powershell
python scripts/analyze_template.py "your.pptx"
```

**Good output:**
```
📋 Recommended Layout Mapping:
  title           → [ 0] Title Slide
  content         → [ 1] Title and Content
  section         → [ 2] Section Header
```

**Warning signs:**
- `title → [0] Layout_0` (unnamed, may work but not optimal)
- All mappings pointing to same index (fallback used)

### Creating Optimal Template (PowerPoint)

If your PPTX lacks properly named layouts:

1. **Open PowerPoint** → View → Slide Master
2. **Rename existing layouts** to match keywords above:
   - First layout → "Title Slide" or "タイトル スライド"
   - Second layout → "Title and Content" or "タイトルとコンテンツ"
   - Add new layout → "Section Header" or "セクション見出し"
3. **Ensure placeholders exist**:
   - Title slide: TITLE + SUBTITLE
   - Content: TITLE + BODY
   - Section: TITLE only
4. **Close Slide Master** → Save
5. **Re-analyze**: `python scripts/analyze_template.py "updated.pptx"`

### Recommended Requirements

| Requirement      | Description                               |
| ---------------- | ----------------------------------------- |
| Size             | 16:9 (13.33" × 7.5") recommended          |
| Required layouts | Title Slide, Title and Content            |
| Recommended      | Section Header, Two Content, Blank        |
| Fonts            | Environment-independent (Arial, Segoe UI) |

---

## Common Errors

| Error                | Cause                                    | Solution              |
| -------------------- | ---------------------------------------- | --------------------- |
| Slide count mismatch | content.json slides vs template mismatch | Check layouts.json    |
| Image overlap        | Missing content_with_image mapping       | Add to layouts.json   |
| Text overflow        | Character count exceeded                 | Check char limits     |
| Background duplicate | Template not cleaned                     | Run clean_template.py |

---

## References

- Quality guidelines: [quality-guidelines.instructions.md](quality-guidelines.instructions.md)
- Naming rules: [common.instructions.md](common.instructions.md)
- Tool flow: [tools-reference.instructions.md](tools-reference.instructions.md)
- Sample: `schemas/content.example.json`
