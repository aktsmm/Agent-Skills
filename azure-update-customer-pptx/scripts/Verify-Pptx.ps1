# Verify-Pptx.ps1 - Gate 3 実機検証スクリプト（拡張版）
# 使用方法: & "scripts\Verify-Pptx.ps1" -PptxPath "path\to\output.pptx"
#
# 検証項目:
#   1. P2 目次が項番形式
#   2. UPDATE Points 表のリージョン列
#   3. リージョンスタンプの存在
#   4. スピーカーノートの存在
#   5. セクション順序の検証
#   6. スライド並び順の検証（【廃止】→【GA】→【Preview】→【アナウンス/更新】）
#   7. UPDATE Points 位置の検証（Weekly Topics の後）
#   8. 表内容品質の検証（汎用的な文言禁止）
#   9. ノート内容整合性チェック（タイトルとノートの対応）★ 2026-02-16 追加
#
param(
    [Parameter(Mandatory=$true)]
    [string]$PptxPath,

    [int]$WeeklyStartSlide = 3,  # P3からWeekly Topics
    [int]$WeeklyCount = 0,  # 0の場合は自動検出
    [int]$AppendixStartSlide = 0,  # 0の場合は自動検出

    [object]$Session = $null,

    [switch]$NoExit
)

# 共通モジュール読み込み（定数使用のため）
Import-Module "$PSScriptRoot\PptxCommon.psm1" -Force

Write-Host "=== Gate 3 実機検証 ===" -ForegroundColor Cyan
Write-Host "対象ファイル: $PptxPath"

# 絶対パスに変換（COM操作に必須）
$PptxPath = (Resolve-Path $PptxPath).Path

if (-not (Test-Path $PptxPath)) {
    Write-Host "❌ ファイルが見つかりません: $PptxPath" -ForegroundColor Red
    exit 1
}

$errors = @()
$warnings = @()

# PowerPoint を開く
$ownsSession = $null -eq $Session
$ppt = if ($Session) { $Session } else { New-Object -ComObject PowerPoint.Application }
$pres = $ppt.Presentations.Open($PptxPath, $true, $false, $false)  # ReadOnly

Write-Host "`n総スライド数: $($pres.Slides.Count)"

$classificationPath = Join-Path (Split-Path $PptxPath -Parent) "manifest\classification.json"
$classification = $null
if (Test-Path $classificationPath) {
    $classification = Get-Content $classificationPath -Encoding UTF8 | ConvertFrom-Json
}
$expectedWeeklyCount = if ($classification -and $classification.weekly) { @($classification.weekly).Count } else { $WeeklyCount }

function Test-HasRedundantStatusPrefix {
    param(
        [string]$Text
    )

    if (-not $Text) { return $false }

    $patterns = @(
        '【GA】\s*(一般提供開始|一般提供|一般公開|Generally Available)\s*[:：]?',
        '【GA】.*\s+(一般提供開始|一般提供|一般公開|Generally Available)$',
        '【Preview】\s*(パブリック\s*プレビュー|プレビュー|Preview|Public Preview|Private Preview)\s*[:：]?',
        '【Preview】.*\s+(パブリック\s*プレビュー|プレビュー|Preview|Public Preview|Private Preview)$',
        '【廃止】\s*(廃止予定|提供終了|サービス終了|Retirement|Deprecated|End of Support)\s*[:：]?',
        '【アナウンス】\s*(アナウンス|Announcement)\s*[:：]?'
    )

    foreach ($pattern in $patterns) {
        if ($Text -match $pattern) {
            return $true
        }
    }

    return $false
}

# ========================================
# 表紙群の動的検出（表示表紙のみをカウント）
# A/B バリエーションは末尾へ移動されているため、「表示中の表紙の中で最初」を見て Weekly 開始位置を決める
# ========================================
$visibleCoverEnd = 0
$reachedNonCover = $false
for ($ci = 1; $ci -le $pres.Slides.Count; $ci++) {
    $sl = $pres.Slides.Item($ci)
    $isCover = $false
    try { if ($sl.CustomLayout.Name -like 'Azure Update Cover*') { $isCover = $true } } catch {}
    if (-not $isCover) { foreach ($sh in $sl.Shapes) { if ($sh.Name -eq 'CoverPanel') { $isCover = $true; break } } }
    if ($isCover -and -not $reachedNonCover) {
        $visibleCoverEnd = $ci
    } else {
        $reachedNonCover = $true
    }
}
if ($visibleCoverEnd -gt 0) {
    $WeeklyStartSlide = $visibleCoverEnd + 2
    Write-Host "Weekly 開始位置を動的検出: P$WeeklyStartSlide (表示表紙 $visibleCoverEnd 枚 + サマリ)" -ForegroundColor Cyan
}

# ========================================
# 検証 1: P2 目次が項番形式か
# ========================================
Write-Host "`n[検証1] サマリ（目次）の項番形式..." -ForegroundColor Yellow

$p2 = $pres.Slides.Item($WeeklyStartSlide - 1)
$p2HasNumberedList = $false

foreach ($shape in $p2.Shapes) {
    if ($shape.HasTextFrame -eq -1) {
        $text = $shape.TextFrame.TextRange.Text
        # 項番形式のパターン（改行コードはCR or CRLF）
        if ($text -match "1\..*【.+】" -and ($expectedWeeklyCount -le 1 -or $text -match "2\..*【.+】")) {
            $p2HasNumberedList = $true
            break
        }
        # 番号が複数行にわたって存在するパターン
        if ($text -match "^1\." -and ($expectedWeeklyCount -le 1 -or $text -match "[\r\n]2\.")) {
            $p2HasNumberedList = $true
            break
        }
    }
}

if ($p2HasNumberedList) {
    Write-Host "  ✅ P2: 項番形式で記載されています" -ForegroundColor Green
} else {
    Write-Host "  ❌ P2: 項番形式でない（• ではなく 1. 2. 3. を使用すること）" -ForegroundColor Red
    $errors += "P2: 目次が項番形式でない"
}

$p2RedundantStatus = @()
foreach ($shape in $p2.Shapes) {
    if ($shape.HasTextFrame -eq -1) {
        $text = $shape.TextFrame.TextRange.Text
        $lines = $text -split "`r?`n"
        foreach ($line in $lines) {
            if (Test-HasRedundantStatusPrefix -Text $line) {
                $p2RedundantStatus += $line.Trim()
            }
        }
    }
}

if ($p2RedundantStatus.Count -eq 0) {
    Write-Host "  ✅ P2: ラベル重複表記はありません" -ForegroundColor Green
} else {
    $sample = $p2RedundantStatus[0]
    Write-Host "  ❌ P2: ラベル重複表記あり（例: $sample）" -ForegroundColor Red
    $errors += "P2: 【GA】一般提供: のようなラベル重複表記が残っている"
}

# ========================================
# 検証 2: UPDATE Points 表のリージョン列
# ========================================
Write-Host "`n[検証2] UPDATE Points 表のリージョン列..." -ForegroundColor Yellow

$updatePointsSlideIndices = @(Get-UpdatePointsSlideIndices -Presentation $pres)
$updatePointTables = @()
$unexpectedUpdatePointStamps = @()
foreach ($slideNumber in $updatePointsSlideIndices) {
    $slide = $pres.Slides.Item($slideNumber)
    foreach ($shape in $slide.Shapes) {
        if ($shape.Name -eq "RegionStamp") {
            $unexpectedUpdatePointStamps += "P$slideNumber"
        }
        if ($shape.HasTable -eq -1) {
            $updatePointTables += [PSCustomObject]@{
                SlideNumber = $slideNumber
                Table = $shape.Table
            }
            break
        }
    }
}

$totalUpdatePointRows = 0
if ($updatePointTables.Count -gt 0) {
    $regionColIndex = 5  # 5列目がリージョン
    $invalidRows = @()
    $overflowSlides = @()

    foreach ($tableInfo in $updatePointTables) {
        $table = $tableInfo.Table
        $dataRows = [Math]::Max(0, $table.Rows.Count - 1)
        $totalUpdatePointRows += $dataRows
        if ($dataRows -gt 10) {
            $overflowSlides += "P$($tableInfo.SlideNumber): ${dataRows}件"
        }

        for ($r = 2; $r -le $table.Rows.Count; $r++) {
            if ($table.Columns.Count -ge $regionColIndex) {
                $regionText = $table.Rows.Item($r).Cells($regionColIndex).Shape.TextFrame.TextRange.Text

                # 有効なリージョン表記かチェック（定数から取得）
                $isValid = $false
                foreach ($pattern in $global:VALID_REGION_PATTERNS) {
                    if ($regionText -match [regex]::Escape($pattern)) {
                        $isValid = $true
                        break
                    }
                }

                if (-not $isValid -or $regionText -eq "" -or $regionText -match "^\s*$") {
                    $invalidRows += "P$($tableInfo.SlideNumber) 行$($r - 1)"
                }
            }
        }
    }

    if ($overflowSlides.Count -gt 0) {
        Write-Host "  ❌ UPDATE Points: 1ページあたりの件数超過 ($($overflowSlides -join ', '))" -ForegroundColor Red
        $errors += "UPDATE Points: 表が分割されていない（$($overflowSlides -join ', ')）"
    }

    if ($unexpectedUpdatePointStamps.Count -gt 0) {
        Write-Host "  ❌ UPDATE Points: RegionStamp が混入 ($($unexpectedUpdatePointStamps -join ', '))" -ForegroundColor Red
        $errors += "UPDATE Points: RegionStamp が混入している（$($unexpectedUpdatePointStamps -join ', ')）"
    }

    if ($invalidRows.Count -eq 0) {
        Write-Host "  ✅ UPDATE Points: 全行のリージョン列が正しく記載されています" -ForegroundColor Green
    } else {
        Write-Host "  ❌ UPDATE Points: $($invalidRows -join ', ') のリージョン情報が不正" -ForegroundColor Red
        $errors += "UPDATE Points: リージョン情報が不正（$($invalidRows -join ', ')）"
    }
} else {
    Write-Host "  ⚠️ UPDATE Points: 表が見つかりません" -ForegroundColor Yellow
    $warnings += "UPDATE Points: 表が見つかりません"
}

# ========================================
# 検証 3: リージョンスタンプの存在
# ========================================
Write-Host "`n[検証3] リージョンスタンプの存在..." -ForegroundColor Yellow

# Weekly 開始位置は冒頭で動的検出済み（visibleCoverEnd ベース）

if ($WeeklyCount -eq 0) {
    # UPDATE Points, Appendix ヘッダーまたは非表示スライドを探す
    for ($i = $WeeklyStartSlide; $i -le $pres.Slides.Count; $i++) {
        $slide = $pres.Slides.Item($i)
        $title = try { $slide.Shapes.Title.TextFrame.TextRange.Text } catch { "" }
        $hidden = $slide.SlideShowTransition.Hidden -eq -1

        if ($title -match "UPDATE.*Points" -or $title -match "Appendix" -or $hidden) {
            $WeeklyCount = $i - $WeeklyStartSlide
            $AppendixStartSlide = $i
            break
        }
    }
    if ($WeeklyCount -eq 0) {
        $WeeklyCount = $pres.Slides.Count - $WeeklyStartSlide - 1
    }
}

$weeklyEnd = $WeeklyStartSlide + $WeeklyCount - 1
Write-Host "  Weekly Topics: P$WeeklyStartSlide 〜 P$weeklyEnd ($WeeklyCount 枚)"

$missingStamps = @()

for ($i = $WeeklyStartSlide; $i -le $weeklyEnd; $i++) {
    $slide = $pres.Slides.Item($i)
    $hasStamp = $false

    foreach ($shape in $slide.Shapes) {
        # スタンプ名または内容で検索
        if ($shape.Name -match "RegionStamp" -or $shape.Name -match "Stamp") {
            $hasStamp = $true
            break
        }
        if ($shape.HasTextFrame -eq -1) {
            $text = $shape.TextFrame.TextRange.Text
            if ($text -match "Japan|グローバル|East|West") {
                # 位置が右下（スタンプ位置）かチェック
                if ($shape.Left -gt 600 -and $shape.Top -gt 400) {
                    $hasStamp = $true
                    break
                }
            }
        }
    }

    if (-not $hasStamp) {
        $missingStamps += $i
    }
}

if ($missingStamps.Count -eq 0) {
    Write-Host "  ✅ 全 Weekly Topics スライドにリージョンスタンプがあります" -ForegroundColor Green
} else {
    Write-Host "  ❌ リージョンスタンプなし: P$($missingStamps -join ', P')" -ForegroundColor Red
    $errors += "リージョンスタンプなし: P$($missingStamps -join ', P')"
}

# ========================================
# 検証 4: スピーカーノートの存在
# ========================================
Write-Host "`n[検証4] スピーカーノートの存在..." -ForegroundColor Yellow

$missingNotes = @()

# Weekly Topics + Appendix（Ending以外、UPDATE Points 表除外）をチェック
for ($i = $WeeklyStartSlide; $i -lt $pres.Slides.Count; $i++) {
    $slide = $pres.Slides.Item($i)
    $title = try { $slide.Shapes.Title.TextFrame.TextRange.Text } catch { "" }

    # Ending スライド（空白）はスキップ
    if ($title -eq "" -and $i -eq $pres.Slides.Count) { continue }

    # UPDATE Points スライド（表スライド）はノート不要
    if ($title -match "UPDATE.*Points") { continue }

    $hasNotes = $false
    try {
        $notesText = $slide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text
        # 定数から最小ノート長を取得
        if ($notesText.Length -gt $global:MIN_NOTE_LENGTH) {
            $hasNotes = $true
        }
    } catch {}

    if (-not $hasNotes) {
        $missingNotes += $i
    }
}

if ($missingNotes.Count -eq 0) {
    Write-Host "  ✅ 全スライドにスピーカーノートがあります" -ForegroundColor Green
} else {
    Write-Host "  ❌ ノートなし: P$($missingNotes -join ', P')" -ForegroundColor Red
    $errors += "ノートなし: P$($missingNotes -join ', P')"
}

# ========================================
# 検証 5: セクション順序の検証
# ========================================
Write-Host "`n[検証5] セクション順序..." -ForegroundColor Yellow

$expectedSectionOrder = @("表紙", "サマリ", "Weekly New Topics", "UPDATE Points", "Appendix", "Ending")
$actualSections = @()

for ($i = 1; $i -le $pres.SectionProperties.Count; $i++) {
    $actualSections += $pres.SectionProperties.Name($i)
}

$sectionOrderOk = $true
$sectionIssues = @()

# セクション数チェック
if ($actualSections.Count -lt 5) {
    $sectionOrderOk = $false
    $sectionIssues += "セクション数が不足（$($actualSections.Count)個、期待: 5-6個）"
}

# 順序チェック（UPDATE Points が Weekly New Topics の後か）
$weeklyIdx = -1
$updatePointsIdx = -1
for ($i = 0; $i -lt $actualSections.Count; $i++) {
    if ($actualSections[$i] -match "Weekly") { $weeklyIdx = $i }
    if ($actualSections[$i] -match "UPDATE.*Points") { $updatePointsIdx = $i }
}

if ($weeklyIdx -ge 0 -and $updatePointsIdx -ge 0) {
    if ($updatePointsIdx -le $weeklyIdx) {
        $sectionOrderOk = $false
        $sectionIssues += "UPDATE Points が Weekly New Topics より前に配置されている"
    }
}

if ($sectionOrderOk) {
    Write-Host "  ✅ セクション順序が正しい" -ForegroundColor Green
    Write-Host "     現在: $($actualSections -join ' → ')"
} else {
    foreach ($issue in $sectionIssues) {
        Write-Host "  ❌ $issue" -ForegroundColor Red
        $errors += "セクション順序: $issue"
    }
    Write-Host "     期待: $($expectedSectionOrder -join ' → ')" -ForegroundColor Yellow
    Write-Host "     実際: $($actualSections -join ' → ')" -ForegroundColor Yellow
}

# ========================================
# 検証 6: スライド並び順の検証（新規）
# ========================================
Write-Host "`n[検証6] スライド並び順（【廃止】→【GA】→【Preview】→【アナウンス/更新】）..." -ForegroundColor Yellow

# classification.json からラベルマップを構築（キーワードフォールバックより信頼性が高い）
$classLabelMap = @{}
if (Test-Path $classificationPath) {
    $classData = if ($classification) { $classification } else { Get-Content $classificationPath -Encoding UTF8 | ConvertFrom-Json }
    foreach ($w in $classData.weekly) {
        $cleanKey = ($w.title -replace "^【[^】]+】\s*", "").Trim()
        # スマートクォート/ダブルクォートを正規化
        $cleanKey = $cleanKey -replace '[\u201C\u201D\u201E\u201F\u0022]', '"'
        # 先頭30文字をキーにする（部分一致用・衝突防止）
        $prefix = $cleanKey.Substring(0, [Math]::Min(30, $cleanKey.Length)).ToLower()
        $classLabelMap[$prefix] = "【$($w.label)】"
    }
}

$slideOrder = @()
for ($i = $WeeklyStartSlide; $i -le $weeklyEnd; $i++) {
    $slide = $pres.Slides.Item($i)
    $title = try { $slide.Shapes.Title.TextFrame.TextRange.Text } catch { "" }

    $label = "【更新】"
    # 🔴 classification.json があればそこからラベルを取得（最優先）
    if ($classLabelMap.Count -gt 0) {
        $cleanT = ($title -replace "^【[^】]+】\s*", "").Trim()
        # スマートクォート/ダブルクォートを正規化
        $cleanT = $cleanT -replace '[\u201C\u201D\u201E\u201F\u0022]', '"'
        $tPrefix = $cleanT.Substring(0, [Math]::Min(30, $cleanT.Length)).ToLower()
        if ($classLabelMap.ContainsKey($tPrefix)) {
            $label = $classLabelMap[$tPrefix]
        } else {
            # フォールバック: 部分一致検索
            foreach ($key in $classLabelMap.Keys) {
                if ($cleanT.ToLower().Contains($key) -or $key.Contains($tPrefix.Substring(0, [Math]::Min(10, $tPrefix.Length)))) {
                    $label = $classLabelMap[$key]
                    break
                }
            }
        }
    }
    # classification.json がない場合のフォールバック
    if ($label -eq "【更新】" -and $classLabelMap.Count -eq 0) {
        # 🔴 【ラベル】形式を最優先でチェック（タイトル内の「利用可能」等に誤マッチしないよう）
        if ($title -match "^【廃止】") { $label = "【廃止】" }
        elseif ($title -match "^【GA】") { $label = "【GA】" }
        elseif ($title -match "^【Preview】") { $label = "【Preview】" }
        elseif ($title -match "^【アナウンス】") { $label = "【アナウンス】" }
        elseif ($title -match "^【更新】") { $label = "【更新】" }
        # フォールバック: 元スライドのステータス語句で判定
        elseif ($title -match "サービス終了|提供終了|廃止|Retire|retirement|サポート終了|サポートを終了|が.*終了$") { $label = "【廃止】" }
        elseif ($title -match "一般公開|一般提供|利用可能|Generally Available") { $label = "【GA】" }
        elseif ($title -match "プレビュー|Preview|Public Preview|Private Preview") { $label = "【Preview】" }
        elseif ($title -match "アナウンス|Announcement") { $label = "【アナウンス】" }
    }

    $slideOrder += @{ Slide = $i; Label = $label; Title = $title }
}

# 優先順位マッピング
$labelPriority = @{ "【廃止】" = 1; "【GA】" = 2; "【Preview】" = 3; "【アナウンス】" = 4; "【更新】" = 4 }

$orderOk = $true
$lastPriority = 0
foreach ($item in $slideOrder) {
    $priority = $labelPriority[$item.Label]
    if ($priority -lt $lastPriority) {
        $orderOk = $false
        break
    }
    $lastPriority = $priority
}

if ($orderOk) {
    Write-Host "  ✅ スライド並び順が正しい" -ForegroundColor Green
} else {
    Write-Host "  ❌ スライド並び順が不正（【廃止】→【GA】→【Preview】→【アナウンス/更新】の順にすること）" -ForegroundColor Red
    $errors += "スライド並び順: 【廃止】→【GA】→【Preview】→【アナウンス/更新】の順になっていない"
    foreach ($item in $slideOrder) {
        Write-Host "     P$($item.Slide): $($item.Label)" -ForegroundColor Yellow
    }
}

# ========================================
# 検証 7: UPDATE Points 位置の検証（新規）
# ========================================
Write-Host "`n[検証7] UPDATE Points 位置..." -ForegroundColor Yellow

$updatePointsSlideNum = 0
for ($i = 1; $i -le $pres.Slides.Count; $i++) {
    $title = try { $pres.Slides.Item($i).Shapes.Title.TextFrame.TextRange.Text } catch { "" }
    if ($title -match "UPDATE.*Points") {
        $updatePointsSlideNum = $i
        break
    }
}

if ($updatePointsSlideNum -gt 0) {
    if ($updatePointsSlideNum -gt $weeklyEnd) {
        Write-Host "  ✅ UPDATE Points (P$updatePointsSlideNum) は Weekly Topics (P$weeklyEnd) の後に配置" -ForegroundColor Green
    } else {
        Write-Host "  ❌ UPDATE Points (P$updatePointsSlideNum) が Weekly Topics (P$weeklyEnd) の前に配置されている" -ForegroundColor Red
        $errors += "UPDATE Points 位置: Weekly Topics の後に配置すること（現在 P$updatePointsSlideNum）"
    }
} else {
    Write-Host "  ⚠️ UPDATE Points スライドが見つかりません" -ForegroundColor Yellow
    $warnings += "UPDATE Points スライドが見つかりません"
}

# ========================================
# 検証 8: 表内容品質の検証
# ========================================
Write-Host "`n[検証8] UPDATE Points 表の内容品質..." -ForegroundColor Yellow

$qualityIssues = @()

if ($updatePointTables.Count -gt 0) {
    foreach ($tableInfo in $updatePointTables) {
        $table = $tableInfo.Table
        for ($r = 2; $r -le $table.Rows.Count; $r++) {
            $content = $table.Rows.Item($r).Cells(3).Shape.TextFrame.TextRange.Text
            $keypoint = $table.Rows.Item($r).Cells(4).Shape.TextFrame.TextRange.Text
            $updateText = $content

            # コンテンツが汎用的すぎないかチェック（定数から取得）
            foreach ($pattern in $global:FORBIDDEN_CONTENT_PATTERNS) {
                if ($content -match $pattern) {
                    $qualityIssues += "P$($tableInfo.SlideNumber) 行$($r - 1): アップデート内容が汎用的（${content}）"
                }
                if ($keypoint -match $pattern) {
                    $qualityIssues += "P$($tableInfo.SlideNumber) 行$($r - 1): キーポイントが汎用的（${keypoint}）"
                }
            }

            # コンテンツが短すぎないかチェック（10文字未満は警告）
            if ($content.Length -lt 10) {
                $qualityIssues += "P$($tableInfo.SlideNumber) 行$($r - 1): アップデート内容が短すぎる（$($content.Length)文字）"
            }

            # キーポイントが短すぎないかチェック
            if ($keypoint.Length -lt 15) {
                $qualityIssues += "P$($tableInfo.SlideNumber) 行$($r - 1): キーポイントが短すぎる（$($keypoint.Length)文字）"
            }

            if (Test-HasRedundantStatusPrefix -Text $updateText) {
                $qualityIssues += "P$($tableInfo.SlideNumber) 行$($r - 1): アップデート内容にラベル重複表記（${updateText}）"
            }

            # キーポイントがフォールバック汎用文言でないかチェック
            # 🔴 設計変更(2026-03-30): ホワイトリスト方式→NGパターン方式に変更
            # AI生成の具体的な文言は自動通過、Enrichのフォールバック汎用文言のみ検出
            $fallbackPatterns = @(
                "^期限までに移行計画の策定",
                "^本番ワークロードで活用検討",
                "^検証環境での機能評価",
                "^既存環境への適用可否",
                "参考情報$",
                "^.*の参考情報$",
                "^.*の参考事例$",
                "^ログ集計でクエリ性能とコストを改善$",
                "^.*活用の参考情報$",
                "^参考情報として活用可能$"
            )
            $isFallback = $false
            foreach ($pattern in $fallbackPatterns) {
                if ($keypoint -match $pattern) {
                    $isFallback = $true
                    break
                }
            }
            if ($isFallback) {
                $qualityIssues += "P$($tableInfo.SlideNumber) 行$($r - 1): キーポイントがフォールバック汎用文言（${keypoint}）"
            }
        }
    }

    if ($totalUpdatePointRows -ne $WeeklyCount) {
        $qualityIssues += "UPDATE Points 表の総件数が Weekly 件数と不一致（表: $totalUpdatePointRows 件 / Weekly: $WeeklyCount 件）"
    }
}

if ($qualityIssues.Count -eq 0) {
    Write-Host "  ✅ 表の内容品質は適切です" -ForegroundColor Green
} else {
    foreach ($issue in $qualityIssues) {
        Write-Host "  ❌ $issue" -ForegroundColor Red
        $errors += "表品質: $issue"
    }
}

# ========================================
# 検証 9: ノート内容整合性チェック
# ★ 2026-02-16 追加: ノートが別トピックの内容になっていないか検証
# ========================================
Write-Host "`n[検証9] ノート内容整合性..." -ForegroundColor Yellow

$noteMismatch = @()
for ($i = $WeeklyStartSlide; $i -lt $pres.Slides.Count; $i++) {
    $slide = $pres.Slides.Item($i)
    $title = try { $slide.Shapes.Title.TextFrame.TextRange.Text } catch { "" }
    if ($title -eq "" -or $title -match "UPDATE.*Points|Appendix") { continue }
    if ($slide.SlideShowTransition.Hidden -eq -1 -and $i -gt $UpdatePointsSlideNum) { continue }

    try {
        $notesText = $slide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text
        if ($notesText.Length -lt $global:MIN_NOTE_LENGTH) { continue }

        # basics の最初のキーワードがタイトルのトピックと関連しているか確認
        # ノートの basics セクション（最初の200文字）を取得
        $notesHead = $notesText.Substring(0, [Math]::Min(200, $notesText.Length)).ToLower()

        # タイトルの主要サービス名（最初の英単語 or サービス名）がノートに含まれるか
        $titleWords = $title -split '[\s　、。「」のはがをにでともやへから]+' | Where-Object { $_.Length -ge 3 }
        $matchFound = $false
        foreach ($word in $titleWords) {
            if ($notesHead -match [regex]::Escape($word.ToLower())) {
                $matchFound = $true
                break
            }
        }
        if (-not $matchFound) {
            $noteMismatch += "P${i}: タイトル「$($title.Substring(0, [Math]::Min(40, $title.Length)))」のキーワードがノート先頭に見つからない"
        }
    } catch {}
}

if ($noteMismatch.Count -eq 0) {
    Write-Host "  ✅ ノート内容がスライドと整合しています" -ForegroundColor Green
} else {
    foreach ($m in $noteMismatch) {
        Write-Host "  ⚠️ $m" -ForegroundColor Yellow
        $warnings += "ノート不整合の可能性: $m"
    }
}

# ========================================
# 結果サマリ
# ========================================
$pres.Close()
try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres) | Out-Null } catch {}
if ($ownsSession) {
    # Quit しない: ユーザーが同じ PowerPoint プロセスでファイルを開いている可能性がある
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
}

Write-Host "`n========================================" -ForegroundColor Cyan

if ($errors.Count -eq 0) {
    $global:PptxVerifyPassed = $true
    Write-Host "✅ Gate 3 PASSED - 全検証項目をクリア" -ForegroundColor Green
    if ($warnings.Count -gt 0) {
        Write-Host "`n警告 ($($warnings.Count)件):" -ForegroundColor Yellow
        $warnings | ForEach-Object { Write-Host "  ⚠️ $_" -ForegroundColor Yellow }
    }
    if ($NoExit) { return }
    exit 0
} else {
    $global:PptxVerifyPassed = $false
    Write-Host "❌ Gate 3 FAILED - $($errors.Count)件のエラー" -ForegroundColor Red
    Write-Host "`nエラー一覧:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "  ❌ $_" -ForegroundColor Red }
    if ($warnings.Count -gt 0) {
        Write-Host "`n警告 ($($warnings.Count)件):" -ForegroundColor Yellow
        $warnings | ForEach-Object { Write-Host "  ⚠️ $_" -ForegroundColor Yellow }
    }
    Write-Host "`n次のステップに進む前に、上記エラーを修正してください。" -ForegroundColor Red
    if ($NoExit) { return }
    exit 1
}
