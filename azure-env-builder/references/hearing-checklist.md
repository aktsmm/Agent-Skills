# ヒアリングチェックリスト

Azure 環境構築時に確認すべき項目一覧。

## 目次

1. [基本情報](#基本情報)
2. [ネットワーク](#ネットワーク)
3. [コンピュート](#コンピュート)
4. [データ・ストレージ](#データストレージ)
5. [監視・可観測性](#監視可観測性)
6. [セキュリティ](#セキュリティ)
7. [DR・バックアップ](#drバックアップ)

---

## 基本情報

```markdown
- [ ] Azure サブスクリプション ID: \_\_\_
- [ ] Azure AD テナント: \_\_\_
- [ ] 環境名: [ ] dev [ ] staging [ ] prod [ ] その他: \_\_\_
- [ ] リージョン: [ ] japaneast [ ] japanwest [ ] その他: \_\_\_
- [ ] デプロイ方式: [ ] Bicep [ ] Azure CLI
- [ ] スコープ: [ ] ResourceGroup [ ] Subscription
- [ ] 命名規則: \_\_\_
- [ ] タグ要件: \_\_\_
```

---

## ネットワーク

### 接続パターン

```markdown
- [ ] パブリック (インターネット経由)
- [ ] 閉域 (Private Endpoint)
- [ ] ハイブリッド (VPN / ExpressRoute)
```

### VNet 構成

```markdown
- [ ] 新規 VNet 作成
  - CIDR: **_._**.**_._**/\_\_\_
- [ ] 既存 VNet 接続
  - VNet 名: \_\_\_
  - [ ] Hub-Spoke 構成
  - [ ] VNet Peering
```

### Private Endpoint

```markdown
必要なサービス:

- [ ] Storage Account
- [ ] SQL Database
- [ ] Key Vault
- [ ] Container Registry
- [ ] Cosmos DB
- [ ] その他: \_\_\_
```

### ハイブリッド接続

```markdown
- [ ] VPN Gateway
  - SKU: [ ] VpnGw1 [ ] VpnGw2 [ ] VpnGw2AZ
  - [ ] Active-Active
  - [ ] P2S (Point-to-Site)
- [ ] ExpressRoute Gateway
  - SKU: [ ] Standard [ ] HighPerf [ ] UltraPerf
- [ ] Virtual WAN
```

### セキュリティ

```markdown
- [ ] Azure Firewall: [ ] Basic [ ] Standard [ ] Premium
- [ ] Azure Bastion: [ ] Basic [ ] Standard [ ] Premium
- [ ] DDoS Protection Plan
- [ ] NSG ルール要件: \_\_\_
```

### 負荷分散

```markdown
- [ ] Azure Load Balancer (L4)
- [ ] Application Gateway (L7)
  - [ ] WAF 必要
- [ ] Azure Front Door
- [ ] Traffic Manager
```

→ MCP で最新スキーマ取得:

```
mcp_bicep_experim_get_az_resource_type_schema(azResourceType: "Microsoft.Network/virtualNetworks")
microsoft_code_sample_search(query: "VNet Bicep", language: "bicep")
```

---

## コンピュート

### IaaS

```markdown
- [ ] Virtual Machine
  - OS: [ ] Windows [ ] Linux
  - SKU: \_\_\_
  - 台数: \_\_\_
  - [ ] Availability Zone
  - [ ] Availability Set
- [ ] VMSS
  - 最小: **_ 最大: _**
  - [ ] Autoscale
- [ ] Azure Virtual Desktop
```

### PaaS

```markdown
- [ ] App Service
  - SKU: [ ] Basic [ ] Standard [ ] Premium
  - [ ] デプロイスロット
  - [ ] VNet 統合
- [ ] Function App
  - プラン: [ ] Consumption [ ] Premium [ ] Dedicated
- [ ] Container Apps
- [ ] Static Web Apps
```

### コンテナ

```markdown
- [ ] AKS
  - [ ] Private Cluster
  - ノード数: \_\_\_
  - [ ] Autoscale
- [ ] ACR
  - SKU: [ ] Basic [ ] Standard [ ] Premium
- [ ] ACI
```

→ MCP で最新スキーマ取得:

```
mcp_bicep_experim_get_az_resource_type_schema(azResourceType: "Microsoft.Web/sites")
mcp_bicep_experim_get_az_resource_type_schema(azResourceType: "Microsoft.ContainerService/managedClusters")
```

---

## データ・ストレージ

### SQL

```markdown
- [ ] Azure SQL Database
  - SKU: [ ] Basic [ ] Standard [ ] Premium [ ] vCore
  - [ ] Serverless
  - [ ] ゾーン冗長
- [ ] SQL Managed Instance
- [ ] PostgreSQL Flexible Server
- [ ] MySQL Flexible Server
```

### NoSQL

```markdown
- [ ] Cosmos DB
  - API: [ ] NoSQL [ ] MongoDB [ ] Cassandra [ ] Gremlin
  - 容量: [ ] Serverless [ ] Provisioned [ ] Autoscale
- [ ] Redis Cache
  - SKU: [ ] Basic [ ] Standard [ ] Premium
```

### ストレージ

```markdown
- [ ] Storage Account
  - SKU: [ ] Standard_LRS [ ] Standard_GRS [ ] Premium_LRS
  - [ ] Blob [ ] Files [ ] Queue [ ] Table
  - [ ] Data Lake Gen2
  - [ ] Private Endpoint
```

### 分析

```markdown
- [ ] Synapse Analytics
- [ ] Data Factory
- [ ] Databricks
- [ ] Event Hubs
```

→ MCP で最新スキーマ取得:

```
mcp_bicep_experim_get_az_resource_type_schema(azResourceType: "Microsoft.Storage/storageAccounts")
mcp_bicep_experim_get_az_resource_type_schema(azResourceType: "Microsoft.DocumentDB/databaseAccounts")
```

---

## 監視・可観測性

```markdown
- [ ] Log Analytics Workspace
  - 保持日数: \_\_\_ 日
- [ ] Azure Monitor Workspace (Prometheus)
- [ ] Application Insights
- [ ] Azure Managed Grafana
- [ ] Microsoft Sentinel
- [ ] アラートルール: \_\_\_
```

→ MCP で最新スキーマ取得:

```
mcp_bicep_experim_get_az_resource_type_schema(azResourceType: "Microsoft.OperationalInsights/workspaces")
microsoft_code_sample_search(query: "Log Analytics Workspace Bicep", language: "bicep")
```

---

## セキュリティ

```markdown
- [ ] Key Vault
  - [ ] RBAC モード
  - [ ] Private Endpoint
- [ ] Managed Identity
  - [ ] SystemAssigned
  - [ ] UserAssigned
- [ ] Azure AD 認証
- [ ] Defender for Cloud
```

---

## DR・バックアップ

```markdown
- [ ] Azure Backup
  - 対象: [ ] VM [ ] SQL [ ] Files
- [ ] Site Recovery
  - DR リージョン: \_\_\_
- [ ] Geo レプリケーション
  - [ ] Storage GRS
  - [ ] SQL Geo-Replica
  - [ ] Cosmos DB Multi-region
```

---

## 使い方

1. 該当項目にチェックを入れる
2. 必要な値を記入
3. MCP ツールで最新スキーマを取得
4. Bicep 実装に進む
