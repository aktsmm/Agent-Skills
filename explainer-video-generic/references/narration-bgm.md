# Narration, readings and BGM

## Policy

- Narration is synthesized by a real neural TTS (see [tts-backends.md](tts-backends.md)). Never use robotic fallbacks (espeak, pyttsx3) for the deliverable.
- **Each line is synthesized separately** (`narration.py synth`): exact per-line durations, no silence-based cutting, parallel and cached. Re-running only re-synthesizes lines whose text/voice/settings changed.
- After synthesis, `fit` writes the **real durations** into the HTML so scenes, captions and animation match the audio, then the MP4 is rendered. Audio can never overrun a scene.
- If the audio comes from outside this script (a TTS web UI, a podcast generator, a colleague), use the batch route: `prepare` -> synthesize the turns -> `split` -> `fit`.

## Steps

```bash
python "$S/scripts/narration.py" prepare --html "$W/{slug}.html" --work "$W/narr" [--lang en] [--readings "$W/readings_extra.tsv"] [--voice NAME] [--backend edge]
python "$S/scripts/narration.py" synth   --work "$W/narr" --backend edge [--voice NAME] [--rate +10%] [--jobs 3] [--only s2:1,s3:0] [--force]
python "$S/scripts/narration.py" fit     --html "$W/{slug}.html" --work "$W/narr" [--gap 0.7 --tail 1.3] [--keep]
node "$S/scripts/render.mjs" check "$W/{slug}.html"
```

- `prepare` writes `lines.json` (every line with its TTS script), `manifest.json`, and for the batch route `batchNN_turns.json` + `batchNN_script.txt`. Language comes from `VIDEO.lang` (override with `--lang`); the default voice depends on backend and language.
- `synth` prints seconds and a pace column (characters/s for ja/zh/ko, words/s otherwise). Lines flagged "unusual pace" deserve a listen (`narr/wav/*.wav`).
- `fit`: line 1 keeps its original start, later lines start at the previous end + 0.7 s, a scene ends 1.3 s after its last line (or `hold`). For snappier pacing `--gap 0.45 --tail 0.9`; to never shorten, `--keep`.
- Changed a few lines only: edit the HTML narration, re-run `prepare` then `synth` (cache), then `fit`.

## Batch route (external audio)

```bash
python "$S/scripts/narration.py" prepare --html "$W/{slug}.html" --work "$W/narr"      # also writes batchNN_turns.json
# synthesize each batch yourself: one utterance per line, silence between lines (>= ~0.85 s works best)
python "$S/scripts/narration.py" split --work "$W/narr" --audio batch01=/path/a.mp3 [batch02=...]
python "$S/scripts/narration.py" fit   --html "$W/{slug}.html" --work "$W/narr"
```

`split` cuts at silences: if the number of long silences equals lines-1 it cuts there ("ok"), otherwise it picks silences closest to the character/word-ratio expectation (DP). A pace column far outside the normal range means a wrong cut: compare with the script and re-synthesize that batch, or use `--skip-head N` if the service reads a title first. `--max-sec` (default 140) controls batch size.

## Readings (pronunciation)

- Screen text and subtitles stay as written; **only the TTS script** is rewritten (`assets/readings.<lang>.tsv`, auto-picked).
- Per-project additions go in `readings_extra.tsv` (`written<TAB>spoken`), passed with `--readings`; they override the defaults. Longer surface forms are applied first. Several videos in one project share **one** file passed to every `prepare` (rebuild scripts included): a per-video copy silently drops entries added elsewhere (a phrase such as 人が went back to the wrong reading after a rebuild), so after any rebuild read the "changed by readings" list for the expected entries.
- Latin surface forms match on word boundaries; replacements touching CJK text get no extra spaces.
- A voice given to `prepare --voice` is kept by `synth`; `synth --voice` overrides it (a note is printed). Without either, the backend/language default (a female voice for ja) applies, so check the `voice:` line `synth` prints.
- After `prepare`, read the "changed by readings" list and the warnings about leftover Latin words (ja) or acronyms (other languages). When unsure how a name is read, ask the user before synthesizing, then add it.
- Japanese: numbers, dates and counters are safest as whole phrases (`2026年3月<TAB>にせんにじゅうろくねん さんがつ`, `40分前<TAB>よんじっぷんまえ`). Brackets are dropped from the TTS script, so add a comma where you need a pause. `/ | ->` become commas, `~` becomes "から", `%` becomes "パーセント".
- English: write spoken forms for acronyms or names that the voice mishandles (`SQL<TAB>sequel`). Currency like `$173.73` is read correctly by the neural voices tested; check the audio.
- Never put readings text on screen.

## Pronunciation review (before the final MP4)

A neural voice can misread a name, a number or a context-dependent kanji (e.g. "人" read as "nin", "行番号" as "kobangō") and nothing in the build notices. Review every video:

```bash
python "$S/scripts/review_narration.py" --work "$W/narr" [--readings "$W/readings_extra.tsv"] [--listen-wav "$W/narr/listen.wav"]
```

0. **Self-review first**: the script only knows its word list, so read the TTS script of every line yourself and list each polyphonic kanji, counter, name, date and number, with the reading you expect and the reading the voice may choose. Add the doubtful ones as phrase-level entries in `readings_extra.tsv` (the bare character would rewrite every use) and add recurring ones to `assets/risky.<lang>.tsv`. Report what you checked.
1. The script lists the risky words of each line (Latin words/acronyms, numbers with counters, context-dependent kanji from `assets/risky.<lang>.tsv`; ja only) and writes `narr/review.md`.
2. If an ASR is available it back-transcribes each line and checks that **each risky word** appears. Compare words, not whole sentences: whole-sentence diffs gave about two thirds false alarms (kanji/kana variants, dropped long vowels). ASR does not repair a misreading: in a test the voice's "nin" came back as "忍", "kobangō" as "広板号" and "dainin" as "ライニー", while correct readings returned the right kanji. Whisper (`pip install openai-whisper`) is only one example: `--transcripts DIR` accepts `<scene>_<idx>.txt` from any other ASR, and `--asr none` skips the check.
3. FLAG = an expected word was not heard: listen to it. An ASR error on correct audio also flags (a false alarm costs one listen). Without ASR the script lists every risky line.
4. Have the user (or yourself, if audio can be played) listen to `listen.wav`, which holds only the flagged and risky lines. Fix a misread with `readings_extra.tsv`, then `synth` (only that line is re-synthesized) -> `fit` -> `mp4` -> `mix`.
5. Passing is a screen, not proof. Tell the user which lines were machine-checked and which were not heard by a person.

## BGM and mixing

```bash
python "$S/scripts/mix.py" --video "$W/{slug}.mp4" --placement "$W/narr/placement.json" --out "$W/{Title}_YYYYMMDD.mp4" [--bgm auto|pad|pop|tech|none|bgm.mp3] [--lang en]
```

| Item | Default |
|---|---|
| BGM | `auto`/`pad`: synthesized (D-major I-V-vi-IV, 92 BPM soft pad + light arpeggio + bass; calm, can feel sleepy). `pop` (bright, 120 BPM) and `tech` (driving, 128 BPM) are upbeat synthesized loops (`scripts/bgm_styles.py`; preview: `python bgm_styles.py pop out.wav`). All deterministic, no copyright concern. `none` = no music; a file = looped/cut to length (the user must hold the rights; never download commercial tracks) |
| BGM level | RMS -30 dBFS where there is no narration (`--bgm-db`); 8 dB lower under narration (`--duck-db`; 0.12 s down, 0.9 s up) |
| Fades | 2 s fade-in, 4 s fade-out |
| Loudness | -16 LUFS, true peak -1.5 dBTP; AAC 48 kHz stereo 192 kbps; video stream copied (not re-encoded) |
| Subtitles | `.srt` from the on-screen wording and the real timing; long lines are split into cues (<= 2 lines each; about 24 characters/line for CJK, 46 for Latin) |
| Splitting | `--split-mb N` splits the result into parts when larger than N MB (for upload limits) |

## Fallback when TTS cannot be used

Give the user the silent MP4 and the narration script (editor button "Narration script TXT", or `narr/batch01_script.txt`) and ask them to add audio with the tool they have, or to supply MP3s for the batch route. See also [prompts.md](prompts.md).
