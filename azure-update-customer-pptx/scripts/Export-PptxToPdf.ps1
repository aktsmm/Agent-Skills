<#
.SYNOPSIS
    Export-PptxToPdf.ps1 - 既存 PPTX を PDF に変換
.DESCRIPTION
    対象 PPTX が既に PowerPoint で開かれていればその Presentation を再利用し、
    開かれていなければ read-only で開いて PDF を出力する。
.PARAMETER PptxPath
    入力 PPTX パス
.PARAMETER PdfPath
    出力 PDF パス。省略時は PPTX と同名の .pdf
.PARAMETER OpenPdf
    出力後に PDF を開く
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$PptxPath,

    [string]$PdfPath,

    [switch]$OpenPdf
)

$ErrorActionPreference = "Stop"

Import-Module "$PSScriptRoot\PptxCommon.psm1" -Force

Write-StepHeader "Export-PptxToPdf.ps1"

$fullPptxPath = Get-PptxFullPath -PptxPath $PptxPath
if (-not (Test-Path $fullPptxPath)) {
    Write-Failure "PPTX が見つかりません: $fullPptxPath"
    exit 1
}

$fullPdfPath = if ($PdfPath) {
    [System.IO.Path]::GetFullPath($PdfPath)
} else {
    [System.IO.Path]::ChangeExtension($fullPptxPath, ".pdf")
}

$app = $null
$pres = $null
$ownsSession = $false
$openedHere = $false

try {
    $app = Get-ActivePptxApplication
    if (-not $app) {
        $app = New-PptxSession
        $ownsSession = $true
    }

    $pres = Find-OpenPptxPresentation -Application $app -PptxPath $fullPptxPath
    if ($pres) {
        Write-Info "開いている PPTX を再利用して PDF 出力します"
    } else {
        Write-Info "PPTX を read-only で開いて PDF 出力します"
        $pres = $app.Presentations.Open($fullPptxPath, $true, $false, $false)
        $openedHere = $true
    }

    if (Test-Path $fullPdfPath) {
        Remove-Item $fullPdfPath -Force
    }

    $pres.SaveAs($fullPdfPath, 32)

    if (-not (Test-Path $fullPdfPath)) {
        throw "PDF が生成されませんでした: $fullPdfPath"
    }

    $pdfFile = Get-Item $fullPdfPath
    if ($pdfFile.Length -le 0) {
        throw "PDF サイズが 0 byte です: $fullPdfPath"
    }

    Write-Success "PDF 出力完了: $fullPdfPath ($($pdfFile.Length) bytes)"

    if ($OpenPdf) {
        Start-Process $fullPdfPath
    }
} catch {
    Write-Failure "PDF 出力エラー: $_"
    exit 1
} finally {
    try {
        if ($pres -and $openedHere) {
            $pres.Close()
        }
    } catch {}

    try {
        if ($pres) {
            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres) | Out-Null
        }
    } catch {}

    try {
        if ($app -and $ownsSession) {
            $app.Quit()
        }
    } catch {}

    try {
        if ($app) {
            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null
        }
    } catch {}

    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}

exit 0