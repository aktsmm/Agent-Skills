# Purpose: Blog to Presentation Instructions

Rules for converting blog articles to presentations.

> 📰 **Target**: Tech blogs, Qiita, Zenn, Medium, internal wikis, official documentation

---

## Workflow

```
1. Fetch article content (API or fetch_webpage)
     ↓
2. ★ Extract image URLs & download (images/{base}/)
     ↓
3. Calculate slide count: base + image count
     ↓
4. Create content.json (type: "photo" for images)
     ↓
5. Generate PPTX
```

---

## Slide Count Guidelines

| Article Length      | Without Images | With Images  | Basis           |
| ------------------- | -------------- | ------------ | --------------- |
| Short (~1500 chars) | 6-8 slides     | 10-14 slides | 300 chars/slide |
| Medium (1500-4000)  | 10-14 slides   | 15-20 slides | steps × 1.5     |
| Long tech (4000+)   | 14-18 slides   | 20-30 slides | sections × 3-4  |

---

## Required Slide Structure

| Position | Slide Type | Required |
| -------- | ---------- | -------- |
| 1        | Title      | ✅       |
| 2        | Agenda     | ✅       |
| 3-N      | Content    | ✅       |
| N-1      | Summary    | ✅       |
| N        | Closing    | ✅       |

---

## Image Handling

### Extraction

```powershell
$base = "20251212_example_blog"
$url = "https://zenn.dev/xxx/articles/yyy"

# Fetch HTML source
$html = curl -s $url

# Extract image URLs
$imageUrls = [regex]::Matches($html, 'https://[^"]+\.(png|jpg|jpeg|gif|webp)')

# Download images
$i = 1
foreach ($imgUrl in $imageUrls) {
    curl -s -o "images/${base}/$('{0:D2}' -f $i)_image.png" $imgUrl
    $i++
}
```

### Placement

| Image Type   | position | width_percent | Notes             |
| ------------ | -------- | ------------- | ----------------- |
| Architecture | `right`  | 50-55         | Side-by-side text |
| Screenshot   | `right`  | 55-60         | Visible detail    |
| Flowchart    | `full`   | -             | Full slide        |
| Icon/Logo    | `right`  | 25-30         | Keep small        |

---

## Code Block Handling

### When to Include

- Core implementation examples
- Configuration snippets
- Command examples

### Format in content.json

```json
{
  "type": "content",
  "title": "Implementation Example",
  "items": ["Point 1", "Point 2"],
  "code": "<button hx-get=\"/api/data\">Fetch</button>"
}
```

### Guidelines

- Max 10 lines per slide
- Remove imports unless critical
- Highlight key parts in speaker notes
- Consider splitting into multiple slides

---

## Speaker Notes

For each content slide, include:

1. **Context**: Why this point matters
2. **Details**: Additional explanation not on slide
3. **Speaking hints**: Emphasis, transitions
4. **Source**: `[Source: Article section "XXX"]`

---

## Quality Checklist

- [ ] All main images extracted
- [ ] Code blocks under 10 lines
- [ ] Agenda lists all sections
- [ ] Summary captures key points
- [ ] Speaker notes enriched
- [ ] Citations included
