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

`item.japanRegion` は可視スライド本文の「日本リージョン：」に直接表示される。判定は必ず以下 3 分類に分けてから書く。

### 判定フロー（必須）

1. **クライアント／IDE／CLI／SDK／PowerShell モジュールなど、リージョン概念が適用されないもの** → `japanEast=true, japanWest=true`, `status="グローバル（クライアント／IDE ベース）"`。`japanRegion` は「本機能はクライアント／IDE ベースのためリージョン非依存です（東日本／西日本を含む全リージョンから利用可）。」等。`japanRegionUrl` は付けない。
2. **公式 Docs (overview / whats-new / reliability / regions) にリージョン表または列挙がある** → grep して Japan East / Japan West が **含まれるか否か** を確認する:
   - 含まれる → `japanEast/West=true`, 従来文言
   - 含まれない → `supportedRegions` に近隣 3 件を日本語で埋め、`supportedRegionsTotal` に総数、`supportedRegionsSource` に該当ページ URL
3. **公式 Docs にリージョン表が本当に無い場合のみ** → `supportedRegions=[]`, `supportedRegionsSource` は overview URL に fallback (E1)。**判定は overview / reliability / whats-new / regions ページを最低 2 種類確認したうえで下す**（1 ページで見つからないだけで空判定にしない）。

**アンチパターン**:

- overview を fetch せずに「対応リージョン未確認」と保守判定 → **禁止**。必ず fetch してリージョン表の有無を目視する。
- クライアント／IDE ツール（`Az.*` PowerShell モジュール、GitHub Copilot 拡張、CLI、SDK など）を「日本未対応」判定 → **禁止**。リージョン非依存として扱う。

### フォーマット

- 対応リージョン明示あり: `現時点で日本未対応（Preview）。対応リージョン：<A> / <B> / <C>[ 他]。GA 時点で日本リージョン提供が予定されています（関連 MS Learn）。`
- 対応リージョン明示なし: `現時点で日本未対応（Preview）。対応リージョンは順次拡大中です。GA 時点で日本リージョン提供が予定されています（関連 MS Learn）。`
- クライアント／IDE ベース: `本機能はクライアント／IDE ベースのためリージョン非依存です（東日本／西日本を含む全リージョンから利用可）。`

### ルール

- 対応リージョンは**日本語表記**（例: `米国中西部` / `東南アジア` / `韓国中部`）、最大 3 件。総数 > 3 件なら末尾に「他」を付ける。
- 近隣 3 件を選ぶ優先順位: **アジア > オセアニア > 米国 > 欧州**。日本の顧客資料なので、地理的に近いリージョンを優先して並べる。
- 「関連 MS Learn」の 11 文字に `item.japanRegionUrl` の URL を run-level hyperlink で貼る（Build 側の `Set-BodySlideContent` が自動で貼る）。
- URL 優先順位: `region_info_reviewed.regions[topic].supportedRegionsSource` > `source` > `learnUrl`。どれも無ければ hyperlink は貼らない。
- `region_info_reviewed.regions[topic]` に SSOT として保存: `supportedRegions` / `supportedRegionsTotal` / `supportedRegionsSource`。
- 日本対応済み (`japanEast=true` or `japanWest=true`) の item には `japanRegionUrl` を付けない。
- `fetched-updates.json` の item schema にも `japanRegionUrl` を追加し、Prepare → classification.json 経由で Build まで伝搬させる。

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

After every build or re-apply, inspect the generated deck, not only script logs.

- Check unresolved placeholders on visible and hidden slides: `{{CUSTOMER}}`, `{{SYSTEM}}`, `{{DATE}}`, `{{SPEAKER}}`, or any `{{...}}`.
- Check customer honorifics: cover text must not duplicate suffixes such as `御中 御中` or `様 様`.
- Check visible-slide neutrality: outside the cover/metadata slide, visible slides must not contain customer name, system name, tenant domain, subscription IDs, or other customer-specific identifiers.
- Check reference affordance: visible update slides distinguish `Microsoft Learn` detail links from `Azure Updates` announcement links, and speaker notes carry the full source trail.
- Check P2 formatting: readable numbering, no placeholder text, and no duplicated bullet glyphs.
- Check classification intent: Weekly for customer-relevant or explicitly requested items; low-relevance items may be hidden Appendix.
- Check notes quality: customer profile context, in-use / not-in-use services, and concrete impact or no-impact rationale. Generic summaries are not enough.
- Check Ending quality: the visible Ending is a simple formal closure paired with the visible cover variant; it must not be blank, action-heavy, or a leftover `Next Steps` placeholder.
- For nontrivial decks, repeated gate failures, or customer delivery, run a rubber-duck style read-only critic review; reconcile blocking findings yourself and rerun the relevant validation.

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
