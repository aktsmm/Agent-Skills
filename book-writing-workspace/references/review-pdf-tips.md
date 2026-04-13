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

## URL Line Breaking

### Problem

Long URLs (especially reference links) overflow the page width in PDF output.
The default `review-jsbook.cls` defines `\UrlBreaks` but does not cover all characters,
and lacks aggressive line-break permissions.

### Solution

**Two changes are required** — LaTeX side and Ruby side:

#### 1. LaTeX: Add `xurl` + `emergencystretch`

Add `xurl` (a TeX Live standard package that extends `url` with permissive break points)
and `\emergencystretch` to the custom sty:

```latex
\usepackage{xurl}
\emergencystretch=3em
```

#### 2. Ruby: Override `inline_href` in `review-ext.rb`

Re:VIEW converts `@<href>{url, text}` to `\href{url}{\texttt{text}}`.
`xurl` only affects `\url{}` commands, so it does **not** break URLs inside `\href{\texttt{}}`.

Override `inline_href` in `review-ext.rb` to emit `\url{}` when the display text equals the URL:

```ruby
def inline_href(str)
  url, label = str.strip.split(/,\s*/, 2)
  if label.nil? || label.strip == url.strip
    "\\url{#{escape_url(url)}}"
  else
    "\\href{#{escape_url(url)}}{#{escape(label.strip)}}"
  end
end
```

> **Warning**: Adding `xurl` alone will appear to fix the build (no compile errors),
> but the PDF will still have overflowing URLs. Both changes are required.

### Where to Add

Place these lines in `review-custom.sty` or the build script's custom sty injection point.
Do **not** edit `sty/review-jsbook.cls` directly — the build script overwrites `sty/`
from the gem defaults on every run.

### Notes

- `xurl` is included in TeX Live and does not require separate installation in the Docker image
- `\emergencystretch=3em` gives LaTeX extra flexibility when it cannot find good break points
- `xurl` alone is **not enough** — the `inline_href` override is essential because Re:VIEW uses `\href{\texttt{}}` not `\url{}`

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

````markdown
```json API response example
{ "ok": true }
```
````

should produce a visible caption, while:

````markdown
```json
{ "ok": true }
```
````

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

## Footnote ID Collisions Across Combined Markdown Files

### Problem

Some book workflows concatenate multiple Markdown section files into one chapter-level `.re` file.
If each source file uses local footnote labels such as `[^1]`, `[^2]`, the same labels can repeat across files.
If the converter normalizes those labels directly into a shared namespace, later definitions may overwrite earlier ones or references may point to the wrong footnote body.

Another trap is treating any `[^id]:` substring as a footnote definition.
Inline prose such as `See note[^4]:` or list items ending with `[^1]:` still contain a reference followed by punctuation, not a footnote definition.

### Recommended Rule

- Namespace Markdown footnote labels per source file before converting them to final Re:VIEW footnote IDs
- Detect footnote definitions only at the start of a line
- Keep reference replacement active even when a colon immediately follows the closing bracket in prose or list items

### Example Strategy

If both `section-a.md` and `section-b.md` contain `[^1]`, rename them to source-scoped labels such as:

- `section_a_1`
- `section_b_1`

Do this before any final ID sanitization for Re:VIEW output.

### Verification

- Inspect a representative `.re` snippet and confirm that each `@<fn>{...}` points to the intended `//footnote[...]`
- Rebuild the final PDF after converter changes; checking only `.re` output is not enough when references can silently resolve to the wrong note body

## Table Notes and Footnotes

### Problem

In a Markdown -> Re:VIEW -> LaTeX -> PDF workflow, a note may semantically belong to a whole table,
but footnote markers placed inside table cells or even in the table header do not reliably become
page-bottom footnotes in the final PDF. Depending on the converter and LaTeX table environment,
the marker may disappear, remain inline, or fail to render as a normal bottom note.

### Recommended Rule

- If a note applies to the whole table, do not place the footnote marker inside a table cell
- Do not rely on table-header footnote markers for bottom-of-page notes
- Add one short prose sentence immediately before or after the table, and attach the footnote marker there
- Write the footnote body so it explicitly says the note applies to the table

### Example Strategy

Prefer this:

```markdown
#### Representative built-in classifiers

Note that, in the table below, Agreements, Resume, and Financial Statement are English-only as of May 2026[^1].

| Classifier | Description |
| ---------- | ----------- |
| Threat     | ...         |
| Agreements | ...         |

[^1]: In the table below, Agreements, Resume, and Financial Statement are English-only as of May 2026.
```

Avoid this:

```markdown
| Classifier[^1] | Description |
| -------------- | ----------- |
| Agreements     | ...         |
```

### Why This Works

- The note still reads as table-specific to the human reader
- The footnote marker stays in normal prose, which Re:VIEW and LaTeX handle more reliably
- The final PDF is less likely to lose the note or render it in an unexpected place

## Odd/Even Running Headers and Side Markers

### Problem

When designing chapter/section markers for the top margin or the left/right side margins,
it is easy to focus on `fancyhdr` slot configuration (`LE`, `RO`, etc.) and miss that the LaTeX
document class is still running in `oneside` mode. In that case, odd/even-specific placements
do not behave as expected, and layout experiments can appear to "do nothing".

Another trap is trying to derive chapter, section, and subsection labels from only one mark
stream. If multiple hierarchy levels need to be displayed at the same time, overloading a single
mark variable tends to produce blanks or stale labels.

### Recommended Rule

- Use `twoside` in `texdocumentclass` whenever odd/even page layout should differ
- Treat chapter and lower-level markers as separate responsibilities
- Prefer `leftmark` for stable chapter-level display
- Use `rightmark` for the currently active lower-level heading when appropriate
- If the design needs multiple hierarchy levels at once, keep separate stored values instead of trying to infer everything from one mark

### Practical Notes

- `oneside` can make odd/even `fancyhdr` settings appear broken even when the style file is correct
- Re:VIEW/jsbook-based stacks often behave more predictably when chapter-level display uses `leftmark`
- Verify the actual PDF result, not just the style file text

### Fastest Way to Isolate Header Problems

If an odd/even running header still does not show the expected chapter or section title,
first verify the slot itself before changing mark logic again.

- Temporarily replace the intended header content with a fixed literal such as `CHAPTER-TEST`
- Rebuild the PDF and check whether that literal appears in the target slot
- If the literal appears, the page-style slot is working and the remaining bug is in mark propagation or title capture
- If the literal does not appear, the issue is page style selection, `twoside` configuration, or viewer caching, not the mark text itself

This avoids repeated changes to `\chaptermark`, `\sectionmark`, or custom state variables when the real problem is elsewhere.

### Margin Labels: Prefer fancyhdr Before Page Overlay Packages

For vertical chapter/section labels placed in the side margins, prefer a `fancyhdr`-based approach first.

- Use `rotatebox` plus horizontal offset inside the appropriate `LE` / `RO` header slots
- Treat page-overlay packages such as `eso-pic` as a fallback, not the first choice

In Re:VIEW/jsbook-based stacks, `eso-pic` can conflict with other page-layout helpers such as `pxesopic` / `gentombow`, causing LaTeX build failures even when the layout idea itself is valid.

If a margin-label experiment unexpectedly breaks the build, remove the overlay package first and return to a plain `fancyhdr` implementation before debugging other parts of the style.

## PDF Viewer Cache During Layout Verification

### Problem

Running-header, footnote, or spacing changes are often verified by repeatedly rebuilding the same
PDF output filename. Some PDF viewers continue to show a cached version of the file even after the
build succeeded, which makes it look as though the latest style change had no effect.

### Recommended Rule

- Do not trust a same-name PDF tab alone when verifying layout changes
- Check the updated file timestamp after each build
- If the workflow archives previous builds into timestamped directories, compare against the newly archived copy as well
- When a result seems unchanged, verify the generated `.re` or `.tex` snippet before assuming the style edit failed

### Verification

- Confirm the output PDF modification time changed
- Open the latest archived/timestamped PDF when available
- Compare one representative `.re` snippet to the PDF page before continuing with further style changes

## Explicit Blank Lines Between Paragraphs

### Problem

In a Markdown -> Re:VIEW -> LaTeX -> PDF workflow, plain blank lines usually only mark paragraph boundaries.
They do not reliably create a visibly larger vertical gap in the final PDF.
Likewise, forcing line breaks with `@<br>{}` may end up as paragraph-internal `\\` and still fail to produce the intended blank line.

### Recommended Rule

- If you need a visibly larger gap in the PDF, do not rely on Markdown blank lines alone
- Use a hidden manuscript marker such as `<!-- review:br -->`
- Convert that marker in the Markdown-to-Re:VIEW script into a raw LaTeX vertical-space command

Recommended conversion target:

```review
//raw[|latex|\\par\\vspace{1em}]
```

This keeps the Markdown source readable while producing an explicit blank gap in PDF output.

### Why This Works

- Markdown blank lines: paragraph split only
- `@<br>{}`: may become `\\`, which is just a line break
- `\par\vspace{1em}`: ends the paragraph and inserts actual vertical space

### Example

Manuscript source:

```markdown
本文の締めです。

<!-- review:br -->
<!-- review:br -->

次の視点へ切り替えます。
```

Converter output:

```review
本文の締めです。

//raw[|latex|\\par\\vspace{1em}]
//raw[|latex|\\par\\vspace{1em}]

次の視点へ切り替えます。
```

### Practical Notes

- Keep the marker name stable across the workspace so authors can reuse it consistently
- Tune `1em` to `1.5em` or `2em` only after checking the actual PDF result
- Prefer this technique only when visual separation matters; for normal prose, paragraph breaks are usually enough

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

## Chapter Illustration on Blank Pages

When using `openright`, a blank even page is inserted before each chapter that
starts on an odd page. This blank page can be used to display an illustration
by overriding `\cleardoublepage` in `review-custom.sty`.

### Implementation

```latex
\makeatletter
% Track mainmatter state — illustration only in mainmatter
\newif\ifreview@inmainmatter
\review@inmainmatterfalse
\g@addto@macro\reviewmainmatterhook{%
  \review@inmainmattertrue
}

\let\review@origcleardoublepage\cleardoublepage
\renewcommand{\cleardoublepage}{%
  \clearpage
  \if@twoside
    \ifodd\c@page\else
      \thispagestyle{empty}%
      \ifreview@inmainmatter
        \edef\review@nextch{\the\numexpr\value{chapter}+1\relax}%
        \ifnum\review@nextch>0
          \ifnum\review@nextch<8  % adjust upper bound to your chapter count
            \null\vfill
            \begin{center}%
              \includegraphics[width=0.65\textwidth,height=0.65\textheight,keepaspectratio]{images/chapter-illustrations/ch\review@nextch}%
            \end{center}%
            \vfill
          \fi
        \fi
      \fi
      \newpage
      \if@twocolumn\hbox{}\newpage\fi
    \fi
  \fi
}
\makeatother
```

### File Naming

Place images as `images/chapter-illustrations/ch1.png`, `ch2.png`, etc.
Do **not** zero-pad (`ch01.png`) because `\thechapter` outputs `1`, not `01`.

### Build Prerequisites

Run `extractbb` on all illustration PNGs **before** `review-pdfmaker`:

```bash
cd /work && for f in images/chapter-illustrations/*.png; do extractbb "$f"; done
```

This generates `.xbb` bounding box files that `dvipdfmx` needs.

## Image Handling Pitfalls (dvipdfmx)

### `\IfFileExists` Does Not Find Image Files

In dvipdfmx environments, `\IfFileExists{images/foo.png}` always returns false
because `.png` is not in the `kpsewhich` search path. Use `\ifnum` conditions
on chapter numbers or `\openin` file-read tests instead.

### extractbb Paranoid Mode in Docker

TeX Live's default `openout_any = p` (paranoid) blocks writes to absolute paths.
`extractbb /work/images/foo.png` fails with `openout_any = p` error.
Always use relative paths: `cd /work && extractbb images/foo.png`.

### `\cleardoublepage` Fires in Frontmatter

The `\cleardoublepage` hook runs for all page transitions, including
title page → TOC. Without a mainmatter guard, images meant for ch1 can
appear on the blank page after the title page (where `chapter` counter = 0,
so `nextch` = 1). Always gate illustration insertion with a `\ifreview@inmainmatter`
flag set in `\reviewmainmatterhook`.

## Footnote Placement in Generated .re Files

### Problem

When a Markdown-to-Re:VIEW converter concatenates multiple Markdown files into one chapter `.re` file,
footnote definitions (`//footnote[id][text]`) are often appended at the end of the chapter.
Re:VIEW's LaTeX builder outputs `\footnotetext[N]{...}` at the position where `//footnote` appears
in the `.re` file. If all definitions are at the chapter end, every footnote in the chapter clusters
on the last few pages of the PDF instead of appearing at the bottom of the page where it is referenced.

### Additional Trap: Nested Blocks

Moving `//footnote` to right after the reference line is not always sufficient.
If the reference is inside a block such as `//table{...//}` that is itself nested inside
a column block (`===[column]...===[/column]`), placing the footnote after the inner `//}` still
leaves it inside the column. Re:VIEW renders columns with `tcolorbox`, and `\footnotetext` inside
`tcolorbox` triggers a `Counter too large` LaTeX error that aborts the build entirely.

### Recommended Rule

1. After generating all `.re` content, redistribute `//footnote` definitions from the chapter end to immediately after their reference locations
2. If the reference is inside any block, place the footnote after the **outermost** enclosing block (where depth returns to 0), not just the innermost `//}`
3. Track block depth for both brace-delimited blocks (`//xxx{...//}`) and column blocks (`===[column]...===[/column]`)
4. Footnotes with no matching reference (unused) stay at chapter end

### Verification

- Check that `//footnote` lines appear near their `@<fn>{}` references in the `.re` file, not all at the end
- Confirm no `//footnote` is inside a `//table{...//}` or `===[column]...===[/column]` block
- Build the full PDF and check that footnotes appear at the bottom of the referencing page, not clustered at chapter end
- Watch for `Counter too large` errors — they indicate a footnote is still inside a tcolorbox-rendered block

### Template Threshold for Skipping Files

When the converter skips files below a character-count threshold to exclude templates,
keep the threshold low enough that short but real content (e.g., a heading + one paragraph + an image reference)
is not silently dropped from the PDF. A threshold around 200 characters for normal section files is
a practical balance; 300 characters can silently skip valid content.
