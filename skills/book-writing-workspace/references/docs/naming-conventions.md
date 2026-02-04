# File Naming Conventions

Naming rules for files and folders in the book project.

---

## Manuscript Files (Markdown)

### Pattern

```
{prefix}-{chapter}-{section}-{number}_{title}.md
```

### Components

| Component   | Description                       | Example          |
| ----------- | --------------------------------- | ---------------- |
| `{prefix}`  | Fixed prefix (01 for manuscripts) | `01-`            |
| `{chapter}` | Chapter number (0-9)              | `1`, `5`         |
| `{section}` | Section letter (a-z, 0 for intro) | `a`, `0`         |
| `{number}`  | Sequence (00-99)                  | `00`, `01`, `10` |
| `{title}`   | Section title                     | `Introduction`   |

### Number Rules

| Number    | Usage                |
| --------- | -------------------- |
| `00`      | Section introduction |
| `01`-`09` | Main subsections     |
| `10`-`19` | Columns/sidebars     |

### Examples

```
01-1-a-00_Section_Introduction.md    # Chapter 1, Section a, intro
01-1-a-01_First_Topic.md             # Chapter 1, Section a, topic 1
01-1-a-10_[Column]_Example.md        # Chapter 1, Section a, column
01-5-0-00_Chapter_Overview.md        # Chapter 5, no section
```

---

## Image Files

### Pattern

```
fig-{chapter}-{section}-{number}.{ext}
```

### Examples

| Filename         | Description                   |
| ---------------- | ----------------------------- |
| `fig-5-a-01.png` | Chapter 5, Section a, image 1 |
| `fig-2-c-02.png` | Chapter 2, Section c, image 2 |

### Prefixes (Optional)

| Prefix   | Usage              |
| -------- | ------------------ |
| `fig-`   | Diagrams (default) |
| `tbl-`   | Table images       |
| `icon-`  | Icons, logos       |
| `photo-` | Photographs        |

### Extensions

| Extension | Usage                               |
| --------- | ----------------------------------- |
| `.png`    | Screenshots, diagrams (recommended) |
| `.jpg`    | Photographs                         |
| `.pdf`    | Vector graphics (print)             |

---

## Folder Structure

```
{project}/
├── 01_contents_keyPoints/
│   └── {N}. {Chapter Title}/
│       └── {section}. {Section Title}/
├── 02_contents/
│   └── {N}. {Chapter Title}/
│       └── {section}. {Section Title}/
├── 04_images/
│   └── {N}_{Chapter_Title}/
```

---

## Re:VIEW Files

### Pattern

```
ch{NN}-{slug}.re
```

### Examples

| Filename               | Chapter                  |
| ---------------------- | ------------------------ |
| `preface.re`           | Chapter 0 (Introduction) |
| `ch01-intro.re`        | Chapter 1                |
| `ch05-tools.re`        | Chapter 5                |
| `postscript.re`        | Conclusion               |
| `appendix-glossary.re` | Glossary                 |

---

## Commit Messages

### Format

```
{verb} {target} {detail}
```

### Verbs

| Verb     | Usage            |
| -------- | ---------------- |
| Add      | New file/feature |
| Fix      | Bug/typo fix     |
| Update   | Content update   |
| Delete   | Remove file      |
| Refactor | Structure change |

### Examples

```
Add ch05-a Microsoft Purview overview
Fix ch01 typo correction
Update writing.instructions.md word count
```

---

## Notes

1. **Spaces**: OK in folder/title, use hyphens in ID portion
2. **Japanese**: OK in titles, alphanumeric + hyphen for IDs
3. **Case**: Lowercase for English (except titles)
4. **Width**: Half-width for numbers/letters, full-width for Japanese
