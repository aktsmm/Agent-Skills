param(
    [string]$InstallRoot = '.tools\msgraph-runner',
    [switch]$AddToProcessEnv,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$resolvedInstallRoot = if ([System.IO.Path]::IsPathRooted($InstallRoot)) {
    $InstallRoot
} else {
    Join-Path (Get-Location) $InstallRoot
}

$zipPath = Join-Path $resolvedInstallRoot 'msgraph.zip'
$extractRoot = Join-Path $resolvedInstallRoot 'msgraph'
$releaseUrl = 'https://github.com/merill/msgraph/releases/latest/download/msgraph.zip'

if ((Test-Path -LiteralPath $extractRoot) -and -not $Force) {
    throw "Install root already contains an extracted runner. Use -Force to overwrite: $extractRoot"
}

New-Item -ItemType Directory -Force -Path $resolvedInstallRoot | Out-Null

Invoke-WebRequest -Uri $releaseUrl -OutFile $zipPath

if (Test-Path -LiteralPath $extractRoot) {
    Remove-Item -LiteralPath $extractRoot -Recurse -Force
}

Expand-Archive -LiteralPath $zipPath -DestinationPath $extractRoot -Force

$packageRoot = Get-ChildItem -LiteralPath $extractRoot -Recurse -Directory |
    Where-Object { $_.Name -eq 'msgraph' } |
    Select-Object -First 1

if (-not $packageRoot) {
    throw 'The extracted package root was not found.'
}

$runnerCandidate = if ($IsWindows) {
    Get-ChildItem -LiteralPath $packageRoot.FullName -Recurse -File |
        Where-Object { $_.Name -eq 'run.ps1' } |
        Select-Object -First 1
} else {
    Get-ChildItem -LiteralPath $packageRoot.FullName -Recurse -File |
        Where-Object { $_.Name -eq 'run.sh' } |
        Select-Object -First 1
}

if (-not $runnerCandidate) {
    throw 'The platform-specific msgraph runner wrapper was not found after extraction.'
}

if ($AddToProcessEnv) {
    $env:GRAPH_GATEWAY_RUNNER = $runnerCandidate.FullName
}

[pscustomobject]@{
    installRoot = $resolvedInstallRoot
    extractedRoot = $extractRoot
    runnerPath = $runnerCandidate.FullName
    graphGatewayRunnerEnv = if ($AddToProcessEnv) { $env:GRAPH_GATEWAY_RUNNER } else { $null }
}