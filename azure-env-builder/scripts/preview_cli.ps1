<#
.SYNOPSIS
    Azure CLI デプロイスクリプトの dry-run (WhatIf) ヘルパー。

.DESCRIPTION
    env/<environment>/cli/deploy.ps1 を -WhatIf モードで呼び出し、
    実行結果をログに保存します。

.PARAMETER Environment
    対象の環境名。

.EXAMPLE
    .\preview_cli.ps1 -Environment staging
#>

param (
    [Parameter(Mandatory = $true)]
    [string]$Environment
)

$ErrorActionPreference = "Stop"

# ============================================
# パスの定義
# ============================================
$repoRoot = (Get-Item (Split-Path $PSScriptRoot -Parent)).Parent.Parent.FullName
$envRoot = Join-Path $repoRoot "env" $Environment
$deployScript = Join-Path $envRoot "cli" "deploy.ps1"
$logsDir = Join-Path $envRoot "logs"

# ============================================
# 前提チェック
# ============================================
if (-not (Test-Path $deployScript)) {
    Write-Error "Deploy script not found: $deployScript"
    exit 1
}

if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
}

# ============================================
# Dry-Run 実行
# ============================================
Write-Host "[INFO] Running CLI deploy script in WhatIf mode..." -ForegroundColor Cyan
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logPath = Join-Path $logsDir "cli_preview_$timestamp.log"

try {
    $output = & pwsh -File $deployScript -WhatIf 2>&1
    $output | Out-File -FilePath $logPath -Encoding UTF8
    Write-Host "[INFO] Log saved to: $logPath" -ForegroundColor Cyan

    Write-Host ""
    Write-Host "========== CLI Preview Result ==========" -ForegroundColor Yellow
    $output | ForEach-Object { Write-Host $_ }
    Write-Host "=========================================" -ForegroundColor Yellow

    Write-Host ""
    Write-Host "[OK] CLI preview completed." -ForegroundColor Green
}
catch {
    Write-Error "CLI preview failed: $_"
    exit 1
}
