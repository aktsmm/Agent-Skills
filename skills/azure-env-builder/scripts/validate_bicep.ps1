<#
.SYNOPSIS
    Bicep ファイルの構文検証と what-if プレビューを実行します。

.PARAMETER Environment
    対象の環境名。

.PARAMETER ResourceGroupName
    デプロイ先のリソースグループ名 (ResourceGroup スコープの場合に使用)。

.PARAMETER DeploymentScope
    デプロイスコープ (ResourceGroup or Subscription)。
    省略時は scope.json から自動判定。

.PARAMETER WhatIf
    true の場合、実際のデプロイを行わず what-if のみ実行。

.EXAMPLE
    # リソースグループスコープ
    .\validate_bicep.ps1 -Environment staging -DeploymentScope ResourceGroup

    # サブスクリプションスコープ
    .\validate_bicep.ps1 -Environment prod -DeploymentScope Subscription
#>

param (
    [Parameter(Mandatory = $true)]
    [string]$Environment,

    [string]$ResourceGroupName,

    [ValidateSet("ResourceGroup", "Subscription")]
    [string]$DeploymentScope,

    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

# ============================================
# パスの定義
# ============================================
$repoRoot = (Get-Item (Split-Path $PSScriptRoot -Parent)).Parent.Parent.FullName
$envRoot = Join-Path $repoRoot "env" $Environment
$bicepDir = Join-Path $envRoot "bicep"
$mainBicep = Join-Path $bicepDir "main.bicep"
$paramFile = Join-Path $bicepDir "parameters" "$Environment.json"
$logsDir = Join-Path $envRoot "logs"

# ============================================
# 前提チェック
# ============================================
if (-not (Test-Path $mainBicep)) {
    Write-Error "Bicep file not found: $mainBicep"
    exit 1
}

if (-not (Test-Path $paramFile)) {
    Write-Warning "Parameter file not found: $paramFile. Proceeding without parameters."
    $paramFile = $null
}

# スコープの自動判定
$scopeConfigPath = Join-Path $bicepDir "scope.json"
if (-not $DeploymentScope) {
    if (Test-Path $scopeConfigPath) {
        $scopeConfig = Get-Content $scopeConfigPath -Raw | ConvertFrom-Json
        $DeploymentScope = $scopeConfig.deploymentScope
        Write-Host "[INFO] Detected deployment scope from scope.json: $DeploymentScope" -ForegroundColor Cyan
    } else {
        $DeploymentScope = "ResourceGroup"
        Write-Host "[INFO] No scope.json found. Defaulting to ResourceGroup scope." -ForegroundColor Yellow
    }
}

# ============================================
# Bicep ビルド (構文チェック)
# ============================================
Write-Host "[INFO] Building Bicep file..." -ForegroundColor Cyan
az bicep build --file $mainBicep --stdout | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Bicep build failed. Fix the errors above."
    exit 1
}
Write-Host "[OK] Bicep syntax is valid." -ForegroundColor Green

# ============================================
# What-If プレビュー
# ============================================

if ($DeploymentScope -eq "Subscription") {
    # サブスクリプションスコープ
    Write-Host "[INFO] Running what-if at Subscription scope..." -ForegroundColor Cyan

    $whatIfArgs = @(
        "deployment", "sub", "what-if",
        "--location", (Get-Content $scopeConfigPath -Raw | ConvertFrom-Json).location,
        "--template-file", $mainBicep
    )

    if ($paramFile) {
        $whatIfArgs += @("--parameters", $paramFile)
    }
} else {
    # リソースグループスコープ
    if (-not $ResourceGroupName) {
        # パラメータから location を読み取って自動生成
        $configPath = Join-Path (Split-Path $bicepDir -Parent) "cli" "config" "config.json"
        if (Test-Path $configPath) {
            $config = Get-Content $configPath -Raw | ConvertFrom-Json
            $ResourceGroupName = $config.resourceGroup
        } else {
            $ResourceGroupName = "rg-$Environment-001"
        }
    }

    Write-Host "[INFO] Running what-if against resource group: $ResourceGroupName" -ForegroundColor Cyan

    $whatIfArgs = @(
        "deployment", "group", "what-if",
        "--resource-group", $ResourceGroupName,
        "--template-file", $mainBicep
    )

    if ($paramFile) {
        $whatIfArgs += @("--parameters", $paramFile)
    }
}

$whatIfOutput = & az @whatIfArgs 2>&1
$exitCode = $LASTEXITCODE

# ログ保存
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logPath = Join-Path $logsDir "whatif_${DeploymentScope}_$timestamp.log"
$whatIfOutput | Out-File -FilePath $logPath -Encoding UTF8
Write-Host "[INFO] What-if log saved to: $logPath" -ForegroundColor Cyan

if ($exitCode -ne 0) {
    Write-Warning "What-if completed with warnings or errors. Review the log above."
} else {
    Write-Host "[OK] What-if completed successfully. (Scope: $DeploymentScope)" -ForegroundColor Green
}

# 出力表示
Write-Host ""
Write-Host "========== What-If Result ($DeploymentScope) ==========" -ForegroundColor Yellow
$whatIfOutput | ForEach-Object { Write-Host $_ }
Write-Host "====================================" -ForegroundColor Yellow
