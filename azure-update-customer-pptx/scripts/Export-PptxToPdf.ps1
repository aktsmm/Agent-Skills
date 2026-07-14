<#
.SYNOPSIS
    Export-PptxToPdf.ps1 - 既存 PPTX を PDF に変換
.DESCRIPTION
    入力PPTXをローカル一時コピーへ複製し、そのコピーをread-onlyで開いてPDFを出力する。
    正規PPTXをPowerPointへ渡さず、出力前後にOpenXML形式とSHA-256不変を検証する。
.PARAMETER PptxPath
    入力 PPTX パス
.PARAMETER PdfPath
    出力 PDF パス。省略時は PPTX と同名の .pdf
.PARAMETER OpenPdf
    出力後に PDF を開く
.PARAMETER RequireUnencrypted
    PDF に暗号化が検出された場合、出力を失敗として扱う
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$PptxPath,

    [string]$PdfPath,

    [switch]$OpenPdf,

    [switch]$RequireUnencrypted
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

$canonicalHash = $null
$tempPptxPath = $null
$app = $null
$pres = $null

function Test-OpenXmlPptx {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
    try {
        $archive = [System.IO.Compression.ZipArchive]::new($stream, [System.IO.Compression.ZipArchiveMode]::Read, $false)
        $archive.Dispose()
        return $true
    } catch {
        return $false
    } finally {
        $stream.Dispose()
    }
}

function Test-PdfEncryption {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $content = [System.Text.Encoding]::ASCII.GetString([System.IO.File]::ReadAllBytes($Path))
    return $content -match '(?m)/Encrypt\s+\d+\s+\d+\s+R\b'
}

try {
    if (-not (Test-OpenXmlPptx -Path $fullPptxPath)) {
        throw "正規PPTXが有効なOpenXML ZIPではありません: $fullPptxPath"
    }
    $canonicalHash = (Get-FileHash -LiteralPath $fullPptxPath -Algorithm SHA256).Hash

    $tempDirectory = Join-Path ([System.IO.Path]::GetTempPath()) "azure-update-pdf"
    New-Item -ItemType Directory -Force -Path $tempDirectory | Out-Null
    $tempPptxPath = Join-Path $tempDirectory ("$([System.IO.Path]::GetFileNameWithoutExtension($fullPptxPath))-$([guid]::NewGuid().ToString())$([System.IO.Path]::GetExtension($fullPptxPath))")
    Copy-Item -LiteralPath $fullPptxPath -Destination $tempPptxPath -Force
    if (-not (Test-OpenXmlPptx -Path $tempPptxPath)) {
        throw "ローカルPDF出力コピーが有効なOpenXML ZIPではありません: $tempPptxPath"
    }
    Write-Info "ローカル一時コピーをread-onlyで開いて PDF 出力します"

    $app = New-PptxSession
    $pres = $app.Presentations.Open($tempPptxPath, $true, $false, $false)

    if (Test-Path -LiteralPath $fullPdfPath) {
        Remove-Item -LiteralPath $fullPdfPath -Force
    }

    $pres.SaveAs($fullPdfPath, 32)

    if (-not (Test-Path $fullPdfPath)) {
        throw "PDF が生成されませんでした: $fullPdfPath"
    }

    $pdfFile = Get-Item $fullPdfPath
    if ($pdfFile.Length -le 0) {
        throw "PDF サイズが 0 byte です: $fullPdfPath"
    }

    $isEncrypted = Test-PdfEncryption -Path $fullPdfPath
    if ($isEncrypted) {
        $message = "PDF に暗号化が検出されました。PowerPoint の感度ラベルと配布要件を確認してください: $fullPdfPath"
        if ($RequireUnencrypted) {
            throw $message
        }
        Write-Warning $message
    }
    if ((Get-FileHash -LiteralPath $fullPptxPath -Algorithm SHA256).Hash -ne $canonicalHash) {
        throw "PDF出力中に正規PPTXが変更されました: $fullPptxPath"
    }
    if (-not (Test-OpenXmlPptx -Path $fullPptxPath)) {
        throw "PDF出力後の正規PPTXが有効なOpenXML ZIPではありません: $fullPptxPath"
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
        if ($pres) {
            $pres.Close()
        }
    } catch {}

    try {
        if ($pres) {
            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres) | Out-Null
        }
    } catch {}

    try {
        if ($app) {
            $app.Quit()
        }
    } catch {}

    try {
        if ($tempPptxPath -and (Test-Path -LiteralPath $tempPptxPath)) {
            Remove-Item -LiteralPath $tempPptxPath -Force
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