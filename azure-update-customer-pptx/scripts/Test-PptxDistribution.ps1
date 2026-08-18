<#
.SYNOPSIS
    Required pre-distribution gate for Azure Update PPTX/PDF artifacts.
#>
param(
    [Parameter(Mandatory = $true)][string]$PptxPath,
    [Parameter(Mandatory = $true)][string]$PdfPath,
    [string]$RetainedOpenXmlPath = "",
    [string]$ResultPath = "",
    [ValidateSet("com", "python")][string]$Engine = "com",
    [string]$WorkspaceRoot = ""
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Test-OpenXmlPackage {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    try {
        $archive = [IO.Compression.ZipFile]::OpenRead([IO.Path]::GetFullPath($Path))
        try { return $null -ne ($archive.Entries | Where-Object FullName -eq '[Content_Types].xml' | Select-Object -First 1) }
        finally { $archive.Dispose() }
    } catch { return $false }
}

function Get-Sha256OrEmpty {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return '' }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
}

$pptx = [IO.Path]::GetFullPath($PptxPath)
$pdf = [IO.Path]::GetFullPath($PdfPath)
$retained = if ([string]::IsNullOrWhiteSpace($RetainedOpenXmlPath)) { '' } else { [IO.Path]::GetFullPath($RetainedOpenXmlPath) }
if ([string]::IsNullOrWhiteSpace($ResultPath)) { $ResultPath = Join-Path (Split-Path -Parent $pptx) 'logs\distribution-gate.json' }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $ResultPath) | Out-Null

$checks = @()
$pptxExists = Test-Path -LiteralPath $pptx
$pdfExists = Test-Path -LiteralPath $pdf
$canonicalOpenXml = Test-OpenXmlPackage -Path $pptx
$retainedOpenXml = $retained -and (Test-OpenXmlPackage -Path $retained)
$checks += [ordered]@{ name='pptx-exists'; pass=$pptxExists; actual=$pptxExists; expected=$true }
$checks += [ordered]@{ name='pdf-exists'; pass=$pdfExists; actual=$pdfExists; expected=$true }
$checks += [ordered]@{ name='verified-openxml-source'; pass=($canonicalOpenXml -or $retainedOpenXml); actual=$(if($canonicalOpenXml){$pptx}else{$retained}); expected='valid OpenXML' }

$pdfPages = 0
$pdfEncrypted = $true
if ($pdfExists) {
    $pdfBytes = [IO.File]::ReadAllBytes($pdf)
    $pdfAscii = [Text.Encoding]::ASCII.GetString($pdfBytes)
    $counts = [regex]::Matches($pdfAscii, '/Count\s+(\d+)') | ForEach-Object { [int]$_.Groups[1].Value }
    $pdfPages = if ($counts) { ($counts | Measure-Object -Maximum).Maximum } else { 0 }
    $pdfEncrypted = $pdfAscii.Contains('/Encrypt')
}
$checks += [ordered]@{ name='pdf-pages-nonzero'; pass=($pdfPages -gt 0); actual=$pdfPages; expected='> 0' }
$checks += [ordered]@{ name='pdf-encrypted'; pass=(-not $pdfEncrypted); actual=$pdfEncrypted; expected=$false }
$pdfFresh = $pdfExists -and $pptxExists -and (Get-Item -LiteralPath $pdf).LastWriteTimeUtc -ge (Get-Item -LiteralPath $pptx).LastWriteTimeUtc
$checks += [ordered]@{ name='pdf-not-older-than-pptx'; pass=$pdfFresh; actual=$(if($pdfExists){(Get-Item -LiteralPath $pdf).LastWriteTimeUtc.ToString('o')}else{''}); expected=$(if($pptxExists){(Get-Item -LiteralPath $pptx).LastWriteTimeUtc.ToString('o')}else{''}) }

if ($Engine -eq 'python') {
    if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) { throw '-WorkspaceRoot is required for the Python PDF text gate.' }
    $workspace = (Resolve-Path -LiteralPath $WorkspaceRoot).Path
    $python = if ($env:AZURE_UPDATE_PYTHON) { $env:AZURE_UPDATE_PYTHON } else { Join-Path $workspace '.venv\Scripts\python.exe' }
    $textVerifier = Join-Path $PSScriptRoot 'python\verify_pdf_text.py'
    $textResult = Join-Path (Split-Path -Parent $ResultPath) 'pdf-text-result.json'
    & $python $textVerifier --pdf $pdf --pptx $pptx --workspace-root $workspace --result $textResult | Out-Null
    $textExitCode = $LASTEXITCODE
    $checks += [ordered]@{ name='pdf-text-customer-safe'; pass=($textExitCode -eq 0); actual=$textExitCode; expected=0 }
}

$passed = @($checks | Where-Object { -not $_.pass }).Count -eq 0
$result = [ordered]@{
    schemaVersion = 1
    evaluatedAt = (Get-Date).ToString('o')
    state = if($passed){'passed'}else{'failed'}
    passed = $passed
    distribution = [ordered]@{
        customer = $pdf
        internal = if($canonicalOpenXml){$pptx}else{$retained}
        quarantinedCanonical = if($canonicalOpenXml){''}else{$pptx}
    }
    hashes = [ordered]@{
        canonicalPptx = Get-Sha256OrEmpty -Path $pptx
        retainedOpenXml = Get-Sha256OrEmpty -Path $retained
        pdf = Get-Sha256OrEmpty -Path $pdf
    }
    checks = $checks
}
$temporary = "$ResultPath.tmp"
$result | ConvertTo-Json -Depth 8 | Out-File $temporary -Encoding UTF8
Move-Item -LiteralPath $temporary -Destination $ResultPath -Force
$result | ConvertTo-Json -Depth 8
if (-not $passed) { exit 1 }
exit 0
