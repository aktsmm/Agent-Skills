# Migration Map (old `.github/*` + `scripts/*` → this skill)

This skill consolidates the previous repo-scoped customization into one portable MCP-first package. The table maps
original assets to their current homes and notes which legacy paths are intentionally not restored.

> 🔄 **SYNC NOTE**: Skill `scripts/` and `agents/` are the portable source. Workspace root `scripts/`
> and workspace `.github/agents/` copies, when present, are runtime or host-registry derivatives.

## Instructions (9) → references/

| Original `.github/instructions/`          | New home                                                                                                                                 |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `pre-check.instructions.md`               | [pre-check.md](pre-check.md)                                                                                                             |
| `pptx-slide-structure.instructions.md`    | [slide-structure.md](slide-structure.md) (merged)                                                                                        |
| `pptx-content-rules.instructions.md`      | [slide-structure.md](slide-structure.md) (merged)                                                                                        |
| `region-stamp.instructions.md`            | [region-stamp.md](region-stamp.md)                                                                                                       |
| `pptx-validation-rules.instructions.md`   | [validation-rules.md](validation-rules.md)                                                                                               |
| `mcp-sourced-content.instructions.md`     | [mcp-sourced-content.md](mcp-sourced-content.md)                                                                                         |
| `customer-keywords.instructions.md`       | [customer-profile.md](customer-profile.md) (abstract) + `assets/customer-keywords.template.json` + `assets/customer-profile.template.md` |
| `<customer>-azure-access.instructions.md` | [customer-profile.md](customer-profile.md) (Azure env, abstract) + `assets/customer-profile.template.md`                                 |
| `azure-update-pptx.instructions.md`       | `SKILL.md` (overview) + [slide-structure.md](slide-structure.md) + [template-requirements.md](template-requirements.md)                  |

## Agents (7) → agents/

All copied verbatim (frontmatter intact, customer strings abstracted), summarized in
[agents-overview.md](agents-overview.md): `orchestrator`, `prepare`, `review`, `build-pptx`,
`notes-generator`, `enrich`, `finalize` → `../agents/<name>.agent.md`.

## Prompts (4) → SKILL.md entry paths / retired paths

| Original `.github/prompts/`          | New home                                                                          |
| ------------------------------------ | --------------------------------------------------------------------------------- |
| `ppt_create-customer-pptx.prompt.md` | retired legacy source-PPTX path; current workflow is MCP-first                    |
| `ppt_create-from-mcp.prompt.md`      | SKILL.md "From MCP" entry path + [mcp-sourced-content.md](mcp-sourced-content.md) |
| `ppt_update.prompt.md`               | SKILL.md fast path (`Run-CustomerPptxPipeline.ps1 -SkipBuild`)                    |
| `review-session-export.prompt.md`    | out of scope (session export; left in repo, not part of this skill)               |

## Scripts (16) → scripts/ (byte-copies)

`Build-CustomerPptx.ps1`, `Cleanup-MasterLayouts-Slow.ps1`, `Enrich-CustomerPptx.ps1`,
`Export-PptxToPdf.ps1`, `Fetch-AzureUpdates.ps1`, `Fix-Labels.ps1`, `Fix-NoteMismatch.ps1`,
`Fix-RegionInfo.ps1`, `PptxCommon.psm1`, `Prepare-CustomerPptx.ps1`, `Refine-Template-Safe.ps1`,
`Refine-Template.ps1`, `Remove-LayoutPreviewBadge.ps1`, `Remove-StaleArtifacts.ps1`,
`Run-CustomerPptxPipeline.ps1`, `Verify-Pptx.ps1` → `../scripts/<same name>`.

> `scripts/Remove-StaleArtifacts.ps1` is a repo-maintenance helper; its hardcoded stale-file arrays were
> emptied (format examples kept). Populate per repo before use.

## Config / data / template

| Original                                               | New home                                                                   |
| ------------------------------------------------------ | -------------------------------------------------------------------------- |
| `.config/exclude-keywords.json` (live, customer values) | `.config/exclude-keywords.json` (generic starter)                           |
| `.config/config.json` (live, customer values)                  | NOT copied — use `assets/config.template.json`                             |
| `.config/processed-updates.json`                        | NOT copied — start from `[]` per repo                                      |
| `template/<branded>.pptx` (live, customer-branded)     | `assets/template/azure-update-template.pptx` (brand-neutral, placeholders) |

## Not migrated (stays repo-scoped)

- `AGENTS.md`, `copilot-instructions.md`, root `README.md` — repo wiring; keep these as thin entry points to this skill.
- Date folders (`MMDD/`), `output/` — customer data / binaries.

