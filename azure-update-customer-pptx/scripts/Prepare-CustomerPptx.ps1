<#
.SYNOPSIS
    Prepare-CustomerPptx.ps1 - MCP 取得済み Azure Updates を分類
.DESCRIPTION
    1. manifest/fetched-updates.json を読み込み
    2. キーワードマッチングで Weekly / Appendix に分類
    3. classification.json と region_info.json を出力
.PARAMETER DateFolder
    日付フォルダ（例: 0120）のパス
.EXAMPLE
    .\Prepare-CustomerPptx.ps1 -DateFolder "C:\...\2026\0120"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$DateFolder,

    [string]$WorkspaceRoot = $null
)

$ErrorActionPreference = "Stop"

# モジュール読み込み
Import-Module "$PSScriptRoot\PptxCommon.psm1" -Force

Write-StepHeader "Prepare-CustomerPptx.ps1"
Write-Info "対象フォルダ: $DateFolder"

function Resolve-WorkspaceRootPath {
    param(
        [string]$ExplicitWorkspaceRoot,
        [string]$DateFolderPath
    )

    $scriptParent = Split-Path $PSScriptRoot -Parent
    $skillsDir = Split-Path $scriptParent -Parent
    $githubDir = Split-Path $skillsDir -Parent
    $isSkillScript = ((Split-Path $skillsDir -Leaf) -eq 'skills' -and (Split-Path $githubDir -Leaf) -eq '.github')
    $skillPackageRoot = if ($isSkillScript) { $scriptParent } else { $null }

    if ($ExplicitWorkspaceRoot) {
        return (Resolve-Path -LiteralPath $ExplicitWorkspaceRoot).Path
    }

    try {
        $resolvedDateFolder = (Resolve-Path -LiteralPath $DateFolderPath -ErrorAction Stop).Path
        $candidateRoot = Split-Path $resolvedDateFolder -Parent
        if ($isSkillScript -and $candidateRoot -eq $skillPackageRoot) {
            throw "skill package root cannot be used as workspace root"
        }
        return $candidateRoot
    } catch {
        # DateFolder must exist for a real run because manifest/fetched-updates.json is required.
    }

    if ($isSkillScript) {
        throw "Workspace root を特定できません。skill 配下の script を直接実行する場合は -WorkspaceRoot を指定するか、root scripts/ に runtime copy を作成してください。"
    }

    $fallbackExcludeConfig = Join-Path $scriptParent ".config\exclude-keywords.json"
    if (Test-Path -LiteralPath $fallbackExcludeConfig) {
        return $scriptParent
    }

    throw "Workspace root を特定できません。DateFolder が存在すること、または -WorkspaceRoot が指定されていることを確認してください。"
}

try {
    $workspaceRootPath = Resolve-WorkspaceRootPath -ExplicitWorkspaceRoot $WorkspaceRoot -DateFolderPath $DateFolder
} catch {
    Write-Failure $_.Exception.Message
    exit 1
}

$configDir = Join-Path $workspaceRootPath ".config"
Write-Info "設定フォルダ: $configDir"

if (-not [System.IO.Path]::IsPathRooted($DateFolder)) {
    $DateFolder = Join-Path $workspaceRootPath $DateFolder
}

try {
    $DateFolder = (Resolve-Path -LiteralPath $DateFolder).Path
} catch {
    Write-Failure "日付フォルダが見つかりません: $DateFolder"
    exit 1
}

Write-Info "解決済み日付フォルダ: $DateFolder"

# ============================================================
# キーワード定義
# ============================================================

# 優先キーワード（マッチしたら Weekly）
$priorityKeywords = @{
    # Breaking（最優先）
    "Breaking" = @{ Category = "Breaking"; Priority = 1 }
    "廃止" = @{ Category = "Breaking"; Priority = 1 }
    "Retirement" = @{ Category = "Breaking"; Priority = 1 }
    "Deprecated" = @{ Category = "Breaking"; Priority = 1 }
    "サポート終了" = @{ Category = "Breaking"; Priority = 1 }
    "EOL" = @{ Category = "Breaking"; Priority = 1 }

    # IaaS（優先度高）
    "仮想マシン" = @{ Category = "IaaS"; Priority = 2 }
    "Virtual Machine" = @{ Category = "IaaS"; Priority = 2 }
    "VM" = @{ Category = "IaaS"; Priority = 2 }
    "VMSS" = @{ Category = "IaaS"; Priority = 2 }
    "Disk" = @{ Category = "IaaS"; Priority = 2 }
    "ディスク" = @{ Category = "IaaS"; Priority = 2 }
    "Premium SSD" = @{ Category = "IaaS"; Priority = 2 }

    # Network
    "VNet" = @{ Category = "Network"; Priority = 3 }
    "仮想ネットワーク" = @{ Category = "Network"; Priority = 3 }
    "ExpressRoute" = @{ Category = "Network"; Priority = 3 }
    "Firewall" = @{ Category = "Network"; Priority = 3 }
    "Load Balancer" = @{ Category = "Network"; Priority = 3 }
    "Bastion" = @{ Category = "Network"; Priority = 3 }
    "Private Endpoint" = @{ Category = "Network"; Priority = 3 }
    "Private Link" = @{ Category = "Network"; Priority = 3 }
    "NAT Gateway" = @{ Category = "Network"; Priority = 3 }
    "既定の送信" = @{ Category = "Network"; Priority = 3 }

    # Storage
    "ストレージ" = @{ Category = "Storage"; Priority = 4 }
    "Storage Account" = @{ Category = "Storage"; Priority = 4 }
    "NetApp" = @{ Category = "Storage"; Priority = 4 }
    "Blob" = @{ Category = "Storage"; Priority = 4 }
    "Azure Files" = @{ Category = "Storage"; Priority = 4 }

    # Backup / DR
    "Backup" = @{ Category = "Backup"; Priority = 5 }
    "バックアップ" = @{ Category = "Backup"; Priority = 5 }
    "Site Recovery" = @{ Category = "Backup"; Priority = 5 }
    "Recovery Services" = @{ Category = "Backup"; Priority = 5 }

    # Security
    "Key Vault" = @{ Category = "Security"; Priority = 6 }
    "Defender" = @{ Category = "Security"; Priority = 6 }
    "Sentinel" = @{ Category = "Security"; Priority = 6 }
    "Entra" = @{ Category = "Security"; Priority = 6 }

    # Monitoring
    "Monitor" = @{ Category = "Monitoring"; Priority = 7 }
    "Log Analytics" = @{ Category = "Monitoring"; Priority = 7 }
    "Application Insights" = @{ Category = "Monitoring"; Priority = 7 }

    # Hybrid
    "Azure Arc" = @{ Category = "Hybrid"; Priority = 8 }

    # AI（注力分野）
    "AI" = @{ Category = "AI"; Priority = 9 }
    "OpenAI" = @{ Category = "AI"; Priority = 9 }
    "Copilot" = @{ Category = "AI"; Priority = 9 }
    "Agent" = @{ Category = "AI"; Priority = 9 }
    "SRE" = @{ Category = "AI"; Priority = 9 }
}

# 顧客別の優先キーワード（存在する場合は組み込み既定を上書き）
$keywordsJsonPath = Join-Path $configDir "customer-keywords.json"
if (Test-Path $keywordsJsonPath) {
    try {
        $kwConfig = Get-Content $keywordsJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($kwConfig.priorityKeywords) {
            $loaded = @{}
            foreach ($p in $kwConfig.priorityKeywords.PSObject.Properties) {
                $loaded[$p.Name] = @{ Category = [string]$p.Value.Category; Priority = [int]$p.Value.Priority }
            }
            if ($loaded.Count -gt 0) {
                $priorityKeywords = $loaded
                Write-Info "優先キーワードを .config/customer-keywords.json から読み込みました（$($loaded.Count) 件）"
            }
        }
    } catch {
        Write-Info "customer-keywords.json の読み込みに失敗したため組み込み既定を使用します: $($_.Exception.Message)"
    }
}

# 除外キーワード（マッチしたら Appendix に強制）
# 📌 SSOT: .config/exclude-keywords.json（単一ファイルで一元管理）
$excludeJsonPath = Join-Path $configDir "exclude-keywords.json"
if (-not (Test-Path $excludeJsonPath)) {
    Write-Failure "除外キーワード定義が見つかりません: $excludeJsonPath。Bootstrap を実行するか、-WorkspaceRoot で workspace root を指定してください。"
    exit 1
}
$excludeConfig = Get-Content $excludeJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
$excludeKeywords = @()
foreach ($category in $excludeConfig.excludeKeywords.PSObject.Properties) {
    foreach ($pattern in @($category.Value)) {
        $excludeKeywords += [pscustomobject]@{
            Category = $category.Name
            Pattern = [string]$pattern
        }
    }
}
$overrideLabels = @($excludeConfig.overrideToWeekly.labels)
$overrideExcludedCategories = @($excludeConfig.overrideToWeekly.excludeCategories)

# ============================================================
# 入力ソース決定: MCP fetched-updates.json 必須
# ============================================================

$manifestFolder = "$DateFolder\manifest"
$fetchedPath = Join-Path $manifestFolder 'fetched-updates.json'
if (-not (Test-Path $fetchedPath)) {
    Write-Failure "MCP fetched-updates.json が見つかりません。先に Fetch-AzureUpdates.ps1 を実行してください: $fetchedPath"
    exit 1
}
Write-Info "入力モード: MCP fetched-updates.json ($fetchedPath)"
$existingClassificationByTitle = @{}
$notesByTitle = @{}

if (Test-Path "$manifestFolder\classification.json") {
    $existingClassification = Get-Content "$manifestFolder\classification.json" -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($item in @($existingClassification.weekly) + @($existingClassification.appendix)) {
        if ($item -and $item.title) {
            $existingClassificationByTitle[(Get-CleanSlideTitle -Title $item.title)] = $item
        }
    }
}

if (Test-Path "$manifestFolder\notes.json") {
    $notesData = Get-Content "$manifestFolder\notes.json" -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($item in @($notesData.weekly) + @($notesData.appendix)) {
        if ($item -and $item.title) {
            $notesByTitle[(Get-CleanSlideTitle -Title $item.title)] = $item
        }
    }
}

function Get-PreparedKeypoint {
    param(
        [string]$Title
    )

    $lookupTitle = Get-CleanSlideTitle -Title $Title
    $existingItem = $existingClassificationByTitle[$lookupTitle]
    if ($existingItem -and $existingItem.keypoint -and $existingItem.keypoint.Length -gt 5) {
        return $existingItem.keypoint
    }

    $notesItem = $notesByTitle[$lookupTitle]
    if (-not $notesItem) { return $null }

    if ($notesItem.systemImpact -match "活用推奨|要対応|影響なし|影響あり") {
        return $notesItem.systemImpact
    }
    if ($notesItem.userValue) {
        return $notesItem.userValue
    }
    if ($notesItem.systemImpact) {
        return $notesItem.systemImpact
    }
    return $null
}

function Get-LabelSortRank {
    param(
        [string]$Label
    )

    switch ($Label) {
        "廃止" { return 1 }
        "GA" { return 2 }
        "Preview" { return 3 }
        default { return 4 }
    }
}

function Test-ConfigPatternMatch {
    param(
        [string]$Text,
        [string]$Pattern
    )

    try {
        return [regex]::IsMatch($Text, $Pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    } catch {
        return $Text -match [regex]::Escape($Pattern)
    }
}

# ============================================================
# 分析（共通: キーワード分類ヘルパー）
# ============================================================

function Get-FetchedClassification {
    param(
        [string]$Text,
        [string]$Label
    )
    $matchedKeyword = $null
    $category = ""
    $priority = 999
    $excluded = $false
    $matchedExcludeCategory = $null

    foreach ($ex in $excludeKeywords) {
        if (Test-ConfigPatternMatch -Text $Text -Pattern $ex.Pattern) {
            $excluded = $true
            $matchedExcludeCategory = $ex.Category
            break
        }
    }

    if ($excluded -and $Label -in $overrideLabels -and $overrideExcludedCategories -notcontains $matchedExcludeCategory) {
        $excluded = $false
    }

    if (-not $excluded) {
        foreach ($kw in $priorityKeywords.Keys) {
            if ($Text -match [regex]::Escape($kw)) {
                $matchedKeyword = $kw
                $category = $priorityKeywords[$kw].Category
                $priority = $priorityKeywords[$kw].Priority
                break
            }
        }
    }

    if (-not $matchedKeyword -and -not $excluded) {
        $category = "AIReview"
        $priority = 100
    }

    return [pscustomobject]@{
        matchedKeyword = $matchedKeyword
        category       = $category
        priority       = $priority
        excluded       = $excluded
    }
}

# ============================================================
# PPTX 分析
# ============================================================

$allSlides = @()

# --- MCP fetched-updates.json から分類 ---
$fetched = Get-Content $fetchedPath -Raw -Encoding UTF8 | ConvertFrom-Json
Write-Info "fetched 更新: $($fetched.Count) 件"
foreach ($u in $fetched) {
        $matchText = @($u.title, $u.targetService, ($u.products -join ' '), ($u.productCategories -join ' ')) -join ' '
        $c = Get-FetchedClassification -Text $matchText -Label $u.label

        # 5 フィールド優先・後方互換フォールバック
        # before/after/customerImpact/pricing/japanRegion が無ければ whatChanged/userBenefit/regionNote から導出
        $backgroundVal     = if ($u.background)     { $u.background }     else { '' }
        $beforeVal         = if ($u.before)         { $u.before }         else { '' }
        $afterVal          = if ($u.after)          { $u.after }          else { $u.whatChanged }
        $customerImpactVal = if ($u.customerImpact) { $u.customerImpact } else { $u.userBenefit }
        $pricingVal        = if ($u.pricing)        { $u.pricing }        else { '課金面は公式価格ページで要確認' }
        $japanRegionVal    = if ($u.japanRegion)    { $u.japanRegion }    else { $u.regionNote }

        # bodyContent (後方互換): 6 項目を改行連結
        $bodySegments = @()
        if ($backgroundVal)     { $bodySegments += "仕組み：`n$backgroundVal" }
        if ($beforeVal)         { $bodySegments += "これまで：`n$beforeVal" }
        if ($afterVal)          { $bodySegments += "今後：`n$afterVal" }
        if ($customerImpactVal) { $bodySegments += "お客様にとっての価値：`n$customerImpactVal" }
        $pricingLine = ''
        if ($pricingVal -and $japanRegionVal) { $pricingLine = "課金：$pricingVal　/　日本リージョン：$japanRegionVal" }
        elseif ($pricingVal)                  { $pricingLine = "課金：$pricingVal" }
        elseif ($japanRegionVal)              { $pricingLine = "日本リージョン：$japanRegionVal" }
        if ($pricingLine) { $bodySegments += $pricingLine }
        $bodyContentVal = $bodySegments -join "`n"

        $allSlides += [pscustomobject]@{
            updateId       = "$($u.id)"
            sourceUrl      = $u.sourceUrl
            learnUrl       = $u.learnUrl
            targetService  = $u.targetService
            background     = $backgroundVal
            before         = $beforeVal
            after          = $afterVal
            customerImpact = $customerImpactVal
            pricing        = $pricingVal
            japanRegion    = $japanRegionVal
            bodyContent    = $bodyContentVal
            regionStatus   = $u.regionNote
            title          = $u.title
            label          = $u.label
            labelPriority  = (Get-LabelSortRank -Label $u.label)
            matchedKeyword = $c.matchedKeyword
            category       = $c.category
            priority       = $c.priority
            excluded       = $c.excluded
            keypoint       = if ($u.keypoint) { $u.keypoint } else { Get-PreparedKeypoint -Title $u.title }
        }
}

# ============================================================
# 分類
# ============================================================

Write-StepHeader "分類結果"

# Weekly（excluded = false）
$weekly = $allSlides | Where-Object { -not $_.excluded } | Sort-Object @{ Expression = { Get-LabelSortRank -Label $_.label } }, @{ Expression = { $_.title } }

# Appendix（excluded = true）
$appendix = $allSlides | Where-Object { $_.excluded } | Sort-Object @{ Expression = { Get-LabelSortRank -Label $_.label } }, @{ Expression = { $_.title } }

Write-Host ""
Write-Host "=== Weekly Topics ($($weekly.Count) 件) ===" -ForegroundColor Green
foreach ($w in $weekly) {
    Write-Host "  [$($w.label)] $($w.title.Substring(0, [Math]::Min(60, $w.title.Length)))..."
}

Write-Host ""
Write-Host "=== Appendix ($($appendix.Count) 件) ===" -ForegroundColor Yellow
foreach ($a in $appendix) {
    Write-Host "  [$($a.label)] $($a.title.Substring(0, [Math]::Min(60, $a.title.Length)))..."
}

# ============================================================
# JSON 出力
# ============================================================

$classification = @{
    generatedAt = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
    summary = @{
        totalSlides = $allSlides.Count
        weeklyCount = $weekly.Count
        appendixCount = $appendix.Count
    }
    weekly = $weekly
    appendix = $appendix
}

# manifest フォルダを作成
if (-not (Test-Path $manifestFolder)) {
    New-Item -ItemType Directory -Path $manifestFolder -Force | Out-Null
}

$jsonPath = "$manifestFolder\classification.json"
$classification | ConvertTo-Json -Depth 10 | Out-File $jsonPath -Encoding UTF8

Write-Success "classification.json 出力完了: $jsonPath"
Write-Host ""
Write-Host "次のステップ: Build-CustomerPptx.ps1 -DateFolder `"$DateFolder`"" -ForegroundColor Cyan

