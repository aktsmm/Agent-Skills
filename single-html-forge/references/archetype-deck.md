# Archetype: deck

16:9 slides driven by the keyboard. Start from `assets/skeletons/deck-skeleton.html`.

## Structure

```html
<main id="shf-root">
  <section data-slide-id="s1" class="is-active">...</section>
  <section data-slide-id="s2" hidden>...</section>
  <div id="shf-chrome">prev / counter / next / presenter</div>
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

The buttons in `#shf-chrome` carry `data-shf-action` of `prev`, `next`, or `presenter`.

## Presenter mode

An overlay in the same window, toggled by `S`. It shows the current slide title, the next one, the notes for the current slide, and elapsed time.

Notes live inside the slide:

```html
<p data-shf-notes>Say this part out loud.</p>
```

They are hidden in the deck and surfaced only in the overlay.

**A separate presenter window is not available in v1.** Populating a second window needs `document.write` or `innerHTML`, which the runtime invariants forbid — that is the same restriction that makes the closed-world check sound. A same-window overlay gives the same information without reopening that surface.

## Printing

Print rules put one slide per page and drop the chrome and the overlay. Use this for a quick handout; use `export_html.py --pdf` when the output matters.

## Common mistakes

- Writing paragraphs instead of lines. A deck is read at a distance.
- Leaving `hidden` off a slide, so two render at once.
- Putting a numeric chart in v1. Only diagrams without a numeric scale are supported; a hand-authored axis is where invented numbers appear.
