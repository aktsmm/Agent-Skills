---
name: Prepare
description: MCP取得済みAzure Updatesを日本語表示タイトル付きで分類し、初期リージョン情報を作成
user-invocable: false
---

# Prepare Agent

## Role

Azure Updates MCPの取得結果を、顧客向けdeckの分類入力へ変換する。ソースPPTXの解凍・分析は現行フローに含めない。

## Inputs

- `{date}/manifest/fetched-updates.json`: Azure Updates MCP取得結果
- `.config/config.json`, `.config/customer-keywords.json`, `.config/exclude-keywords.json`, `.config/customer-profile.md`
- `references/pre-check.md`, `references/customer-profile.md`, `references/slide-structure.md`

Each fetched item must have `id`, `title`, `label`, `sourceUrl`; retain `products` / `productCategories` when supplied by MCP.

- `title`: byte-exact Azure Updates原題。不変の分類・notes・region join key。
- `titleJa`: 顧客可視の日本語表示タイトル。新規workspaceでは必須。

## Outputs

- `{date}/manifest/classification.json`
- `{date}/manifest/region_info.json`

## Required Flow

1. Read the pre-check, customer profile, and slide structure references.
2. Use Azure Updates MCP to create `fetched-updates.json`; retain `title` and `sourceUrl` as received.
3. Before Prepare, add `titleJa` to every item:
   - concise natural Japanese, normally within 36 full-width characters and two rendered lines
   - preserve official product, SKU, and protocol names
   - do not include GA/Preview/Retirement wording; the label badge owns status display
   - do not add customer/system-specific terms
4. Run:

```powershell
& "$BasePath\scripts\Prepare-CustomerPptx.ps1" -DateFolder "{date}"
```

5. Review `classification.json`:
   - `title` is preserved as the raw join key and `titleJa` is present on every item
   - label/category/exclusion/keypoint use raw `title` plus products/categories
   - Weekly and Appendix are sorted by label priority then raw title
6. Produce `region_info.json` keyed by raw `title`; hand it to Review for Docs-backed verification.

## Gates

- `fetched-updates.json` exists before Prepare. A new config with `content.requireTitleJa=true` must fail Prepare when any item lacks `titleJa`.
- Every update is in exactly one of Weekly / Appendix and classification contains at least one Weekly item.
- `titleJa` has no status wording, is customer-neutral, and is unique and not prefix-related after 12 normalized characters.
- If `titleJa` changes after Prepare, rerun Prepare, region review, notes generation, and saved-deck verification together.
- Report the actual exit code; do not infer success.

## Next

Hand off `classification.json` and `region_info.json` to Review.
