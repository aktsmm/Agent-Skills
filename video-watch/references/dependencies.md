# Dependencies

`video-watch` uses local tools and does not store credentials.

## Required

| Tool         | Used for                           | Check               |
| ------------ | ---------------------------------- | ------------------- |
| Python 3.10+ | scripts                            | `python --version`  |
| ffmpeg       | frame extraction and contact sheet | `ffmpeg --version`  |
| ffprobe      | duration detection                 | `ffprobe --version` |

## Required for URL Captions, Download, or Frames

| Tool   | Used for                        | Check              |
| ------ | ------------------------------- | ------------------ |
| yt-dlp | URL captions and video download | `yt-dlp --version` |

Run:

```powershell
python .github/skills/video-watch/scripts/preflight.py
python .github/skills/video-watch/scripts/preflight.py --url-mode
```

`yt-dlp` is not required when using an external transcript with `--detail transcript --metadata-only --transcript-file <path>` because no URL captions or video download are attempted.

Windows install hints:

```powershell
winget install --id Gyan.FFmpeg -e
python -m pip install --user yt-dlp
```

## Safety Boundary

- Do not pass cookies, bearer tokens, private headers, or authentication exports to `yt-dlp`.
- Do not use the skill to bypass DRM, paywalls, access controls, or site terms.
- Generated manifests redact URL query strings. Still review artifacts before sharing private video content.
- URL mode passes `--no-playlist`; process one video per run.
