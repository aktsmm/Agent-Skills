---
applyTo: "02_contents/**/*.md"
---

# Heading Level Instructions

Rules for Markdown heading levels in manuscripts.

## Basic Rules

| File Type                     | Allowed Levels      | Start With |
| ----------------------------- | ------------------- | ---------- |
| Chapter intro (`ch*-00_*.md`) | `#`, `##`, `###`    | `#`        |
| Section file                  | `##`, `###`, `####` | `##`       |
| Column/sidebar                | `##`, `###`         | `##`       |

## Why This Matters

- Chapter files define the chapter title with `#`
- Section files are **part of** a chapter, so they start with `##`
- This ensures correct hierarchy in PDF/EPUB output

## Examples

### Correct

```markdown
## Section Title

Content here...

### Subsection

More content...
```

### Wrong

```markdown
# Section Title

Content here...
```

Using `#` in a section file is a P1 issue.
