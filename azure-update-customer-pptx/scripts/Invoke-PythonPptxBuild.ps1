<#
.SYNOPSIS
    Invoke the opt-in python-pptx Azure Update build engine.
#>
param(
    [Parameter(Mandatory = $true)][string]$DateFolder,
    [string]$WorkspaceRoot = "",
    [string]$OutputPath = "",
    [string]$RunId = ([guid]::NewGuid().ToString())
)

$ErrorActionPreference = 'Stop'

$resolvedDateFolder = (Resolve-Path -LiteralPath $DateFolder).Path
if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
    $WorkspaceRoot = Split-Path $resolvedDateFolder -Parent
}
$workspace = (Resolve-Path -LiteralPath $WorkspaceRoot).Path
$python = if ($env:AZURE_UPDATE_PYTHON) { $env:AZURE_UPDATE_PYTHON } else { Join-Path $workspace '.venv\Scripts\python.exe' }
$builder = Join-Path $PSScriptRoot 'python\build_customer_pptx.py'
$lock = Join-Path $PSScriptRoot 'python\requirements.lock'

if (-not (Test-Path -LiteralPath $python)) {
    throw "Workspace Python was not found: $python. Create it explicitly with uv venv and uv pip sync; packages are never installed automatically."
}
if (-not (Test-Path -LiteralPath $builder)) { throw "Python builder was not found: $builder" }
if (-not (Test-Path -LiteralPath $lock)) { throw "Python dependency lock was not found: $lock" }

$requiredModules = @('pptx', 'PIL', 'lxml')
$moduleCheck = @"
import importlib.util, json
required = $($requiredModules | ConvertTo-Json -Compress)
missing = [name for name in required if importlib.util.find_spec(name) is None]
print(json.dumps({'missing': missing}))
raise SystemExit(1 if missing else 0)
"@
$checkResult = $moduleCheck | & $python -
if ($LASTEXITCODE -ne 0) {
    throw "Python build dependencies are missing. Run: uv pip sync --python `"$python`" `"$lock`". Details: $checkResult"
}

$arguments = @(
    $builder,
    '--workspace-root', $workspace,
    '--date-folder', $resolvedDateFolder,
    '--run-id', $RunId,
    '--result', (Join-Path $resolvedDateFolder "logs\python-build-$RunId.json")
)
if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
    $arguments += @('--output', [System.IO.Path]::GetFullPath($OutputPath))
}

& $python @arguments
if ($LASTEXITCODE -ne 0) {
    throw "Python PPTX build failed with exit code $LASTEXITCODE"
}
