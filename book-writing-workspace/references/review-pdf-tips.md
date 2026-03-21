# Re:VIEW PDF Build Tips

Practical tips for customizing PDF output with Re:VIEW 5.x and the `vvakame/review` Docker image.

## Font Selection

Add `jafont=<preset>` to `texdocumentclass` options in `config.yml`:

```yaml
texdocumentclass:
  [
    "review-jsbook",
    "media=ebook,paper=b5,...,jafont=noto-otf",
  ]
```

### Available Presets (vvakame/review:5.9)

| Preset      | Mincho (Body)            | Gothic (Headings)        | Notes                          |
| ----------- | ------------------------ | ------------------------ | ------------------------------ |
| (default)   | IPAex Mincho             | IPAex Gothic             | Classic, slightly dated        |
| `haranoaji` | Harano Aji Mincho        | Harano Aji Gothic        | TeX Live default, sharp        |
| `noto-otf`  | Noto Serif CJK JP        | Noto Sans CJK JP         | Google/Adobe, rich weights     |

> `noto-otf` provides ExtraLight through Black weights and is pre-installed in the Docker image.

## TOC Depth Control

### Problem

`config.yml`'s `tocdepth` setting maps to `\def\review@tocdepth{N}` in the generated `.tex`.
However, Re:VIEW's `\reviewtableofcontents` macro applies this value **after** document begin,
so neither direct `\setcounter{tocdepth}` nor `\AtBeginDocument` in `review-style.sty` can override it.

### Solution

Redefine `\review@tocdepth` itself in `review-style.sty`:

```latex
\makeatletter
\def\review@tocdepth{1}
\makeatother
```

### Depth Values

| Value | Shows in TOC               | Markdown equivalent |
| ----- | -------------------------- | ------------------- |
| 0     | Chapter (`#`) only         | `#`                 |
| 1     | + Section (`##`)           | `#`, `##`           |
| 2     | + Subsection (`###`)       | `#`, `##`, `###`    |

### Build Script Integration

When using a build script that injects styles via `printf >> sty/review-style.sty`:

```bash
printf '%s\n' \
  '% TOC depth: show only chapter and section' \
  '\makeatletter' \
  '\def\review@tocdepth{1}' \
  '\makeatother' \
  >> /work/sty/review-style.sty
```

## Header/Footer Customization

Custom headers and footers can be injected into `review-style.sty` using `fancyhdr`:

```latex
\fancyhead{}
\fancyhead[LE]{\gtfamily\sffamily\bfseries\upshape \leftmark}
\fancyhead[RO]{\gtfamily\sffamily\bfseries\upshape \rightmark}
\fancypagestyle{plain}{%
  \fancyhead{}
  \fancyfoot{}
  \fancyfoot[LE,RO]{\thepage}
  \renewcommand{\headrulewidth}{0pt}
  \renewcommand{\footrulewidth}{0pt}
}
```

## Debugging

- Add `--debug` to `review-pdfmaker` to keep the build directory for inspection
- Check `sty/review-style.sty` inside the build directory to verify injected settings
- Use `grep -rn 'tocdepth' sty/ *.tex` to trace where values are set
- Use `pdftotext output.pdf -` to verify TOC content without opening a viewer
