# Optional Backends

The MVP has no hard dependency on cloud transcription or Microsoft Scout.

## Microsoft Scout

Treat Scout as an optional external agent surface, not as a required runtime. If the environment has Scout enabled, it can be used to inspect generated artifacts or run follow-up analysis, but `video-watch` must still work with standard GitHub Copilot artifact reading.

## Whisper or Azure Speech

Future transcription backends can fill `transcript.md` when captions or sidecar transcripts are unavailable.

## Backend Contract

Any transcription backend must produce the same artifacts so Copilot usage stays stable:

- `transcript.md`: timestamped text when available; otherwise an explicit unavailable / not implemented message.
- `manifest.json`: add `transcript_backend`, `transcript_status` (`available` / `unavailable`), `language`, `speaker_labels`, `duration_seconds` when known, and `warnings` for partial results.
- `prompt.md`: do not include secrets or raw service errors; summarize only the evidence boundary.

Current bridge: pass `--transcript-file <path>` to import text produced by Speech Translator Desktop Plus, Azure Speech, Whisper, or another tool without adding that provider as a runtime dependency.

Provider failures must not delete visual artifacts. If transcription fails, continue with frames/contact sheet and tell the user the answer is visual-only or transcript-limited.

## Speech Translator Desktop Plus Pattern

Use `aktsmm/speech-translator-desktop-plus` as a design reference for live-audio backends, not as a runtime dependency.

Reference repo: https://github.com/aktsmm/speech-translator-desktop-plus

Useful patterns to borrow:

- Provider routing: keep Azure AI Speech as one backend option, with Google, Whisper, Deepgram, AssemblyAI, or other providers behind explicit provider names.
- Transcript-only mode: support transcription without translation when the user only needs video understanding.
- PC audio and livestream thinking: treat system playback as a first-class source when the target is a livestream, demo, or webinar.
- Explicit staged providers: allow settings or notes for future providers, but return an explicit `not implemented` / `unavailable` status instead of silently falling back.
- Secret handling: API keys must come from environment variables, OS-protected local config, or ignored local files; never write keys into `manifest.json`, `prompt.md`, transcripts, or logs.

Do not copy the WPF app shape into this skill. Borrow the provider-routing and credential-boundary patterns only; `video-watch` remains a file-artifact workflow for GitHub Copilot.

## Azure Speech Backend Choices

- Use Speech to text real-time APIs for live audio, microphone, PC audio, or streaming scenarios.
- Use Speech Transcription SDK / Fast Transcription style flows for prerecorded files or remote URLs.
- Use batch transcription for long prerecorded media or high-volume jobs where asynchronous output is acceptable.
- Keep translation out of the first backend unless the user explicitly asks for translated transcripts; transcript-only is the default.

Official Azure Speech grounding:

- Speech to text supports real-time transcription, batch transcription, and file/stream scenarios: https://learn.microsoft.com/ja-jp/azure/ai-services/speech-service/speech-to-text
- Azure AI Speech Transcription SDK targets near-real-time and non-real-time scenarios using local captured audio, files, and Azure Blob Storage data: https://learn.microsoft.com/ja-jp/azure/ai-services/speech-service/transcription-sdk

Implementation rules:

- Read API keys from environment variables or a local ignored config file.
- Never write secrets into artifacts or logs.
- Mark backend name and confidence in `manifest.json`.
- Preserve the current fallback behavior: if transcription fails, still create `transcript.md` with an unavailable notice.
