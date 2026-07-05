<#
.SYNOPSIS
    Fix-Labels.ps1 - ラベル修正後の PPTX を部分更新
.DESCRIPTION
    classification.json の weekly 配列順に既存 PPTX の Weekly スライドを並べ替え、
    P2 目次と UPDATE Points 表のみを再書き込みします。
    Build/Enrich 全再実行を避け、ラベル誤判定修正を短時間で反映します。
    リージョンスタンプやスピーカーノートは再反映しないため、それらの欠落修復には使いません。
.PARAMETER DateFolder
    日付フォルダ（例: 0511）のパス
.PARAMETER OpenPowerPoint
    完了後に PowerPoint で開く
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$DateFolder,

    [switch]$OpenPowerPoint
)

$ErrorActionPreference = "Stop"

Import-Module "$PSScriptRoot\PptxCommon.psm1" -Force

Write-StepHeader "Fix-Labels.ps1"

$DateFolder = (Resolve-Path $DateFolder).Path
$basePath = Split-Path $DateFolder -Parent
$config = Get-Content "$basePath\.config\config.json" -Encoding UTF8 | ConvertFrom-Json
$dateString = Split-Path $DateFolder -Leaf
$outputFileName = $config.output.fileNamePattern -replace '\{year\}', $config.output.year -replace '\{date\}', $dateString
$outputPath = "$DateFolder\$outputFileName"
$manifestFolder = "$DateFolder\manifest"
$classificationPath = "$manifestFolder\classification.json"
$regionInfoReviewedPath = "$manifestFolder\region_info_reviewed.json"
$regionInfoPath = if (Test-Path $regionInfoReviewedPath) { $regionInfoReviewedPath } else { "$manifestFolder\region_info.json" }

if (-not (Test-Path $outputPath)) { Write-Failure "PPTX が見つかりません: $outputPath"; exit 1 }
if (-not (Test-Path $classificationPath)) { Write-Failure "classification.json が見つかりません: $classificationPath"; exit 1 }

$classification = Get-Content $classificationPath -Encoding UTF8 | ConvertFrom-Json
$regionInfo = @{}
if (Test-Path $regionInfoPath) {
    $regionData = Get-Content $regionInfoPath -Encoding UTF8 | ConvertFrom-Json
    $regionInfo = ConvertTo-RegionInfoMap -RegionData $regionData
}

Write-Info "対象ファイル: $outputPath"
Write-Info "Weekly: $($classification.weekly.Count) 件"
Write-Info "このスクリプトは P2 目次と UPDATE Points 表のみを更新します（ノート/スタンプは再反映しません）"

function Find-WeeklySlideIndex {
    param(
        [object]$Presentation,
        [string]$Title,
        [int]$Start,
        [int]$End
    )

    $target = Get-CleanSlideTitle -Title $Title
    $targetPrefix = $target.Substring(0, [Math]::Min(30, $target.Length)).ToLower()
    for ($i = $Start; $i -le $End; $i++) {
        $slideTitle = Get-CleanSlideTitle -Title (Get-SlideTitle -Slide $Presentation.Slides.Item($i))
        $slidePrefix = $slideTitle.Substring(0, [Math]::Min(30, $slideTitle.Length)).ToLower()
        if ($slidePrefix -eq $targetPrefix -or $slideTitle.ToLower().Contains($targetPrefix)) {
            return $i
        }
    }
    return 0
}

$ppt = $null
$pres = $null
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

Close-OpenPptxPresentation -PptxPath $outputPath -Save | Out-Null
$ppt = New-PptxSession
$pres = $ppt.Presentations.Open($outputPath)

$weeklyStart = $global:PPTX_WEEKLY_START
$updatePointsSlide = Find-UpdatePointsSlideIndex -Presentation $pres
if ($updatePointsSlide -le 0) { Write-Failure "UPDATE Points スライドが見つかりません"; exit 1 }
$weeklyEnd = $updatePointsSlide - 1

Write-Info "Weekly 範囲: P$weeklyStart〜P$weeklyEnd"

for ($idx = 0; $idx -lt $classification.weekly.Count; $idx++) {
    $targetIndex = $weeklyStart + $idx
    $wanted = $classification.weekly[$idx]
    $currentTitle = Get-CleanSlideTitle -Title (Get-SlideTitle -Slide $pres.Slides.Item($targetIndex))
    $wantedTitle = Get-CleanSlideTitle -Title $wanted.title
    $wantedPrefix = $wantedTitle.Substring(0, [Math]::Min(30, $wantedTitle.Length)).ToLower()

    if ($currentTitle.ToLower().StartsWith($wantedPrefix)) { continue }

    $foundIndex = Find-WeeklySlideIndex -Presentation $pres -Title $wanted.title -Start $targetIndex -End $weeklyEnd
    if ($foundIndex -le 0) { Write-Failure "スライドが見つかりません: $($wanted.title)"; exit 1 }

    Write-Host "  Move P$foundIndex -> P$targetIndex : [$($wanted.label)] $($wantedTitle.Substring(0, [Math]::Min(45, $wantedTitle.Length)))"
    $pres.Slides.Item($foundIndex).MoveTo($targetIndex)
    Start-Sleep -Milliseconds 100
}

if (Update-SummarySlideContent -Presentation $pres -Classification $classification) {
    Write-Success "P2 目次更新完了"
} else {
    Write-Failure "P2 目次の書き込み先が見つかりません"
    exit 1
}

if (Update-UpdatePointsTableContent -Presentation $pres -Classification $classification -RegionInfo $regionInfo) {
    Write-Success "UPDATE Points 表更新完了"
} else {
    Write-Failure "UPDATE Points 表が見つかりません"
    exit 1
}

$pres.Save()
Write-Success "保存完了"
$pres.Close()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres) | Out-Null
$ppt.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()

$verifyLogPath = "$DateFolder\fix-labels-verify.log"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$PSScriptRoot\Verify-Pptx.ps1" -PptxPath $outputPath *> $verifyLogPath
$verifyExitCode = $LASTEXITCODE

$status = @{
    generatedAt = (Get-Date).ToString("s")
    script = "Fix-Labels.ps1"
    pptxPath = $outputPath
    passed = ($verifyExitCode -eq 0)
    verifyExitCode = $verifyExitCode
    verifyLogPath = $verifyLogPath
    elapsedSeconds = [Math]::Round($stopwatch.Elapsed.TotalSeconds, 1)
}
$status | ConvertTo-Json -Depth 4 | Out-File "$manifestFolder\verify_status.json" -Encoding UTF8

if ($verifyExitCode -ne 0) {
    Write-Warning "ノートやリージョンスタンプの欠落修復には Fix-Labels ではなく Run-CustomerPptxPipeline.ps1 -SkipBuild または Enrich-CustomerPptx.ps1 を使用してください。"
    exit 1
}

Write-Success "Fix-Labels 完了（$([Math]::Round($stopwatch.Elapsed.TotalSeconds, 1)) 秒）"
if ($OpenPowerPoint) { Start-Process $outputPath }
exit 0
