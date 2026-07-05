# 本文レイアウト（slide4 由来「プレビュー」）から、レイアウト上の「プレビュー」
# バッジ装飾を削除する。テンプレートと生成PPTX両方に適用可能。
param([Parameter(Mandatory)][string]$PptxPath)
$ErrorActionPreference = 'Stop'

$ppt = New-Object -ComObject PowerPoint.Application
$p = $ppt.Presentations.Open($PptxPath, $false, $false, $false)

$removed = 0
foreach ($master in $p.Designs) {
    foreach ($layout in $master.SlideMaster.CustomLayouts) {
        $name = $layout.Name
        if ($name -notmatch 'プレビュー|Preview') { continue }
        # レイアウト内のシェイプを走査し、テキストが「プレビュー」または「Preview」だけのものを削除
        for ($i = $layout.Shapes.Count; $i -ge 1; $i--) {
            $sh = $layout.Shapes.Item($i)
            if (-not $sh.HasTextFrame) { continue }
            if (-not $sh.TextFrame.HasText) { continue }
            $t = ($sh.TextFrame.TextRange.Text -replace "[\s\r\n\t]", '').Trim()
            if ($t -eq 'プレビュー' -or $t -eq 'Preview') {
                Write-Host "  Layout '$name' から '$($sh.Name)' (text='$t') を削除"
                $sh.Delete()
                $removed++
            }
        }
    }
}

$p.Save()
$p.Close()
$ppt.Quit()
Write-Host "DONE removed=$removed"
