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

This skill is a toolkit, not a standalone runner. It carries scripts, references, starter config, and a neutral template. A usable workspace must have:

- `.config/config.json`
- `.config/customer-keywords.json`, `.config/customer-profile.md`, `.config/exclude-keywords.json`
- `scripts/*.ps1` and `scripts/PptxCommon.psm1`
- `template/*.pptx`
- `{MMDD}/manifest/` and `{MMDD}/logs/`

If any workspace contract file is missing, do not build. Run Bootstrap first, then fill `.config`.

## Mode Selection

1. **Bootstrap**: no `.config/config.json`, no root `scripts/`, or no template folder. Run `Initialize-AzureUpdateWorkspace.ps1` and fill `.config`.
2. **Template Design**: no customer-approved template exists. Work in PowerPoint first; scripts may inspect, but must not invent the design.
3. **Template Contract**: a candidate template exists. Validate required layouts, placeholders, sections, table shape, hidden-slide policy, and branding before content build.
4. **Fetch/Prepare**: date folder exists but manifests are missing or stale. Use Azure Updates MCP to write `fetched-updates.json`, then run `Prepare-CustomerPptx.ps1`.
5. **Build/Re-apply**: manifests and template contract are ready. Run `Run-CustomerPptxPipeline.ps1` or `-SkipBuild` for manifest-only changes.
6. **Repair**: Verify fails. Fix only the failed slice, then rerun the same gate.

## MCP Boundary

- Scripts do not call MCP directly; Copilot / agent steps write MCP-sourced content to `{date}/manifest/*.json`.
- PowerShell scripts consume manifest JSON and mutate PPTX deterministically. Adapt `assets/mcp.sample.json` to the host MCP server if needed.
- For each Azure Updates item, store the announcement URL as `sourceUrl` and search Microsoft Learn / Docs MCP for the closest official service document. Put that URL in `learnUrl` when a relevant first-party page exists.
- Slide-visible manifest fields must stay reusable and customer-neutral. Customer/system-specific impact belongs in `notes.json` or review notes, not in visible body fields such as `customerImpact`, `background`, `before`, `after`, `pricing`, or `keypoint`.

## Previous Delivery Diff (必須)

新しい `{date}` フォルダを作るときは、前回 delivery からの差分を必ず MCP で確認する。抜けを見つけたら、そのまま今回に追加するか次回へ持ち越すかをユーザーに確認する。

1. `previousDate` を決める: 直近の `{MMDD}/manifest/classification.json` を持つフォルダ。 fetched-updates.json が無い場合は `{date}/logs/` や README の「対象週」記述から範囲を割り出す。
2. `previousEndDate` を出す: 前回の対象末日（例: 0622 は `20260618` PPTX まで＝2026-06-18）。
3. 今回 Fetch 範囲を `created ge <previousEndDate+1> and created le <today>` にする。Days ベースの fallback ではなく、前回終端を必ず使う。
4. 二重チェック: `mcp_releasecommun_get_recent_azure_updates` で `created ge <previousEndDate> and created le <newStartDate-1>` を投げて 0 件になることを確認する（境界日で漏れが出やすい）。
5. 見つけた抜け item を `{date}/logs/diff-check.md` に「id / title / created / 追加 or 次回持ち越し」で残す。

## Japan Region Rendering (可視スライド)

`item.japanRegion` は可視スライド本文へ直接表示される。判定は [Region Stamp Definition](references/region-stamp.md) を SSOT とし、必ず次の3分類を通す。

### 判定フロー（必須）

1. クライアント／IDE／CLI／SDKなどリージョン非依存のものはグローバルとして扱う。
2. 公式Docsにdeploy regionの表・列挙があれば、Japan East / Westの有無と近隣regionを確認する。
3. 表がない判定はoverview / reliability / whats-new / regionsのうち最低2種類を確認してから行う。

overview未確認の保守判定と、クライアントツールの日本未対応判定は禁止する。可視文言、近隣regionの優先順、URL伝搬、reviewed JSON schemaは [Region Stamp Definition](references/region-stamp.md) に従う。

## Bootstrap

From a blank workspace, run:

```powershell
& ".\.github\skills\azure-update-customer-pptx\scripts\Initialize-AzureUpdateWorkspace.ps1" -TargetRoot "." -UpdateScripts
```

If you also want a ready-to-use VS Code workspace MCP config, add `-CopyMcpSample`. This writes `.vscode/mcp.json` with the Microsoft Learn Docs and MRC remote MCP endpoints unless the file already exists.

Rules: keep existing customer config by default, write starter conflicts as `.new`, use `-UpdateScripts` for runtime script refresh, and use `-ForceConfig` only for intentional config replacement.

After Bootstrap, ask for missing customer values before generating a deck: customer/system name, filename year/pattern, template/branding, priority services, in-use or monitored SKUs, Appendix categories, and tenant/subscription references when needed.

## Standard Run

```powershell
$d = "0704"
New-Item -ItemType Directory -Force "$d\manifest", "$d\logs" | Out-Null
# Agent step: write $d/manifest/fetched-updates.json from Azure Updates MCP
& ".\scripts\Prepare-CustomerPptx.ps1" -DateFolder ".\$d"
# Agent steps: review region info and generate notes JSON
& ".\scripts\Run-CustomerPptxPipeline.ps1" -DateFolder ".\$d"
# Agent step: inspect generated deck quality before reporting done
```

Fast re-apply after manifest-only changes:

```powershell
& ".\scripts\Run-CustomerPptxPipeline.ps1" -DateFolder ".\0704" -SkipBuild
```

Template setup is intentionally separate from regular generation. See `references/template-lifecycle.md` before automating a new customer template.

## Validation

Run preflight before build/re-apply:

```powershell
& ".\scripts\Test-AzureUpdateWorkspace.ps1" -TargetRoot "." -DateFolder ".\0704"
```

Final script success is `scripts/Verify-Pptx.ps1` exit code `0`. Do not report final done until the quality review below also passes or the remaining issue is explicitly reported.

## Quality Review Loop

After every build or re-apply, inspect the generated deck rather than trusting logs. Apply all script and visual checks in [Validation Rules](references/validation-rules.md), including placeholders, customer neutrality, links, notes, Ending, Appendix visibility, region evidence, and critic review for nontrivial delivery decks.

## SSOT And Runtime Copies

Skill/runtime ownership and refresh rules are defined in [Dependencies](references/dependencies.md). Customer-specific values belong in workspace config and manifests, never in skill references.

## Agent Registry

- Skill `agents/` is the role-definition source for this workflow.
- Copy agents to workspace `.github/agents/` only when the host requires a workspace agent registry.
- Copied workspace agents are derived artifacts; do not hard-code customer values in them.

## References

- Preflight/template: `pre-check.md`, `template-lifecycle.md`, `template-requirements.md`
- Content/validation: `mcp-sourced-content.md`, `validation-rules.md`, `slide-structure.md`, `region-stamp.md`
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
- Quality review passes: no unresolved placeholders, duplicate honorifics, visible customer-specific terms outside cover/metadata, malformed bullets, weak notes, or Appendix visibility mismatch
- Rubber-duck / critic review is completed or explicitly skipped with a reason for nontrivial customer-delivery decks
