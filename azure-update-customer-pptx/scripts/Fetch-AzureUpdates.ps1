<#
.SYNOPSIS
    Azure Updates 取得ワークフローの差分管理（state）ヘルパー。

.DESCRIPTION
    MCP 呼び出し自体は AI（Fetch エージェント）が行う。本スクリプトは決定論的な
    「取得範囲の決定」と「処理済み id の記録」だけを担当する。

    Plan モード:   取得すべき日付範囲と除外すべき処理済み id を JSON で出力する。
    Commit モード: fetched-updates.json の id を processed-updates.json に追記する。

.PARAMETER DateFolder
    出力先の日付フォルダ（例 0624 / test-3day）。manifest/ がこの配下に作られる。

.PARAMETER Mode
    Plan | Commit

.PARAMETER From / To
    明示範囲（ISO 日付 yyyy-MM-dd）。指定時は最優先。

.PARAMETER Days
    フォールバック日数（既定 14）。履歴も明示範囲も無いときに使う。

.EXAMPLE
    ./Fetch-AzureUpdates.ps1 -DateFolder test-3day -Mode Plan -Days 3
    ./Fetch-AzureUpdates.ps1 -DateFolder test-3day -Mode Commit
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $DateFolder,
    [ValidateSet('Plan', 'Commit')] [string] $Mode = 'Plan',
    [string] $From,
    [string] $To,
    [int] $Days = 14
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$configDir = Join-Path $repoRoot 'config'
$statePath = Join-Path $configDir 'processed-updates.json'
$manifestDir = Join-Path $repoRoot (Join-Path $DateFolder 'manifest')
$fetchedPath = Join-Path $manifestDir 'fetched-updates.json'

if (-not (Test-Path $configDir)) { New-Item -ItemType Directory -Path $configDir -Force | Out-Null }

function Get-State {
    if (Test-Path $statePath) {
        try {
            $raw = Get-Content $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
            return $raw
        }
        catch {
            Write-Warning "processed-updates.json の読込に失敗。空 state として扱います: $($_.Exception.Message)"
        }
    }
    return [pscustomobject]@{ processedIds = @(); lastRunUtc = $null; lastCreatedCutoff = $null }
}

if ($Mode -eq 'Plan') {
    $state = Get-State
    $processedIds = @($state.processedIds)

    # 範囲決定の優先順位: 明示範囲 > 履歴差分 > Days フォールバック
    $todayUtc = (Get-Date).ToUniversalTime().Date
    if ($From) {
        $createdFrom = $From
        $createdTo = if ($To) { $To } else { $todayUtc.ToString('yyyy-MM-dd') }
        $basis = 'explicit-range'
    }
    elseif ($processedIds.Count -gt 0 -and $state.lastCreatedCutoff) {
        # 履歴あり: 前回 cutoff 以降を取得し、id で重複排除する
        $createdFrom = ([datetime]$state.lastCreatedCutoff).ToString('yyyy-MM-dd')
        $createdTo = $todayUtc.ToString('yyyy-MM-dd')
        $basis = 'incremental-since-last'
    }
    else {
        $createdFrom = $todayUtc.AddDays(-$Days).ToString('yyyy-MM-dd')
        $createdTo = $todayUtc.ToString('yyyy-MM-dd')
        $basis = "fallback-$Days-days"
    }

    if (-not (Test-Path $manifestDir)) { New-Item -ItemType Directory -Path $manifestDir -Force | Out-Null }

    $plan = [ordered]@{
        dateFolder       = $DateFolder
        basis            = $basis
        createdFrom      = $createdFrom
        createdTo        = $createdTo
        odataCreatedFrom = "$($createdFrom)T00:00:00Z"
        odataCreatedTo   = "$($createdTo)T23:59:59Z"
        excludeIds       = $processedIds
        fetchedPath      = (Resolve-Path -Relative $fetchedPath -ErrorAction SilentlyContinue) ?? $fetchedPath
        instructions     = "mcp_releasecommun_get_recent_azure_updates を created ge '$($createdFrom)T00:00:00Z' and created le '$($createdTo)T23:59:59Z' で取得し、excludeIds を除外。詳細は get_azure_update_by_id。正規化して fetched-updates.json へ。スキーマは .github/skills/azure-update-customer-pptx/references/mcp-sourced-content.md を参照。"
    }
    $plan | ConvertTo-Json -Depth 6
    return
}

if ($Mode -eq 'Commit') {
    if (-not (Test-Path $fetchedPath)) {
        throw "fetched-updates.json が見つかりません: $fetchedPath"
    }
    $fetched = Get-Content $fetchedPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $newIds = @($fetched | ForEach-Object { "$($_.id)" } | Where-Object { $_ })

    $state = Get-State
    $merged = @($state.processedIds) + $newIds | Where-Object { $_ } | Select-Object -Unique

    # 最新 created を cutoff として保存（次回 incremental の起点）
    $maxCreated = $null
    $createdValues = @($fetched | ForEach-Object { $_.created } | Where-Object { $_ })
    if ($createdValues.Count -gt 0) {
        $maxCreated = ($createdValues | Sort-Object -Descending | Select-Object -First 1)
    }

    $newState = [ordered]@{
        processedIds      = @($merged)
        lastRunUtc        = (Get-Date).ToUniversalTime().ToString('o')
        lastCreatedCutoff = $maxCreated
    }
    $newState | ConvertTo-Json -Depth 4 | Set-Content -Path $statePath -Encoding UTF8
    Write-Host "Committed $($newIds.Count) ids. processed-updates.json total = $($merged.Count)."
    return
}
