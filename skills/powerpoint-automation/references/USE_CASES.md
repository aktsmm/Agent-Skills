# Common Use Cases

Detailed examples of how to use PowerPoint Automation for various scenarios.

## 1. Tech Blog → Presentation

**Scenario**: Convert a Zenn or Qiita technical article into a presentation

**Input**:

- URL: `https://zenn.dev/example/articles/azure-copilot-guide`
- Article length: 3000 words, 5 images, 3 code blocks

**User Request**:

```
"Create a 15-slide presentation about Azure Copilot from this Zenn article:
https://zenn.dev/example/articles/azure-copilot-guide"
```

**Workflow**:

```
TRIAGE → User provides URL
    ↓
PLAN → System proposes: 15 slides, template D, standard detail
    ↓
EXTRACT → Fetch article content + download images
    ↓
TRANSLATE → (Skip if Japanese source)
    ↓
BUILD → create_from_template.py
    ↓
REVIEW → PPTX Reviewer checks quality
    ↓
DONE → Open PowerPoint
```

**Output**:

- 15-slide PPTX with:
  - Title slide
  - Agenda (3 sections)
  - 10 content slides (with code blocks)
  - 3 image slides (screenshots)
  - Summary slide

**Time**: ~3-5 minutes

---

## 2. English PPTX → Japanese Translation

**Scenario**: Translate Microsoft Ignite session slides to Japanese

**Input**:

- File: `input/BRK252_DataSecurity.pptx` (120 slides, English)
- Requirement: Maintain original design and layout

**User Request**:

```
"Translate this Microsoft presentation to Japanese, keeping the same design"
```

**Workflow**:

```
TRIAGE → Detect PPTX input
    ↓
PLAN → User confirms: Full translation (120 slides), method A (template inheritance)
    ↓
PREPARE_TEMPLATE → Diagnose + clean template
    ↓
EXTRACT → reconstruct_analyzer.py (PPTX → content.json)
         → extract_images.py (save all images)
    ↓
TRANSLATE → Localizer agent (content.json → content_ja.json)
    ↓
BUILD → create_from_template.py (inherit master from original)
    ↓
REVIEW → JSON Reviewer (translation quality)
       → PPTX Reviewer (layout, overflow, notes)
    ↓
DONE → 120-slide Japanese PPTX
```

**Output**:

- Japanese PPTX maintaining:
  - Original colors and fonts
  - Slide master design
  - Image positions
  - Speaker notes (translated)

**Key Features**:

- Template inheritance (method A)
- Automatic layout selection
- AutoFit control (prevent text spacing issues)
- Position adjustment for Japanese text

**Time**: ~15-20 minutes for 120 slides

---

## 3. Report Generation from Notes

**Scenario**: Create quarterly report presentation from Markdown notes

**Input**:

- Markdown notes with bullet points
- 5 charts/graphs (PNG images)
- Goal: Formal business report

**User Request**:

```
"Create a quarterly report presentation from my notes.
Include these 5 charts and make it professional."
```

**Workflow**:

```
TRIAGE → Detect mixed input (text + images)
    ↓
BRAINSTORM → Interactive Q&A
           → "Who's the audience?" → "Executives"
           → "Duration?" → "30 minutes"
           → "Tone?" → "Formal"
    ↓
        proposal.json generated
    ↓
PLAN → User confirms: 25 slides, template (business style)
    ↓
EXTRACT → Convert notes to content.json
        → Map images to slides
    ↓
BUILD → create_from_template.py
    ↓
REVIEW → PPTX Reviewer
    ↓
DONE → Business report PPTX
```

**Output**:

- 25-slide report with:
  - Executive summary
  - 5 sections with charts
  - Key metrics and insights
  - Action items and next steps

**Brainstormer Interaction**:
The Brainstormer agent asks:

1. Who's the audience?
2. Presentation duration?
3. Key message/goal?
4. Tone (formal/casual)?
5. Any topics to avoid?

**Time**: ~10 minutes (including brainstorming)

---

## 4. Technical Documentation → Training Material

**Scenario**: Convert API documentation into training slides

**Input**:

- API reference (Markdown/HTML)
- Code examples (JSON, cURL)
- Architecture diagram

**User Request**:

```
"Create training material for our REST API.
Include authentication, endpoints, and code examples."
```

**Workflow**:

```
TRIAGE → Detect documentation input
    ↓
PLAN → User confirms: 20 slides, method B (pptxgenjs for code blocks)
    ↓
EXTRACT → Parse documentation
        → Extract code snippets
        → Convert architecture diagram
    ↓
BUILD → create_pptx.js (pptxgenjs)
    ↓
REVIEW → PPTX Reviewer (code readability)
    ↓
DONE → Training material PPTX
```

**Output**:

- 20-slide training with:
  - API overview
  - Authentication flow (diagram)
  - Endpoint reference (with code)
  - Error handling examples
  - Best practices

**Why pptxgenjs (Method B)?**

- Better code block formatting (monospace, syntax highlighting)
- Custom diagram positioning
- Fine-grained control over layout

**Time**: ~8-10 minutes

---

## 5. Architecture Diagram + Presentation

**Scenario**: Add custom architecture diagrams to existing template

**Input**:

- Existing presentation template
- Architecture components (boxes, arrows, labels)

**User Request**:

```
"Create an Azure architecture diagram and insert it into slide 5 of this template"
```

**Workflow**:

```
PLAN → User confirms: Insert diagram at slide 5
    ↓
DIAGRAM → create_pptx.js (generate diagram with shapes)
        → Output: diagrams.pptx
    ↓
MERGE → insert_diagram_slides.py
      → Insert diagrams.pptx[0] at position 5
      → Select layout: "Title and Content"
    ↓
DONE → Combined PPTX
```

**Diagram Creation** (pptxgenjs):

```javascript
// Azure components
slide.addShape(pptx.ShapeType.rect, {
  x: 1,
  y: 2,
  w: 2,
  h: 1,
  fill: "0078D4", // Azure blue
  line: { color: "FFFFFF" },
});

// Arrows
slide.addShape(pptx.ShapeType.rightArrow, {
  x: 3.5,
  y: 2.3,
  w: 1,
  h: 0.4,
  fill: "505050",
});
```

**Time**: ~5 minutes

---

## 6. Slide Count Reduction (Summarization)

**Scenario**: Reduce 60-slide presentation to 20 slides for shorter session

**Input**:

- Original PPTX (60 slides)
- Target: 20 slides (1/3 compression)

**User Request**:

```
"Reduce this 60-slide presentation to 20 slides for a 15-minute talk"
```

**Workflow**:

```
EXTRACT → reconstruct_analyzer.py
    ↓
SUMMARIZE → summarize_content.py
          → AI combines related slides
          → Keeps key visuals
          → Merges bullet points
    ↓
BUILD → create_from_template.py
    ↓
REVIEW → Check for information loss
    ↓
DONE → 20-slide condensed version
```

**Summarization Strategy**:

- Merge similar content slides
- Keep all section dividers
- Preserve key images
- Combine related bullet points
- Maintain logical flow

**Time**: ~10 minutes

---

## 7. Multilingual Presentations

**Scenario**: Create same presentation in 3 languages (EN, JA, ZH)

**Input**:

- Original content.json (English)

**User Request**:

```
"Create this presentation in English, Japanese, and Chinese"
```

**Workflow**:

```
EXTRACT → content.json (English)
    ↓
TRANSLATE → Localizer (EN → JA) → content_ja.json
    ↓
TRANSLATE → Localizer (EN → ZH) → content_zh.json
    ↓
BUILD → create_from_template.py × 3
      → output_ppt/{base}_en.pptx
      → output_ppt/{base}_ja.pptx
      → output_ppt/{base}_zh.pptx
    ↓
DONE → 3 language versions
```

**Font Handling**:

- English: Arial, Calibri
- Japanese: Meiryo, Yu Gothic
- Chinese: Microsoft YaHei, SimHei

**Time**: ~20 minutes for 3 languages

---

## Quick Reference

| Use Case         | Input          | Method                      | Time      | Output       |
| ---------------- | -------------- | --------------------------- | --------- | ------------ |
| **Blog → PPTX**  | URL            | EXTRACT → BUILD             | 3-5 min   | 15-20 slides |
| **EN → JA**      | PPTX           | EXTRACT → TRANSLATE → BUILD | 15-20 min | Same design  |
| **Report**       | Notes + Images | BRAINSTORM → BUILD          | 10 min    | 25 slides    |
| **Training**     | Docs + Code    | EXTRACT → BUILD (pptxgenjs) | 8-10 min  | 20 slides    |
| **Diagram**      | Components     | DIAGRAM → MERGE             | 5 min     | 1 diagram    |
| **Summarize**    | 60 slides      | EXTRACT → SUMMARIZE → BUILD | 10 min    | 20 slides    |
| **Multilingual** | content.json   | TRANSLATE × N → BUILD × N   | 20 min    | N versions   |

---

## Tips & Best Practices

### For Blog Conversions

- Prefer standard detail (option 2) for balance
- Always include images from the article
- Use method D (first template) for professional look

### For Translations

- Use method A (template inheritance) to maintain design
- Review speaker notes carefully
- Check for technical term consistency

### For Technical Content

- Use pptxgenjs (method B) for code-heavy slides
- Limit code blocks to 10 lines per slide
- Include comments in code for clarity

### For Business Reports

- Use formal templates
- Include agenda and summary slides
- Add speaker notes for presenter guidance
- Keep bullet points to 5-8 items max

### For Diagrams

- Use pptxgenjs for custom shapes
- Match template colors (read from master)
- Position diagrams at "right" or "bottom" for text space
