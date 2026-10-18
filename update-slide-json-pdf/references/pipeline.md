# Pipeline & Gotchas

## Rendering (HTML → PDF)

- Fixed 1280×720 px page; escape every field, apply `**bold**` only after escaping; links https + allowlisted host.
- **Font fit loop**: try font sizes from large to small (e.g. 16 → 12.5 px) and take the largest that fits; if none fits, move detail panels to a continuation page that has its own fit loop. Do not shrink below readability to hide overload.
- **Overflow check must compare card bottoms with the footer top**, not only `scrollHeight`: flex columns can overlap the footer without any scroll overflow.
- Under `tsx`/esbuild, a function passed to `page.evaluate` fails with `__name is not defined`; pass a string expression instead.
- Chrome writes a 1280×720 px page as **960×540 pt**. Pages drawn later with pdf-lib must be created at 960×540 pt and scaled 0.75 (`concatTransformationMatrix`), otherwise cover/ending look one size bigger than slides.
- On Linux runners install a CJK font package before rendering.

## Browser-side merge (static site)

- Pre-render one PDF per item at deploy; keep PDFs out of Git; limit publication to a retention window (e.g. last 3 months) to bound size.
- pdf-lib + fontkit draws cover / TOC (with page numbers computed from per-item page counts) / summary / ending, and `copyPages` appends the per-item PDFs (links survive).
- **CJK font**: a variable Noto Sans JP file lost glyphs (garbled / missing characters). Instantiate a static weight (`fontTools.varLib.instancer wght=400`), subset to JIS X 0208 + ASCII + common symbols (`--layout-features=` empty, `--glyph-names`), and embed with pdf-lib `subset: false`. Result ≈ 2.3 MB, loaded only when the user presses download. Always view a page image to verify.
- JSON download = selection conditions + items + slide JSON, built client-side from the same filtered list the page shows.

## Browser-side PPTX (editable)

- Generate with `pptxgenjs` in the browser from the same slide JSON: native text boxes / shapes / hyperlinks (not images), source URLs in speaker notes, cover/TOC/summary/ending built the same way as the PDF bundle. Bundle it as a separate lazy-loaded script (~0.4 MB).
- It cannot measure text, so estimate wrapping: CJK glyph ≈ 1 em, ASCII ≈ 0.5 em, Latin words never split, CJK may wrap anywhere; then pick the largest font where both columns fit. Calibrate against real renders; a first estimator left cards half empty or overflowing the footer.
- Under NodeNext the package typings disagree (`new PptxGenJS()` not constructable): resolve the constructor at runtime (`default?.default ?? default`) and keep loose option types. Declare `jszip` explicitly if tests unzip the output.
- Verify by opening the file in desktop PowerPoint (COM `Slide.Export` to PNG) and looking at every slide.

## Light access gate for downloads

- Per-item PDFs at predictable URLs cannot be hidden by removing links. Publish the newest as `sample.pdf`; encrypt every other `<id>.pdf` to `<id>.pdf.enc` (AES-256-GCM, PBKDF2-SHA256 600k iterations, 12-byte IV prefix) with a secret; publish only salt/iterations. Without the secret, publish no encrypted files and disable the merge button.
- A password check that only compares a hash still leaves plain files public — it is not a gate. Reusable workflows need `secrets: inherit` or the secret is empty.
- Pages caches assets for 10 minutes: put a content hash in `app.js` / `style.css` / lazy-script URLs so a stale page cannot hide new buttons.

## Cloud generation (GitHub Agentic Workflows)

- The agent's shell is allowlisted: it cannot run validators. Put prepare/validate/render in `steps` / `post-steps`; the agent only writes one JSON file.
- Give the agent the schema, one finished sample of the same kind as the quality bar, concrete length budgets (bullet ≤ 60 chars, ≤ 3 bullets), and a region/glossary lookup procedure. First runs without length budgets overflowed and without region steps omitted the stamp.
- A dispatcher workflow (cron) starts one run per pending item (newest first, max N, spaced out, skip existing files / open PRs). `workflow_run` does **not** fire for runs dispatched with the default token; call the auto-merge workflow explicitly after the batch and keep a cron as backstop.
- Auto-merge: allow only branches with the expected prefix + label, exactly one expected file, validate with code from the default branch, `gh pr merge --match-head-commit <sha>` to prevent validate/merge races.
- A bad slide must never break the site deploy: skip it with a warning, and publish JSON only after its PDF rendered.
- Pin the agent model explicitly (`engine: {id: copilot, model: ...}`) for predictable cost and quality; measure per-run AI credits from the run's usage artifact (one slide ≈ 28 credits on claude-sonnet-5.5, 30 summaries ≈ 158).
- Two Pages deploys can collide ("in progress deployment"): re-run after the first finishes.

## Static JSON API

Publish deterministic files (index, latest, per-month, per-item, per-category); do not republish source description text; state attribution and coverage per month so a short list is never read as zero.
