# AVM (Azure Verified Modules) カタログ

Azure Verified Modules の推奨モジュール一覧。表のバージョンは 2026-10-04 に MCR タグ（`https://mcr.microsoft.com/v2/bicep/<module>/tags/list`）で確認した値。生成前に Bicep MCP の `list_avm_metadata` か MCR タグで最新版を確認すること。

各 reference のコード例の `:x.y.z` は例示時点の版で、表より古いことがある。0.x 系はマイナー版でもパラメーターが変わるため、版を上げるときは各モジュールの README で params を確認する。

## 使用方法

```bicep
// Bicep Registry から直接参照
module example 'br/public:avm/res/storage/storage-account:0.31.0' = {
  name: 'exampleDeployment'
  params: { ... }
}
```

---

## カテゴリ別モジュール一覧

### 🌐 ネットワーク

| モジュール                                       | 説明               | 最新バージョン |
| ------------------------------------------------ | ------------------ | -------------- |
| `avm/res/network/virtual-network`                | VNet               | 0.10.2         |
| `avm/res/network/virtual-network/subnet`         | サブネット         | 0.2.0          |
| `avm/res/network/network-security-group`         | NSG                | 0.5.3          |
| `avm/res/network/application-gateway`            | App Gateway        | 0.10.0         |
| `avm/res/network/azure-firewall`                 | Azure Firewall     | 0.11.1         |
| `avm/res/network/bastion-host`                   | Bastion            | 0.8.2          |
| `avm/res/network/nat-gateway`                    | NAT Gateway        | 2.1.1          |
| `avm/res/network/load-balancer`                  | Load Balancer      | 0.8.0          |
| `avm/res/network/private-endpoint`               | Private Endpoint   | 0.12.1         |
| `avm/res/network/private-dns-zone`               | Private DNS        | 0.8.1          |
| `avm/res/network/dns-zone`                       | Public DNS         | 0.6.2          |
| `avm/res/network/public-ip-address`              | Public IP          | 0.13.0         |
| `avm/res/network/route-table`                    | UDR                | 0.5.0          |
| `avm/res/network/virtual-network-gateway`        | VPN/ER Gateway     | 0.12.0         |
| `avm/res/network/express-route-circuit`          | ExpressRoute       | 0.9.0          |
| `avm/res/network/ddos-protection-plan`           | DDoS Protection    | 0.3.2          |
| `avm/ptn/network/hub-networking`                 | Hub-Spoke パターン | 0.5.0          |
| `avm/ptn/network/private-link-private-dns-zones` | PL DNS 一括作成    | 0.7.3          |

### 💻 コンピュート

| モジュール                                           | 説明            | 最新バージョン |
| ---------------------------------------------------- | --------------- | -------------- |
| `avm/res/compute/virtual-machine`                    | VM              | 0.22.3         |
| `avm/res/compute/virtual-machine-scale-set`          | VMSS            | 0.11.1         |
| `avm/res/compute/availability-set`                   | 可用性セット    | 0.2.4          |
| `avm/res/compute/disk`                               | Managed Disk    | 0.6.1          |
| `avm/res/compute/gallery`                            | Compute Gallery | 0.9.5          |
| `avm/res/compute/image`                              | VM Image        | 0.3.4          |
| `avm/ptn/virtual-machine-images/azure-image-builder` | AIB パターン    | 0.2.2          |

### 📦 コンテナ

| モジュール                                   | 説明               | 最新バージョン |
| -------------------------------------------- | ------------------ | -------------- |
| `avm/res/container-registry/registry`        | ACR                | 0.13.1         |
| `avm/res/container-service/managed-cluster`  | AKS                | 0.14.0         |
| `avm/res/app/managed-environment`            | Container Apps Env | 0.16.0         |
| `avm/res/app/container-app`                  | Container App      | 0.23.0         |
| `avm/res/app/job`                            | Container App Job  | 0.7.2          |
| `avm/res/container-instance/container-group` | ACI                | 0.7.1          |
| `avm/ptn/aca-lza/hosting-environment`        | ACA Landing Zone   | 0.6.3          |

### 🌍 Web

| モジュール                        | 説明                | 最新バージョン |
| --------------------------------- | ------------------- | -------------- |
| `avm/res/web/serverfarm`          | App Service Plan    | 0.7.0          |
| `avm/res/web/site`                | Web App / Functions | 0.24.0         |
| `avm/res/web/static-site`         | Static Web Apps     | 0.9.6          |
| `avm/res/web/hosting-environment` | App Service Env     | 0.5.0          |
| `avm/res/cdn/profile`             | CDN / Front Door    | 0.20.0         |
| `avm/res/api-management/service`  | API Management      | 0.14.4         |

### 🗄️ データベース

| モジュール                                   | 説明             | 最新バージョン |
| -------------------------------------------- | ---------------- | -------------- |
| `avm/res/sql/server`                         | SQL Server       | 0.22.1         |
| `avm/res/sql/server/database`                | SQL Database     | 0.3.1          |
| `avm/res/sql/managed-instance`               | SQL MI           | 0.5.1          |
| `avm/res/db-for-postgre-sql/flexible-server` | PostgreSQL       | 0.16.1         |
| `avm/res/db-for-my-sql/flexible-server`      | MySQL            | 0.11.1         |
| `avm/res/document-db/database-account`       | Cosmos DB        | 0.21.1         |
| `avm/res/document-db/mongo-cluster`          | MongoDB vCore    | 0.4.3          |
| `avm/res/cache/redis`                        | Redis Cache      | 0.18.0         |
| `avm/res/cache/redis-enterprise`             | Redis Enterprise | 0.5.1          |

`cache/redis` は Azure Cache for Redis（2028-09-30 廃止、2026-04-01 以降は新規顧客の作成不可）。新規は `cache/redis-enterprise`（Azure Managed Redis）を使う。

### 📊 ストレージ

| モジュール                                               | 説明               | 最新バージョン |
| -------------------------------------------------------- | ------------------ | -------------- |
| `avm/res/storage/storage-account`                        | Storage Account    | 0.33.1         |
| `avm/res/storage/storage-account/blob-service/container` | Blob Container     | 0.3.4          |
| `avm/res/storage/storage-account/file-service/share`     | File Share         | 0.1.3          |
| `avm/res/net-app/net-app-account`                        | Azure NetApp Files | 0.12.4         |
| `avm/res/elastic-san/elastic-san`                        | Elastic SAN        | 0.5.1          |

### 🤖 AI / ML

| モジュール                                    | 説明                        | 最新バージョン |
| --------------------------------------------- | --------------------------- | -------------- |
| `avm/res/cognitive-services/account`          | Cognitive Services / OpenAI | 0.19.1         |
| `avm/res/machine-learning-services/workspace` | ML Workspace                | 0.14.1         |
| `avm/res/search/search-service`               | AI Search                   | 0.13.0         |
| `avm/ptn/ai-ml/ai-foundry`                    | AI Foundry パターン         | 0.7.0          |
| `avm/ptn/ai-platform/baseline`                | AI Platform 基盤            | 0.8.0          |

`ai-ml/ai-foundry` は Microsoft Foundry（旧 Azure AI Foundry）の Foundry resource + project を作る。

### 📈 監視

| モジュール                               | 説明                | 最新バージョン |
| ---------------------------------------- | ------------------- | -------------- |
| `avm/res/operational-insights/workspace` | Log Analytics       | 0.16.1         |
| `avm/res/insights/component`             | App Insights        | 0.8.0          |
| `avm/res/insights/action-group`          | Action Group        | 0.8.0          |
| `avm/res/insights/metric-alert`          | Metric Alert        | 0.4.1          |
| `avm/res/insights/data-collection-rule`  | DCR                 | 0.11.0         |
| `avm/res/insights/diagnostic-setting`    | Diagnostic Settings | 0.1.4          |
| `avm/ptn/azd/monitoring`                 | 監視パターン        | 0.2.1          |

### 🔐 セキュリティ

| モジュール                                        | 説明                  | 最新バージョン |
| ------------------------------------------------- | --------------------- | -------------- |
| `avm/res/key-vault/vault`                         | Key Vault             | 0.14.2         |
| `avm/res/managed-identity/user-assigned-identity` | Managed Identity      | 0.6.0          |
| `avm/ptn/security/security-center`                | Defender for Cloud    | 0.3.0          |
| `avm/res/aad/domain-service`                      | Entra Domain Services | 0.7.0          |

### 🔄 統合

| モジュール                      | 説明             | 最新バージョン |
| ------------------------------- | ---------------- | -------------- |
| `avm/res/event-hub/namespace`   | Event Hubs       | 0.15.1         |
| `avm/res/service-bus/namespace` | Service Bus      | 0.17.1         |
| `avm/res/event-grid/topic`      | Event Grid Topic | 0.10.0         |
| `avm/res/logic/workflow`        | Logic App        | 0.6.0          |
| `avm/res/data-factory/factory`  | Data Factory     | 0.12.1         |

### 🔧 DevOps

| モジュール                                | 説明                | 最新バージョン |
| ----------------------------------------- | ------------------- | -------------- |
| `avm/res/dev-ops-infrastructure/pool`     | Managed DevOps Pool | 0.8.0          |
| `avm/ptn/dev-ops/cicd-agents-and-runners` | CI/CD エージェント  | 0.3.1          |
| `avm/res/automation/automation-account`   | Automation Account  | 0.19.3         |

### 🏢 ガバナンス

| モジュール                                | 説明                   | 最新バージョン |
| ----------------------------------------- | ---------------------- | -------------- |
| `avm/ptn/lz/sub-vending`                  | サブスクリプション発行 | 0.8.0          |
| `avm/ptn/authorization/policy-assignment` | ポリシー割り当て       | 0.5.3          |
| `avm/ptn/authorization/role-assignment`   | ロール割り当て         | 0.2.4          |
| `avm/res/management/management-group`     | 管理グループ           | 0.2.0          |
| `avm/res/consumption/budget`              | 予算アラート           | 0.3.8          |

### 💾 バックアップ / DR

| モジュール                             | 説明                    | 最新バージョン |
| -------------------------------------- | ----------------------- | -------------- |
| `avm/res/recovery-services/vault`      | Recovery Services Vault | 0.13.2         |
| `avm/res/data-protection/backup-vault` | Backup Vault            | 0.13.3         |

---

## パターンモジュール (ptn)

複数リソースを組み合わせた複合パターン：

| モジュール                                    | 説明                    | 最新バージョン |
| --------------------------------------------- | ----------------------- | -------------- |
| `avm/ptn/network/hub-networking`              | Hub-Spoke ネットワーク  | 0.5.0          |
| `avm/ptn/aca-lza/hosting-environment`         | ACA Landing Zone        | 0.6.3          |
| `avm/ptn/app-service-lza/hosting-environment` | App Service LZ          | 0.2.0          |
| `avm/ptn/ai-ml/ai-foundry`                    | AI Foundry              | 0.7.0          |
| `avm/ptn/lz/sub-vending`                      | サブスクリプション発行  | 0.8.0          |
| `avm/ptn/azd/container-apps-stack`            | Container Apps スタック | 0.4.0          |
| `avm/ptn/data/private-analytical-workspace`   | 分析ワークスペース      | 0.1.2          |

---

## 使用例

### VM + カスタムスクリプト

```bicep
module vm 'br/public:avm/res/compute/virtual-machine:0.21.0' = {
  name: 'vmDeployment'
  params: {
    name: 'vm-app-${environment}'
    vmSize: 'Standard_D4s_v5'
    imageReference: {
      publisher: 'Canonical'
      offer: '0001-com-ubuntu-server-jammy'
      sku: '22_04-lts-gen2'
      version: 'latest'
    }
    osType: 'Linux'
    nicConfigurations: [
      {
        ipConfigurations: [
          { subnetResourceId: subnetId }
        ]
      }
    ]
    adminUsername: 'azureuser'
    disablePasswordAuthentication: true
    publicKeys: [
      { path: '/home/azureuser/.ssh/authorized_keys', keyData: sshPublicKey }
    ]
    // cloud-init でアプリ初期化
    customData: loadFileAsBase64('scripts/vm-init/app-init.yaml')
  }
}
```

### Private Endpoint 付き Storage

```bicep
module storage 'br/public:avm/res/storage/storage-account:0.31.0' = {
  name: 'storageDeployment'
  params: {
    name: 'st${workloadName}${environment}'
    skuName: 'Standard_LRS'
    kind: 'StorageV2'
    privateEndpoints: [
      {
        subnetResourceId: subnetId
        service: 'blob'
        privateDnsZoneGroup: {
          privateDnsZoneGroupConfigs: [
            { privateDnsZoneResourceId: blobPrivateDnsZoneId }
          ]
        }
      }
    ]
  }
}
```

---

## 最新情報の取得

```powershell
# MCP が使えないときは MCR タグで最新版を確認
(Invoke-RestMethod 'https://mcr.microsoft.com/v2/bicep/avm/res/storage/storage-account/tags/list').tags
```
