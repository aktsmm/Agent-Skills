<#
.SYNOPSIS
    顧客ワークスペースを初期化するスクリプト

.DESCRIPTION
    customer-workspaceスキルのセットアップを自動化します。
    - フォルダ構造の作成
    - テンプレートファイルのコピー
    - 顧客プロファイルの初期化

.PARAMETER CustomerName
    顧客名（必須）

.PARAMETER ContractType
    契約または支援形態（任意。公開テンプレートでは組織固有の契約コードや社内用語を前提にしない）

.PARAMETER ContractPeriod
    契約期間（例: 2025/04 - 2028/03）

.PARAMETER WorkspacePath
    ワークスペースのパス（デフォルト: カレントディレクトリ）

.EXAMPLE
    .\Initialize-CustomerWorkspace.ps1 -CustomerName "ABC株式会社様"
    
.EXAMPLE
    .\Initialize-CustomerWorkspace.ps1 -CustomerName "ABC株式会社様" -ContractType "年間支援" -ContractPeriod "2025/04 - 2028/03"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$CustomerName,

    [Parameter(Mandatory = $false)]
    [string]$ContractType = "",

    [Parameter(Mandatory = $false)]
    [string]$ContractPeriod = "",

    [Parameter(Mandatory = $false)]
    [string]$KeyContacts = "",

    [Parameter(Mandatory = $false)]
    [string]$WorkspacePath = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

# スキルのルートパスを取得
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillRoot = Split-Path -Parent $ScriptDir
$AssetsPath = Join-Path $SkillRoot "assets"
$TemplatesPath = Join-Path $AssetsPath "_templates"

function Expand-TemplateContent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$TemplatePath
    )

    $content = Get-Content $TemplatePath -Raw
    $content = $content -replace '\{\{CUSTOMER_NAME\}\}', $CustomerName
    $content = $content -replace '\{\{CONTRACT_TYPE\}\}', $(if ($ContractType) { $ContractType } else { "未設定" })
    $content = $content -replace '\{\{CONTRACT_PERIOD\}\}', $(if ($ContractPeriod) { $ContractPeriod } else { "未設定" })
    $content = $content -replace '\{\{KEY_CONTACTS\}\}', $(if ($KeyContacts) { $KeyContacts } else { "" })
    $content = $content -replace '\{\{YEAR\}\}', (Get-Date -Format "yyyy")
    $content = $content -replace '\{\{YEAR_MONTH\}\}', (Get-Date -Format "yyyy-MM")
    $content = $content -replace '\{\{START_DATE\}\}', (Get-Date -Format "yyyy-MM-dd")
    $content = $content -replace '\{\{TODAY\}\}', (Get-Date -Format "yyyy-MM-dd")
    $content = $content -replace '\{\{MEETING_TITLE\}\}', "YYYY-MM-DD topic"

    return $content
}

Write-Host "🚀 顧客ワークスペース初期化を開始します..." -ForegroundColor Cyan
Write-Host "   顧客名: $CustomerName" -ForegroundColor Gray
Write-Host "   ワークスペース: $WorkspacePath" -ForegroundColor Gray

# フォルダ構造の作成
$folders = @(
    ".github",
    ".github\prompts",
    "_inbox",
    "_questions",
    "_knowledge",
    "_customer",
    "_templates",
    "research-reports"
)

foreach ($folder in $folders) {
    $path = Join-Path $WorkspacePath $folder
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "   📁 作成: $folder" -ForegroundColor Green
    }
}

# 現在の年月を取得
$currentYearMonth = Get-Date -Format "yyyy-MM"

# copilot-instructions.md の処理
$copilotInstructionsPath = Join-Path $WorkspacePath ".github\copilot-instructions.md"
$copilotInstructionsAsset = Join-Path $AssetsPath "copilot-instructions.md"

if (Test-Path $copilotInstructionsPath) {
    # 既存ファイルに追記
    $existingContent = Get-Content $copilotInstructionsPath -Raw
    $newContent = Get-Content $copilotInstructionsAsset -Raw
    
    # 顧客情報を置換
    $newContent = $newContent -replace '\{\{CUSTOMER_NAME\}\}', $CustomerName
    $newContent = $newContent -replace '\{\{CONTRACT_TYPE\}\}', $(if ($ContractType) { $ContractType } else { "未設定" })
    $newContent = $newContent -replace '\{\{CONTRACT_PERIOD\}\}', $(if ($ContractPeriod) { $ContractPeriod } else { "未設定" })
    $newContent = $newContent -replace '\{\{KEY_CONTACTS\}\}', $(if ($KeyContacts) { $KeyContacts } else { "未設定" })
    
    $combinedContent = $existingContent + "`n`n---`n`n" + $newContent
    Set-Content -Path $copilotInstructionsPath -Value $combinedContent -Encoding UTF8
    Write-Host "   📝 追記: .github/copilot-instructions.md" -ForegroundColor Yellow
} else {
    # 新規作成
    $content = Get-Content $copilotInstructionsAsset -Raw
    $content = $content -replace '\{\{CUSTOMER_NAME\}\}', $CustomerName
    $content = $content -replace '\{\{CONTRACT_TYPE\}\}', $(if ($ContractType) { $ContractType } else { "未設定" })
    $content = $content -replace '\{\{CONTRACT_PERIOD\}\}', $(if ($ContractPeriod) { $ContractPeriod } else { "未設定" })
    $content = $content -replace '\{\{KEY_CONTACTS\}\}', $(if ($KeyContacts) { $KeyContacts } else { "未設定" })
    Set-Content -Path $copilotInstructionsPath -Value $content -Encoding UTF8
    Write-Host "   📝 作成: .github/copilot-instructions.md" -ForegroundColor Green
}

# プロンプトファイルのコピー
$prompts = @("inbox.prompt.md", "convert-meeting-minutes.prompt.md", "extract-questions.prompt.md")
foreach ($prompt in $prompts) {
    $src = Join-Path $AssetsPath $prompt
    $dst = Join-Path $WorkspacePath ".github\prompts\$prompt"
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
        Write-Host "   📝 作成: .github/prompts/$prompt" -ForegroundColor Green
    }
}

# テンプレートのコピー
$templates = @("meeting-minutes.md", "internal-memo.md", "customer-profile.md", "attachments.md")
foreach ($template in $templates) {
    $src = Join-Path $TemplatesPath $template
    $dst = Join-Path $WorkspacePath "_templates\$template"
    if (Test-Path $src) {
        $content = Expand-TemplateContent -TemplatePath $src
        Set-Content -Path $dst -Value $content -Encoding UTF8
        Write-Host "   📝 作成: _templates/$template" -ForegroundColor Green
    }
}

# ルートドキュメントの作成
$workspaceReadmePath = Join-Path $WorkspacePath "README.md"
if (-not (Test-Path $workspaceReadmePath)) {
    $workspaceReadmeTemplate = Join-Path $TemplatesPath "workspace-readme.md"
    if (Test-Path $workspaceReadmeTemplate) {
        $content = Expand-TemplateContent -TemplatePath $workspaceReadmeTemplate
        Set-Content -Path $workspaceReadmePath -Value $content -Encoding UTF8
        Write-Host "   📝 作成: README.md" -ForegroundColor Green
    }
}

$workspaceSummaryPath = Join-Path $WorkspacePath "workspace-summary.md"
if (-not (Test-Path $workspaceSummaryPath)) {
    $workspaceSummaryTemplate = Join-Path $TemplatesPath "workspace-summary.md"
    if (Test-Path $workspaceSummaryTemplate) {
        $content = Expand-TemplateContent -TemplatePath $workspaceSummaryTemplate
        Set-Content -Path $workspaceSummaryPath -Value $content -Encoding UTF8
        Write-Host "   📝 作成: workspace-summary.md" -ForegroundColor Green
    }
}

# インボックス初期ファイル作成
$inboxPath = Join-Path $WorkspacePath "_inbox\$currentYearMonth.md"
if (-not (Test-Path $inboxPath)) {
    $inboxContent = @"
# $currentYearMonth インボックス

> 💡 ``/prompt inbox`` で追記。タグで検索可能。

---

"@
    Set-Content -Path $inboxPath -Value $inboxContent -Encoding UTF8
    Write-Host "   📝 作成: _inbox/$currentYearMonth.md" -ForegroundColor Green
}

# 質問一覧初期ファイル作成
$questionsPath = Join-Path $WorkspacePath "_questions\$currentYearMonth.md"
if (-not (Test-Path $questionsPath)) {
    $questionsContent = @"
# $currentYearMonth 質問・アクション

> 💡 ``/prompt extract-questions`` で会議ログから抽出して追記。

---

"@
    Set-Content -Path $questionsPath -Value $questionsContent -Encoding UTF8
    Write-Host "   📝 作成: _questions/$currentYearMonth.md" -ForegroundColor Green
}

# ナレッジ台帳初期ファイル作成
$knowledgeReadmePath = Join-Path $WorkspacePath "_knowledge\README.md"
if (-not (Test-Path $knowledgeReadmePath)) {
    $knowledgeReadmeTemplate = Join-Path $TemplatesPath "knowledge-readme.md"
    if (Test-Path $knowledgeReadmeTemplate) {
        $content = Expand-TemplateContent -TemplatePath $knowledgeReadmeTemplate
        Set-Content -Path $knowledgeReadmePath -Value $content -Encoding UTF8
        Write-Host "   📝 作成: _knowledge/README.md" -ForegroundColor Green
    }
}

$knowledgeGeneralPath = Join-Path $WorkspacePath "_knowledge\general.md"
if (-not (Test-Path $knowledgeGeneralPath)) {
    $knowledgeGeneralTemplate = Join-Path $TemplatesPath "knowledge-general.md"
    if (Test-Path $knowledgeGeneralTemplate) {
        $content = Expand-TemplateContent -TemplatePath $knowledgeGeneralTemplate
        Set-Content -Path $knowledgeGeneralPath -Value $content -Encoding UTF8
        Write-Host "   📝 作成: _knowledge/general.md" -ForegroundColor Green
    }
}

# 顧客プロファイル作成
$profilePath = Join-Path $WorkspacePath "_customer\profile.md"
if (-not (Test-Path $profilePath)) {
    $profileTemplate = Join-Path $TemplatesPath "customer-profile.md"
    if (Test-Path $profileTemplate) {
        $content = Expand-TemplateContent -TemplatePath $profileTemplate
        Set-Content -Path $profilePath -Value $content -Encoding UTF8
        Write-Host "   📝 作成: _customer/profile.md" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "✅ ワークスペースセットアップ完了!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 作成されたファイル:" -ForegroundColor Cyan
Write-Host "   - .github/copilot-instructions.md（自動判定ルール）"
Write-Host "   - .github/prompts/inbox.prompt.md（インボックス）"
Write-Host "   - .github/prompts/convert-meeting-minutes.prompt.md（議事録変換）"
Write-Host "   - .github/prompts/extract-questions.prompt.md（質問抽出）"
Write-Host "   - README.md（開始案内）"
Write-Host "   - workspace-summary.md（引き継ぎサマリ）"
Write-Host "   - _inbox/$currentYearMonth.md（インボックス）"
Write-Host "   - _questions/$currentYearMonth.md（質問・アクション）"
Write-Host "   - _knowledge/（汎用知見台帳）"
Write-Host "   - _customer/profile.md（顧客プロファイル）"
Write-Host "   - _templates/（テンプレート）"
Write-Host "   - research-reports/（調査・レポート成果物）"
Write-Host ""
Write-Host "🎯 使い方:" -ForegroundColor Cyan
Write-Host "   1. 情報を貼るだけ → 自動でインボックスに蓄積"
Write-Host "   2. Teams AI議事録を貼る → 自動で議事録変換"
Write-Host "   3. /prompt inbox で明示的にインボックス追記"
