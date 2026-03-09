# File Naming Conventions

Naming rules for files and folders in the book project.

## Manuscript Files

### Pattern

```text
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

## Image Files

### Pattern

```text
fig-{chapter}-{section}-{number}.{ext}
```

### Extensions

| Extension | Usage                     |
| --------- | ------------------------- |
| `.png`    | Screenshots, diagrams     |
| `.jpg`    | Photographs               |
| `.pdf`    | Vector graphics for print |

## Re:VIEW Files

### Pattern

```text
ch{NN}-{slug}.re
```

### Examples

| Filename        | Chapter    |
| --------------- | ---------- |
| `preface.re`    | Chapter 0  |
| `ch01-intro.re` | Chapter 1  |
| `postscript.re` | Conclusion |

## Notes

1. Spaces are OK in folder titles
2. Japanese is OK in visible titles
3. Keep IDs alphanumeric and half-width
