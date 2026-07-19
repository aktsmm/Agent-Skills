# Drawio Delivery Patterns

For documentation-facing diagrams, generate outputs as a pair:

- `name.drawio` for editing in VS Code Draw.io
- `name.drawio.svg` for README / web embedding

Reserve `*.drawio.svg` for SVG files that actually contain draw.io metadata. If you hand-author or post-process a plain SVG without embedded draw.io metadata, name it `*.svg` instead of `*.drawio.svg`.

If the visible asset started from manual SVG cleanup or hand-authored layout tweaks, still keep a matching `name.drawio` as the editable SSOT. Do not leave documentation diagrams as SVG-only when future edits are expected.

After any `.drawio` layout or label edit, regenerate the paired `.drawio.svg` from its source and verify both rendering and re-opening as an editable draw.io SVG. Do not treat manual `content` metadata edits as the normal sync path; exporter formatting is implementation-specific.

For draw.io Desktop CLI exports on Windows, use absolute source/output paths and wait for the spawned process. A running GUI instance can make a direct CLI call return before the files appear. Gate delivery on exit code `0`, output existence, and an output timestamp newer than the source edit. If source and delivery timestamps are ambiguous, re-export to a temporary file and compare hashes before upload or publication.

## Recommended Markdown Pattern

```markdown
Use `outputs/name.drawio.svg` as the embedded image path.

- outputs/name.drawio.svg
- outputs/name.drawio
```

## Multilingual Variants

Keep parallel filenames instead of overwriting a single asset:

- `name.drawio` / `name.drawio.svg`
- `name-ja.drawio` / `name-ja.drawio.svg`

## Local Article Drafting

If the Markdown preview surface does not reliably render the SVG variant:

- keep `.drawio` as the editable source
- keep `.drawio.svg` as the web / embeddable artifact
- temporarily reference a generated `*.png` from the draft article for local preview stability

At publish time, replace local relative preview paths with the final hosted asset URL.

## Qiita-specific

For Qiita articles, do not leave non-trivial diagrams as Mermaid blocks in the article body — Qiita rendering can be inconsistent. Workflow:

1. Create a `.drawio` source
2. Export PNG for Qiita image upload
3. Keep `.drawio.svg` as the web artifact
4. Replace the draft-local path with the hosted Qiita image URL before publish
