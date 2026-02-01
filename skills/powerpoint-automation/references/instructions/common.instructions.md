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
