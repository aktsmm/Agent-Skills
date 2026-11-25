# Editing the template (assets/template_engine.html)

`template_engine.html` is a Canvas 2D explainer-video editor. Edit only section **1 (VIDEO, C, SCENES)** at the top of the script. Leave **2 (engine)** alone.

## Where to edit

| Place | Content |
|---|---|
| `<title>` and `<h1 id="ttl">` | video title |
| `VIDEO.title` | video title |
| `VIDEO.slug` | ASCII letters/digits/hyphens plus date (e.g. `nvidia-update-20261124`). **Unique per video** (autosave key and export file names) |
| `VIDEO.date` | creation date text (e.g. `'November 24, 2026'`); show it on the last screen as "as of" |
| `VIDEO.lang` | narration language: `'en'`, `'ja'`, `'zh'`, `'ko'`, `'es'`, ... Drives duration estimates, default TTS readings/voice, preview voice |
| `VIDEO.uiLang` | editor UI language: `'en'` or `'ja'` (add another dictionary in the engine's `DICT` to support more) |
| `VIDEO.images` | embedded logos/icons (data URIs), filled by `scripts/icons.py embed`. Draw with `oi()` / `img()` |
| `C` | colors; keep one meaning per color |
| `SCENES` | array of scenes (below) |

The `/*FIT-BEGIN*/ ... /*FIT-END*/` line is rewritten by `narration.py fit`. Do not delete it.

**Multi-language trick**: keep all text in a `COPY = { en: {...}, ja: {...} }` object and select `const X = COPY[LANG]`, as the test project did. A second language is then the same drawing code with another `LANG` (re-run `narration.py` for that language, since durations differ).

## Scene shape

```js
{
  id: 's1', title: 'Opening', duration: 12,                // seconds; overwritten by fit once audio exists
  hold: 1.5,                                               // optional: seconds to keep after the last line
  narration: [                                             // `at` = seconds in the scene (a rough target)
    { at: 0.8, text: 'Line from the storyboard, verbatim.' },
    { at: 6.0, text: 'Second line.' },
  ],
  captions: [                                              // 'L0' = start of narration line 1
    { at: 'L0', main: 'Caption', sub: 'Detail (optional)' },
    { at: 'L1', main: 'Next caption' },
  ],
  media: [                                                 // optional: demo recordings
    { id: 'demo1', src: 'clips/demo1.mp4', from: 0.5, start: 3.0, rate: 1.5 },
  ],
  draw(ctx, t) {                                           // t = seconds in the scene
    bg(ctx);
    act(ctx, 'Section label');
    fx(ctx, IN(t, L(0), 0.6), 20, () => text(ctx, 'Headline', 960, 400, { size: 72, weight: 800 }));
    arrow(ctx, 600, 600, 1300, 600, { color: C.blue, progress: IN(t, L(1), 0.8) });
  },
}
```

- Coordinates are 1920x1080. Safe area: 96 px left/right, 54 px top/bottom. Captions are drawn by the engine at y about 900-1010, so keep important content above y 860.
- **Anchor motion to narration** with `L(i)` (start of line i). After fitting to real audio the motion stays in sync. `LE(i)` = end of line i.
- Same `t` must give the same picture: no random numbers, no current time, no state from earlier frames.
- The engine crossfades scenes for 0.5 s; start each `draw` with `bg(ctx)`.
- `t` may be negative or beyond the scene duration (crossfades): never produce NaN.
- Data-driven visuals (charts) should compute positions from the numbers so screen and narration agree.

## Time helpers

| Function | Meaning |
|---|---|
| `IN(t, a, d=0.5)` | 0 -> 1 over `d` seconds from `a` (ease-out) |
| `OUT(t, a, d=0.4)` | 1 -> 0 |
| `P(t, a, d)` | linear 0 -> 1 |
| `eio(x)` / `eo(x)` | ease-in-out / ease-out |
| `lerp(a, b, u)` | interpolate |
| `L(i)` / `LE(i)` | start / end of narration line i in this scene |
| `typed(str, t, a, cps)` | typewriter substring |

## Drawing helpers

| Function | Use |
|---|---|
| `bg(ctx, color?)` | fill background |
| `fx(ctx, alpha, dy, () => {...})` | fade in while rising by `dy` |
| `text(ctx, str, x, y, {size, weight, color, align, maxW, lineH, top})` | text; `\n` breaks lines; `maxW` wraps (CJK per character with line-break rules, Latin per word); out-of-safe-area text is reported by `check` |
| `rbox(ctx, x, y, w, h, {fill, stroke, lw, r, shadow, dash})` | rounded rectangle |
| `line`, `arrow` (`progress` animates growth) | lines and arrows |
| `chip`, `bubble` | pill label, speech bubble |
| `act(ctx, label)` | top-left section label |
| `note(ctx, str)` | bottom-right note ("illustrative screen", sources) |
| `icon(ctx, kind, x, y, size, color)` | line icons: doc chat mail calendar folder db person people cloud gear check shield chart search agent globe lock bolt laptop video mic music code board spark |
| `oi(ctx, id, cx, cy, size)` / `img(ctx, id, x, y, w, h)` | embedded logo/icon by center+size / by box |
| `media(ctx, id, x, y, w, h, {fit, r, stroke})` | current frame of a video asset |
| `focus(ctx, x, y, w, h, alpha, color)` | dim the surroundings and frame a region |

For a new shape, use Canvas 2D directly inside `draw`, or add a helper to section 1.

### Zoom motion on a screenshot

Add to section 1. Keyframes are `[time, centerX, centerY, zoom]` in the image's own pixels; each move takes 0.9 s; the image keeps the frame's aspect ratio. Anchor times to `L(i)`.

```js
const ez = x => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
function zoomState(nw, nh, kfs, t) {
  let s = [nw / 2, nh / 2, 1];
  for (const [kt, cx, cy, z] of kfs) {
    if (t >= kt + 0.9) s = [cx, cy, z];
    else if (t >= kt) { const p = ez((t - kt) / 0.9); s = [s[0] + (cx - s[0]) * p, s[1] + (cy - s[1]) * p, s[2] + (z - s[2]) * p]; break; }
    else break;
  }
  return s;
}
function zoomFrame(ctx, id, nw, nh, X, Y, W, H, kfs, t) {
  rbox(ctx, X - 8, Y - 8, W + 16, H + 16, { fill: '#111', stroke: C.line, r: 12, shadow: true });
  const im = IMAGES[id]; if (!im || !im.complete || !im.naturalWidth) return;
  const [cx, cy, z] = zoomState(nw, nh, kfs, t), sw = nw / z, sh = nh / z, k = im.naturalWidth / nw;
  const sx = Math.min(Math.max(cx - sw / 2, 0), nw - sw), sy = Math.min(Math.max(cy - sh / 2, 0), nh - sh);
  ctx.save(); ctx.beginPath(); ctx.rect(X, Y, W, H); ctx.clip(); ctx.drawImage(im, sx * k, sy * k, sw * k, sh * k, X, Y, W, H); ctx.restore();
}
// fx(ctx, IN(t, 0.3, 0.7), 20, () => zoomFrame(ctx, 'shot', 1576, 874, 100, 130, 1180, 654, [[L(1) + 0.2, 890, 490, 2.0], [L(2) + 5, 788, 437, 1]], t));
```

## Video assets (demo recordings)

- `from` = scene second playback starts; `start` = offset into the clip; `rate` = speed (1.5-2 to skip waiting).
- `render.mjs mp4` serves clips through all-keyframe proxy files (`.xvproxy/` next to the clip) so frame seeking is exact.
- When the user exports in their own browser, keep the clips at the same relative path or pick them under "Asset files" (double-clicking the HTML can block export because of browser restrictions).

## Editor features (for explaining to the user)

- Play/seek/scene jump (Space, Left/Right, [ ]), toggles for captions / narration subtitles / production guides, browser-voice preview (timing check only; not in the MP4).
- Scene durations, "auto-fit durations to narration" (estimate-based). After fitting to real audio the duration column is locked.
- Export: MP4 (silent; Full HD/4K; whole/test 5 s/current scene), SRT, VTT, narration TXT, timing JSON, frame PNG, save/load adjustments.
- MP4 is encoded with WebCodecs H.264, one frame at a time (needs current Chrome/Edge).
