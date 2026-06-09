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

### Phase 1: Scope Fix

1. 影響リソース、発生時刻、影響継続中かどうかを整理する
2. 可能なら resource ID を取得する
3. 顧客影響の粒度を整理する

出力:

- 対象サブスクリプション
- 対象リソース
- 発生時刻
- 現在の影響有無

### Phase 2: Live Fact Collection

1. Azure CLI の認証状態を確認する
2. 対象サブスクリプションへ切り替える
3. 対象リソースの現在状態を取得する
4. Activity Log を取得し、Active / Updated / Resolved の履歴を確認する
5. 依存リソースの現在状態を確認する
6. network runtime が論点なら、diagnostic settings の有無と resource logs / metrics の観測可能性を確認する

優先して見るもの:

- `az account show`
- `az account set --subscription ...`
- `az resource show`
- `az monitor activity-log list --resource-id ...`
- `az vm get-instance-view`
- `Microsoft.ResourceHealth/availabilityStatuses/current`

### Phase 3: Platform vs Workload Split

以下で分岐する。

- Resource Health が `Active` / `Degraded` / `Unavailable` のまま: Azure 側継続影響の可能性を優先
- Activity Log に `Resolved` があり current health が `Available`: 一時的な Azure 側イベントは復旧済みと判断
- Resource Health は正常だがサービス影響が継続: アプリ、OS、probe、NIC、NSG、依存先を優先調査
- VM が停止 / Provisioning failed: VM 側を優先

### Phase 3.5: Service Branch

対象サービスごとの追加チェックは [service-branches.md](./references/service-branches.md) を使う。

- AKS: control plane と workload のどちらが壊れているかを切り分ける
- App Service: platform / plan 正常性と app 側障害を切り分ける
- Database: platform、接続経路、負荷飽和のどこが主因かを切り分ける
- Entra ID: tenant-wide か app-specific か user-specific かを切り分ける
- Load Balancer: dataplane と backend 個別異常を切り分ける
- VPN Gateway / BGP: control-plane 更新と runtime flap を切り分ける

### Phase 4: Official Grounding

1. Microsoft Learn で対象サービスの Resource Health / diagnostics / troubleshooting ページを検索する
2. 使う主張は URL 付きで裏付ける
3. Docs に明記がないものは「明記なし」と書く

重点観点:

- Resource Health の状態意味
- PlatformInitiated / UserInitiated の意味
- Activity Log の Resource Health schema
- 対象サービス固有の診断メトリック
- Activity Log で見える範囲と、resource logs / metrics が必要な範囲

### Phase 5: Report Synthesis

最低限、以下をレポートへ入れる。

1. 一次結論
2. 事実確認結果
3. 現在状態
4. 解釈
5. 次に確認すべきこと
6. 必要なら SR 用識別子

時系列は JST と UTC の対応が必要なら両方書く。

### Phase 6: Save

- 障害調査、切り分け、初動確認、復旧経過整理は `Troubleshooting/` に保存する
- 通常回答が主目的なら `Answer/` に保存する
- 保存先が曖昧な場合は「主目的が回答か、調査記録か」で判定する

## Decision Points

### MFA or Auth Blocked

- MFA 再認証が必要なら、その事実を報告する
- 共有ターミナルが対話プロンプトで詰まったら、独立 task や別プロセスで read-only 調査を続ける
- `az login --use-device-code` が Conditional Access でブロックされる場合は、通常のブラウザー対話ログイン（`az login -t <tenantId>`）を優先する

### Resource Graph Gaps

- Resource Graph は child resource を返さないことがある。親リソースは見えるのに child が 0 件なら、親の resource ID から child ID を組み立てて `az resource show --ids ... --api-version <version>` で直接確認する
- AVS の cluster SKU 確認では、`az vm list` ではなく `Microsoft.AVS/privateClouds/<name>/clusters/<cluster>` の `sku.name` と `properties.clusterSize` を見る

### Resource Health Already Recovered

- `Resolved` と current health `Available` が確認できたら、継続障害と断定しない
- その上で、まだ影響が残るならアプリ / probe / backend 側へ切り替える

### Run Command RBAC Check

- Run Command の実行には `Microsoft.Compute/virtualMachines/runCommand/action` が必要
- `az role assignment list --assignee ...` が Graph 権限不足で失敗したら、対象 scope の role assignment 一覧を取得して `principalName` を後段で絞る
- 権限確認が不完全なまま guest 実行を既成事実化しない

### Service-Specific Follow-up

- AKS は node pool、CNI、ingress、pod を追加確認する
- App Service は deployment slot、config change、dependency を追加確認する
- Database は firewall、private endpoint、DNS、接続数、throttling を追加確認する
- Entra ID は sign-in logs、Conditional Access、secret / certificate expiry を追加確認する
- Load Balancer は `VipAvailability`、`DipAvailability`、backend 個別異常、構成変更有無を追加確認する
- VPN Gateway / BGP は RouteDiagnosticLog、TunnelDiagnosticLog、BGP Peer Status、BGP Routes Learned の有無を追加確認し、diagnostic settings 未構成ならその制約を明記する

### Incomplete Scope

- リソース ID がない場合は、subscription / resource group / resource name の組み合わせで補完する
- それでも対象が曖昧なら、対象確定を優先し、無理に広く調べない

### No Official Doc for a Claim

- 「公式ドキュメントには明記されていません」と書く
- 観測事実と仮説を混ぜない

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

レポートは次の骨子を推奨する。

```markdown
# {タイトル}

## 回答

{一次結論}

## いただいた質問

{原文}

## 事実確認結果

{観測結果}

## 解釈

{公式 Docs 付きの意味づけ}

## 次に確認すべきこと

{次アクション}
```

## Example Prompts

- `/azure-troubleshooting subscription ID と resource ID を渡すので、Azure 側継続障害か切り分けて`
- `/azure-troubleshooting Resource Health の PlatformInitiated アラートが来た。current state と Activity Log を見て報告書を作って`
- `/azure-troubleshooting Load Balancer と配下 VM の障害調査をして、Troubleshooting に保存して`
- `/azure-troubleshooting AKS の API server は生きていそうだが Pod が不安定。Azure 側かワークロード側か切り分けて`
- `/azure-troubleshooting App Service が 5xx を返している。platform 障害か app 側か切り分けて`
- `/azure-troubleshooting Azure SQL / PostgreSQL の接続障害を調べて、platform とネットワークを切り分けて`
- `/azure-troubleshooting Entra ID のサインイン障害を tenant-wide か app-specific か切り分けて`