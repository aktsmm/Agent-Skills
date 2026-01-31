<#
.SYNOPSIS
    Initialize biz-ops workspace folder structure

.DESCRIPTION
    Creates all required folders and initial files for a biz-ops workspace.
    Run this after interview to set up the basic structure.

.PARAMETER WorkspacePath
    Target workspace path (default: current directory)

.PARAMETER Customers
    Array of customer IDs to create (e.g., @("contoso", "fabrikam"))

.PARAMETER Country
    Country code for holiday configuration (default: japan)

.EXAMPLE
    .\Initialize-BizOpsWorkspace.ps1 -WorkspacePath "D:\my-biz-ops" -Customers @("contoso", "fabrikam")

.EXAMPLE
    .\Initialize-BizOpsWorkspace.ps1 -Customers @("acme", "globex") -Country "us"
#>

param(
    [string]$WorkspacePath = (Get-Location).Path,
    [string[]]$Customers = @(),
    [string]$Country = "japan"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Initializing Biz-Ops Workspace" -ForegroundColor Cyan
Write-Host "   Path: $WorkspacePath" -ForegroundColor Gray
Write-Host ""

# ============================================
# 1. Create Folder Structure
# ============================================

Write-Host "📁 Creating folder structure..." -ForegroundColor Yellow

$folders = @(
    "ActivityReport",
    "Customers",
    "Tasks",
    "_internal\_inbox",
    "_internal\_meetings",
    "_internal\tech-connect",
    "_internal\team",
    "_inbox",
    "_datasources",
    "_workiq",
    ".github\agents",
    ".github\prompts"
)

foreach ($folder in $folders) {
    $fullPath = Join-Path $WorkspacePath $folder
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "   ✅ Created: $folder" -ForegroundColor Green
    } else {
        Write-Host "   ⏭️ Exists: $folder" -ForegroundColor Gray
    }
}

# ============================================
# 2. Create Customer Workspaces
# ============================================

if ($Customers.Count -gt 0) {
    Write-Host ""
    Write-Host "👥 Creating customer workspaces..." -ForegroundColor Yellow
    
    foreach ($customerId in $Customers) {
        $customerPath = Join-Path $WorkspacePath "Customers\$customerId"
        $subfolders = @("_inbox", "_meetings")
        
        foreach ($subfolder in $subfolders) {
            $subPath = Join-Path $customerPath $subfolder
            if (-not (Test-Path $subPath)) {
                New-Item -ItemType Directory -Path $subPath -Force | Out-Null
            }
        }
        
        # Create profile.md
        $profilePath = Join-Path $customerPath "profile.md"
        if (-not (Test-Path $profilePath)) {
            @"
# Customer: $customerId

## Basic Information

| Item | Value |
|------|-------|
| Customer ID | $customerId |
| Customer Name | <!-- Add customer name --> |
| Primary Contact | <!-- Add contact name --> |
| Created | $(Get-Date -Format "yyyy-MM-dd") |

## Notes

<!-- Add customer notes here -->
"@ | Out-File -FilePath $profilePath -Encoding utf8
        }
        
        # Create tasks.md
        $tasksPath = Join-Path $customerPath "tasks.md"
        if (-not (Test-Path $tasksPath)) {
            @"
# Tasks: $customerId

## Active

<!-- No active tasks -->

## Completed

<!-- No completed tasks -->
"@ | Out-File -FilePath $tasksPath -Encoding utf8
        }
        
        Write-Host "   ✅ Created: Customers/$customerId" -ForegroundColor Green
    }
}

# ============================================
# 3. Create Initial Files
# ============================================

Write-Host ""
Write-Host "📄 Creating initial files..." -ForegroundColor Yellow

# Tasks files
$taskFiles = @{
    "Tasks\active.md" = @"
# Active Tasks

## High Priority

<!-- No high priority tasks -->

## Medium Priority

<!-- No medium priority tasks -->

## Low Priority

<!-- No low priority tasks -->
"@
    "Tasks\completed.md" = @"
# Completed Tasks

## $(Get-Date -Format "yyyy-MM")

<!-- No completed tasks this month -->
"@
    "Tasks\backlog.md" = @"
# Backlog

<!-- No backlog items -->
"@
    "Tasks\unclassified.md" = @"
# Unclassified Tasks

<!-- Tasks that don't fit existing categories -->
"@
}

foreach ($file in $taskFiles.GetEnumerator()) {
    $filePath = Join-Path $WorkspacePath $file.Key
    if (-not (Test-Path $filePath)) {
        $file.Value | Out-File -FilePath $filePath -Encoding utf8
        Write-Host "   ✅ Created: $($file.Key)" -ForegroundColor Green
    }
}

# Customers README
$customersReadme = Join-Path $WorkspacePath "Customers\README.md"
if (-not (Test-Path $customersReadme)) {
    @"
# Customers

## Customer List

| Customer ID | Customer Name | Primary Contact |
|-------------|---------------|-----------------|
$(if ($Customers.Count -gt 0) { $Customers | ForEach-Object { "| $_ | <!-- Add name --> | <!-- Add contact --> |" } | Out-String } else { "| <!-- Add customers --> | | |" })

## Structure

Each customer folder contains:

- `profile.md` - Customer profile and notes
- `tasks.md` - Customer-specific tasks
- `_inbox/` - Information accumulation
- `_meetings/` - Meeting notes
"@ | Out-File -FilePath $customersReadme -Encoding utf8
    Write-Host "   ✅ Created: Customers/README.md" -ForegroundColor Green
}

# _internal README
$internalReadme = Join-Path $WorkspacePath "_internal\README.md"
if (-not (Test-Path $internalReadme)) {
    @"
# Internal

Internal events and activities storage.

## Structure

- `_inbox/` - General internal information
- `_meetings/` - Internal meeting notes
- `tech-connect/` - Tech Connect related
- `team/` - Team meetings and 1-on-1s
"@ | Out-File -FilePath $internalReadme -Encoding utf8
    Write-Host "   ✅ Created: _internal/README.md" -ForegroundColor Green
}

# _datasources README
$datasourcesReadme = Join-Path $WorkspacePath "_datasources\README.md"
if (-not (Test-Path $datasourcesReadme)) {
    @"
# Data Sources

Configuration for data sources used in report generation.

## Files

- `external-paths.md` - External folder references (OneDrive, Git repos, etc.)
- `workiq-spec.md` - workIQ query specification (optional)

## Usage

Configure external paths after setup interview.
Report generator will automatically check these sources.
"@ | Out-File -FilePath $datasourcesReadme -Encoding utf8
    Write-Host "   ✅ Created: _datasources/README.md" -ForegroundColor Green
}

# _workiq README
$workiqReadme = Join-Path $WorkspacePath "_workiq\README.md"
if (-not (Test-Path $workiqReadme)) {
    @"
# workIQ Configuration

workIQ (Microsoft 365 Copilot) integration settings.

## Files

- `{country}-holidays.md` - Holiday configuration for report skipping

## Note

workIQ integration is optional. The system works without it using workspace data.
"@ | Out-File -FilePath $workiqReadme -Encoding utf8
    Write-Host "   ✅ Created: _workiq/README.md" -ForegroundColor Green
}

# ============================================
# 4. Create ActivityReport Structure
# ============================================

$currentMonth = Get-Date -Format "yyyy-MM"
$monthPath = Join-Path $WorkspacePath "ActivityReport\$currentMonth"
$dailyPath = Join-Path $monthPath "daily"
$weeklyPath = Join-Path $monthPath "weekly"

if (-not (Test-Path $dailyPath)) {
    New-Item -ItemType Directory -Path $dailyPath -Force | Out-Null
    Write-Host "   ✅ Created: ActivityReport/$currentMonth/daily" -ForegroundColor Green
}
if (-not (Test-Path $weeklyPath)) {
    New-Item -ItemType Directory -Path $weeklyPath -Force | Out-Null
    Write-Host "   ✅ Created: ActivityReport/$currentMonth/weekly" -ForegroundColor Green
}

# ============================================
# 5. Summary
# ============================================

Write-Host ""
Write-Host "✅ Workspace initialization complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Copy agent templates from skill assets to .github/agents/" -ForegroundColor White
Write-Host "   2. Copy prompt templates from skill assets to .github/prompts/" -ForegroundColor White
Write-Host "   3. Create copilot-instructions.md with customer mappings" -ForegroundColor White
Write-Host "   4. Configure _datasources/external-paths.md (if using external folders)" -ForegroundColor White
Write-Host "   5. Copy holiday file to _workiq/$Country-holidays.md" -ForegroundColor White
Write-Host ""
Write-Host "📁 Created structure:" -ForegroundColor Cyan
Get-ChildItem -Path $WorkspacePath -Directory -Depth 1 | 
    Where-Object { $_.Name -ne ".git" } |
    ForEach-Object { Write-Host "   $($_.FullName.Replace($WorkspacePath, '.'))" -ForegroundColor Gray }
