<#
.SYNOPSIS
    Fix-NoteMismatch.ps1 - P7/P10/P12 のスピーカーノート不整合を修正
.DESCRIPTION
    notes.json のタイトルとスライドタイトルを正規化して正確にマッチさせ、
    正しいノート内容を書き込む。
    
    根本原因: Find-ByPartialTitle の -match がサブストリングマッチを行い、
    "Application Gateway" を含む複数タイトルで誤マッチが発生した。
.PARAMETER DateFolder
    日付フォルダ（絶対パスまたは相対パス）
.PARAMETER TargetSlides
    修正対象のスライド番号（カンマ区切り）
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$DateFolder,
    
    [int[]]$TargetSlides = @(7, 10, 12)
)

$ErrorActionPreference = "Stop"

# モジュール読み込み
Import-Module "$PSScriptRoot\PptxCommon.psm1" -Force

Write-StepHeader "Fix-NoteMismatch.ps1"

# パス設定
$DateFolder = (Resolve-Path $DateFolder).Path
$basePath = Split-Path $DateFolder -Parent
$configPath = "$basePath\.config\config.json"
$config = Get-Content $configPath -Encoding UTF8 | ConvertFrom-Json

$dateString = Split-Path $DateFolder -Leaf
$outputFileName = $config.output.fileNamePattern -replace '\{year\}', $config.output.year -replace '\{date\}', $dateString
$outputPath = "$DateFolder\$outputFileName"
$manifestFolder = "$DateFolder\manifest"
$classificationPath = "$manifestFolder\classification.json"
$notesPath = "$manifestFolder\notes.json"
$regionInfoReviewedPath = "$manifestFolder\region_info_reviewed.json"
$regionInfoPath = if (Test-Path $regionInfoReviewedPath) { $regionInfoReviewedPath } else { "$manifestFolder\region_info.json" }

Write-Info "対象ファイル: $outputPath"
Write-Info "修正対象スライド: $($TargetSlides -join ', ')"

# ============================================================
# JSON 読み込み
# ============================================================

$classification = Get-Content $classificationPath -Encoding UTF8 | ConvertFrom-Json
$notesData = Get-Content $notesPath -Encoding UTF8 | ConvertFrom-Json

# region_info 読み込み
$regionInfo = @{}
if (Test-Path $regionInfoPath) {
    $regionData = Get-Content $regionInfoPath -Encoding UTF8 | ConvertFrom-Json
    $regionsObject = if ($regionData.PSObject.Properties["services"]) { $regionData.services }
                     elseif ($regionData.PSObject.Properties["regions"]) { $regionData.regions }
                     else { $regionData }
    foreach ($prop in $regionsObject.PSObject.Properties) {
        $regionInfo[$prop.Name] = $prop.Value
    }
}

# ============================================================
# 🔴 正規化関数（スマートクォート・NBSP・全角スペース対応）
# ============================================================
function Get-NormalizedTitle {
    param([string]$Text)
    $t = $Text -replace "^【[^】]+】\s*", ""       # ラベル除去
    $t = $t -replace "\u00A0", " "                   # NBSP → 通常スペース
    $t = $t -replace "[\u201C\u201D]", '"'           # スマートダブルクォート
    $t = $t -replace "[\u2018\u2019]", "'"           # スマートシングルクォート
    $t = $t -replace "\u3000", " "                   # 全角スペース→半角
    $t = $t -replace "\s+", " "                      # 連続スペース正規化
    $t = $t.Trim()
    return $t
}

# ============================================================
# 🔴 正確なタイトルマッチング（サブストリングではなく正規化一致）
# ============================================================
function Find-ExactNoteEntry {
    param(
        [string]$SlideTitle,
        [array]$NotesArray
    )
    
    $normalizedSlide = Get-NormalizedTitle $SlideTitle
    
    # Phase 1: 完全一致
    foreach ($entry in $NotesArray) {
        $normalizedEntry = Get-NormalizedTitle $entry.title
        if ($normalizedSlide -eq $normalizedEntry) {
            return $entry
        }
    }
    
    # Phase 2: 先頭30文字プレフィックス一致（先頭のみ、サブストリングではない）
    foreach ($entry in $NotesArray) {
        $normalizedEntry = Get-NormalizedTitle $entry.title
        $len = [Math]::Min(30, [Math]::Min($normalizedSlide.Length, $normalizedEntry.Length))
        if ($normalizedSlide.Substring(0, $len).ToLower() -eq $normalizedEntry.Substring(0, $len).ToLower()) {
            return $entry
        }
    }
    
    return $null
}

function Find-ExactClassificationEntry {
    param(
        [string]$SlideTitle,
        [array]$ClassificationArray
    )
    
    $normalizedSlide = Get-NormalizedTitle $SlideTitle
    
    foreach ($entry in $ClassificationArray) {
        $normalizedEntry = Get-NormalizedTitle $entry.title
        if ($normalizedSlide -eq $normalizedEntry) {
            return $entry
        }
    }
    
    foreach ($entry in $ClassificationArray) {
        $normalizedEntry = Get-NormalizedTitle $entry.title
        $len = [Math]::Min(30, [Math]::Min($normalizedSlide.Length, $normalizedEntry.Length))
        if ($normalizedSlide.Substring(0, $len).ToLower() -eq $normalizedEntry.Substring(0, $len).ToLower()) {
            return $entry
        }
    }
    
    return $null
}

function Find-ExactRegionEntry {
    param(
        [string]$SlideTitle,
        [hashtable]$RegionMap
    )
    
    $normalizedSlide = Get-NormalizedTitle $SlideTitle
    
    foreach ($key in $RegionMap.Keys) {
        $normalizedKey = Get-NormalizedTitle $key
        if ($normalizedSlide -eq $normalizedKey) {
            return $RegionMap[$key]
        }
    }
    
    foreach ($key in $RegionMap.Keys) {
        $normalizedKey = Get-NormalizedTitle $key
        $len = [Math]::Min(30, [Math]::Min($normalizedSlide.Length, $normalizedKey.Length))
        if ($normalizedSlide.Substring(0, $len).ToLower() -eq $normalizedKey.Substring(0, $len).ToLower()) {
            return $RegionMap[$key]
        }
    }
    
    return $null
}

# ============================================================
# ノート組み立て関数（Enrich-CustomerPptx.ps1 と同一フォーマット）
# ============================================================
function Build-WeeklyNote {
    param(
        [object]$NoteInfo,
        [object]$ClassInfo,
        [object]$RegionEntry
    )
    
    $noteLines = @()
    
    if ($NoteInfo) {
        # basics
        if ($NoteInfo.basics -and $NoteInfo.basics.Count -gt 0) {
            $noteLines += "■ 基礎知識（そもそもこれって何？）"
            foreach ($b in $NoteInfo.basics) {
                $noteLines += "・$b"
            }
            $noteLines += ""
        }
        $noteLines += "■ ユーザー価値"
        $noteLines += $NoteInfo.userValue
        $noteLines += ""
        $noteLines += "■ 技術・仕組み"
        $noteLines += $NoteInfo.technical
        $noteLines += ""
        $noteLines += "■ Before/After"
        $noteLines += $NoteInfo.beforeAfter
        
        if ($NoteInfo.systemImpact) {
            $noteLines += ""
            $noteLines += "■ 顧客システムへの影響"
            $noteLines += $NoteInfo.systemImpact
        }
        
        if ($NoteInfo.customerConcerns -and $NoteInfo.customerConcerns.Count -gt 0) {
            $noteLines += ""
            $noteLines += "■ 想定 Q&A"
            foreach ($qa in $NoteInfo.customerConcerns) {
                # customerConcerns がオブジェクト(question/answer)か文字列かを判定
                if ($qa.PSObject.Properties["question"]) {
                    $noteLines += "・Q: $($qa.question) → A: $($qa.answer)"
                } else {
                    $noteLines += "・$qa"
                }
            }
        }
        
        if ($ClassInfo -and $ClassInfo.keypoint) {
            $noteLines += ""
            $noteLines += "■ キーポイント"
            $noteLines += $ClassInfo.keypoint
            if ($ClassInfo.justification) {
                $noteLines += "■ 選定理由: $($ClassInfo.justification)"
            }
        }
    }
    
    # 参考URL
    $url = ""
    if ($NoteInfo -and $NoteInfo.referenceUrl) {
        $url = $NoteInfo.referenceUrl
    } elseif ($RegionEntry -and $RegionEntry.source) {
        $url = $RegionEntry.source
    }
    if ($url) {
        $noteLines += ""
        $noteLines += "■ 参考URL"
        $noteLines += $url
    }
    
    return ($noteLines -join "`n")
}

# ============================================================
# PPTX 操作
# ============================================================

$ppt = $null
$pres = $null

try {
    Close-OpenPptxPresentation -PptxPath $outputPath -Save | Out-Null
    $ppt = New-PptxSession
    $pres = $ppt.Presentations.Open($outputPath)
    
    Write-Info "スライド数: $($pres.Slides.Count)"
    
    $fixedCount = 0
    
    foreach ($slideNum in $TargetSlides) {
        Write-StepHeader "P$slideNum の修正"
        
        $slide = $pres.Slides.Item($slideNum)
        $rawTitle = Get-SlideTitle -Slide $slide
        $normalizedTitle = Get-NormalizedTitle $rawTitle
        
        Write-Info "タイトル: $rawTitle"
        Write-Info "正規化後: $normalizedTitle"
        
        # notes.json から正確にマッチ
        $nInfo = Find-ExactNoteEntry -SlideTitle $rawTitle -NotesArray $notesData.weekly
        $wInfo = Find-ExactClassificationEntry -SlideTitle $rawTitle -ClassificationArray $classification.weekly
        $rInfo = Find-ExactRegionEntry -SlideTitle $rawTitle -RegionMap $regionInfo
        
        if (-not $nInfo) {
            Write-Warning "P$slideNum : notes.json にマッチするエントリが見つかりません"
            Write-Warning "  正規化タイトル: $normalizedTitle"
            continue
        }
        
        $matchedTitle = Get-NormalizedTitle $nInfo.title
        Write-Info "マッチしたエントリ: $matchedTitle"
        
        # 現在のノート冒頭を表示
        $currentNote = Get-SpeakerNote -Slide $slide
        $currentFirst50 = if ($currentNote.Length -gt 50) { $currentNote.Substring(0, 50) } else { $currentNote }
        Write-Host "  修正前ノート冒頭: $currentFirst50" -ForegroundColor Yellow
        
        # 正しいノートを組み立て
        $newNote = Build-WeeklyNote -NoteInfo $nInfo -ClassInfo $wInfo -RegionEntry $rInfo
        
        # 書き込み
        Set-SpeakerNote -Slide $slide -NoteText $newNote | Out-Null
        
        $newFirst50 = if ($newNote.Length -gt 50) { $newNote.Substring(0, 50) } else { $newNote }
        Write-Host "  修正後ノート冒頭: $newFirst50" -ForegroundColor Green
        
        $fixedCount++
        Write-Success "P$slideNum : ノート修正完了"
    }
    
    # 保存
    $pres.Save()
    Write-Success "保存完了（$fixedCount 件修正）: $outputPath"
    
} catch {
    Write-Failure "エラー発生: $_"
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
} finally {
    if ($pres) { 
        $pres.Close()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres) | Out-Null
    }
    if ($ppt) { 
        $ppt.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
    }
    [GC]::Collect()
    Write-Info "COM セッション解放完了"
}

