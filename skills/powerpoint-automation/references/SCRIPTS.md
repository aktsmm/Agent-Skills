# Script Reference

Complete documentation of all scripts in the PowerPoint Automation pipeline.

## Content Extraction

### `classify_input.py`

**Purpose**: Detect input type and determine appropriate workflow

**Usage**:

```powershell
python scripts/classify_input.py input/file_or_url
```

**Output**: `output_manifest/{base}_classification.json`

### `extract_images.py`

**Purpose**: Extract images from PPTX or web sources

**Usage**:

```powershell
python scripts/extract_images.py input/presentation.pptx images/{base}/
```

**Output**: Image files in `images/{base}/`

### `reconstruct_analyzer.py`

**Purpose**: Convert PPTX to content.json (IR format)

**Usage**:

```powershell
python scripts/reconstruct_analyzer.py input/presentation.pptx output_manifest/{base}_content.json
```

**Output**: `output_manifest/{base}_content.json`

**Features**:

- Automatic slide type detection (title, content, section, etc.)
- Speaker notes extraction
- Image path mapping
- Source slide tracking

---

## Template Management

### `analyze_template.py`

**Purpose**: Analyze template layouts and generate mapping configuration

**Usage**:

```powershell
python scripts/analyze_template.py templates/template.pptx
```

**Output**: `output_manifest/{template}_layouts.json`

**When to Use**: First time using a new template

### `diagnose_template.py`

**Purpose**: Detect quality issues in templates

**Usage**:

```powershell
python scripts/diagnose_template.py templates/template.pptx
```

**Detects**:

- Background images in master slides
- Broken image references
- Narrow placeholders
- Dark backgrounds (contrast issues)

### `clean_template.py`

**Purpose**: Remove problematic elements from templates

**Usage**:

```powershell
python scripts/clean_template.py input/template.pptx output/clean_template.pptx
```

**Actions**:

- Remove background images
- Fix broken image references
- Normalize viewProps.xml

### `create_clean_template.py`

**Purpose**: Generate clean template from source PPTX

**Usage**:

```powershell
python scripts/create_clean_template.py input/presentation.pptx output/template.pptx --all
```

**Options**:

- `--remove-backgrounds`: Remove background images
- `--remove-decorations`: Remove decorative shapes
- `--fix-placeholders`: Optimize placeholder positions
- `--all`: Apply all fixes (recommended)
- `--analyze`: Analysis only, no changes

---

## PPTX Generation

### `create_from_template.py` ⭐ **Recommended**

**Purpose**: Generate PPTX from content.json using template

**Usage**:

```powershell
python scripts/create_from_template.py templates/template.pptx output_manifest/{base}_content.json output_ppt/{base}.pptx
```

**Features**:

- Template master inheritance (colors, fonts, backgrounds)
- Automatic layout selection
- Image positioning and sizing
- Code block support
- AutoFit control
- Empty placeholder cleanup

**Configuration**: Reads `output_manifest/{template}_layouts.json` for layout mapping

### `create_ja_pptx.py`

**Purpose**: Generate PPTX from scratch using python-pptx

**Usage**:

```powershell
python scripts/create_ja_pptx.py output_manifest/{base}_content.json output_ppt/{base}.pptx
```

**When to Use**: When no template is needed (minimal design)

### `create_pptx.js`

**Purpose**: Generate PPTX with custom diagrams using pptxgenjs

**Usage**:

```bash
node scripts/create_pptx.js
```

**When to Use**:

- Architecture diagrams with shapes and arrows
- Custom layouts not available in templates
- Full control over positioning and styling

---

## Advanced Operations

### `merge_slides.py`

**Purpose**: Merge slides from source PPTX into template

**Usage**:

```powershell
python scripts/merge_slides.py template.pptx source.pptx output.pptx [--clear-template] [--position N]
```

**Options**:

- `--clear-template`: Remove existing slides, keep master only
- `--position N`: Insert at position N (-1 = append)
- `--keep-source-master`: Preserve source colors

**Use Case**: Combine pptxgenjs diagrams with template design

### `insert_diagram_slides.py`

**Purpose**: Insert diagram slides at specific positions with layout selection

**Usage**:

```powershell
python scripts/insert_diagram_slides.py base.pptx diagrams.pptx output.pptx --config config.json
```

**Config Format**:

```json
{
  "insertions": [
    {
      "source_index": 0,
      "target_position": 4,
      "layout_name": "Title and Content"
    }
  ]
}
```

### `summarize_content.py`

**Purpose**: Reduce slide count using AI summarization

**Usage**:

```powershell
python scripts/summarize_content.py output_manifest/{base}_content.json --target-slides 15
```

**When to Use**: Converting long presentations to shorter versions

---

## Quality Assurance

### `validate_content.py`

**Purpose**: Validate content.json against schema

**Usage**:

```powershell
python scripts/validate_content.py output_manifest/{base}_content.json
```

**Checks**:

- Schema compliance
- Empty slides detection
- Image path existence
- Items format validation

**Exit Codes**:

- 0 = PASS
- 1 = FAIL (schema violation)
- 2 = WARN (quality issues)

### `validate_pptx.py`

**Purpose**: Detect PPTX quality issues

**Usage**:

```powershell
python scripts/validate_pptx.py output_ppt/{base}.pptx output_manifest/{base}_content.json
```

**Checks**:

- Slide count mismatch
- Text overflow (>800 chars, >15 paragraphs)
- Missing speaker notes
- Source-only notes (lacking content)

### `review_pptx.py`

**Purpose**: Extract PPTX content for AI review

**Usage**:

```powershell
python scripts/review_pptx.py output_ppt/{base}.pptx
```

**Output**: Markdown report with slide content for AI analysis

---

## Utility Scripts

### `reorder_slides.py`

**Purpose**: Reorder and duplicate slides

**Usage**:

```powershell
python scripts/reorder_slides.py input.pptx output.pptx --order 0,1,1,2,5
```

### `extract_shapes.py`

**Purpose**: Extract shape inventory from PPTX

**Usage**:

```powershell
python scripts/extract_shapes.py input.pptx output_manifest/{base}_inventory.json
```

**Use Case**: Analysis for text replacement workflows

### `apply_content.py`

**Purpose**: Apply text replacements to PPTX shapes

**Usage**:

```powershell
python scripts/apply_content.py input.pptx output_manifest/{base}_replacements.json output.pptx
```

**Note**: Experimental, use reconstruct method instead

### `extract_parallel.ps1`

**Purpose**: Run EXTRACT phase in parallel (analyze + extract + reconstruct)

**Usage**:

```powershell
.\scripts\extract_parallel.ps1 -InputPptx "input/presentation.pptx" -Base "20251218_example"
```

### `workflow_tracer.py`

**Purpose**: Generate workflow trace logs

**Usage**:

```powershell
python scripts/workflow_tracer.py {base} {phase} {status}
```

**Output**: `output_manifest/{base}_trace.jsonl`

### `resume_workflow.py`

**Purpose**: Resume workflow from specific phase after manual fixes

**Usage**:

```powershell
python scripts/resume_workflow.py {base} --from REVIEW_JSON [--reset-retry]
```

---

## Script Dependencies

### Python Requirements

See `scripts/requirements.txt`:

- python-pptx
- Pillow (image processing)
- jsonschema (validation)

### Node.js Requirements

See `scripts/package.json`:

- pptxgenjs (diagram generation)

### Installation

```powershell
# Python
pip install -r scripts/requirements.txt

# Node.js
npm install --prefix scripts
```

---

## Common Workflows

### Web Article → PPTX

```powershell
# 1. Extract (manual content creation)
# 2. Translate (Localizer agent)
# 3. Generate
python scripts/create_from_template.py templates/template.pptx output_manifest/{base}_content_ja.json output_ppt/{base}.pptx
```

### English PPTX → Japanese

```powershell
# 1. Extract
python scripts/extract_images.py input/en.pptx images/{base}/
python scripts/reconstruct_analyzer.py input/en.pptx output_manifest/{base}_content.json

# 2. Translate (Localizer agent)

# 3. Generate
python scripts/create_from_template.py input/en.pptx output_manifest/{base}_content_ja.json output_ppt/{base}.pptx
```

### Diagram + Template

```powershell
# 1. Generate diagrams
node scripts/create_pptx.js  # → diagrams.pptx

# 2. Merge
python scripts/merge_slides.py templates/template.pptx diagrams.pptx output_ppt/{base}.pptx --clear-template
```
