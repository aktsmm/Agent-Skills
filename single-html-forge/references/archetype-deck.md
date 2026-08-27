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

Rough capacity per slide at the default scale: one heading plus about six short lines, or a table of five rows, or three cards.

## Keyboard and controls

| Key                    | Action           |
| ---------------------- | ---------------- |
| `→` `Space` `PageDown` | next             |
| `←` `PageUp`           | previous         |
| `Home` / `End`         | first / last     |
| `S`                    | toggle presenter |
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
```

Each entry's `data-shf-goto` must equal a `data-slide-id`. **The runtime cannot build this list** — it never creates elements — so the list is authored and can drift from the slides. Verification catches that: an entry pointing at no slide fails, and under `data-shf-layout="outline"` a slide with no entry fails too. `build_skeletons.py` derives the list from the slides for the same reason.

The list numbers itself with a CSS counter, so entry order is document order. The active entry gets `.is-current` and `aria-current` from the runtime.

Press `O` or use the 目次 button to collapse the sidebar and give the stage the full width. Do that when projecting; the list is for reading and reviewing. Printing and per-slide PNG export drop the sidebar either way.

## Printing

Print rules put one slide per page and drop the chrome and the overlay. Use this for a quick handout; use `export_html.py --pdf` when the output matters.

The `print` button in the chrome calls the browser's own print dialog, so a recipient can save a PDF without any tooling. It is the only path available to someone who just opened the file, and it disappears in the printed output along with the rest of the chrome.

## Common mistakes

- Writing paragraphs instead of lines. A deck is read at a distance.
- Leaving `hidden` off a slide, so two render at once.
- Putting a numeric chart in v1. Only diagrams without a numeric scale are supported; a hand-authored axis is where invented numbers appear.
