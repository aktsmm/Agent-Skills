---
name: azure-update-customer-pptx
description: >-
  Build a customer-facing Azure Update PowerPoint from Azure Updates MCP results,
  including customer classification, Japan region stamps, UPDATE Points, speaker
  notes, and Verify-Pptx gate checks. Use when creating or updating an Azure
  Update / Azure アップデート customer deck, bootstrapping a new Azure Update PPTX
  workspace, reviewing Deploy Region support, or re-applying manifest JSON to an
  existing deck.
argument-hint: "Date folder, customer config/profile, Azure Updates IDs/range, or workspace root"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Azure Update Customer PPTX

Portable MCP-first toolkit for turning Azure Updates into a customer-facing Azure Update deck.

## When To Use

- "Azure Update PPT を作って", "顧客向け Azure アップデート資料", "今月の Azure Update スライド"
- Bootstrapping a blank workspace from this skill's assets/scripts
- Fetching Azure Updates by MCP and classifying them for a customer
- Rebuilding / enriching an existing date folder from manifest JSON
- Fixing labels, notes, region stamps, UPDATE Points, or gate failures in this workflow

## When Not To Use

- General PowerPoint editing or design-only cleanup
- Non-Microsoft or non-Azure update decks
- Workflows that do not use Azure Updates MCP or MCP-sourced manifest JSON
- One-off extraction from an arbitrary existing PPTX without this manifest contract

## Execution Model

This skill is a toolkit, not a standalone runner. It carries scripts, references, starter config, and a neutral template. A usable workspace must have:

- `.config/config.json`
- `.config/customer-keywords.json`, `.config/customer-profile.md`, `.config/exclude-keywords.json`
- `scripts/*.ps1` and `scripts/PptxCommon.psm1`
- `template/*.pptx`
- `{MMDD}/manifest/` and `{MMDD}/logs/`

If any workspace contract file is missing, do not build. Run Bootstrap first, then fill `.config`.

## Mode Selection

1. **Bootstrap**: no `.config/config.json`, no root `scripts/`, or no template. Run `scripts/Initialize-AzureUpdateWorkspace.ps1` from the skill.
2. **Fetch**: date folder exists but `manifest/fetched-updates.json` is missing. Use Azure Updates MCP through the agent path and write manifest JSON.
3. **Prepare**: fetched updates exist but classification / initial region JSON is missing. Run `Prepare-CustomerPptx.ps1`.
4. **Build**: manifests exist but PPTX is missing. Run `Run-CustomerPptxPipeline.ps1` without `-SkipBuild`.
5. **Re-apply**: PPTX exists and manifest JSON changed. Run `Run-CustomerPptxPipeline.ps1 -SkipBuild`.
6. **Repair**: Verify fails. Fix only the failed slice, then rerun the same gate.

## MCP Boundary

- Scripts do not call MCP directly.
- MCP-sourced content is written to `{date}/manifest/*.json` by Copilot / agent steps.
- PowerShell scripts consume manifest JSON and mutate PPTX deterministically.
- A sample MCP config is provided at `assets/mcp.sample.json`; it uses placeholders and must be adapted to the host's actual MCP server commands.

## Bootstrap

From a blank workspace, run:

```powershell
& ".\.github\skills\azure-update-customer-pptx\scripts\Initialize-AzureUpdateWorkspace.ps1" -TargetRoot "." -UpdateScripts
```

Rules:

- Existing customer config is never overwritten by default.
- Existing config conflicts are written as `.new` files.
- Use `-UpdateScripts` to refresh root `scripts/` from the skill.
- Use `-ForceConfig` only when intentionally replacing starter config.

After Bootstrap, ask for missing customer values before generating a deck:

- customer name and system name
- fiscal year / output filename pattern
- template choice or branding requirement
- priority services, in-use SKUs, and monitored SKUs
- services or categories that should usually go to Appendix
- tenant / subscription reference values when region or impact review needs them

## Standard Run

```powershell
$d = "0704"
New-Item -ItemType Directory -Force "$d\manifest", "$d\logs" | Out-Null
# Agent step: write $d/manifest/fetched-updates.json from Azure Updates MCP
& ".\scripts\Prepare-CustomerPptx.ps1" -DateFolder ".\$d"
# Agent steps: review region info and generate notes JSON
& ".\scripts\Run-CustomerPptxPipeline.ps1" -DateFolder ".\$d"
```

Fast re-apply after manifest-only changes:

```powershell
& ".\scripts\Run-CustomerPptxPipeline.ps1" -DateFolder ".\0704" -SkipBuild
```

## Validation

Run preflight before build/re-apply:

```powershell
& ".\scripts\Test-AzureUpdateWorkspace.ps1" -TargetRoot "." -DateFolder ".\0704"
```

Final success is `scripts/Verify-Pptx.ps1` exit code `0`. The current gate has 9 checks; keep `references/validation-rules.md` aligned with `Verify-Pptx.ps1`.

## SSOT And Runtime Copies

- Skill `scripts/` is the portable source for newly bootstrapped workspaces.
- Root `scripts/` is the runtime copy used by a customer workspace.
- Refresh runtime scripts only through `Initialize-AzureUpdateWorkspace.ps1 -UpdateScripts` or an intentional manual sync.
- Customer-specific values belong in workspace `config*` files and date-folder manifests, never in skill references.

## Agent Registry

- Skill `agents/` is the role-definition source for this workflow.
- Copy agents to workspace `.github/agents/` only when the host requires a workspace agent registry.
- Copied workspace agents are derived artifacts; do not hard-code customer values in them.

## References

- `references/pre-check.md`: preflight and PowerPoint guardrails
- `references/mcp-sourced-content.md`: manifest contract and MCP boundary
- `references/validation-rules.md`: gate checks
- `references/template-requirements.md`: template expectations
- `references/agents-overview.md`: agent role boundaries
- `references/slide-structure.md`: section order, label priority, and UPDATE Points layout
- `references/region-stamp.md`: Deploy Region rule and region stamp styles
- `references/customer-profile.md`: customer profile template guidance
- `references/dependencies.md`: related skills and dependency boundaries
- `references/migration-map.md`: legacy layout migration notes

## Done Criteria

- Workspace contract exists or Bootstrap completed
- `manifest/fetched-updates.json`, `classification.json`, reviewed region JSON, and `notes.json` exist
- Deck has section order, label order, UPDATE Points, notes, and region stamps applied
- `Verify-Pptx.ps1` exits `0`
