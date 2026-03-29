# Re:VIEW PDF Build Tips

Practical tips for customizing PDF output with Re:VIEW 5.x and the `vvakame/review` Docker image.

## Font Selection

Add `jafont=<preset>` to `texdocumentclass` options in `config.yml`:

```yaml
texdocumentclass: ["review-jsbook", "media=ebook,paper=b5,...,jafont=noto-otf"]
```

### Available Presets (vvakame/review:5.9)

| Preset      | Mincho (Body)     | Gothic (Headings) | Notes                      |
| ----------- | ----------------- | ----------------- | -------------------------- |
| (default)   | IPAex Mincho      | IPAex Gothic      | Classic, slightly dated    |
| `haranoaji` | Harano Aji Mincho | Harano Aji Gothic | TeX Live default, sharp    |
| `noto-otf`  | Noto Serif CJK JP | Noto Sans CJK JP  | Google/Adobe, rich weights |

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

| Value | Shows in TOC         | Markdown equivalent |
| ----- | -------------------- | ------------------- |
| 0     | Chapter (`#`) only   | `#`                 |
| 1     | + Section (`##`)     | `#`, `##`           |
| 2     | + Subsection (`###`) | `#`, `##`, `###`    |

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

## Font Size Tuning

Changing font size requires adjusting multiple parameters together.
Add all values to `texdocumentclass` in `config.yml`:

| Setting           | 10pt (default) | 9pt (compact) |
| ----------------- | -------------- | ------------- |
| `fontsize`        | 10pt           | 9pt           |
| `baselineskip`    | 15.4pt         | 13.5pt        |
| `line_length`     | 40zw           | 43zw          |
| `number_of_lines` | 35             | 38            |
| Chars/page (est.) | ~585           | ~740          |

Example (9pt):

```yaml
texdocumentclass:
  [
    "review-jsbook",
    "media=ebook,paper=b5,serial_pagination=true,openright,fontsize=9pt,baselineskip=13.5pt,line_length=43zw,number_of_lines=38,head_space=30mm,headsep=10mm,headheight=5mm,footskip=10mm,jafont=noto-otf",
  ]
```

## Chapter Opening on Right Page

Use `openright` instead of `openany` in `texdocumentclass` options.
This ensures every `#` (chapter) starts on an odd (right-side) page.
If the previous chapter ends on an odd page, a blank even page is inserted automatically.

## Chapter Title Page (Full Page)

Override `\@makechapterhead` in `review-custom.sty` to make the chapter title
occupy a full page with centered layout and decorative rules:

```latex
\makeatletter
\renewcommand{\@makechapterhead}[1]{%
  \vspace*{3cm}%
  \begin{center}%
    {\Large\headfont \@chapapp\thechapter\@chappos}%
    \par\vskip 12pt%
    {\rule{0.6\textwidth}{0.5pt}}%
    \par\vskip 16pt%
    {\Huge\headfont #1}%
    \par\vskip 12pt%
    {\rule{0.6\textwidth}{0.5pt}}%
  \end{center}%
  \clearpage%
}
\makeatother
```

The `\clearpage` at the end forces the first `##` (section) to start on the next page.

> **Pitfall**: Do not use `\renewcommand{\reviewchapterhead}` — this macro does not exist
> in Re:VIEW 5.x. Use `\@makechapterhead` (standard jsbook) instead.
> Also avoid `\\` (line break) in `\@makechapterhead`; use `\par\vskip` for spacing.

## Code Block Auto-Wrapping with review-ext.rb

Long code lines that exceed the page width can be automatically wrapped at build time
using a `review-ext.rb` extension with the `unicode-display_width` gem.

### Setup

1. Place `review-ext.rb` in the Re:VIEW project root (same directory as `config.yml`)
2. Install the gem at build time:

```bash
gem install unicode-display_width --no-document
```

3. Adjust `WRAP_WIDTH` constants for your font size and line length:

| Font Size | line_length | Recommended WRAP_WIDTH |
| --------- | ----------- | ---------------------- |
| 10pt      | 40zw        | 76                     |
| 9pt       | 43zw        | 82                     |

### How It Works

The extension overrides `code_line` and `code_line_num` in `LATEXBuilder`.
When a line exceeds `WRAP_WIDTH` display columns, it should split at spaces
or delimiters such as `/`, `-`, `_`, `.`, `:` when possible, and only fall back
to character-level wrapping when no safe break point exists.

Do not inject visible continuation markers such as `↵` into the PDF output.
They tend to look like mojibake or converter garbage in review screenshots.

See `templates/review-ext.rb` for a ready-to-use template.

### Practical Rules

- Prefer delimiter-aware wrapping over raw character-count splitting
- Do not add visible wrap markers to wrapped code lines
- Keep a last-resort hard wrap for single long tokens that exceed line width

## Code Fence Captions

### Problem

If a Markdown code fence has a language but no explicit caption, some converters
accidentally promote the language name itself (`text`, `json`, `markdown`) into a
visible list caption. This looks like converter noise in the final PDF.

### Recommended Rule

- Treat the first fence token as the syntax/language only
- Only emit a visible Re:VIEW list caption when the fence info contains an explicit caption
- When the caption is omitted, still emit the required Re:VIEW block arguments, but keep the caption empty

Example:

~~~markdown
```json API response example
{ "ok": true }
```
~~~

should produce a visible caption, while:

~~~markdown
```json
{ "ok": true }
```
~~~

should not show `json` as the caption.

## Reference URLs Inside Bullet Lists

### Problem

In Markdown manuscripts, authors often write references as a bullet title followed by a URL on
the next indented line. During Markdown -> Re:VIEW -> LaTeX conversion, that newline may collapse
back into a space inside list items, causing long URLs to run across the page and get clipped.

### Recommended Rule

- Write manuscript references in two lines inside the same list item
- Put the title on the first line
- Put the URL itself as a link on the next indented line
- In the converter, emit an explicit line break before link-only continuation lines

Example manuscript form:

```markdown
- GitHub Docs: GitHub Copilot policies
  [https://docs.github.com/en/copilot/concepts/policies](https://docs.github.com/en/copilot/concepts/policies)
```

This keeps the title readable and prevents long URLs from relying on implicit line wrapping alone.

## Markdown Backslash Escapes in PDF Output

### Problem

Markdown allows backslash escapes such as `\_`, `\*`, `` \` ``, `\\` to prevent
special characters from being interpreted as formatting. When converting Markdown
to Re:VIEW (`.re`), these escapes may pass through literally, producing visible
backslashes in the PDF output (e.g. `yuyanz\_` instead of `yuyanz_`).

### Solution

Add an unescape step in the Markdown-to-Re:VIEW conversion script's inline
processing, **after** protecting code spans but **before** applying bold/italic
transformations:

```python
# Unescape Markdown backslash escapes (e.g. \_ -> _)
text = re.sub(r"\\([_*`\\])", r"\1", text)
```

This must run before bold/italic regex matching so that `\_` is reduced to `_`
before the `*...*` patterns are evaluated.

### Affected Elements

- Headings (`## Yuya（yuyanz\_）` → shows backslash in section title)
- Body text (e.g. `file\_name` → shows backslash in prose)
- Any inline context processed by `replace_inline()`

## Markdown Image Caption vs Layout Metadata

### Problem

When Markdown images are converted to Re:VIEW, the image alt text and optional title
often get mixed together. If authors put manual figure numbering such as `Image: ...`
or `図 01` into alt text, the final PDF can end up with duplicated numbering because
Re:VIEW already manages figure numbering.

Another common issue is using the title field as if it were a second caption.
For example, `![Caption](images/foo.png "scale=0.80")` should treat `scale=0.80`
as layout metadata, not as visible caption text.

### Recommended Rule

- Use alt text for the visible caption only
- Do not put manual numbering such as `図 01`, `Figure 1`, or `Image:` into alt text
- Use the Markdown image title only for layout metadata such as `scale=0.80`
- If no caption is provided, let the converter fall back to the file stem or another deterministic rule

## Markdown Tables Need `//tsize` for PDF Wrapping

### Problem

When Markdown pipe tables are converted to plain Re:VIEW `//table{}` blocks without a matching
`//tsize`, LaTeX PDF output often falls back to fixed-width-free columns such as `|l|l|l|`.
In that mode, long Japanese prose inside cells does not wrap correctly and can run past the page edge.

This tends to surface in tables where the last column contains explanatory sentences, for example:

- tool comparison tables
- role / usage / notes matrices
- long scenario descriptions in 3-column tables

### Solution

Emit a LaTeX-specific `//tsize` immediately before the generated `//table{}` block:

```review
//tsize[|latex||L{27mm}|L{36mm}|L{63mm}|]
//table{
項目	説明	利用シーン
------------------------------------------------------------
...
//}
```

### Practical Rule

- Use `L{...mm}` columns for any table column that may need wrapping
- Reserve the widest column for prose-heavy cells, usually the last column
- Generate widths automatically in the Markdown-to-Re:VIEW converter when possible
- Keep the total width aligned to the actual PDF text area used by the project

### Why This Matters

Even if the manuscript source looks fine in Markdown, the PDF builder only wraps table cells when
the LaTeX column spec supports wrapping. If a project relies on auto-generated Re:VIEW, table layout
must be handled in the converter, not left to authors to patch by hand after every build.

### Recommended Pattern

```markdown
![Agent モードの選択](images/docmng_img02.png "scale=0.80")
```

This should become a Re:VIEW image block where:

- caption = `Agent モードの選択`
- metric = `scale=0.80`

### Anti-Patterns

```markdown
![Image: Agent モードの選択](images/docmng_img02.png)
![図 01. Agent モードの選択](images/docmng_img02.png)
![Agent モードの選択](images/docmng_img02.png "図 01")
```

These patterns make later conversion and numbering brittle.
