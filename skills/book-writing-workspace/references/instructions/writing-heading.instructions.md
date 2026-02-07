---
applyTo: "02_contents/**/*.md"
---

# Heading Level Instructions

Rules for Markdown heading levels in manuscripts.

## Basic Rules

| File Type                     | Allowed Levels      | Start With |
| ----------------------------- | ------------------- | ---------- |
| Chapter intro (`*-0-00_*.md`) | `#`, `##`, `###`    | `#`        |
| Section file                  | `##`, `###`, `####` | `##`       |
| Column/sidebar                | `##`, `###`         | `##`       |

## Why This Matters

- Chapter files define the chapter title with `#`
- Section files are **part of** a chapter, so they start with `##`
- This ensures correct hierarchy in PDF/EPUB output

## Examples

### ✅ Correct (Section file)

```markdown
## Section Title

Content here...

### Subsection

More content...
```

### ❌ Wrong (Section file with `#`)

```markdown
# Section Title ← ERROR: Should be

Content here...
```

## P1 Violation

Using `#` in a section file is a **P1 (Critical)** issue and will be flagged during review.

## Quick Check

Before submitting:

1. Is this a chapter intro file (`*-0-00_*.md`)? → `#` is OK
2. Is this a section file? → Must start with `##`
