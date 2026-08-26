# Japanese typography

The templates already set this up. The notes here explain what to preserve when writing content.

## Font stack

```css
font-family:
  "Segoe UI", "Yu Gothic UI", "Hiragino Sans", Meiryo, system-ui, sans-serif;
```

Windows lands on Yu Gothic UI, macOS and iOS on Hiragino Sans, Android on its own sans. **The same file therefore renders with different glyphs on different machines.** That is the price of a genuinely self-contained file: bundling a Japanese web font would add megabytes and a licence question.

Say this plainly when someone asks about pixel fidelity. Line breaks can land differently across machines, which is why layouts here are built to tolerate a line more, not to be pixel-perfect.

## What the templates set

```css
font-feature-settings: "palt" 1; /* proportional kana and punctuation spacing */
line-break: strict; /* proper kinsoku */
overflow-wrap: anywhere; /* long tokens wrap instead of overflowing */
line-height: 1.7 – 1.8; /* CJK needs more than a Latin default */
```

`palt` matters. Without it, Japanese punctuation carries full-width sidebearings and headlines look gappy.

`line-break: strict` keeps 、。 ） off the start of a line and （ off the end. Loosening it is what makes text look subtly wrong without an obvious cause.

## Writing rules

- Put a half-width space between Japanese and Latin or digits: `HTML の仕様`, `3 つの論点`. Not around punctuation.
- Do not insert manual line breaks to control wrapping. They will be wrong at another width or on another machine.
- Headings read better short. Japanese has no inter-word spaces, so a long heading gives the eye nowhere to break.
- Prefer full-width 、。 in body text and half-width `,` `.` inside code.
- Avoid mixing ～ and 〜 in one document.

## Line length

`--shf-size-measure` defaults to `74ch` in the doc archetype. For Japanese that is roughly 37 characters per line, which is close to the comfortable range of 35–45. Widening past that is the most common reason a document becomes tiring to read.

## Numbers and units

Use half-width digits. Keep a space before a unit (`12 GB`), except for `%` and `°C`. Tabular figures are worth it in tables:

```css
font-variant-numeric: tabular-nums;
```

## Things that break silently

- A `<code>` element inherits `palt` unless the template resets it. The deck and doc CSS already do; if you add code elsewhere, check the spacing.
- Vertical writing (`writing-mode: vertical-rl`) is not supported in v1. The stage sizing assumes horizontal.
- Rare glyphs may fall back to a different face mid-sentence on some machines. Nothing to do about it in a font-free artifact, but it is worth knowing before someone reports it as a bug.
