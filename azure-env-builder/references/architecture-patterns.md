# アーキテクチャパターン

実践的な Azure 複合構成パターン集。MCP ツールで最新情報を取得してから使用すること。

## 目次

1. [Landing Zone (Hub-Spoke)](#1-landing-zone-hub-spoke)
2. [Web + DB (3 層アーキテクチャ)](#2-web--db-3層アーキテクチャ)
3. [コンテナ基盤 (AKS / Container Apps)](#3-コンテナ基盤)
4. [AI/ML 基盤](#4-aiml-基盤)
5. [データ分析基盤](#5-データ分析基盤)
6. [プロキシ/ゲートウェイ VM](#6-プロキシゲートウェイ-vm)

---

## 1. Landing Zone (Hub-Spoke)

### 概要

エンタープライズ向けネットワーク基盤。Hub VNet に共有サービス（Firewall, Bastion, VPN）を配置し、Spoke VNet とピアリング。

### AVM モジュール

```bicep
// Hub ネットワーク
module hubNetwork 'br/public:avm/ptn/network/hub-networking:0.5.0' = {
  name: 'hubNetworkDeployment'
  params: {
    hubVirtualNetworks: {
      hub1: {
        addressPrefixes: ['10.0.0.0/16']
        subnets: {
          AzureFirewallSubnet: { addressPrefix: '10.0.1.0/26' }
          AzureBastionSubnet: { addressPrefix: '10.0.2.0/26' }
          GatewaySubnet: { addressPrefix: '10.0.3.0/26' }
        }
      }
    }
  }
}

// Azure Firewall
module firewall 'br/public:avm/res/network/azure-firewall:0.9.2' = {
  name: 'firewallDeployment'
  params: {
    name: 'afw-hub-${environment}'
    virtualNetworkResourceId: hubNetwork.outputs.hubVirtualNetworkResourceIds.hub1
    publicIPAddressObject: {
      name: 'pip-afw-hub-${environment}'
    }
  }
}

// Bastion
module bastion 'br/public:avm/res/network/bastion-host:0.8.2' = {
  name: 'bastionDeployment'
  params: {
    name: 'bas-hub-${environment}'
    virtualNetworkResourceId: hubNetwork.outputs.hubVirtualNetworkResourceIds.hub1
  }
}
```

### 設定値連携

| Hub リソース     | 連携先 Spoke        | 連携内容                        |
| ---------------- | ------------------- | ------------------------------- |
| Azure Firewall   | UDR                 | 0.0.0.0/0 → Firewall Private IP |
| Private DNS Zone | VNet Link           | Spoke VNet への DNS 解決        |
| Log Analytics    | Diagnostic Settings | 全リソースのログ収集先          |

---

## 2. Web + DB (3 層アーキテクチャ)

### 概要

App Service + SQL Database の典型的な Web アプリ構成。Private Endpoint で閉域化可能。

### AVM モジュール

```bicep
// App Service Plan
module appServicePlan 'br/public:avm/res/web/serverfarm:0.5.0' = {
  name: 'appServicePlanDeployment'
  params: {
    name: 'asp-${workloadName}-${environment}'
    skuName: 'P1v3'
    kind: 'Linux'
  }
}

// Web App
module webApp 'br/public:avm/res/web/site:0.19.4' = {
  name: 'webAppDeployment'
  params: {
    name: 'app-${workloadName}-${environment}'
    serverFarmResourceId: appServicePlan.outputs.resourceId
    siteConfig: {
      linuxFxVersion: 'DOTNETCORE|8.0'
      appSettings: [
        // SQL 接続文字列は Key Vault 参照
        { name: 'ConnectionStrings__DefaultConnection', value: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=sql-connection-string)' }
      ]
    }
    privateEndpoints: enablePrivateEndpoint ? [
      {
        subnetResourceId: subnetId
        privateDnsZoneGroup: {
          privateDnsZoneGroupConfigs: [
            { privateDnsZoneResourceId: privateDnsZoneId }
          ]
        }
      }
    ] : []
  }
}

// SQL Server + Database
module sqlServer 'br/public:avm/res/sql/server:0.21.1' = {
  name: 'sqlServerDeployment'
  params: {
    name: 'sql-${workloadName}-${environment}'
    administratorLogin: 'sqladmin'
    administratorLoginPassword: sqlAdminPassword
    databases: [
      {
        name: 'sqldb-${workloadName}-${environment}'
        skuName: 'S1'
      }
    ]
    privateEndpoints: enablePrivateEndpoint ? [
      {
        subnetResourceId: subnetId
        privateDnsZoneGroup: {
          privateDnsZoneGroupConfigs: [
            { privateDnsZoneResourceId: sqlPrivateDnsZoneId }
          ]
        }
      }
    ] : []
  }
}
```

### 設定値連携

| ソース       | ターゲット | 連携内容                    |
| ------------ | ---------- | --------------------------- |
| SQL Server   | Web App    | 接続文字列 (Key Vault 経由) |
| App Insights | Web App    | InstrumentationKey          |
| Storage      | Web App    | Blob 接続文字列             |

---

## 3. コンテナ基盤

### 3.1 Azure Container Apps

```bicep
// Container Apps Environment
module containerAppsEnv 'br/public:avm/res/app/managed-environment:0.11.3' = {
  name: 'containerAppsEnvDeployment'
  params: {
    name: 'cae-${workloadName}-${environment}'
    logAnalyticsWorkspaceResourceId: logAnalyticsId
    infrastructureSubnetId: containerAppsSubnetId
  }
}

// Container App
module containerApp 'br/public:avm/res/app/container-app:0.19.0' = {
  name: 'containerAppDeployment'
  params: {
    name: 'ca-${workloadName}-${environment}'
    environmentResourceId: containerAppsEnv.outputs.resourceId
    containers: [
      {
        name: 'main'
        image: '${acrName}.azurecr.io/${imageName}:${imageTag}'
        resources: {
          cpu: json('0.5')
          memory: '1Gi'
        }
        env: [
          { name: 'DATABASE_URL', secretRef: 'db-connection' }
        ]
      }
    ]
    secrets: {
      secureList: [
        { name: 'db-connection', keyVaultUrl: '${keyVaultUri}secrets/db-connection', identity: managedIdentityId }
      ]
    }
  }
}
```

### 3.2 Azure Kubernetes Service (AKS)

```bicep
// AKS Cluster
module aksCluster 'br/public:avm/res/container-service/managed-cluster:0.11.1' = {
  name: 'aksClusterDeployment'
  params: {
    name: 'aks-${workloadName}-${environment}'
    primaryAgentPoolProfiles: [
      {
        name: 'systempool'
        mode: 'System'
        count: 3
        vmSize: 'Standard_D4s_v5'
        vnetSubnetResourceId: aksSubnetId
      }
    ]
    agentPoolProfiles: [
      {
        name: 'userpool'
        mode: 'User'
        count: 3
        vmSize: 'Standard_D8s_v5'
        vnetSubnetResourceId: aksSubnetId
      }
    ]
    networkPlugin: 'azure'
    networkPolicy: 'azure'
    enablePrivateCluster: true
    aadProfile: {
      managed: true
      enableAzureRbac: true
    }
  }
}
```

---

## 4. AI/ML 基盤

### 概要

Azure AI Foundry (旧 Azure Machine Learning) を中心とした AI 開発環境。

### AVM モジュール

```bicep
// AI Foundry
module aiFoundry 'br/public:avm/ptn/ai-ml/ai-foundry:0.6.0' = {
  name: 'aiFoundryDeployment'
  params: {
    name: 'aif-${workloadName}-${environment}'
    projectName: 'project-${workloadName}'
    // Cognitive Services (OpenAI) を自動作成
    cognitiveServicesAccountName: 'cog-${workloadName}-${environment}'
    cognitiveServicesDeployments: [
      { name: 'gpt-4o', model: { name: 'gpt-4o', version: '2024-08-06' }, sku: { name: 'Standard', capacity: 10 } }
      { name: 'text-embedding-3-large', model: { name: 'text-embedding-3-large', version: '1' }, sku: { name: 'Standard', capacity: 10 } }
    ]
    storageAccountName: 'st${workloadName}${environment}'
    keyVaultName: 'kv-${workloadName}-${environment}'
  }
}
```

### OpenAI Service 単体

```bicep
// Azure OpenAI
module openai 'br/public:avm/res/cognitive-services/account:0.14.1' = {
  name: 'openaiDeployment'
  params: {
    name: 'oai-${workloadName}-${environment}'
    kind: 'OpenAI'
    customSubDomainName: 'oai-${workloadName}-${environment}'
    deployments: [
      {
        name: 'gpt-4o'
        model: { format: 'OpenAI', name: 'gpt-4o', version: '2024-08-06' }
        sku: { name: 'Standard', capacity: 10 }
      }
    ]
    privateEndpoints: enablePrivateEndpoint ? [
      { subnetResourceId: subnetId }
    ] : []
  }
}
```

---

## 5. データ分析基盤

### Synapse Analytics

```bicep
// Synapse Workspace
module synapse 'br/public:avm/res/synapse/workspace:0.14.2' = {
  name: 'synapseDeployment'
  params: {
    name: 'syn-${workloadName}-${environment}'
    defaultDataLakeStorageAccountResourceId: storageAccountId
    defaultDataLakeStorageFilesystem: 'synapse'
    sqlAdministratorLogin: 'synadmin'
    sqlAdministratorLoginPassword: sqlAdminPassword
    managedVirtualNetwork: 'default'
  }
}
```

### Microsoft Fabric (Capacity)

```bicep
// Fabric Capacity
module fabricCapacity 'br/public:avm/res/fabric/capacity:0.1.2' = {
  name: 'fabricCapacityDeployment'
  params: {
    name: 'fab${workloadName}${environment}'
    skuName: 'F2'
    administrationMembers: [
      adminPrincipalId
    ]
  }
}
```

---

## 6. プロキシ/ゲートウェイ VM

### 6.1 Squid Proxy VM

```bicep
// Squid Proxy VM
module squidVm 'br/public:avm/res/compute/virtual-machine:0.21.0' = {
  name: 'squidVmDeployment'
  params: {
    name: 'vm-squid-${environment}'
    vmSize: 'Standard_B2ms'
    imageReference: {
      publisher: 'Canonical'
      offer: '0001-com-ubuntu-server-jammy'
      sku: '22_04-lts-gen2'
      version: 'latest'
    }
    osType: 'Linux'
    osDisk: {
      diskSizeGB: 64
      managedDisk: { storageAccountType: 'Premium_LRS' }
    }
    nicConfigurations: [
      {
        ipConfigurations: [
          { subnetResourceId: subnetId }
        ]
        enableIPForwarding: true
      }
    ]
    adminUsername: 'azureuser'
    adminPassword: adminPassword
    // cloud-init で Squid 自動インストール
    customData: loadFileAsBase64('../../scripts/vm-init/squid-init.yaml')
    // または CustomScriptExtension
    extensionCustomScriptConfig: {
      enabled: true
      fileData: [
        { uri: 'https://raw.githubusercontent.com/yourrepo/scripts/squid-setup.sh' }
      ]
      settings: {
        commandToExecute: 'bash squid-setup.sh --allowed-networks "10.0.0.0/8,172.16.0.0/12"'
      }
    }
  }
}
```

### 6.2 Nginx リバースプロキシ VM

```bicep
// Nginx Reverse Proxy VM
module nginxVm 'br/public:avm/res/compute/virtual-machine:0.21.0' = {
  name: 'nginxVmDeployment'
  params: {
    name: 'vm-nginx-${environment}'
    vmSize: 'Standard_B2ms'
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
          {
            subnetResourceId: subnetId
            publicIPAddressResourceId: publicIpId
          }
        ]
      }
    ]
    adminUsername: 'azureuser'
    disablePasswordAuthentication: true
    publicKeys: [
      { path: '/home/azureuser/.ssh/authorized_keys', keyData: sshPublicKey }
    ]
    // cloud-init で Nginx + Let's Encrypt 自動設定
    customData: loadFileAsBase64('../../scripts/vm-init/nginx-init.yaml')
  }
}
```

---

## 設定値連携のベストプラクティス

### 1. Key Vault 経由の接続文字列管理

```bicep
// SQL 接続文字列を Key Vault に格納
module sqlConnectionSecret 'br/public:avm/res/key-vault/vault/secret:0.1.0' = {
  name: 'sqlConnectionSecretDeployment'
  params: {
    keyVaultName: keyVault.outputs.name
    name: 'sql-connection-string'
    value: 'Server=tcp:${sqlServer.outputs.fullyQualifiedDomainName},1433;Database=${databaseName};Authentication=Active Directory Managed Identity;'
  }
}

// App Service から参照
var appSettings = [
  {
    name: 'ConnectionStrings__DefaultConnection'
    value: '@Microsoft.KeyVault(SecretUri=${sqlConnectionSecret.outputs.secretUri})'
  }
]
```

### 2. Managed Identity による認証

```bicep
// User Assigned Managed Identity
module identity 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.3' = {
  name: 'identityDeployment'
  params: {
    name: 'id-${workloadName}-${environment}'
  }
}

// SQL Server への RBAC 付与
module sqlRoleAssignment 'br/public:avm/res/authorization/role-assignment/rg-scope:0.1.1' = {
  name: 'sqlRoleAssignmentDeployment'
  params: {
    roleDefinitionId: '9b7fa17d-e63e-47b0-bb0a-15c516ac86ec' // SQL DB Contributor
    principalId: identity.outputs.principalId
  }
}
```

### 3. Private DNS Zone の一元管理

```bicep
// Private Link 用 DNS ゾーンを一括作成
module privateDnsZones 'br/public:avm/ptn/network/private-link-private-dns-zones:0.7.1' = {
  name: 'privateDnsZonesDeployment'
  params: {
    location: 'global'
    virtualNetworkLinks: [
      { virtualNetworkResourceId: hubVnetId }
      { virtualNetworkResourceId: spokeVnetId }
    ]
  }
}
```

---

## 次のステップ

1. [VM アプリケーションスクリプト](vm-app-scripts/) - Squid, Nginx 等の初期化スクリプト
2. [サービス設定テンプレート](service-config-templates.md) - 連携設定のテンプレート
3. [AVM モジュール一覧](avm-modules.md) - 推奨モジュールカタログ
