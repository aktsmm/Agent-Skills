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

## Per-Item Reference Rules

Each `fetched-updates.json` item should carry both reference layers when possible:

- `sourceUrl`: Azure Updates / Release Communications announcement URL.
- `learnUrl`: closest Microsoft Learn or official Docs page for the underlying service feature, found through Microsoft Learn Docs MCP. Leave `null` only when no relevant first-party documentation exists after a targeted search.
- Visible slides must label these roles explicitly: `詳細：Microsoft Learn` for `learnUrl`, and `発表：Azure Updates` for `sourceUrl`.
- Speaker notes should carry the full source trail: `Microsoft Learn 詳細: <url>` and `Azure Updates 発表: <url>`.
- If `learnUrl` is `null`, add a review note such as `learnUrl_note` explaining whether no first-party page was found or the page is still unverified.

## Visible Content Boundary

Visible slide body fields must be reusable across decks. Keep `background`, `before`, `after`, `customerImpact`, `pricing`, `japanRegion`, and `keypoint` customer-neutral.

Do not put customer name, system name, tenant domain, subscription IDs, or internal environment labels in visible body fields. Put customer-specific impact or applicability in `notes.json` speaker notes or a review-only artifact.

Examples:

- Use: `GCS から Azure Blob Storage への移行予定がなければ直接影響は限定的です。`
- Avoid: `現行の {SYSTEM} で GCS 利用がなければ直接影響は限定的です。`
