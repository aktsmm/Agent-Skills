---
name: visualize-as-infographic
description: "Create colorful infographic PNGs from a conversation, topic, file, skill, or workflow. Use when: インフォグラフィック, 図解, 挿絵, 章扉, X投稿用画像, OGP, HTML→PNG, visualize session, poster image. Produces 2-3 self-contained HTML patterns, renders PNGs, and verifies every image visually before reporting."
argument-hint: "図示する対象、用途（X投稿/章扉/ブログOGP等）、比率やパターン数の希望"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Visualize As Infographic

Turn a conversation summary, topic, file, skill, or workflow into 2-3 polished infographic PNGs. Generate one self-contained HTML file per pattern, render PNGs, inspect every PNG, fix visual defects, and report usable outputs.

## When To Use

- User asks for `インフォグラフィック`, `図解`, `挿絵`, `章扉`, `X投稿用画像`, `OGP`, `visualize`, or `HTML→PNG`.
- User wants multiple visual directions, not a single text-only slide.
- The artifact should be shareable as PNG and reproducible from HTML.

## Inputs

- Target: explicit argument if provided; otherwise summarize the latest relevant session context.
- Usage: default is X / SNS. If the user mentions book chapter inserts, OGP, slide, or PDF, adapt the ratio and style.
- Ask at most one clarifying question only if the output would materially change.

## Output Defaults

- Create 2-3 different patterns, one HTML per pattern.
- Save under `output/<topic>-diagrams/`.
- File names:
  - HTML: `<topic>-<pattern>.html`
  - PNG: `<topic>-<pattern>.png`
- Common ratios:
  - X / SNS: 1200x675 and/or 1200x1200
  - Blog OGP: 1200x630
  - Chapter insert / book figure: match the book tone; prefer calm, high-readable layouts over flashy decoration.

## Design Rules

- Use visual hierarchy: title, short lead, 3-6 visual units, concise footer if useful.
- Avoid information overload. If text looks dense, split into another pattern rather than shrinking aggressively.
- Set `html, body` to exact poster `width` / `height` and `overflow: hidden`.
- Use Noto Sans JP for Japanese poster text unless a project-specific style says otherwise.
- Use stable dimensions for cards, badges, rails, and panels so text or icons cannot push adjacent elements.
- For chapter inserts, match the book's palette and mood; do not force SNS-dark neon styling if the publication design is quiet.
- Do not add signatures, account names, license text, or skill names unless the user asks.

## Rendering Procedure

1. Create the output folder.
2. Create independent HTML files. Do not pack multiple patterns into one HTML.
3. Render with Playwright. Prefer Python Playwright if available. A helper script is provided: [render_infographics.py](./scripts/render_infographics.py).
4. Render at `device_scale_factor=2`, wait 1-1.5 seconds after page load for fonts.
5. Inspect every PNG with `view_image`.
6. If any PNG has overlap, clipping, unreadable text, wrong order, or excessive density, fix the HTML, render again, and re-check that PNG.
7. Do not send final until all PNGs have completed `inspect -> fix if needed -> rerender -> re-inspect`.

## Visual QA Checklist

- No text overlaps other text, icons, rails, cards, or borders.
- No content is clipped at the image edge.
- Step numbers and visual order match DOM / reading order.
- Card text fits without cramped line breaks.
- Contrast is readable on the final PNG, not just in HTML.
- The final answer refers to the current infographic request, not an older topic from the conversation.

## Completion Report

Provide a compact table:

| PNG | Size | Pattern | Best use |
| --- | --- | --- | --- |

Then recommend one image to use first and explain why in one sentence.

## Do Not

- Do not report completion after generating PNGs but before inspecting them.
- Do not leave a known-bad PNG as a recommended output.
- Do not invent numeric claims, quotes, or external facts that are not in the source material.
- Do not use hardcoded local absolute paths inside generated HTML.
