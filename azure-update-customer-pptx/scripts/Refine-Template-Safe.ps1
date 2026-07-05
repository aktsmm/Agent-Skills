# Phase1-5 安全版
# - フォント適用: 本文・サマリで使われている「プレビュー」「Topics_Theme Normal Content」レイアウトのみ
# - セクション化のみ
# - 未使用レイアウト削除はスキップ（前回ハング原因のため）
param([Parameter(Mandatory)][string]$TemplatePath)
$ErrorActionPreference = 'Stop'

$JpFont = 'BIZ UDPゴシック'

$ppt = New-Object -ComObject PowerPoint.Application
$p = $ppt.Presentations.Open($TemplatePath, $false, $false, $false)

# --- セクション再構築 ---
try {
    while ($p.SectionProperties.Count -gt 0) { $p.SectionProperties.Delete(1, $false) }
} catch {}

$coverIds = @()
for ($i = 1; $i -le $p.Slides.Count; $i++) {
    foreach ($sh in $p.Slides.Item($i).Shapes) {
        if ($sh.Name -eq 'CoverPanel') { $coverIds += $i; break }
    }
}
if ($coverIds.Count -gt 0) {
    $coverEnd = ($coverIds | Sort-Object -Descending)[0]
    $p.SectionProperties.AddBeforeSlide(1, '表紙') | Out-Null
    if (($coverEnd + 1) -le $p.Slides.Count) {
        $p.SectionProperties.AddBeforeSlide($coverEnd + 1, '本文') | Out-Null
    }
    if ($p.Slides.Count -gt 1) {
        $endingIdx = $p.Slides.Count
        $p.SectionProperties.AddBeforeSlide($endingIdx, 'Ending') | Out-Null
    }
    Write-Host "セクション: 表紙(1..$coverEnd) + 本文 + Ending"
}

# --- 本文レイアウト「プレビュー」と「Topics_Theme Normal Content」のみフォント適用 ---
$targetLayouts = @('プレビュー', 'Topics_Theme Normal Content')
$fontApplied = 0
foreach ($lay in $p.SlideMaster.CustomLayouts) {
    if ($targetLayouts -notcontains $lay.Name) { continue }
    foreach ($sh in $lay.Shapes) {
        if (-not $sh.HasTextFrame) { continue }
        try {
            $tr = $sh.TextFrame.TextRange
            $tr.Font.NameFarEast = $JpFont
            $fontApplied++
        } catch {}
    }
}
Write-Host "本文系レイアウトに $JpFont 適用: $fontApplied シェイプ"

# --- サマリスライドのみ本文 24pt + フォント適用 ---
foreach ($s in $p.Slides) {
    $title = ''
    foreach ($sh in $s.Shapes) {
        if (-not $sh.HasTextFrame) { continue }
        if ($sh.Name -like 'Title*' -or $sh.Name -like 'タイトル*') {
            try { $title = $sh.TextFrame.TextRange.Text } catch {}
            break
        }
    }
    if ($title -notmatch 'Weekly\s*News\s*Topics|今週のトピックス') { continue }
    foreach ($sh in $s.Shapes) {
        if (-not $sh.HasTextFrame) { continue }
        if ($sh.Name -like 'Title*' -or $sh.Name -like 'タイトル*') { continue }
        if ($sh.Name -like 'RegionStamp*') { continue }
        try {
            $sh.TextFrame.TextRange.Font.Size = 24
            $sh.TextFrame.TextRange.Font.NameFarEast = $JpFont
        } catch {}
    }
    Write-Host "サマリ本文 24pt + $JpFont 適用"
}

$p.Save()
$p.Close()
$ppt.Quit()
Write-Host "DONE (safe mode)"
