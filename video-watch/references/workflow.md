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
python <skill-dir>/scripts/video_watch.py "<url-or-path>" --question "<question>"
```

Use an existing transcript from another tool or speech backend:

```powershell
python <skill-dir>/scripts/video_watch.py "<url-or-path>" --transcript-file "<transcript.txt>" --question "<question>"
```

Use `--start` and `--end` when the user names a moment:

```powershell
python <skill-dir>/scripts/video_watch.py "<url-or-path>" --start 2:15 --end 2:45 --question "what changes here?"
```

## Copilot Consumption Pattern

Follow the artifact read order and evidence-boundary rule in SKILL.md Core Workflow steps 3-4.

## Review Checkpoints

SKILL.md Rubber Duck Checkpoints owns the review loop. Stop at PASS or PASS_WITH_NOTES, with at most 2 critic rounds per checkpoint unless the user asks for more.
