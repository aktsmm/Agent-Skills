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

## Shared Network / DNS / Azure Firewall / ExpressRoute

### First Checks

- 発生時刻を UTC に正規化し、事象前後を含む固定 window で全リソースを比較する
- private IP は Resource Graph で NIC、VM、subnet、resource group へ逆引きし、複数 VNet / subnet にまたがるか確認する
- VM の current power state だけで過去の停止を否定せず、`VmAvailabilityMetric` を 1 分粒度で確認し、利用可能なら guest `Heartbeat` も照合する
- Azure Firewall は current provisioning state に加え、`FirewallHealth`、latency、throughput、SNAT utilization、diagnostic settings、対象 window の policy / network resource Activity Log を確認する
- Firewall structured logs は最初に `getschema` で列名を確認し、全体 deny 件数ではなく対象 IP / FQDN / port / rule と時系列へ絞る
- ExpressRoute は current peering state に加え、回線ごとの Primary / Secondary `BgpAvailability` と `ArpAvailability`、gateway route-change frequency、traffic continuity、QoS drop を確認する
- DNS 疑いでは、対象 query の response code / latency、内部 DNS への通信、外部 UDP/53 への fallback、DNS / identity host の可用性を同じ window で比較する

### Split

- `VmAvailabilityMetric=1` が全分継続し guest Heartbeat も残る: VM 停止より、監視経路、DNS、proxy、application dependency を優先する
- Resource Health の latest record が `Unknown -> Available`: `Unknown` は platform が health を判定できなかった状態であり、VM 停止の証拠にしない
- Firewall health が 100%、capacity / latency に異常がなく、対象 flow が `Allow`: Firewall 障害や rule deny より、次 hop、戻り経路、宛先 service を優先する
- ICMP echo request が Firewall で `Allow`: Firewall 通過までは言えるが、宛先応答や reply 到達の証明にはしない
- 全体 deny が増えていても対象 flow に deny がない: 背景 traffic と分離し、増加元、宛先、port、開始時刻が事象と一致するか確認する
- DNS host が通常の forwarder ではなく root DNS へ急増: forwarder / upstream resolution failure の fallback 仮説として扱い、単独で根本原因と断定しない
- Azure Firewall DNS query log に対象 query がない: DNS Proxy 未経由の可能性を確認し、内部 DNS への Network Rule log と DNS server log を優先する
- ExpressRoute の Primary / Secondary BGP・ARP が全分 100%、route change 0、traffic 継続、drop 0: Azure 側回線断の可能性を下げ、オンプレミス側の監視経路や appliance を確認する

### Gotchas

- Log Analytics query の schema error 後に以前の terminal output を結果として採用しない。`getschema` 後に `Invoke-RestMethod -ErrorAction Stop` で再実行し、成功した response だけを整形する
- 複数 metric の共通 time grain が合わない場合は、エラーに示された最小共通粒度へそろえ、短時間 flap を見逃す制約を報告する
- effective route / effective NSG / Network Watcher の action API は通常の read 権限だけでは `AuthorizationFailed` になりうる。未確認を正常判定に置き換えず、必要な RBAC と未検証範囲を明示する
- Activity Log が空でも dataplane 正常とは言えない。metrics、resource logs、flow evidence を別に確認する

### Report Notes

- `current Succeeded`、`発生 window の metric`、`対象 flow の Allow/Deny` を別の事実として書く
- 観測した相関は「有力候補」または「整合する」とし、DNS server / proxy / appliance 側ログがない段階で根本原因と断定しない

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

## VPN Gateway / BGP

### First Checks

- Connection resource の status が `Connected` かを確認する
- gateway の BGP peer status と learned routes を確認する
- Activity Log で control-plane の更新履歴を確認する
- diagnostic settings の有無を確認し、`RouteDiagnosticLog` / `TunnelDiagnosticLog` / `IKEDiagnosticLog` を後追い確認できる状態かを判定する
- `BgpPeerStatus`、`BgpRoutesLearned`、`BgpRoutesAdvertised`、必要なら tunnel packet drop 系メトリクスを確認する

### Split

- Activity Log に write/update があるだけ: control-plane 変更は言えるが、runtime flap の有無はまだ言えない
- `RouteDiagnosticLog` に `BgpDisconnectedEvent` / `BgpConnectedEvent` がある: BGP flap の有無と時刻をこちらで判断する
- `TunnelDiagnosticLog` に同時刻の disconnect/connect がある: tunnel 側不安定が BGP flap の主因候補
- diagnostic settings 未構成: `瞬断なし` ではなく `後追いで証明できる証跡がない` と書く
- `BgpPeerStatus` が正常でも time grain が粗い場合: 短い flap 見逃しの可能性を残す

### Report Notes

- `Activity Log では構成変更時刻を確認、runtime event は別証跡で確認` と役割を分けて書く
- `flap はなかった` と断定する条件と、`見えなかっただけ` の条件を分けて書く
- diagnostic settings 未構成なら、その制約を明示して結論の強さを下げる

## Shared Reporting Pattern

各分岐でも、レポートは以下の順で短くまとめる。

1. 一次結論
2. live で確認した current state
3. 影響が Azure 側継続か、復旧済みか、ワークロード側継続か
4. 次の確認対象
