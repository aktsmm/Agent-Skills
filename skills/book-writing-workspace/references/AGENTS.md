## Installed Skills

The following agents are available in this workspace.

| Agent                                                         | Role                              |
| ------------------------------------------------------------- | --------------------------------- |
| [@writing](.github/agents/writing.agent.md)                   | Manuscript writing and editing    |
| [@writing-reviewer](.github/agents/writing-reviewer.agent.md) | Quality review (P1/P2/P3)         |
| [@converter](.github/agents/converter.agent.md)               | Markdown to Re:VIEW conversion    |
| [@orchestrator](.github/agents/orchestrator.agent.md)         | Multi-agent workflow coordination |

## Quick Commands

| Prompt             | Action              |
| ------------------ | ------------------- |
| `/gc_Commit`       | Git commit          |
| `/gcp_Commit_Push` | Git commit and push |
| `/gpull`           | Git pull            |

## Folder Permissions

| Folder                   | Writing  | Reviewer | Converter |
| ------------------------ | -------- | -------- | --------- |
| `01_contents_keyPoints/` | Read     | Read     | Read      |
| `02_contents/`           | **Edit** | Read     | Read      |
| `03_re-view_output/`     | -        | -        | **Edit**  |
| `04_images/`             | Read     | Read     | Read      |

## Workflow

```
Key Points → Draft → Review → Fix → Convert → PDF
   ↓          ↓       ↓        ↓       ↓
01_contents  02_contents  Loop until  03_re-view
_keyPoints              P1=0, P2=0   _output
```

## Data Verification

Before completing a chapter:

1. Run `python scripts/count_chars.py` to check word counts
2. Verify against `docs/page-allocation.md` targets
3. Ensure folder structure matches `01_contents_keyPoints/`
