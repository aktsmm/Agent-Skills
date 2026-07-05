<#
.SYNOPSIS
    UPDATE Points表のリージョン列を修正
#>
param(
    [string]$PptxPath
)

$ErrorActionPreference = "Stop"

Write-Host "=== リージョン情報修正 ===" -ForegroundColor Cyan
Write-Host "対象: $PptxPath"

$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue

# 開いているプレゼンを取得
$presentation = $null
foreach ($p in $ppt.Presentations) {
    if ($p.FullName -eq $PptxPath) {
        $presentation = $p
        Write-Host "既存のプレゼンテーションを使用"
        break
    }
}

if (-not $presentation) {
    Write-Host "ファイルを開きます..."
    $presentation = $ppt.Presentations.Open($PptxPath)
}

# UPDATE Pointsスライドを探す
$updatePointsSlide = $null
for ($i = 1; $i -le $presentation.Slides.Count; $i++) {
    $slide = $presentation.Slides.Item($i)
    for ($j = 1; $j -le $slide.Shapes.Count; $j++) {
        $shape = $slide.Shapes.Item($j)
        try {
            if ($shape.HasTextFrame -eq -1) {
                if ($shape.TextFrame.HasText -eq -1) {
                    $text = $shape.TextFrame.TextRange.Text
                    if ($text -match "UPDATE.*Points|今週のUPDATE") {
                        $updatePointsSlide = $slide
                        Write-Host "UPDATE Pointsスライド発見: P$i"
                        break
                    }
                }
            }
        } catch { }
    }
    if ($updatePointsSlide) { break }
}

if (-not $updatePointsSlide) {
    Write-Host "❌ UPDATE Pointsスライドが見つかりません" -ForegroundColor Red
    exit 1
}

# 表を探す
$table = $null
for ($j = 1; $j -le $updatePointsSlide.Shapes.Count; $j++) {
    $shape = $updatePointsSlide.Shapes.Item($j)
    if ($shape.HasTable -eq -1) {
        $table = $shape.Table
        Write-Host "表発見: $($table.Rows.Count) 行"
        break
    }
}

if (-not $table) {
    Write-Host "❌ 表が見つかりません" -ForegroundColor Red
    exit 1
}

# 修正対象
$corrections = @{
    "ランサムウェア" = "Japan East のみ"
    "SRE Agent" = "日本未対応"
}

$fixed = 0
for ($row = 2; $row -le $table.Rows.Count; $row++) {
    try {
        $titleText = $table.Cell($row, 3).Shape.TextFrame.TextRange.Text

        foreach ($pattern in $corrections.Keys) {
            if ($titleText -match $pattern) {
                $newValue = $corrections[$pattern]
                $table.Cell($row, 5).Shape.TextFrame.TextRange.Text = $newValue
                Write-Host "✅ 行${row}: $pattern → $newValue" -ForegroundColor Green
                $fixed++
            }
        }
    } catch {
        Write-Host "行${row}: スキップ（エラー）"
    }
}

$presentation.Save()
Write-Host "`n✅ 修正完了: ${fixed} 件修正・保存しました" -ForegroundColor Green

# COM解放
try {
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($table) | Out-Null
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($updatePointsSlide) | Out-Null
} catch { }
[GC]::Collect()
[GC]::WaitForPendingFinalizers()

exit 0
