<#
.SYNOPSIS
    Bootstrap an Azure Update PPTX workspace from the azure-update-customer-pptx skill.
.DESCRIPTION
    Copies starter config, template, and runtime scripts into a target workspace.
    Existing customer config is not overwritten by default; conflicts are written as .new files.
#>

param(
    [string]$TargetRoot = ".",
    [switch]$UpdateScripts,
    [switch]$ForceConfig,
    [switch]$CopyMcpSample
)

$ErrorActionPreference = "Stop"

$skillRoot = Split-Path $PSScriptRoot -Parent
$targetRootPath = (Resolve-Path $TargetRoot).Path
$assetsRoot = Join-Path $skillRoot "assets"
$sourceScripts = Join-Path $skillRoot "scripts"

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Skip {
    param([string]$Message)
    Write-Host "[SKIP] $Message" -ForegroundColor DarkYellow
}

function Copy-StarterFile {
    param(
        [string]$Source,
        [string]$Destination,
        [switch]$AllowOverwrite
    )

    $destinationFolder = Split-Path $Destination -Parent
    New-Item -ItemType Directory -Force -Path $destinationFolder | Out-Null

    if (-not (Test-Path -LiteralPath $Destination)) {
        Copy-Item -LiteralPath $Source -Destination $Destination
        Write-Info "Created $Destination"
        return
    }

    if ($AllowOverwrite) {
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
        Write-Info "Updated $Destination"
        return
    }

    $newPath = "$Destination.new"
    Copy-Item -LiteralPath $Source -Destination $newPath -Force
    Write-Skip "Kept existing $Destination; wrote starter to $newPath"
}

Write-Info "Target root: $targetRootPath"

$workspaceFolders = @(
    (Join-Path $targetRootPath ".config"),
    (Join-Path $targetRootPath "scripts"),
    (Join-Path $targetRootPath "template")
)
New-Item -ItemType Directory -Force -Path $workspaceFolders | Out-Null

Copy-StarterFile -Source (Join-Path $assetsRoot "config.template.json") -Destination (Join-Path $targetRootPath ".config\config.json") -AllowOverwrite:$ForceConfig
Copy-StarterFile -Source (Join-Path $assetsRoot "customer-keywords.template.json") -Destination (Join-Path $targetRootPath ".config\customer-keywords.json") -AllowOverwrite:$ForceConfig
Copy-StarterFile -Source (Join-Path $assetsRoot "exclude-keywords.template.json") -Destination (Join-Path $targetRootPath ".config\exclude-keywords.json") -AllowOverwrite:$ForceConfig
Copy-StarterFile -Source (Join-Path $assetsRoot "customer-profile.template.md") -Destination (Join-Path $targetRootPath ".config\customer-profile.md") -AllowOverwrite:$ForceConfig

$templateSource = Join-Path $assetsRoot "template\azure-update-template.pptx"
if (Test-Path -LiteralPath $templateSource) {
    Copy-StarterFile -Source $templateSource -Destination (Join-Path $targetRootPath "template\azure-update-template.pptx") -AllowOverwrite:$ForceConfig
} else {
    Write-Skip "No neutral template found at $templateSource"
}

if ($UpdateScripts) {
    Get-ChildItem -LiteralPath $sourceScripts -File | Where-Object { $_.Extension -in @(".ps1", ".psm1") } | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $targetRootPath "scripts\$($_.Name)") -Force
        Write-Info "Updated scripts\$($_.Name)"
    }
} else {
    Write-Skip "Runtime scripts were not updated. Re-run with -UpdateScripts to refresh root scripts."
}

if ($CopyMcpSample) {
    $mcpSource = Join-Path $assetsRoot "mcp.sample.json"
    $mcpTarget = Join-Path $targetRootPath ".vscode\mcp.json"
    Copy-StarterFile -Source $mcpSource -Destination $mcpTarget
}

$metaPath = Join-Path $skillRoot ".skill-meta.json"
$meta = if (Test-Path -LiteralPath $metaPath) { Get-Content -LiteralPath $metaPath -Raw -Encoding UTF8 | ConvertFrom-Json } else { $null }
$version = if ($meta -and $meta.version) { $meta.version } else { "unknown" }
$marker = [ordered]@{
    skill = "azure-update-customer-pptx"
    version = $version
    generatedAt = (Get-Date).ToString("s")
    scriptsUpdated = [bool]$UpdateScripts
}
$marker | ConvertTo-Json -Depth 4 | Out-File (Join-Path $targetRootPath ".azure-update-workspace.json") -Encoding UTF8

Write-Info "Bootstrap marker written to .azure-update-workspace.json"
Write-Info "Next: fill .config/customer-profile.md and .config/customer-keywords.json, then create a date folder."

