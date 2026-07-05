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
- Bicep / AVM で再利用前提の構成を設計・デプロイしたいとき
  - → `azure-env-builder`

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
- 構成変更や設定変更の検証では、**変更前に観測スクリプトを準備**し、control-plane の変更時刻と dataplane / route の影響時刻を別々に取る
- control-plane の検証と data-plane / route の検証を分けて考える
- before/after 比較を必ず残す
- `あとで Activity Log を見ればよい` と考えず、変更直後の polling で再収束時間や瞬断有無を採る
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

デプロイ制約・READY 判定・詳細 phase 手順は [references/validation-runbook.md](references/validation-runbook.md) を参照する。

## Workflow

1. Feasibility: 検証ゴール、Azure-only 可否、最小構成、cost/cleanup を決める
2. Scope: tenant / subscription / lab or production boundary / 到達点を固定する
3. Official grounding: Microsoft Learn で prerequisites / limits / supported SKUs を確認する
4. Preflight: `az account show`、provider registration、region availability、RBAC、観測方法を確認する
5. Build: 最小 Resource Group / VNet / GatewaySubnet / peering / core resources を作る
6. Observe: `READY` / `Connected` まで待ち、baseline routes / peer status / metrics を保存する
7. Change: 対象設定を 1 つだけ変え、要求時刻・Succeeded 時刻・correlation ID を残す
8. Compare: before/after、再収束時間、瞬断有無を polling 証跡で評価する
9. Cleanup or persist: lab を残すか削除し、結果を report / Answer へ反映する

Detailed steps: [references/validation-runbook.md](references/validation-runbook.md)

## Done Criteria

- [ ] 対象 tenant / subscription が固定されている
- [ ] 検証トポロジが最小構成になっている
- [ ] Azure の制約に応じて SKU / zone / address plan を調整済み
- [ ] `READY` / `Connected` を確認してから次工程へ進んでいる
- [ ] before/after の route 情報が残っている
- [ ] 変更要求時刻、Succeeded 時刻、影響観測時刻のいずれかが残っている
- [ ] 再収束時間または瞬断有無を、Activity Log だけでなく polling 証跡で説明できる
- [ ] 結果を `Answer/` や `reports/` に反映した
- [ ] cleanup 方針を残した

## Output Shape

レポートには `検証目的`、`検証構成`、`事前状態`、`変更内容`、`変更時刻`、`事後状態`、`評価`、`Cleanup` を含める。テンプレートは [references/output-template.md](references/output-template.md) を使う。

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

## References

- [references/validation-runbook.md](references/validation-runbook.md)
- [references/output-template.md](references/output-template.md)