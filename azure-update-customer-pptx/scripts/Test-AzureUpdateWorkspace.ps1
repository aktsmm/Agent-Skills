<#
.SYNOPSIS
    Preflight checks for an Azure Update PPTX workspace.
.DESCRIPTION
    Validates the workspace contract before build or re-apply. Warnings do not fail the script;
    errors return exit code 1.
#>

param(
    [string]$TargetRoot = ".",
    [string]$DateFolder = "",
    [switch]$CheckPowerPoint
)

$ErrorActionPreference = "Stop"

$targetRootPath = (Resolve-Path $TargetRoot).Path
$checks = New-Object System.Collections.Generic.List[object]

function Add-Check {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Severity,
        [string]$Message
    )

    $checks.Add([pscustomobject]@{
        name = $Name
        passed = $Passed
        severity = $Severity
        message = $Message
    }) | Out-Null
}

function Test-JsonFile {
    param([string]$Path)
    try {
        Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json | Out-Null
        return $true
    } catch {
        return $false
    }
}

Write-Host "=== Azure Update workspace preflight ===" -ForegroundColor Cyan
Write-Host "Target root: $targetRootPath"

$configPath = Join-Path $targetRootPath ".config\config.json"
$config = $null
if (Test-Path -LiteralPath $configPath) {
    Add-Check "config.json exists" $true "Error" "Found config.json"
    if (Test-JsonFile -Path $configPath) {
        $config = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Add-Check "config.json parses" $true "Error" "config.json is valid JSON"
    } else {
        Add-Check "config.json parses" $false "Error" "config.json is not valid JSON"
    }
} else {
    Add-Check "config.json exists" $false "Error" "Run Initialize-AzureUpdateWorkspace.ps1 first"
}

foreach ($relativePath in @(".config\customer-keywords.json", ".config\exclude-keywords.json")) {
    $path = Join-Path $targetRootPath $relativePath
    $exists = Test-Path -LiteralPath $path
    Add-Check "$relativePath exists" $exists "Error" $(if ($exists) { "Found $relativePath" } else { "Missing $relativePath" })
    if ($exists) {
        Add-Check "$relativePath parses" (Test-JsonFile -Path $path) "Error" "JSON parse check"
    }
}

$profilePath = Join-Path $targetRootPath ".config\customer-profile.md"
Add-Check ".config\customer-profile.md exists" (Test-Path -LiteralPath $profilePath) "Error" "Customer profile must be filled per workspace"

if ($config -and $config.template) {
    $templatePath = Join-Path (Join-Path $targetRootPath $config.template.folder) $config.template.fileName
    Add-Check "template exists" (Test-Path -LiteralPath $templatePath) "Error" $templatePath
}

$requiredScripts = @(
    "Build-CustomerPptx.ps1",
    "Enrich-CustomerPptx.ps1",
    "Fetch-AzureUpdates.ps1",
    "Prepare-CustomerPptx.ps1",
    "Run-CustomerPptxPipeline.ps1",
    "Verify-Pptx.ps1",
    "PptxCommon.psm1"
)

foreach ($scriptName in $requiredScripts) {
    $scriptPath = Join-Path $targetRootPath "scripts\$scriptName"
    Add-Check "scripts\$scriptName exists" (Test-Path -LiteralPath $scriptPath) "Error" $scriptPath
}

$markerPath = Join-Path $targetRootPath ".azure-update-workspace.json"
Add-Check "bootstrap marker exists" (Test-Path -LiteralPath $markerPath) "Warning" "Marker is optional for existing workspaces"

if ($DateFolder) {
    $dateFolderPath = if ([System.IO.Path]::IsPathRooted($DateFolder)) { $DateFolder } else { Join-Path $targetRootPath $DateFolder }
    Add-Check "date folder exists" (Test-Path -LiteralPath $dateFolderPath) "Error" $dateFolderPath
    $manifestPath = Join-Path $dateFolderPath "manifest"
    Add-Check "manifest folder exists" (Test-Path -LiteralPath $manifestPath) "Error" $manifestPath
    $logsPath = Join-Path $dateFolderPath "logs"
    Add-Check "logs folder exists" (Test-Path -LiteralPath $logsPath) "Warning" $logsPath

    foreach ($manifestName in @("fetched-updates.json", "classification.json", "region_info_reviewed.json", "notes.json")) {
        $path = Join-Path $manifestPath $manifestName
        $exists = Test-Path -LiteralPath $path
        Add-Check "manifest\$manifestName exists" $exists "Warning" $(if ($exists) { "Found $manifestName" } else { "Missing until that workflow stage completes" })
        if ($exists) {
            Add-Check "manifest\$manifestName parses" (Test-JsonFile -Path $path) "Error" "JSON parse check"
        }
    }
}

if ($CheckPowerPoint) {
    $ppt = $null
    try {
        $ppt = New-Object -ComObject PowerPoint.Application
        Add-Check "PowerPoint COM available" $true "Error" "PowerPoint COM object created"
    } catch {
        Add-Check "PowerPoint COM available" $false "Error" $_.Exception.Message
    } finally {
        if ($ppt) {
            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
        }
    }
}

foreach ($check in $checks) {
    $color = if ($check.passed) { "Green" } elseif ($check.severity -eq "Warning") { "DarkYellow" } else { "Red" }
    $status = if ($check.passed) { "OK" } elseif ($check.severity -eq "Warning") { "WARN" } else { "FAIL" }
    Write-Host "[$status] $($check.name): $($check.message)" -ForegroundColor $color
}

$errors = @($checks | Where-Object { -not $_.passed -and $_.severity -eq "Error" })
$warnings = @($checks | Where-Object { -not $_.passed -and $_.severity -eq "Warning" })
Write-Host "Summary: $($errors.Count) error(s), $($warnings.Count) warning(s)"

if ($errors.Count -gt 0) {
    exit 1
}

exit 0

