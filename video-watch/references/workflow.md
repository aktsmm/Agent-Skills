# Video Watch Workflow

Use this reference when the user asks for detailed operation or when the first pass is too sparse.

## Artifact Contract

The script creates one run directory containing:

| Artifact            | Purpose                                                                        |
| ------------------- | ------------------------------------------------------------------------------ |
| `manifest.json`     | Machine-readable source, artifact list, warnings, and limitations. Read first. |
| `prompt.md`         | Short task packet for Copilot. Read second.                                    |
| `transcript.md`     | Captions, sidecar transcript, or an explicit unavailable notice.               |
| `frame-index.md`    | Frame file names and approximate timestamps.                                   |
| `contact-sheet.jpg` | Grid image for visual scan.                                                    |
| `frames/`           | Individual sampled frames. Read only selected frames when necessary.           |

## Standard Run

```powershell
python .github/skills/video-watch/scripts/video_watch.py "<url-or-path>" --question "<question>"
```

Use an existing transcript from another tool or speech backend:

```powershell
python .github/skills/video-watch/scripts/video_watch.py "<url-or-path>" --transcript-file "<transcript.txt>" --question "<question>"
```

Use `--start` and `--end` when the user names a moment:

```powershell
python .github/skills/video-watch/scripts/video_watch.py "<url-or-path>" --start 2:15 --end 2:45 --question "what changes here?"
```

## Copilot Consumption Pattern

1. Read `manifest.json` and note warnings.
2. Read `prompt.md` to preserve the user's question.
3. Read `transcript.md` for spoken content.
4. Read `frame-index.md` and inspect `contact-sheet.jpg`.
5. Inspect individual frames only when the contact sheet points to relevant timestamps.
6. Answer with evidence boundaries: transcript-only, frame-only, sparse sampling, or missing captions.

## Review Checkpoints

Use a producer/critic loop when changing this skill:

1. Producer drafts the plan or implementation.
2. Critic reviews read-only for primitive choice, scope, artifact order, safety boundary, dependency boundary, self-contained resources, and validation.
3. Producer fixes blocking findings and reruns the smallest relevant validation.
4. Repeat until PASS or PASS_WITH_NOTES, with a maximum of 2 critic rounds per checkpoint unless the user asks for more.

Checkpoint targets:

- Plan review: before adding or changing workflow behavior.
- Implementation review: after editing `SKILL.md`, scripts, or references.
