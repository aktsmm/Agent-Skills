# Template: Advanced Operations

Detailed procedures for template analysis, cleaning, and slide master generation.

> 📖 See [template.instructions.md](template.instructions.md) for basic flow.

---

## analyze_template.py

Analyzes template layout structure and generates layouts.json.

### Usage

```powershell
python scripts/analyze_template.py templates/sample.pptx
# → Generates output_manifest/sample_layouts.json
```

### Output Example

```json
{
  "template": "sample.pptx",
  "layouts": [
    {
      "index": 0,
      "name": "Title Slide",
      "placeholders": ["TITLE", "SUBTITLE"]
    },
    {
      "index": 1,
      "name": "Title and Content",
      "placeholders": ["TITLE", "BODY"]
    },
    {
      "index": 2,
      "name": "Section Header",
      "placeholders": ["TITLE", "BODY"]
    },
    {
      "index": 3,
      "name": "Two Content",
      "placeholders": ["TITLE", "BODY", "CONTENT"]
    }
  ],
  "layout_mapping": {
    "title": 0,
    "content": 1,
    "section": 2,
    "two_column": 3,
    "content_with_image": 3
  }
}
```

### ★ Adding content_with_image Mapping

To prevent image overlap for `type: "content"` + `image` slides, map to Two Column layout:

```json
"layout_mapping": {
  "content_with_image": 3
}
```

---

## diagnose_template.py

Diagnoses template quality issues.

```powershell
python scripts/diagnose_template.py templates/sample.pptx
```

### Detection Items

| Issue               | Description                    | Resolution               |
| ------------------- | ------------------------------ | ------------------------ |
| Background images   | Images in master layouts       | clean_template           |
| Broken references   | Invalid blip references        | clean_template           |
| External links      | Broken links                   | Manual removal           |
| Narrow placeholders | Title width too narrow         | Auto-fix or alt template |
| Dark backgrounds    | Insufficient contrast          | Different template       |
| viewProps settings  | Opens in master view           | Auto-normalization       |
| Embedded fonts      | Font missing warnings possible | Specify fallback         |

---

## clean_template.py

Cleans template by removing problem elements.

```powershell
python scripts/clean_template.py templates/sample.pptx "output_manifest/${base}_clean.pptx"
```

### Processing

- Removes PICTURE shapes from masters/layouts
- Removes blip references from Picture Placeholders
- Removes broken external links
- Normalizes viewProps.xml

---

## create_clean_template.py

Creates a clean template from source PPTX.

```powershell
# Analysis only (no changes)
python scripts/create_clean_template.py input/presentation.pptx --analyze

# Apply all processing
python scripts/create_clean_template.py input/presentation.pptx "templates/${base}_clean.pptx" --all
```

### Options

| Option                 | Effect                               |
| ---------------------- | ------------------------------------ |
| `--remove-backgrounds` | Remove background images             |
| `--remove-decorations` | Remove decorative shapes (side bars) |
| `--fix-placeholders`   | Optimize placeholder positions       |
| `--all`                | Apply all above (recommended)        |
| `--analyze`            | Analysis only, no file changes       |

---

## PREPARE_TEMPLATE Phase (Required)

When using external templates, always execute:

```powershell
$base = "20251214_example"
$input = "input/external_template.pptx"

# 1. Diagnose
python scripts/diagnose_template.py $input

# 2. Clean (if issues found)
python scripts/clean_template.py $input "output_manifest/${base}_clean.pptx"
$template = "output_manifest/${base}_clean.pptx"

# 3. Analyze layout
python scripts/analyze_template.py $template

# 4. Add content_with_image to layouts.json (manually if needed)
```

> ⚠️ Skipping this causes background image duplication and layout issues.

---

## Template Selection by Purpose

| Purpose            | Recommended Template    | Reason                  |
| ------------------ | ----------------------- | ----------------------- |
| Internal reports   | Simple templates        | No flashy decoration    |
| Customer proposals | Corporate logo template | Branding                |
| Tech study groups  | Code-friendly template  | Code block support      |
| Conferences        | Official event template | Sponsor display support |
| PPTX translation   | Source PPTX master      | Design preservation (A) |

---

## References

- Basic flow: [template.instructions.md](template.instructions.md)
- content.json format: [template-content-json.instructions.md](template-content-json.instructions.md)
- replacements.json format: [template-replacements.instructions.md](template-replacements.instructions.md)
- Quality guidelines: [quality-guidelines.instructions.md](quality-guidelines.instructions.md)
