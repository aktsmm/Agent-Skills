# Building from demo recordings (pattern C)

Record the real product screen, then add callouts, highlight frames and narration.

## 1. Recording tips (for the user)

- Record in segments of about 2 minutes; some agents/uploaders cap attachments (often ~200 MB). Name them in order (`01_request.mp4`, `02_plan.mp4`, ...).
- Cut or speed up waiting time afterwards; do not show or mention processing time itself.
- Keep personal names and real customer data off the screen (use a demo tenant/dataset).
- Screenshots or recordings taken from a real environment: blur account/tenant/subscription/resource names, internal IPs and other-chat titles before embedding, state the masking in the on-screen note, and keep unmasked originals out of the deliverable folder.

## 2. Read the clips

```bash
python "$S/scripts/clip_sheet.py" "$W/clips/*.mp4" --out "$W/sheets" [--warn-mb 200]
```

- Produces up to 24 timestamped frames per clip as `*_sheet.png`; open them with the agent's image viewer and note what happens when.
- Zoom into a range: `ffmpeg -ss START -to END -i clip.mp4 -vf fps=2,scale=960:-2 "$W/frames/%03d.png"`.
- `sheets/clips.json` lists duration, resolution and size.

## 3. Storyboard

- For each scene write: which clip, from which second to which second, at what speed.
- Name what viewers should notice (buttons, results, tools used) and plan a highlight frame + label for it.
- Label the mechanisms in viewer language (e.g. a knowledge-search tool -> "Searches the internal knowledge base").
- Call something a "demo" only if it is a real recording.

## 4. HTML

- Put clips in `$W/clips/` and register them in the scene's `media` (`from`, `start`, `rate`).
- In `draw`: `media(ctx, 'demo1', x, y, w, h)`, `focus()` for the area of interest, `chip()` / `bubble()` for labels. A side panel with 3-4 key points (clip 1400 px wide on the left) also works.
- Add "Actual product screen recording" in the lower-right note.

## 5. Replacing and fixing

- Re-recorded a part? Replace that clip, fix `src` and seconds, then re-synthesize only the changed lines (`synth` caches the rest).
- Long clips render slowly; pre-cut the part you use: `ffmpeg -ss START -to END -i in.mp4 -an -c:v libx264 -b:v 8M out.mp4` (use `libopenh264` if `libx264` is missing).

## 6. Rendering

`render.mjs mp4` converts each clip into an all-keyframe proxy (`.xvproxy/` next to it) and then renders frame by frame. Expect roughly 3x real time at Full HD when many clips are used.
