---
name: explainer-video-generic
description: "Create a narrated explainer video (MP4) with captions, BGM and SRT from documents, articles, research or demo recordings. Use to turn a deck into a video, make motion graphics, add narration or commentary to a recording, translate a video or revise a scene. Not for slide decks themselves, still images, podcasts, live-action editing or video summaries/transcripts. 日本語: 「解説動画を作って」「動画化して」「資料・記事・ニュースを動画に」「デモ録画に解説とナレーションを付けて」「動画の英語版・日本語版を作って」「動画のシーンを直して」。"
argument-hint: "題材・元ネタ(資料/URL/メモ/デモ録画)、視聴者、長さ目安、言語(ja/en等)、声(TTS)、出力先"
disable-model-invocation: true
user-invocable: true
license: CC BY-NC-SA 4.0
compatibility: Needs Python 3.9+ (numpy), Node.js 18+ with Playwright and a Chromium-family browser, and ffmpeg. Run scripts/check_env.py first. Works in GitHub Copilot (CLI / VS Code / cloud agent), Codex, Claude Code and any agent that supports Agent Skills and can run shell commands.
metadata:
  author: yamapan (https://github.com/aktsmm)
  category: media
  version: "1.0"
---

# Explainer video (generic)

Builds a narrated explainer video from source material, locally:

```
request
  -> brief (one multiple-choice round) -> production plan ......... user approves
  -> read / research the source (docs, notes, web, demo recordings)
  -> storyboard (screen, captions, narration per scene) ........... user approves (if chosen)
  -> HTML animation (copy assets/template_engine.html, edit VIDEO / C / SCENES)
  -> check (render errors, safe-area overflow, contact sheet)
  -> narration: TTS one line at a time -> real durations -> fit the HTML timing
  -> MP4 (headless Chromium renders every frame -> ffmpeg H.264)
  -> mix BGM (ducking, -16 LUFS) -> MP4 with audio + SRT
```

**Align first, then build.** Never start building before the brief and plan are agreed. **The storyboard decides the quality**: spend the effort there.
**Facts come only from the source.** Do not add numbers, names or claims that are not in the source; mark invented examples "(example)".
**Deliverable: MP4 with audio.** Name files `{title}_YYYYMMDD.mp4` (same-day rebuild: `_YYYYMMDD_2`), keep only the latest.

## Files

| File | Role |
|---|---|
| `assets/template_engine.html` | Editor/engine template. Only `VIDEO`, `C`, `SCENES` are edited. Playback, timing, SRT/VTT/TXT export, in-browser MP4 export included. English UI, Japanese UI via `VIDEO.uiLang: 'ja'` |
| `assets/readings.ja.tsv`, `readings.en.tsv` | Pronunciation fixes applied to the TTS script only (auto-picked by `VIDEO.lang`); add project-specific names in a separate `readings_extra.tsv`. `assets/risky.ja.tsv` lists context-dependent kanji for the pronunciation review |
| `scripts/check_env.py` | Verifies python/numpy/ffmpeg/node/Playwright/browser/TTS deps and prints fixes |
| `scripts/render.mjs` | `check`, `still`, `sheet` (contact sheet), `mp4` |
| `scripts/narration.py` | `prepare`, `synth` (per-line TTS), `split` (external batch audio), `fit` |
| `scripts/mix.py` | silent MP4 + narration WAVs + BGM (`auto`/`pad` calm, `pop`/`tech` upbeat, or a file) -> MP4 with audio + SRT |
| `scripts/bgm_styles.py` | Upbeat synthesized BGM loops used by `mix.py --bgm pop\|tech` |
| `scripts/review_narration.py` | Pronunciation review: risky words per line, optional ASR check (Whisper is just one example), `listen.wav` of the lines to hear |
| `scripts/icons.py` | `import` (user icon set), `extract` (pptx), `fetch` (web, product page icon), `sheet`, `embed` (refuses empty SVGs) |
| `scripts/clip_sheet.py` | Contact sheets of demo recordings (pattern C) |
| `references/hearing-plan.md` | Brief questions, production-plan template |
| `references/storyboard.md` | How to write the storyboard + template |
| `references/engine-guide.md` | Template editing guide and drawing helpers |
| `references/narration-bgm.md` | Narration, readings, BGM, mixing details |
| `references/tts-backends.md` | edge-tts / OpenAI / Azure / VOICEVOX / custom command / external audio |
| `references/icons.md` | Finding and using logos and icons (own set, web, license notes) |
| `references/production-brief.md` | Optional production-brief document (pattern B) |
| `references/demo-recording.md` | Building from demo recordings and real-product screenshots (masking scope, zoom) |
| `references/revisions.md` | Revising a finished video: request -> shortest command path |
| `references/prompts.md` | Ready-made prompts for agents without this skill |
| `references/troubleshooting.md` | Limits and common failures |

## When to use / not use

- Use: explain a concept/product/news/report as a 1-5 minute video; add commentary to a demo recording; add narration + BGM to a silent video; make another language version.
- Do not use: building the slide deck itself, still illustrations, audio-only podcasts, live-action cuts/color grading, summarizing or transcribing an existing video.

## Patterns

| Pattern | Best for | Flow |
|---|---|---|
| A. From material (default) | explainers, concept videos, news summaries, training intros | source -> storyboard -> HTML |
| B. With a production brief | monthly refreshes, strict design rules, reproducible builds | storyboard -> **production brief (Markdown)** -> HTML |
| C. From demo recordings or real screenshots | product demos with real screens | analyze clips/screens -> storyboard -> HTML embedding the clips or screenshots (callouts, highlight frames, zoom) |

Default to A. "Monthly/brief" -> B. Recording files or real-product screenshots supplied -> C.

## Decisions to collect (Step 1)

1. **Source**: files, pasted text, URLs, or a topic to research. The video's facts come only from this.
2. **Audience and goal**: who watches, what should they think/do afterwards.
3. **Length / count**: default one video of 1.5-3 minutes; split longer topics.
4. **Tone**: default calm and professional; match a reference video/HTML if supplied.
5. **Language, voice, BGM**: default = language of the request; TTS backend `edge` (free, no key); subtle BGM.
6. **Visibility**: default = may be shown to customers/public: no confidential data, no personal data about private individuals, no unverified claims about people.
7. **Checkpoints**: where to pause for approval (default: storyboard only, then build through to MP4).
8. **Brand assets**: logos, icons, colors (optional; otherwise find them, see `references/icons.md`).

Do not ask what the request or attachments already answer. Ask the remaining important items **once, as multiple choice** (see `references/hearing-plan.md`).

## Procedure

### Step 0: Locate the skill and prepare a work folder

`SKILL_DIR` is the folder that contains this `SKILL.md` (the agent knows its path when it loads the skill). Use a work folder in the user's project, e.g. `./work/{slug}` (slug: ASCII letters, digits, hyphens).

```powershell
# PowerShell
$S = "<SKILL_DIR>"; $W = "$PWD/work/{slug}"; New-Item -ItemType Directory -Force $W | Out-Null
python "$S/scripts/check_env.py" --lang en      # fix every MISS before continuing
```
```bash
# bash / zsh
S="<SKILL_DIR>"; W="$PWD/work/{slug}"; mkdir -p "$W"
python3 "$S/scripts/check_env.py" --lang en
```

Use `python3` instead of `python` where that is the interpreter name. Run steps in order; batch commands that are strictly sequential into one call. Set `PYTHONUTF8=1` on Windows for non-ASCII text.

### Step 1: Brief and production plan (always first)

Details, questions and the plan template: [references/hearing-plan.md](references/hearing-plan.md).

1. **Read** the request/attachments first; skim the source for size and structure. If a file cannot be read (encrypted, blocked), say so and ask for another copy.
2. **Brief**: ask the still-open items (max 4) in **one** multiple-choice round using the agent's question tool (e.g. `ask_user`), else one short numbered message. Put the recommended default first. **Always include the checkpoint question.**
3. **Plan**: write `$W/{slug}_plan.md` (goal, spec, outline, checkpoints, defaults used, deliverables) and summarize it in chat. State clearly that the deliverable is an MP4 with audio and where you will pause.
4. **Get approval** before the storyboard. A supplied topic or "go ahead" does not waive the brief and plan; only an explicit "no questions / just do it / decide for me" does. Then show a short plan anyway and proceed (still ask for a topic if there is no source or theme), and say in the report that the brief was skipped at the user's request.

### Step 1b: Read the source

Read documents fully (not only titles). For news/finance/current-events topics, research with primary sources first (company/agency releases), cross-check key numbers in at least two independent outlets, record dates, and prefer wording the source itself uses. For product or feature claims, verify against the vendor's official documentation and list the URLs under the storyboard's Sources; label preview/beta/unreleased features as such on screen. Pattern C: `python "$S/scripts/clip_sheet.py" "$W/clips/*.mp4" --out "$W/sheets"` and read the sheets ([references/demo-recording.md](references/demo-recording.md)).

### Step 2: Storyboard

Write `$W/storyboard.md` per [references/storyboard.md](references/storyboard.md): per scene = seconds, screen, captions, narration (1-2 sentences per line). Follow a user-supplied storyboard word for word. Show it and wait for approval if "storyboard" is a checkpoint; otherwise state the key points and continue.

### Step 3 (pattern B only): Production brief

Create `$W/{slug}_brief.md` from [references/production-brief.md](references/production-brief.md). All later work follows it.

### Step 4: Build the HTML

1. `cp assets/template_engine.html $W/{slug}.html`
2. Edit per [references/engine-guide.md](references/engine-guide.md): `VIDEO` (title, **unique slug with date**, `lang`, `uiLang`), `C`, `SCENES`. Do not touch section 2 (engine).
3. Copy narration verbatim from the storyboard. Anchor captions and animation to narration lines: `at: 'L0'`, `L(i)`, so timing survives the later fit to audio.
4. Remove the sample scenes and the word "Sample".
5. **Logos/icons (use the official ones actively)**: list every product/service/company named on screen or in narration and give each its real logo/icon, from the sources in [references/icons.md](references/icons.md) (user's set, vendor icon set, product page icon; license notes recorded). Generic line icons `icon()` are only for abstract concepts (approve, person, search), never for a named product. Do not give up after one source: try each source in order before falling back, and say which names fell back. View the contact sheet; `icons.py embed`; draw with `oi(ctx, 'id', cx, cy, size)`.
6. **Date**: use the user's local date for `VIDEO.slug` suffix and `VIDEO.date`; end with an "as of {date}" line.
7. **Real screenshots**: move them where it helps, hold them where it matters. Use zoom/pan (`zoomFrame`, [references/engine-guide.md](references/engine-guide.md)) to push into the part each narration line is about, but let the frame rest (no motion) while the viewer must read a prompt, result or table; move again only when the narration moves on. Masking scope: [references/demo-recording.md](references/demo-recording.md).

### Step 5: Check (all must pass before continuing)

```bash
node "$S/scripts/render.mjs" check "$W/{slug}.html" --json "$W/timing.json"
node "$S/scripts/render.mjs" sheet "$W/{slug}.html" --out "$W/sheet.png"      # 3 frames per scene
node "$S/scripts/render.mjs" still "$W/{slug}.html" --t 12.5 --out "$W/f.png" # full-size frame
```

`check` renders every 0.1 s and reports render errors, NaN, text outside the safe area and narration expected to overrun. Open `sheet.png` with the agent's image viewer and look for overlaps, empty areas, unreadable text. For zoomed screenshots also render `still` frames at each zoom keyframe time (the sheet only shows 3 frames per scene) and confirm the target is framed and readable. If "motion preview" is a checkpoint, hand `sheet.png` to the user and wait.

### Step 6: Narration (fit timing to real audio)

Full detail: [references/narration-bgm.md](references/narration-bgm.md), backends: [references/tts-backends.md](references/tts-backends.md).

```bash
python "$S/scripts/narration.py" prepare --html "$W/{slug}.html" --work "$W/narr" [--readings "$W/readings_extra.tsv"] [--voice NAME]
python "$S/scripts/narration.py" synth   --work "$W/narr" --backend edge        # one TTS call per line, cached
python "$S/scripts/narration.py" fit     --html "$W/{slug}.html" --work "$W/narr"
node "$S/scripts/render.mjs" check "$W/{slug}.html"
```

1. Read the "changed by readings" and "Latin words / acronyms" notes from `prepare`. Fix mispronounced names with a project `readings_extra.tsv`, then re-run `synth` (only changed lines are re-synthesized).
2. Confirm sensitive text may be sent to the TTS service (edge/openai/azure are online). For confidential material use VOICEVOX/local `command` backends or ask.
3. `synth` prints seconds and a pace column; look at lines flagged "unusual pace".
4. `fit` writes the real durations into the HTML (`--keep` to never shorten, `--gap/--tail` to change pacing). For a scene that should show something after the last line, set `hold: seconds` on the scene.
5. Audio from another tool: `prepare` -> synthesize `batchNN_turns.json` yourself -> `split --audio batch01=file.mp3` -> `fit`.
6. **Review the pronunciation** before the final MP4, in two layers (details and limits in `narration-bgm.md`):
   - **Self-review (always)**: read every `tts` line in `narr/lines.json` yourself and, for each kanji word with more than one reading (人, 行, 方, 後, 何, 生, 大人, 一言, counters, names, numbers/dates), decide the reading the voice will most likely produce versus the one the context needs. Do not trust the script's word list to be complete. Register every doubtful or wrong case in `readings_extra.tsv` as the surrounding phrase (e.g. `人が<TAB>ひとが`), not the bare character.
   - **Script check**: `python "$S/scripts/review_narration.py" --work "$W/narr" --listen-wav "$W/narr/listen.wav"` (ASR optional). Fix misreadings via `readings_extra.tsv`, re-`synth`, `fit`.

### Step 7: Render the silent MP4

```bash
node "$S/scripts/render.mjs" mp4 "$W/{slug}.html" --out "$W/{slug}.mp4"      # 1080p, 30 fps, H.264
# test: --from 0 --to 5   4K: --scale 2   force encoder: --codec libx264
```

Rendering takes roughly 1.3-2x the video length (more with embedded recordings). Run long renders in the background. If the toolchain is unavailable, give the user the HTML: open in current Chrome/Edge and press "Export MP4 (silent)".

### Step 8: Mix BGM and finish

```bash
python "$S/scripts/mix.py" --video "$W/{slug}.mp4" --placement "$W/narr/placement.json" --out "$W/{Title}_YYYYMMDD.mp4" [--bgm auto|pad|pop|tech|none|file.mp3] [--lang en]
```

Default BGM is a calm synthesized pad (no copyright concerns); `pop` / `tech` are upbeat synthesized loops for a livelier tone (ask in the brief); a user-supplied file is allowed (user holds the rights; never fetch commercial music). BGM ducks 8 dB under speech, final mix -16 LUFS, SRT written next to the MP4 (long lines are split into cues).

### Step 9: Verify and deliver

- Probe the result (H.264 1920x1080 30 fps, AAC 48 kHz stereo, duration equals the HTML total): `mix.py` prints it. **Prove the audio is audible, not just present**: `ffmpeg -i out.mp4 -af volumedetect -vn -f null -` (mean about -20 dB) and `-af ebur128` (about -16 LUFS); a stream that exists can still be silent.
- Extract 3-4 frames from the **final** MP4 and look at them (captions, highlights, logos). Check that each named product shows its real icon (no generic glyph standing in) and list any that fell back.
- Report which narration lines were checked by `review_narration.py` and which a person has listened to; do not call the pronunciation verified from an ASR pass alone.
- Copy deliverables to `./output/` (or the user's folder): MP4, SRT, editable HTML, contact sheet, plus storyboard and plan (and brief for pattern B). Remove outdated dated versions unless asked to keep them, and remove your temporary files (not the user's).
- Report with **absolute paths**, what was verified, and what was assumed. Say explicitly which file has the sound (the MP4) and that the editable HTML preview is silent. Mention sources used and anything the user should double-check.

## Content and rights rules

- **Facts**: only from the source; attribute contested statements to who said them; put dates on time-sensitive figures; use an "as of" line.
- **People and sensitive news**: stick to what the primary source and reputable outlets state; do not repeat unverified allegations or private details; no speculation about guilt or motives.
- **Finance**: state "news summary, not investment advice"; never predict prices.
- **"Demo"**: call a scene a demo only if it shows a real screen recording; mark diagrams of screens "illustrative screen".
- **Naming and attribution**: product named in full (never a generic noun alone); claims attributed to the owner ("Microsoft recommends"), sources in the storyboard, no on-screen source line unless asked. See `references/storyboard.md`.
- **Logos/icons**: nominative use only (to identify the company), unmodified, with the source/license recorded. Do not imply endorsement. Ask before publishing branded material externally.
- **Music/voices**: synthesized BGM by default; do not imitate a real person's voice.
- **Privacy**: TTS backends other than local ones send the narration text to a third party. Real-environment screenshots are masked before embedding, with the scope agreed with the owner (see `references/demo-recording.md`).

## Placement (so agents discover the skill)

Copy this folder to `.agents/skills/explainer-video-generic/` (read by GitHub Copilot and Codex), `.github/skills/` (Copilot), `.claude/skills/` (Claude Code), or `~/.agents/skills/` for all projects. The folder name must match `name`. Mention the skill by name (`/skills`, `$explainer-video-generic`) or just describe the task.
