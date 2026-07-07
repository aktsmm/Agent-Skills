# Common Instructions

Rules common to all agents and methods.

> **Single Source of Truth**: This file is the definition source for common rules. Other files reference only.

---

## Design Principles

### Dynamic Context

Do not hardcode output (template) characteristics. Retrieve at processing start and propagate to all steps.

```python
# ❌ NG: Hardcoded
slide_width = 13.333  # Assumes standard size only

# ✅ OK: Dynamic retrieval
slide_width = prs.slide_width.inches  # Works with any template
```

### Complete Extraction

When extracting from web sources, explicitly list and retrieve all these elements:

| Element     | Retrieval Method        | Storage                      |
| ----------- | ----------------------- | ---------------------------- |
| Title       | `<title>` or `<h1>`     | `metadata.title`             |
| Body text   | `<article>` or `<main>` | `slides[].items`             |
| Image URLs  | `<img src>`             | Download to `images/{base}/` |
| Code blocks | `<pre><code>`           | `slides[].code`              |
| Metadata    | `<meta>` tags           | `metadata.*`                 |

---

## File Naming Convention

### Common Format

```
{YYYYMMDD}_{keyword}_{purpose}.{ext}
```

| Element    | Description                        | Example                            |
| ---------- | ---------------------------------- | ---------------------------------- |
| `YYYYMMDD` | Generation date (required)         | `20241211`                         |
| `keyword`  | English keyword describing content | `q3_sales`, `git_cleanup`          |
| `purpose`  | Purpose                            | `report`, `lt`, `incident`, `blog` |
| `ext`      | Extension                          | `pptx`, `json`                     |

### File Types and Output Paths

| File Type          | Output Path        | Filename Pattern            |
| ------------------ | ------------------ | --------------------------- |
| **Final PPTX**     | `output_ppt/`      | `{base}.pptx`               |
| Working PPTX       | `output_manifest/` | `{base}_working.pptx`       |
| Diagram PPTX       | `output_manifest/` | `{base}_diagrams.pptx`      |
| Insert config JSON | `output_manifest/` | `{base}_insert_config.json` |
| Inventory          | `output_manifest/` | `{base}_inventory.json`     |
| Replacements       | `output_manifest/` | `{base}_replacements.json`  |

※ `{base}` = `{YYYYMMDD}_{keyword}_{purpose}`

---

## Bullet Point Format

> **⚠️ Critical Rule**: Manual bullet characters are prohibited. Always use structured format.

### Prohibited Characters (at start of text)

`•` `・` `●` `○` `-` `*` `+`

---

## 🚨 IR Schema Usage (★ Important)

**Two different JSON formats exist. Do not confuse them.**

| Format                | Usage                          | Schema                        | items Type         |
| --------------------- | ------------------------------ | ----------------------------- | ------------------ |
| **content.json**      | reconstruct / summarize        | `schemas/content.schema.json` | `string[]`         |
| **replacements.json** | preserve method (experimental) | None (deprecated)             | `{text, bullet}[]` |

```json
// ✅ content.json: String array
{ "items": ["Item 1", "Item 2"] }

// ❌ Schema error (validate_content.py detects)
{ "items": [{"text": "Item 1", "bullet": true}] }
```

---

## Output Path Rules

| Type         | Path               | Purpose                    |
| ------------ | ------------------ | -------------------------- |
| Final output | `output_ppt/`      | Completed PPTX             |
| Intermediate | `output_manifest/` | Working files, JSON, etc.  |
| Templates    | `templates/`       | Template files (read-only) |

### Prohibited Actions

- ❌ Overwriting template files
- ❌ Output outside designated folders
- ❌ Direct PPTX binary editing

---

## Content Creation Principles

### 🎯 "Communicate" is Justice

> Slides are for "viewing" not "reading".

- **1 slide = 1 message**
- **Conclusion first**: Always think "So what?"
- **Slide count depends on content**: If it communicates, it's correct
- **Appendix is for "details here"**

### Common Mistakes and Solutions

| Mistake             | Solution                        |
| ------------------- | ------------------------------- |
| Too much on 1 slide | Split or move to Appendix       |
| Over-summarized     | Keep 1 concrete example         |
| Omitted all code    | Put working sample in Appendix  |
| Forgot citation     | Always include URL if available |
| Inconsistent tone   | Maintain initial tone           |

---

## Emoji Usage (★ Important)

**Emoji is prohibited in PPTX slides.**

| Location      | Emoji | Reason                          |
| ------------- | ----- | ------------------------------- |
| Slide title   | ❌    | Font compatibility issues       |
| Bullet items  | ❌    | May not render correctly        |
| Speaker notes | ⚠️ OK | Internal use, not shown to audience |

### Why No Emoji?

- PowerPoint fonts may not support all emoji
- Different OS versions render emoji differently
- Professional presentations should avoid emoji
- Use icons from template instead

---

## python-pptx Placeholder Manipulation Rules

### Placeholder idx Varies per Template — Inspect First

Custom templates do **not** always use the standard `idx=0` (title) / `idx=1` (body) mapping. Some templates assign `idx=10` / `11` / other numbers per layout, or move the title into a non-placeholder text box entirely. Hard-coding `idx=0` for title will silently write into a wrong shape (subtitle, footer, image caption).

Before any idx-based placeholder code, run `scripts/analyze_template.py <template.pptx>` and confirm the actual `idx / type / name` per layout. If a layout has no `idx=0`, either use the correct idx from the analyzer output, or add a plain text box at a fixed position instead of relying on a placeholder.

Applies to: hand-rolled generators, `apply_content.py` custom mappings, and any inherited-value pattern like the xfrm 4-attribute rule below.

### Master / Layout Decorations Are Not Placeholders — Do Not Delete

Custom templates often include intentional **decorative shapes** on the Slide Master or SlideLayout (color bands, side rails, empty boxes, accent stripes). These are regular shapes with `is_placeholder=False`, inherited into every slide. They look "empty" but are part of the design language — never strip them just because they seem redundant.

Before writing a "clean up empty shapes" helper, classify each shape:

- Appears in `slide.slide_layout.shapes` (same name/position) → **Layout decoration**, keep
- Appears in `slide.slide_layout.slide_master.shapes` → **Master decoration**, keep
- Not in either → slide-owned shape (candidate for removal)

Any `strip_empty_placeholders(slide, ...)` helper must filter on `is_placeholder=True` and additionally on `placeholder_format.idx`. Never iterate over all `slide.shapes` blindly to remove empty ones.

### strip_empty_placeholders: `keep_idx` should still drop when empty

When you hand-roll all body content via `add_textbox()` (not via placeholder insertion), the layout's body/subtitle placeholders (typically `idx=11` on custom templates) stay behind on every slide as visible empty rectangles. A naive `keep_idx=(10, 11)` will protect these empties and leave them floating.

**Correct policy**: `keep_idx` guards against structural removal, but a placeholder with empty `text_frame.text.strip()` should still be dropped. This lets the same helper handle both:

- Cover slide: subtitle written into `idx=11` → text present → kept
- Body slides: nothing written into `idx=11` → text empty → dropped

```python
def strip_empty_placeholders(slide, keep_idx=(10,)):
    for shape in list(slide.shapes):
        if not shape.is_placeholder:
            continue
        idx = shape.placeholder_format.idx
        # keep if in keep list AND has content
        if idx in keep_idx and shape.has_text_frame and shape.text_frame.text.strip():
            continue
        # otherwise: drop empty placeholders regardless of keep_idx
        if shape.has_text_frame and not shape.text_frame.text.strip():
            sp = shape._element
            sp.getparent().remove(sp)
```

Default `keep_idx=(10,)` protects the title. Everything else auto-classifies: written = kept, empty = removed. No per-slide branching needed.

Verification: after build, count `[sh for sh in s.shapes if sh.is_placeholder and sh.has_text_frame and not sh.text_frame.text.strip()]` should equal 0 across all slides.

### Placeholder Font Size: `clear()` + `add_run()` is required

Assigning `text_frame.text = "..."` to a placeholder does **not** reset the inherited font size from the slide layout / master. Iterating `text_frame.paragraphs → paragraph.runs` and setting `run.font.size = Pt(N)` afterward often has no visible effect for the subtitle / body placeholder, because python-pptx keeps the layout-owned run's rPr in some templates.

**Correct pattern for cover subtitle or any placeholder where explicit font size is required**:

```python
tf = shape.text_frame
tf.clear()  # remove inherited runs
for i, (txt, size, bold) in enumerate(lines):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    r = p.add_run()
    r.text = txt
    r.font.name = FONT_JA
    r.font.size = Pt(size)
    r.font.bold = bold
```

Symptom of the bug: cover subtitle renders at ~12pt even when the code sets `Pt(20)`. Cause: the shape still has the layout's original run with its own rPr, and the new setter appends without overriding.

### MSO_AUTO_SIZE enum: only `NONE` / `SHAPE_TO_FIT_TEXT` are supported

python-pptx が公開している `MSO_AUTO_SIZE` は **`NONE` と `SHAPE_TO_FIT_TEXT`** の 2 値のみ。PowerPoint COM 由来の名前 `TEXT_TO_SHAPE_ON_OVERFLOW` (テキストを枠に合わせて縮小) は **存在しない**。誤って使うと `AttributeError: type object 'MSO_AUTO_SIZE' has no attribute 'TEXT_TO_SHAPE_ON_OVERFLOW'` で build 失敗。

使い分け:

- `tf.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT`: 枠の height を text 量に合わせて伸ばす。テキスト増減が読めない slide 向け
- `tf.auto_size = MSO_AUTO_SIZE.NONE` (default): 枠固定、はみ出し時はクリップ
- 「テキストを枠内に自動縮小」は python-pptx では未実装。必要なら pywin32 経由で `TextFrame.AutoSize = 2` (msoAutoSizeTextToFitShape) を build 後に COM で設定する

### xfrm 4-Attribute Rule

When modifying a placeholder's position or size, **always set all 4 attributes** (`left`, `top`, `width`, `height`). Setting only some attributes causes python-pptx to create a new `xfrm` element, resetting unset attributes to **0** (width=0 → text wraps per character → appears vertical).

```python
# ❌ NG: Partial update — width resets to 0
body_ph.top = new_top
body_ph.height = new_height

# ✅ OK: Retrieve inherited values from layout, set all 4
layout = slide.slide_layout
for lph in layout.placeholders:
    if lph.placeholder_format.idx == target_idx:
        layout_left = lph.left
        layout_width = lph.width
        break
body_ph.left = layout_left
body_ph.width = layout_width
body_ph.top = new_top
body_ph.height = new_height
```

### Text Direction After Resize

After resizing a placeholder, explicitly set `vert="horz"` on `bodyPr` to prevent vertical text:

```python
txBody = body_ph._element.find(qn("p:txBody"))
if txBody is not None:
    bodyPr = txBody.find(qn("a:bodyPr"))
    if bodyPr is not None:
        bodyPr.set("vert", "horz")
```

### Table + Placeholder Overlap

When adding a table to a slide with an existing body placeholder (idx=1), move the placeholder below the table rather than deleting it (keeps it available for ad-hoc notes):

1. Calculate table bottom: `table_bottom = (table.top + table.height) / 914400`
2. Set placeholder top to `table_bottom + 0.1in`
3. Apply the 4-attribute rule above

### Section Rebuild After Dynamic Slide Addition

When dynamically adding slides from a template, the template's original section definitions remain stale. **Delete all sections and rebuild** before saving:

```python
# Remove old sectionLst from extLst
# Create new sectionLst with sections matching actual slide order
# Each section maps to a range of slide IDs
```
