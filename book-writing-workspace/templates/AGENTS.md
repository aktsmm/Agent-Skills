## Installed Skills

The following agents are available in this workspace.

| Agent                                                         | Role                           |
| ------------------------------------------------------------- | ------------------------------ |
| [@writing](.github/agents/writing.agent.md)                   | Manuscript writing and editing |
| [@writing-reviewer](.github/agents/writing-reviewer.agent.md) | Quality review (P1/P2/P3)      |

If Re:VIEW/PDF support is enabled, add a converter agent for Markdown to Re:VIEW conversion.

## Folder Permissions

| Folder             | Writing  | Reviewer | Converter |
| ------------------ | -------- | -------- | --------- |
| `keypoints/`       | Read     | Read     | Read      |
| `sections/`        | **Edit** | Read     | Read      |
| `re-view-output/`  | -        | -        | Optional  |
| `images/`          | Read     | Read     | Read      |

## Workflow

```text
Key Points -> Draft -> Review -> Fix -> Optional Convert/PDF
   ↓          ↓        ↓       ↓       ↓
keypoints  sections  Loop until  re-view-output
                     P1=0, P2=0  when enabled
```

## Data Verification

Before completing a chapter:

1. Run `python scripts/count_chars.py` to check word counts
2. Verify against `docs/page-allocation.md` targets
3. Ensure folder structure matches `keypoints/`
