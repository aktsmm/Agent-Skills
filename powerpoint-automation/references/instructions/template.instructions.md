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

### Deck vs Template Gate

Before authoring, distinguish the requested deliverable:

| User intent | Deliverable | Work to do |
| --- | --- | --- |
| "Create the next meeting deck" / "make slides from this content" | A populated presentation deck | Fill audience-ready slides from content and validate visuals |
| "Create a reusable template" / "make the slide master" | A template PPTX | Create/clean slide master and reusable custom layouts; sample slides are only previews |

Do not drift from deck creation into template authoring unless the user explicitly asks for a reusable template or slide master. Conversely, when the user asks for a template, do not stop at sample slides; verify the slide master and custom layouts are actually reusable.

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

If the user intends to reuse the same external template across follow-up updates, stage that PPTX in a stable template location (for example, an `assets/templates/` directory in the working project) and keep the analyzed `*_layouts.json` next to the staged copy. Reuse the staged copy and its cached layout mapping instead of repeatedly pointing at ad hoc original paths.

### Layout Detection Keywords

The analyzer detects layouts by name matching:

| Slide Type  | English Keywords            | Japanese Keywords                       |
| ----------- | --------------------------- | --------------------------------------- |
| **title**   | "Title Slide"               | "タイトル スライド", "タイトルスライド" |
| **content** | "Title and Content"         | "タイトルとコンテンツ"                  |
| **section** | "Section Header", "Divider" | "セクション見出し", "セクション"        |
| agenda      | "Agenda"                    | "アジェンダ"                            |
| closing     | "Closing"                   | -                                       |
| two_column  | "Two Column", "2 Column"    | "2列"                                   |
| code        | "Code", "Developer"         | -                                       |
| photo       | "Photo", "Picture", "50/50" | -                                       |
| blank       | "Blank"                     | "白紙"                                  |

### Placeholder Detection

Layouts are also detected by placeholder types:

| Placeholder | Type Constant           | Used For       |
| ----------- | ----------------------- | -------------- |
| Title       | `TITLE`, `CENTER_TITLE` | All layouts    |
| Subtitle    | `SUBTITLE`              | Title slide    |
| Body        | `BODY`                  | Content slides |
| Content     | `OBJECT`, `CONTENT`     | Two-column     |
| Picture     | `PICTURE`               | Photo layouts  |

### Cover Placeholder Fidelity Gate

When the user provides a template and expects the cover to use it, treat the
cover as a fidelity requirement, not just a visual background.

- Use the actual title/subtitle placeholders on the template cover whenever possible.
- Do not cover template placeholder text with opaque rectangles or independent text boxes.
- Preserve the template's background, whitespace, and master intent; only add overlays when the placeholder cannot be edited and the user accepts the tradeoff.
- After editing the cover, render slide 1 and check for leftover placeholder text, duplicated titles, covered template elements, and contrast problems.

Before adding any title text to the cover:

1. Inspect the actual cover slide placeholders with COM:
   - `slide.Shapes.Placeholders`
   - each placeholder's `Name`, `PlaceholderFormat.Type`, `Left`, `Top`,
     `Width`, `Height`, and current text
2. Fill the existing slide-level placeholders first. Typical cover placeholders
   are `Title 1` and `Text Placeholder 2` / body placeholder.
3. Preserve template font sizes and geometry unless the user explicitly asks for
   a redesign. Do not set arbitrary title sizes just because the text is longer.
4. Do not cover leftover placeholder text with a same-color rectangle, image, or
   new text box. If placeholder text remains visible, the placeholder was not
   correctly filled or removed.
5. Render the cover, then close and reopen the deck and render the cover again.
   A COM edit that appears correct before reopen can still be wrong if it
   touched a layout placeholder instead of the slide placeholder.

If `CustomLayout.Shapes` exposes placeholder text but changing it does not
appear on the slide, do not claim the template placeholder was filled. In many
legacy/OLE templates the editable placeholders are on `slide.Shapes`, while the
layout placeholders are only defaults. Fill the slide placeholders or reinsert
the original cover slide and fill its placeholders.

If a required subtitle/date does not fit the existing subtitle placeholder,
prefer shortening the visible subtitle and moving details to notes over adding
a second overlapping text box. Only add a normal text box when the user accepts
that it is no longer a pure placeholder-filled cover.

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

### Editing Slide Master with COM

Use this when the user asks to improve an existing reusable template or base slide master directly. This is different from polishing one populated deck: update `SlideMaster.CustomLayouts` and their placeholders so future decks inherit the change.

### Converting an Example Deck into a Reusable Template

When the source file is an example deck with real slides, first identify the **primary source layout** from the actual slides and the user's intent. Do not synthesize new "actual slide" layouts by copying every text box into fresh placeholders unless the user explicitly wants one new layout per slide.

Practical rules:

- Count actual slide usage by `Slide.CustomLayout.Design.Name` and `Slide.CustomLayout.Name`; the main template should preserve the heavily used layout, not replace it with a reconstructed lookalike.
- For product/service menu one-pagers, treat the original `1 Pager`-style custom layout as the master source of truth. Keep its geometry, fonts, footer, slide number, and inherited visuals; replace text in-place on sample slides for placeholder previews.
- If the user asks to "add slide masters from actual slides," interpret this as "promote reusable existing layouts and sample surfaces," not "create malformed placeholders over the visual design." Only duplicate a layout when a sample slide has a genuinely distinct reusable surface that is not already represented by an existing custom layout.
- Build a placeholder/sample set by duplicating the original sample slides that already use the target layout, then replacing their text with neutral prompts. This catches whether a new slide created from the layout still inherits the intended design.
- Include other reusable original layouts (for example agenda / two-content pages) as separate sample pages when they exist in the source, instead of forcing everything into the main one-pager layout.
- Before handoff, open the sample set and verify each sample slide still reports the intended `Design.Name` and `CustomLayout.Name`. A slide that visually degrades into generic bullets or floating blue placeholder squares fails the template conversion.

```python
import win32com.client

template = r"C:\path\to\template_master.pptx"
app = win32com.client.DispatchEx("PowerPoint.Application")
app.Visible = True
pres = app.Presentations.Open(template, False, False, False)

FONT_JA = "BIZ UDPゴシック"
FONT_LATIN = "BIZ UDPGothic"
ppAlignLeft = 1
ppAlignCenter = 2
msoAnchorTop = 1
msoAnchorMiddle = 3
msoTrue = -1

def set_text_defaults(shape, size=None, align=None, vertical=None):
    if not shape.HasTextFrame:
        return
    tr = shape.TextFrame.TextRange
    tr.Font.Name = FONT_JA
    tr.Font.NameFarEast = FONT_JA
    tr.Font.NameAscii = FONT_LATIN
    if size:
        tr.Font.Size = size
    if align:
        tr.ParagraphFormat.Alignment = align
    if vertical:
        shape.TextFrame.VerticalAnchor = vertical

for design in pres.Designs:
    master = design.SlideMaster
    for layout in master.CustomLayouts:
        for shape in layout.Shapes:
            try:
                ph_type = shape.PlaceholderFormat.Type if shape.Type == 14 else None
            except Exception:
                ph_type = None
            # Placeholder types: 1=Title, 2=Body, 4=Subtitle, 13=Slide number
            if ph_type == 1:
                set_text_defaults(shape, size=30, align=ppAlignLeft, vertical=msoAnchorMiddle)
            elif ph_type == 2:
                set_text_defaults(shape, size=16, align=ppAlignLeft, vertical=msoAnchorTop)
            elif ph_type == 4:
                set_text_defaults(shape, size=16, align=ppAlignLeft, vertical=msoAnchorMiddle)
            elif ph_type == 13:
                set_text_defaults(shape, size=10, align=ppAlignCenter, vertical=msoAnchorMiddle)

pres.Save()
pres.Close()
app.Quit()
```

Practical rules:

- Back up the template before COM edits; OneDrive/SharePoint templates may open with a URL-backed `FullName`.
- Edit `SlideMaster.CustomLayouts`, not only sample slides. Sample slides are previews; custom layouts are what future decks inherit.
- When turning existing sample slides into a reusable template, move reusable background art, logos, arcs, lines, and image placeholders into the custom layout. Leave content-specific screenshots/photos/text on the sample slide. A clean slide count is not enough if a blank slide created from the layout loses the design.
- Placeholder prompt text belongs on the layout/master, not as literal text on sample slides. After editing, scan actual slide XML/text for literals such as `<Title>`, `<Body>`, `<Subtitle>`, `Date`, and `Footer`; they should not appear as user-visible sample-slide text.
- If multiple sample slides share one source layout but have different visual surfaces, duplicate the layout first and assign one custom layout per distinct surface before moving art. Otherwise a closing/next-event/title design can overwrite another slide's inherited background.
- Add slide-number placeholders on non-cover layouts only. Do not leave a slide-number placeholder on the cover layout unless the user explicitly wants cover numbering.
- For Japanese templates, set `Name`, `NameFarEast`, and `NameAscii` together; visible sample text can look correct while layout defaults still inherit a different font.
- Keep body placeholders around 16pt by default. If a sample table needs more room, shorten text or rebalance columns/rows before shrinking below the readability target.
- After saving, create test slides from the edited layouts, not only the existing sample slides. Create those test slides inside the same presentation/copy that owns the layouts; passing `CustomLayout` objects across presentations can fail in COM. Verify title/body spacing, table readability, inherited background/images, slide numbers, and that no old placeholder text bleeds through.

### OneDrive / COM Safety for Template Masters

When a template lives in OneDrive or has been opened by the user, PowerPoint COM can silently save a `.pptx` path as a legacy/OLE body or trigger coauthoring conflict dialogs. Use this safer sequence for slide-master work:

1. Close the target presentation without saving, or work from a local temp copy.
2. Normalize the editable copy with `Presentation.SaveAs(path, 24)` only when the result is verified as a ZIP/OpenXML package.
3. Before package-level work, verify `zipfile.is_zipfile(path)` and the first bytes are `PK`; if the first bytes are `D0 CF 11 E0`, treat it as legacy/OLE and do not use `python-pptx` or ZIP edits on it.
4. Prefer OpenXML package edits for repetitive layout cleanup: duplicate layout parts, update slide layout relationships, move reusable art into `ppt/slideLayouts/*`, and update layout relationships for copied images.
5. Re-verify after every open/save cycle. PowerPoint may convert the file shape again after a read-only review or conflict resolution.
6. For final user review, open read-only copies when possible and do not save them. If PowerPoint changes timestamps or package format during review, restore from the last validated OpenXML artifact before continuing automation.

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
