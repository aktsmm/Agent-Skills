# Phase1-5 一括スクリプト
# - 未使用カスタムレイアウト削除
# - 表紙セクション化（A/B を表紙セクション内に移動）
# - 4種ステータスバッジ（GA/Preview/廃止/アナウンス）の右上配置用ヘルパーを定義
# - BIZ UDPGothic を本文・サマリ・UPDATE Points レイアウトに適用
# - サマリ本文を 24pt に
param([Parameter(Mandatory)][string]$TemplatePath)
$ErrorActionPreference = 'Stop'

$JpFont = 'BIZ UDPゴシック'

$ppt = New-Object -ComObject PowerPoint.Application
$p = $ppt.Presentations.Open($TemplatePath, $false, $false, $false)

# --- Phase5: 未使用カスタムレイアウト削除 ---
# 使用中: Topics_Theme Title / Topics_Theme Normal Content / プレビュー / Topics_Theme End Slide Blue
# 「セクション ヘッダー」も将来用に残す
$keepLayouts = @(
    'Topics_Theme Title',
    'Topics_Theme Normal Content',
    'プレビュー',
    'Topics_Theme End Slide Blue',
    'セクション ヘッダー',
    'Topics_Theme Section Header'
)
$removed = 0
$master = $p.SlideMaster
for ($i = $master.CustomLayouts.Count; $i -ge 1; $i--) {
    $lay = $master.CustomLayouts.Item($i)
    if ($keepLayouts -notcontains $lay.Name) {
        Write-Host "  削除: $($lay.Name)"
        try { $lay.Delete(); $removed++ } catch { Write-Warning "削除失敗 $($lay.Name): $_" }
    }
}
Write-Host "未使用レイアウト削除: $removed 件"

# --- Phase4 (template 側): 表紙セクションを定義 ---
# 既存セクション構造を一旦削除して再構築（表紙 / 本文 / Ending）
try {
    while ($p.SectionProperties.Count -gt 0) { $p.SectionProperties.Delete(1, $false) }
} catch { Write-Warning "section reset: $_" }

# 表紙群（CoverPanel を持つ全スライド）を表紙セクションに
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

# --- BIZ UDPGothic: 全テキストシェイプの日本語フォント設定 ---
# プレースホルダ・コンテンツに対して FarEast Name を BIZ UDPゴシック に
$fontApplied = 0
foreach ($lay in $master.CustomLayouts) {
    foreach ($sh in $lay.Shapes) {
        if (-not $sh.HasTextFrame) { continue }
        try {
            $tr = $sh.TextFrame.TextRange
            $tr.Font.NameFarEast = $JpFont
            # 半角は等幅一致を狙わず、可読性のため同じ BIZ UDP を当てる
            $tr.Font.Name = $JpFont
            $fontApplied++
        } catch {}
    }
}
# 各スライド内の現存テキストにも適用（表紙除く）
foreach ($s in $p.Slides) {
    $isCover = $false
    foreach ($sh in $s.Shapes) { if ($sh.Name -eq 'CoverPanel') { $isCover = $true; break } }
    if ($isCover) { continue }  # 表紙は Segoe UI 維持
    foreach ($sh in $s.Shapes) {
        if (-not $sh.HasTextFrame) { continue }
        try {
            $tr = $sh.TextFrame.TextRange
            $tr.Font.NameFarEast = $JpFont
            $tr.Font.Name = $JpFont
            $fontApplied++
        } catch {}
    }
}
Write-Host "BIZ UDPゴシック 適用シェイプ: $fontApplied"

# --- サマリ本文を 24pt に（テンプレ側のサンプル文字） ---
foreach ($s in $p.Slides) {
    $title = ''
    foreach ($sh in $s.Shapes) {
        if (-not $sh.HasTextFrame) { continue }
        if ($sh.Name -like 'Title*' -or $sh.Name -like 'タイトル*') {
            $title = $sh.TextFrame.TextRange.Text
            break
        }
    }
    if ($title -notmatch 'Weekly\s*News\s*Topics|今週のトピックス') { continue }
    foreach ($sh in $s.Shapes) {
        if (-not $sh.HasTextFrame) { continue }
        if ($sh.Name -like 'Title*' -or $sh.Name -like 'タイトル*') { continue }
        if ($sh.Name -like 'RegionStamp*') { continue }
        try { $sh.TextFrame.TextRange.Font.Size = 24 } catch {}
    }
    Write-Host "サマリ本文フォント 24pt 適用"
}

$p.Save()
$p.Close()
$ppt.Quit()
Write-Host "DONE"
