# PptxCommon.psm1 - PowerPoint COM 操作の共通関数モジュール
# 使用方法: Import-Module "$PSScriptRoot\PptxCommon.psm1"

# ============================================================
# 定数定義（マジックナンバー集約）
# ============================================================

# スライド位置
$global:PPTX_COVER_SLIDE = 1
$global:PPTX_SUMMARY_SLIDE = 2
$global:PPTX_WEEKLY_START = 3

# スタンプデザイン
$global:STAMP_WIDTH = 180
$global:STAMP_HEIGHT = 30
$global:STAMP_MARGIN_RIGHT = 20
$global:STAMP_MARGIN_BOTTOM = 20
$global:STAMP_FONT_SIZE = 14

# スタンプ背景色（BGR形式）
$global:STAMP_COLOR_GLOBAL = 0x50B000      # 緑 (#00B050)
$global:STAMP_COLOR_UNSUPPORTED = 0xB85E00 # 青 (#005EB8)
$global:STAMP_COLOR_PARTIAL = 0xD47800     # 水色 (#0078D4)
$global:STAMP_COLOR_BOTH = 0xF0B000        # 水色 (#00B0F0)

# 検証閾値
$global:MIN_NOTE_LENGTH = 20
$global:CLIPBOARD_RETRY_COUNT = 3
$global:CLIPBOARD_WAIT_MS = 500

# 有効なリージョンパターン
$global:VALID_REGION_PATTERNS = @(
    "Japan East",
    "Japan West",
    "グローバル",
    "日本リージョン未対応",
    "日本未対応",
    "Japan East / West 対応",
    "Japan East のみ対応",
    "Japan West のみ対応"
)

# 禁止コンテンツパターン（汎用的すぎる表現）
$global:FORBIDDEN_CONTENT_PATTERNS = @(
    "詳細はP\d+参照",
    "^一般提供開始$",
    "^本番環境で利用可能に$",
    "^GAになりました$",
    "^プレビュー開始$",
    "^新機能$",
    "^機能追加$"
)

# ============================================================
# COM 管理
# ============================================================

function New-PptxSession {
    <#
    .SYNOPSIS
        PowerPoint COM セッションを開始
    .OUTPUTS
        PowerPoint.Application COM オブジェクト
    #>
    $ppt = New-Object -ComObject PowerPoint.Application
    $ppt.GetType().InvokeMember("Visible", [System.Reflection.BindingFlags]::SetProperty, $null, $ppt, @([int]-1)) | Out-Null
    return $ppt
}

function Get-ActivePptxApplication {
    <#
    .SYNOPSIS
        既存の PowerPoint.Application COM オブジェクトを取得
    #>
    try {
        return [System.Runtime.InteropServices.Marshal]::GetActiveObject("PowerPoint.Application")
    } catch {
        return $null
    }
}

function Get-PptxFullPath {
    param(
        [string]$PptxPath
    )

    if (Test-Path $PptxPath) {
        return (Resolve-Path $PptxPath).Path
    }
    return [System.IO.Path]::GetFullPath($PptxPath)
}

function Find-OpenPptxPresentation {
    <#
    .SYNOPSIS
        指定された PowerPoint.Application 内で、対象 PPTX を開いている Presentation を探す
    #>
    param(
        [object]$Application,
        [string]$PptxPath
    )

    if (-not $Application) { return $null }
    $fullPath = Get-PptxFullPath -PptxPath $PptxPath
    $targetName = [System.IO.Path]::GetFileName($fullPath)
    $targetFolder = [System.IO.Path]::GetFileName([System.IO.Path]::GetDirectoryName($fullPath))
    for ($i = 1; $i -le $Application.Presentations.Count; $i++) {
        $presentation = $Application.Presentations.Item($i)
        $candidate = ""
        $candidateName = ""
        try { $candidate = $presentation.FullName } catch {}
        try { $candidateName = $presentation.Name } catch {}

        $normalizedCandidate = [System.Uri]::UnescapeDataString($candidate) -replace '/', '\'
        $isExactPath = $candidate -and [string]::Equals($candidate, $fullPath, [System.StringComparison]::OrdinalIgnoreCase)
        $isOneDriveUrlPath = $normalizedCandidate -and $normalizedCandidate.EndsWith("\$targetFolder\$targetName", [System.StringComparison]::OrdinalIgnoreCase)
        $isSameNameInFolder = $candidateName -and [string]::Equals($candidateName, $targetName, [System.StringComparison]::OrdinalIgnoreCase) -and $normalizedCandidate -match [regex]::Escape($targetFolder)

        if ($isExactPath -or $isOneDriveUrlPath -or $isSameNameInFolder) {
            return $presentation
        }
    }
    return $null
}

function Close-OpenPptxPresentation {
    <#
    .SYNOPSIS
        対象 PPTX だけを、既存 PowerPoint から閉じる
    .DESCRIPTION
        他の PowerPoint ファイルや PowerPoint プロセスは終了しない。
        COM の Running Object Table で取得できる PowerPoint.Application が対象。
    #>
    param(
        [object]$Application,
        [string]$PptxPath,
        [switch]$Save
    )

    $application = if ($Application) { $Application } else { Get-ActivePptxApplication }
    if (-not $application) { return $false }

    $presentation = Find-OpenPptxPresentation -Application $application -PptxPath $PptxPath
    if (-not $presentation) { return $false }

    if ($Save) {
        try { $presentation.Save() } catch { Write-Warning "対象 PPTX の保存に失敗しました: $_" }
    }
    Write-Info "開いている対象 PPTX だけを閉じます: $(Get-PptxFullPath -PptxPath $PptxPath)"
    $presentation.Close()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($presentation) | Out-Null
    return $true
}

function Close-PptxSession {
    <#
    .SYNOPSIS
        PowerPoint COM セッションを完全に解放
    #>
    param(
        [object]$Presentation,
        [object]$Application,
        [switch]$Save
    )

    try {
        if ($Presentation) {
            if ($Save) { $Presentation.Save() }
            $Presentation.Close()
            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($Presentation) | Out-Null
        }
    } catch {
        Write-Warning "Presentation 解放エラー: $_"
    }

    try {
        if ($Application) {
            $Application.Quit()
            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($Application) | Out-Null
        }
    } catch {
        Write-Warning "Application 解放エラー: $_"
    }

    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}

# ============================================================
# スライド操作
# ============================================================

function Get-SlideTitle {
    <#
    .SYNOPSIS
        スライドのタイトルを取得（Unicode正規化付き）
    #>
    param(
        [object]$Slide
    )

    $title = ""
    try {
        $title = $Slide.Shapes.Title.TextFrame.TextRange.Text -replace "`r`n", " "
        # PowerPoint スマートクォート・NBSP の正規化（機械的テキスト変換）
        $title = $title -replace "\u00A0", " "           # NBSP → 通常スペース
        $title = $title -replace "[\u201C\u201D]", '"'   # スマートダブルクォート → ストレート
        $title = $title -replace "[\u2018\u2019]", "'"   # スマートシングルクォート → ストレート
    } catch {}
    return $title
}

function ConvertTo-PptxSafeText {
    <#
    .SYNOPSIS
        PowerPoint COM の TextRange.Text 代入で文字化けしやすい記号を安全な等価文字へ正規化する。
    .DESCRIPTION
        COM 経由の文字列代入は一部の Unicode 記号（en-dash 等）を "?" にフォールバックさせる
        ことがある。全角チルダや各種ダッシュ・引用符を、日本語スライドで自然な文字へ寄せる。
    #>
    param([string]$Text)
    if (-not $Text) { return $Text }
    $t = $Text
    $t = $t -replace "[\u2010\u2011\u2012\u2013\u2014\u2015]", "-"  # 各種ハイフン/ダッシュ -> ASCII ハイフン
    $t = $t -replace "[\u2212]", "-"                                # minus sign
    $t = $t -replace "[\u301C]", ([char]0xFF5E)                       # 波ダッシュ U+301C -> 全角チルダ U+FF5E（COM で ? 化け防止）
    $t = $t -replace "[\u201C\u201D]", '"'                          # 二重引用符
    $t = $t -replace "[\u2018\u2019]", "'"                          # 単一引用符
    $t = $t -replace "[\u2026]", "..."                              # 三点リーダ
    return $t
}

function Get-CleanSlideTitle {
    <#
    .SYNOPSIS
        ラベルや空白を除去した比較用タイトルを返す
    #>
    param(
        [string]$Title
    )

    if (-not $Title) { return "" }
    $cleanTitle = $Title -replace "^【[^】]+】\s*", ""
    $leadingStatusPatterns = @(
        '^パブリック\s*プレビュー\s*[:：]\s*',
        '^(プレビュー|Preview|Public Preview|Private Preview)\s*[:：]\s*',
        '^(一般提供開始|一般提供|一般公開|Generally Available)\s*[:：]\s*',
        '^(廃止予定|提供終了|サービス終了|Retirement|Deprecated|End of Support)\s*[:：]\s*'
    )
    foreach ($pattern in $leadingStatusPatterns) {
        $cleanTitle = $cleanTitle -replace $pattern, ""
    }
    $trailingStatusPatterns = @(
        '\s+(一般提供開始|一般提供|一般公開|Generally Available)$',
        '\s+(パブリック\s*プレビュー|プレビュー|Preview|Public Preview|Private Preview)$'
    )
    foreach ($pattern in $trailingStatusPatterns) {
        $cleanTitle = $cleanTitle -replace $pattern, ""
    }
    $cleanTitle = $cleanTitle -replace "\u00A0", " "
    $cleanTitle = ConvertTo-PptxSafeText -Text $cleanTitle
    return ($cleanTitle -replace '\s+', ' ').Trim()
}

function Get-SlideBodyTextForLabel {
    <#
    .SYNOPSIS
        ラベル判定用の本文を取得し、「参考:」セクションを先頭に寄せる
    .DESCRIPTION
        Azure Updates の英語ステータス（Generally Available / Public Preview）が
        末尾の参考欄に入ることが多いため、通常本文の前に参考欄を連結する。
    #>
    param(
        [object]$Slide,
        [string[]]$ExcludeShapeNames = @("Title 1")
    )

    $allText = @()
    foreach ($shape in $Slide.Shapes) {
        if ($shape.HasTextFrame -eq -1 -and ($ExcludeShapeNames -notcontains $shape.Name)) {
            try {
                $text = $shape.TextFrame.TextRange.Text
                if (-not [string]::IsNullOrWhiteSpace($text)) {
                    $allText += $text
                }
            } catch {}
        }
    }

    $bodyText = $allText -join "`n"
    if ([string]::IsNullOrWhiteSpace($bodyText)) { return "" }

    $lines = $bodyText -split "\r?\n|\r"
    $referenceLines = New-Object System.Collections.Generic.List[string]
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        if ($line -match "^\s*参考\s*[：:]" -or $line -match "Generally Available|Public Preview|パブリック\s*プレビュー") {
            for ($j = $i; $j -lt [Math]::Min($i + 6, $lines.Count); $j++) {
                if (-not [string]::IsNullOrWhiteSpace($lines[$j])) {
                    $referenceLines.Add($lines[$j])
                }
            }
        }
    }

    if ($referenceLines.Count -gt 0) {
        return (($referenceLines | Select-Object -Unique) -join "`n") + "`n" + $bodyText
    }
    return $bodyText
}

function Get-SlideLabel {
    <#
    .SYNOPSIS
        タイトル（+ 本文フォールバック）からラベル（廃止/GA/Preview/アナウンス/更新）を判定
    .DESCRIPTION
        タイトルで判定できない場合、Body テキストの先頭部分もチェックする。
        本文の「一般提供開始」「プレビューとして提供」等を拾うため。
    .OUTPUTS
        ラベル文字列と Priority のハッシュテーブル
    #>
    param(
        [string]$Title,
        [string]$Body = ""
    )

    # 本文は先頭800文字を使用（「参考:」行の英語タイトルを拾うため拡大）
    $bodySnippet = if ($Body.Length -gt 800) { $Body.Substring(0, 800) } else { $Body }

    # 元スライドのステータス語句を優先して判定
    if ($Title -match "サービス終了|提供終了|廃止|Retirement|Deprecated|End\s*of\s*(Support|Life)|EOL") {
        return @{ Label = "廃止"; Priority = 1 }
    }
    elseif ($Title -match "一般公開|一般提供|利用可能になりました|Generally Available") {
        return @{ Label = "GA"; Priority = 2 }
    }
    elseif ($Title -match "プレビュー|Preview|Private Preview|Public Preview") {
        return @{ Label = "Preview"; Priority = 3 }
    }
    elseif ($Title -match "^\s*(Update|アップデート)\s*[:：]" -or $Title -match "アナウンス|Announcement") {
        return @{ Label = "アナウンス"; Priority = 4 }
    }

    # タイトルで判定できなかった場合、本文でフォールバック判定
    if ($bodySnippet) {
        if ($bodySnippet -match "サービス終了|提供終了|廃止|Retirement|Deprecated|End\s*of\s*(Support|Life)|EOL") {
            return @{ Label = "廃止"; Priority = 1 }
        }
        elseif ($bodySnippet -match "一般公開|一般提供|利用可能になりました|Generally Available") {
            return @{ Label = "GA"; Priority = 2 }
        }
        elseif ($bodySnippet -match "プレビュー|Preview|Private Preview|Public Preview|パブリック\s*プレビュー") {
            return @{ Label = "Preview"; Priority = 3 }
        }
        elseif ($bodySnippet -match "(^|`n)\s*(Update|アップデート)\s*[:：]" -or $bodySnippet -match "アナウンス|Announcement") {
            return @{ Label = "アナウンス"; Priority = 4 }
        }
    }

    return @{ Label = "更新"; Priority = 4 }
}

# ============================================================
# リージョン判定
# ============================================================

function New-PrefixMap {
    <#
    .SYNOPSIS
        ハッシュテーブルからプレフィックスマップを生成（O(n)で事前計算）
    .DESCRIPTION
        検索を O(1) にするためのプレフィックスインデックスを作成
    #>
    param(
        [hashtable]$Map,
        [int]$MatchLength = 15
    )

    if (-not $Map -or $Map.Count -eq 0) { return @{} }

    $prefixMap = @{}
    foreach ($key in $Map.Keys) {
        $cleanKey = Get-CleanSlideTitle -Title $key
        $prefix = $cleanKey.Substring(0, [Math]::Min($MatchLength, $cleanKey.Length)).ToLower()
        if (-not $prefixMap.ContainsKey($prefix)) {
            $prefixMap[$prefix] = @{ Key = $key; Value = $Map[$key] }
        }
    }
    return $prefixMap
}

function Find-ByPartialTitle {
    <#
    .SYNOPSIS
        タイトル部分一致でハッシュテーブルから値を検索（高速版）
    .DESCRIPTION
        先頭N文字で部分一致検索を行い、マッチしたキーの値を返す
        PrefixMap が渡された場合は O(1) で検索、なければ O(n) でフォールバック
    .PARAMETER Title
        検索対象のタイトル
    .PARAMETER Map
        検索対象のハッシュテーブル（キー = タイトル）
    .PARAMETER PrefixMap
        事前計算済みプレフィックスマップ（オプション、高速検索用）
    .PARAMETER MatchLength
        部分一致に使用する文字数（デフォルト: 15）
    .OUTPUTS
        マッチした値。見つからなければ $null
    #>
    param(
        [string]$Title,
        [hashtable]$Map,
        [hashtable]$PrefixMap = $null,
        [int]$MatchLength = 15
    )

    if (-not $Map -or $Map.Count -eq 0) { return $null }

    $cleanTitle = Get-CleanSlideTitle -Title $Title
    $titlePrefix = $cleanTitle.Substring(0, [Math]::Min($MatchLength, $cleanTitle.Length)).ToLower()

    # 高速パス: PrefixMap がある場合は O(1) で検索
    if ($PrefixMap -and $PrefixMap.ContainsKey($titlePrefix)) {
        return $PrefixMap[$titlePrefix].Value
    }

    # フォールバック: 正規化完全一致 → プレフィックス一致の 2 段階
    # ★ 2026-02-16 修正: -match のサブストリングマッチを廃止
    #   原因: "Application Gateway" を含む複数タイトルが全て同じエントリに誤マッチ

    # Step 1: 正規化完全一致（スペース・ケース無視）
    $normalizedTitle = ($cleanTitle -replace '\s+', ' ').Trim().ToLower()
    foreach ($key in $Map.Keys) {
        $normalizedKey = (Get-CleanSlideTitle -Title $key -replace '\s+', ' ').Trim().ToLower()
        if ($normalizedTitle -eq $normalizedKey) {
            return $Map[$key]
        }
    }

    # Step 2: プレフィックス一致（先頭N文字の完全一致）
    foreach ($key in $Map.Keys) {
        $keyPrefix = (Get-CleanSlideTitle -Title $key -replace '\s+', ' ').Trim().ToLower()
        $keyPrefix = $keyPrefix.Substring(0, [Math]::Min($MatchLength, $keyPrefix.Length))
        if ($titlePrefix -eq $keyPrefix) {
            return $Map[$key]
        }
    }
    return $null
}

function Find-RegionStatus {
    <#
    .SYNOPSIS
        region_info ハッシュテーブルからリージョン状態を検索
    .PARAMETER Title
        スライドタイトル
    .PARAMETER RegionInfo
        リージョン情報のハッシュテーブル
    .OUTPUTS
        リージョン状態文字列（見つからなければフォールバック値）
    #>
    param(
        [string]$Title,
        [hashtable]$RegionInfo
    )

    $info = Find-ByPartialTitle -Title $Title -Map $RegionInfo -MatchLength 25
    if ($info -and $info.regionStatus) {
        return $info.regionStatus
    }
    return Get-RegionInfo -Title $Title
}

function ConvertTo-RegionInfoMap {
    <#
    .SYNOPSIS
        region_info.json / region_info_reviewed.json の JSON を検索用ハッシュへ変換
    #>
    param(
        [object]$RegionData
    )

    $regionInfo = @{}
    if (-not $RegionData) { return $regionInfo }

    $regionsObject = if ($RegionData.PSObject.Properties["services"]) {
        $RegionData.services
    } elseif ($RegionData.PSObject.Properties["regions"]) {
        $RegionData.regions
    } else {
        $RegionData
    }

    foreach ($prop in $regionsObject.PSObject.Properties) {
        $title = $prop.Name
        $info = $prop.Value

        $regionStatus = ""
        if ($info.stamp) {
            $regionStatus = $info.stamp
        } elseif ($info.status -match "グローバル|全リージョン") {
            $regionStatus = "グローバル"
        } elseif ($info.japanEast -and $info.japanWest) {
            $regionStatus = "Japan East / West 対応"
        } elseif ($info.japanEast) {
            $regionStatus = "Japan East のみ対応"
        } elseif ($info.japanWest) {
            $regionStatus = "Japan West のみ対応"
        } elseif ($info.global -or $info.note -match "グローバル|全リージョン" -or $info.evidence -match "グローバル|全リージョン") {
            $regionStatus = "グローバル"
        } else {
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
    return $regionInfo
}

function Get-RegionInfo {
    <#
    .SYNOPSIS
        タイトルからリージョン情報を判定（フォールバック用）
        本来は region_info.json に MCP 調査結果を記録して使用すること
    #>
    param(
        [string]$Title
    )

    # 廃止系は常にグローバル
    if ($Title -match "廃止|Retirement|サポート終了|EOL") {
        return "グローバル"
    }

    # 🔴 フォールバック: region_info.json になければ「要確認」を返す
    # 本来は Prepare エージェントが #microsoft.docs.mcp で調査して region_info.json に記録する
    # 安全側に倒す: 不明な場合は「対応」と仮定せず、明示的に確認を促す
    Write-Warning "region_info.json にリージョン情報がありません: $Title（要確認）"
    return "要確認"
}

# ============================================================
# セクション操作
# ============================================================

function Set-PptxSections {
    <#
    .SYNOPSIS
        セクション構成を設定
    #>
    param(
        [object]$Presentation,
        [hashtable]$Sections  # @{ "セクション名" = 開始スライド番号 }
    )

    # 既存セクションを削除（後ろから）
    for ($i = $Presentation.SectionProperties.Count; $i -ge 1; $i--) {
        $Presentation.SectionProperties.Delete($i, $false)
    }

    # 新しいセクションを追加（順番に）
    foreach ($section in $Sections.GetEnumerator() | Sort-Object Value) {
        $Presentation.SectionProperties.AddSection($section.Value, $section.Key)
    }
}

# ============================================================
# シェイプ操作
# ============================================================

function Set-StatusBadge {
    <#
    .SYNOPSIS
        本文スライド右上にステータスバッジ（GA/Preview/廃止/アナウンス）を配置する。
        テーマ色（Indigo+Amber）に合わせた4種カラーパレットを使用。
    #>
    param(
        [Parameter(Mandatory)] $Slide,
        [Parameter(Mandatory)] [string]$Label  # GA / Preview / 廃止 / アナウンス
    )

    function BGR([int]$r,[int]$g,[int]$b){ return ($b -shl 16) -bor ($g -shl 8) -bor $r }
    $White   = BGR 0xFF 0xFF 0xFF
    $Indigo  = BGR 0x3B 0x4C 0x8A   # theme accent1 (GA)
    $Amber   = BGR 0xF5 0xA6 0x23   # theme accent2 (Preview)
    $RedDark = BGR 0xC0 0x39 0x3E   # 廃止
    $Teal    = BGR 0x0E 0x7C 0x7B   # アナウンス
    $Gray    = BGR 0x6E 0x6E 0x6E   # 更新

    $palette = switch -Wildcard ($Label) {
        'GA'        { @{ Fill = $Indigo;  Text = 'GA';           FontColor = $White; FontSize = 14 } }
        'Preview'   { @{ Fill = $Amber;   Text = 'PREVIEW';      FontColor = $White; FontSize = 13 } }
        '廃止'      { @{ Fill = $RedDark; Text = 'RETIREMENT';   FontColor = $White; FontSize = 11 } }
        'アナウンス' { @{ Fill = $Teal;    Text = 'ANNOUNCEMENT'; FontColor = $White; FontSize = 11 } }
        '更新'      { @{ Fill = $Gray;    Text = 'UPDATE';       FontColor = $White; FontSize = 13 } }
        default     { @{ Fill = $Gray;    Text = 'UPDATE';       FontColor = $White; FontSize = 13 } }
    }

    # 既存の StatusBadge を削除（再実行耐性）
    for ($i = $Slide.Shapes.Count; $i -ge 1; $i--) {
        $sh = $Slide.Shapes.Item($i)
        if ($sh.Name -eq 'StatusBadge') { $sh.Delete() }
    }

    # 右上配置: 960x540pt スライドの右上 (Left=800, Top=22)
    $badge = $Slide.Shapes.AddShape(5, 800, 22, 142, 32)  # msoShapeRoundedRectangle
    $badge.Name = 'StatusBadge'
    $badge.Fill.ForeColor.RGB = $palette.Fill
    $badge.Fill.Transparency = 0
    $badge.Line.Visible = 0
    $badge.Shadow.Visible = 0
    $badge.TextFrame.TextRange.Text = $palette.Text
    $badge.TextFrame.TextRange.Font.Size = $palette.FontSize
    $badge.TextFrame.TextRange.Font.Bold = -1
    $badge.TextFrame.TextRange.Font.Color.RGB = $palette.FontColor
    $badge.TextFrame.TextRange.Font.Name = 'Segoe UI'
    $badge.TextFrame.HorizontalAnchor = 2  # msoAnchorCenter
    $badge.TextFrame.VerticalAnchor = 3    # msoAnchorMiddle
    $badge.ZOrder(0)  # msoBringToFront

    # タイトルシェイプ幅を縮めてバッジと重ならないように調整
    foreach ($sh in $Slide.Shapes) {
        if ($sh.Name -like 'Title*' -or $sh.Name -like 'タイトル*') {
            try {
                # 右端をバッジ左端の手前まで（22 + 142 = 964 の左、790 まで）
                $currentRight = $sh.Left + $sh.Width
                $newRight = 790
                if ($currentRight -gt $newRight) {
                    $sh.Width = [Math]::Max(200, $newRight - $sh.Left)
                }
            } catch {}
            break
        }
    }

    return $badge
}

function Add-RegionStamp {
    <#
    .SYNOPSIS
        スライドにリージョンスタンプを追加（右下配置、テンプレート準拠デザイン）
    .DESCRIPTION
        定数 $global:STAMP_* を使用してデザインを適用
    #>
    param(
        [object]$Slide,
        [string]$RegionText
    )

    # 既存スタンプがあれば削除（Shape.Nameで識別）
    # 🔴 "RegionStamp" だけでなく、テンプレ由来の "RegionStamp_JapanBoth" 等の
    #    名前付きサンプルスタンプ（RegionStamp_*）も消す。これを消さないと、
    #    MCP 駆動の本文テンプレ複製方式で 5 種のスタンプが残り重なって表示される。
    for ($i = $Slide.Shapes.Count; $i -ge 1; $i--) {
        $shape = $Slide.Shapes.Item($i)
        if ($shape.Name -like "RegionStamp*") {
            $shape.Delete()
        }
    }

    # 定数から値を取得（スライドサイズ: 960pt x 540pt）
    $stampWidth = $global:STAMP_WIDTH
    $stampHeight = $global:STAMP_HEIGHT
    $marginRight = $global:STAMP_MARGIN_RIGHT
    $marginBottom = $global:STAMP_MARGIN_BOTTOM

    $left = 960 - $marginRight - $stampWidth
    $top = 540 - $marginBottom - $stampHeight

    $textBox = $Slide.Shapes.AddTextbox(1, $left, $top, $stampWidth, $stampHeight)
    $textBox.Name = "RegionStamp"
    $textBox.TextFrame.TextRange.Text = $RegionText
    $textBox.TextFrame.TextRange.Font.Size = $global:STAMP_FONT_SIZE
    $textBox.TextFrame.TextRange.Font.Bold = $true
    $textBox.TextFrame.TextRange.Font.Color.RGB = 0xFFFFFF  # 白文字
    $textBox.TextFrame.TextRange.ParagraphFormat.Alignment = 2  # ppAlignCenter
    $textBox.TextFrame.MarginLeft = 10
    $textBox.TextFrame.MarginRight = 10
    $textBox.TextFrame.MarginTop = 5
    $textBox.TextFrame.MarginBottom = 5

    # 背景色（定数から取得）
    if ($RegionText -match "グローバル") {
        $textBox.Fill.ForeColor.RGB = $global:STAMP_COLOR_GLOBAL
    } elseif ($RegionText -match "未対応") {
        $textBox.Fill.ForeColor.RGB = $global:STAMP_COLOR_UNSUPPORTED
    } elseif ($RegionText -match "West のみ|East のみ") {
        $textBox.Fill.ForeColor.RGB = $global:STAMP_COLOR_PARTIAL
    } else {
        $textBox.Fill.ForeColor.RGB = $global:STAMP_COLOR_BOTH
    }
    $textBox.Fill.Solid()

    # 枠線なし
    try { $textBox.Line.Visible = 0 } catch {}

    return $textBox
}

function Set-SpeakerNote {
    <#
    .SYNOPSIS
        スライドにスピーカーノートを設定
    #>
    param(
        [object]$Slide,
        [string]$NoteText
    )

    try {
        $safeNote = ConvertTo-PptxSafeText -Text $NoteText
        $Slide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = $safeNote
        return $true
    } catch {
        Write-Warning "ノート設定エラー: $_"
        return $false
    }
}

function Get-SpeakerNote {
    <#
    .SYNOPSIS
        スライドのスピーカーノートを取得
    #>
    param(
        [object]$Slide
    )

    try {
        return $Slide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text
    } catch {
        return ""
    }
}

# ============================================================
# テーブル操作
# ============================================================

function Update-TableRow {
    <#
    .SYNOPSIS
        テーブルの行を更新
    #>
    param(
        [object]$Table,
        [int]$RowIndex,
        [string[]]$Values
    )

    for ($col = 1; $col -le [Math]::Min($Values.Count, $Table.Columns.Count); $col++) {
        $Table.Cell($RowIndex, $col).Shape.TextFrame.TextRange.Text = $Values[$col - 1]
    }
}

function Find-UpdatePointsSlideIndex {
    param(
        [object]$Presentation
    )

    for ($i = 1; $i -le $Presentation.Slides.Count; $i++) {
        $title = Get-SlideTitle -Slide $Presentation.Slides.Item($i)
        if ($title -match "^(UPDATE Points|今週のUPDATE)|UPDATE\s*Points|UPDATE.*ポイント|今週の.*ポイント") {
            return $i
        }
    }
    return 0
}

function Get-UpdatePointsSlideIndices {
    param(
        [object]$Presentation
    )

    $indices = @()
    for ($i = 1; $i -le $Presentation.Slides.Count; $i++) {
        $title = Get-SlideTitle -Slide $Presentation.Slides.Item($i)
        if ($title -match "^(UPDATE Points|今週のUPDATE)|UPDATE\s*Points|UPDATE.*ポイント|今週の.*ポイント") {
            $indices += $i
        }
    }
    return $indices
}

function Get-UpdatePointsChunkSizes {
    param(
        [int]$ItemCount,
        [int]$SingleSlideCapacity = 10,
        [int]$MaxRowsPerSplitSlide = 10
    )

    if ($ItemCount -le 0) {
        return @()
    }

    if ($ItemCount -le $SingleSlideCapacity) {
        return @($ItemCount)
    }

    $slideCount = [Math]::Ceiling($ItemCount / [double]$MaxRowsPerSplitSlide)
    $baseSize = [Math]::Floor($ItemCount / $slideCount)
    $remainder = $ItemCount % $slideCount
    $chunkSizes = @()

    for ($i = 0; $i -lt $slideCount; $i++) {
        $size = $baseSize
        if ($i -lt $remainder) {
            $size++
        }
        $chunkSizes += $size
    }

    return $chunkSizes
}

function Set-UpdatePointsTableColumnWidths {
    param(
        [object]$Table
    )

    if (-not $Table -or $Table.Columns.Count -lt 5) {
        return
    }

    $numberColumn = $Table.Columns.Item(1)
    $keywordColumn = $Table.Columns.Item(2)
    $targetNumberWidth = 42
    $delta = $targetNumberWidth - [double]$numberColumn.Width

    if ($delta -le 0) {
        return
    }

    $minKeywordWidth = 70
    $newKeywordWidth = [double]$keywordColumn.Width - $delta
    if ($newKeywordWidth -lt $minKeywordWidth) {
        $delta = [double]$keywordColumn.Width - $minKeywordWidth
        $newKeywordWidth = $minKeywordWidth
    }

    if ($delta -gt 0) {
        $numberColumn.Width = [double]$numberColumn.Width + $delta
        $keywordColumn.Width = $newKeywordWidth
    }
}

function Set-UpdatePointsNumberCellStyle {
    param(
        [object]$CellShape
    )

    if (-not $CellShape -or $CellShape.HasTextFrame -ne -1) {
        return
    }

    try {
        $CellShape.TextFrame.MarginLeft = 2
        $CellShape.TextFrame.MarginRight = 2
        $CellShape.TextFrame.TextRange.ParagraphFormat.Alignment = 2
    } catch {}
}

function Remove-RegionStamp {
    param(
        [object]$Slide
    )

    if (-not $Slide) {
        return
    }

    for ($i = $Slide.Shapes.Count; $i -ge 1; $i--) {
        $shape = $Slide.Shapes.Item($i)
        if ($shape.Name -eq "RegionStamp") {
            $shape.Delete()
        }
    }
}

function Update-UpdatePointsSlides {
    param(
        [object]$Presentation,
        [int[]]$ChunkSizes
    )

    $existingIndices = @(Get-UpdatePointsSlideIndices -Presentation $Presentation)
    if ($existingIndices.Count -eq 0) {
        return @()
    }

    $primaryIndex = $existingIndices[0]
    $primarySlide = $Presentation.Slides.Item($primaryIndex)
    $baseTitle = Get-SlideTitle -Slide $primarySlide

    for ($i = $existingIndices.Count - 1; $i -ge 1; $i--) {
        $Presentation.Slides.Item($existingIndices[$i]).Delete()
        Start-Sleep -Milliseconds 50
    }

    $requiredSlides = [Math]::Max(1, $ChunkSizes.Count)
    for ($i = 1; $i -lt $requiredSlides; $i++) {
        # クリップボード非依存で複製（COM クリップボード障害環境対策）。
        # Duplicate() はソース直後に複製を挿入する。
        $Presentation.Slides.Item($primaryIndex).Duplicate() | Out-Null
        Start-Sleep -Milliseconds 50
    }

    $finalIndices = @(Get-UpdatePointsSlideIndices -Presentation $Presentation)
    for ($i = 0; $i -lt $finalIndices.Count; $i++) {
        $slide = $Presentation.Slides.Item($finalIndices[$i])
        Remove-RegionStamp -Slide $slide
        try {
            $titleShape = $slide.Shapes.Title
            if ($titleShape) {
                $newTitle = $baseTitle
                if ($i -gt 0) {
                    $newTitle = "$baseTitle（続き）"
                }
                $titleShape.TextFrame.TextRange.Text = $newTitle
            }
        } catch {}
    }

    return $finalIndices
}

function Update-SummarySlideContent {
    param(
        [object]$Presentation,
        [object]$Classification
    )

    $tocItems = @()
    $num = 1
    foreach ($w in $Classification.weekly) {
        $cleanTitle = Get-CleanSlideTitle -Title $w.title
        $tocItems += "$num. 【$($w.label)】$cleanTitle"
        $num++
    }

    $tocHeader = "■ 今週の Weekly New Topics（$($Classification.weekly.Count) 件）"
    $tocContent = $tocHeader + "`n`n" + ($tocItems -join "`n")

    $p2 = $Presentation.Slides.Item($global:PPTX_SUMMARY_SLIDE)
    $tocShape = $null
    $maxArea = 0
    $contentBoxes = @()

    foreach ($shape in $p2.Shapes) {
        if ($shape.HasTextFrame -eq -1 -and $shape.Name -ne "Title 1") {
            $contentBoxes += $shape
            if ($shape.Width * $shape.Height -gt $maxArea) {
                $maxArea = $shape.Width * $shape.Height
                $tocShape = $shape
            }
        }
    }

    foreach ($box in $contentBoxes) {
        if ($tocShape -and $box.Name -ne $tocShape.Name) {
            try { $box.TextFrame.TextRange.Text = "" } catch {}
        }
    }

    if ($tocShape) {
        $tocShape.TextFrame.TextRange.Text = $tocContent
        $tocShape.TextFrame.TextRange.Font.Size = 14
        return $true
    }
    return $false
}

function Get-DisplayCategory {
    param(
        [string]$Category,
        [string]$Title
    )

    $normalizedCategory = if ($null -ne $Category) { $Category.Trim() } else { "" }
    switch ($normalizedCategory) {
        "IaaS" { return "インフラ基盤" }
        "Network" { return "ネットワーク" }
        "Storage" { return "ストレージ" }
        "Backup" { return "バックアップ・災害復旧" }
        "Security" { return "セキュリティ・ID" }
        "Monitoring" { return "監視・運用" }
        "Hybrid" { return "ハイブリッド・マルチクラウド" }
        "App" { return "アプリケーション基盤" }
        "AppPlatform" { return "アプリケーション基盤" }
        "AI" { return "AI・ML" }
        "AIReview" { }
        "Breaking" { }
        "" { }
        default {
            if ($normalizedCategory -match "インフラ基盤|ネットワーク|ストレージ|バックアップ・災害復旧|セキュリティ・ID|監視・運用|ハイブリッド・マルチクラウド|アプリケーション基盤|AI・ML|その他") {
                return $normalizedCategory
            }
        }
    }

    $normalizedTitle = if ($null -ne $Title) { $Title } else { "" }
    if ($normalizedTitle -match "Blob|Storage|ストレージ|Azure Files|NetApp|キャッシュボリューム|Storage Actions") {
        return "ストレージ"
    }
    if ($normalizedTitle -match "仮想マシン|Virtual Machine|VMSS|Premium SSD|Disk|ディスク") {
        return "インフラ基盤"
    }
    if ($normalizedTitle -match "Virtual Network|VNet|NSG|ルート テーブル|Network Watcher|Virtual Network Manager|ExpressRoute|Firewall|Load Balancer|Bastion|Private Endpoint|Private Link|NAT Gateway") {
        return "ネットワーク"
    }
    if ($normalizedTitle -match "Backup|バックアップ|Site Recovery|Recovery Services") {
        return "バックアップ・災害復旧"
    }
    if ($normalizedTitle -match "Key Vault|Defender|Sentinel|Entra") {
        return "セキュリティ・ID"
    }
    if ($normalizedTitle -match "Monitor|Log Analytics|Application Insights") {
        return "監視・運用"
    }
    if ($normalizedTitle -match "Azure Arc") {
        return "ハイブリッド・マルチクラウド"
    }
    if ($normalizedTitle -match "App Service|Logic Apps|Automation") {
        return "アプリケーション基盤"
    }
    if ($normalizedTitle -match "OpenAI|Copilot|Agent|SRE|AI|Machine Learning|機械学習") {
        return "AI・ML"
    }

    return "その他"
}

function Update-UpdatePointsTableContent {
    param(
        [object]$Presentation,
        [object]$Classification,
        [hashtable]$RegionInfo
    )

    $chunkSizes = @(Get-UpdatePointsChunkSizes -ItemCount $Classification.weekly.Count)
    if ($chunkSizes.Count -eq 0) {
        return $false
    }

    Write-Host "  UPDATE Points 分割: $($Classification.weekly.Count) 件 -> $($chunkSizes -join '+')"

    $updatePointsIndices = @(Update-UpdatePointsSlides -Presentation $Presentation -ChunkSizes $chunkSizes)
    if ($updatePointsIndices.Count -eq 0) {
        return $false
    }

    $globalRowOffset = 0
    for ($slideIdx = 0; $slideIdx -lt $chunkSizes.Count; $slideIdx++) {
        $slideNumber = $updatePointsIndices[$slideIdx]
        $updatePointsSlide = $Presentation.Slides.Item($slideNumber)
        $tableShape = $null
        foreach ($shape in $updatePointsSlide.Shapes) {
            if ($shape.HasTable -eq -1) {
                $tableShape = $shape
                break
            }
        }
        if (-not $tableShape) {
            return $false
        }

        $table = $tableShape.Table
        $chunkSize = $chunkSizes[$slideIdx]
        $requiredRows = $chunkSize + 1

        Set-UpdatePointsTableColumnWidths -Table $table

        while ($table.Rows.Count -lt $requiredRows) {
            $table.Rows.Add() | Out-Null
        }
        while ($table.Rows.Count -gt $requiredRows) {
            $table.Rows.Item($table.Rows.Count).Delete()
            Start-Sleep -Milliseconds 20
        }

        for ($dataRow = 2; $dataRow -le $requiredRows; $dataRow++) {
            $wIdx = $globalRowOffset + ($dataRow - 2)
            $w = $Classification.weekly[$wIdx]
            $cleanTitle = Get-CleanSlideTitle -Title $w.title
            $keyword = Get-DisplayCategory -Category $w.category -Title $cleanTitle
            $update = "【$($w.label)】$cleanTitle"
            $keypoint = if ($w.keypoint -and $w.keypoint.Length -gt 5) { $w.keypoint } else { "既存環境への適用可否を確認" }
            $region = Find-RegionStatus -Title $cleanTitle -RegionInfo $RegionInfo

            $numberCellShape = $table.Cell($dataRow, 1).Shape
            $numberCellShape.TextFrame.TextRange.Text = [string]($wIdx + 1)
            Set-UpdatePointsNumberCellStyle -CellShape $numberCellShape
            $table.Cell($dataRow, 2).Shape.TextFrame.TextRange.Text = $keyword
            $table.Cell($dataRow, 3).Shape.TextFrame.TextRange.Text = $update
            $table.Cell($dataRow, 4).Shape.TextFrame.TextRange.Text = $keypoint
            $table.Cell($dataRow, 5).Shape.TextFrame.TextRange.Text = $region
        }

        Write-Host "    P$slideNumber : $chunkSize 件"
        $globalRowOffset += $chunkSize
    }

    return $true
}

# ============================================================
# ユーティリティ
# ============================================================

function Find-SlideIndexById {
    <#
    .SYNOPSIS
        SlideID から現在のスライドインデックスを返す（複製/移動で位置が変わっても安定的に特定）。
    #>
    param(
        [Parameter(Mandatory)] $Presentation,
        [Parameter(Mandatory)] $SlideId
    )
    for ($i = 1; $i -le $Presentation.Slides.Count; $i++) {
        if ($Presentation.Slides.Item($i).SlideID -eq $SlideId) { return $i }
    }
    return 0
}

function Set-BodySlideContent {
    <#
    .SYNOPSIS
        MCP 由来の本文スライド（テンプレ複製）に 対象 / これまで / 今後 /
        お客様にとっての価値 / 課金 / 日本リージョン / 詳細リンク / 参考リンク を流し込む。
    .DESCRIPTION
        本文雛形スライド（コンテンツ プレースホルダーを持つ）を前提に、
        以下の段落構成を生成する:
          1. 対象：
          2. {TargetService}
          3. これまで：
          4. {Before}
          5. 今後：
          6. {After}
          7. お客様にとっての価値：
          8. {CustomerImpact}
          9. 課金：{Pricing}　/　日本リージョン：{JapanRegion}
          10. 詳細はこちらをご参照ください。
          11. 参考：
          12. {SourceUrl}
        後方互換: -BodyContent のみが与えられた場合は、改行を保ったまま単一段落として 4 番目に挿入する旧構成にフォールバックする。
    #>
    param(
        [Parameter(Mandatory)] $Slide,
        [Parameter(Mandatory)] [string]$Title,
        [string]$TargetService,
        [string]$Background,
        [string]$Before,
        [string]$After,
        [string]$CustomerImpact,
        [string]$Pricing,
        [string]$JapanRegion,
        [string]$BodyContent,
        [string]$LearnUrl,
        [string]$SourceUrl
    )

    # COM 代入で化けやすい記号（en-dash 等）を正規化
    $Title          = ConvertTo-PptxSafeText -Text $Title
    $TargetService  = ConvertTo-PptxSafeText -Text $TargetService
    $Background     = ConvertTo-PptxSafeText -Text $Background
    $Before         = ConvertTo-PptxSafeText -Text $Before
    $After          = ConvertTo-PptxSafeText -Text $After
    $CustomerImpact = ConvertTo-PptxSafeText -Text $CustomerImpact
    $Pricing        = ConvertTo-PptxSafeText -Text $Pricing
    $JapanRegion    = ConvertTo-PptxSafeText -Text $JapanRegion
    $BodyContent    = ConvertTo-PptxSafeText -Text $BodyContent

    # 6 フィールドモードか後方互換モードかを判定
    $useFiveField = $Before -or $After -or $CustomerImpact -or $Pricing -or $JapanRegion -or $Background

    # --- タイトル設定 ---
    foreach ($sh in $Slide.Shapes) {
        $isTitle = $false
        try { if ($sh.Type -eq 14 -or $sh.Name -like 'タイトル*' -or ($sh.PlaceholderFormat -and $sh.PlaceholderFormat.Type -eq 13)) { $isTitle = $true } } catch {}
        try { if ($sh.Name -like 'Title*' -or $sh.Name -like 'タイトル*') { $isTitle = $true } } catch {}
        if ($isTitle -and $sh.HasTextFrame) {
            $sh.TextFrame.TextRange.Text = $Title
            break
        }
    }

    # --- 本文コンテンツ プレースホルダー特定 ---
    $contentShape = $null
    foreach ($sh in $Slide.Shapes) {
        if ($sh.Name -like 'コンテンツ*' -or $sh.Name -like 'Content*') { $contentShape = $sh; break }
    }
    if (-not $contentShape) {
        $best = $null; $bestArea = 0
        foreach ($sh in $Slide.Shapes) {
            if ($sh.Name -like 'RegionStamp*') { continue }
            if (-not $sh.HasTextFrame) { continue }
            $txt = ""
            try { $txt = $sh.TextFrame.TextRange.Text } catch {}
            if ($txt -match '対象|内容|これまで') {
                $area = 0; try { $area = $sh.Width * $sh.Height } catch {}
                if ($area -ge $bestArea) { $bestArea = $area; $best = $sh }
            }
        }
        $contentShape = $best
    }
    if (-not $contentShape) {
        throw "本文コンテンツ プレースホルダーが見つかりません (slide title: $Title)"
    }

    # --- 本文プレースホルダ枠を拡大（6項目化でオーバーフロー対策）---
    # スライド高 540pt のうち、上部にタイトル領域（~140pt）、下部余白（~10pt）を残し、
    # 本文枠を Top=145, Height=385 まで広げる
    try {
        if ($contentShape.Top -gt 150) { $contentShape.Top = 145 }
        $contentShape.Height = 385
        # オートサイズで内容に合わせて縮小（テキストが収まらない場合フォント自動縮小）
        $contentShape.TextFrame.WordWrap = -1
        $contentShape.TextFrame.AutoSize = 2  # ppAutoSizeTextToFitShape
    } catch {}

    # --- 段落を再構築 ---
    $tr = $contentShape.TextFrame.TextRange
    $detailText = '詳細はこちらをご参照ください。'

    if ($useFiveField) {
        # 5 項目モード: ラベル段落を太字 Indigo にし、値段落はインデント lvl2
        $pricingLine = ''
        if ($Pricing -and $JapanRegion) {
            $pricingLine = "課金：$Pricing　/　日本リージョン：$JapanRegion"
        } elseif ($Pricing) {
            $pricingLine = "課金：$Pricing"
        } elseif ($JapanRegion) {
            $pricingLine = "日本リージョン：$JapanRegion"
        }

        # ラベルと値を 1 行に連結（オーバーフロー防止: 各項目 2 行→1 行で計 5 行短縮）
        $lines = @(
            "対象：$TargetService",
            "仕組み：$Background",
            "これまで：$Before",
            "今後：$After",
            "お客様にとっての価値：$CustomerImpact",
            $pricingLine,
            "$detailText（参考：$SourceUrl）"
        )
        $tr.Text = ($lines -join "`r")

        # ラベル「対象：」「仕組み：」「これまで：」「今後：」「お客様にとっての価値：」を Indigo 太字に
        # (段落全体ではなく、行頭の「ラベル：」部分のみ色付け)
        $indigo = ($0x8A) -bor (0x4C -shl 8) -bor (0x3B -shl 16)
        $labelPatterns = @('対象：', '仕組み：', 'これまで：', '今後：', 'お客様にとっての価値：')
        $fullText = $contentShape.TextFrame.TextRange.Text
        foreach ($lbl in $labelPatterns) {
            $pos = $fullText.IndexOf($lbl)
            if ($pos -ge 0) {
                try {
                    $chars = $contentShape.TextFrame.TextRange.Characters($pos + 1, $lbl.Length)
                    $chars.Font.Bold = -1
                    $chars.Font.Color.RGB = $indigo
                } catch {}
            }
        }
    }
    else {
        # 後方互換モード（旧 bodyContent 単段落）
        $lines = @('対象：', $TargetService, '内容：', $BodyContent, $detailText, '参考：', $SourceUrl)
        $tr.Text = ($lines -join "`r")
        try { $tr.Paragraphs(2, 1).IndentLevel = 2 } catch {}
        try { $tr.Paragraphs(4, 1).IndentLevel = 2 } catch {}
    }

    # --- ハイパーリンク付与 ---
    $full = $contentShape.TextFrame.TextRange.Text
    if ($LearnUrl) {
        $idx = $full.IndexOf('こちら')
        if ($idx -ge 0) {
            try { $contentShape.TextFrame.TextRange.Characters($idx + 1, 3).ActionSettings(1).Hyperlink.Address = $LearnUrl } catch {}
        }
    }
    if ($SourceUrl) {
        $idx2 = $full.IndexOf($SourceUrl)
        if ($idx2 -ge 0) {
            try { $contentShape.TextFrame.TextRange.Characters($idx2 + 1, $SourceUrl.Length).ActionSettings(1).Hyperlink.Address = $SourceUrl } catch {}
        }
    }

    # --- BIZ UDPゴシック: テンプレのレイアウト側で適用済みのため Set-BodySlideContent では追加適用しない
    #     （per-shape ループが OneDrive 同期で遅延する既知問題への対策。
    #       フォント未適用に見える場合はテンプレ側の master/layout を更新）

    return $true
}

function Write-StepHeader {
    <#
    .SYNOPSIS
        ステップヘッダーを表示
    #>
    param(
        [string]$Message
    )

    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host " $Message" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Yellow
}

function Write-Failure {
    param([string]$Message)
    Write-Host "[NG] $Message" -ForegroundColor Red
}

# エクスポート
Export-ModuleMember -Function *
