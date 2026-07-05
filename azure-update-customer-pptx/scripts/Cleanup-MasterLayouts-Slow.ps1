# テンプレートから未使用カスタムレイアウトをゆっくり削除する
# - 1 件削除ごとに 0.5 秒待機 + Save() で OneDrive 同期の混雑を回避
# - 使用中レイアウトは絶対に削除しない
# - 一度に削除する件数を MaxRemove で制限可能（既定: 5 件）
param(
    [Parameter(Mandatory)][string]$TemplatePath,
    [int]$MaxRemove = 5
)
$ErrorActionPreference = 'Stop'

$keepLayouts = @(
    'Topics_Theme Title',
    'Topics_Theme Normal Content',
    'プレビュー',
    'Topics_Theme End Slide Blue',
    'セクション ヘッダー',
    'Topics_Theme Section Header'
)

Get-Process POWERPNT -EA SilentlyContinue | Stop-Process -Force
Start-Sleep 3

$ppt = New-Object -ComObject PowerPoint.Application
$p = $ppt.Presentations.Open($TemplatePath, $false, $false, $false)

$master = $p.SlideMaster
$removed = 0
$candidates = @()
for ($i = $master.CustomLayouts.Count; $i -ge 1; $i--) {
    $lay = $master.CustomLayouts.Item($i)
    if ($keepLayouts -notcontains $lay.Name) {
        $candidates += [pscustomobject]@{ Index = $i; Name = $lay.Name }
    }
}
Write-Host "削除候補: $($candidates.Count) 件 / 今回最大削除: $MaxRemove 件"

foreach ($c in $candidates | Select-Object -First $MaxRemove) {
    Write-Host "  削除中: $($c.Name) ..."
    try {
        # Index が変わるので毎回再取得
        $target = $null
        for ($j = $master.CustomLayouts.Count; $j -ge 1; $j--) {
            if ($master.CustomLayouts.Item($j).Name -eq $c.Name) { $target = $master.CustomLayouts.Item($j); break }
        }
        if ($target) {
            $target.Delete()
            $removed++
            Start-Sleep -Milliseconds 500
            # 5 件ごとに保存
            if ($removed % 5 -eq 0) {
                Write-Host "  途中保存..."
                $p.Save()
                Start-Sleep 1
            }
        }
    } catch {
        Write-Warning "  削除失敗: $($c.Name) - $($_.Exception.Message)"
    }
}

Write-Host "削除完了: $removed 件 / 残り候補: $([Math]::Max(0, $candidates.Count - $removed)) 件"
$p.Save()
$p.Close()
$ppt.Quit()
Write-Host "DONE"
