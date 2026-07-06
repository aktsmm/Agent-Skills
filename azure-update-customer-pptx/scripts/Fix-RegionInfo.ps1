<#
.SYNOPSIS
    UPDATE Points 表のリージョン列を manifest の region 情報から再反映する。
.DESCRIPTION
    one-off のタイトル固定補正は行わず、manifest/region_info_reviewed.json を優先し、
    無ければ manifest/region_info.json を使う。対象 PPTX が開いていれば再利用し、
    このスクリプトが開いた Presentation だけを閉じる。
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$PptxPath,

    [string]$RegionInfoPath = ""
)

$ErrorActionPreference = "Stop"

Import-Module "$PSScriptRoot\PptxCommon.psm1" -Force

Write-StepHeader "Fix-RegionInfo.ps1"

$fullPptxPath = Get-PptxFullPath -PptxPath $PptxPath
if (-not (Test-Path -LiteralPath $fullPptxPath)) {
    Write-Failure "PPTX が見つかりません: $fullPptxPath"
    exit 1
}

$dateFolder = Split-Path $fullPptxPath -Parent
$manifestFolder = Join-Path $dateFolder "manifest"
$resolvedRegionInfoPath = if ($RegionInfoPath) {
    (Resolve-Path -LiteralPath $RegionInfoPath).Path
} elseif (Test-Path -LiteralPath (Join-Path $manifestFolder "region_info_reviewed.json")) {
    Join-Path $manifestFolder "region_info_reviewed.json"
} else {
    Join-Path $manifestFolder "region_info.json"
}

if (-not (Test-Path -LiteralPath $resolvedRegionInfoPath)) {
    Write-Failure "リージョン情報 JSON が見つかりません: $resolvedRegionInfoPath"
    exit 1
}

$regionData = Get-Content -LiteralPath $resolvedRegionInfoPath -Raw -Encoding UTF8 | ConvertFrom-Json
$regionInfo = ConvertTo-RegionInfoMap -RegionData $regionData
if ($regionInfo.Count -eq 0) {
    Write-Failure "リージョン情報が空です: $resolvedRegionInfoPath"
    exit 1
}

Write-Info "対象 PPTX: $fullPptxPath"
Write-Info "リージョン情報: $resolvedRegionInfoPath ($($regionInfo.Count) 件)"

$ppt = $null
$presentation = $null
$openedHere = $false
$ownsSession = $false

try {
    $ppt = Get-ActivePptxApplication
    if (-not $ppt) {
        $ppt = New-PptxSession
        $ownsSession = $true
    }

    $presentation = Find-OpenPptxPresentation -Application $ppt -PptxPath $fullPptxPath
    if ($presentation) {
        Write-Info "開いている PPTX を再利用します"
    } else {
        Write-Info "PPTX を開きます"
        $presentation = $ppt.Presentations.Open($fullPptxPath)
        $openedHere = $true
    }

    $updatePointsIndices = @(Get-UpdatePointsSlideIndices -Presentation $presentation)
    if ($updatePointsIndices.Count -eq 0) {
        throw "UPDATE Points スライドが見つかりません"
    }

    $fixed = 0
    foreach ($updatePointsSlideNumber in $updatePointsIndices) {
        $updatePointsSlide = $presentation.Slides.Item($updatePointsSlideNumber)
        $table = $null

        foreach ($shape in $updatePointsSlide.Shapes) {
            if ($shape.HasTable -eq -1) {
                $table = $shape.Table
                break
            }
        }

        if (-not $table) {
            throw "P$updatePointsSlideNumber に UPDATE Points 表が見つかりません"
        }

        for ($row = 2; $row -le $table.Rows.Count; $row++) {
            $titleText = $table.Cell($row, 3).Shape.TextFrame.TextRange.Text
            $cleanTitle = Get-CleanSlideTitle -Title $titleText
            $newValue = Find-RegionStatus -Title $cleanTitle -RegionInfo $regionInfo
            $currentValue = $table.Cell($row, 5).Shape.TextFrame.TextRange.Text

            if ($newValue -and $newValue -ne $currentValue) {
                $table.Cell($row, 5).Shape.TextFrame.TextRange.Text = $newValue
                Write-Host "  P$updatePointsSlideNumber 行$($row - 1): $currentValue -> $newValue"
                $fixed++
            }
        }
    }

    $presentation.Save()
    Write-Success "リージョン列を再反映しました（$fixed 件更新）"
} catch {
    Write-Failure "リージョン情報修正エラー: $_"
    exit 1
} finally {
    try {
        if ($presentation -and $openedHere) {
            $presentation.Close()
        }
    } catch {}

    try {
        if ($presentation) {
            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($presentation) | Out-Null
        }
    } catch {}

    try {
        if ($ppt -and $ownsSession) {
            $ppt.Quit()
        }
    } catch {}

    try {
        if ($ppt) {
            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
        }
    } catch {}

    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}

exit 0
