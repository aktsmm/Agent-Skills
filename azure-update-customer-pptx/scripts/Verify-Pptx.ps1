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
#   10. テンプレートプレースホルダー残存チェック
#   11. 敬称重複チェック
#   12. 表紙以外の表示スライドに顧客固有語が出ていないこと
#   13. 参照リンク種別と hyperlink
#   14. Ending variants と空プレースホルダー
#   15. Appendix hidden/count 整合性
#   16. リージョン reviewed evidence
#
param(
    [Parameter(Mandatory=$true)]
    [string]$PptxPath,
    
    [int]$WeeklyStartSlide = 3,  # P3からWeekly Topics
    [int]$WeeklyCount = 0,  # 0の場合は自動検出
    [int]$AppendixStartSlide = 0,  # 0の場合は自動検出

    [object]$Session = $null,

    [switch]$DeliveryMode,

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
$ownsSession = $false
$ppt = $Session
if (-not $ppt) {
    $ppt = Get-ActivePptxApplication
}
if (-not $ppt) {
    $ppt = New-PptxSession
    $ownsSession = $true
}
$pres = $ppt.Presentations.Open($PptxPath, $true, $false, $false)  # ReadOnly

Write-Host "`n総スライド数: $($pres.Slides.Count)"

$classificationPath = Join-Path (Split-Path $PptxPath -Parent) "manifest\classification.json"
$classification = $null
if (Test-Path $classificationPath) {
    $classification = Get-Content $classificationPath -Encoding UTF8 | ConvertFrom-Json
}
$expectedWeeklyCount = if ($classification -and $classification.weekly) { @($classification.weekly).Count } else { $WeeklyCount }

function Get-CustomerProfileValueForVerify {
    param(
        [string]$ProfilePath,
        [string]$Field
    )

    if (-not (Test-Path -LiteralPath $ProfilePath)) { return "" }

    $lines = Get-Content -LiteralPath $ProfilePath -Encoding UTF8
    foreach ($line in $lines) {
        if ($line -match "^\|\s*$([regex]::Escape($Field))\s*\|\s*(.*?)\s*\|") {
            return (($Matches[1] -replace '^`|`$', '').Trim())
        }
    }
    return ""
}

function Get-BaseCustomerNameForVerify {
    param([string]$CustomerName)

    $trimmed = ($CustomerName -replace '\s+', ' ').Trim()
    if ($trimmed -match '^(.*?)\s*(御中|様)$') { return $Matches[1].Trim() }
    return $trimmed
}

function Get-CustomerSpecificVisibleTerms {
    param([string]$ProfilePath)

    $terms = New-Object System.Collections.Generic.List[string]
    $customerName = Get-CustomerProfileValueForVerify -ProfilePath $ProfilePath -Field "Customer name"
    $customerBaseName = Get-BaseCustomerNameForVerify -CustomerName $customerName
    $systemName = Get-CustomerProfileValueForVerify -ProfilePath $ProfilePath -Field "System name"
    $tenantDomain = Get-CustomerProfileValueForVerify -ProfilePath $ProfilePath -Field "Tenant domain"
    $tenantId = Get-CustomerProfileValueForVerify -ProfilePath $ProfilePath -Field "Tenant id"

    foreach ($term in @($customerName, $customerBaseName, $systemName, $tenantDomain, $tenantId)) {
        if ($term -and $term.Trim().Length -ge 4 -and -not $terms.Contains($term.Trim())) {
            $terms.Add($term.Trim())
        }
    }

    if (Test-Path -LiteralPath $ProfilePath) {
        $profileText = Get-Content -LiteralPath $ProfilePath -Raw -Encoding UTF8
        foreach ($match in [regex]::Matches($profileText, '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')) {
            $value = $match.Value
            if (-not $terms.Contains($value)) { $terms.Add($value) }
        }
    }

    return @($terms)
}

function Get-MatchingClassificationItem {
    param(
        [string]$Title,
        [object[]]$Items
    )

    $cleanTitle = (Get-CleanSlideTitle -Title $Title -replace '\s+', ' ').Trim().ToLower()
    foreach ($item in @($Items)) {
        $itemTitle = (Get-CleanSlideTitle -Title $item.title -replace '\s+', ' ').Trim().ToLower()
        if ($cleanTitle -eq $itemTitle) { return $item }
    }
    foreach ($item in @($Items)) {
        $itemTitle = (Get-CleanSlideTitle -Title $item.title -replace '\s+', ' ').Trim().ToLower()
        $prefixLength = [Math]::Min(25, [Math]::Min($cleanTitle.Length, $itemTitle.Length))
        if ($prefixLength -gt 0 -and $cleanTitle.Substring(0, $prefixLength) -eq $itemTitle.Substring(0, $prefixLength)) { return $item }
    }
    return $null
}

function Get-SlideText {
    param([object]$Slide, [switch]$IncludeLayout)

    $parts = @()
    foreach ($shape in $Slide.Shapes) {
        if ($shape.HasTextFrame -ne -1) { continue }
        try {
            if ($shape.TextFrame.HasText) { $parts += $shape.TextFrame.TextRange.Text }
        } catch {}
    }
    if ($IncludeLayout) {
        try {
            foreach ($shape in $Slide.CustomLayout.Shapes) {
                if ($shape.HasTextFrame -ne -1) { continue }
                try {
                    if ($shape.TextFrame.HasText) { $parts += $shape.TextFrame.TextRange.Text }
                } catch {}
            }
        } catch {}
    }
    return ($parts -join "`n")
}

function Get-HyperlinkAddressForLabel {
    param(
        [object]$Slide,
        [string]$Label
    )

    foreach ($shape in $Slide.Shapes) {
        if ($shape.HasTextFrame -ne -1) { continue }
        try {
            $range = $shape.TextFrame.TextRange
            $text = $range.Text
            $idx = $text.IndexOf($Label)
            if ($idx -lt 0) { continue }
            $address = $range.Characters($idx + 1, $Label.Length).ActionSettings(1).Hyperlink.Address
            if ($address) { return $address }
        } catch {}
    }
    return ""
}

function Get-ComparableUrlForVerify {
    param([string]$Url)

    if (-not $Url) { return "" }
    $withoutFragment = ($Url -replace '#.*$', '')
    return $withoutFragment.TrimEnd('/')
}

function Test-AzureUpdateEndingSlideForVerify {
    param([object]$Slide)

    try { if ($Slide.CustomLayout.Name -like 'Azure Update Ending*') { return $true } } catch {}
    foreach ($shape in $Slide.Shapes) { if ($shape.Name -like 'Ending-*') { return $true } }
    return $false
}

function Test-AzureUpdateCoverSlideForVerify {
    param([object]$Slide)

    try { if ($Slide.CustomLayout.Name -like 'Azure Update Cover*') { return $true } } catch {}
    foreach ($shape in $Slide.Shapes) { if ($shape.Name -eq 'CoverPanel') { return $true } }
    return $false
}

function Get-EndingVariantNameForVerify {
    param([object]$Slide)

    foreach ($shape in $Slide.Shapes) {
        if ($shape.Name -match 'Indigo') { return 'Indigo Amber' }
        if ($shape.Name -match 'Azure') { return 'Azure Blue' }
        if ($shape.Name -match 'Teal') { return 'Teal Fresh' }
    }
    try {
        if ($Slide.CustomLayout.Name -match 'Indigo') { return 'Indigo Amber' }
        if ($Slide.CustomLayout.Name -match 'Azure') { return 'Azure Blue' }
        if ($Slide.CustomLayout.Name -match 'Teal') { return 'Teal Fresh' }
    } catch {}
    return ''
}

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
    
    # Ending スライドはノート不要
    if (Test-AzureUpdateEndingSlideForVerify -Slide $slide) { continue }

    # 非表示の表紙バリエーションはノート不要
    if ($slide.SlideShowTransition.Hidden -eq -1 -and (Test-AzureUpdateCoverSlideForVerify -Slide $slide)) { continue }
    
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
# 検証 10: テンプレートプレースホルダー残存チェック
# ========================================
Write-Host "`n[検証10] テンプレートプレースホルダー残存チェック..." -ForegroundColor Yellow

$placeholderHits = @()
for ($i = 1; $i -le $pres.Slides.Count; $i++) {
    $slide = $pres.Slides.Item($i)
    foreach ($shape in $slide.Shapes) {
        if ($shape.HasTextFrame -ne -1) { continue }
        try {
            $text = $shape.TextFrame.TextRange.Text
            if ($text -match '\{\{[^}]+\}\}') {
                $sample = ($text -replace "`r|`n", ' ').Trim()
                if ($sample.Length -gt 80) { $sample = $sample.Substring(0, 80) + '...' }
                $placeholderHits += "P${i} $($shape.Name): $sample"
            }
        } catch {}
    }
}

if ($placeholderHits.Count -eq 0) {
    Write-Host "  ✅ テンプレートプレースホルダーは残っていません" -ForegroundColor Green
} else {
    foreach ($hit in $placeholderHits) {
        Write-Host "  ❌ $hit" -ForegroundColor Red
        $errors += "プレースホルダー残存: $hit"
    }
}

# ========================================
# 検証 11: 敬称重複チェック
# ========================================
Write-Host "`n[検証11] 敬称重複チェック..." -ForegroundColor Yellow

$honorificHits = @()
for ($i = 1; $i -le $pres.Slides.Count; $i++) {
    $slide = $pres.Slides.Item($i)
    foreach ($shape in $slide.Shapes) {
        if ($shape.HasTextFrame -ne -1) { continue }
        try {
            $text = $shape.TextFrame.TextRange.Text
            if ($text -match '(御中\s*御中|様\s*様|御中\s*様|様\s*御中)') {
                $sample = ($text -replace "`r|`n", ' ').Trim()
                if ($sample.Length -gt 80) { $sample = $sample.Substring(0, 80) + '...' }
                $honorificHits += "P${i} $($shape.Name): $sample"
            }
        } catch {}
    }
}

if ($honorificHits.Count -eq 0) {
    Write-Host "  ✅ 敬称重複はありません" -ForegroundColor Green
} else {
    foreach ($hit in $honorificHits) {
        Write-Host "  ❌ $hit" -ForegroundColor Red
        $errors += "敬称重複: $hit"
    }
}

# ========================================
# 検証 12: 表紙以外の表示スライドに顧客固有語が出ていないか
# ========================================
Write-Host "`n[検証12] 表示スライドの顧客固有語チェック..." -ForegroundColor Yellow

$workspaceRoot = Split-Path (Split-Path $PptxPath -Parent) -Parent
$profilePath = Join-Path $workspaceRoot ".config\customer-profile.md"
$customerSpecificTerms = Get-CustomerSpecificVisibleTerms -ProfilePath $profilePath
$customerTermHits = @()

if ($customerSpecificTerms.Count -eq 0) {
    Write-Host "  ⚠️ 顧客固有語の検出条件を作成できませんでした" -ForegroundColor Yellow
    $warnings += "顧客固有語チェック条件なし: $profilePath"
} else {
    for ($i = 2; $i -le $pres.Slides.Count; $i++) {
        $slide = $pres.Slides.Item($i)
        if ($slide.SlideShowTransition.Hidden -eq -1) { continue }

        foreach ($shape in $slide.Shapes) {
            if ($shape.HasTextFrame -ne -1) { continue }
            try {
                $text = $shape.TextFrame.TextRange.Text
                foreach ($term in $customerSpecificTerms) {
                    if ($text -and $text.IndexOf($term, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
                        $sample = ($text -replace "`r|`n", ' ').Trim()
                        if ($sample.Length -gt 80) { $sample = $sample.Substring(0, 80) + '...' }
                        $customerTermHits += "P${i} $($shape.Name): '$term' in $sample"
                    }
                }
            } catch {}
        }
    }

    if ($customerTermHits.Count -eq 0) {
        Write-Host "  ✅ 表紙以外の表示スライドに顧客固有語はありません" -ForegroundColor Green
    } else {
        foreach ($hit in $customerTermHits) {
            Write-Host "  ❌ $hit" -ForegroundColor Red
            $errors += "顧客固有語が表示スライド本文に残存: $hit"
        }
    }
}

# ========================================
# 検証 13: 参照リンク種別と hyperlink
# ========================================
Write-Host "`n[検証13] 参照リンク種別と hyperlink..." -ForegroundColor Yellow

$referenceIssues = @()
if ($classification -and $classification.weekly) {
    for ($i = $WeeklyStartSlide; $i -lt $UpdatePointsSlideNum; $i++) {
        $slide = $pres.Slides.Item($i)
        if ($slide.SlideShowTransition.Hidden -eq -1) { continue }
        $title = try { $slide.Shapes.Title.TextFrame.TextRange.Text } catch { "" }
        $item = Get-MatchingClassificationItem -Title $title -Items @($classification.weekly)
        if (-not $item) { continue }

        $slideText = Get-SlideText -Slide $slide
        if ($item.learnUrl -and $slideText -notmatch 'Microsoft Learn') {
            $referenceIssues += "P${i}: Microsoft Learn 詳細ラベルがありません"
        }
        if ($item.sourceUrl -and $slideText -notmatch 'Azure Updates') {
            $referenceIssues += "P${i}: Azure Updates 発表ラベルがありません"
        }

        if ($item.learnUrl) {
            $learnAddress = Get-HyperlinkAddressForLabel -Slide $slide -Label 'Microsoft Learn'
            if (-not $learnAddress) { $referenceIssues += "P${i}: Microsoft Learn ラベルに hyperlink がありません" }
            elseif ((Get-ComparableUrlForVerify $learnAddress) -ne (Get-ComparableUrlForVerify $item.learnUrl)) { $referenceIssues += "P${i}: Microsoft Learn hyperlink 不一致 ($learnAddress)" }
        }
        if ($item.sourceUrl) {
            $sourceAddress = Get-HyperlinkAddressForLabel -Slide $slide -Label 'Azure Updates'
            if (-not $sourceAddress) { $referenceIssues += "P${i}: Azure Updates ラベルに hyperlink がありません" }
            elseif ((Get-ComparableUrlForVerify $sourceAddress) -ne (Get-ComparableUrlForVerify $item.sourceUrl)) { $referenceIssues += "P${i}: Azure Updates hyperlink 不一致 ($sourceAddress)" }
        }
    }
}

if ($referenceIssues.Count -eq 0) {
    Write-Host "  ✅ 参照リンク種別と hyperlink は明確です" -ForegroundColor Green
} else {
    foreach ($issue in $referenceIssues) {
        Write-Host "  ❌ $issue" -ForegroundColor Red
        $errors += "参照リンク: $issue"
    }
}

# ========================================
# 検証 14: Ending variants と空プレースホルダー
# ========================================
Write-Host "`n[検証14] Ending variants と空プレースホルダー..." -ForegroundColor Yellow

$endingIssues = @()
$endingSlides = @()
$visibleEndingSlides = @()
for ($i = 1; $i -le $pres.Slides.Count; $i++) {
    $slide = $pres.Slides.Item($i)
    if (-not (Test-AzureUpdateEndingSlideForVerify -Slide $slide)) { continue }
    $endingSlides += [pscustomobject]@{ Index = $i; Slide = $slide; Hidden = ($slide.SlideShowTransition.Hidden -eq -1); Variant = (Get-EndingVariantNameForVerify -Slide $slide) }
    if ($slide.SlideShowTransition.Hidden -ne -1) { $visibleEndingSlides += $endingSlides[-1] }
}

if ($visibleEndingSlides.Count -ne 1) {
    $endingIssues += "表示 Ending は 1 枚である必要があります（現在 $($visibleEndingSlides.Count) 枚）"
}
if ($endingSlides.Count -lt 3) {
    $endingIssues += "Ending variants が 3 枚未満です（現在 $($endingSlides.Count) 枚）"
}

foreach ($ending in $endingSlides) {
    $slide = $ending.Slide
    # 結び見出し・ヘッダーは layout 側に配置されているため、layout の text も含めて検査する
    $text = (Get-SlideText -Slide $slide -IncludeLayout).Trim()
    if (-not $ending.Hidden) {
        # 新デザイン：結び見出し 'AZURE UPDATE 情報 END' と、底部ヘッダー 'Microsoft Azure' のいずれかを確認。
        # 旧デザイン：'Azure アップデート情報' を受入れ。
        if ($text -notmatch 'AZURE\s*UPDATE\s*情報|Azure\s*アップデート情報') { $endingIssues += "P$($ending.Index): 結び見出し（AZURE UPDATE 情報 または Azure アップデート情報）がありません" }
        if ($text -match 'Next Steps|TBD|\[EDIT ME\]|Click here') { $endingIssues += "P$($ending.Index): テンプレート scaffolding 文言が残っています" }
    }
    # Ending-Title / Ending-Subtitle オーバーレイ shape は layout 内容と重複していたため撤去済み。
    # 現在は layout 自体が結び見出しとヘッダーを提供するので、shape 存在チェックは行わない。
}

$visibleCoverVariant = ''
for ($i = 1; $i -le $pres.Slides.Count; $i++) {
    $slide = $pres.Slides.Item($i)
    if ($slide.SlideShowTransition.Hidden -eq -1) { continue }
    try {
        if ($slide.CustomLayout.Name -like 'Azure Update Cover*') {
            if ($slide.CustomLayout.Name -match 'Indigo') { $visibleCoverVariant = 'Indigo Amber' }
            elseif ($slide.CustomLayout.Name -match 'Azure') { $visibleCoverVariant = 'Azure Blue' }
            elseif ($slide.CustomLayout.Name -match 'Teal') { $visibleCoverVariant = 'Teal Fresh' }
            break
        }
    } catch {}
}
# Cover と表示 Ending のカラーバリアント一致を確認（layout 名ベース）。
if ($visibleCoverVariant -and $visibleEndingSlides.Count -eq 1) {
    $visibleEndingLayoutName = ''
    try { $visibleEndingLayoutName = $visibleEndingSlides[0].Slide.CustomLayout.Name } catch {}
    $expectedSuffix = $visibleCoverVariant
    if ($visibleEndingLayoutName -and ($visibleEndingLayoutName -notmatch [regex]::Escape($expectedSuffix))) {
        $endingIssues += "表示 Cover ($visibleCoverVariant) と表示 Ending ($visibleEndingLayoutName) のカラーバリアントが一致しません"
    }
}

if ($endingIssues.Count -eq 0) {
    Write-Host "  ✅ Ending variants は formal closure として整っています" -ForegroundColor Green
} else {
    foreach ($issue in $endingIssues) {
        Write-Host "  ❌ $issue" -ForegroundColor Red
        $errors += "Ending: $issue"
    }
}

# ========================================
# 検証 15: Appendix hidden/count 整合性
# ========================================
Write-Host "`n[検証15] Appendix hidden/count 整合性..." -ForegroundColor Yellow

$appendixIssues = @()
$expectedAppendixCount = if ($classification -and $classification.appendix) { @($classification.appendix).Count } else { 0 }
$hiddenAppendixSlides = @()

if ($updatePointsSlideNum -gt 0) {
    for ($i = $updatePointsSlideNum + 1; $i -le $pres.Slides.Count; $i++) {
        $slide = $pres.Slides.Item($i)
        if ($slide.SlideShowTransition.Hidden -ne -1) { continue }
        if (Test-AzureUpdateCoverSlideForVerify -Slide $slide) { continue }
        if (Test-AzureUpdateEndingSlideForVerify -Slide $slide) { continue }
        $hiddenAppendixSlides += $i
    }
}

if ($expectedAppendixCount -ne $hiddenAppendixSlides.Count) {
    $appendixIssues += "classification Appendix 件数 ($expectedAppendixCount) と hidden Appendix slide 数 ($($hiddenAppendixSlides.Count)) が一致しません"
}

if ($classification -and $classification.appendix) {
    for ($i = 1; $i -le $pres.Slides.Count; $i++) {
        $slide = $pres.Slides.Item($i)
        if ($slide.SlideShowTransition.Hidden -eq -1) { continue }
        $title = try { $slide.Shapes.Title.TextFrame.TextRange.Text } catch { "" }
        if (-not $title) { continue }
        $appendixItem = Get-MatchingClassificationItem -Title $title -Items @($classification.appendix)
        if ($appendixItem) { $appendixIssues += "P${i}: Appendix item が表示スライドに残っています ($title)" }
    }
}

if ($appendixIssues.Count -eq 0) {
    Write-Host "  ✅ Appendix slides は hidden で classification と整合しています" -ForegroundColor Green
} else {
    foreach ($issue in $appendixIssues) {
        Write-Host "  ❌ $issue" -ForegroundColor Red
        $errors += "Appendix: $issue"
    }
}

# ========================================
# 検証 16: リージョン reviewed evidence
# ========================================
Write-Host "`n[検証16] リージョン reviewed evidence..." -ForegroundColor Yellow

$dateFolder = Split-Path $PptxPath -Parent
$regionReviewedPath = Join-Path $dateFolder 'manifest\region_info_reviewed.json'
$regionReviewedIssues = @()

if (Test-Path -LiteralPath $regionReviewedPath) {
    try {
        $reviewed = Get-Content -LiteralPath $regionReviewedPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $regionsObject = if ($reviewed.PSObject.Properties['regions']) { $reviewed.regions } elseif ($reviewed.PSObject.Properties['services']) { $reviewed.services } else { $reviewed }
        $missingEvidence = @()
        foreach ($prop in $regionsObject.PSObject.Properties) {
            $info = $prop.Value
            if (-not $info.PSObject.Properties['verified'] -or $info.verified -ne $true -or -not $info.evidence -or -not $info.source) {
                $missingEvidence += $prop.Name
            }
        }
        if ($missingEvidence.Count -gt 0) {
            $regionReviewedIssues += "region_info_reviewed.json に verified/evidence/source 不足があります: $($missingEvidence -join ', ')"
        }
    } catch {
        $regionReviewedIssues += "region_info_reviewed.json を解析できません: $($_.Exception.Message)"
    }
} elseif ($DeliveryMode) {
    $regionReviewedIssues += "DeliveryMode では region_info_reviewed.json が必須です"
} else {
    $warnings += "region_info_reviewed.json がありません。リージョンスタンプは初期 region_info.json 判定です。顧客提出前に Review-agent MCP 検証を実施してください。"
}

if ($regionReviewedIssues.Count -eq 0) {
    if (Test-Path -LiteralPath $regionReviewedPath) {
        Write-Host "  ✅ region_info_reviewed.json の reviewed evidence を確認しました" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ reviewed region evidence は未作成です（draft warning）" -ForegroundColor Yellow
    }
} else {
    foreach ($issue in $regionReviewedIssues) {
        Write-Host "  ❌ $issue" -ForegroundColor Red
        $errors += "Region reviewed: $issue"
    }
}

# ========================================
# 結果サマリ
# ========================================
$pres.Close()
try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres) | Out-Null } catch {}
if ($ownsSession) {
    try { $ppt.Quit() } catch {}
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
} elseif (-not $Session -and $ppt) {
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
