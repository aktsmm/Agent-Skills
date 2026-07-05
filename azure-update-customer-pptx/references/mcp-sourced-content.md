# MCP-sourced Content Contract

MCP fetch and research are agent-mediated. PowerShell scripts consume JSON and do not call MCP directly.

## Required Manifests

| File                                 | Producer                     | Consumer                   |
| ------------------------------------ | ---------------------------- | -------------------------- |
| `manifest/fetched-updates.json`      | Azure Updates MCP agent step | `Prepare-CustomerPptx.ps1` |
| `manifest/classification.json`       | Prepare / AI classification  | Build / Enrich             |
| `manifest/region_info_reviewed.json` | Review agent step            | Enrich / Verify            |
| `manifest/notes.json`                | Notes agent step             | Enrich / Verify            |
| `manifest/verify_status.json`        | Pipeline script              | Final report               |

If `fetched-updates.json` is missing, do not start raw PowerShell build. Fetch through the MCP path first.
