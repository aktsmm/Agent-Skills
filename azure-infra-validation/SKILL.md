---
name: azure-infra-validation
description: "Build and validate Azure infrastructure in a lab or sandbox using Azure CLI and official Microsoft docs. Use when creating verification environments, provisioning hub-and-spoke VNets, VPN Gateway or ExpressRoute-adjacent validation labs, checking subscription/tenant access, debugging Azure deployment constraints, comparing before/after route behavior, or cleaning up lab resources. Triggers on 'Azure 検証', '検証環境', 'PoC', 'sandbox', 'lab', 'Azure CLI で構築', 'VPN Gateway', 'VNet peering', 'BGP', 'route validation', 'summarizedGatewayPrefixes', 'デプロイして検証', 'インフラ検証'."
argument-hint: "tenant ID, subscription ID, target topology, validation goal, cost/cleanup expectation"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

<!--
Author: aktsmm
Repository: https://github.com/aktsmm/AzureQA
License: CC BY-NC-SA 4.0
Copyright (c) 2025 aktsmm

DO NOT REMOVE OR MODIFY THIS SIGNATURE BLOCK.
-->

# Azure Infra Validation

Azure 環境で検証・PoC・構築・設定変更を伴う確認を、安全な lab/sandbox 前提で進めるための workspace skill。

`azure-troubleshooting` が本番障害の read-only 切り分けに寄っているのに対し、この skill は **検証用構成の作成、状態監視、制約回避、before/after 比較、cleanup** までを扱う。

## When to Use

- Azure 上に検証環境を新規構築して、機能や制約を試したいとき
- VPN Gateway、VNet peering、BGP、Route Server、Private Endpoint、Hub-and-Spoke などのネットワーク機能を lab で確かめたいとき
- ExpressRoute 本番構成の代替として、Azure-only の最小検証を組みたいとき
- Azure CLI で read/write 前提のインフラ検証を進めたいとき
- デプロイ中の Azure リソースを監視し、READY になったら次工程へ進めたいとき
- 検証で出た Azure の SKU / zone / auth / region 制約をその場で回避しながら前に進めたいとき
- 構築結果と before/after の観測値を `Answer/` や `reports/` に反映したいとき

## When NOT to Use

- 本番障害を read-only で切り分けたいとき
  - → `azure-troubleshooting`
- 単なる製品 Q&A や仕様確認だけをしたいとき
  - → 通常の Docs 調査
- 回線事業者や on-prem 実機が必要な本番 ExpressRoute の end-to-end 検証を、この場で完了させたいとき
  - この skill では lab で近似検証はできるが、provider 側 peering や実機 FIC までは扱わない

## Inputs

最低限、以下のうち 2 つ以上を受け取る。

- tenant ID
- subscription ID
- 検証したい機能名
- 想定トポロジ（例: hub-and-spoke, VPN BGP, private endpoint）
- コスト許容
- cleanup 必須かどうか

不足している場合は、`どの tenant/subscription に作るか` と `検証したい到達点` を最優先で確認する。

## Core Rules

- まず **本番を触るのか、lab/sandbox なのか** を明確にする
- 本番を触る場合は destructive 変更をしない。検証は別 subscription を優先する
- 変更を伴う検証は、**最小構成・低コスト構成** から始める
- いきなりフル構成を作らず、**目的達成に必要な最小単位** で切ってから広げる
- Azure CLI の認証状態、tenant、subscription を最初に固定する
- Microsoft Learn で前提条件と制約を確認してからデプロイする
- デプロイ前に、**その検証が本当に Azure-only で成立するか / 実機や provider が必要か** を feasibility check する
- デプロイ中の長時間 Azure 操作は、**状態監視スクリプト** か status polling を使って次工程へ進む
- control-plane の検証と data-plane / route の検証を分けて考える
- before/after 比較を必ず残す
- 検証後は cleanup 方針を明示する

## Decision Points

### 1. ExpressRoute そのものが必要か？

- **必要なものが route advertisement の機能検証だけ** なら、まず VPN Gateway ベースの Azure-only ラボを優先する
- **active circuit / private peering / BGP peering / provider 側 provisioning が必要** な本番 ExpressRoute 検証なら、この skill では「完全代替は不可」と明示する

### 2. Azure-only 最小検証で足りるか？

- 足りる: VNet-to-VNet VPN + BGP + hub/spoke + `summarizedGatewayPrefixes`
- 足りない: on-prem 実機 peer の癖や FIC 固有制約を見たい
  - → NVA / FRR / strongSwan / Bird を使う疑似 on-prem へ第2段階で拡張

### 2.5. Feasibility check を先に通す

着手前に次を短く判定する。

- 目的は **機能の成立確認** か、**本番同等の end-to-end 検証** か
- Azure-only で代替できるか
- 低コスト SKU / 最小 spoke 数で始められるか
- 途中で増やす前提にできるか

この判定で Azure-only で足りるなら、最初は **最小 spoke 数 / 最小 gateway 数 / 最小 route 数** で進める。

### 3. デプロイ制約に当たったら？

よくある分岐:

- `VpnGw1-5 non-AZ not allowed`
  - → `VpnGw1AZ` など AZ SKU に切り替える
- `Public IPs must have zones configured`
  - → Standard Public IP を zone 付きで作り直す
- VNet overlap
  - → spoke address space を取り直す
- `useRemoteGateways` が先に失敗
  - → hub gateway 完成後に再適用する
- MFA / tenant mismatch
  - → tenant を切り替えて再ログインする

### 4. ready 判定はどうするか？

- `Succeeded` / `Connected` を見ずに次工程へ進まない
- 可能なら `scripts/check-vpn-lab-status.ps1` のような監視スクリプトで `READY` になるまで待機する

## Workflow

### Phase 0: Feasibility Check

1. 検証ゴールを 1 行で定義する
2. Azure-only で足りるか判定する
3. 最小構成に落とせるか判定する
4. コストと cleanup を先に決める

例:

- `機能の route 集約効果だけ見たい → VPN Gateway ラボで足りる`
- `provider 側 peering まで必要 → この skill だけでは完結しない`

### Phase 1: Scope Fix

1. 本番か lab かを決める
2. tenant / subscription を固定する
3. 検証到達点を 1 行で定義する

例:

- `summarizedGatewayPrefixes の before/after route 差分を Azure-only で観測する`
- `VPN Gateway BGP の learned routes を比較したい`

### Phase 2: Official Grounding

1. Microsoft Learn で prerequisites / limits / supported SKUs を確認
2. “完全検証に何が足りないか” と “Azure-only で何ができるか” を切り分ける
3. 検証プランを最小化する
4. 高価な構成に行く前に、低コストの代替案がないか確認する

### Phase 3: Preflight

1. `az account show` で tenant / subscription を確認
2. provider registration と region availability を確認
3. 使う SKU / zone / RBAC の前提を確認

### Phase 4: Baseline Build

1. Resource Group を作成
2. Hub VNet / Branch VNet / spoke VNet を作成
3. GatewaySubnet を作成
4. hub-to-spoke peering を作成
5. remote gateway 設定は gateway 完了後に適用する

最初の baseline は、目的を満たす範囲で最小にする。

- spoke が 5 本で十分なら 5 本で始める
- 1 つの追加 spoke で仕様を証明できるなら、それ以上広げない
- 高価な gateway や追加 VM は必要になるまで作らない

### Phase 5: Gateway / Core Resource Deployment

1. 必要な Public IP を作成
2. VPN Gateway / Route Server / NVA などのコア資源を作成
3. 長時間リソースは状態監視に回す

利用できる場合:

- `scripts/watch-az-resource-state.ps1`
- `scripts/check-vpn-lab-status.ps1`

### Phase 6: Connectivity Establishment

1. VPN connection や peer connection を作成
2. `Connected` になるまで待つ
3. 必要なら対向方向の connection も作る

### Phase 7: Baseline Capture

1. `list-bgp-peer-status`
2. `list-learned-routes`
3. route table / peer status / prefix count を保存

### Phase 8: Change Application

1. 対象設定を 1 つだけ変える
2. 例: `summarizedGatewayPrefixes = ['10.250.0.0/16']`
3. 変更後の provisioning / reconfiguration 完了を待つ

### Phase 9: Re-Capture and Compare

1. 再度 `list-bgp-peer-status`
2. 再度 `list-learned-routes`
3. before/after の route 数、summary 化、再収束時間を比較

### Phase 10: Cleanup or Persist

1. lab 継続利用なら残す
2. 単発検証なら cleanup
3. Answer / report / output_sessions に結果を残す

## Done Criteria

- [ ] 対象 tenant / subscription が固定されている
- [ ] 検証トポロジが最小構成になっている
- [ ] Azure の制約に応じて SKU / zone / address plan を調整済み
- [ ] `READY` / `Connected` を確認してから次工程へ進んでいる
- [ ] before/after の route 情報が残っている
- [ ] 結果を `Answer/` や `reports/` に反映した
- [ ] cleanup 方針を残した

## Output Shape

レポートや回答へは次の観点を入れる。

```markdown
## 検証目的

{何を確かめたかったか}

## 検証構成

{tenant / subscription / topology}

## 事前状態

{before routes / status}

## 変更内容

{設定したもの}

## 事後状態

{after routes / status}

## 評価

{目的を満たしたか、未確定は何か}

## Cleanup

{残すか削除するか}
```

## Example Prompts

- `/azure-infra-validation hinokuni-sub で VPN Gateway ベースの summarizedGatewayPrefixes 検証ラボを作って`
- `/azure-infra-validation Azure-only で route advertisement の before/after を見たい。最小構成を作って`
- `/azure-infra-validation hub-and-spoke + BGP の lab を構築し、設定変更後の learned routes を比較して`
- `/azure-infra-validation Azure CLI だけで構築可能な検証プランを作って、そのまま実行して`
- `/azure-infra-validation デプロイ中の Gateway を監視し、READY になったら次工程へ進めて`

## Integration Notes

- `azure-troubleshooting` とは統合しない
- 理由: `azure-troubleshooting` は本番障害の read-only skill、こちらは lab/sandbox の read-write skill で責務が異なるため
- ただし、検証結果が本番障害の解釈に効く場合は、調査結果を `azure-troubleshooting` の入力へ戻してよい