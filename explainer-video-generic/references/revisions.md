# Revising an existing video

Pick the shortest path that matches the request; ask for approval first only when scenes or length change a lot (state the scenes to add, the key lines and the expected length; stop at the checkpoints the user chose). Commands use `$S` (skill dir), `$W` (work folder), `{slug}` as in SKILL.md.

| Request | Do |
|---|---|
| Change a narration line / caption wording | edit the HTML -> `prepare` -> `synth` (only changed lines are synthesized) -> `fit` -> `check` -> `mp4` -> `mix` |
| Faster / tighter pacing | shorten lines, `fit --gap 0.3 --tail 0.6`, shorter animation seconds -> `mp4` -> `mix` |
| Change an animation only | edit that scene's `draw` -> `check` -> `sheet` -> `mp4` -> `mix` (no new audio) |
| Swap an icon / logo | `icons.py embed` -> fix the id in `draw` -> `check` -> `mp4` -> `mix` (no new audio) |
| Quieter or no BGM | `mix.py --bgm-db -34` / `--bgm none` (reuse the silent MP4) |
| Remove captions / burn subtitles in | `render.mjs mp4 --no-captions` / `--subs`, then `mix` |
| Add a scene or hit a target length | edit the HTML and storyboard (new facts need sources) -> `check` -> `sheet` -> `prepare` -> `synth` -> `fit` -> `mp4` -> `mix`; update and re-deliver the storyboard |
| Another language | copy the HTML, new slug, `VIDEO.lang`, translate captions and narration, new work folder, `prepare --lang <code> --voice <name>` -> `synth` -> `fit` -> `mp4` -> `mix --lang <code>` |
| Work folder is gone | copy the editable HTML (it holds scenes, timing and embedded images) to `$W/{slug}.html`; narration audio is not in it: `prepare` -> `synth` -> `fit` -> `mp4` -> `mix` |
| Same-day rebuild | name the file `_YYYYMMDD_2` and delete the previous version |

After any change that touches audio or timing, re-run `check`, and re-probe the final MP4 (audible audio, duration equals the HTML total) before reporting.
