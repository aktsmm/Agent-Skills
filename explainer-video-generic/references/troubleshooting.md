# Limits and troubleshooting

## Setup

Run `python scripts/check_env.py --lang <ja|en|...>` first. It prints what is missing and how to fix it.

| Need | Install |
|---|---|
| Python 3.9+ and numpy | `pip install numpy` |
| ffmpeg with an H.264 encoder | `winget install Gyan.FFmpeg` / `brew install ffmpeg` / `apt install ffmpeg`, or `pip install imageio-ffmpeg` (bundled binary; found automatically). `FFMPEG` env var overrides |
| Node.js 18+ and Playwright | `npm i -g playwright` then `npx playwright install chromium` (or set `XV_PLAYWRIGHT` to a folder containing `node_modules`) |
| A browser | Playwright's Chromium, or an installed Chrome/Edge (found automatically); `XV_CHROME` overrides |
| edge-tts (default voice) | `pip install edge-tts` |
| CJK captions | a CJK font on the machine (Windows/macOS have one; Linux: `apt install fonts-noto-cjk`) |

Locked-down machines may block public package registries (npm/PyPI). Use the organization's mirror or approved internal feeds instead of bypassing the policy; or run the build somewhere unrestricted (CI, a container).

## Common failures

| Symptom | Cause | Fix |
|---|---|---|
| Robotic narration | a simple local synthesizer was used | use `narration.py synth` with edge/openai/azure/voicevox |
| `synth` fails with HTTP 403 (edge) | the unofficial endpoint changed; old edge-tts | `pip install -U edge-tts`; otherwise switch backend |
| Name or acronym mispronounced | missing reading | add to `readings_extra.tsv`, re-run `prepare` + `synth` (only that line is re-synthesized) |
| Audio of a different length than the scene | audio not fitted yet | run `fit`, re-run `check`, re-render |
| `check`: NaN | arithmetic in `draw` (divide by zero, undefined) | fix the scene and second reported |
| `check`: text outside the safe area | line too long / near the edge | shorten, use `maxW`, move inward |
| `check`: narration expected to overrun | line longer than the gap to the next line | synthesize and `fit`; before TTS shorten the line or move `at` later |
| `split` pace column extreme | wrong cut positions | compare with the script; re-synthesize that batch; `--skip-head` if a title is read first |
| Previous video's timing/captions show up in the editor | same `VIDEO.slug` (browser autosave) | change the slug; press "Reset" in the editor |
| In-browser export yields a tiny/black MP4 | tab in the background / asset restrictions | keep the tab in front, pick assets under "Asset files", or use `render.mjs mp4` |
| Browser says MP4 export unsupported | old browser | current Chrome/Edge |
| 4K export falls back to Full HD | the machine cannot encode 4K H.264 | use `render.mjs mp4 --scale 2` |
| `render.mjs`: no usable browser | no Chromium found | `npx playwright install chromium` or set `XV_CHROME` |
| `render.mjs`: no H.264 encoder | ffmpeg build without libx264/openh264 | install a full ffmpeg build; `--codec` to force another encoder |
| Rendering is slow | many embedded clips, SVG icons drawn every frame, 4K | expected (about 1.3-2x video length); use Full HD, pre-cut clips, run in the background |
| Result larger than an upload limit | long video / many clips | `mix.py --split-mb N`; trim clips |
| Icon not found | not in any set | see icons.md (official assets, Simple Icons, favicon); else line icon and say so |
| Logo looks wrong | wrong file under the name | always open the icon contact sheet before embedding |
| Windows console garbles text | legacy code page | `PYTHONUTF8=1`; the scripts also force UTF-8 output |
| Command fails with "cannot find working directory" right after writing files | the shell lost its cwd | `cd` into the work folder at the start of every command |

## Local export by the user (when the toolchain is unavailable)

1. Download `{slug}.html` (and the clip folder) and keep the same folder layout.
2. Open the HTML in current Chrome/Edge; with clips, pick them under "Asset files".
3. Run "Test (0-5 s)" first, then "Whole video".
4. Send the MP4 back and run `mix.py` to add audio and BGM.
