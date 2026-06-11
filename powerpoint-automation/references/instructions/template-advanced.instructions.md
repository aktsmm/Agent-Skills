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
| Background images   | Images in the wrong surface    | classify as reusable layout art vs slide content |
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

- Removes or relocates PICTURE shapes from masters/layouts when they are not reusable template art
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

## Reusable Template Creation from Scratch

Use this when the user wants a reusable PowerPoint template, not just a one-off deck.

### Goal

Create a clean template file with:

- one slide master
- only the custom layouts the user will actually reuse
- generic layout names, not customer/project-specific names
- sample slides that demonstrate each layout
- theme fonts set for both Latin and Japanese text

### Recommended layout set

Keep the first version small. A useful internal template usually needs only:

| Layout | Purpose |
| --- | --- |
| `Internal Title Slide` | Cover |
| `Internal Section Header` | Section divider |
| `Internal Title and Content` | Normal body slide |
| `Internal Process` | Simple flow / process diagram |
| `Internal References` | Page title + URL reference list |

### Procedure

1. Start from a new blank presentation instead of modifying a busy existing template.
2. Create one slide master and add only the required custom layouts.
3. Delete unused default/custom layouts if PowerPoint inserted them.
4. Add one sample slide per layout so future users can preview the template.
5. Use generic names such as `Internal ...`; do not bake customer names or project names into reusable templates.
6. Set theme fonts and placeholder fonts explicitly. For Japanese decks, set Latin and Far East fonts together.
7. Move reusable visual design into layouts: background arcs, brand marks, decorative lines, slide-number placeholders, and reusable image frames belong on custom layouts; concrete screenshots/photos/body text belong on sample slides.
8. Keep placeholder prompt strings on layouts only. Sample slides should not visibly contain literal `<Title>`, `<Body>`, `Date`, or `Footer` text unless intentionally demonstrating a placeholder.
9. Duplicate layouts when different sample slides need different inherited backgrounds. Do not reuse one custom layout for visually distinct surfaces just to keep the layout count small.
10. Run `analyze_template.py` and verify that `title`, `content`, and `section` map to the intended custom layouts.
11. Inspect the resulting PPTX theme/layout XML if font correctness matters. Confirm the theme uses the intended Japanese font, not just visible shapes.
12. Create blank test slides from each custom layout in the same presentation/copy and render them. Existing sample slides can look correct even when the layout is missing its background art, page number, or image placeholder.

### Done checks

- `masters=1` unless the user explicitly asked for multiple masters
- custom layouts are limited to the intended reusable set
- generated mapping points to the intended layouts
- no customer-specific words remain in layout names or sample placeholders
- theme XML and layout XML include the intended fonts
- sample slide XML does not contain literal placeholder prompt strings as visible text
- non-cover layouts include slide-number placeholders when the template convention requires page numbers
- blank slides created from each layout inherit the expected design surface
- verification uses layouts from the same presentation/copy, not `CustomLayout` COM objects passed across decks

### Common pitfall

Creating five sample slides is not the same as creating a reusable template. The reusable value is in the slide master and custom layouts; sample slides are only previews.

Also avoid the opposite failure mode: deleting too aggressively until the layout is clean but visually empty. A reusable template must preserve intended design in the layout itself, not only in the preview slide.

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
