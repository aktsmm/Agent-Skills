# Design tokens

Colour is chosen per topic rather than picked from a catalogue, but only inside `<style id="shf-theme">`, and only as declarations the token grammar accepts. Everything else is hash-pinned.

## The one editable block

```html
<style id="shf-theme">
  :root {
    --shf-color-accent: #0067b8;
    --shf-size-base: 20px;
  }
</style>
```

One `:root` block, custom properties only. No selectors, no at-rules, no `url(`, no `var(`, no backslash. Any property outside the table below fails, so a typo cannot quietly become dead CSS.

| Property         | Grammar                       | Example   |
| ---------------- | ----------------------------- | --------- |
| `--shf-color-*`  | `#rrggbb`                     | `#0067b8` |
| `--shf-space-*`  | number + `px` or `rem`        | `24px`    |
| `--shf-size-*`   | number + `px`, `rem`, or `ch` | `74ch`    |
| `--shf-scale-*`  | bare number                   | `1.25`    |
| `--shf-radius-*` | number + `px` or `rem`        | `12px`    |
| `--shf-weight-*` | `100`–`900` in hundreds       | `700`     |
| `--shf-ratio-*`  | bare number                   | `1.6`     |

Named colours, `rgb()`, and `hsl()` are all rejected. Hex keeps the contrast check straightforward.

## Choosing a palette

Pick a base hue from the subject, not from habit.

| Subject                              | Hue range                |
| ------------------------------------ | ------------------------ |
| Infrastructure, security, platform   | blue 200–230             |
| Data, analysis, finance              | teal to green 160–200    |
| Product, launch, marketing           | orange to red 10–40      |
| Research, policy, education          | indigo to violet 250–280 |
| Operations, logistics, manufacturing | amber to brown 30–50     |

Then:

1. One accent. Two only if the second marks a genuinely different category. A third makes the artifact look decorated rather than designed.
2. Text is not pure black. `#1b1f27` reads better than `#000000`.
3. Surfaces are the accent hue at very low saturation, not grey. It is what makes a palette feel deliberate.
4. Body text against its background must clear **4.5:1**. Large display text must clear 3:1. Check it; do not eyeball it.
5. Never let colour be the only carrier of meaning. Pair it with a word or an icon.

## Contrast, quickly

Relative luminance per channel: `c/255`, then `c<=0.03928 ? c/12.92 : ((c+0.055)/1.055)**2.4`, weighted `0.2126 R + 0.7152 G + 0.0722 B`. Ratio is `(lighter+0.05)/(darker+0.05)`.

The default accent `#0067b8` on white is about 5.6:1, so it is safe for body text. Lighten it much and it stops being.

## Varying the look without new CSS

The template is fixed, so distinction comes from restraint, not from novel layout: how much whitespace, whether surfaces are used at all, how heavy the display weight is, whether the accent appears as a rule, a card edge, or only in links. A deck with `--shf-weight-display:900`, generous spacing and a single hairline accent reads nothing like one with cards everywhere, and neither needed a line of custom CSS.
