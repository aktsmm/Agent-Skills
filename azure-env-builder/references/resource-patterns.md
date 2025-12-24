# リソースパターン

#microsoft.docs.mcp 公式サンプルから抽出した Bicep パターン。

## 目次

1. [監視・可観測性](#監視可観測性)
2. [ネットワーク](#ネットワーク)
3. [コンピュート](#コンピュート)
4. [DR・バックアップ](#drバックアップ)
5. [データサービス](#データサービス)

---

## 監視・可観測性

### Log Analytics Workspace

**Source:** https://learn.microsoft.com/en-us/azure/azure-monitor/logs/quick-create-workspace

```bicep
// Log Analytics Workspace の作成
@description('Log Analytics workspace name')
param workspaceName string

@description('Pricing tier (PerGB2018 recommended)')
param sku string = 'PerGB2018'

@description('Location')
param location string = resourceGroup().location

@description('Data retention in days')
param retentionInDays int = 30

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: workspaceName
  location: location
  properties: {
    sku: {
      name: sku
    }
    retentionInDays: retentionInDays
    features: {
      searchVersion: 1
    }
  }
}

output workspaceId string = logAnalyticsWorkspace.id
output customerId string = logAnalyticsWorkspace.properties.customerId
```

### Diagnostic Settings (Activity Log)

**Source:** https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/scenarios-monitoring#diagnostic-settings

```bicep
// サブスクリプションレベルの診断設定
targetScope = 'subscription'

@description('Log Analytics workspace resource ID')
param logAnalyticsWorkspaceId string

var activityLogDiagnosticSettingsName = 'export-activity-log'

resource subscriptionActivityLog 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: activityLogDiagnosticSettingsName
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      { category: 'Administrative', enabled: true }
      { category: 'Security', enabled: true }
      { category: 'ServiceHealth', enabled: true }
      { category: 'Alert', enabled: true }
      { category: 'Recommendation', enabled: true }
      { category: 'Policy', enabled: true }
      { category: 'Autoscale', enabled: true }
      { category: 'ResourceHealth', enabled: true }
    ]
  }
}
```

---

## ネットワーク

### ExpressRoute Gateway

**Source:** https://learn.microsoft.com/en-us/azure/expressroute/quickstart-create-expressroute-vnet-bicep

```bicep
// ExpressRoute 回線 + ゲートウェイ構成
@description('ExpressRoute Gateway SKU')
@allowed(['Standard', 'HighPerformance', 'UltraPerformance', 'ErGw1AZ', 'ErGw2AZ', 'ErGw3AZ'])
param gatewaySku string = 'HighPerformance'

@description('Virtual network name')
param vnetName string

@description('Gateway subnet prefix (must be /27 or larger)')
param gatewaySubnetPrefix string = '10.10.10.224/27'

@description('Location')
param location string = resourceGroup().location

// VNet は既存を参照
resource vnet 'Microsoft.Network/virtualNetworks@2023-09-01' existing = {
  name: vnetName
}

resource gatewayPublicIP 'Microsoft.Network/publicIPAddresses@2023-09-01' = {
  name: '${vnetName}-ergw-pip'
  location: location
  sku: {
    name: 'Standard'
    tier: 'Regional'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}

resource gateway 'Microsoft.Network/virtualNetworkGateways@2023-09-01' = {
  name: '${vnetName}-ergw'
  location: location
  properties: {
    ipConfigurations: [
      {
        name: 'gwIPconf'
        properties: {
          privateIPAllocationMethod: 'Dynamic'
          subnet: {
            id: resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, 'GatewaySubnet')
          }
          publicIPAddress: {
            id: gatewayPublicIP.id
          }
        }
      }
    ]
    gatewayType: 'ExpressRoute'
    sku: {
      name: gatewaySku
      tier: gatewaySku
    }
    vpnType: 'RouteBased'
  }
}

output gatewayName string = gateway.name
```

### VPN Gateway (Site-to-Site)

**Source:** https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-howto-site-to-site-resource-manager-cli

```bicep
// VPN Gateway for S2S connection
@description('VPN Gateway SKU')
@allowed(['VpnGw1', 'VpnGw2', 'VpnGw2AZ', 'VpnGw3', 'VpnGw3AZ'])
param vpnGatewaySku string = 'VpnGw2AZ'

@description('Virtual network name')
param vnetName string

@description('Location')
param location string = resourceGroup().location

resource vpnGatewayPip 'Microsoft.Network/publicIPAddresses@2023-09-01' = {
  name: '${vnetName}-vpngw-pip'
  location: location
  sku: {
    name: 'Standard'
  }
  zones: ['1', '2', '3']
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}

resource vpnGateway 'Microsoft.Network/virtualNetworkGateways@2023-09-01' = {
  name: '${vnetName}-vpngw'
  location: location
  properties: {
    gatewayType: 'Vpn'
    vpnType: 'RouteBased'
    sku: {
      name: vpnGatewaySku
      tier: vpnGatewaySku
    }
    ipConfigurations: [
      {
        name: 'vpngwipconfig'
        properties: {
          privateIPAllocationMethod: 'Dynamic'
          subnet: {
            id: resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, 'GatewaySubnet')
          }
          publicIPAddress: {
            id: vpnGatewayPip.id
          }
        }
      }
    ]
    enableBgp: false
  }
}
```

---

## コンピュート

### AKS (Private Cluster)

**Source:** https://learn.microsoft.com/en-us/azure/aks/private-clusters

```bicep
// AKS Private Cluster
@description('AKS cluster name')
param clusterName string = 'aksprivate'

@description('Location')
param location string = resourceGroup().location

@description('Kubernetes version')
param kubernetesVersion string = '1.30'

@description('Node count')
param nodeCount int = 3

@description('Node size')
param nodeSize string = 'Standard_D4s_v3'

resource aksCluster 'Microsoft.ContainerService/managedClusters@2024-02-01' = {
  name: clusterName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    dnsPrefix: clusterName
    kubernetesVersion: kubernetesVersion
    networkProfile: {
      networkPlugin: 'azure'
    }
    apiServerAccessProfile: {
      enablePrivateCluster: true
    }
    agentPoolProfiles: [
      {
        name: 'systempool'
        count: nodeCount
        vmSize: nodeSize
        mode: 'System'
        enableAutoScaling: true
        minCount: 1
        maxCount: 5
      }
    ]
  }
}

output clusterFqdn string = aksCluster.properties.fqdn
```

### Container Apps Environment

**Source:** https://learn.microsoft.com/en-us/azure/container-apps/managed-identity-image-pull

```bicep
// Container Apps Environment with Log Analytics
@description('Environment name')
param environmentName string

@description('Log Analytics workspace name')
param logAnalyticsName string

@description('Location')
param location string = resourceGroup().location

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    retentionInDays: 30
    sku: {
      name: 'PerGB2018'
    }
  }
}

resource appEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: environmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
  }
}

output environmentId string = appEnvironment.id
```

### App Service (Linux)

**Source:** https://learn.microsoft.com/en-us/azure/app-service/provision-resource-bicep

```bicep
// App Service on Linux
@description('Web app name')
param webAppName string = uniqueString(resourceGroup().id)

@description('App Service plan SKU')
param sku string = 'P1v3'

@description('Runtime stack')
param linuxFxVersion string = 'DOTNETCORE|8.0'

@description('Location')
param location string = resourceGroup().location

var appServicePlanName = toLower('asp-${webAppName}')

resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: appServicePlanName
  location: location
  kind: 'linux'
  sku: {
    name: sku
  }
  properties: {
    reserved: true // Linux の場合は true
  }
}

resource appService 'Microsoft.Web/sites@2023-12-01' = {
  name: webAppName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: linuxFxVersion
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
    }
  }
  identity: {
    type: 'SystemAssigned'
  }
}

output appUrl string = 'https://${appService.properties.defaultHostName}'
```

---

## DR・バックアップ

### Recovery Services Vault

**Source:** https://learn.microsoft.com/en-us/azure/site-recovery/quickstart-create-vault-bicep

```bicep
// Recovery Services Vault for Azure Backup & Site Recovery
@description('Vault name')
param vaultName string

@description('Enable Cross Region Restore')
param enableCRR bool = true

@description('Storage redundancy type')
@allowed(['LocallyRedundant', 'GeoRedundant'])
param vaultStorageType string = 'GeoRedundant'

@description('Location')
param location string = resourceGroup().location

resource recoveryServicesVault 'Microsoft.RecoveryServices/vaults@2022-02-01' = {
  name: vaultName
  location: location
  sku: {
    name: 'RS0'
    tier: 'Standard'
  }
  properties: {}
}

resource vaultStorageConfig 'Microsoft.RecoveryServices/vaults/backupstorageconfig@2022-02-01' = {
  parent: recoveryServicesVault
  name: 'vaultstorageconfig'
  properties: {
    storageModelType: vaultStorageType
    crossRegionRestoreFlag: enableCRR
  }
}

output vaultId string = recoveryServicesVault.id
```

### Vault Diagnostic Settings

**Source:** https://learn.microsoft.com/en-us/azure/azure-monitor/platform/resource-manager-diagnostic-settings

```bicep
// Recovery Services Vault with diagnostic settings
@description('Recovery Services vault name')
param vaultName string

@description('Log Analytics workspace ID')
param workspaceId string

resource vault 'Microsoft.RecoveryServices/vaults@2021-08-01' existing = {
  name: vaultName
}

resource vaultDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${vaultName}-diag'
  scope: vault
  properties: {
    workspaceId: workspaceId
    logs: [
      { category: 'CoreAzureBackup', enabled: true }
      { category: 'AddonAzureBackupJobs', enabled: true }
      { category: 'AddonAzureBackupAlerts', enabled: true }
      { category: 'AddonAzureBackupPolicy', enabled: true }
      { category: 'AddonAzureBackupStorage', enabled: true }
      { category: 'AddonAzureBackupProtectedInstance', enabled: true }
    ]
    logAnalyticsDestinationType: 'Dedicated'
  }
}
```

---

## Azure CLI 参考コマンド

```bash
# リソースグループ作成
az group create --name $RG_NAME --location $LOCATION

# AKS Private Cluster 作成
az aks create \
  --resource-group $RG_NAME \
  --name myPrivateCluster \
  --enable-private-cluster \
  --network-plugin azure \
  --generate-ssh-keys

# VPN Gateway 作成
az network vnet-gateway create \
  --name MyVnetGateway \
  --resource-group $RG_NAME \
  --vnet MyVnet \
  --gateway-type Vpn \
  --vpn-type RouteBased \
  --sku VpnGw2AZ

# Recovery Services Vault 作成
az backup vault create \
  --resource-group $RG_NAME \
  --name myRecoveryVault \
  --location $LOCATION
```

---

## データサービス

### Azure SQL Database

**Source:** https://learn.microsoft.com/en-us/azure/azure-sql/database/single-database-create-bicep-quickstart

```bicep
// Azure SQL Database (シンプル構成)
@description('SQL Server name')
param serverName string = uniqueString('sql', resourceGroup().id)

@description('SQL Database name')
param sqlDBName string = 'SampleDB'

@description('Location')
param location string = resourceGroup().location

@description('Administrator login')
param administratorLogin string

@description('Administrator password')
@secure()
param administratorLoginPassword string

// SQL Server
resource sqlServer 'Microsoft.Sql/servers@2022-05-01-preview' = {
  name: serverName
  location: location
  properties: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
  }
}

// SQL Database
resource sqlDB 'Microsoft.Sql/servers/databases@2022-05-01-preview' = {
  parent: sqlServer
  name: sqlDBName
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
}
```

### Azure SQL Database with Private Endpoint

**Source:** https://learn.microsoft.com/en-us/azure/private-link/create-private-endpoint-bicep

```bicep
// Private Endpoint 付き SQL Database
@description('SQL administrator login')
param sqlAdministratorLogin string

@secure()
param sqlAdministratorLoginPassword string

@description('Location')
param location string = resourceGroup().location

var sqlServerName = 'sqlserver${uniqueString(resourceGroup().id)}'
var privateDnsZoneName = 'privatelink${environment().suffixes.sqlServerHostname}'
var privateEndpointName = 'sqlPrivateEndpoint'

// SQL Server (Public Network Access 無効)
resource sqlServer 'Microsoft.Sql/servers@2021-11-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: sqlAdministratorLogin
    administratorLoginPassword: sqlAdministratorLoginPassword
    version: '12.0'
    publicNetworkAccess: 'Disabled'
  }
}

// Private Endpoint
resource privateEndpoint 'Microsoft.Network/privateEndpoints@2021-05-01' = {
  name: privateEndpointName
  location: location
  properties: {
    subnet: {
      id: subnet.id
    }
    privateLinkServiceConnections: [
      {
        name: privateEndpointName
        properties: {
          privateLinkServiceId: sqlServer.id
          groupIds: ['sqlServer']
        }
      }
    ]
  }
}

// Private DNS Zone
resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: privateDnsZoneName
  location: 'global'
}
```

### Azure Cosmos DB

**Source:** https://learn.microsoft.com/en-us/azure/cosmos-db/manage-with-bicep

```bicep
// Cosmos DB Account (Autoscale構成)
@description('Cosmos DB account name')
param accountName string = 'sql-${uniqueString(resourceGroup().id)}'

@description('Location')
param location string = resourceGroup().location

@description('Primary region')
param primaryRegion string

@description('Secondary region')
param secondaryRegion string

@description('Database name')
param databaseName string

@description('Container name')
param containerName string

@description('Max autoscale throughput')
@minValue(1000)
@maxValue(1000000)
param autoscaleMaxThroughput int = 1000

var locations = [
  { locationName: primaryRegion, failoverPriority: 0, isZoneRedundant: false }
  { locationName: secondaryRegion, failoverPriority: 1, isZoneRedundant: false }
]

// Cosmos DB Account
resource account 'Microsoft.DocumentDB/databaseAccounts@2022-05-15' = {
  name: toLower(accountName)
  kind: 'GlobalDocumentDB'
  location: location
  properties: {
    consistencyPolicy: { defaultConsistencyLevel: 'Session' }
    locations: locations
    databaseAccountOfferType: 'Standard'
    enableAutomaticFailover: true
  }
}

// Database
resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2022-05-15' = {
  parent: account
  name: databaseName
  properties: {
    resource: { id: databaseName }
  }
}

// Container with Autoscale
resource container 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2022-05-15' = {
  parent: database
  name: containerName
  properties: {
    resource: {
      id: containerName
      partitionKey: { paths: ['/myPartitionKey'], kind: 'Hash' }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [{ path: '/*' }]
        excludedPaths: [{ path: '/_etag/?' }]
      }
    }
    options: {
      autoscaleSettings: { maxThroughput: autoscaleMaxThroughput }
    }
  }
}
```

### Azure Cache for Redis

**Source:** https://learn.microsoft.com/en-us/azure/redis/redis-cache-bicep-provision

```bicep
// Azure Cache for Redis
@description('Redis cache name')
param redisCacheName string = 'redisCache-${uniqueString(resourceGroup().id)}'

@description('Location')
param location string = resourceGroup().location

@description('SKU: Basic, Standard, Premium')
@allowed(['Basic', 'Standard', 'Premium'])
param redisCacheSKU string = 'Standard'

@description('SKU Family: C = Basic/Standard, P = Premium')
@allowed(['C', 'P'])
param redisCacheFamily string = 'C'

@description('Cache size (0-6 for C family, 1-5 for P family)')
@allowed([0, 1, 2, 3, 4, 5, 6])
param redisCacheCapacity int = 1

resource redisCache 'Microsoft.Cache/redis@2023-08-01' = {
  name: redisCacheName
  location: location
  properties: {
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
    sku: {
      capacity: redisCacheCapacity
      family: redisCacheFamily
      name: redisCacheSKU
    }
    redisConfiguration: {
      'aad-enabled': 'true'
    }
  }
}

output redisHostName string = redisCache.properties.hostName
```

### Azure Managed Redis (Enterprise)

**Source:** https://learn.microsoft.com/en-us/azure/redis/redis-cache-bicep-provision

```bicep
// Azure Managed Redis (Enterprise)
@description('Redis cache name')
param redisCacheName string = 'redisCache-${uniqueString(resourceGroup().id)}'

@description('Location')
param location string = resourceGroup().location

resource redisEnterprise 'Microsoft.Cache/redisEnterprise@2024-05-01-preview' = {
  name: redisCacheName
  location: location
  sku: { name: 'Balanced_B5' }
  identity: { type: 'None' }
  properties: { minimumTlsVersion: '1.2' }
}

resource redisEnterpriseDatabase 'Microsoft.Cache/redisEnterprise/databases@2024-05-01-preview' = {
  name: 'default'
  parent: redisEnterprise
  properties: {
    clientProtocol: 'Encrypted'
    port: 10000
    clusteringPolicy: 'OSSCluster'
    evictionPolicy: 'NoEviction'
    persistence: { aofEnabled: false, rdbEnabled: false }
  }
}
```

---

## MCP ツール活用例

最新のスキーマ・サンプルを取得する:

```python
# リソース型のスキーマを取得
mcp_bicep_experim_get_az_resource_type_schema(
    azResourceType="Microsoft.ContainerService/managedClusters"
)

# 公式 Bicep サンプルを検索
mcp_microsoft_docs_microsoft_code_sample_search(
    query="AKS private cluster Bicep",
    language="bicep"
)

# Azure Verified Modules を検索
mcp_bicep_experim_list_avm_metadata()
```

---

## 参考リンク

- [Azure Bicep 公式ドキュメント](https://learn.microsoft.com/ja-jp/azure/azure-resource-manager/bicep/)
- [Azure Verified Modules](https://azure.github.io/Azure-Verified-Modules/)
- [Azure QuickStart Templates](https://github.com/Azure/azure-quickstart-templates)
