<#
.SYNOPSIS
    Compare already-built COM and Python decks with fresh verifier runs and semantic diff.
#>
param(
    [Parameter(Mandatory = $true)][string]$ComPptxPath,
    [Parameter(Mandatory = $true)][string]$PythonPptxPath,
    [Parameter(Mandatory = $true)][string]$WorkspaceRoot,
    [string]$ResultDirectory = ""
)

$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path -LiteralPath $WorkspaceRoot).Path
$python = if ($env:AZURE_UPDATE_PYTHON) { $env:AZURE_UPDATE_PYTHON } else { Join-Path $workspace '.venv\Scripts\python.exe' }
if (-not (Test-Path -LiteralPath $python)) { throw "Python was not found: $python" }
$com = (Resolve-Path -LiteralPath $ComPptxPath).Path
$pythonDeck = (Resolve-Path -LiteralPath $PythonPptxPath).Path
if ([string]::IsNullOrWhiteSpace($ResultDirectory)) { $ResultDirectory = Join-Path ([IO.Path]::GetTempPath()) ("azure-update-parity-" + [guid]::NewGuid().ToString()) }
New-Item -ItemType Directory -Force -Path $ResultDirectory | Out-Null

function Find-ManifestSource {
    param([string]$StartPath)
    $current = Get-Item -LiteralPath (Split-Path -Parent $StartPath)
    while ($current) {
        $candidate = Join-Path $current.FullName 'manifest'
        if (Test-Path -LiteralPath (Join-Path $candidate 'classification.json')) { return $candidate }
        $current = $current.Parent
    }
    throw "Could not find manifest ancestor for $StartPath"
}

$manifestSource = Find-ManifestSource -StartPath $com
$parityRootName = '.parity-' + [guid]::NewGuid().ToString('N')
$comDateFolder = Join-Path $workspace ($parityRootName + '-com')
$pythonDateFolder = Join-Path $workspace ($parityRootName + '-python')
foreach ($folder in @($comDateFolder, $pythonDateFolder)) {
    New-Item -ItemType Directory -Force -Path (Join-Path $folder 'manifest') | Out-Null
    Get-ChildItem -LiteralPath $manifestSource | Copy-Item -Destination (Join-Path $folder 'manifest') -Recurse -Force
}
$comVerifyCopy = Join-Path $comDateFolder ([IO.Path]::GetFileName($com))
$pythonVerifyCopy = Join-Path $pythonDateFolder ([IO.Path]::GetFileName($pythonDeck))
Copy-Item -LiteralPath $com -Destination $comVerifyCopy -Force
Copy-Item -LiteralPath $pythonDeck -Destination $pythonVerifyCopy -Force

$comRun = [guid]::NewGuid().ToString()
$pythonRun = [guid]::NewGuid().ToString()
try {
    & "$PSScriptRoot\Invoke-PptxVerify.ps1" -PptxPath $comVerifyCopy -RunId $comRun -ResultPath (Join-Path $ResultDirectory 'verify-com.json') -LogPath (Join-Path $ResultDirectory 'verify-com.log') | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'COM deck verifier failed.' }
    & "$PSScriptRoot\Invoke-PptxVerify.ps1" -PptxPath $pythonVerifyCopy -RunId $pythonRun -ResultPath (Join-Path $ResultDirectory 'verify-python.json') -LogPath (Join-Path $ResultDirectory 'verify-python.log') | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Python deck verifier failed.' }

    $comparer = Join-Path $PSScriptRoot 'python\compare_pptx.py'
    & $python $comparer --com $com --python $pythonDeck --result (Join-Path $ResultDirectory 'parity.json')
    if ($LASTEXITCODE -ne 0) { throw "Engine parity failed. See $ResultDirectory" }
    Write-Host "Parity PASS: $ResultDirectory"
}
finally {
    Remove-Item -LiteralPath $comDateFolder, $pythonDateFolder -Recurse -Force -ErrorAction SilentlyContinue
}
