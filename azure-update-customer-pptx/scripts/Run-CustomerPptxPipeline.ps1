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
    [switch]$SkipEnrich,

    [ValidateSet("", "com", "python")]
    [string]$Engine = "",

    [switch]$NoOpen
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
$logsFolder = "$DateFolder\logs"
$statusPath = "$manifestFolder\verify_status.json"
$runId = [guid]::NewGuid().ToString()
$selectedEngine = if ($Engine) { $Engine } elseif ($config.build -and $config.build.engine) { [string]$config.build.engine } else { "com" }
$effectiveSkipEnrich = [bool]$SkipEnrich -or $selectedEngine -eq "python"
$resultKey = [System.IO.Path]::GetRelativePath($basePath, $outputPath).Normalize([Text.NormalizationForm]::FormC).ToLowerInvariant()

New-Item -ItemType Directory -Force -Path $manifestFolder, $logsFolder | Out-Null

function Get-FileSha256OrEmpty {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return "" }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
}

function Write-PipelineStatus {
    param(
        [string]$State,
        [string]$Phase,
        [bool]$Passed,
        [string]$ErrorSummary = "",
        [int]$VerifyExitCode = -1,
        [string]$VerifyLogPath = ""
    )
    $document = [ordered]@{ schemaVersion = 2; aggregatePassed = $false; results = [ordered]@{} }
    if (Test-Path -LiteralPath $statusPath) {
        try {
            $existing = Get-Content -LiteralPath $statusPath -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
            if ($existing.schemaVersion -eq 2 -and $existing.results) { $document = $existing }
        } catch {}
    }
    $document.results[$resultKey] = [ordered]@{
        runId = $runId
        state = $State
        phase = $Phase
        requestedEngine = $selectedEngine
        actualEngine = $selectedEngine
        engineVersion = if ($selectedEngine -eq "python") { "1.0.0" } else { "legacy-com" }
        templateContractVersion = if ($config.build -and $config.build.templateContractVersion) { [int]$config.build.templateContractVersion } else { 1 }
        passed = $Passed
        pptxPath = $outputPath
        outputHash = Get-FileSha256OrEmpty -Path $outputPath
        generatedAt = (Get-Date).ToString("o")
        verifyExitCode = $VerifyExitCode
        verifyLogPath = $VerifyLogPath
        error = $ErrorSummary
        skippedBuild = [bool]$SkipBuild
        skippedEnrich = $effectiveSkipEnrich
    }
    $document.aggregatePassed = @($document.results.Values | Where-Object { -not $_.passed }).Count -eq 0
    $temporaryStatus = "$statusPath.$runId.tmp"
    $document | ConvertTo-Json -Depth 8 | Out-File $temporaryStatus -Encoding UTF8
    Move-Item -LiteralPath $temporaryStatus -Destination $statusPath -Force
}

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$ppt = $null
$currentPhase = "preflight"
Write-PipelineStatus -State "started" -Phase $currentPhase -Passed $false

# 対象 PPTX が PowerPoint で開いたままだと、COM 上書きとクラウド同期の自動保存が競合し、
# 競合マージで Weekly スライドの二重化やセクション消失を起こす。開いていれば保存せず閉じる。
$existingApp = Get-ActivePptxApplication
if ($existingApp) {
    try {
        if (Close-OpenPptxPresentation -Application $existingApp -PptxPath $outputPath) {
            Write-Info "開いていた対象 PPTX を閉じました: $outputPath"
        }
    }
    finally {
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($existingApp) | Out-Null
    }
}

try {
    if (-not $SkipBuild) {
        $currentPhase = "build"
        Write-PipelineStatus -State "started" -Phase $currentPhase -Passed $false
        Write-StepHeader "Build"
        if ($selectedEngine -eq "python") {
            & "$PSScriptRoot\Invoke-PythonPptxBuild.ps1" -DateFolder $DateFolder -WorkspaceRoot $basePath -OutputPath $outputPath -RunId $runId
            if ($LASTEXITCODE -ne 0) { throw "Python PPTX build failed with exit code $LASTEXITCODE" }
        } else {
            $ppt = New-PptxSession
            & "$PSScriptRoot\Build-CustomerPptx.ps1" -DateFolder $DateFolder -Session $ppt -ClosePresentation
            if (-not $?) { throw "Build-CustomerPptx.ps1 failed" }
        }
    }

    if (-not $effectiveSkipEnrich) {
        $currentPhase = "enrich"
        Write-PipelineStatus -State "started" -Phase $currentPhase -Passed $false
        Write-StepHeader "Enrich"
        if (-not $ppt) { $ppt = New-PptxSession }
        & "$PSScriptRoot\Enrich-CustomerPptx.ps1" -DateFolder $DateFolder -Session $ppt -ClosePresentation
        if (-not $?) { throw "Enrich-CustomerPptx.ps1 failed" }
    }
    elseif ($selectedEngine -eq "python" -and -not $SkipEnrich) {
        Write-Info "Python engine already renders Enrich content; COM Enrich was skipped."
    }

    $currentPhase = "verify"
    Write-PipelineStatus -State "started" -Phase $currentPhase -Passed $false
    Write-StepHeader "Verify"
    # このスクリプトが作成した COM セッションなので、検証前に終了して空の PowerPoint を残さない。
    if ($ppt) {
        $ppt.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
        $ppt = $null
    }
    $verifyLogPath = "$logsFolder\verify-$runId.log"
    $verifyResultPath = "$logsFolder\verify-$runId.json"
    & "$PSScriptRoot\Invoke-PptxVerify.ps1" -PptxPath $outputPath -RunId $runId -ResultPath $verifyResultPath -LogPath $verifyLogPath | Out-Null
    $verifyExitCode = $LASTEXITCODE

    if ($verifyExitCode -ne 0) { throw "Verify-Pptx.ps1 failed" }
    Write-PipelineStatus -State "passed" -Phase "complete" -Passed $true -VerifyExitCode $verifyExitCode -VerifyLogPath $verifyLogPath
    $elapsedSeconds = [Math]::Round($stopwatch.Elapsed.TotalSeconds, 1)
    Write-Success "Pipeline 完了 ($elapsedSeconds 秒)"
} catch {
    Write-PipelineStatus -State $(if ($currentPhase -eq "verify") { "verify-failed" } else { "build-failed" }) -Phase $currentPhase -Passed $false -ErrorSummary $_.Exception.Message
    Write-Failure "Pipeline エラー: $_"
    exit 1
} finally {
    if ($ppt) {
        try { $ppt.Quit() } catch {}
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
    }
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}

# 完了後は canonical ではなくローカル snapshot を開く（自動化/parityでは -NoOpen）
if (-not $NoOpen) {
    $reviewDirectory = Join-Path ([System.IO.Path]::GetTempPath()) "azure-update-review"
    New-Item -ItemType Directory -Force -Path $reviewDirectory | Out-Null
    $reviewPath = Join-Path $reviewDirectory ("$([System.IO.Path]::GetFileNameWithoutExtension($outputPath))-review-$runId.pptx")
    Copy-Item -LiteralPath $outputPath -Destination $reviewPath -Force
    Start-Process $reviewPath
}
exit 0
