<#
.SYNOPSIS
    Build-CustomerPptx.ps1 - 顧客向け PPTX を構築
.DESCRIPTION
    1. classification.json を読み込み
    2. テンプレートをコピー
    3. 正しい順序でスライドを挿入（【廃止】→【GA】→【Preview】→【更新】）
    4. セクション構成を設定
.PARAMETER DateFolder
    日付フォルダ（例: 0120）のパス
.EXAMPLE
    .\Build-CustomerPptx.ps1 -DateFolder "C:\...\2026\0120"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$DateFolder,

    [object]$Session = $null,

    [switch]$ClosePresentation
)

$ErrorActionPreference = "Stop"

# モジュール読み込み
Import-Module "$PSScriptRoot\PptxCommon.psm1" -Force

Write-StepHeader "Build-CustomerPptx.ps1"

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
$templatePath = "$basePath\$($config.template.folder)\$($config.template.fileName)"
$manifestFolder = "$DateFolder\manifest"
$classificationPath = "$manifestFolder\classification.json"

# 出力ファイル名（config.json のパターンから生成）
$dateString = Split-Path $DateFolder -Leaf
$outputFileName = $config.output.fileNamePattern -replace '\{year\}', $config.output.year -replace '\{date\}', $dateString
$outputPath = "$DateFolder\$outputFileName"

Write-Info "テンプレート: $templatePath"
Write-Info "分類ファイル: $classificationPath"
Write-Info "出力先: $outputPath"

# ============================================================
# classification.json 読み込み
# ============================================================

if (-not (Test-Path $classificationPath)) {
    Write-Failure "classification.json が見つかりません。先に Prepare-CustomerPptx.ps1 を実行してください。"
    exit 1
}

$classification = Get-Content $classificationPath -Encoding UTF8 | ConvertFrom-Json

Write-Info "Weekly: $($classification.weekly.Count) 件"
Write-Info "Appendix: $($classification.appendix.Count) 件"

# MCP fetched モード必須（本文レイアウト生成方式）
$fetchedPath = Join-Path $DateFolder 'manifest\fetched-updates.json'
if (-not (Test-Path $fetchedPath)) {
    Write-Failure "MCP fetched-updates.json が見つかりません。先に Fetch-AzureUpdates.ps1 を実行してください: $fetchedPath"
    exit 1
}
Write-Info "Build モード: MCP fetched（本文レイアウト生成）"

function Set-ClassifiedSlideTitle {
    param(
        [object]$Slide,
        [object]$Entry
    )

    if (-not $Slide -or -not $Entry -or -not $Entry.title) { return }

    $currentTitle = Get-SlideTitle -Slide $Slide
    $currentClean = Get-CleanSlideTitle -Title $currentTitle
    $desiredTitle = [string]$Entry.title
    $desiredClean = Get-CleanSlideTitle -Title $desiredTitle

    if ($desiredClean -and $desiredClean -ne $currentClean) {
        try {
            $Slide.Shapes.Title.TextFrame.TextRange.Text = $desiredTitle
        } catch {
            Write-Warning "スライドタイトル更新に失敗: $desiredTitle"
        }
    }
}

# ============================================================
# テンプレートコピー
# ============================================================

Close-OpenPptxPresentation -PptxPath $outputPath | Out-Null

if (Test-Path $outputPath) {
    Remove-Item $outputPath -Force
}
Copy-Item $templatePath $outputPath -Force
Write-Success "テンプレートコピー完了"

# ============================================================
# PPTX 構築
# ============================================================

$ppt = $null
$output = $null
$ownsSession = $null -eq $Session

try {
    $ppt = if ($Session) { $Session } else { New-PptxSession }
    $output = $ppt.Presentations.Open($outputPath)
    $placeholderValues = Get-TemplatePlaceholderValues -WorkspaceRoot $basePath -DateFolder $DateFolder
    $placeholderCount = Replace-TemplatePlaceholders -Presentation $output -Placeholders $placeholderValues
    Write-Info "テンプレートプレースホルダー置換: $placeholderCount 件"
    
    Write-Info "テンプレート: $($output.Slides.Count) スライド"
    
    # ----------------------------------------------------------
    # Phase 1: テンプレート分析
    # ----------------------------------------------------------
    
    Write-StepHeader "Phase 1: テンプレート分析"
    
    $templateInfo = @{
        CoverSlide = 1
        CoverSlides = @()
        SummarySlide = 2
        UpdatePointsSlide = 0
        EndingSlide = $output.Slides.Count
        EndingSlides = @()
        SamplesToDelete = @()
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
        foreach ($shape in $Slide.Shapes) { if ($shape.Name -like 'Ending-*') { return $true } }
        return $false
    }

    function Get-AzureUpdateLayout {
        param([object]$Presentation, [string]$Name)
        for ($li = 1; $li -le $Presentation.SlideMaster.CustomLayouts.Count; $li++) {
            $layout = $Presentation.SlideMaster.CustomLayouts.Item($li)
            if ($layout.Name -eq $Name) { return $layout }
        }
        throw "テンプレート内にレイアウト '$Name' が見つかりません"
    }

    $bodyLayout = Get-AzureUpdateLayout -Presentation $output -Name 'Azure Update Body'

    # 表紙群を検出: レイアウト名を優先し、旧テンプレ互換で CoverPanel も許容
    for ($i = 1; $i -le $output.Slides.Count; $i++) {
        $slide = $output.Slides.Item($i)
        if (Test-AzureUpdateCoverSlide -Slide $slide) { $templateInfo.CoverSlides += $i }
    }
    if ($templateInfo.CoverSlides.Count -eq 0) { $templateInfo.CoverSlides = @(1) }  # 後方互換
    $templateInfo.CoverSlide = $templateInfo.CoverSlides[0]
    $templateInfo.SummarySlide = $templateInfo.CoverSlides[-1] + 1
    
    for ($i = 1; $i -le $output.Slides.Count; $i++) {
        $slide = $output.Slides.Item($i)
        $title = Get-SlideTitle -Slide $slide
        
        # 🔴 「ポイント」だけでマッチすると「エンドポイント」等を誤検出
        if ($title -match "UPDATE\s*Points|UPDATE.*ポイント|今週の.*ポイント") {
            $templateInfo.UpdatePointsSlide = $i
            Write-Host "  P$i : UPDATE Points"
        }
        elseif ($templateInfo.CoverSlides -contains $i) {
            $hidden = if ($slide.SlideShowTransition.Hidden) { '非表示' } else { '表示' }
            Write-Host "  P$i : 表紙 [$hidden]"
        }
        elseif ($i -eq $templateInfo.SummarySlide) {
            Write-Host "  P$i : サマリ（$title）"
        }
        elseif (Test-AzureUpdateEndingSlide -Slide $slide) {
            $hidden = if ($slide.SlideShowTransition.Hidden) { '非表示' } else { '表示' }
            Write-Host "  P$i : Ending"
        }
        else {
            Write-Host "  P$i : $title"
        }
    }

    if ($templateInfo.UpdatePointsSlide -eq 0) {
        throw "テンプレート内に UPDATE Points スライドが見つかりません"
    }

    # Ending variants を検出。新テンプレートでは複数 Ending sample slides を許容する。
    $detectedEndingSlides = @()
    for ($i = $templateInfo.UpdatePointsSlide + 1; $i -le $output.Slides.Count; $i++) {
        $slide = $output.Slides.Item($i)
        $title = Get-SlideTitle -Slide $output.Slides.Item($i)
        if ((Test-AzureUpdateEndingSlide -Slide $slide) -or [string]::IsNullOrWhiteSpace($title) -or $title -match "^Ending$|^End$|おわり|ご清聴|以上") {
            $detectedEndingSlides += $i
        }
    }
    if ($detectedEndingSlides.Count -gt 0) {
        $templateInfo.EndingSlides = @($detectedEndingSlides)
        $templateInfo.EndingSlide = @($detectedEndingSlides)[0]
        Write-Info "Ending 候補を検出: $(@($detectedEndingSlides) -join ', ')"
    }

    # 表紙・サマリ・UPDATE Points・Ending 以外は、前回生成物やサンプルが混入していても全削除する
    # 表紙は複数枚のことがある（C 表示 + A/B 非表示）ので CoverSlides を全て保持
    $keepSlides = @($templateInfo.CoverSlides) + @($templateInfo.EndingSlides) + @($templateInfo.SummarySlide, $templateInfo.UpdatePointsSlide, $templateInfo.EndingSlide)

    Write-Info "本文レイアウト: $($bodyLayout.Name)"

    $templateInfo.SamplesToDelete = @()
    for ($i = 1; $i -le $output.Slides.Count; $i++) {
        if ($keepSlides -notcontains $i) {
            $templateInfo.SamplesToDelete += $i
        }
    }
    
    # ----------------------------------------------------------
    # Phase 2: サンプルスライド削除
    # ----------------------------------------------------------
    
    Write-StepHeader "Phase 2: サンプルスライド削除"
    
    # 後ろから削除
    $templateInfo.SamplesToDelete | Sort-Object -Descending | ForEach-Object {
        Write-Host "  削除: P$_"
        $output.Slides.Item($_).Delete()
        Start-Sleep -Milliseconds 50
    }
    
    Write-Success "現在 $($output.Slides.Count) スライド"
    
    # ----------------------------------------------------------
    # Phase 3: MCP fetched mode
    # ----------------------------------------------------------
    
    Write-StepHeader "Phase 3: MCP fetched mode"
    Write-Info "MCP 取得データから本文レイアウトでスライドを生成します。"
    
    # ----------------------------------------------------------
    # Phase 4: Weekly スライド挿入（P3 から）
    # ----------------------------------------------------------
    
    Write-StepHeader "Phase 4: Weekly Topics 挿入"
    
    # 挿入位置（サマリの後。表紙複数枚ありでも動的に決定）
    # Phase 2 でサンプルを削除した後の最新 SummarySlide 位置を取り直す
    # 🔴 表紙群にも 'Weekly New Topics' バッジが入っているため、表紙は除外して検索する
    $coverIds = @($templateInfo.CoverSlides)
    $summaryPosNow = 0
    for ($i = 1; $i -le $output.Slides.Count; $i++) {
        if ($coverIds -contains $i) { continue }
        $sl = $output.Slides.Item($i)
        if (Test-AzureUpdateCoverSlide -Slide $sl) { continue }
        $t = Get-SlideTitle -Slide $sl
        if ($t -match "Weekly\s*News\s*Topics|今週のトピックス|Summary") { $summaryPosNow = $i; break }
    }
    if ($summaryPosNow -eq 0) { $summaryPosNow = $templateInfo.SummarySlide }
    $insertPos = $summaryPosNow + 1
    Write-Info "本文挿入位置: P$insertPos（サマリ P$summaryPosNow の直後）"
    
    # classification.json の weekly は既にソート済み（Prepare で labelPriority, title 順）
    foreach ($w in $classification.weekly) {
        # 本文レイアウトから新規スライドを追加 → 挿入位置へ移動 → 内容流し込み
        $output.Slides.AddSlide($output.Slides.Count + 1, $bodyLayout) | Out-Null
        $output.Slides.Item($output.Slides.Count).MoveTo($insertPos)
        $newSlide = $output.Slides.Item($insertPos)
        # タイトルは titleJa を優先（日本語表示）、なければ title にフォールバック
        $wDisplayTitle = if ($w.titleJa) { $w.titleJa } else { $w.title }
        Set-BodySlideContent -Slide $newSlide -Title $wDisplayTitle -TargetService $w.targetService `
            -Background $w.background -Before $w.before -After $w.after -CustomerImpact $w.customerImpact -Pricing $w.pricing -JapanRegion $w.japanRegion `
            -JapanRegionUrl $w.japanRegionUrl `
            -BodyContent $w.bodyContent -LearnUrl $w.learnUrl -SourceUrl $w.sourceUrl | Out-Null
        Set-StatusBadge -Slide $newSlide -Label $w.label | Out-Null
        $newSlide.SlideShowTransition.Hidden = 0  # Weekly は表示
        $currentTitle = Get-SlideTitle -Slide $newSlide
        Write-Host "  P$insertPos : $($currentTitle.Substring(0, [Math]::Min(60, $currentTitle.Length)))..."
        $insertPos++
    }
    
    $weeklyEndPos = $insertPos - 1
    Write-Success "Weekly Topics: $($classification.weekly.Count) 件 (P3〜P$weeklyEndPos)"
    
    # ----------------------------------------------------------
    # 🔴 スライド数チェック（重複コピー防止）
    # ----------------------------------------------------------
    
    $expectedSlides = 2 + $classification.weekly.Count + 2  # 表紙+サマリ + Weekly + UPDATE Points + Ending
    $actualSlides = $output.Slides.Count
    
    # 許容範囲: 期待値の ±20% まで（サンプル削除分の誤差を考慮）
    $tolerance = [Math]::Ceiling($expectedSlides * 0.5)
    if ($actualSlides -gt ($expectedSlides + $tolerance)) {
        Write-Failure "🔴 スライド数異常検出: 期待 ~$expectedSlides 枚、実際 $actualSlides 枚"
        Write-Failure "   重複コピーの可能性があります。処理を中断します。"
        throw "スライド重複エラー: 期待 ~$expectedSlides 枚、実際 $actualSlides 枚"
    }
    
    Write-Info "スライド数チェック OK: $actualSlides 枚（期待: ~$expectedSlides 枚）"
    
    # ----------------------------------------------------------
    # Phase 5: UPDATE Points を Weekly の直後に移動
    # ----------------------------------------------------------
    
    Write-StepHeader "Phase 5: UPDATE Points 位置調整"
    
    # UPDATE Points の現在位置を検出
    # 🔴 「ポイント」だけでマッチすると「エンドポイント」等を誤検出するため、
    #    「UPDATE Points」または「UPDATE.*ポイント」で厳密にマッチ
    $updatePointsCurrentPos = 0
    for ($i = 1; $i -le $output.Slides.Count; $i++) {
        $title = Get-SlideTitle -Slide $output.Slides.Item($i)
        if ($title -match "UPDATE\s*Points|UPDATE.*ポイント|今週の.*ポイント") {
            $updatePointsCurrentPos = $i
            break
        }
    }
    
    # 正しい位置は Weekly の直後（$weeklyEndPos + 1）
    $updatePointsTargetPos = $weeklyEndPos + 1
    
    if ($updatePointsCurrentPos -ne $updatePointsTargetPos -and $updatePointsCurrentPos -gt 0) {
        Write-Info "UPDATE Points を P$updatePointsCurrentPos から P$updatePointsTargetPos へ移動"
        
        # スライドを移動（MoveTo メソッドを使用）
        $output.Slides.Item($updatePointsCurrentPos).MoveTo($updatePointsTargetPos)
        Start-Sleep -Milliseconds 200
        
        $updatePointsPos = $updatePointsTargetPos
    } else {
        $updatePointsPos = $updatePointsCurrentPos
    }
    
    Write-Success "UPDATE Points: P$updatePointsPos"
    
    # ----------------------------------------------------------
    # Phase 6: Appendix 挿入
    # ----------------------------------------------------------
    
    Write-StepHeader "Phase 6: Appendix 挿入"
    
    # Appendix 挿入位置（UPDATE Points の後）
    # 注: Appendixヘッダースライドは追加しない（ユーザー要件: 17枚構成）
    $appendixInsertPos = $updatePointsPos + 1
    
    # Appendix スライド挿入
    foreach ($a in $classification.appendix) {
        $output.Slides.AddSlide($output.Slides.Count + 1, $bodyLayout) | Out-Null
        $output.Slides.Item($output.Slides.Count).MoveTo($appendixInsertPos)
        $newSlide = $output.Slides.Item($appendixInsertPos)
        # タイトルは titleJa を優先（日本語表示）、なければ title にフォールバック
        $aDisplayTitle = if ($a.titleJa) { $a.titleJa } else { $a.title }
        Set-BodySlideContent -Slide $newSlide -Title $aDisplayTitle -TargetService $a.targetService `
            -Background $a.background -Before $a.before -After $a.after -CustomerImpact $a.customerImpact -Pricing $a.pricing -JapanRegion $a.japanRegion `
            -JapanRegionUrl $a.japanRegionUrl `
            -BodyContent $a.bodyContent -LearnUrl $a.learnUrl -SourceUrl $a.sourceUrl | Out-Null
        Set-StatusBadge -Slide $newSlide -Label $a.label | Out-Null
        $newSlide.SlideShowTransition.Hidden = -1
        Write-Host "  P$appendixInsertPos : [非表示] $($aDisplayTitle.Substring(0, [Math]::Min(40, $aDisplayTitle.Length)))..."
        $appendixInsertPos++
    }
    
    Write-Success "Appendix: $($classification.appendix.Count) 件"
    
    # ----------------------------------------------------------
    # 🔴 表紙バリエーション（非表示）を末尾へ移動
    #    既定表示の表紙C のみ先頭、非表示の表紙A/B は Ending の後ろに退避する
    #    （顧客提示順を妨げず、表紙バリエーションは末尾で参照可能にする）
    # ----------------------------------------------------------
    $variantCoverIds = @()
    for ($i = 1; $i -le $output.Slides.Count; $i++) {
        $sl = $output.Slides.Item($i)
        $isCover = Test-AzureUpdateCoverSlide -Slide $sl
        if (-not $isCover) { continue }
        if ($sl.SlideShowTransition.Hidden) { $variantCoverIds += $sl.SlideID }
    }
    foreach ($sid in $variantCoverIds) {
        $idx = Find-SlideIndexById -Presentation $output -SlideId $sid
        if ($idx -gt 0) {
            $output.Slides.Item($idx).MoveTo($output.Slides.Count)
            Write-Host "  表紙バリエーション SlideID=$sid を末尾へ移動"
        }
    }

    # ----------------------------------------------------------
    # 🔴 最終スライド数チェック
    # ----------------------------------------------------------
    
    $coverCount = if ($templateInfo.CoverSlides) { $templateInfo.CoverSlides.Count } else { 1 }
    $endingCount = if ($templateInfo.EndingSlides) { @($templateInfo.EndingSlides).Count } else { 1 }
    $finalExpected = $coverCount + 1 + $classification.weekly.Count + 1 + $classification.appendix.Count + $endingCount  # 表紙群 + サマリ + Weekly + UPDATE Points + Appendix + Ending variants
    $finalActual = $output.Slides.Count
    
    if ($finalActual -gt ($finalExpected + 5)) {
        Write-Warning "⚠️ スライド数が期待値より多い: 期待 $finalExpected 枚、実際 $finalActual 枚"
        Write-Warning "   重複や余分なスライドがある可能性があります。"
    } else {
        Write-Success "最終スライド数: $finalActual 枚（期待: $finalExpected 枚）"
    }
    
    # ----------------------------------------------------------
    # Phase 7: セクション構成
    # ----------------------------------------------------------
    
    Write-StepHeader "Phase 7: セクション構成"
    
    # 表紙群 / サマリ / Weekly 開始 / UPDATE Points / Appendix(最初の非表示本文) / Ending を動的検出
    $visibleCoverEnd = 0
    $variantCoverStart = 0
    $summaryPos = 0
    $weeklyStart = 0
    $updatePointsPos = 0
    $appendixStart = 0
    $endingPos = $output.Slides.Count

    # 表紙レイアウトを持つ連続表紙範囲（表示中）と、末尾に退避された非表示表紙の開始位置
    $reachedNonCover = $false
    for ($i = 1; $i -le $output.Slides.Count; $i++) {
        $sl = $output.Slides.Item($i)
        $isCover = Test-AzureUpdateCoverSlide -Slide $sl
        if ($isCover -and -not $reachedNonCover) {
            $visibleCoverEnd = $i
        } elseif (-not $isCover) {
            $reachedNonCover = $true
        } elseif ($isCover -and $reachedNonCover -and $variantCoverStart -eq 0) {
            $variantCoverStart = $i
        }
    }

    # サマリ = 表紙群直後の非表示でない 1 枚（Weekly News Topics タイトル想定）
    $summaryPos = $visibleCoverEnd + 1
    $weeklyStart = $summaryPos + 1

    # UPDATE Points / Appendix / Ending を Title or 非表示遷移で検出
    for ($i = $weeklyStart; $i -le $output.Slides.Count; $i++) {
        $title = Get-SlideTitle -Slide $output.Slides.Item($i)
        if ($updatePointsPos -eq 0 -and $title -match "UPDATE\s*Points|UPDATE.*ポイント|今週の.*ポイント") {
            $updatePointsPos = $i
        }
        if ($appendixStart -eq 0 -and $i -gt $updatePointsPos -and $updatePointsPos -gt 0 -and $output.Slides.Item($i).SlideShowTransition.Hidden -eq -1) {
            # 表紙/Ending バリエーションは Appendix にしない
            $sl = $output.Slides.Item($i)
            $isCover = Test-AzureUpdateCoverSlide -Slide $sl
            $isEnding = Test-AzureUpdateEndingSlide -Slide $sl
            if (-not $isCover -and -not $isEnding) { $appendixStart = $i }
        }
    }
    # Ending = 最初の表示 Ending variant。なければ最後の非表紙スライド。
    $endingPos = 0
    for ($i = 1; $i -le $output.Slides.Count; $i++) {
        $sl = $output.Slides.Item($i)
        if ((Test-AzureUpdateEndingSlide -Slide $sl) -and $sl.SlideShowTransition.Hidden -ne -1) { $endingPos = $i; break }
    }
    for ($i = $output.Slides.Count; $i -ge 1; $i--) {
        if ($endingPos -gt 0) { break }
        $sl = $output.Slides.Item($i)
        $isCover = Test-AzureUpdateCoverSlide -Slide $sl
        if (-not $isCover) { $endingPos = $i; break }
    }

    Write-Host "  表紙(表示): P1..P$visibleCoverEnd / サマリ: P$summaryPos / Weekly開始: P$weeklyStart"
    Write-Host "  UPDATE Points: P$updatePointsPos / Appendix開始: P$appendixStart / Ending: P$endingPos / 表紙バリエ開始: P$variantCoverStart"

    # 既存セクション削除
    for ($i = $output.SectionProperties.Count; $i -ge 1; $i--) {
        $output.SectionProperties.Delete($i, $false)
    }

    # セクション追加（順序厳守: 必ず若い位置から AddBeforeSlide）
    $output.SectionProperties.AddBeforeSlide(1, "表紙")
    $output.SectionProperties.AddBeforeSlide($summaryPos, "サマリ")
    $output.SectionProperties.AddBeforeSlide($weeklyStart, "Weekly New Topics")
    if ($updatePointsPos -gt 0) {
        $output.SectionProperties.AddBeforeSlide($updatePointsPos, "UPDATE Points")
    }
    if ($appendixStart -gt 0) {
        $output.SectionProperties.AddBeforeSlide($appendixStart, "Appendix")
    }
    $output.SectionProperties.AddBeforeSlide($endingPos, "Ending")
    if ($variantCoverStart -gt 0) {
        $output.SectionProperties.AddBeforeSlide($variantCoverStart, "表紙バリエーション")
    }

    Write-Success "セクション構成完了"
    
    # ----------------------------------------------------------
    # 最終確認
    # ----------------------------------------------------------
    
    Write-StepHeader "最終確認"
    
    Write-Host "--- スライド一覧 ---"
    for ($i = 1; $i -le $output.Slides.Count; $i++) {
        $slide = $output.Slides.Item($i)
        $title = Get-SlideTitle -Slide $slide
        $hidden = if ($slide.SlideShowTransition.Hidden -eq -1) { " [非表示]" } else { "" }
        $displayTitle = if ($title.Length -gt 60) { $title.Substring(0, 60) + "..." } else { $title }
        Write-Host "  P$i$hidden : $displayTitle"
    }
    
    # ----------------------------------------------------------
    # 保存
    # ----------------------------------------------------------
    
    $output.Save()
    Write-Success "保存完了: $outputPath"
    Write-Host ""
    Write-Host "次のステップ: Enrich-CustomerPptx.ps1 -DateFolder `"$DateFolder`"" -ForegroundColor Cyan

} catch {
    Write-Failure "エラー発生: $_"
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    throw
} finally {
    if ($ClosePresentation -and $output) {
        try { $output.Close() } catch {}
        try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($output) | Out-Null } catch {}
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
