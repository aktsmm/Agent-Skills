# Dependencies and scope

This skill focuses on the **Azure Update customer-deck workflow** (classification, region stamps,
UPDATE Points table, notes, validation gate, MCP sourcing). It deliberately does not re-document general
PowerPoint mechanics.

## PowerPoint COM (generic behavior)

This skill's scripts already implement the COM / python-pptx operations the workflow needs. Generic
behaviors they rely on:

- COM Automation against an open PowerPoint (win32com): close only the target presentation, never other open decks
- RefURL pattern: bottom-left "page title + URL" text boxes with shape-level hyperlinks
- Overflow is checked by the validation gate; fix text length rather than relying on autofit

Out of scope: general deck translation / editing, screenshots, icons, video, and debugging generic COM,
autofit, or hyperlink mechanics outside this workflow.

## Python build engine

The optional Python build phase uses `python-pptx` and Pillow from the checked-in
`scripts/python/requirements.lock`. It requires an existing workspace `.venv`; skill scripts never install
or mutate global packages. PowerPoint remains required for PDF export, rendering, and final delivery gates.
Python-engine customer distribution additionally uses pinned `pypdf` to extract the actual PDF text; it is
not a build dependency, but the distribution gate fails closed when it is unavailable.
Pipeline and verifier wrappers require PowerShell 7 (`pwsh`); Windows PowerShell 5.1 is not supported.

## Orchestration pattern

This skill's pipeline uses the **Orchestrator-Workers** pattern (a coordinator that delegates
to parallel workers and joins their outputs — see [agents-overview.md](agents-overview.md)).

Out of scope: general workflow-design questions such as whether a new piece should be an agent, a
script, or a reference, or whether the orchestration is over-engineered.

## Microsoft docs / Azure Updates MCP

Two MCP servers are used. Tool name prefixes vary by host (e.g. `mcp_releasecommun_*`,
`mcp_microsoft_lea_*`); match against your host's registered tools.

| MCP server                                             | Endpoint URL                                          | Tools                                                                                      | Use                                                               |
| ------------------------------------------------------ | ----------------------------------------------------- | ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| Azure Updates — Microsoft Release Communications (MRC) | `https://www.microsoft.com/releasecommunications/mcp` | `*_get_recent_azure_updates` (list, OData filter) / `*_get_azure_update_by_id` (full body) | fetch + detail Azure Updates (region hint, status, body)          |
| Microsoft Learn Docs                                   | `https://learn.microsoft.com/api/mcp`                 | `*_microsoft_docs_search` / `*_microsoft_docs_fetch`                                       | verify region (Deploy Region), retirement dates, GA/Preview state |

- The MRC server also powers M365 Roadmap; this skill uses only the Azure Updates tools. No auth / no license required (subject to Microsoft API Terms of Use). Source: https://learn.microsoft.com/microsoft-365/admin/manage/mrc-mcp
- Endpoints are for MCP clients over streamable HTTP, not direct browser/API calls; tool names/schemas may change — discover via `tools/list`, don't hardcode.
- Azure Updates MCP: list with `*_get_recent_azure_updates`, then deep-dive each id with
  `*_get_azure_update_by_id`. Prefer one-by-one over wide parallel batches.
- Microsoft Learn Docs MCP: always prefer ja-jp URLs (`learn.microsoft.com/ja-jp/...`) in output.
- These are the only external services this skill calls; both are read-only.

## Boundary

| Need                                                              | Where                    |
| ----------------------------------------------------------------- | ------------------------ |
| Azure Update classification / region stamp / UPDATE Points / gate | **this skill**           |
| Region / status / body facts                                      | docs & Azure Updates MCP |
| Generic deck editing / translation / workflow design              | out of scope             |
