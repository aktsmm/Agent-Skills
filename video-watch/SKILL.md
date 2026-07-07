---
name: video-watch
description: "Prepare video URLs or local video files for GitHub Copilot analysis by extracting captions, sampled frames, contact sheets, and a prompt packet. Use when the user asks Copilot to watch, inspect, summarize, or diagnose a video, screen recording, demo, webinar, YouTube/Loom/TikTok/X/Vimeo URL, or .mp4/.mov/.mkv/.webm file."
argument-hint: "動画URLまたはローカル動画パス、質問、必要なら時間範囲"
user-invocable: true
license: MIT
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Video Watch

Prepare video artifacts that GitHub Copilot can inspect: captions, frame contact sheets, a frame index, a manifest, and a prompt packet.

This skill is inspired by `bradautomates/claude-video`, but it targets GitHub Copilot workflows. Do not assume Claude Code `Read` parallelism. Generate files first, then inspect only the artifacts needed for the user's question.

## When to Use

- The user asks to watch, inspect, summarize, compare, or diagnose a video.
- The input is a video URL supported by `yt-dlp`, or a local `.mp4`, `.mov`, `.mkv`, or `.webm` file.
- The task depends on both what is said and what appears on screen, such as bug reproductions, product demos, launch videos, tutorials, webinars, ads, or screen recordings.

## Not the Best Fit

- Do not bypass DRM, paywalls, authentication, or site terms.
- Do not request or store cookies, bearer tokens, signed URLs, or private media credentials.
- If an official API or existing transcript answers the task without video processing, prefer that lighter path.

## Core Workflow

1. Run preflight if dependencies are uncertain:
   `python .github/skills/video-watch/scripts/preflight.py`
   Use `python .github/skills/video-watch/scripts/preflight.py --url-mode` for URL inputs.
2. Produce artifacts:
   `python .github/skills/video-watch/scripts/video_watch.py <url-or-path> --question "<what to answer>"`
   Use `--transcript-file <path>` when another tool, Azure Speech, or Speech Translator Desktop Plus already produced a transcript.
   For private or authenticated media, prefer `--detail transcript --metadata-only --transcript-file <path>` and do not pass cookies, bearer tokens, or signed URL credentials.
3. Read artifacts in this order:
   `manifest.json` → `prompt.md` → `transcript.md` → `frame-index.md` → `contact-sheet.jpg` → selected files in `frames/` only if needed.
4. Answer from the artifacts. State when the answer is transcript-only, frame-only, or limited by sparse sampling.
5. For named moments, rerun with `--start` / `--end` to focus the frame budget.

## Detail Modes

| Mode           | Use                                                                      |
| -------------- | ------------------------------------------------------------------------ |
| `transcript`   | Captions or sidecar transcript only. Fastest.                            |
| `efficient`    | Small visual pass for quick triage.                                      |
| `balanced`     | Default contact sheet for most screen recordings and demos.              |
| `token-burner` | Larger visual pass when the user explicitly needs broad visual coverage. |

## Rubber Duck Checkpoints

- Before changing this skill's workflow, review the plan for primitive choice, hidden dependencies, safety boundaries, and Copilot artifact order.
- After editing, review `SKILL.md`, scripts, and references for self-contained behavior, trigger quality, line count, and executable validation.
- Treat the critic as read-only. The producer applies changes and reruns validation.

## References

| Need                                         | Reference                                                |
| -------------------------------------------- | -------------------------------------------------------- |
| Detailed workflow                            | [references/workflow.md](references/workflow.md)         |
| Dependencies and setup                       | [references/dependencies.md](references/dependencies.md) |
| Frame budget and contact sheets              | [references/frame-budget.md](references/frame-budget.md) |
| Optional Scout/Whisper/Azure Speech backends | [references/backends.md](references/backends.md)         |
