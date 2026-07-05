param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('POST', 'PATCH', 'PUT')]
    [string]$Method,

    [Parameter(Mandatory = $true)]
    [string]$Path,

    [ValidateSet('v1.0', 'beta')]
    [string]$ApiVersion = 'v1.0',

    [string]$PermissionProfile,

    [string]$IntentSummary,

    [string]$BodyJson
)

$ErrorActionPreference = 'Stop'

function Get-BodyPreview {
    param(
        [object]$ResolvedBody
    )

    if ($null -eq $ResolvedBody) {
        return @()
    }

    if ($ResolvedBody -is [string]) {
        if ([string]::IsNullOrWhiteSpace($ResolvedBody)) {
            return @()
        }

        try {
            $parsedBody = $ResolvedBody | ConvertFrom-Json -Depth 20
        } catch {
            return @('Body JSON could not be parsed')
        }
    } else {
        $parsedBody = $ResolvedBody
    }

    if ($parsedBody -isnot [psobject]) {
        return @('Body content is not an object payload')
    }

    $lines = [System.Collections.Generic.List[string]]::new()
    foreach ($property in $parsedBody.PSObject.Properties | Select-Object -First 10) {
        $valuePreview = $property.Value
        if ($valuePreview -is [System.Array]) {
            $valuePreview = "Array[$($valuePreview.Count)]"
        } elseif ($valuePreview -is [psobject]) {
            $valuePreview = 'Object'
        }

        $lines.Add("- $($property.Name): $valuePreview")
    }

    return @($lines)
}

$summaryLines = [System.Collections.Generic.List[string]]::new()
$summaryLines.Add("Target: $Path")
$summaryLines.Add("Action: $Method")
$summaryLines.Add("API version: $ApiVersion")

if ($PermissionProfile) {
    $summaryLines.Add("Permission profile: $PermissionProfile")
}

if ($IntentSummary) {
    $summaryLines.Add("Intent: $IntentSummary")
}

if ($ApiVersion -eq 'beta') {
    $summaryLines.Add('Risk: beta API requested')
}

$summaryLines.Add('Body preview:')
foreach ($line in Get-BodyPreview -ResolvedBody $BodyJson) {
    $summaryLines.Add($line)
}

$summaryLines -join [Environment]::NewLine