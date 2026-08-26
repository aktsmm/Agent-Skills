# Archetype: poster

One fixed-pixel canvas, meant to leave as a PNG. Start from `assets/skeletons/poster-skeleton.html`.

Unlike the other two, the HTML is a means rather than the deliverable. What ships is usually the exported image.

## Canvas size

Set through theme tokens:

```css
:root {
  --shf-size-canvas-w: 1200px;
  --shf-size-canvas-h: 630px;
}
```

| Purpose                 | Size                |
| ----------------------- | ------------------- |
| Article header, OG card | `1200px` x `630px`  |
| Vertical social         | `1080px` x `1350px` |
| Square                  | `1080px` x `1080px` |
| A4 landscape at 150dpi  | `1754px` x `1240px` |

The canvas does not reflow. Content that does not fit overflows, and the verifier fails it — that is deliberate, because a silently clipped poster looks fine in HTML and wrong in the PNG.

## Export

```
python scripts/export_html.py poster.html --png out.png --scale 2
```

`--scale 2` renders at twice the canvas size. Any embedded bitmap therefore needs at least `displayed width x scale` real pixels, or it will look soft in the export while looking fine on screen. `embed_assets.py` records the true dimensions so this is checkable.

## Composition

The skeleton is eyebrow, headline, lead, a row of points, then a footer. It works because it has one focal point.

Hold to roughly: one headline under 30 characters, a lead of one sentence, and three points. A poster read in two seconds cannot carry more, and the fixed canvas will not grow to accommodate it.

If a colour is doing the work of a label — a red card meaning "bad" — add a word too. The PNG may be viewed by someone who cannot separate those hues.

## When the workspace has its own rules

If the poster is destined for a specific publishing target and the active workspace has instructions covering figure colour or style, those win over this skill's defaults. Check before picking a palette.

## Common mistakes

- Designing at the wrong canvas size and rescaling afterwards; type sizing stops being right.
- Embedding a screenshot without checking its real resolution against the export scale.
- Treating the HTML as the deliverable when the recipient expects an image.
