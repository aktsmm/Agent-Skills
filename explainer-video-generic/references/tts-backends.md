# TTS backends

`narration.py synth --backend <name>` synthesizes one audio file per narration line, converts it to 48 kHz mono WAV, trims silence and records the real duration. Pick the backend by quality, cost, privacy and availability.

| Backend | Setup | Cost / network | Notes |
|---|---|---|---|
| `edge` (default) | `pip install edge-tts` | free, no key, **online** (Microsoft Edge read-aloud service) | Many languages/voices (`edge-tts --list-voices`). Unofficial endpoint: it can change; upgrade the package if you get HTTP 403 (`pip install -U edge-tts`; 7.3.1 fixed a 403 seen in November 2026). Text leaves the machine |
| `openai` | `OPENAI_API_KEY` (optional `OPENAI_BASE_URL`) | paid API, online | `--model gpt-4o-mini-tts` (default), `--voice alloy` (default), `--instructions "calm newsreader"`, `--speed 1.0`. Multilingual |
| `azure` | `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION` (e.g. `japaneast`) | paid (free tier exists), online | Same neural voice names as edge (e.g. `ja-JP-NanamiNeural`); official, supported service |
| `voicevox` | run a VOICEVOX engine (`VOICEVOX_URL`, default `http://127.0.0.1:50021`) | free, **local** | Japanese only; `--voice` is the style id (default 2), `--speed` sets speedScale. Check each character's license terms |
| `command` | any CLI | depends | `--cmd 'mytts --voice {voice} --in "{text_file}" --out "{out}"'` with placeholders `{text_file}` `{out}` `{voice}` `{text}`. Output can be wav/mp3/ogg (anything ffmpeg reads). Good for local engines (Piper, Coqui, macOS `say` + conversion, ...) |
| external audio | none | n/a | `prepare` -> make audio elsewhere -> `split` -> `fit` (see narration-bgm.md) |

## Voices

| Language | edge / azure default | Other examples |
|---|---|---|
| ja | `ja-JP-NanamiNeural` (female) | `ja-JP-KeitaNeural` (male) |
| en | `en-US-AriaNeural` | `en-US-AndrewMultilingualNeural`, `en-GB-SoniaNeural` |
| zh | `zh-CN-XiaoxiaoNeural` | |
| ko | `ko-KR-SunHiNeural` | |
| es / fr / de / pt / it | `es-ES-ElviraNeural` / `fr-FR-DeniseNeural` / `de-DE-KatjaNeural` / `pt-BR-FranciscaNeural` / `it-IT-ElsaNeural` | |

Set `--voice` for anything else. Match `VIDEO.lang` to the narration language so duration estimates and readings are right.

## Privacy and rights

- `edge`, `openai`, `azure` send the narration text to a third-party service. For confidential material use `voicevox` or a local `command` backend, or ask the user first.
- Do not clone or imitate a real person's voice. Check the terms of the chosen voice/service for commercial use and for attribution (for example VOICEVOX credit notation).

## Behavior

- Calls run in parallel (`--jobs`, default 3) with up to 4 retries and back-off. Results are cached in `narr/synth_cache.json` keyed by backend, voice, settings and text; use `--force` to ignore the cache and `--only s2:1,s3:0` to limit lines.
- Any failure after retries aborts with the backend name and a hint; nothing partial is written to `audio_lines.json` for failed lines.
- `--rate +10%` (edge) speeds up speech; for other backends use `--speed`.
