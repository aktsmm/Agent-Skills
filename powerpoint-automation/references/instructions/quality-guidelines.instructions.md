# Quality Guidelines

## Citation Rules (★ Important)

When generating new PPTX from existing PPTX, **include source slide number in speaker notes**.

### Auto-Added (reconstruct method)

`reconstruct_analyzer.py` auto-adds to each slide's notes:

```
[Source: Original slide #5]
```

### Manual Creation / Integration Rules

| Case                        | Notes Content                          |
| --------------------------- | -------------------------------------- |
| 1-to-1 conversion           | `[Source: Original slide #N]`          |
| Multiple slides merged      | `[Source: Original slides #3, #4, #5]` |
| Summarized/restructured     | `[Source: Based on slides #10-15]`     |
| Newly added (not in source) | `[Newly created]`                      |

---

## Slide Structure Rules

1. **Agenda required**: Place `type: "agenda"` immediately after title slide
2. **Summary required**: Place summary/wrap-up before closing
3. **No empty slides**: Slides with only notes (no body content) are prohibited
4. **Minimum content**: `type: "content"` must have `items` or `image`
5. **Section subtitles**: `type: "section"` should have `subtitle` (prevents empty-looking slides)
6. **Enriched speaker notes**: All slide notes must have specific explanations (citations only is NG)

---

## Section Slide Rules (★ Important)

**Problem**: `type: "section"` with title only looks empty

**Recommended**: Always add `subtitle` field with section overview

```json
// ❌ NG: Title only, looks empty
{
  "type": "section",
  "title": "MCP Server Development and Deployment"
}

// ✅ OK: Subtitle adds context
{
  "type": "section",
  "title": "MCP Server Development and Deployment",
  "subtitle": "Develop in VS Code, deploy to Azure Container Apps"
}
```

---

## 🚨 Speaker Notes Quality (★ Auto-Detection)

**Problem**: Notes with only "Source: Original slide #XX" don't help presenter know what to say

**Auto-Detection**: `validate_pptx.py` detects "citation-only" pattern and warns

```
⚠️ [source_only_notes] slides [14, 17, ...]: X slides have only source citations
💡 Add talking points, background info, or context for the presenter
```

**Rule**: All slide notes must include specific explanations

| Slide Type      | Notes Should Include                        | Min Lines  |
| --------------- | ------------------------------------------- | ---------- |
| **title**       | Self-intro, session purpose                 | 3 lines    |
| **agenda**      | Agenda overview, time estimates             | 2 lines    |
| **section**     | Section purpose, topics covered, transition | 3-5 lines  |
| **content**     | Item details, background, speaking hints    | 5-10 lines |
| **photo/image** | Image description, what to point out        | 3-5 lines  |
| **two_column**  | Comparison points, conclusion to convey     | 3-5 lines  |
| **summary**     | Summary points, next actions                | 3 lines    |

### Good Example (section)

```json
{
  "type": "section",
  "title": "Microsoft Fabric Security",
  "subtitle": "Protecting Fabric Copilot",
  "notes": "From here, we'll discuss data security in Microsoft Fabric.\n\nLike M365, oversharing is a real issue in Fabric. We can apply the same playbook (DSPM → DLP → Protection policies).\n\nMain topics:\n- DSPM risk assessment for Fabric\n- DLP policies for Fabric\n- Blocking in Fabric Copilot\n\n---\n[Source: Based on slides #126-153]"
}
```

### Avoid This Example

```json
{
  "type": "section",
  "title": "Microsoft Fabric Security",
  "subtitle": "Protecting Fabric Copilot",
  "notes": "[Source: Based on slides #126-153]"
}
```

---

## Overflow Prevention

1. **Auto-validation**: `validate_pptx.py` detects overflow after BUILD (800+ chars, 15+ paragraphs, 120+ char lines)
2. **Character limits**: Title 40 chars, bullet items 80 chars (guideline)
3. **Item limits**: 5-8 bullets per slide max, can use 1-level indent
4. **Split recommended**: If content is heavy, split into multiple slides

---

## Theme Font Resolution (★★ Critical)

**Problem**: Japanese text renders in 游ゴシック despite setting `<a:ea>` to BIZ UDPゴシック.

**Root cause**: PowerPoint resolves Japanese fonts via `<a:font script="Jpan">` in theme XML, which takes priority over `<a:ea>`.

### Font Resolution Chain (priority order)

```
1. run <a:rPr> → explicit font on the run
2. paragraph <a:pPr>/<a:defRPr> → paragraph default
3. slideMaster titleStyle/bodyStyle → master-level default
4. theme majorFont/minorFont:
   a. <a:font script="Jpan"> ← ★ THIS decides Japanese font
   b. <a:ea>                  ← fallback for non-script-specific EA
   c. <a:latin>               ← Latin characters
```

> ⚠️ `+mn-ea` / `+mn-lt` tokens in master styles resolve to theme fonts.
> If theme has 游ゴシック, all `+mn-ea` references become 游ゴシック.

### Fix: Modify theme XML directly

python-pptx cannot modify theme fonts. Use ZIP-level manipulation:

```python
import zipfile, shutil, re, os

def fix_theme_fonts(pptx_path, font_ja='BIZ UDPゴシック', font_latin='BIZ UDPGothic'):
    tmp = pptx_path + '.tmp'
    shutil.copy2(pptx_path, tmp)
    with zipfile.ZipFile(tmp, 'r') as zin:
        with zipfile.ZipFile(pptx_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.startswith('ppt/theme/') and item.filename.endswith('.xml'):
                    content = data.decode('utf-8')
                    # Fix script="Jpan" (the REAL Japanese font source)
                    content = re.sub(
                        r'(<a:font script="Jpan" typeface=")[^"]+(")' ,
                        f'\\g<1>{font_ja}\\2', content)
                    # Fix ea
                    content = re.sub(
                        r'(<a:ea typeface=")[^"]*(")' ,
                        f'\\g<1>{font_ja}\\2', content)
                    data = content.encode('utf-8')
                zout.writestr(item, data)
    os.remove(tmp)
```

### Detection

```python
import zipfile, re
with zipfile.ZipFile('output.pptx') as z:
    for tf in [f for f in z.namelist() if 'theme' in f]:
        content = z.read(tf).decode('utf-8')
        jpan = re.findall(r'<a:font script="Jpan" typeface="([^"]+)"', content)
        print(f"{tf}: Jpan={set(jpan)}")
        # If Jpan contains 游ゴシック → fix required
```

---

## Font Size Minimum (★ Important)

**Rule**: All text in slides must be **12pt or larger**.

| Element          | Min Size | Recommended |
| ---------------- | -------- | ----------- |
| Slide title      | 18pt     | 20-28pt     |
| Body / bullets   | 12pt     | 13-14pt     |
| Footer / source  | 10pt     | 10-11pt     |
| Captions / notes | 8pt      | 8-10pt      |

> ⚠️ Exception: Footer URLs / source citations may use 8-10pt, but body text must never go below 12pt.

**Validation**: After generating PPTX, check for undersized text:

```python
from pptx import Presentation
from pptx.util import Pt
prs = Presentation('output.pptx')
MIN_PT = 12
for i, slide in enumerate(prs.slides, 1):
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    if run.font.size and run.font.size < Pt(MIN_PT):
                        print(f"⚠️ Slide {i}: {run.font.size.pt}pt < {MIN_PT}pt: {run.text[:40]}")
```

---

## Textbox Overlap Prevention (★ Important)

**Rule**: Textboxes must not overlap. Verify that `shape.top + shape.height <= next_shape.top`.

**Problem**: When adding textboxes programmatically (e.g. customer name, subtitle), they may overlap if positions are not calculated from existing shapes.

**Prevention checklist**:

1. Read existing shape positions (`top`, `height`) before adding new ones
2. Calculate `bottom = top + height` for each shape
3. Ensure new shape's `top >= previous shape's bottom + gap`
4. Shrink oversized textbox `height` (e.g. subtitle placeholders have large default height)

**Validation snippet**:

```python
from pptx import Presentation
prs = Presentation('output.pptx')
for i, slide in enumerate(prs.slides, 1):
    shapes = sorted(
        [s for s in slide.shapes if s.has_text_frame],
        key=lambda s: s.top
    )
    for j in range(len(shapes) - 1):
        bottom = shapes[j].top + shapes[j].height
        next_top = shapes[j+1].top
        if bottom > next_top:
            t1 = shapes[j].text_frame.paragraphs[0].text[:30]
            t2 = shapes[j+1].text_frame.paragraphs[0].text[:30]
            print(f"⚠️ Slide {i}: overlap! [{t1}] bottom={bottom} > [{t2}] top={next_top}")
```

---

## Image Size Guidelines

| Original Size     | Recommended width_percent | Notes            |
| ----------------- | ------------------------- | ---------------- |
| Large (1000px+)   | 40-50%                    | Normal size      |
| Medium (500-1000) | 30-40%                    | Slightly smaller |
| Small (<500px)    | 20-30%                    | Don't enlarge    |
| Icon/Logo         | 15-25%                    | Keep original    |

**Important**: Don't oversized small images (they blur)

### Title Slide Image Limit (★ Important)

Images on title slides (`type: "title"` / `type: "closing"`) are **auto-limited to 25%**.

**Reason**:

- Large presenter photos cut off titles
- Title slides should prioritize the title, images are supplementary

---

## Slide Master Usage Rules (★ Important)

**Problem**: Using same layout for all slides looks "amateur"

**Rule**: Select appropriate layout based on slide type

| Slide Type   | Recommended Layout               | Description           |
| ------------ | -------------------------------- | --------------------- |
| `title`      | Title Slide / Title square photo | Title-specific layout |
| `section`    | Section Header / Section Divider | Section break         |
| `content`    | Title and Content                | Standard content      |
| `two_column` | Two Content                      | Comparison            |
| `closing`    | Closing / Thank You              | Ending-specific       |
| `agenda`     | Title and Content                | Same as content OK    |

### Avoid "Demo" / Sample Layouts (★ Important)

**Problem**: Template PPTX files often contain "Demo slide" or sample layouts with dark backgrounds and placeholder text (e.g. "Demo title", "Speaker name"). When slides use these layouts, the placeholder text bleeds through as ghost text even when empty.

**Detection**:

```python
from pptx import Presentation
prs = Presentation('output.pptx')
bad_layouts = ['Demo slide', 'Demo', 'Sample']
for i, slide in enumerate(prs.slides, 1):
    if any(b.lower() in slide.slide_layout.name.lower() for b in bad_layouts):
        print(f"⚠️ Slide {i}: uses '{slide.slide_layout.name}' layout - change required")
```

**Fix — Change slide layout** (python-pptx has no `slide.slide_layout` setter):

```python
# slide.slide_layout = new_layout  ← ❌ AttributeError: no setter
# Must modify the relationship target directly:
target_layout = [l for l in prs.slide_layouts if l.name == 'タイトルとコンテンツ'][0]
for slide in prs.slides:
    if 'Demo' in slide.slide_layout.name:
        for rel in slide.part.rels.values():
            if "slideLayout" in rel.reltype:
                rel._target = target_layout.part
                break
```

### Empty Placeholder Cleanup (★ Important)

**Problem**: Even after changing layouts, empty placeholders inherited from the original layout remain in the slide XML and display ghost text from the layout definition.

**Fix — Remove empty placeholders**:

```python
for slide in prs.slides:
    to_remove = []
    for shape in slide.shapes:
        if shape.is_placeholder:
            txt = ''.join(r.text for p in shape.text_frame.paragraphs for r in p.runs).strip()
            if not txt:
                to_remove.append(shape)
    for shape in to_remove:
        shape._element.getparent().remove(shape._element)
```

> ⚠️ Always run this AFTER layout change, as placeholder inheritance depends on the layout.

**Full post-generation checklist**:

1. **Fix theme fonts** → Ensure `script="Jpan"` uses correct font (not 游ゴシック)
2. Check for "Demo" / sample layouts → change to standard layout
3. Remove empty placeholders
4. Normalize TB shape fonts to match PH defaults (size + typeface)
5. Validate font sizes (≥ 12pt)
6. Check textbox overlaps
7. Verify text overflow (paragraph count, char count)

