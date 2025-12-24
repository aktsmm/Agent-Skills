---
name: azure-env-builder
description: Guide for scaffolding Azure environment deployments with per-environment artifacts using either Azure CLI or Bicep workflows. Supports both Resource Group and Subscription scope deployments. Prioritizes Bicep MCP tools and Microsoft Learn Docs MCP for accurate, up-to-date guidance.
---

# Azure Environment Builder

## 優先的に使用するツール

このスキルでは以下の MCP ツールを積極的に活用してください。

### Bicep MCP ツール (必須)

| ツール                                                  | 用途                                |
| ------------------------------------------------------- | ----------------------------------- |
| `mcp_bicep_experim_get_bicep_best_practices`            | Bicep ベストプラクティスの取得      |
| `mcp_bicep_experim_list_az_resource_types_for_provider` | プロバイダーのリソースタイプ一覧    |
| `mcp_bicep_experim_get_az_resource_type_schema`         | リソースのスキーマ取得              |
| `mcp_bicep_experim_list_avm_metadata`                   | Azure Verified Modules (AVM) の一覧 |

### Microsoft Learn Docs MCP ツール (必須)

| ツール                         | 用途                               |
| ------------------------------ | ---------------------------------- |
| `microsoft_docs_search`        | Azure/Bicep 関連ドキュメントの検索 |
| `microsoft_docs_fetch`         | 特定ページの完全なコンテンツ取得   |
| `microsoft_code_sample_search` | 公式コードサンプルの検索           |

## このスキルを使うタイミング

- Azure の新しい環境 (dev / test / staging / prod など) を構築するタスクを依頼されたとき。
- Azure CLI と Bicep のどちらでデプロイするかをユーザーとすり合わせたいとき。
- 環境ごとに成果物 (スクリプト / パラメータ / ドキュメント) を整理して残しておきたいとき。
- **サブスクリプションレベル**でリソースグループ作成から一括管理したいとき。
- 複数のリソースグループを一つの Bicep/CLI で管理したいとき。

## 事前に確認すること

### 基本情報

1. 対象となる Azure サブスクリプション ID と利用する Azure AD テナント。
2. 環境名 (例: `dev`, `staging`, `prod-eastasia`)。
3. デプロイ方法の希望 (Azure CLI or Bicep)。未指定なら対話して決定する。
4. **デプロイスコープ** (ResourceGroup or Subscription)。未指定なら対話して決定する。
   - `ResourceGroup`: 既存のリソースグループにリソースをデプロイ。
   - `Subscription`: サブスクリプションレベルでリソースグループ作成から一括管理。
5. リソースグループやリージョンの標準命名ルール。
6. 認証済みかどうか (`az login` / `Connect-AzAccount`)。

### ネットワーク要件 (重要)

以下のネットワーク構成パターンを必ずヒアリングしてください。

#### 接続パターン

| パターン           | 説明                              | 主なユースケース            |
| ------------------ | --------------------------------- | --------------------------- |
| **パブリック**     | インターネット経由でアクセス      | 開発/テスト環境、コスト重視 |
| **閉域 (Private)** | VNet 内のみ、インターネット非公開 | 本番環境、金融/医療系       |
| **ハイブリッド**   | オンプレ接続 (VPN/ExpressRoute)   | エンタープライズ環境        |

#### 確認すべきネットワーク項目

1. **閉域要件**

   - パブリックエンドポイントの許可/禁止
   - Private Endpoint の必要性
   - パブリック IP の使用可否

2. **既存ネットワーク構成**

   - Hub-Spoke トポロジーの有無
   - 既存 VNet への接続要件
   - VNet Peering / VPN Gateway の有無

3. **外部接続要件**

   - オンプレミス接続 (ExpressRoute / S2S VPN)
   - 他の Azure リージョン / サブスクリプションとの接続
   - サードパーティ SaaS との連携

4. **セキュリティ要件**

   - NSG / Azure Firewall ルール
   - Azure Policy による制約 (例: Public IP 禁止)
   - DDoS Protection の要否

5. **DNS 要件**
   - Private DNS Zone の使用
   - カスタム DNS サーバー
   - Azure DNS Private Resolver

#### ネットワーク構成ヒアリング用質問

```markdown
## ネットワーク要件確認

1. この環境はインターネットからアクセス可能にしますか？

   - [ ] はい（パブリックエンドポイント許可）
   - [ ] いいえ（閉域構成必須）

2. Private Endpoint は必要ですか？

   - [ ] Storage Account
   - [ ] Azure SQL / Cosmos DB
   - [ ] Key Vault
   - [ ] Container Registry
   - [ ] その他: \_\_\_

3. 既存のネットワークに接続しますか？

   - [ ] 既存 VNet への接続（VNet 名: \_\_\_）
   - [ ] Hub-Spoke 構成の Spoke として接続
   - [ ] オンプレミス接続あり

4. Azure Policy によるネットワーク制約はありますか？
   - [ ] Public IP 作成禁止
   - [ ] パブリックエンドポイント禁止
   - [ ] 特定リージョンのみ許可
```

### リソース固有のネットワーク考慮事項

| リソース         | パブリック構成             | 閉域構成                                 |
| ---------------- | -------------------------- | ---------------------------------------- |
| **VM**           | Public IP + NSG            | Private IP のみ + Bastion / VPN          |
| **Storage**      | パブリックアクセス許可     | Private Endpoint + ファイアウォール      |
| **Databricks**   | 標準 VNet インジェクション | No Public IP (NPIP) + NAT Gateway        |
| **SQL Database** | パブリックエンドポイント   | Private Endpoint + VNet Service Endpoint |
| **AKS**          | Public API Server          | Private Cluster                          |
| **Key Vault**    | パブリックアクセス         | Private Endpoint + ファイアウォール      |

## ワークフロー概要

1. 入力情報をヒアリングし、`references/environment-template.md` をベースに環境要件を記録。
2. `scripts/scaffold_environment.ps1` で環境フォルダとテンプレート資材を生成。
3. デプロイ方式を選択し、以下のいずれかの手順に従う。
   - **Azure CLI 方式**: `env/<environment>/cli/deploy.ps1` を編集し、`az deployment sub/group create` コマンドを定義。
   - **Bicep 方式**: `env/<environment>/bicep/main.bicep` と `env/<environment>/bicep/parameters/<environment>.json` を編集。
4. Microsoft Learn MCP ツール (`microsoft_docs_search`, `microsoft_docs_fetch`) を使って最新ベストプラクティスを確認。
5. `scripts/validate_bicep.ps1` または `scripts/preview_cli.ps1` でデプロイ検証 (what-if / dry-run)。
6. 実行ログと変更点を `env/<environment>/README.md` に記録。
7. リポジトリにコミットし、Pull Request でレビューを依頼。

## 詳細手順

### Step 1: インプットの整理

- ユーザーに質問して不足情報を補う。
- `references/environment-template.md` をコピーし、`env/<environment>/README.md` に貼り付けて編集。

### Step 2: 環境フォルダの生成

```powershell
# 例: staging 環境の初期化 (リソースグループスコープ)
pwsh scripts/scaffold_environment.ps1 -Environment staging -Location "japaneast" -DeploymentMode "Bicep" -DeploymentScope "ResourceGroup"

# 例: prod 環境の初期化 (サブスクリプションスコープ)
pwsh scripts/scaffold_environment.ps1 -Environment prod -Location "japaneast" -DeploymentMode "Bicep" -DeploymentScope "Subscription"
```

- 生成物:
  - `env/<env>/cli/deploy.ps1`
  - `env/<env>/bicep/main.bicep` (スコープに応じた `targetScope` 設定済み)
  - `env/<env>/bicep/parameters/<env>.json`
  - `env/<env>/README.md`
- **Subscription スコープ**の場合:
  - `main.bicep` に `targetScope = 'subscription'` が設定される
  - リソースグループ作成用モジュールが含まれる
  - `az deployment sub create` でデプロイ
- フォルダ構造は環境ごとに独立。複数環境を並行管理する際も資材が衝突しない。

### Step 3: デプロイ方式の合意

- ユーザーが指定しない場合は以下を基準に提案:
  - **Azure CLI**: 小規模 / ワンショット / スクリプト中心。
  - **Bicep**: IaC を標準化 / 継続的に管理したい場合。

### Step 3.5: ネットワーク構成の決定 (重要)

ネットワーク要件に応じて、以下の構成パターンから選択:

#### パターン A: パブリック構成 (開発/テスト向け)

```bicep
// Public IP + NSG でシンプルに構成
resource pip 'Microsoft.Network/publicIPAddresses@2023-11-01' = {
  name: 'pip-${environmentName}'
  location: location
  sku: { name: 'Basic' }
  properties: { publicIPAllocationMethod: 'Dynamic' }
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  // パブリックアクセス許可
  properties: {
    publicNetworkAccess: 'Enabled'
    allowBlobPublicAccess: false  // Blob は非公開推奨
  }
}
```

#### パターン B: 閉域構成 (本番向け)

```bicep
// Private Endpoint + ファイアウォールで閉域化
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  properties: {
    publicNetworkAccess: 'Disabled'  // パブリックアクセス禁止
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
  }
}

resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = {
  name: 'pe-${storageAccountName}'
  location: location
  properties: {
    subnet: { id: subnet.id }
    privateLinkServiceConnections: [{
      name: 'storage-connection'
      properties: {
        privateLinkServiceId: storageAccount.id
        groupIds: ['blob']
      }
    }]
  }
}

// Private DNS Zone 連携
resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'privatelink.blob.core.windows.net'
  location: 'global'
}
```

#### パターン C: Databricks 閉域構成 (No Public IP)

```bicep
resource databricksWorkspace 'Microsoft.Databricks/workspaces@2024-05-01' = {
  properties: {
    parameters: {
      enableNoPublicIp: { value: true }  // NPIP 有効化
      customVirtualNetworkId: { value: vnet.id }
      customPublicSubnetName: { value: 'snet-databricks-public' }
      customPrivateSubnetName: { value: 'snet-databricks-private' }
    }
    publicNetworkAccess: 'Disabled'
    requiredNsgRules: 'NoAzureDatabricksRules'  // NSG ルール最小化
  }
}

// NAT Gateway (NPIP 構成に必須)
resource natGateway 'Microsoft.Network/natGateways@2023-11-01' = {
  name: 'nat-${environmentName}'
  location: location
  sku: { name: 'Standard' }
  properties: {
    publicIpAddresses: [{ id: natPip.id }]
  }
}
```

#### パターン D: Hub-Spoke 接続

```bicep
// Spoke VNet を Hub に Peering
resource peeringToHub 'Microsoft.Network/virtualNetworks/virtualNetworkPeerings@2023-11-01' = {
  parent: spokeVnet
  name: 'peer-to-hub'
  properties: {
    remoteVirtualNetwork: { id: hubVnetId }
    allowVirtualNetworkAccess: true
    allowForwardedTraffic: true
    useRemoteGateways: true  // Hub の Gateway を使用
  }
}
```

### Step 4: Bicep MCP でベストプラクティスを確認 (重要)

Bicep ファイルを作成・編集する前に、必ず以下を実行:

```
# 1. Bicep ベストプラクティスを取得
mcp_bicep_experim_get_bicep_best_practices

# 2. 必要なリソースタイプのスキーマを確認
mcp_bicep_experim_list_az_resource_types_for_provider(providerNamespace: "Microsoft.Storage")
mcp_bicep_experim_get_az_resource_type_schema(azResourceType: "Microsoft.Storage/storageAccounts", apiVersion: "2023-05-01")

# 3. Azure Verified Modules (AVM) の活用を検討
mcp_bicep_experim_list_avm_metadata

# 4. ネットワーク関連の最新ドキュメント確認
microsoft_docs_search(query: "Azure Private Endpoint Bicep")
microsoft_code_sample_search(query: "Private Endpoint storage account", language: "bicep")
```

これにより、最新の API バージョンと正しいプロパティを使用できます。

### Step 5A: Azure CLI 方式

1. `env/<environment>/cli/deploy.ps1` を編集し、必要な `az` コマンドを記述。
2. 変数・タグ・パラメータは `env/<environment>/cli/config/` 配下に JSON で保存。
3. `pwsh env/<environment>/cli/deploy.ps1 -WhatIf` で dry-run。
4. 本番実行時は `-Confirm:$false` を活用し、自動化を優先。

### Step 5B: Bicep 方式

1. `env/<environment>/bicep/main.bicep` を編集し、標準リソースを定義。
2. パラメータは `env/<environment>/bicep/parameters/<environment>.json` にまとめる。
3. 構文チェック:

   ```powershell
   # リソースグループスコープ
   pwsh scripts/validate_bicep.ps1 -Environment <environment> -DeploymentScope ResourceGroup

   # サブスクリプションスコープ
   pwsh scripts/validate_bicep.ps1 -Environment <environment> -DeploymentScope Subscription
   ```

4. デプロイプレビュー:
   - **ResourceGroup スコープ**: `az deployment group what-if`
   - **Subscription スコープ**: `az deployment sub what-if`

#### サブスクリプションスコープでの注意点

- `targetScope = 'subscription'` を `main.bicep` の先頭に記述。
- リソースグループは `resource rg 'Microsoft.Resources/resourceGroups@2024-03-01'` で作成。
- リソースグループ内のリソースは `module` を使って別ファイルから参照。

```bicep
// サブスクリプションスコープの例
targetScope = 'subscription'

param location string
param environment string

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${environment}-${location}'
  location: location
}

module resources './modules/resources.bicep' = {
  scope: rg
  name: 'resourcesDeployment'
  params: {
    location: location
    environment: environment
  }
}
```

### Step 8: ベストプラクティス参照 (必須)

Microsoft Learn MCP サーバーを活用して最新仕様を確認。

```
# Azure Bicep のデプロイスコープについて
microsoft_docs_search(query: "Bicep deploy subscription scope resource group")

# 特定リソースのコードサンプル
microsoft_code_sample_search(query: "Bicep Storage Account", language: "bicep")

# 詳細なチュートリアルが必要な場合
microsoft_docs_fetch(url: "https://learn.microsoft.com/azure/azure-resource-manager/bicep/deploy-to-subscription")
```

**重要**: Bicep コード生成時は、インターネット上の古いサンプルではなく、これらのツールで取得した最新情報を優先してください。

### Step 8: デプロイ完了時の出力 (重要)

デプロイ成功後は、必ず以下の情報をユーザーに提示してください。

#### 必須出力項目

1. **デプロイ結果サマリー** (リソース名、状態)
2. **Azure Portal リンク** (各リソースへの直接リンク)
3. **接続情報** (エンドポイント、URL など)

#### Azure Portal リンクの生成方法

```
# リソースグループへのリンク
https://portal.azure.com/#@<tenant>/resource/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/overview

# 個別リソースへのリンク
https://portal.azure.com/#@<tenant>/resource<resourceId>
```

#### 出力例フォーマット

デプロイ完了後、以下の形式で出力:

```markdown
## 🎉 デプロイ完了

### デプロイ結果

| リソース   | 名前        | 状態     |
| ---------- | ----------- | -------- |
| ✅ VM      | vm-demo-001 | 作成済み |
| ✅ Storage | stdemoxxx   | 作成済み |

### Azure Portal リンク

| リソース         | Portal リンク                                                                                                                                                             |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| リソースグループ | [rg-demo-minimal](https://portal.azure.com/#@/resource/subscriptions/{subId}/resourceGroups/rg-demo-minimal/overview)                                                     |
| VM               | [vm-demo-001](https://portal.azure.com/#@/resource/subscriptions/{subId}/resourceGroups/rg-demo-minimal/providers/Microsoft.Compute/virtualMachines/vm-demo-001/overview) |
| Storage          | [stdemoxxx](https://portal.azure.com/#@/resource/subscriptions/{subId}/resourceGroups/rg-demo-minimal/providers/Microsoft.Storage/storageAccounts/stdemoxxx/overview)     |
| Databricks       | [dbw-demo-001](https://portal.azure.com/#@/resource/subscriptions/{subId}/resourceGroups/rg-demo-minimal/providers/Microsoft.Databricks/workspaces/dbw-demo-001/overview) |

### 接続情報

| サービス     | エンドポイント                           |
| ------------ | ---------------------------------------- |
| Databricks   | https://adb-xxx.azuredatabricks.net      |
| Storage Blob | https://stdemoxxx.blob.core.windows.net/ |
| VM SSH       | ssh azureuser@<publicIP>                 |
```

**ヒント**: `az deployment group show` の出力から `outputResources` を取得し、リソース ID を使ってリンクを生成。

### Step 8: 成果物のドキュメント化

- `env/<environment>/README.md` に以下を記録:
  - 目的 / スコープ / 状態
  - デプロイ手順
  - 利用したコマンドと出力の要約
  - Azure Portal リンク一覧
  - 今後の改善点

### Step 9: レビューと後続タスク

- Pull Request 用チェックリスト: `references/review-checklist.md`
- 必要に応じてパイプライン (GitHub Actions / Azure DevOps) 化を検討。

## 参照ファイル

- `scripts/scaffold_environment.ps1`: 環境フォルダとテンプレートの自動生成 (ResourceGroup / Subscription 両対応)。
- `scripts/validate_bicep.ps1`: Bicep ファイルの lint & what-if 補助 (スコープ別)。
- `scripts/preview_cli.ps1`: Azure CLI スクリプトの dry-run ヘルパー。
- `scripts/deploy_subscription.ps1`: サブスクリプションレベルデプロイの実行スクリプト。
- `references/environment-template.md`: 環境定義テンプレート。
- `references/review-checklist.md`: レビュー時の確認事項。

## 期待される成果物

- `env/<environment>/` 配下に CLI / Bicep の資材と README が揃っている。
- デプロイ方式が明確に分離され、環境ごとの差分が追跡可能。
- 実行方法と検証結果が記録されており、他メンバーが再現できる状態。

---

環境ごとの成果物を確実に残しつつ、Azure CLI / Bicep のどちらにも対応できるテンプレート運用を目指してください。必要に応じて追加スクリプトやパイプライン連携を提案します。
