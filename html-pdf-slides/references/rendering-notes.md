# Rendering Notes

## Fit and overflow

- Auto-fit: render a content slide at a descending set of font sizes (e.g. 16 → 12.5 px) via the `--fs` CSS variable and keep the largest that has zero overflow; if none fits, move secondary cards to a continuation page with its own fit loop.
- Overflow = card bottoms below the footer top, or `scrollHeight > clientHeight` of the columns. Checking only `scrollHeight` misses flex columns that overlap the footer.
- Under `tsx`/esbuild, pass a *string* to `page.evaluate`; a function breaks with `__name is not defined`.
- Wait for `document.fonts.ready` before measuring or printing. On Linux install a CJK font package (e.g. Noto CJK).

## Page size

Chrome prints a 1280×720 px page as **960×540 pt**. If you add pages with pdf-lib, create them at 960×540 pt and scale drawing by 0.75; otherwise cover/ending appear larger than slides.

## Bundling pages in a browser (static site)

- Pre-render one PDF per item; merge only the selected ones client-side with pdf-lib (`copyPages` keeps links), drawing cover / TOC with page numbers / summary / ending yourself.
- Japanese text in pdf-lib needs an embedded font. A variable CJK font lost glyphs; instantiate one static weight (`fontTools.varLib.instancer wght=400`), subset to JIS X 0208 + ASCII + symbols (`--layout-features=` empty), and embed with `subset: false` (≈ 2.3 MB). Verify by viewing a page.
- Keep generated PDFs out of Git; generate at deploy.

## Data-driven decks

Keep content as schema-validated JSON and generate the HTML from it (escape every field; apply `**bold**` only after escaping). Validate before rendering; skip a bad item with a warning instead of failing the whole build.
