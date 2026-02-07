# Tools Reference

## Method Selection

| Purpose                 | Recommended Method                                    | Rating     | Notes                    |
| ----------------------- | ----------------------------------------------------- | ---------- | ------------------------ |
| English PPTX → Japanese | `reconstruct_analyzer.py` + `create_from_template.py` | ⭐⭐⭐⭐⭐ | Best, master inheritance |
| Template-based          | `analyze_template.py` + `create_from_template.py`     | ⭐⭐⭐⭐⭐ | Best, design inheritance |
| From scratch            | `create_ja_pptx.py`                                   | ⭐⭐⭐⭐   | Simple and clean         |
| Code/tech heavy         | Custom JS (pptxgenjs)                                 | ⭐⭐⭐⭐   | Code block support       |
| Diagrams                | Custom JS (pptxgenjs)                                 | ⭐⭐⭐⭐⭐ | Shapes, arrows, colors   |

### Experimental / Deprecated Methods

| Method   | Status           | Reason                                               |
| -------- | ---------------- | ---------------------------------------------------- |
| preserve | **experimental** | Layout issues with charts/diagrams → use reconstruct |
| html     | **deprecated**   | Low design quality → use template method             |

---

## Common Tools

### Classification & Extraction

- `classify_input.py`: Input classification, method selection → classification.json
- `reconstruct_analyzer.py`: English PPTX → content.json (auto slide type detection, notes extraction)
  - `--classification` option to reference classification.json
- `extract_images.py`: Extract images from PPTX → images/slide\_{nn}.png/jpg

### Template Processing

- `analyze_template.py`: Layout analysis → layouts.json (first time only)
- `diagnose_template.py`: Template quality diagnosis (backgrounds, broken refs)
- `clean_template.py`: Remove backgrounds and problem elements
- `create_clean_template.py`: **Auto-generate clean template from source PPTX** ★ NEW

### Validation

- `validate_content.py`: content.json schema validation, empty slide detection, image path verification
- `validate_pptx.py`: PPTX validation (slide count match, notes, images, overflow)

### Generation

- `create_from_template.py`: content.json + template → PPTX
  - **Validation**: Detects `type='content'` slides without `items`/`bullets` and exits with code 1
  - **Empty placeholder removal**: Auto-removes empty Picture Placeholders after image addition
  - `--force` for warning-only forced generation
- `create_ja_pptx.py`: JSON → new PPTX (python-pptx)
- `merge_slides.py`: Merge pptxgenjs diagrams into template
- `insert_diagram_slides.py`: Insert diagram slides at correct position/layout ★ NEW

---

## English PPTX Localization Flow (reconstruct) ★ Recommended

```powershell
$base = "20251213_example_presentation"
$input = "input/BRK252_presentation.pptx"

# 0. ★ Template diagnosis & cleaning (required for external templates)
python scripts/diagnose_template.py $input
# If issues found:
python scripts/clean_template.py $input "output_manifest/${base}_clean_template.pptx"
$template = "output_manifest/${base}_clean_template.pptx"
# If no issues:
$template = $input

# 1. Layout analysis (first time only)
python scripts/analyze_template.py $template

# 2. ★ Image extraction (required)
python scripts/extract_images.py $input "images"

# 3. Content extraction → content.json
python scripts/reconstruct_analyzer.py $input "output_manifest/${base}_content.json"

# 4. Translation (delegate to Localizer agent)
# Localizer agent translates content.json
# → output_manifest/${base}_content_ja.json

# 5. PPTX reconstruction
python scripts/create_from_template.py $input "output_manifest/${base}_content_ja.json" "output_ppt/${base}.pptx"

# 6. Verify in PowerPoint
Start-Process "output_ppt/${base}.pptx"
```

---

## Image Extraction Rules (Web Source)

When generating PPTX from web sources (Qiita, Zenn, blogs), **extract images first**.

### ⚠️ Important: fetch_webpage Limitations

`fetch_webpage` tool **may not return image URLs**. Extract separately:

```powershell
$base = "20251212_example_blog"
$url = "https://zenn.dev/xxx/articles/yyy"

# 1. Get HTML source
$html = curl -s $url

# 2. Extract image URLs with regex
$imageUrls = [regex]::Matches($html, 'https://[^"]+\.(png|jpg|jpeg|gif|webp)') |
    ForEach-Object { $_.Value } |
    Select-Object -Unique

# 3. Create image directory
New-Item -ItemType Directory -Path "images/${base}" -Force

# 4. Download images
$i = 1
foreach ($imgUrl in $imageUrls) {
    $ext = [System.IO.Path]::GetExtension($imgUrl) -replace '\?.*$', ''
    curl -s -o "images/${base}/$('{0:D2}' -f $i)_image$ext" $imgUrl
    $i++
}
```

### Code Block Extraction

Code blocks in articles go in content.json `code` field:

```json
{
  "type": "content",
  "title": "Example",
  "items": ["Point 1", "Point 2"],
  "code": "<button hx-get=\"/api/data\">Fetch</button>"
}
```

**Support Status:**

| Method                       | Code Block Support | Notes                   |
| ---------------------------- | ------------------ | ----------------------- |
| `create_from_template.py`    | ✅ Supported       | Dark bg + Consolas font |
| `create_pptx.js` (pptxgenjs) | ✅ Supported       | Native support          |
| `create_ja_pptx.py`          | ⚠️ To be added     | Future support          |

---

## Template New Generation Flow

```powershell
# Dynamically get first template
$template = (Get-ChildItem -Path "assets" -Filter "*.pptx" | Select-Object -First 1).BaseName
$base = "20251212_example_blog"

# 1. Analyze if layouts.json doesn't exist
if (-not (Test-Path "output_manifest/${template}_layouts.json")) {
    python scripts/analyze_template.py "assets/${template}.pptx"
}

# 2. Get images (for web sources)
New-Item -ItemType Directory -Path "images/${base}" -Force
curl -s -o "images/${base}/01_diagram.png" "{extracted_image_url}"

# 3. Create content.json (include image paths)

# 4. Generate PPTX
python scripts/create_from_template.py "assets/${template}.pptx" "output_manifest/${base}_content.json" "output_ppt/${base}.pptx"
```

---

## Web Source PPTX Generation Flow (All Methods)

```
1. Fetch article (API or fetch)
     ↓
2. ★ Extract image URLs & download (images/{base}/)
     ↓
3. Calculate slides: base count + image count
     ↓
4. Create content.json (place images with type: "photo")
     ↓
5. Generate PPTX
```

**Compliance Required**: Do not skip images and add later.

---

## Diagram + Template Workflow ★ Recommended

**To use template design (colors, fonts) while creating diagrams with shapes:**

```powershell
$base = "20251216_azure_diagram"
$template = "assets/template.pptx"

# 1. Generate diagram with pptxgenjs (shapes, arrows)
node scripts/create_azure_diagram.js
# → output_ppt/${base}_diagram.pptx

# 2. Merge into template (inherit master)
python scripts/merge_slides.py $template "output_ppt/${base}_diagram.pptx" "output_ppt/${base}.pptx" --clear-template

# 3. Verify in PowerPoint
Start-Process "output_ppt/${base}.pptx"
```

**merge_slides.py Options:**

| Option                 | Effect                                         |
| ---------------------- | ---------------------------------------------- |
| `--clear-template`     | Delete template slides (inherit master only) ★ |
| `--position 0`         | Insert at beginning                            |
| `--position -1`        | Append at end (default)                        |
| `--keep-source-master` | Keep source colors                             |

### ⚠️ pptxgenjs Size Note (★ Important)

pptxgenjs `LAYOUT_16x9` is **10" × 5.625"**, different from template (usually 13.33" × 7.5").

**Recommended Steps:**

1. Get template size
2. Define same size with `defineLayout()`
3. Calculate all coordinates using SLIDE_WIDTH/SLIDE_HEIGHT variables

```powershell
# Get template size
$templateSize = python -c "from pptx import Presentation; p=Presentation('$template'); print(f'{p.slide_width.inches},{p.slide_height.inches}')"
$sizes = $templateSize -split ','
$slideWidth = [double]$sizes[0]
$slideHeight = [double]$sizes[1]
```

---

## PREPARE_TEMPLATE Phase (★ Required)

When using external templates (especially English PPTX), **always** execute these steps. Skipping causes layout issues and background duplication.

| Issue                     | Symptom                             | Solution                          |
| ------------------------- | ----------------------------------- | --------------------------------- |
| Master background images  | Mountain scenery overlays on slides | Delete PICTURE shapes             |
| Picture Placeholder blip  | "Image cannot be displayed"         | Delete blip reference or PH       |
| Missing embedded fonts    | Font substitution warning           | Specify fallback fonts            |
| Broken external links     | Link error                          | Delete external references        |
| viewProps.xml inheritance | Opens in master view                | Auto-normalization (at BUILD)     |
| content+image overlap     | Image covers text                   | Add content_with_image to layouts |

**Diagnosis & Cleaning Steps:**

```powershell
$base = "20251214_example"
$input = "input/template.pptx"

# 1. Diagnose template
python scripts/diagnose_template.py $input

# 2. Clean if issues found
python scripts/clean_template.py $input "output_manifest/${base}_clean_template.pptx"
$template = "output_manifest/${base}_clean_template.pptx"

# 3. Analyze layout
python scripts/analyze_template.py $template

# 4. Add content_with_image mapping to layouts.json
# 📖 See template-advanced.instructions.md for details (SSOT)
```

**Recommended layouts.json Mapping:**

```json
{
  "layout_mapping": {
    "content_with_image": 6
  }
}
```

> 💡 Without `content_with_image`, `type: "content"` + `image` slides will have image overlapping text
