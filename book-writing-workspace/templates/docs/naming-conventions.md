# File Naming Conventions

Naming rules for files and folders in the book project.

## Manuscript Files

### Pattern

```text
ch{chapter}-{number}_{title}.md
```

### Components

| Component   | Description              | Example                |
| ----------- | ------------------------ | ---------------------- |
| `{chapter}` | Chapter number (0-9)     | `0`, `1`, `5`          |
| `{number}`  | Sequence (00-99)         | `00`, `01`, `10`       |
| `{title}`   | Section title (Japanese) | `日常業務を爆速化する` |

### Examples

| Filename                              | Usage         |
| ------------------------------------- | ------------- |
| `ch0-00_Copilotで何が変わったのか.md` | Chapter 0     |
| `ch1-00_事例ギャラリー.md`            | Chapter 1     |
| `ch2-01_Excelタスク自動化.md`         | Chapter 2, #1 |
| `ch2-02_メール作成支援.md`            | Chapter 2, #2 |

## File Division Strategy

### Basic Principle

**1 file = 1 section**

### File Structure

Each chapter consists of:

- `ch{N}-00` = Chapter introduction (300-500 chars)
- `ch{N}-01` = Section 1 (2,000-6,000 chars)
- `ch{N}-02` = Section 2 (2,000-6,000 chars)
- `ch{N}-03` = Section 3 (2,000-6,000 chars)

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
