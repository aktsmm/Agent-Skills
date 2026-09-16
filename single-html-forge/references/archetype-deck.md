# Archetype: deck

16:9 slides driven by the keyboard. Start from `assets/skeletons/deck-skeleton.html`.

## Structure

```html
<main id="shf-root">
  <section data-slide-id="s1" class="is-active">...</section>
  <section data-slide-id="s2" hidden>...</section>
  <div id="shf-chrome">prev / counter / next / presenter / print</div>
</main>
<div id="shf-presenter" hidden>...</div>
```

The first slide carries `class="is-active"`; every other slide carries `hidden`. The runtime keeps them in sync from there.

`data-slide-id` values are the edit handles. Keep them stable across revisions so "change slide 4" stays unambiguous.

## Sizing

The stage is `100vw` wide and `56.25vw` tall, capped by the viewport, so the deck letterboxes instead of reflowing. All slide typography is in `cqw`, which means one layout works from a laptop to a projector without a second breakpoint.

Because sizes are proportional, **shrinking text to make content fit is not an option** — it shrinks for everyone. If a slide overflows, split it. The verifier fails on overflow rather than letting you scale down past readability.

Rough vertical capacity per slide at the default scale: one heading plus about six short lines, or a table of five rows, or three cards. An eyebrow or chapter label consumes another line; a five-row table that fits without it can overflow once it is added.

## How much text fits on a line

Horizontal capacity is arithmetic, not taste. A slide's padding is `7cqw` each side, so content is `86cqw` wide:

```
漢字/行 ≈ (86 − indent in cqw) ÷ font-size in cqw
```

**Budget in kanji**, because kanji are the worst case. Measured on Windows with the default stack, kanji come out at exactly `1.00em`, while the kana and Latin capitals sampled measured about `0.82em` and `0.90em`: `Yu Gothic UI` is the proportional variant, so its kana are drawn narrower than an em and vary by glyph, independently of `palt`. A kana-heavy line therefore fits roughly a fifth more than the budget while a kanji-heavy one lands on it. Another platform resolves the stack to a different face with its own metrics — see [japanese-typography.md](japanese-typography.md) — which is why nothing here promises pixel fidelity.

Measured at a 1280px stage; at 1920px every figure held except 3-across card kana, which gained one:

| Element                  | Size     | 漢字/行 | かな/行 |
| ------------------------ | -------- | ------- | ------- |
| `h1` — title slide       | `6.2cqw` | 14      | 16      |
| `h2` — slide heading     | `4.4cqw` | 19      | 23      |
| `li` — body list item    | `2.6cqw` | 31      | 38      |
| `.shf-lead`              | `2.2cqw` | 39      | 47      |
| `.shf-card h3`, 3 across | `2.5cqw` | 8       | 10      |
| `.shf-card p`, 3 across  | `2.6cqw` | 8       | 9       |
| `.shf-card p`, 2 across  | `2.6cqw` | 13      | 16      |

A `p` outside a list spends nothing on the `1.3em` marker indent, so it takes 33 instead of 31.

A table is the exception: columns size to their content, so budget the row, not the cell. At `2.1cqw` a row is about 41 全角 wide and each cell spends 1.4 全角 on padding, leaving roughly 36 kanji to share across three columns — 12 apiece if they are even.

Cards are the trap. Three across leaves eight kanji per line, so a card heading is a noun and not a sentence; dropping to two nearly doubles it. `--shf-space-gap` is a fixed pixel value while everything around it is proportional, so a narrower stage — the outline layout with its sidebar open, for instance — spends a larger share of its width on the gaps and gives a card slightly less room, never more.

These are authoring budgets, not a substitute for Tier 2. Overflow is still decided by the browser.

## Keyboard and controls

| Key                    | Action                     |
| ---------------------- | -------------------------- |
| `→` `Space` `PageDown` | next                       |
| `←` `PageUp`           | previous                   |
| `Home` / `End`         | first / last               |
| `S`                    | toggle presenter           |
| `O`                    | toggle the outline sidebar |

The buttons in `#shf-chrome` carry `data-shf-action` of `prev`, `next`, `presenter`, `outline`, or `print`.

## Presenter mode

An overlay in the same window, toggled by `S`. It shows the current slide title, the next one, the notes for the current slide, and elapsed time.

Notes live inside the slide:

```html
<p data-shf-notes>Say this part out loud.</p>
```

They are hidden in the deck and surfaced only in the overlay.

**A separate presenter window is not available in v1.** Populating a second window needs `document.write` or `innerHTML`, which the runtime invariants forbid — that is the same restriction that makes the closed-world check sound. A same-window overlay gives the same information without reopening that surface.

## Outline layout

A variant that puts a slide list on the left and the stage on the right. Start from `assets/skeletons/deck-outline-skeleton.html`. It is the same archetype and the same pinned CSS; the only difference is an attribute on `<html>` and the extra `<nav>`.

```html
<html lang="ja" data-shf-archetype="deck" data-shf-layout="outline" ...>
  ...
  <nav id="shf-outline">
    <p class="shf-outline-title">SLIDES</p>
    <ol>
      <li><button type="button" data-shf-goto="s1">見出し</button></li>
    </ol>
  </nav>
</html>
```

Each entry's `data-shf-goto` must equal a `data-slide-id`. **The runtime cannot build this list** — it never creates elements — so the list is authored and can drift from the slides. Verification catches that: an entry pointing at no slide fails, and under `data-shf-layout="outline"` a slide with no entry fails too. `build_skeletons.py` derives the list from the slides for the same reason.

The list numbers itself with a CSS counter, so entry order is document order. The active entry gets `.is-current` and `aria-current` from the runtime.

Press `O` or use the 目次 button to collapse the sidebar and give the stage the full width. Do that when projecting; the list is for reading and reviewing. Printing and per-slide PNG export drop the sidebar either way.

### Chapter groups

For multi-section review decks, group the outline by the source's chapters rather than listing all slides as peers. Runtime/CSS v4 supports `details[data-shf-section]` groups with native keyboard-accessible `summary` controls:

```html
<details data-shf-section="introduction" open="open">
  <summary>Introduction</summary>
  <ol>
    <li>
      <button type="button" data-shf-page="01" data-shf-goto="s1">
        Overview
      </button>
    </li>
  </ol>
</details>
```

Use one level of groups. Each slide belongs to exactly one group; button order follows slide order. The optional `data-shf-page` overrides the per-list counter with a global page number. Navigation opens the current slide's group and marks it `is-current-section`; collapsing a group does not change the selected slide. Check membership, collapse/expand, chapter jumps, next/previous across boundaries, and a unique current-page marker.

Plan 3–5 chapters before authoring when a deck has six or more slides or crosses multiple topics. Keep slide titles short and parallel within a chapter. If slides also carry a visible eyebrow or chapter label, put it on the chapter opener only; repeating it on every slide weakens hierarchy and consumes vertical capacity. Use a full divider slide only when the audience needs a deliberate reset.

If separate files are needed for authoring, offer a combined review deck as well, with stable slide IDs. Grouping must change navigation behavior, not just add decorative headings.

## Cross-format review

Keep the source's titles, body, examples, caveats, source labels/URLs, and the order and relationships expressed by diagrams. Decoration and line wrapping can differ; replacing an ordered or branching diagram with a flat list can remove meaning even when its words match. Compare each mapped slide's visible content and relationships with the source, and state which presentation details intentionally differ. Hidden notes or serialized content are not proof of visible information parity.

## Printing

### Player controls and steps

Player v8 keeps navigation available while effects run. Both deck skeletons include a sidebar: the presentation skeleton starts with it closed. Use O or the sidebar icon, F for fullscreen, M to mute, and Esc to close settings or presenter notes. On narrow screens the sidebar is a temporary drawer. Settings use ordinary Tab/Space interaction, not ARIA menu semantics. Notes remain in the shared window, not a private presenter window.

Sound is opt-in; the settings menu contains sound, volume, motion and printing. The thumbnail/title-list button appears only after thumbnails are generated. Motion can be disabled without changing content order; OS reduced-motion always disables timing effects. During that override the Motion checkbox is disabled and unchecked with a visible system-status message. Removing the override restores the user's prior choice.

Use sibling step groups with contiguous indices starting at 0 (unmarked content is also stage 0). The next action reveals the next step before advancing to another slide. Previous reverses this path. A sidebar jump selects the first step. View changes preserve the step. Supported effects are `fade`, `rise`, `emphasis`, and `route` (SVG path emphasis). Do not nest step groups.

```html
<section data-slide-id="flow" data-shf-print="all" hidden>
  <h2>A conclusion changes with the evidence</h2>
  <p data-shf-step="0" data-shf-until="0">Initial interpretation.</p>
  <p data-shf-step="1" data-shf-effect="rise">Revised interpretation.</p>
</section>
```

`data-shf-until` is inclusive and requires `data-shf-print="all"`: each stage is printed separately. Cumulative steps use the default `final` print policy. The finalizer generates static print markup, so printing does not discard replaced explanations or depend on animation timing.

Print copies rewrite fragment links, label `for`, and ARIA ID references together with the target IDs. A target on the same printed stage is preferred; otherwise the first printed occurrence is used. Keep referenced descriptions inside printable slide content, not speaker notes or permanently hidden elements. Missing print targets and duplicate content IDs fail finalization. SVG `title`/`desc` identifiers and author-supplied `aria-hidden` on decorative descendants are retained. After changing content or upgrading the print generator, finalize again; do not patch generated print pages by hand.

```
python scripts/export_html.py draft.html --finalize final.html --thumbnails
python scripts/verify_html.py final.html --tier2
```

Finalization needs Playwright; thumbnails additionally need Pillow. Recipients need neither. Thumbnails are 320x180 PNGs of the last step, one per slide, and are navigation previews rather than a substitute for all explanation stages. The command replaces its target only after Tier 1/2 pass; existing content is preserved on failure. Edit the original draft and rerun after content/style changes. The final HTML has schema 2 derived metadata; old schema 1 artifacts remain supported.

For individual PNG export, cumulative slides keep `slide-01.png` naming; replacement stages add `-step-01`. The generated manifest maps filenames to actual slide IDs and steps. Use [deck-motion-skeleton.html](../assets/skeletons/deck-motion-skeleton.html) as a reproducible example, not the reference document's custom JavaScript.

Run `--finalize` separately from `--pdf`, `--png` and `--slides-png`; combining them fails before rendering. `--thumbnails` requires `--finalize`. Export paths must differ from the source HTML and from each other, including filesystem aliases. In-place `--finalize` is supported because the candidate is verified before replacement. `--slides-png` requires actual slides; it does not silently succeed with an empty document export.

All requested exports are rendered and checked in temporary storage before destination files are changed. Each file replacement is atomic; multiple destination files are not a filesystem transaction. If a later save fails, earlier successfully reported files remain. Use the reported filenames and PNG manifest to reconcile a partial save; unrelated existing files are never deleted. Invalid paths, rendering and file-write failures report `STOP:` with a nonzero exit code.

Print rules put one slide per page and drop the chrome and the overlay. Use this for a quick handout; use `export_html.py --pdf` when the output matters.

Current deck CSS sets a 16in x 9in page with zero margins. Tier 2 and PDF export measure the actual print-media layout at the matching 1536 x 864 CSS-pixel viewport before accepting it. A print-only overflow blocks PDF publication even when the screen view fits. Custom printer scaling/paper overrides are outside that verified layout. Preserving HTML accessible names does not by itself certify PDF tagging or screen-reader behavior in every PDF viewer.

The `print` button in the chrome calls the browser's own print dialog, so a recipient can save a PDF without any tooling. It is the only path available to someone who just opened the file, and it disappears in the printed output along with the rest of the chrome.

## Common mistakes

- Writing paragraphs instead of lines. A deck is read at a distance.
- Leaving `hidden` off a slide, so two render at once.
- Putting a numeric chart in v1. Only diagrams without a numeric scale are supported; a hand-authored axis is where invented numbers appear.
