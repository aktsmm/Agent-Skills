# Region Stamp Definition

Source: `region-stamp.instructions.md`. **SSOT** — this definition must match `.config/config.json` →
`regionStamp` and the scripts that apply stamps. `applyTo` (as repo instruction):
`**/scripts/*.ps1,**/*.pptx`.

## Stamp types and colors

| Type | Text | Background (RGB) | Use |
| --- | --- | --- | --- |
| グローバル | `グローバル` | green `#00B050` | all regions (retirements etc.) |
| 日本リージョン未対応 | `日本リージョン未対応` | blue `#005EB8` | neither Japan East nor West |
| Japan East のみ | `Japan East のみ対応` | light blue `#0078D4` | Japan East only |
| Japan West のみ | `Japan West のみ対応` | light blue `#0078D4` | Japan West only |
| Japan East / West 対応 | `Japan East / West 対応` | cyan `#00B0F0` | both |

## Placement

- Position: bottom-right of the slide
- Size: 180pt × 30pt (template-derived)
- Margin: 20pt from right, 20pt from bottom
- Font: 14pt, bold, white
- `Shape.Name`: starts with `RegionStamp`
- 🔴 **De-dup**: the template has 5 named sample stamps (`RegionStamp_JapanBoth` etc.). When applying,
  delete existing by **prefix match `RegionStamp*`** then add the single correct one. Exact-match delete
  leaves the 5 samples overlapping under the MCP body-template duplication path.

## 🔴 Offer Availability vs Deploy Region (critical)

| Concept | Meaning | Use for region? |
| --- | --- | --- |
| Offer Availability (purchasable countries) | where you can buy/contract the service | ❌ never |
| Deploy Region | where the resource is actually deployed | ✅ judge by this |

Watch: Azure AI Foundry / Azure OpenAI (judge by Hub/Project deploy region), Marketplace services
(availability ≠ deploy region), Global Standard deployments (broad offer, limited deploy), Hybrid /
migration management services (check data path & target constraints if the resource region is only
control/metadata).

MCP verification steps: (1) search `{service} region availability`; (2) identify Offer vs Deploy;
(3) if only "Available in: Japan", search `{service} supported regions`; (4) if explicit deploy
regions are listed (e.g. East US 2, Sweden Central), judge by those.

> ⚠️ Past incident: an "Offer Availability includes Japan → グローバル" misjudgement; real Deploy
> Region was East US 2 / Sweden Central only = 日本リージョン未対応.

## Judgement priority

0. Web tool / portal feature / docs update (not region-specific) → **グローバル**.
   0a. Hybrid / migration management service whose resource region is only control/metadata and whose
   data path / target storage does not block Japan use → **グローバル**.
1. Retirement / 廃止 / サポート終了 → **グローバル**.
2. `global: true` → **グローバル**.
3. Defined in `region_info_reviewed.json` → use that value (Review-verified).
   4a. Private Preview, no region limit stated → **Japan East / West 対応** (sign-up required).
   4b. Preview with stated region limit → only the stated regions.
   4c. Preview, insufficient info → **日本リージョン未対応** (fail-safe).
4. GA with no region limit → **グローバル**.
5. Unknown → **日本リージョン未対応** (default).

> ⚠️ Always go through Review-agent MCP verification. Never ship Prepare's initial judgement as-is.

## region_info.json (Prepare initial output)

```json
{
  "generatedAt": "2026-01-19T20:00:00",
  "generatedBy": "Prepare Agent (初期判定)",
  "regions": {
    "スライドタイトル": {
      "japanEast": true, "japanWest": false,
      "status": "Japan East のみ対応",
      "source": "https://learn.microsoft.com/...",
      "note": "Review Agent で再検証必要"
    }
  }
}
```

## region_info_reviewed.json — canonical schema (SSOT)

🔴 The only canonical definition. Review agent and Enrich scripts must conform.

```json
{
  "generatedAt": "2026-01-19T21:00:00",
  "generatedBy": "Review Agent (MCP再検証)",
  "reviewNote": "全エントリをMCPで検証完了",
  "corrections": [
    { "topic": "...", "originalStatus": "...", "correctedStatus": "...", "reason": "..." }
  ],
  "regions": {
    "スライドタイトル（完全一致キー）": {
      "japanEast": true, "japanWest": false,
      "status": "Japan East のみ対応",
      "source": "https://learn.microsoft.com/...",
      "evidence": "Supported regions list: Japan East only",
      "verified": true
    }
  }
}
```

Fields (all required): `japanEast` bool, `japanWest` bool, `status` (one canonical text below),
`source` URL, `evidence` (concrete wording), `verified` bool. The region key must be the **byte-exact
slide title** (join key). **Forbidden**: emoji (✅❌) in `status`, the deprecated `stamp` field.

Canonical `status` values: `グローバル` / `Japan East / West 対応` / `Japan East のみ対応` /
`Japan West のみ対応` / `日本リージョン未対応`.

## Required rules

1. Review-agent verification mandatory (never ship Prepare's initial judgement).
2. Investigate region via Microsoft Docs MCP (`microsoft_docs_search`).
3. Check the "Limitations" section for "limited to".
4. Record `source` URL in `region_info_reviewed.json`.
5. `evidence` required (concrete wording of the basis).
6. No guessing — if unconfirmed in docs, use 日本リージョン未対応 (fail-safe).

