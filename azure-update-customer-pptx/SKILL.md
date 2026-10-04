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
- Designing or validating a customer-specific PowerPoint template before automation
- Rebuilding / enriching an existing date folder from manifest JSON
- Fixing labels, notes, region stamps, UPDATE Points, or gate failures in this workflow

## When Not To Use

- General PowerPoint editing or design-only cleanup
- Non-Microsoft or non-Azure update decks
- Workflows that do not use Azure Updates MCP or MCP-sourced manifest JSON
- One-off extraction from an arbitrary existing PPTX without this manifest contract

## Execution Model

This skill is a toolkit, not a standalone runner. It carries scripts, references, starter config, and a neutral template. Required files: [Pre-check › Workspace Contract](references/pre-check.md#workspace-contract).

If any workspace contract file is missing, do not build. Run Bootstrap first, then fill `.config`.

## Mode Selection

1. **Bootstrap**: no `.config/config.json`, no root `scripts/`, or no template folder. Run `Initialize-AzureUpdateWorkspace.ps1` and fill `.config`.
2. **Template Design**: no customer-approved template exists. Work in PowerPoint first; scripts may inspect, but must not invent the design.
3. **Template Contract**: a candidate template exists. Validate required layouts, placeholders, sections, table shape, hidden-slide policy, and branding before content build.
4. **Fetch/Prepare**: date folder exists but manifests are missing or stale. Use Azure Updates MCP to write `fetched-updates.json`, then run `Prepare-CustomerPptx.ps1`.
5. **Build/Re-apply**: manifests and template contract are ready. Run `Run-CustomerPptxPipeline.ps1` or `-SkipBuild` for manifest-only changes.
6. **Repair**: Verify fails. Fix only the failed slice, then rerun the same gate.

Build engine selection: missing `build.engine` means `com`. Use `python` only for contract-v1 templates;
it fails closed and never silently falls back to COM. See [Python Build Engine](references/python-build-engine.md).

## MCP Boundary

- Script/MCP split and `sourceUrl` / `learnUrl` rules: [MCP-sourced Content › MCP Boundary](references/mcp-sourced-content.md#mcp-boundary).
- Slide-visible manifest fields, including `title` and `titleJa`, must stay reusable and customer-neutral. Customer/system-specific impact belongs in `notes.json` or review notes, not in visible body fields such as `customerImpact`, `background`, `before`, `after`, `pricing`, or `keypoint`.

## Previous Delivery Diff (必須)

新しい `{date}` フォルダを作るときは、前回 delivery からの差分を必ず MCP で確認する。抜けを見つけたら、そのまま今回に追加するか次回へ持ち越すかをユーザーに確認する。手順（`previousEndDate` 起点の Fetch 範囲、境界日の二重チェック、`logs/diff-check.md`）: [Previous Delivery Diff](references/delivery-diff.md#steps)。

## Japan Region Rendering (可視スライド)

`item.japanRegion` は可視スライド本文へ直接表示される。判定は [Region Stamp Definition](references/region-stamp.md) を SSOT とし、必ず次の3分類を通す: [Region Stamp Definition › Japan Region Rendering Flow](references/region-stamp.md#japan-region-rendering-flow)。

overview未確認の保守判定と、クライアントツールの日本未対応判定は禁止する。可視文言、近隣regionの優先順、URL伝搬、reviewed JSON schemaは [Region Stamp Definition](references/region-stamp.md) に従う。

## Bootstrap

From a blank workspace, run:

```powershell
& ".\.github\skills\azure-update-customer-pptx\scripts\Initialize-AzureUpdateWorkspace.ps1" -TargetRoot "." -UpdateScripts
```

Options (`-CopyMcpSample`, `.new` conflicts, `-ForceConfig`): [Pre-check › Bootstrap Options](references/pre-check.md#bootstrap-options).

After Bootstrap, ask for missing customer values before generating a deck: customer/system name, filename year/pattern, template/branding, priority services, in-use or monitored SKUs, Appendix categories, and tenant/subscription references when needed.

## Standard Run

```powershell
$d = "0704"
New-Item -ItemType Directory -Force "$d\manifest", "$d\logs" | Out-Null
# Agent step: write $d/manifest/fetched-updates.json from Azure Updates MCP
# Agent step: add customer-neutral Japanese `titleJa` for every selected update before Prepare
& ".\scripts\Prepare-CustomerPptx.ps1" -DateFolder ".\$d"
# Agent steps: review region info and generate notes JSON
& ".\scripts\Run-CustomerPptxPipeline.ps1" -DateFolder ".\$d"
# Agent step: inspect generated deck quality before reporting done
```

Fast re-apply after manifest-only changes (`-SkipBuild`): [Pre-check › Fast Re-apply](references/pre-check.md#fast-re-apply).

Template setup is intentionally separate from regular generation. See [Template Lifecycle](references/template-lifecycle.md) before automating a new customer template.

## Gotchas

- Close the target deck before any COM write, and re-apply all sections after any Weekly rebuild. Details and other COM pitfalls: [Validation Rules › COM Write Gotchas](references/validation-rules.md#com-write-gotchas).

## Validation

Run preflight (`Test-AzureUpdateWorkspace.ps1`) before build/re-apply: [Pre-check › Preflight Command](references/pre-check.md#preflight-command).

Final script success is `scripts/Verify-Pptx.ps1` exit code `0`. Do not report final done until the quality review below also passes or the remaining issue is explicitly reported.

## Quality Review Loop

After every build or re-apply, inspect the generated deck rather than trusting logs. Apply all script and visual checks in [Validation Rules](references/validation-rules.md), including placeholders, customer neutrality, links, notes, Ending, Appendix visibility, region evidence, and critic review for nontrivial delivery decks.

## SSOT And Runtime Copies

Skill/runtime ownership and refresh rules are defined in [Dependencies](references/dependencies.md). Customer-specific values belong in workspace config and manifests, never in skill references.

## Agent Registry

Skill `agents/` is the role-definition source; workspace copies are derived. Rules: [Agents Overview › Agent Registry](references/agents-overview.md#agent-registry).

## References

- Preflight/template: `pre-check.md`, `template-lifecycle.md`, `template-requirements.md`
- Content/validation: `mcp-sourced-content.md`, `validation-rules.md`, `slide-structure.md`, `region-stamp.md`, `delivery-diff.md`
- Operation/migration: `customer-profile.md`, `agents-overview.md`, `dependencies.md`, `migration-map.md`

## Done Criteria

- Workspace contract exists or Bootstrap completed
- Customer-specific template is designed, approved, and contract-validated before regular build automation
- `manifest/fetched-updates.json`, `classification.json`, reviewed region JSON, and `notes.json` exist
- Weekly items use Azure Updates `sourceUrl` and, where available, Microsoft Learn `learnUrl`
- Deck has section order, label order, UPDATE Points, notes, and region stamps applied
- Visible reference labels and hyperlinks distinguish Microsoft Learn detail pages from Azure Updates announcements
- The Ending slide says only a concise formal closure such as `以上` / `Azure アップデート情報`, and non-selected ending variants are hidden
- `Verify-Pptx.ps1` exits `0`
- Immediately before customer delivery, `Test-PptxDistribution.ps1` passes for the exact PPTX/PDF pair; Python-engine delivery also requires nonempty PDF text extraction and customer-safe body checks.
- Quality review passes: no unresolved placeholders, duplicate honorifics, visible customer-specific terms outside cover/metadata, malformed bullets, weak notes, or Appendix visibility mismatch
- Rubber-duck / critic review is completed or explicitly skipped with a reason for nontrivial customer-delivery decks
