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
