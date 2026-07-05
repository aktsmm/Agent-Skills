# サービス設定テンプレート

Azure リソース間の設定値連携パターン集。リソース作成時に他リソースの情報を自動連携する。

## 目次

1. [接続文字列パターン](#1-接続文字列パターン)
2. [Private Endpoint 連携](#2-private-endpoint-連携)
3. [Managed Identity 連携](#3-managed-identity-連携)
4. [監視設定連携](#4-監視設定連携)
5. [ネットワーク設定連携](#5-ネットワーク設定連携)
6. [完全な連携例](#6-完全な連携例)

---

## 1. 接続文字列パターン

### SQL Database → App Service

```bicep
// SQL Server 作成
module sqlServer 'br/public:avm/res/sql/server:0.21.1' = {
  name: 'sqlServerDeployment'
  params: {
    name: 'sql-${workloadName}-${environment}'
    administratorLogin: 'sqladmin'
    administratorLoginPassword: sqlAdminPassword
    databases: [
      { name: 'sqldb-${workloadName}', skuName: 'S1' }
    ]
  }
}

// Key Vault に接続文字列を格納
module sqlConnectionSecret 'br/public:avm/res/key-vault/vault/secret:0.1.0' = {
  name: 'sqlConnectionSecretDeployment'
  params: {
    keyVaultName: keyVault.outputs.name
    name: 'sql-connection-string'
    // Managed Identity 認証の接続文字列
    value: 'Server=tcp:${sqlServer.outputs.fullyQualifiedDomainName},1433;Database=sqldb-${workloadName};Authentication=Active Directory Managed Identity;'
  }
}

// App Service から Key Vault 参照
module webApp 'br/public:avm/res/web/site:0.19.4' = {
  name: 'webAppDeployment'
  params: {
    name: 'app-${workloadName}-${environment}'
    serverFarmResourceId: appServicePlan.outputs.resourceId
    managedIdentities: {
      userAssignedResourceIds: [identity.outputs.resourceId]
    }
    siteConfig: {
      appSettings: [
        {
          name: 'ConnectionStrings__DefaultConnection'
          value: '@Microsoft.KeyVault(VaultName=${keyVault.outputs.name};SecretName=sql-connection-string)'
        }
      ]
    }
  }
}
```

### Storage Account → Various Services

```bicep
// Storage Account 作成
module storage 'br/public:avm/res/storage/storage-account:0.31.0' = {
  name: 'storageDeployment'
  params: {
    name: 'st${workloadName}${environment}'
    skuName: 'Standard_LRS'
  }
}

// 接続文字列の構築
var storageConnectionString = 'DefaultEndpointsProtocol=https;AccountName=${storage.outputs.name};AccountKey=${storage.outputs.primaryBlobServiceConnectionString};EndpointSuffix=core.windows.net'

// Blob URL の構築
var blobEndpoint = storage.outputs.primaryBlobEndpoint

// Key Vault に格納
module storageSecret 'br/public:avm/res/key-vault/vault/secret:0.1.0' = {
  name: 'storageSecretDeployment'
  params: {
    keyVaultName: keyVault.outputs.name
    name: 'storage-connection-string'
    value: storageConnectionString
  }
}
```

### Redis Cache → App Service

```bicep
// Redis Cache 作成
module redis 'br/public:avm/res/cache/redis:0.16.4' = {
  name: 'redisDeployment'
  params: {
    name: 'redis-${workloadName}-${environment}'
    skuName: 'Standard'
    capacity: 1
  }
}

// Redis 接続文字列を Key Vault に格納
module redisSecret 'br/public:avm/res/key-vault/vault/secret:0.1.0' = {
  name: 'redisSecretDeployment'
  params: {
    keyVaultName: keyVault.outputs.name
    name: 'redis-connection-string'
    value: '${redis.outputs.hostName}:6380,password=${redis.outputs.primaryKey},ssl=True,abortConnect=False'
  }
}

// Container App での使用例
module containerApp 'br/public:avm/res/app/container-app:0.19.0' = {
  params: {
    containers: [
      {
        name: 'main'
        image: '${acrName}.azurecr.io/myapp:latest'
        env: [
          { name: 'REDIS_URL', secretRef: 'redis-connection' }
        ]
      }
    ]
    secrets: {
      secureList: [
        {
          name: 'redis-connection'
          keyVaultUrl: '${keyVault.outputs.uri}secrets/redis-connection-string'
          identity: identity.outputs.resourceId
        }
      ]
    }
  }
}
```

---

## 2. Private Endpoint 連携

### 共通 Private DNS Zone パターン

```bicep
// Private Link 用 DNS ゾーンを一括作成
module privateDnsZones 'br/public:avm/ptn/network/private-link-private-dns-zones:0.7.1' = {
  name: 'privateDnsZonesDeployment'
  scope: resourceGroup(dnsResourceGroup)
  params: {
    location: 'global'
    virtualNetworkLinks: [
      { virtualNetworkResourceId: hubVnetId }
      { virtualNetworkResourceId: spokeVnetId }
    ]
  }
}

// 各サービスの Private Endpoint で DNS ゾーンを参照
var privateDnsZoneConfigs = {
  blob: '${subscription().id}/resourceGroups/${dnsResourceGroup}/providers/Microsoft.Network/privateDnsZones/privatelink.blob.core.windows.net'
  sql: '${subscription().id}/resourceGroups/${dnsResourceGroup}/providers/Microsoft.Network/privateDnsZones/privatelink.database.windows.net'
  keyvault: '${subscription().id}/resourceGroups/${dnsResourceGroup}/providers/Microsoft.Network/privateDnsZones/privatelink.vaultcore.azure.net'
  webapp: '${subscription().id}/resourceGroups/${dnsResourceGroup}/providers/Microsoft.Network/privateDnsZones/privatelink.azurewebsites.net'
}

// Storage Private Endpoint
module storagePrivateEndpoint 'br/public:avm/res/network/private-endpoint:0.11.1' = {
  name: 'storagePrivateEndpointDeployment'
  params: {
    name: 'pe-${storage.outputs.name}-blob'
    subnetResourceId: privateEndpointSubnetId
    privateLinkServiceConnections: [
      {
        name: 'storage-blob'
        properties: {
          privateLinkServiceId: storage.outputs.resourceId
          groupIds: ['blob']
        }
      }
    ]
    privateDnsZoneGroup: {
      privateDnsZoneGroupConfigs: [
        { privateDnsZoneResourceId: privateDnsZoneConfigs.blob }
      ]
    }
  }
}
```

---

## 3. Managed Identity 連携

### RBAC 付与パターン

```bicep
// User Assigned Managed Identity
module identity 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.3' = {
  name: 'identityDeployment'
  params: {
    name: 'id-${workloadName}-${environment}'
  }
}

// 各リソースへの RBAC 付与

// Storage Blob Data Contributor
module storageBlobRole 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.2' = {
  name: 'storageBlobRoleDeployment'
  params: {
    resourceId: storage.outputs.resourceId
    roleDefinitionId: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe' // Storage Blob Data Contributor
    principalId: identity.outputs.principalId
    principalType: 'ServicePrincipal'
  }
}

// Key Vault Secrets User
module keyVaultRole 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.2' = {
  name: 'keyVaultRoleDeployment'
  params: {
    resourceId: keyVault.outputs.resourceId
    roleDefinitionId: '4633458b-17de-408a-b874-0445c86b69e6' // Key Vault Secrets User
    principalId: identity.outputs.principalId
    principalType: 'ServicePrincipal'
  }
}

// Azure SQL に対する Directory Reader (Entra ID 認証)
// ※ SQL Server の administrators に Managed Identity を追加
module sqlServer 'br/public:avm/res/sql/server:0.21.1' = {
  params: {
    administrators: {
      azureADOnlyAuthentication: true
      login: 'id-${workloadName}-${environment}'
      sid: identity.outputs.principalId
      tenantId: subscription().tenantId
    }
  }
}
```

### 一般的な Role Definition ID

| ロール名                       | Role Definition ID                     | 用途                 |
| ------------------------------ | -------------------------------------- | -------------------- |
| Storage Blob Data Contributor  | `ba92f5b4-2d11-453d-a403-e96b0029c9fe` | Blob 読み書き        |
| Storage Blob Data Reader       | `2a2b9908-6ea1-4ae2-8e65-a410df84e7d1` | Blob 読み取り        |
| Key Vault Secrets User         | `4633458b-17de-408a-b874-0445c86b69e6` | シークレット読み取り |
| Key Vault Certificates Officer | `a4417e6f-fecd-4de8-b567-7b0420556985` | 証明書管理           |
| SQL DB Contributor             | `9b7fa17d-e63e-47b0-bb0a-15c516ac86ec` | SQL DB 管理          |
| AcrPull                        | `7f951dda-4ed3-4680-a7ca-43fe172d538d` | ACR イメージ Pull    |
| Cognitive Services OpenAI User | `5e0bd9bd-7b93-4f28-af87-19fc36ad61bd` | OpenAI 利用          |

---

## 4. 監視設定連携

### Application Insights → App Service

```bicep
// Log Analytics Workspace
module logAnalytics 'br/public:avm/res/operational-insights/workspace:0.14.2' = {
  name: 'logAnalyticsDeployment'
  params: {
    name: 'log-${workloadName}-${environment}'
    retentionInDays: 30
  }
}

// Application Insights
module appInsights 'br/public:avm/res/insights/component:0.7.1' = {
  name: 'appInsightsDeployment'
  params: {
    name: 'appi-${workloadName}-${environment}'
    workspaceResourceId: logAnalytics.outputs.resourceId
    kind: 'web'
    applicationType: 'web'
  }
}

// App Service に接続
module webApp 'br/public:avm/res/web/site:0.19.4' = {
  params: {
    siteConfig: {
      appSettings: [
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsights.outputs.connectionString }
        { name: 'ApplicationInsightsAgent_EXTENSION_VERSION', value: '~3' }
      ]
    }
  }
}
```

### Diagnostic Settings 連携

```bicep
// 全リソースに Diagnostic Settings を適用するモジュール
module diagnosticSettings 'br/public:avm/res/insights/diagnostic-setting:0.1.4' = [for resource in resources: {
  name: 'diagnosticSettingsDeployment-${resource.name}'
  scope: resource.scope
  params: {
    name: 'diag-${resource.name}'
    workspaceResourceId: logAnalytics.outputs.resourceId
    logs: [
      { categoryGroup: 'allLogs', enabled: true }
    ]
    metrics: [
      { category: 'AllMetrics', enabled: true }
    ]
  }
}]
```

---

## 5. ネットワーク設定連携

### Firewall → UDR 連携

```bicep
// Azure Firewall
module firewall 'br/public:avm/res/network/azure-firewall:0.9.2' = {
  name: 'firewallDeployment'
  params: {
    name: 'afw-hub-${environment}'
    virtualNetworkResourceId: hubVnetId
    publicIPAddressObject: { name: 'pip-afw-hub-${environment}' }
  }
}

// Spoke VNet 用 UDR (Firewall 経由)
module spokeRouteTable 'br/public:avm/res/network/route-table:0.5.0' = {
  name: 'spokeRouteTableDeployment'
  params: {
    name: 'rt-spoke-to-firewall'
    routes: [
      {
        name: 'default-to-firewall'
        addressPrefix: '0.0.0.0/0'
        nextHopType: 'VirtualAppliance'
        nextHopIpAddress: firewall.outputs.privateIpAddress
      }
    ]
  }
}

// Subnet に UDR を関連付け
module spokeVnet 'br/public:avm/res/network/virtual-network:0.7.2' = {
  params: {
    subnets: [
      {
        name: 'snet-app'
        addressPrefix: '10.1.1.0/24'
        routeTableResourceId: spokeRouteTable.outputs.resourceId
      }
    ]
  }
}
```

### Squid Proxy → UDR 連携

```bicep
// Squid VM
module squidVm 'br/public:avm/res/compute/virtual-machine:0.21.0' = {
  name: 'squidVmDeployment'
  params: {
    name: 'vm-squid-${environment}'
    nicConfigurations: [
      {
        ipConfigurations: [
          {
            subnetResourceId: proxySubnetId
            privateIPAllocationMethod: 'Static'
            privateIPAddress: '10.0.2.10'  // 固定 IP
          }
        ]
        enableIPForwarding: true
      }
    ]
    customData: loadFileAsBase64('scripts/vm-init/squid-init.yaml')
  }
}

// HTTP/HTTPS トラフィックを Squid 経由にルーティング
module proxyRouteTable 'br/public:avm/res/network/route-table:0.5.0' = {
  name: 'proxyRouteTableDeployment'
  params: {
    name: 'rt-via-squid'
    routes: [
      {
        name: 'http-to-squid'
        addressPrefix: '0.0.0.0/0'
        nextHopType: 'VirtualAppliance'
        nextHopIpAddress: '10.0.2.10'  // Squid の IP
      }
    ]
  }
}
```

---

## 6. 完全な連携例

### Web + SQL + Redis + Storage 構成

```bicep
// === main.bicep ===
@description('環境名 (dev/staging/prod)')
param environment string

@description('ワークロード名')
param workloadName string

@description('リージョン')
param location string = resourceGroup().location

// === Managed Identity ===
module identity 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.3' = {
  name: 'identityDeployment'
  params: {
    name: 'id-${workloadName}-${environment}'
    location: location
  }
}

// === Key Vault ===
module keyVault 'br/public:avm/res/key-vault/vault:0.13.3' = {
  name: 'keyVaultDeployment'
  params: {
    name: 'kv-${workloadName}-${environment}'
    location: location
    enableRbacAuthorization: true
  }
}

// Key Vault への RBAC
module kvRole 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.2' = {
  name: 'kvRoleDeployment'
  params: {
    resourceId: keyVault.outputs.resourceId
    roleDefinitionId: '4633458b-17de-408a-b874-0445c86b69e6'
    principalId: identity.outputs.principalId
  }
}

// === Storage ===
module storage 'br/public:avm/res/storage/storage-account:0.31.0' = {
  name: 'storageDeployment'
  params: {
    name: 'st${workloadName}${environment}'
    location: location
    skuName: 'Standard_LRS'
  }
}

// Storage への RBAC
module storageRole 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.2' = {
  name: 'storageRoleDeployment'
  params: {
    resourceId: storage.outputs.resourceId
    roleDefinitionId: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    principalId: identity.outputs.principalId
  }
}

// === SQL Database ===
module sqlServer 'br/public:avm/res/sql/server:0.21.1' = {
  name: 'sqlServerDeployment'
  params: {
    name: 'sql-${workloadName}-${environment}'
    location: location
    administrators: {
      azureADOnlyAuthentication: true
      login: identity.outputs.name
      sid: identity.outputs.principalId
      tenantId: subscription().tenantId
    }
    databases: [
      { name: 'sqldb-${workloadName}', skuName: 'S1' }
    ]
  }
}

// === Redis ===
module redis 'br/public:avm/res/cache/redis:0.16.4' = {
  name: 'redisDeployment'
  params: {
    name: 'redis-${workloadName}-${environment}'
    location: location
    skuName: 'Standard'
    capacity: 1
  }
}

// Redis 接続文字列を Key Vault に格納
module redisSecret 'br/public:avm/res/key-vault/vault/secret:0.1.0' = {
  name: 'redisSecretDeployment'
  dependsOn: [kvRole]
  params: {
    keyVaultName: keyVault.outputs.name
    name: 'redis-connection'
    value: '${redis.outputs.hostName}:6380,password=${redis.outputs.primaryKey},ssl=True,abortConnect=False'
  }
}

// === App Insights ===
module appInsights 'br/public:avm/res/insights/component:0.7.1' = {
  name: 'appInsightsDeployment'
  params: {
    name: 'appi-${workloadName}-${environment}'
    location: location
    workspaceResourceId: logAnalytics.outputs.resourceId
  }
}

// === App Service ===
module webApp 'br/public:avm/res/web/site:0.19.4' = {
  name: 'webAppDeployment'
  params: {
    name: 'app-${workloadName}-${environment}'
    location: location
    serverFarmResourceId: appServicePlan.outputs.resourceId
    managedIdentities: {
      userAssignedResourceIds: [identity.outputs.resourceId]
    }
    keyVaultAccessIdentityResourceId: identity.outputs.resourceId
    siteConfig: {
      appSettings: [
        // SQL 接続 (Managed Identity 認証)
        {
          name: 'ConnectionStrings__DefaultConnection'
          value: 'Server=tcp:${sqlServer.outputs.fullyQualifiedDomainName},1433;Database=sqldb-${workloadName};Authentication=Active Directory Managed Identity;User Id=${identity.outputs.clientId};'
        }
        // Redis 接続 (Key Vault 参照)
        {
          name: 'ConnectionStrings__Redis'
          value: '@Microsoft.KeyVault(VaultName=${keyVault.outputs.name};SecretName=redis-connection)'
        }
        // Storage 接続 (Managed Identity 認証)
        {
          name: 'AzureStorage__BlobEndpoint'
          value: storage.outputs.primaryBlobEndpoint
        }
        // App Insights
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.outputs.connectionString
        }
      ]
    }
  }
}

// === Outputs ===
output webAppUrl string = 'https://${webApp.outputs.defaultHostName}'
output sqlServerFqdn string = sqlServer.outputs.fullyQualifiedDomainName
output storageEndpoint string = storage.outputs.primaryBlobEndpoint
```

---

## 接続文字列早見表

| サービス     | 接続方式         | 接続文字列形式                                                                                              |
| ------------ | ---------------- | ----------------------------------------------------------------------------------------------------------- |
| SQL Database | Managed Identity | `Server=tcp:{fqdn},1433;Database={db};Authentication=Active Directory Managed Identity;User Id={clientId};` |
| Storage Blob | Managed Identity | エンドポイント URL のみ + SDK で認証                                                                        |
| Redis        | 接続文字列       | `{host}:6380,password={key},ssl=True,abortConnect=False`                                                    |
| Cosmos DB    | Managed Identity | エンドポイント URL のみ + SDK で認証                                                                        |
| Event Hub    | 接続文字列       | `Endpoint=sb://{namespace}.servicebus.windows.net/;SharedAccessKeyName={keyName};SharedAccessKey={key}`     |
| Service Bus  | Managed Identity | エンドポイント URL のみ + SDK で認証                                                                        |
