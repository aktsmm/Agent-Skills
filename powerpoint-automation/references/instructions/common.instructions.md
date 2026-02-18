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
