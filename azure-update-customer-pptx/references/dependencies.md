# Dependencies (related skills — do not duplicate)

This skill focuses on the **Azure Update customer-deck workflow** (classification, region stamps,
UPDATE Points table, notes, validation gate, MCP sourcing). It deliberately does not re-document general
PowerPoint mechanics. Reference these instead.

## powerpoint-automation skill

General PPTX engineering. Use it for the underlying COM / python-pptx mechanics this workflow builds on:

- COM Automation against an open PowerPoint (win32com), target-only close, restore
- RefURL pattern (bottom-left "page title + URL" text boxes with shape-level hyperlinks)
- Overflow review, autofit, text-frame handling
- Translating / editing existing decks, screenshots, icons, video

This skill's scripts already implement the Azure-Update-specific COM operations; when you need to debug
COM behavior, autofit, or hyperlink mechanics generally, defer to `powerpoint-automation`.

## agentic-workflow-guide skill

The SSOT for primitive selection (prompt vs instruction vs skill vs agent vs hook) and multi-agent
design. This skill's pipeline uses the **Orchestrator-Workers** pattern (a coordinator that delegates
to parallel workers and joins their outputs — see [agents-overview.md](agents-overview.md)). Use the
guide when:

- deciding whether a new piece of this workflow should be an agent, a script, or a reference
- reviewing or refactoring the 7-agent orchestration
- judging whether the orchestration is over-engineered for a given run

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
| Generic COM / RefURL / overflow / translate                       | powerpoint-automation    |
| Should this be an agent/script/reference?                         | agentic-workflow-guide   |
| Region / status / body facts                                      | docs & Azure Updates MCP |
