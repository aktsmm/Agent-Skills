<#
.SYNOPSIS
    環境ごとのフォルダ構造と初期テンプレートを生成します。

.PARAMETER Environment
    環境名 (例: dev, staging, prod)。

.PARAMETER Location
    Azure リージョン (例: japaneast, eastus)。

.PARAMETER DeploymentMode
    デプロイ方式 (CLI or Bicep or Both)。

.PARAMETER DeploymentScope
    デプロイスコープ (ResourceGroup or Subscription)。
    - ResourceGroup: 既存のリソースグループにデプロイ。
    - Subscription: サブスクリプションレベルでリソースグループ作成から管理。

.EXAMPLE
    # リソースグループスコープ
    .\scaffold_environment.ps1 -Environment staging -Location japaneast -DeploymentMode Bicep -DeploymentScope ResourceGroup

    # サブスクリプションスコープ
    .\scaffold_environment.ps1 -Environment prod -Location japaneast -DeploymentMode Bicep -DeploymentScope Subscription
#>

param (
    [Parameter(Mandatory = $true)]
    [string]$Environment,

    [Parameter(Mandatory = $true)]
    [string]$Location,

    [Parameter(Mandatory = $true)]
    [ValidateSet("CLI", "Bicep", "Both")]
    [string]$DeploymentMode,

    [Parameter(Mandatory = $false)]
    [ValidateSet("ResourceGroup", "Subscription")]
    [string]$DeploymentScope = "ResourceGroup"
)

# ============================================
# パスの定義
# ============================================
$repoRoot = (Get-Item (Split-Path $PSScriptRoot -Parent)).Parent.Parent.FullName
$envRoot = Join-Path $repoRoot "env" $Environment
$cliDir = Join-Path $envRoot "cli"
$bicepDir = Join-Path $envRoot "bicep"
$paramsDir = Join-Path $bicepDir "parameters"
$configDir = Join-Path $cliDir "config"
$logsDir = Join-Path $envRoot "logs"

# ============================================
# ディレクトリ作成
# ============================================
Write-Host "[INFO] Creating folder structure for environment: $Environment" -ForegroundColor Cyan

New-Item -ItemType Directory -Force -Path $envRoot | Out-Null
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null

if ($DeploymentMode -in @("CLI", "Both")) {
    New-Item -ItemType Directory -Force -Path $cliDir | Out-Null
    New-Item -ItemType Directory -Force -Path $configDir | Out-Null
}

if ($DeploymentMode -in @("Bicep", "Both")) {
    New-Item -ItemType Directory -Force -Path $bicepDir | Out-Null
    New-Item -ItemType Directory -Force -Path $paramsDir | Out-Null
}

# ============================================
# テンプレートファイルの生成
# ============================================

# README.md (環境テンプレートのコピー)
$templatePath = Join-Path $PSScriptRoot ".." "references" "environment-template.md"
$readmePath = Join-Path $envRoot "README.md"
if (Test-Path $templatePath) {
    Copy-Item $templatePath $readmePath -Force
    (Get-Content $readmePath) -replace '<!-- dev / staging / prod など -->', $Environment `
        -replace '<!-- japaneast / japanwest など -->', $Location | Set-Content $readmePath
    Write-Host "[INFO] README.md generated at $readmePath" -ForegroundColor Green
} else {
    Write-Warning "Template not found: $templatePath. Skipping README generation."
}

# CLI デプロイスクリプト
if ($DeploymentMode -in @("CLI", "Both")) {
    $cliScriptContent = @"
<#
.SYNOPSIS
    $Environment 環境への Azure CLI デプロイスクリプト

.DESCRIPTION
    このスクリプトはリソースグループの作成と関連リソースのデプロイを行います。

.PARAMETER WhatIf
    dry-run モードで実行し、実際のデプロイを行いません。
#>
param (
    [switch]`$WhatIf
)

`$ErrorActionPreference = "Stop"

# 設定読み込み
`$configPath = Join-Path `$PSScriptRoot "config" "config.json"
`$config = Get-Content `$configPath -Raw | ConvertFrom-Json

# リソースグループ名・リージョン
`$resourceGroup = "rg-$Environment-$Location-001"
`$location = "$Location"

Write-Host "[INFO] Target Resource Group: `$resourceGroup" -ForegroundColor Cyan
Write-Host "[INFO] Location: `$location" -ForegroundColor Cyan

if (`$WhatIf) {
    Write-Host "[WHATIF] Would create resource group `$resourceGroup" -ForegroundColor Yellow
    # 他のリソースについても同様に WhatIf 出力
} else {
    az group create --name `$resourceGroup --location `$location --output table
    # TODO: 必要なリソースの az コマンドを追加
}

Write-Host "[INFO] Deployment script completed." -ForegroundColor Green
"@
    $cliScriptPath = Join-Path $cliDir "deploy.ps1"
    Set-Content -Path $cliScriptPath -Value $cliScriptContent -Encoding UTF8
    Write-Host "[INFO] deploy.ps1 generated at $cliScriptPath" -ForegroundColor Green

    # config.json
    $configContent = @{
        environment   = $Environment
        location      = $Location
        resourceGroup = "rg-$Environment-$Location-001"
        tags          = @{
            Environment = $Environment
            ManagedBy   = "azure-env-builder"
        }
    } | ConvertTo-Json -Depth 3
    $configFilePath = Join-Path $configDir "config.json"
    Set-Content -Path $configFilePath -Value $configContent -Encoding UTF8
    Write-Host "[INFO] config.json generated at $configFilePath" -ForegroundColor Green
}

# Bicep ファイル
if ($DeploymentMode -in @("Bicep", "Both")) {
    # modules フォルダ作成 (Subscription スコープ用)
    $modulesDir = Join-Path $bicepDir "modules"
    if ($DeploymentScope -eq "Subscription") {
        New-Item -ItemType Directory -Force -Path $modulesDir | Out-Null
    }

    if ($DeploymentScope -eq "Subscription") {
        # ============================================
        # Subscription スコープ用 Bicep テンプレート
        # ============================================
        $bicepContent = @"
// ============================================
// main.bicep - $Environment 環境 (Subscription Scope)
// ============================================

targetScope = 'subscription'

// パラメータ
param location string = '$Location'
param environment string = '$Environment'
param tags object = {
  Environment: environment
  ManagedBy: 'azure-env-builder'
}

// ============================================
// リソースグループ作成
// ============================================
var resourceGroupName = 'rg-`${environment}-`${location}-001'

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

// ============================================
// モジュール参照 (リソースグループ内リソース)
// ============================================
module resources './modules/resources.bicep' = {
  scope: rg
  name: 'resourcesDeployment-`${environment}'
  params: {
    location: location
    environment: environment
    tags: tags
  }
}

// 出力
output resourceGroupName string = rg.name
output resourceGroupId string = rg.id
"@
        # modules/resources.bicep
        $resourcesModuleContent = @"
// ============================================
// resources.bicep - リソースグループ内リソース
// ============================================

// パラメータ
param location string
param environment string
param tags object

// ============================================
// リソース定義 (例: Storage Account)
// ============================================
var storageAccountName = 'st`${environment}`${uniqueString(resourceGroup().id)}'

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

// TODO: 必要なリソースを追加

output storageAccountName string = storageAccount.name
"@
        $modulePath = Join-Path $modulesDir "resources.bicep"
        Set-Content -Path $modulePath -Value $resourcesModuleContent -Encoding UTF8
        Write-Host "[INFO] resources.bicep generated at $modulePath" -ForegroundColor Green

    } else {
        # ============================================
        # ResourceGroup スコープ用 Bicep テンプレート (従来)
        # ============================================
        $bicepContent = @"
// ============================================
// main.bicep - $Environment 環境
// ============================================

targetScope = 'resourceGroup'

// パラメータ
param location string = '$Location'
param environment string = '$Environment'
param tags object = {
  Environment: environment
  ManagedBy: 'azure-env-builder'
}

// ============================================
// リソース定義 (例: Storage Account)
// ============================================
var storageAccountName = 'st`${environment}`${uniqueString(resourceGroup().id)}'

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

// TODO: 必要なリソースを追加

output storageAccountName string = storageAccount.name
"@
    }

    $bicepPath = Join-Path $bicepDir "main.bicep"
    Set-Content -Path $bicepPath -Value $bicepContent -Encoding UTF8
    Write-Host "[INFO] main.bicep generated at $bicepPath (Scope: $DeploymentScope)" -ForegroundColor Green

    # パラメータファイル (スコープに応じてスキーマを変更)
    if ($DeploymentScope -eq "Subscription") {
        $paramContent = @{
            "`$schema"       = "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#"
            "contentVersion" = "1.0.0.0"
            "parameters"     = @{
                "location"    = @{ "value" = $Location }
                "environment" = @{ "value" = $Environment }
            }
        } | ConvertTo-Json -Depth 4
    } else {
        $paramContent = @{
            "`$schema"       = "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#"
            "contentVersion" = "1.0.0.0"
            "parameters"     = @{
                "location"    = @{ "value" = $Location }
                "environment" = @{ "value" = $Environment }
            }
        } | ConvertTo-Json -Depth 4
    }
    $paramPath = Join-Path $paramsDir "$Environment.json"
    Set-Content -Path $paramPath -Value $paramContent -Encoding UTF8
    Write-Host "[INFO] $Environment.json generated at $paramPath" -ForegroundColor Green

    # デプロイスコープをconfig.jsonに保存
    $scopeConfigPath = Join-Path $bicepDir "scope.json"
    $scopeConfig = @{
        deploymentScope = $DeploymentScope
        location        = $Location
        environment     = $Environment
    } | ConvertTo-Json -Depth 2
    Set-Content -Path $scopeConfigPath -Value $scopeConfig -Encoding UTF8
    Write-Host "[INFO] scope.json generated at $scopeConfigPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "[DONE] Environment '$Environment' scaffolded successfully! (Scope: $DeploymentScope)" -ForegroundColor Green
Write-Host "       Path: $envRoot" -ForegroundColor White
