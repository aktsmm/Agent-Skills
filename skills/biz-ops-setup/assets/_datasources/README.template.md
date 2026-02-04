# Data Sources Configuration

Directory for data source configuration and references used in the workspace.

## Available Data Sources

### Microsoft 365 (via workIQ - Auto-retrieve)

| Source | Status | Retrieval Method | Priority |
| ------ | ------ | ---------------- | -------- |
| Meetings/Calendar | ✅ Auto | workIQ `mcp_workiq_ask_work_iq` | ⭐⭐⭐ |
| Sent Emails | ✅ Auto | workIQ `mcp_workiq_ask_work_iq` | ⭐⭐⭐ |
| Edited Files | ✅ Auto | workIQ `mcp_workiq_ask_work_iq` | ⭐⭐ |
| Teams Meeting Notes | ✅ Auto | workIQ `mcp_workiq_ask_work_iq` | ⭐⭐ |
| OneNote | ✅ Auto | workIQ `mcp_workiq_ask_work_iq` | ⭐ |
| Planner/To Do | ✅ Auto | workIQ `mcp_workiq_ask_work_iq` | ⭐ |

### Manual Input (Supplementary)

| Source | Status | Retrieval Method |
| ------ | ------ | ---------------- |
| Teams Chat | ✅ Manual | Copy & Paste |
| Teams Meeting Notes | ✅ Manual | AI transcript copy |
| Outlook Email | ✅ Manual | Forward/Copy |

### File Reference

| Source | Status | Retrieval Method |
| ------ | ------ | ---------------- |
| Excel | ✅ Reference | File path |
| PowerPoint | ✅ Reference | File path |
| OneDrive | ✅ Reference | Path |
| SharePoint Online | ✅ Reference | URL/Path |

### External Folder Reference (Optional)

| Source | Path | Target Files |
| ------ | ---- | ------------ |
| **Configure in external-folders.md** | {path} | `_inbox/*.md`, `*_議事録.md` |

→ Details in [external-folders.md](external-folders.md)

### External Sources (Planned)

| Source | Status | Retrieval Method |
| ------ | ------ | ---------------- |
| GitHub Issues | 🔜 Planned | API integration |
| Azure DevOps | 🔜 Planned | API integration |

## Directory Structure

```
_datasources/
├── README.md               # This file
├── workiq-spec.md          # workIQ data retrieval spec
├── external-folders.md     # External folder reference config
└── scripts/
    └── Check-ExternalFolders.ps1  # External folder check script
```

## workIQ Data Retrieval Spec

→ Details in [workiq-spec.md](workiq-spec.md)

### Quick Reference

```markdown
## Meeting Data
@workiq "List of meetings on {date}. Include meeting name, time, duration"

## Sent Emails
@workiq "Emails I sent on {date}. Include subject, time, recipient"

## Edited Files
@workiq "Word/PowerPoint/Excel files I edited on {date}"

## Teams Meeting Notes
@workiq "Decisions and action items from {meeting name}"

## OneNote
@workiq "OneNote pages I updated on {date}"
```

## Report Generation Priority

Data retrieval priority during report generation:

```
1. Workspace reports (daily/weekly)
2. workIQ auto-retrieve (meetings, emails, files, etc.)
3. Workspace data (inbox, tasks)
4. Estimated tasks to fill gaps ([Estimated] mark)
```
