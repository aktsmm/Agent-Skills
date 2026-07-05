<#
.SYNOPSIS
    Enrich-CustomerPptx.ps1 - 顧客向け PPTX のコンテンツ充実
.DESCRIPTION
    1. P2 目次を項番形式で更新
    2. UPDATE Points 表を更新
    3. リージョンスタンプを追加
    4. スピーカーノートを追加
.PARAMETER DateFolder
    日付フォルダ（例: 0120）のパス
.EXAMPLE
    .\Enrich-CustomerPptx.ps1 -DateFolder "C:\...\2026\0120"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$DateFolder,

    [string]$PptxPath = "",

    [object]$Session = $null,

    [switch]$ClosePresentation
)

$ErrorActionPreference = "Stop"

# モジュール読み込み
Import-Module "$PSScriptRoot\PptxCommon.psm1" -Force

Write-StepHeader "Enrich-CustomerPptx.ps1"

# ============================================================
# パス設定（絶対パスに変換 - COM操作に必須）
# config.json から設定を読み込み
# ============================================================

$DateFolder = (Resolve-Path $DateFolder).Path
$basePath = Split-Path $DateFolder -Parent
$configPath = "$basePath\.config\config.json"

# config.json 読み込み
if (-not (Test-Path $configPath)) {
    Write-Failure "config.json が見つかりません: $configPath"
    exit 1
}
$config = Get-Content $configPath -Encoding UTF8 | ConvertFrom-Json

# パス設定（config.json から取得）
$dateString = Split-Path $DateFolder -Leaf
$outputFileName = $config.output.fileNamePattern -replace '\{year\}', $config.output.year -replace '\{date\}', $dateString
$outputPath = if ([string]::IsNullOrWhiteSpace($PptxPath)) { "$DateFolder\$outputFileName" } else { (Resolve-Path $PptxPath).Path }
$manifestFolder = "$DateFolder\manifest"
$classificationPath = "$manifestFolder\classification.json"
# 🔴 Review Agent 検証済みファイルを優先使用
$regionInfoReviewedPath = "$manifestFolder\region_info_reviewed.json"
$regionInfoPath = if (Test-Path $regionInfoReviewedPath) { $regionInfoReviewedPath } else { "$manifestFolder\region_info.json" }
$notesPath = "$manifestFolder\notes.json"

Write-Info "対象ファイル: $outputPath"

# ============================================================
# classification.json & region_info.json 読み込み
# ============================================================

$classification = Get-Content $classificationPath -Encoding UTF8 | ConvertFrom-Json
Write-Info "Weekly: $($classification.weekly.Count) 件"

# region_info.json / region_info_reviewed.json を読み込み（リージョン情報を正確に取得）
# 📌 SSOT: スキーマ定義は .github/skills/azure-update-customer-pptx/references/region-stamp.md を参照
# 形式: { "regions": { "タイトル": { "japanEast": bool, "japanWest": bool, "status": "...", ... } } }
$regionInfo = @{}
if (Test-Path $regionInfoPath) {
    $regionData = Get-Content $regionInfoPath -Encoding UTF8 | ConvertFrom-Json

    # region_info_reviewed.json は services または regions プロパティ内にネスト
    $regionsObject = if ($regionData.PSObject.Properties["services"]) {
        $regionData.services
    } elseif ($regionData.PSObject.Properties["regions"]) {
        $regionData.regions
    } else {
        $regionData
    }

    foreach ($prop in $regionsObject.PSObject.Properties) {
        $title = $prop.Name
        $info = $prop.Value

        # stamp フィールドがあれば優先使用（reviewed.json）、なければ生成
        # 🔴 テンプレート準拠の文字列形式（絵文字なし、日本語表記）
        # 🔴 status フィールドを優先チェック（グローバルサービスの正しい判定）
        $regionStatus = ""
        if ($info.stamp) {
            # stamp フィールドが明示的に設定されている場合
            $regionStatus = $info.stamp
        } elseif ($info.status -match "グローバル|全リージョン") {
            # status フィールドでグローバルと判定されている場合（廃止通知など）
            $regionStatus = "グローバル"
        } elseif ($info.japanEast -and $info.japanWest) {
            $regionStatus = "Japan East / West 対応"
        } elseif ($info.japanEast) {
            $regionStatus = "Japan East のみ対応"
        } elseif ($info.japanWest) {
            $regionStatus = "Japan West のみ対応"
        } elseif ($info.global -or $info.note -match "グローバル|全リージョン" -or $info.evidence -match "グローバル|全リージョン") {
            # 旧形式互換：global フラグ、note、evidence でグローバル判定
            $regionStatus = "グローバル"
        } else {
            # Japan East/West 両方 false → 日本未対応
            $regionStatus = "日本リージョン未対応"
        }

        $regionInfo[$title] = @{
            regionStatus = $regionStatus
            japanEast = $info.japanEast
            japanWest = $info.japanWest
            note = $info.note
            url = $info.source
        }
    }
    Write-Info "region_info: $($regionInfo.Count) 件（ファイル: $(Split-Path $regionInfoPath -Leaf)）"
}

# notes.json を読み込み（AIエージェントが生成した4観点ノート）
# 形式: { "weekly": [...], "appendix": [...] }
$notesData = $null
$weeklyNotes = @{}
$appendixNotes = @{}
if (Test-Path $notesPath) {
    $notesData = Get-Content $notesPath -Encoding UTF8 | ConvertFrom-Json

    # タイトルをキーにマップ化
    foreach ($n in $notesData.weekly) {
        $weeklyNotes[$n.title] = $n
    }
    foreach ($n in $notesData.appendix) {
        $appendixNotes[$n.title] = $n
    }
    Write-Info "notes.json: Weekly $($notesData.weekly.Count) 件, Appendix $($notesData.appendix.Count) 件"
} else {
    Write-Warning "notes.json が見つかりません。スピーカーノートは基本情報のみになります。"
}

# ============================================================
# PPTX 操作
# ============================================================

$ppt = $null
$pres = $null
$ownsSession = $null -eq $Session

try {
    if (-not $Session) {
        Close-OpenPptxPresentation -PptxPath $outputPath -Save | Out-Null
    }
    $ppt = if ($Session) { $Session } else { New-PptxSession }
    $pres = $ppt.Presentations.Open($outputPath)

    Write-Info "スライド数: $($pres.Slides.Count)"

    # ----------------------------------------------------------
    # Phase 1: スライド構造分析
    # ----------------------------------------------------------

    Write-StepHeader "Phase 1: スライド構造分析"

    $structure = @{
        WeeklyStart = 3
        WeeklyEnd = 0
        UpdatePointsSlide = 0
        AppendixStart = 0
    }

    function Test-AzureUpdateCoverSlide {
        param([object]$Slide)
        try { if ($Slide.CustomLayout.Name -like 'Azure Update Cover*') { return $true } } catch {}
        foreach ($shape in $Slide.Shapes) { if ($shape.Name -eq 'CoverPanel') { return $true } }
        return $false
    }

    function Test-AzureUpdateEndingSlide {
        param([object]$Slide)
        try { if ($Slide.CustomLayout.Name -like 'Azure Update Ending*') { return $true } } catch {}
        return $false
    }

    for ($i = 1; $i -le $pres.Slides.Count; $i++) {
        $slide = $pres.Slides.Item($i)
        $title = Get-SlideTitle -Slide $slide

        # 🔴 修正: "UPDATE Points" または "今週のUPDATE" で完全一致に近いマッチング
        # "プライベート エンドポイント" などの誤検知を防止
        if ($title -match "^(UPDATE Points|今週のUPDATE)" -and $structure.UpdatePointsSlide -eq 0) {
            $structure.UpdatePointsSlide = $i
            $structure.WeeklyEnd = $i - 1
        }
        # Appendix は UPDATE Points セクションの後にある、非表示かつ表紙/Ending ではない本文から開始
        if ($structure.AppendixStart -eq 0 -and $structure.UpdatePointsSlide -gt 0 -and $i -gt $structure.UpdatePointsSlide) {
            if ($slide.SlideShowTransition.Hidden -eq -1 -and -not (Test-AzureUpdateCoverSlide -Slide $slide) -and -not (Test-AzureUpdateEndingSlide -Slide $slide) -and $title -notmatch "^(UPDATE Points|今週のUPDATE)") {
                $structure.AppendixStart = $i
            }
        }
    }

    Write-Host "  Weekly: P$($structure.WeeklyStart)〜P$($structure.WeeklyEnd)"
    Write-Host "  UPDATE Points: P$($structure.UpdatePointsSlide)"
    Write-Host "  Appendix: P$($structure.AppendixStart)〜"

    # ----------------------------------------------------------
    # Phase 2: P2 目次更新
    # ----------------------------------------------------------

    Write-StepHeader "Phase 2: P2 目次更新"

    # 目次内容を構築（classification.json から）
    # 🔴 改善: スクリプトでは文字詰めしない（インストラクションで制御）
    $tocItems = @()
    $num = 1
    foreach ($w in $classification.weekly) {
        $cleanTitle = Get-CleanSlideTitle -Title $w.title
        # タイトルをそのまま使用（文字数はインストラクションで制御）
        $tocItems += "$num. 【$($w.label)】$cleanTitle"
        $num++
    }

    $tocHeader = "■ 今週の Weekly New Topics（$($classification.weekly.Count) 件）"
    $tocContent = $tocHeader + "`n`n" + ($tocItems -join "`n")

    # P2 のテキストボックスを更新
    # 再実行耐性: Shape.Name で識別し、タイトル以外の全テキストボックスを
    # 先にクリアしてから最大のものに書き込む（2回実行で重複書き込みを防止）
    # 表紙複数枚対応: Azure Update Cover レイアウト（旧テンプレでは CoverPanel）を除外し、
    # 最初に登場する非表紙スライド（=サマリ）を対象にする
    $summaryIdx = 0
    for ($si = 1; $si -le $pres.Slides.Count; $si++) {
        $sl = $pres.Slides.Item($si)
        $isCover = $false
        try { if ($sl.CustomLayout.Name -like 'Azure Update Cover*') { $isCover = $true } } catch {}
        if (-not $isCover) { foreach ($sh in $sl.Shapes) { if ($sh.Name -eq 'CoverPanel') { $isCover = $true; break } } }
        if (-not $isCover) { $summaryIdx = $si; break }
    }
    if ($summaryIdx -eq 0) { $summaryIdx = 2 }
    $p2 = $pres.Slides.Item($summaryIdx)
    $tocShape = $null
    $maxArea = 0
    $contentBoxes = @()

    foreach ($shape in $p2.Shapes) {
        if ($shape.HasTextFrame -eq -1 -and $shape.Name -ne "Title 1") {
            $contentBoxes += $shape
            $isContentPlaceholder = $false
            try { if ($shape.PlaceholderFormat.Type -eq 7) { $isContentPlaceholder = $true } } catch {}
            if ($isContentPlaceholder) {
                $tocShape = $shape
                break
            }
            if ($shape.Width * $shape.Height -gt $maxArea) {
                $maxArea = $shape.Width * $shape.Height
                $tocShape = $shape
            }
        }
    }

    # タイトル以外の全テキストボックスをクリア（再実行時の重複防止）
    foreach ($box in $contentBoxes) {
        if ($box.Name -ne $tocShape.Name) {
            try { $box.TextFrame.TextRange.Text = "" } catch {}
        }
    }

    if ($tocShape) {
        $tocShape.TextFrame.TextRange.Text = $tocContent
        $tocShape.TextFrame.TextRange.Font.Size = 24
        try {
            $tocShape.TextFrame.TextRange.Font.NameFarEast = 'BIZ UDPゴシック'
            $tocShape.TextFrame.TextRange.Font.Name = 'BIZ UDPゴシック'
        } catch {}
        Write-Success "目次更新完了（$($tocShape.Name) / 24pt / BIZ UDPゴシック）"
    } else {
        Write-Warning "目次テキストボックスが見つかりません"
    }

    # ----------------------------------------------------------
    # Phase 3: UPDATE Points 表更新
    # ----------------------------------------------------------

    Write-StepHeader "Phase 3: UPDATE Points 表更新"

    $updatePointsSlide = $pres.Slides.Item($structure.UpdatePointsSlide)
    $tableShape = $null

    foreach ($shape in $updatePointsSlide.Shapes) {
        if ($shape.HasTable -eq -1) {
            $tableShape = $shape
            break
        }
    }

    if ($tableShape) {
        $table = $tableShape.Table
        Write-Host "  表: $($table.Rows.Count) 行 x $($table.Columns.Count) 列"

        if (Update-UpdatePointsTableContent -Presentation $pres -Classification $classification -RegionInfo $regionInfo) {
            Write-Success "UPDATE Points 表更新完了"
        } else {
            Write-Warning "UPDATE Points 表の更新に失敗しました"
        }
    } else {
        Write-Warning "UPDATE Points 表が見つかりません"
    }

    # ----------------------------------------------------------
    # Phase 4: リージョンスタンプ追加（Weekly + Appendix）
    # ----------------------------------------------------------

    Write-StepHeader "Phase 4: リージョンスタンプ追加"

    $stampCount = 0

    # Weekly スライドにスタンプ追加
    for ($i = $structure.WeeklyStart; $i -le $structure.WeeklyEnd; $i++) {
        $slide = $pres.Slides.Item($i)
        $title = Get-SlideTitle -Slide $slide

        # 共通関数でリージョン情報を取得
        $region = Find-RegionStatus -Title $title -RegionInfo $regionInfo

        Add-RegionStamp -Slide $slide -RegionText $region | Out-Null
        Write-Host "  P$i (Weekly): $region"
        $stampCount++
    }

    # Appendix スライドにスタンプ追加（Appendix ヘッダーと Ending は除く）
    if ($structure.AppendixStart -gt 0) {
        for ($i = $structure.AppendixStart; $i -lt $pres.Slides.Count; $i++) {
            $slide = $pres.Slides.Item($i)
            $title = Get-SlideTitle -Slide $slide

            # Ending/空白スライドは除外
            if ([string]::IsNullOrWhiteSpace($title)) { continue }
            if (Test-AzureUpdateCoverSlide -Slide $slide) { continue }
            if (Test-AzureUpdateEndingSlide -Slide $slide) { continue }

            # 共通関数でリージョン情報を取得
            $region = Find-RegionStatus -Title $title -RegionInfo $regionInfo

            Add-RegionStamp -Slide $slide -RegionText $region | Out-Null
            Write-Host "  P$i (Appendix): $region"
            $stampCount++
        }
    }

    Write-Success "リージョンスタンプ追加完了（$stampCount 件）"

    # ----------------------------------------------------------
    # Phase 5: スピーカーノート追加
    # 🔴 notes.json + classification.json + region_info.json から機械的に書き込み
    # ----------------------------------------------------------

    Write-StepHeader "Phase 5: スピーカーノート追加"

    $noteCount = 0

    # classification.json から各スライドの情報マップを作成
    $weeklyInfoMap = @{}
    foreach ($w in $classification.weekly) {
        $weeklyInfoMap[$w.title] = $w
    }

    $appendixInfoMap = @{}
    foreach ($a in $classification.appendix) {
        $appendixInfoMap[$a.title] = $a
    }

    for ($i = 1; $i -le $pres.Slides.Count; $i++) {
        $slide = $pres.Slides.Item($i)
        $title = Get-SlideTitle -Slide $slide
        $cleanTitle = $title -replace "^【[^】]+】\s*", ""

        $note = ""

        if ($i -eq 1) {
            # 表紙スライド
            $note = "Weekly Topics: $($classification.weekly.Count) 件"
        }
        elseif ($i -eq 2) {
            # サマリスライド
            $summaryItems = @()
            $num = 1
            foreach ($w in $classification.weekly) {
                $wTitle = Get-CleanSlideTitle -Title $w.title
                $summaryItems += "$num. 【$($w.label)】$wTitle"
                $num++
            }
            $note = "■ 今週の Weekly Topics（$($classification.weekly.Count) 件）`n`n$($summaryItems -join "`n")"
        }
        elseif ($i -ge $structure.WeeklyStart -and $i -le $structure.WeeklyEnd) {
            # Weekly スライド - classification.json + notes.json から情報を取得
            # 共通関数で classification.json と notes.json から情報を取得
            $wInfo = Find-ByPartialTitle -Title $cleanTitle -Map $weeklyInfoMap -MatchLength 20
            $nInfo = Find-ByPartialTitle -Title $cleanTitle -Map $weeklyNotes -MatchLength 15

            # リージョン情報を取得（参考URL用）
            $regionEntry = Find-ByPartialTitle -Title $cleanTitle -Map $regionInfo -MatchLength 15
            $regionUrl = if ($regionEntry) { $regionEntry.url } else { "" }
            $referenceUrl = if ($nInfo -and $nInfo.PSObject.Properties['referenceUrl'] -and $nInfo.referenceUrl) { $nInfo.referenceUrl } else { $regionUrl }

            # 🔴 ノート組み立て（notes.json の 5 観点のみ）
            # スライド上で確認できる情報（概要・ラベル・リージョン）は記載しない
            $noteLines = @()

            # notes.json から 5 観点を追加
            if ($nInfo) {
                # 🆕 basics（基礎知識・キーワード解説）を先頭に追加
                if ($nInfo.basics -and $nInfo.basics.Count -gt 0) {
                    $noteLines += "■ 基礎知識（そもそもこれって何？）"
                    foreach ($b in $nInfo.basics) {
                        $noteLines += "・$b"
                    }
                    $noteLines += ""
                }
                $noteLines += "■ ユーザー価値"
                $noteLines += $nInfo.userValue
                $noteLines += ""
                $noteLines += "■ 技術・仕組み"
                $noteLines += $nInfo.technical
                $noteLines += ""
                $noteLines += "■ Before/After"
                $noteLines += $nInfo.beforeAfter
                # 🆕 systemImpact（現行システムへの影響）を追加
                if ($nInfo.systemImpact) {
                    $noteLines += ""
                    $noteLines += "■ 顧客システムへの影響"
                    $noteLines += $nInfo.systemImpact
                }
                # 🆕 customerConcerns（想定 Q&A）を追加
                if ($nInfo.customerConcerns -and $nInfo.customerConcerns.Count -gt 0) {
                    $noteLines += ""
                    $noteLines += "■ 想定 Q&A"
                    foreach ($qa in $nInfo.customerConcerns) {
                        $noteLines += "・$qa"
                    }
                }
                # 🆕 notes.json がある場合でも classification.json のキーポイント・選定理由を追加
                if ($wInfo -and $wInfo.keypoint) {
                    $noteLines += ""
                    $noteLines += "■ キーポイント"
                    $noteLines += $wInfo.keypoint
                    # 選定理由は改行なしで続ける
                    if ($wInfo.justification) {
                        $noteLines += "■ 選定理由: $($wInfo.justification)"
                    }
                }
            } else {
                # notes.json がない場合は classification.json の情報を使用
                if ($wInfo -and $wInfo.keypoint) {
                    $noteLines += "■ キーポイント"
                    $noteLines += $wInfo.keypoint
                    if ($wInfo.justification) {
                        $noteLines += "■ 選定理由: $($wInfo.justification)"
                    }
                }
            }

            # 参考URLを追加
            if ($referenceUrl) {
                $noteLines += ""
                $noteLines += "■ 参考URL"
                $noteLines += $referenceUrl
            }

            $note = $noteLines -join "`n"
        }
        elseif ($title -match "UPDATE Points") {
            # UPDATE Points スライド - ★印の項目を詳しく解説するガイドを生成
            $noteLines = @()
            $noteLines += "■ 今週のポイント（$($classification.weekly.Count) 件）"

            # ラベル別に集計
            $labelCounts = @{}
            $starDetails = @()
            $nonStarItems = @()
            foreach ($w in $classification.weekly) {
                $label = $w.label
                if (-not $labelCounts.ContainsKey($label)) { $labelCounts[$label] = 0 }
                $labelCounts[$label]++

                # ★印の項目を詳しく解説
                if ($w.keypoint -match "^★") {
                    $shortTitle = $w.title
                    if ($shortTitle.Length -gt 30) { $shortTitle = $shortTitle.Substring(0, 30) + "…" }

                    # キーポイントから★を除去
                    $keypointContent = $w.keypoint -replace "^★\s*", ""

                    # 共通関数で notes.json から詳細情報を取得
                    $nInfo = Find-ByPartialTitle -Title $w.title -Map $weeklyNotes -MatchLength 15

                    $starDetails += ""
                    $starDetails += "【$($w.label)】$shortTitle"
                    $starDetails += "  ポイント: $keypointContent"
                    $starDetails += "  選定理由: $($w.justification)"

                    # notes.json からの詳細
                    if ($nInfo) {
                        if ($nInfo.userValue) {
                            $starDetails += "  お客様メリット: $($nInfo.userValue)"
                        }
                        if ($nInfo.systemImpact) {
                            $starDetails += "  顧客システムへの影響: $($nInfo.systemImpact)"
                        }
                        # 想定質問（廃止情報の場合）
                        if ($w.label -eq "廃止") {
                            $starDetails += "  ※想定質問: 「うちは影響ある？」「いつまでに対応？」"
                        }
                    }
                } else {
                    $shortTitle = $w.title
                    if ($shortTitle.Length -gt 25) { $shortTitle = $shortTitle.Substring(0, 25) + "…" }
                    $nonStarItems += "・$shortTitle（$($w.keypoint)）"
                }
            }

            # ラベル別件数
            $labelSummary = ($labelCounts.GetEnumerator() | ForEach-Object { "$($_.Key): $($_.Value)件" }) -join "、"
            $noteLines += $labelSummary

            # ★印の項目（特に丁寧に説明）
            if ($starDetails.Count -gt 0) {
                $starCount = ($starDetails | Where-Object { $_ -match "^【" }).Count
                $noteLines += ""
                $noteLines += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                $noteLines += "■ ★印は特に丁寧に説明（$starCount 件）"
                $noteLines += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                $noteLines += $starDetails
            }

            # ★なしの項目（参考情報）
            if ($nonStarItems.Count -gt 0) {
                $noteLines += ""
                $noteLines += "■ 参考情報（時間があれば）"
                $noteLines += $nonStarItems
            }

            # 説明の流れ
            $noteLines += ""
            $noteLines += "■ 説明の流れ"
            $noteLines += "1. 廃止情報から先に（影響有無を明確に）"
            $noteLines += "2. ★印の活用推奨機能を紹介"
            $noteLines += "3. 参考情報は時間があれば"

            $note = $noteLines -join "`n"
        }
        elseif ($i -ge $structure.AppendixStart -and $structure.AppendixStart -gt 0 -and -not [string]::IsNullOrWhiteSpace($title) -and -not (Test-AzureUpdateCoverSlide -Slide $slide) -and -not (Test-AzureUpdateEndingSlide -Slide $slide)) {
            # Appendix コンテンツスライド - 共通関数で情報を取得
            $aInfo = Find-ByPartialTitle -Title $cleanTitle -Map $appendixInfoMap -MatchLength 20
            $nInfo = Find-ByPartialTitle -Title $cleanTitle -Map $appendixNotes -MatchLength 15

            # 🔴 修正: classification.json では justification を使用、notes.json では excludeReason を使用
            $excludeReason = ""
            if ($nInfo -and $nInfo.excludeReason) {
                $excludeReason = $nInfo.excludeReason
            } elseif ($aInfo -and $aInfo.justification) {
                $excludeReason = $aInfo.justification
            } elseif ($aInfo -and $aInfo.excludeReason) {
                $excludeReason = $aInfo.excludeReason
            } else {
                $excludeReason = "優先度判定による"
            }

            # 🔴 ノート組み立て（Appendix 配置理由 + notes.json の 5 観点）
            $noteLines = @()
            $noteLines += "■ Appendix 配置理由"
            $noteLines += $excludeReason

            # notes.json から 5 観点を追加
            if ($nInfo) {
                # 🆕 basics（基礎知識・キーワード解説）を追加
                if ($nInfo.basics -and $nInfo.basics.Count -gt 0) {
                    $noteLines += ""
                    $noteLines += "■ 基礎知識（そもそもこれって何？）"
                    foreach ($b in $nInfo.basics) {
                        $noteLines += "・$b"
                    }
                }
                $noteLines += ""
                $noteLines += "■ ユーザー価値"
                $noteLines += $nInfo.userValue
                $noteLines += ""
                $noteLines += "■ 技術・仕組み"
                $noteLines += $nInfo.technical
                $noteLines += ""
                $noteLines += "■ Before/After"
                $noteLines += $nInfo.beforeAfter
                # 🆕 systemImpact（現行システムへの影響）を追加
                if ($nInfo.systemImpact) {
                    $noteLines += ""
                    $noteLines += "■ 顧客システムへの影響"
                    $noteLines += $nInfo.systemImpact
                }
                # 🆕 notes.json がある場合でも classification.json のキーポイントを追加
                if ($aInfo -and $aInfo.keypoint) {
                    $noteLines += ""
                    $noteLines += "■ キーポイント"
                    $noteLines += $aInfo.keypoint
                    if ($aInfo.justification) {
                        $noteLines += "■ 選定理由: $($aInfo.justification)"
                    }
                }
            } else {
                # 🔴 フォールバック: notes.json にマッチしなかった場合は classification.json から情報を使用
                if ($aInfo -and $aInfo.keypoint) {
                    $noteLines += ""
                    $noteLines += "■ キーポイント"
                    $noteLines += $aInfo.keypoint
                    if ($aInfo.justification) {
                        $noteLines += "■ 選定理由: $($aInfo.justification)"
                    }
                }
            }

            $note = $noteLines -join "`n"
        }
        elseif ($i -eq $pres.Slides.Count) {
            # Ending スライド - ノート不要
            $note = ""
        }

        if ($note.Length -gt 10) {
            Set-SpeakerNote -Slide $slide -NoteText $note | Out-Null
            Write-Host "  P$i : ノート更新"
            $noteCount++
        } else {
            $dispTitle = if ($title.Length -gt 30) { $title.Substring(0, 30) } else { $title }
            Write-Host "  P$i : スキップ（$dispTitle）"
        }
    }

    Write-Success "スピーカーノート更新完了（$noteCount 件）"

    # ----------------------------------------------------------
    # 保存
    # ----------------------------------------------------------

    Write-StepHeader "保存"

    $pres.Save()
    Write-Success "保存完了: $outputPath"

    # ----------------------------------------------------------
    # 最終確認
    # ----------------------------------------------------------

    Write-StepHeader "最終スライド構成"

    for ($i = 1; $i -le $pres.Slides.Count; $i++) {
        $slide = $pres.Slides.Item($i)
        $title = Get-SlideTitle -Slide $slide
        $hidden = if ($slide.SlideShowTransition.Hidden -eq -1) { " [非表示]" } else { "" }
        $displayTitle = if ($title.Length -gt 50) { $title.Substring(0, 50) + "..." } else { $title }
        Write-Host "  P$i$hidden : $displayTitle"
    }

    Write-Host ""
    Write-Host "次のステップ: Verify-Pptx.ps1 -PptxPath `"$outputPath`"" -ForegroundColor Cyan

} catch {
    Write-Failure "エラー発生: $_"
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
} finally {
    if ($ClosePresentation -and $pres) {
        try { $pres.Close() } catch {}
        try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres) | Out-Null } catch {}
    }
    if ($ClosePresentation -and $ownsSession -and $ppt) {
        try { $ppt.Quit() } catch {}
        try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null } catch {}
    }

    if ($ClosePresentation) {
        Write-Info "PowerPoint を閉じました。"
    } else {
        Write-Info "PowerPoint は開いたままです。確認後、手動で閉じてください。"
    }
}

