<#
.SYNOPSIS
    Check external folder updates and sync changes to biz-ops workspace

.DESCRIPTION
    Monitor specified folders, detect updated files, and sync to workspace.
    Target extensions: .md, .txt, .xlsx, .pptx, .docx

.PARAMETER SourcePath
    External folder path to monitor (required)

.PARAMETER DestinationPath
    Destination biz-ops workspace path (default: current directory)

.PARAMETER DaysBack
    Number of days to look back for changes (default: 7)

.PARAMETER CustomerId
    Customer ID (e.g., contoso). Routes to Customers/{id}/ subfolder

.PARAMETER DryRun
    Preview mode - show changed files without syncing

.PARAMETER ShowContent
    Preview .md file contents (default: true)

.EXAMPLE
    # Check external folder (dry run)
    .\Check-ExternalFolders.ps1 -SourcePath "C:\Users\{user}\OneDrive\CustomerProjects" -DryRun

    # Sync to specific customer
    .\Check-ExternalFolders.ps1 -SourcePath "path\to\folder" -CustomerId "contoso" -DaysBack 3

    # Without content preview
    .\Check-ExternalFolders.ps1 -SourcePath "path\to\folder" -DryRun -ShowContent:$false
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePath,
    
    # TODO: Update this path to your workspace
    [string]$DestinationPath = $PWD.Path,
    
    [int]$DaysBack = 7,
    
    [string]$CustomerId,
    
    [switch]$DryRun,
    
    [bool]$ShowContent = $true
)

# === 設定 ===

# 対象ファイル拡張子
$TargetExtensions = @(".md", ".txt", ".xlsx", ".xls", ".pptx", ".ppt", ".docx", ".doc")

# 除外パターン
$ExcludePatterns = @(
    "*.github*",
    "*_templates*",
    "*\skills\*",
    "*\.venv*",
    "*node_modules*",
    "*\template\*",
    "*\.git\*"
)

# 顧客マッピング（自動検出用）
# TODO: Update this mapping based on your customer folder names
$CustomerMapping = @{
    # "FolderName" = "customer-id"
    # Example:
    # "01_CustomerA"  = "customer-a"
    # "02_CustomerB"  = "customer-b"
}

# 最終チェック記録ファイル
$LastCheckFile = Join-Path $DestinationPath "_datasources\scripts\.last-check"

# === 関数 ===

function Get-LastCheckTime {
    if (Test-Path $LastCheckFile) {
        try {
            return [datetime](Get-Content $LastCheckFile -Raw)
        } catch {
            return (Get-Date).AddDays(-$DaysBack)
        }
    }
    return (Get-Date).AddDays(-$DaysBack)
}

function Set-LastCheckTime {
    $dir = Split-Path $LastCheckFile -Parent
    if (-not (Test-Path $dir)) {
        New-Item -Path $dir -ItemType Directory -Force | Out-Null
    }
    (Get-Date).ToString("o") | Out-File $LastCheckFile -Force
}

function Test-ShouldExclude {
    param([string]$FilePath)
    
    foreach ($pattern in $ExcludePatterns) {
        if ($FilePath -like $pattern) {
            return $true
        }
    }
    return $false
}

function Get-CustomerIdFromPath {
    param([string]$FilePath)
    
    # 引数で指定されていればそれを使用
    if ($CustomerId) {
        return $CustomerId
    }
    
    # パスから自動検出
    foreach ($folder in $CustomerMapping.Keys) {
        if ($FilePath -like "*\$folder\*" -or $FilePath -like "*/$folder/*") {
            return $CustomerMapping[$folder]
        }
    }
    return $null
}

function Get-FileType {
    param([System.IO.FileInfo]$FileInfo)
    
    $name = $FileInfo.Name
    $ext = $FileInfo.Extension.ToLower()
    $dirName = $FileInfo.Directory.Name
    
    # ファイル名・ディレクトリから判定
    if ($dirName -eq "_inbox") { return "inbox" }
    if ($name -like "*_議事録*" -or $dirName -eq "_meetings") { return "meeting" }
    if ($name -like "*_内部メモ*") { return "memo" }
    
    # 拡張子から判定
    switch ($ext) {
        ".xlsx" { return "excel" }
        ".xls"  { return "excel" }
        ".pptx" { return "powerpoint" }
        ".ppt"  { return "powerpoint" }
        ".docx" { return "word" }
        ".doc"  { return "word" }
        ".txt"  { return "text" }
        default { return "other" }
    }
}

function Get-FileIcon {
    param([string]$FileType)
    
    switch ($FileType) {
        "inbox"      { return "📥" }
        "meeting"    { return "📝" }
        "memo"       { return "📋" }
        "excel"      { return "📊" }
        "powerpoint" { return "📽️" }
        "word"       { return "📄" }
        "text"       { return "📃" }
        default      { return "📄" }
    }
}

function Find-ChangedFiles {
    param(
        [string]$RootPath,
        [datetime]$Since
    )
    
    $changedFiles = @()
    
    # 対象拡張子のファイルを検索
    foreach ($ext in $TargetExtensions) {
        $pattern = "*$ext"
        $files = Get-ChildItem -Path $RootPath -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { 
                $_.LastWriteTime -gt $Since -and
                -not (Test-ShouldExclude $_.FullName)
            }
        
        foreach ($file in $files) {
            $customerId = Get-CustomerIdFromPath -FilePath $file.FullName
            $fileType = Get-FileType -FileInfo $file
            
            $changedFiles += [PSCustomObject]@{
                FullPath     = $file.FullName
                RelativePath = $file.FullName.Replace($RootPath, "").TrimStart("\").TrimStart("/")
                FileName     = $file.Name
                Extension    = $file.Extension.ToLower()
                LastModified = $file.LastWriteTime
                SizeKB       = [math]::Round($file.Length / 1KB, 1)
                CustomerId   = $customerId
                FileType     = $fileType
            }
        }
    }
    
    return $changedFiles | Sort-Object FullPath -Unique | Sort-Object LastModified -Descending
}

function Show-FileContent {
    param(
        [string]$FilePath,
        [int]$MaxLines = 30
    )
    
    $ext = [System.IO.Path]::GetExtension($FilePath).ToLower()
    
    # テキスト系のみ内容表示
    if ($ext -notin @(".md", ".txt")) {
        Write-Host "   (バイナリファイル - 内容プレビューなし)" -ForegroundColor Gray
        return
    }
    
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor DarkGray
    
    $content = Get-Content $FilePath -TotalCount $MaxLines -ErrorAction SilentlyContinue
    if ($content) {
        $content | ForEach-Object { Write-Host $_ }
        
        $totalLines = (Get-Content $FilePath -ErrorAction SilentlyContinue | Measure-Object -Line).Lines
        if ($totalLines -gt $MaxLines) {
            Write-Host "`n... ($($totalLines - $MaxLines) 行省略)" -ForegroundColor Yellow
        }
    }
    Write-Host ("=" * 60) -ForegroundColor DarkGray
}

function Get-DestinationFolder {
    param(
        [PSCustomObject]$FileInfo
    )
    
    $base = $DestinationPath
    
    if ($FileInfo.CustomerId) {
        $customerBase = Join-Path $base "Customers\$($FileInfo.CustomerId)"
        
        switch ($FileInfo.FileType) {
            "inbox"   { return Join-Path $customerBase "_inbox" }
            "meeting" { return Join-Path $customerBase "_meetings" }
            "memo"    { return Join-Path $customerBase "_inbox" }
            default   { return Join-Path $customerBase "_inbox" }
        }
    }
    
    # 顧客ID不明の場合
    return Join-Path $base "_inbox"
}

function Sync-ToBizOps {
    param(
        [PSCustomObject]$FileInfo
    )
    
    $destFolder = Get-DestinationFolder -FileInfo $FileInfo
    
    # フォルダ作成
    if (-not (Test-Path $destFolder)) {
        New-Item -Path $destFolder -ItemType Directory -Force | Out-Null
    }
    
    $destFile = Join-Path $destFolder $FileInfo.FileName
    
    # 差分チェック（既存ファイルとの比較）
    if (Test-Path $destFile) {
        $srcHash = (Get-FileHash $FileInfo.FullPath).Hash
        $dstHash = (Get-FileHash $destFile).Hash
        if ($srcHash -eq $dstHash) {
            Write-Host "  ✓ 変更なし（ハッシュ一致）" -ForegroundColor Gray
            return $false
        }
    }
    
    # コピー実行
    Copy-Item -Path $FileInfo.FullPath -Destination $destFile -Force
    Write-Host "  ✅ 同期完了: $destFile" -ForegroundColor Green
    return $true
}

# === メイン処理 ===

# パス検証
if (-not (Test-Path $SourcePath)) {
    Write-Host "❌ エラー: ソースパスが存在しません: $SourcePath" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔍 外部フォルダ更新チェック" -ForegroundColor Cyan
Write-Host "   ソース: $SourcePath" -ForegroundColor White
Write-Host "   同期先: $DestinationPath" -ForegroundColor White
Write-Host "   期間: 過去 $DaysBack 日間"
Write-Host "   対象: $($TargetExtensions -join ', ')"
if ($CustomerId) {
    Write-Host "   顧客ID: $CustomerId" -ForegroundColor Yellow
}
if ($DryRun) {
    Write-Host "   モード: DryRun（同期なし）" -ForegroundColor Yellow
}
Write-Host ""

# 最終チェック時刻を取得
$lastCheck = Get-LastCheckTime
Write-Host "📅 前回チェック: $($lastCheck.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Gray
Write-Host ""

# 変更ファイルを検索
$changedFiles = Find-ChangedFiles -RootPath $SourcePath -Since $lastCheck

if ($changedFiles.Count -eq 0) {
    Write-Host "✅ 変更なし" -ForegroundColor Green
    exit 0
}

Write-Host "📋 変更ファイル: $($changedFiles.Count) 件" -ForegroundColor Yellow
Write-Host ""

# 結果表示
$syncCount = 0
foreach ($file in $changedFiles) {
    $icon = Get-FileIcon -FileType $file.FileType
    $customerLabel = if ($file.CustomerId) { "[$($file.CustomerId)]" } else { "[未マッピング]" }
    
    Write-Host "$icon $customerLabel $($file.FileName)" -ForegroundColor White
    Write-Host "   パス: $($file.RelativePath)" -ForegroundColor Gray
    Write-Host "   更新: $($file.LastModified.ToString('yyyy-MM-dd HH:mm:ss')) | サイズ: $($file.SizeKB) KB" -ForegroundColor Gray
    
    # 内容プレビュー
    if ($ShowContent) {
        Show-FileContent -FilePath $file.FullPath -MaxLines 25
    }
    
    # 同期処理
    if (-not $DryRun) {
        if (Sync-ToBizOps -FileInfo $file) {
            $syncCount++
        }
    }
    
    Write-Host ""
}

# 最終チェック時刻を更新
if (-not $DryRun) {
    Set-LastCheckTime
    Write-Host "✅ 完了: $syncCount 件を同期しました" -ForegroundColor Green
} else {
    Write-Host "ℹ️ DryRunモード: 同期は実行されませんでした" -ForegroundColor Yellow
}

# サマリー出力
Write-Host ""
Write-Host "📊 サマリー" -ForegroundColor Cyan

# 顧客別
Write-Host "  [顧客別]" -ForegroundColor White
$changedFiles | Group-Object CustomerId | ForEach-Object {
    $label = if ($_.Name) { $_.Name } else { "未マッピング" }
    Write-Host "    $label : $($_.Count) 件"
}

# ファイル種別
Write-Host "  [種別]" -ForegroundColor White
$changedFiles | Group-Object FileType | ForEach-Object {
    $icon = Get-FileIcon -FileType $_.Name
    Write-Host "    $icon $($_.Name) : $($_.Count) 件"
}
