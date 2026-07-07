# Frame Budget

GitHub Copilot works better when video frames are condensed into a small set of artifacts instead of many independent image reads.

## Modes

| Mode           | Default frames | Best for                                                   |
| -------------- | -------------: | ---------------------------------------------------------- |
| `transcript`   |              0 | Captions-only summary or quote extraction                  |
| `efficient`    |             12 | Fast triage and bug repro skim                             |
| `balanced`     |             24 | Default demos, tutorials, launch videos, screen recordings |
| `token-burner` |             60 | User explicitly wants broader visual coverage              |

## Guidance

- Use focused windows with `--start` and `--end` for named moments.
- Keep `--resolution 512` by default; increase only when text on screen is unreadable.
- Prefer `contact-sheet.jpg` for first visual pass.
- Read individual `frames/` only after the contact sheet or transcript identifies a relevant moment.

## Known Limitation

The MVP sampler uses uniform time sampling through ffmpeg. It is not scene-change aware yet, so short UI flashes can be missed unless the user provides a focused time window.
