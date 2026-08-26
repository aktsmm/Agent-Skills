---
name: single-html-forge
description: "Generate a single self-contained HTML file — a horizontal slide deck, a vertical-scroll explainer document, or a fixed-canvas summary image — with zero external runtime dependencies, then verify it mechanically. Use when the user asks for HTMLスライド, 単一HTMLスライド, single-file HTML presentation, ブラウザーで開く説明資料, HTML 説明資料, HTMLサマリ画像, or self-contained HTML, or wants to hand someone a deck or explainer that opens anywhere without PowerPoint. Also use to embed images into such a file or to re-check an existing one. Does not output PPTX."
argument-hint: "作りたい内容と、deck / doc / poster のどれか"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Single HTML Forge

One HTML file. No CDN, no build step, no external fetch at runtime. Opens the same on any machine and survives being emailed.

## When to Use

- "HTMLスライドを作って" / "単一HTMLで資料にして" / "ブラウザーで開ける説明資料にして" / "サマリ画像を1枚"
- Handing a deck or explainer to someone who should not need PowerPoint
- Embedding images into a self-contained HTML artifact
- Re-verifying or editing an artifact this skill produced

Not for: PPTX output (this skill does not produce it), editable diagram source files, or anything needing a live server.

## Archetype Routing

Ask which one unless the request already says. Load only that archetype's reference.

| Archetype | Shape                                            | Use for                           | Reference                                             |
| --------- | ------------------------------------------------ | --------------------------------- | ----------------------------------------------------- |
| `deck`    | 16:9 slides, keyboard nav, presenter overlay     | talks, walkthroughs               | [archetype-deck.md](references/archetype-deck.md)     |
| `doc`     | vertical scroll, sidebar nav, numbered citations | explainers, comparisons, handouts | [archetype-doc.md](references/archetype-doc.md)       |
| `poster`  | one fixed canvas, exported as PNG                | summary images, social cards      | [archetype-poster.md](references/archetype-poster.md) |

## Intake

1. Archetype (above).
2. Topic, audience, and roughly how much content.
3. Colour direction — propose two or three, or derive one from the topic. See [design-tokens.md](references/design-tokens.md).
4. Images? If any is a screenshot or of unknown provenance, ask the sanitization question in Hard Constraints **before** embedding.
5. Which export, if any: PDF, PNG, or per-slide PNG. Produce only what was asked for.

## Hard Constraints

These gate the output. They are here, not in a reference, because a reference may never be read.

- **No artifact-specific JavaScript or CSS.** Script is the bundled runtime only; styling is the fixed template plus typed custom properties. Any other `<script>` or `<style>` fails verification.
- **Images ride in a `data:` URI on an `<img>`, or in allowlisted inline SVG.** Nothing else may carry a resource — not CSS `url()`, not `srcset`, not `<object>`, `<embed>`, `<iframe>`, `<video>`, `<link>`, and never `srcdoc`.
- **No web fonts.** System font stack only. Glyphs will differ across machines; say so rather than claiming pixel fidelity.
- **Do not generate brand logos or trademarks.**
- **Never write a customer name, tenant name, subscription id, or internal hostname into the output.**
- **Before embedding a screenshot or an image of unknown provenance, ask: "is this sanitized for publication?"** On "no" or "not sure", stop and mask it first ([mask_image.py](scripts/mask_image.py)). A text scan cannot see a name rendered inside an image, so this judgement stays with the user. Re-ask if the image changes.
- **Prefer the active workspace's instructions** for colour and formatting when they exist; otherwise use this skill's defaults.
- **Never call an artifact finished on Tier 1 alone.** Without the browser pass, report it as `UNVERIFIED`.

## Build Flow

1. Copy the skeleton for the chosen archetype from `assets/skeletons/`.
2. Replace the content. Keep `data-slide-id` and section `id` values stable — they are the handles for later edits.
3. Adjust colours by editing `<style id="shf-theme">` only. Never touch `<style id="shf-css">` or `<script id="shf-runtime">`; both are hash-pinned.
4. For each image: `embed_assets.py`, then paste the `dataUri` into an `<img>` with `alt` and `data-asset-ref`, and add the asset entry to `<script id="shf-model">`.
5. Verify, then export only the requested format.

Changing anything under `assets/runtime/` or `assets/css/` means re-running `build_skeletons.py`, which regenerates the skeletons and re-pins the registry.

## Verification Gate

```
python scripts/verify_html.py <artifact.html> --tier2
```

- **Tier 1** is standard library only and always runs: canonical grammar, element and attribute allowlist, pinned-region hashes, theme tokens, model and asset closure, data URI decode, image metadata, link schemes, size budget.
- **Tier 2** needs Playwright: blocks all network egress, walks every slide, waits for images to finish decoding, then checks for zero-size images, missing viewBox, overflow, and console errors.

Exit codes: `0` PASS, `1` FAIL, `2` UNVERIFIED. Anything but `0` means do not ship it.

Fast path is the default: one viewport, only the requested export. Do the exhaustive pass at publish time. Even the fast path never skips single-file-ness, image decode, overflow at the target viewport, deck navigation, or the sanitization question.

## Scripts

| Script                                           | Needs                       | Purpose                             |
| ------------------------------------------------ | --------------------------- | ----------------------------------- |
| [verify_html.py](scripts/verify_html.py)         | stdlib (Tier 2: Playwright) | the gate                            |
| [build_skeletons.py](scripts/build_skeletons.py) | stdlib                      | rebuild skeletons and re-pin hashes |
| [embed_assets.py](scripts/embed_assets.py)       | stdlib (resize: Pillow)     | fetch, strip metadata, encode       |
| [mask_image.py](scripts/mask_image.py)           | Pillow                      | mask rectangles before embedding    |
| [export_html.py](scripts/export_html.py)         | Playwright                  | PDF / PNG                           |
| [test_verify.py](scripts/test_verify.py)         | stdlib                      | proves the gate actually fails      |

Missing Pillow or Playwright stops the affected step with installation guidance. It never silently degrades.

## References

- [artifact-grammar.md](references/artifact-grammar.md) — the normative rules the verifier enforces
- [design-tokens.md](references/design-tokens.md) — colour recipe and the token grammar
- [japanese-typography.md](references/japanese-typography.md) — CJK line breaking and spacing
- [asset-embedding.md](references/asset-embedding.md) — image routes, budget, provenance
- [component-patterns.md](references/component-patterns.md) — the markup blocks available
- [anti-slop.md](references/anti-slop.md) — what makes output look generated
- [verification.md](references/verification.md) — what to check by eye

## Requirements

A harness with file read/write and Python 3.x. Everything in this folder is self-contained; copy it anywhere and it still works.

## Done Criteria

- [ ] Archetype confirmed with the user
- [ ] `verify_html.py --tier2` exits `0`; a Tier 1-only run is reported as `UNVERIFIED`
- [ ] Every image has `alt`, a model entry, and a sanitization answer if it is a screenshot
- [ ] Only the requested exports exist
- [ ] Output carries no customer, tenant, or subscription identifiers
