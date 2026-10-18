---
name: html-pdf-slides
description: >-
  Make good-looking slide-style PDFs fast with HTML + headless Chrome instead of PowerPoint: a ready 1280x720 template (Microsoft-style cover / content slide / ending), a render script that outputs PDF + per-page PNG and detects overflow, and design rules for dense one-page slides. Use when asked to quickly create a PDF slide deck, one-page explainers, customer handouts, or "PowerPoint-less" slides, or to bundle cards/info into a branded PDF. Not for editing existing .pptx files or template-based PPTX generation.
argument-hint: "スライドの目的・読者・枚数と、載せたい内容（または元データ）"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# HTML → PDF Slides

Write each slide as HTML, render with Chrome. You get precise layout, selectable text, live links, and no PowerPoint automation. Pitfalls and merge/font details: [Rendering Notes](references/rendering-notes.md).

## When to Use

- 「PDF でスライドをさっと作りたい」「1 枚で完結する解説ページ」「顧客向けに綺麗な PDF」
- 元データ（JSON など）から同じ見た目のページを大量に作りたい
- PPTX の編集は不要で、配布物は PDF（＋任意で PNG）でよい

## Quick Start

1. Copy [assets/deck-template.html](assets/deck-template.html); keep one `<section class="page">` per page (1280×720 px). Page kinds: cover, content (`page slide`), ending.
2. Fill content. Content slides need `data-key` (for reports), a `.ft` footer, and use `.card` blocks so overflow can be measured.
3. Render: `node scripts/render-deck.mjs deck.html out` (needs `playwright-core` + a Chrome/Edge; set `CHROME_PATH` if not auto-found). Output: `out/<name>.pdf`, `out/<name>-pN.png`, `out/<name>-report.json`. Exit code 1 = a slide overflows.
4. **Look at the PNGs** (cover, a dense slide, ending) before reporting done.

## Design Rules

- One slide = one question and one takeaway; title states the claim, a one-line subtitle supports it.
- Fixed 3-box info strip under the title for explainers: 誰に関係するか (bold the target) / 嬉しい点 / 対応の要否.
- Fill the page with useful content in cards (what changes, how it works, limits, glossary); avoid empty bands. Keep body ≥ 12.5 px, preferably 14–16 px; when it does not fit, cut wording or split to a continuation page rather than shrinking further.
- Palette: white field, brand blue accents, navy footer band; one accent colour per meaning (green good, red caution). Do not make every card equally loud.
- Visible text is final copy: no internal-memo wording (未確認 / 記載なし / 要確認 / 推定). Confirmed → write; unconfirmable → omit.
- Put IDs, categories and links in the footer; per-page creation dates and credits only on cover/ending.
- Every link `https://`, escaped; cite official sources for facts.

## Done Criteria

- Render exits 0 with zero overflow, PNGs inspected, links clickable in the PDF, Japanese glyphs visible (view an image; text extraction alone can hide missing glyphs).
