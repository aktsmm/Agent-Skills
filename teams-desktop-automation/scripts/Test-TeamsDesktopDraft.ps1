[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $PSScriptRoot 'Set-TeamsDesktopDraft.ps1'
$tokens = $null
$parseErrors = $null
$null = [System.Management.Automation.Language.Parser]::ParseFile(
    $scriptPath,
    [ref]$tokens,
    [ref]$parseErrors
)

if ($parseErrors.Count -ne 0) {
    throw "PowerShell parser reported $($parseErrors.Count) error(s)."
}

$source = Get-Content -LiteralPath $scriptPath -Raw -Encoding utf8
$requiredFragments = @(
    "[ValidateSet('Open', 'Inspect', 'Draft')]",
    'Refusing to overwrite it.',
    '$valuePattern.SetValue($Message)',
    '$currentDraft.TrimEnd("`r", "`n") -in $composerPlaceholders',
    "'ready-for-user-send'",
    'SendActionPerformed = $false'
)

foreach ($fragment in $requiredFragments) {
    if (-not $source.Contains($fragment)) {
        throw "Required safety contract is missing: $fragment"
    }
}

$forbiddenPatterns = @(
    'SendKeys',
    'SendWait',
    'InvokePattern',
    'SetCursorPos',
    'mouse_event'
)

foreach ($pattern in $forbiddenPatterns) {
    if ($source -match [regex]::Escape($pattern)) {
        throw "Forbidden send mechanism found: $pattern"
    }
}

$invalidEmailRejected = $false
try {
    & $scriptPath -Mode Open `
        -RecipientDisplayName 'Example User' `
        -RecipientEmail 'not-an-email' `
        -ExpectedAccount 'operator@example.com'
}
catch {
    $invalidEmailRejected = $_.Exception.Message -like 'Invalid email address:*'
}

if (-not $invalidEmailRejected) {
    throw 'Invalid recipient email was not rejected before opening Teams.'
}

[pscustomobject]@{
    ParserErrors         = 0
    RequiredGuards       = $requiredFragments.Count
    ForbiddenMechanisms = 0
    InvalidEmailRejected = $true
    Result               = 'PASS'
} | ConvertTo-Json