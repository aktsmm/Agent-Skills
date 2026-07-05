<#
.SYNOPSIS
    Run-CustomerPptxPipeline.ps1 - Build/Enrich/Verify を単一 COM セッションで実行
.DESCRIPTION
    既存スクリプトの後方互換性を保ちつつ、PowerPoint COM の起動回数を削減します。
.PARAMETER DateFolder
    日付フォルダ（例: 0511）のパス
.PARAMETER SkipBuild
    Build をスキップして Enrich + Verify のみ実行
.PARAMETER SkipEnrich
    Enrich をスキップして Build + Verify のみ実行
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$DateFolder,

    [switch]$SkipBuild,
    [switch]$SkipEnrich
)

$ErrorActionPreference = "Stop"

Import-Module "$PSScriptRoot\PptxCommon.psm1" -Force

Write-StepHeader "Run-CustomerPptxPipeline.ps1"

$DateFolder = (Resolve-Path $DateFolder).Path
$basePath = Split-Path $DateFolder -Parent
$config = Get-Content "$basePath\.config\config.json" -Encoding UTF8 | ConvertFrom-Json
$dateString = Split-Path $DateFolder -Leaf
$outputFileName = $config.output.fileNamePattern -replace '\{year\}', $config.output.year -replace '\{date\}', $dateString
$outputPath = "$DateFolder\$outputFileName"
$manifestFolder = "$DateFolder\manifest"

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$ppt = $null

try {
    $ppt = New-PptxSession

    if (-not $SkipBuild) {
        Write-StepHeader "Build"
        & "$PSScriptRoot\Build-CustomerPptx.ps1" -DateFolder $DateFolder -Session $ppt -ClosePresentation
        if (-not $?) { throw "Build-CustomerPptx.ps1 failed" }
    }

    if (-not $SkipEnrich) {
        Write-StepHeader "Enrich"
        & "$PSScriptRoot\Enrich-CustomerPptx.ps1" -DateFolder $DateFolder -Session $ppt -ClosePresentation
        if (-not $?) { throw "Enrich-CustomerPptx.ps1 failed" }
    }

    Write-StepHeader "Verify"
    # COM セッション解放（Quit しない: ユーザーが開いている PowerPoint を閉じないため）
    if ($ppt) {
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
        $ppt = $null
    }
    $verifyLogPath = "$DateFolder\pipeline-verify.log"
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$PSScriptRoot\Verify-Pptx.ps1" -PptxPath $outputPath *> $verifyLogPath
    $verifyExitCode = $LASTEXITCODE

    $status = @{
        generatedAt = (Get-Date).ToString("s")
        script = "Run-CustomerPptxPipeline.ps1"
        pptxPath = $outputPath
        passed = ($verifyExitCode -eq 0)
        verifyExitCode = $verifyExitCode
        verifyLogPath = $verifyLogPath
        elapsedSeconds = [Math]::Round($stopwatch.Elapsed.TotalSeconds, 1)
        skippedBuild = [bool]$SkipBuild
        skippedEnrich = [bool]$SkipEnrich
    }
    $status | ConvertTo-Json -Depth 4 | Out-File "$manifestFolder\verify_status.json" -Encoding UTF8

    if ($verifyExitCode -ne 0) { throw "Verify-Pptx.ps1 failed" }
    $elapsedSeconds = [Math]::Round($stopwatch.Elapsed.TotalSeconds, 1)
    Write-Success "Pipeline 完了 ($elapsedSeconds 秒)"
} catch {
    Write-Failure "Pipeline エラー: $_"
    exit 1
} finally {
    if ($ppt) {
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
    }
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}

# 完了後に PowerPoint で開く（ユーザー確認用）
Start-Process $outputPath
exit 0
