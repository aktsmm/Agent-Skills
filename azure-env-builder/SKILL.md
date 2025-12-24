---
name: azure-env-builder
description: "Azure 環境構築スキル。dev/staging/prod 等の環境を Azure CLI または Bicep でデプロイ。ResourceGroup/Subscription スコープ対応。監視、ネットワーク、コンピュート、コンテナ、データベース等のエンタープライズ構成をサポート。必ず Bicep MCP と Microsoft Learn Docs MCP を使用して最新のスキーマとサンプルを取得すること。"
---

# Azure Environment Builder

## ワークフロー概要

環境構築は以下のステップで進める：

1. ヒアリング (基本情報 + リソース要件)
2. MCP ツールで最新情報を取得
3. 環境フォルダ生成 (`scripts/scaffold_environment.ps1`)
4. Bicep/CLI 実装
5. 検証 (`what-if`) → デプロイ
6. 結果を README.md に記録

## 必須: MCP ツールの使用

**Bicep コード生成前に必ず実行すること。**

```
# 1. ベストプラクティス取得
mcp_bicep_experim_get_bicep_best_practices

# 2. リソーススキーマ確認
mcp_bicep_experim_list_az_resource_types_for_provider(providerNamespace: "Microsoft.Network")
mcp_bicep_experim_get_az_resource_type_schema(azResourceType: "Microsoft.Storage/storageAccounts", apiVersion: "2023-05-01")

# 3. AVM (Azure Verified Modules) 確認
mcp_bicep_experim_list_avm_metadata

# 4. 公式ドキュメント/サンプル検索
microsoft_docs_search(query: "Private Endpoint Bicep")
microsoft_code_sample_search(query: "Storage Account Private Endpoint", language: "bicep")
```

## Step 1: ヒアリング

### 基本情報 (必須)

| 項目               | 確認内容                                  |
| ------------------ | ----------------------------------------- |
| サブスクリプション | ID またはログイン状態 (`az account show`) |
| 環境名             | dev / staging / prod など                 |
| リージョン         | japaneast / japanwest など                |
| デプロイ方式       | Azure CLI / Bicep                         |
| スコープ           | ResourceGroup / Subscription              |

### リソース要件

ユーザーの要件に応じて以下をヒアリング：

**ネットワーク**

- 接続パターン: パブリック / 閉域 (Private Endpoint) / ハイブリッド (VPN/ER)
- 既存 VNet 接続: Hub-Spoke / Peering

**コンピュート**

- VM / VMSS / App Service / Functions / Container Apps / AKS

**データ**

- SQL Database / PostgreSQL / Cosmos DB / Redis / Storage

**監視**

- Log Analytics / App Insights / Grafana / Sentinel

**セキュリティ**

- Azure Firewall / Bastion / DDoS Protection

→ 詳細なヒアリング項目: [references/hearing-checklist.md](references/hearing-checklist.md)

## Step 2: 環境フォルダ生成

```powershell
pwsh scripts/scaffold_environment.ps1 -Environment <env> -Location <region> -DeploymentMode Bicep -DeploymentScope <scope>
```

生成物:

- `env/<env>/bicep/main.bicep`
- `env/<env>/bicep/parameters/<env>.json`
- `env/<env>/README.md`

## Step 3: Bicep 実装

### MCP でスキーマ取得 → Bicep 生成

```
# 例: Storage Account のスキーマ取得
mcp_bicep_experim_get_az_resource_type_schema(
  azResourceType: "Microsoft.Storage/storageAccounts",
  apiVersion: "2023-05-01"
)

# 例: 公式サンプル検索
microsoft_code_sample_search(query: "Storage Account Bicep Private Endpoint", language: "bicep")
```

### Subscription スコープの場合

```bicep
targetScope = 'subscription'

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${environment}-${location}'
  location: location
}

module resources './modules/resources.bicep' = {
  scope: rg
  name: 'resourcesDeployment'
  params: { ... }
}
```

## Step 4: 検証 & デプロイ

```powershell
# 検証 (what-if)
az deployment group what-if --resource-group <rg> --template-file main.bicep --parameters @parameters/<env>.json

# デプロイ
az deployment group create --resource-group <rg> --template-file main.bicep --parameters @parameters/<env>.json
```

## Step 5: 結果出力

デプロイ完了後、以下を必ず出力：

```markdown
## 🎉 デプロイ完了

| リソース   | 名前      | 状態     |
| ---------- | --------- | -------- |
| ✅ Storage | stprodxxx | 作成済み |

### Azure Portal リンク

- [リソースグループ](https://portal.azure.com/#@/resource/subscriptions/{subId}/resourceGroups/{rg}/overview)
- [Storage](https://portal.azure.com/#@/resource{resourceId})
```

## 参照ファイル

| ファイル                                                                 | 用途                   |
| ------------------------------------------------------------------------ | ---------------------- |
| [references/hearing-checklist.md](references/hearing-checklist.md)       | 詳細ヒアリング項目     |
| [references/environment-template.md](references/environment-template.md) | 環境定義テンプレート   |
| [references/resource-patterns.md](references/resource-patterns.md)       | リソース別構成パターン |
| [references/review-checklist.md](references/review-checklist.md)         | レビュー確認事項       |
| scripts/scaffold_environment.ps1                                         | 環境フォルダ生成       |
| scripts/validate_bicep.ps1                                               | Bicep 検証             |
