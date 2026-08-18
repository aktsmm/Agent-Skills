<#
.SYNOPSIS
    Run Verify-Pptx.ps1 in a fresh process and emit a run-scoped JSON result.
#>
param(
    [Parameter(Mandatory = $true)][string]$PptxPath,
    [string]$RunId = ([guid]::NewGuid().ToString()),
    [string]$ResultPath = "",
    [string]$LogPath = ""
)

$ErrorActionPreference = 'Stop'
Import-Module "$PSScriptRoot\PptxCommon.psm1" -Force
$resolvedPptx = [System.IO.Path]::GetFullPath($PptxPath)
$dateFolder = Split-Path -Parent $resolvedPptx
if ([string]::IsNullOrWhiteSpace($ResultPath)) { $ResultPath = Join-Path $dateFolder "logs\verify-$RunId.json" }
if ([string]::IsNullOrWhiteSpace($LogPath)) { $LogPath = Join-Path $dateFolder "logs\verify-$RunId.log" }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $ResultPath), (Split-Path -Parent $LogPath) | Out-Null

$state = 'started'
$exitCode = -1
$errorSummary = ''
$startedAt = (Get-Date).ToString('o')
$outputHash = ''
$verifier = Join-Path $PSScriptRoot 'Verify-Pptx.ps1'

try {
    if (-not (Test-Path -LiteralPath $resolvedPptx)) { throw "PPTX was not found: $resolvedPptx" }
    if (-not (Test-Path -LiteralPath $verifier)) { throw "Verifier was not found: $verifier" }
    $activeApplication = Get-ActivePptxApplication
    if ($activeApplication) {
        try { Close-OpenPptxPresentation -Application $activeApplication -PptxPath $resolvedPptx | Out-Null }
        finally { [Runtime.InteropServices.Marshal]::ReleaseComObject($activeApplication) | Out-Null }
    }
    $outputHash = (Get-FileHash -LiteralPath $resolvedPptx -Algorithm SHA256).Hash
    $powershell = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
    if (-not $powershell) { throw 'PowerShell 7 (pwsh) is required by the canonical verifier.' }
    & $powershell -NoLogo -NoProfile -File $verifier -PptxPath $resolvedPptx *> $LogPath
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        $state = 'verify-failed'
        $errorSummary = "Verify-Pptx.ps1 exited with code $exitCode"
    } else {
        $state = 'passed'
    }
} catch {
    $state = 'infra-failed'
    $errorSummary = $_.Exception.Message
} finally {
    $currentHash = if (Test-Path -LiteralPath $resolvedPptx) { (Get-FileHash -LiteralPath $resolvedPptx -Algorithm SHA256).Hash } else { '' }
    $result = [ordered]@{
        schemaVersion = 1
        runId = $RunId
        state = $state
        passed = ($state -eq 'passed')
        pptxPath = $resolvedPptx
        outputHash = $outputHash
        outputHashAfterVerify = $currentHash
        hashUnchanged = ($outputHash -and $outputHash -eq $currentHash)
        verifyExitCode = $exitCode
        verifier = $verifier
        logPath = [System.IO.Path]::GetFullPath($LogPath)
        startedAt = $startedAt
        completedAt = (Get-Date).ToString('o')
        error = $errorSummary
    }
    $temporary = "$ResultPath.$RunId.tmp"
    $result | ConvertTo-Json -Depth 5 | Out-File $temporary -Encoding UTF8
    Move-Item -LiteralPath $temporary -Destination $ResultPath -Force
    $result | ConvertTo-Json -Depth 5
}

if ($state -ne 'passed') { exit 1 }
exit 0
