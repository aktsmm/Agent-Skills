---
name: azure-troubleshooting
description: "Investigate Azure incidents and service degradations with a read-only workflow using Azure CLI, Resource Health, Activity Log, and official Microsoft docs. Use when troubleshooting Azure outages, Resource Health alerts, AKS incidents, App Service failures, database connectivity issues, Entra ID sign-in problems, load balancer issues, VPN Gateway or BGP instability, VM availability problems, platform-vs-workload cutover, or drafting a troubleshooting report. Triggers on 'Azure トラブルシューティング', '障害調査', '切り分け', 'Resource Health', '復旧確認', 'AKS', 'App Service', 'SQL', 'PostgreSQL', 'Cosmos DB', 'Entra ID', 'VPN Gateway', 'BGP', 'flap', 'incident', 'degraded', 'unavailable'."
argument-hint: "subscription ID, resource ID(s), symptom, occurrence time, and current user impact"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Azure Troubleshooting

Azure の障害調査、切り分け、初動確認、復旧確認を read-only で進め、事実ベースのレポートへ落とすための workspace skill。

## When to Use

- Azure リソースの障害、性能劣化、到達性異常を調査したいとき
- Azure Resource Health の Active / Updated / Resolved イベントを解釈したいとき
- Load Balancer、VM、NIC、NSG、Activity Log を軸に原因を切り分けたいとき
- AKS、App Service、Azure SQL、PostgreSQL、Cosmos DB、Entra ID の障害切り分けをしたいとき
- Azure プラットフォーム障害か、顧客側の構成 / OS / アプリ障害かを切り分けたいとき
- 調査結果を `Troubleshooting/` 向けレポートとして保存したいとき

## When NOT to Use

- 通常の製品 Q&A や比較検討だけを行うとき
- 変更作業や復旧操作を実行するとき
- 設計提案やベストプラクティス整理が主目的のとき

## Inputs

最低限、以下のうち 1 つ以上を受け取る。

- サブスクリプション ID
- リソース ID またはリソース名 + Resource Group
- 発生時刻
- 影響症状
- 監視アラート本文

不足している場合は、調査に必要なキー情報だけ追加確認する。

## Core Rules

- まず live 状態を read-only で確認し、推測より観測結果を優先する
- Azure CLI / Activity Log / Resource Health の事実と、そこからの解釈を分けて書く
- Activity Log は control-plane の履歴確認に有効だが、network runtime event の証明には過信しない
- 現在も障害中か、過去に発生して既に復旧したのかを最初に切り分ける
- Microsoft / Azure の意味づけは公式 Docs で裏付ける
- 障害調査レポートは `Troubleshooting/` を正本にし、`Answer/` と重複保存しない
- Load Balancer 系では Resource Health が復旧済みでも `VipAvailability` と `DipAvailability` を確認する
- `DipAvailability` の `BackendPort` と `BackendIPAddress` は別次元集計として扱い、直接の 1 台 1 ポート値として書かない
- VPN Gateway や BGP flap 疑いでは、Activity Log だけで `瞬断なし` と断定せず、RouteDiagnosticLog / TunnelDiagnosticLog / BGP 系メトリクスの有無も確認する
- 報告書では「報告書としては」のようなメタ表現を避け、判断文そのものへ落とす
- 破壊的操作、構成変更、再起動、フェールオーバーはこの skill の範囲外

## Workflow

1. Scope Fix: affected resource, time window, resource ID, and current user impact.
2. Live Fact Collection: auth/subscription, current resource state, Activity Log, Resource Health, and dependent resources.
3. Platform vs Workload Split: decide active Azure platform impact, recovered Azure event, or customer-side continuing issue.
4. Service Branch: use [references/service-branches.md](references/service-branches.md) for AKS, App Service, Database, Entra ID, Load Balancer, VPN/BGP.
5. Official Grounding: verify Resource Health, diagnostic limits, and service-specific claims with Microsoft Learn URLs.
6. Report Synthesis: primary conclusion, facts, current state, interpretation, next checks, and SR identifiers if needed.
7. Save: troubleshooting records go to `Troubleshooting/`; ordinary Q&A answers go to `Answer/`.

## Decision Points

- Auth blocked: report MFA/Conditional Access status and prefer normal browser login when device code is blocked.
- Resource Graph gaps: child resources may be missing; construct child IDs and query `az resource show --ids` directly.
- Recovered Resource Health: do not call it ongoing once `Resolved` and current `Available` are confirmed.
- Run Command RBAC: do not imply guest execution is possible without `Microsoft.Compute/virtualMachines/runCommand/action` or equivalent role evidence.
- Incomplete scope: resolve resource ID / subscription / resource group first; do not broaden blindly.
- No official doc: state that the official docs do not explicitly say it, and separate observation from hypothesis.

## Done Criteria

- [ ] 対象リソースと発生時刻が明確
- [ ] current state を live で確認済み
- [ ] Activity Log または同等の履歴を確認済み
- [ ] network runtime が論点なら、Activity Log だけで足りるか / resource logs や metrics が必要かを判定済み
- [ ] Azure 側継続影響か、復旧済みか、顧客側継続影響かを切り分け済み
- [ ] 公式 Docs の URL を最低 1 件以上付与
- [ ] 事実と解釈を分けて記述
- [ ] レポートを `Troubleshooting/` へ保存、または保存先判定理由を明示

## Output Shape

レポートは `回答`、`いただいた質問`、`事実確認結果`、`解釈`、`次に確認すべきこと` を基本にする。詳細テンプレートは [references/report-template.md](references/report-template.md) を使う。

## Example Prompts

- `/azure-troubleshooting subscription ID と resource ID を渡すので、Azure 側継続障害か切り分けて`
- `/azure-troubleshooting Resource Health の PlatformInitiated アラートが来た。current state と Activity Log を見て報告書を作って`
- `/azure-troubleshooting Load Balancer と配下 VM の障害調査をして、Troubleshooting に保存して`
- `/azure-troubleshooting AKS の API server は生きていそうだが Pod が不安定。Azure 側かワークロード側か切り分けて`
- `/azure-troubleshooting App Service が 5xx を返している。platform 障害か app 側か切り分けて`
- `/azure-troubleshooting Azure SQL / PostgreSQL の接続障害を調べて、platform とネットワークを切り分けて`
- `/azure-troubleshooting Entra ID のサインイン障害を tenant-wide か app-specific か切り分けて`

## References

- [references/service-branches.md](references/service-branches.md)
- [references/report-template.md](references/report-template.md)