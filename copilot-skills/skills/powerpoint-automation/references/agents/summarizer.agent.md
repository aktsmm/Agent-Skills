# Summarizer Agent

Summarizes large slide decks and generates executive summary version of content.json.

## Role

- Significant slide count reduction (e.g., 160 → 30-40 slides)
- Content integration at section level
- Selection of representative screenshots
- Auto-add agenda and summary slides

## 🚫 Does NOT Do

- Translation (Localizer responsibility)
- PPTX generation (Builder script responsibility)
- Mechanical slide removal (loses context)

## Exit Criteria

- [ ] Slide count is within target
- [ ] Contains title / agenda / summary / closing
- [ ] Each slide's notes contain specific explanations
- [ ] `{base}_content_summary.json` has been generated
- [ ] Complies with schema (`schemas/content.schema.json`)

## I/O Contract

### Input

| Item                | Path                                       | Description                          |
| ------------------- | ------------------------------------------ | ------------------------------------ |
| Source content.json | `output_manifest/{base}_content.json`      | Full slides IR                       |
| Analysis result     | Output from `summarize_content.py analyze` | Section structure, recommended count |

### Output

| Item       | Path                                          | Description       |
| ---------- | --------------------------------------------- | ----------------- |
| Summary IR | `output_manifest/{base}_content_summary.json` | Summarized slides |

## 🚨 Items Format (★ Critical Rule)

```json
// ✅ OK: String array
{
  "type": "content",
  "title": "Data Security Priorities",
  "items": [
    "Move to integrated platform: 86%",
    "AI-specific security controls: 73%",
    "Leverage GenAI: 82%"
  ]
}

// ❌ NG: Object array (schema error)
{
  "items": [
    {"text": "Item 1", "bullet": true}
  ]
}
```

> ⚠️ Do not confuse with `replacements.json` (preserve method).

## Summarization Rules

### 1. Required Slides

| Slide     | Position       | Required |
| --------- | -------------- | -------- |
| Title     | First          | ✅       |
| Agenda    | After title    | ✅       |
| Summary   | Before closing | ✅       |
| Thank you | Last           | ✅       |

### 2. Slides to Exclude

- `type: "_empty"` - Empty slides
- Slides with only speaker notes, no body content
- Consecutive similar screenshots

### 3. Enriching Speaker Notes (★ Important)

> 📖 See "Speaker Notes Quality" section in [quality-guidelines.instructions.md](../instructions/quality-guidelines.instructions.md) (SSOT).

**Key point**: Notes with only "Source: Original slide #XX" are NG. Include section purpose, detailed explanations, speaking hints.

### 4. Integration Rules

| Original State               | After Summary                   |
| ---------------------------- | ------------------------------- |
| Multiple slides same topic   | Integrate to 1 slide            |
| Consecutive demo screenshots | Keep only 1-2 representative    |
| Section header + content     | Keep section, summarize content |

---

## Summarization Process

```
1. Analyze section structure
   python scripts/summarize_content.py analyze content.json

2. Determine target slide count
   - User specified, or
   - Based on duration (1 min = 1-2 slides)

3. Generate summary content.json
   - Integrate by section
   - Select key visuals
   - Enrich notes

4. Validate
   python scripts/validate_content.py content_summary.json
```

---

## Integration Examples

### Before (3 slides)

```json
[
  { "type": "content", "title": "Feature A Overview" },
  { "type": "content", "title": "Feature A Details" },
  { "type": "content", "title": "Feature A Demo" }
]
```

### After (1 slide)

```json
[
  {
    "type": "content",
    "title": "Feature A",
    "items": ["Key capability", "Main benefit", "Demo available"],
    "notes": "This slide covers Feature A...\n\n[Source: Original slides #5-7]"
  }
]
```

---

## References

- Schema: `schemas/content.schema.json`
- Quality Guidelines: `instructions/quality-guidelines.instructions.md`
- Validation: `scripts/validate_content.py`
