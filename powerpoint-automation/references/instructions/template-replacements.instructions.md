# Template: replacements.json Format

Detailed specification for replacements.json used in Localizer method (text replacement).

> 📖 See [template.instructions.md](template.instructions.md) for basic flow.
> ⚠️ **Note**: This format is for preserve method (experimental). Recommended is content.json format (reconstruct method).

---

## Basic Structure

```json
{
  "slide-0": {
    "shape-0": {
      "paragraphs": [
        {
          "text": "New Title",
          "font_size": 52.0,
          "bold": true
        }
      ]
    }
  },
  "slide-1": {
    "shape-0": {
      "paragraphs": [
        {
          "text": "New Heading"
        }
      ]
    },
    "shape-1": {
      "paragraphs": [
        { "text": "Item 1", "bullet": true, "level": 0 },
        { "text": "Item 2", "bullet": true, "level": 0 },
        { "text": "Sub-item", "bullet": true, "level": 1 }
      ]
    }
  }
}
```

---

## Paragraph Properties

| Property    | Type   | Required | Description        | Example   |
| ----------- | ------ | -------- | ------------------ | --------- |
| `text`      | string | ✅       | Text content       | "Heading" |
| `bullet`    | bool   | -        | Bullet point flag  | true      |
| `level`     | int    | -        | Indent level (0-8) | 0         |
| `bold`      | bool   | -        | Bold               | true      |
| `italic`    | bool   | -        | Italic             | false     |
| `alignment` | string | -        | Alignment          | "CENTER"  |
| `font_size` | float  | -        | Font size (pt)     | 24.0      |
| `font_name` | string | -        | Font name          | "Arial"   |

### alignment Values

| Value   | Description  |
| ------- | ------------ |
| LEFT    | Left align   |
| CENTER  | Center align |
| RIGHT   | Right align  |
| JUSTIFY | Justify      |

---

## 🚨 Bullet Point Format (Critical)

> **Manual bullet characters are prohibited. Always use `bullet: true`.**

### ❌ NG Patterns

```json
// ❌ NG: Manual symbols
{ "paragraphs": [{ "text": "• Item 1\n• Item 2" }] }

// ❌ NG: Symbols in text
{ "paragraphs": [{ "text": "- Item 1" }] }
```

### ✅ OK Pattern

```json
// ✅ OK: Use bullet property
{
  "paragraphs": [
    { "text": "Item 1", "bullet": true, "level": 0 },
    { "text": "Item 2", "bullet": true, "level": 0 },
    { "text": "Sub-item", "bullet": true, "level": 1 }
  ]
}
```

### Prohibited Characters (in text)

`•` `・` `●` `○` `◆` `◇` `▪` `▫` `-` `*` `+` `①` `②` `③` ...

---

## Common Errors and Solutions

### Failure ①: Content Becomes Empty

```json
// ❌ NG: Not using paragraphs array
"shape-0": "Title text"
"shape-0": { "text": "Title" }

// ✅ OK: paragraphs array required
"shape-0": { "paragraphs": [{ "text": "Title" }] }
```

### Failure ②: Overflow Error

| inventory height | Recommended text amount |
| ---------------- | ----------------------- |
| ≤ 0.5 inches     | 1 line only             |
| 0.5 - 1.5 inches | 1-2 lines               |
| 1.5 - 3.0 inches | 3-5 lines               |
| ≥ 3.0 inches     | 5-8 lines               |

### Failure ③: Shapes replaced: 0

**Cause:** paragraphs structure error or shape-id mismatch

---

## Text Amount Guidelines

| Element     | Recommended | Maximum   |
| ----------- | ----------- | --------- |
| Title       | 20 chars    | 40 chars  |
| Heading     | 15 chars    | 30 chars  |
| Bullet item | 20 chars    | 40 chars  |
| Paragraph   | 50 chars    | 100 chars |

---

## References

- Basic flow: [template.instructions.md](template.instructions.md)
- Implementation: `scripts/apply_content.py`
