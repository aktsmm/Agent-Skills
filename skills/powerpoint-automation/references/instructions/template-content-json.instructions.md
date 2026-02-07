# Template: content.json Format

Detailed specification for content.json. Used for template-based PPTX generation.

> 📖 See [template.instructions.md](template.instructions.md) for basic flow.

---

## content.json Format

```json
{
  "slides": [
    { "type": "title", "title": "Title", "subtitle": "Subtitle" },
    {
      "type": "agenda",
      "title": "Today's Agenda",
      "items": ["Item 1", "Item 2"]
    },
    { "type": "content", "title": "Body", "items": ["Bullet 1", "Bullet 2"] },
    { "type": "summary", "title": "Summary", "items": ["Point 1", "Point 2"] },
    { "type": "closing", "title": "Thank You" }
  ]
}
```

---

## Slide Type Usage

| Type      | Purpose                        | Has items          |
| --------- | ------------------------------ | ------------------ |
| `title`   | Title slide                    | Usually no         |
| `agenda`  | Table of contents / agenda     | Yes                |
| `content` | Body (bullet points)           | Yes                |
| `section` | Section divider                | Usually no         |
| `summary` | Summary (with bullets)         | Yes                |
| `closing` | Ending (Thank You, short text) | **No recommended** |

> ⚠️ **Note**: `closing` type is for short endings only. Use `content` or `summary` for bullet-point summaries.

---

## Image Embedding

To embed images in slides, use the `image` field.

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

### Image Options

| Property         | Description                          | Example                           |
| ---------------- | ------------------------------------ | --------------------------------- |
| `path`           | Local image path (relative/absolute) | `"images/diagram.png"`            |
| `url`            | Image URL (auto-downloaded)          | `"https://example.com/image.png"` |
| `position`       | Image placement                      | `"right"` / `"bottom"` / `"full"` |
| `width_percent`  | Width (% of slide width)             | `45`                              |
| `height_percent` | Height (for position=bottom)         | `50`                              |

### Position Behavior

| position | Behavior                            |
| -------- | ----------------------------------- |
| `right`  | Image on right, text on left        |
| `bottom` | Image at bottom, text at top        |
| `full`   | Image covers entire slide (no text) |

---

## Image Placement Best Practices

| Image Type   | Recommended position | width_percent | Notes             |
| ------------ | -------------------- | ------------- | ----------------- |
| Architecture | `right`              | 50-55         | Side-by-side text |
| Screenshot   | `right`              | 55-60         | Visible detail    |
| Flowchart    | `full`               | -             | Full slide        |
| Icon/Logo    | `right`              | 25-30         | Keep modest size  |

---

## Web Image Extraction Workflow

When generating PPTX from blog articles or technical docs, extract and place images automatically.

### 1. Extract Image URLs

```powershell
$base = "20251212_example_blog"
$url = "https://example.com/blog-post"

# Extract image URLs
$html = Invoke-WebRequest -Uri $url -UseBasicParsing
$html.Images | Select-Object -ExpandProperty src | Where-Object { $_ -match "image" }
```

### 2. Download Images

```powershell
New-Item -ItemType Directory -Path "images/${base}" -Force

$images = @(
    @{url="https://example.com/image1.png"; name="01_architecture.png"},
    @{url="https://example.com/image2.png"; name="02_workflow.png"}
)
foreach ($img in $images) {
    $outPath = "images/${base}/$($img.name)"
    Invoke-WebRequest -Uri $img.url -OutFile $outPath -UseBasicParsing
}
```

### 3. Place in content.json

```json
{
  "type": "photo",
  "title": "Architecture Overview",
  "items": ["Point 1", "Point 2"],
  "image": {
    "path": "images/20251212_example_blog/01_architecture.png",
    "position": "right",
    "width_percent": 55
  }
}
```

### Image Extraction Notes

1. **Naming convention**: `{number}_{description}.png` (e.g., `01_auth_flow.png`)
2. **Storage**: Store under `images/{base}/`
3. **Appropriate placement**: Place in relevant slides, not appendix
4. **Type**: Use `type: "photo"` for image-containing slides

---

## Code Blocks

For technical presentations, use the `code` field:

```json
{
  "type": "content",
  "title": "Implementation Example",
  "items": ["Point 1", "Point 2"],
  "code": "const result = await fetch('/api/data');\nconst data = await result.json();"
}
```

### Code Block Guidelines

- Max 10 lines per slide
- Use monospace font (auto-applied)
- Dark background for contrast (auto-applied)
- Explain key points in speaker notes

---

## Two-Column Comparison

Use `type: "two_column"` for comparisons:

```json
{
  "type": "two_column",
  "title": "Before vs After",
  "left_title": "Before",
  "left_items": ["Manual process", "Error-prone", "Time-consuming"],
  "right_title": "After",
  "right_items": ["Automated", "Reliable", "Fast"],
  "notes": "Emphasize the improvement in efficiency."
}
```

---

## References

- Basic flow: [template.instructions.md](template.instructions.md)
- Schema: `schemas/content.schema.json`
- Example: `schemas/content.example.json`
