---
author: aktsmm
repository: https://github.com/aktsmm/AzureQA
license: CC BY-NC 4.0
copyright: Copyright (c) 2025 aktsmm
---

# Azure Troubleshooting Service Branches

Azure インシデント調査で、共通の live fact collection の後に分岐するサービス別チェックリスト。

## Load Balancer / VM

### First Checks

- `Microsoft.ResourceHealth/availabilityStatuses/current` で current health を確認する
- Activity Log で `Active` / `Updated` / `Resolved` の履歴を確認する
- `az vm get-instance-view` で関連 VM の power / provisioning を確認する
- `VipAvailability` を確認する
- `DipAvailability` を `BackendPort` と `BackendIPAddress` で**別々に**確認する
- 直近 24 時間の Azure Administrative Activity で LB / VM / NIC / NSG への構成変更有無を確認する

### Split

- Resource Health が復旧済みでも VIP が低下: LB 全体の dataplane 影響を優先
- VIP は 100% だが DIP が低下: backend 個別異常を優先
- `DipAvailability` は別次元集計なので、`BackendPort` と `BackendIPAddress` を組み合わせて推定する
- `HealthProbeStatus` が列挙されない環境では `DipAvailability` を主指標にする
- BackendPort 側と特定 Backend IP 側の両方に低下が残り、他の Backend IP が 100% に戻っている場合は、その VM の待受サービス、OS Firewall、アプリ応答を優先する

### Report Notes

- `10.186.80.198:59502` のような直接値として書かず、「別次元の集計値」と明記する
- 会話メタではなく、「本事象は〜と評価する」のような判断文へ落とす

## AKS

### First Checks

- `az aks show` で cluster の provisioningState、powerState、kubernetesVersion を確認する
- `az aks nodepool list` で node pool の状態を確認する
- Activity Log で upgrade、rotate、scale、maintenance の履歴を確認する
- Resource Health や Service Health に AKS / Compute / Network の継続影響がないか確認する

### Split

- control plane が正常で workload だけ異常: ingress、CNI、node、pod 側を優先
- node pool が不健康: VMSS、node image、quota、network を優先
- API server 到達不可: Azure 側継続影響または認証 / private cluster 経路を優先

## App Service

### First Checks

- `az webapp show` で state、hostNames、serverFarmId を確認する
- deployment slot、recent deployment、app settings の変更履歴を確認する
- Health Check、HTTP 5xx、restart、scale、certificate 更新の有無を確認する
- Activity Log で restart、config change、plan scale の履歴を確認する

### Split

- App Service plan と platform が正常でアプリだけ異常: code、config、dependency、identity を優先
- slot swap 直後から異常: slot 設定差分を優先
- 全 instance で 5xx が増加: upstream dependency または platform event を確認

## Database

### Azure SQL / SQL MI

- `az sql server show`、`az sql db show` または SQL MI の状態を確認する
- failover、maintenance、firewall、private endpoint、connection policy を確認する
- CPU、storage、workers、sessions などの飽和を確認する

### PostgreSQL / MySQL Flexible Server

- server state、HA 状態、storage 使用率、メンテナンス履歴を確認する
- firewall、private DNS、SSL/TLS、connection count を確認する

### Cosmos DB

- regional failover、write region、replication、throughput、429/throttling を確認する
- hot partition や特定 container 偏りを確認する

### Split

- platform state が正常で接続障害のみ継続: firewall、private endpoint、DNS、credential rotation を優先
- 稼働中だが遅い: RU、connection saturation、query regression、hot spot を優先

## Entra ID

### First Checks

- 影響範囲が tenant 全体か、特定 app / user / CA policy かを切り分ける
- sign-in logs、audit logs、Conditional Access 変更、federation / provisioning 変更を確認する
- Entra / M365 側の Service Health を確認する
- app registration、service principal、secret / certificate expiry を確認する

### Split

- tenant-wide sign-in failure: Service Health、federation、MFA、identity provider 側を優先
- 特定アプリのみ失敗: app registration、redirect URI、secret / cert、有効な audience を優先
- 特定ユーザー / グループのみ失敗: Conditional Access、group membership、device compliance を優先

## Shared Reporting Pattern

各分岐でも、レポートは以下の順で短くまとめる。

1. 一次結論
2. live で確認した current state
3. 影響が Azure 側継続か、復旧済みか、ワークロード側継続か
4. 次の確認対象
