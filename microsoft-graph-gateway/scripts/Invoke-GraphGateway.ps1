param(
    [ValidateSet('GET', 'POST', 'PATCH', 'PUT', 'DELETE')]
    [string]$Method,

    [string]$Path,

    [ValidateSet('v1.0', 'beta')]
    [string]$ApiVersion = 'v1.0',

    [string]$Select,

    [string]$Filter,

    [int]$Top,

    [string]$Expand,

    [string]$OrderBy,

    [string[]]$Headers,

    [string]$BodyJson,

    [string]$PermissionProfile,

    [string]$IntentSummary,

    [switch]$AllowWrites,

    [switch]$DryRun,

    [string]$RunnerPath,

    [string]$RequestFile
)

$ErrorActionPreference = 'Stop'

function Get-RequestValue {
    param(
        [object]$ExplicitValue,
        [object]$FileValue,
        [switch]$AllowEmptyString
    )

    if ($null -ne $ExplicitValue) {
        if ($AllowEmptyString -or $ExplicitValue -ne '') {
            return $ExplicitValue
        }
    }

    return $FileValue
}

function Resolve-RunnerCommand {
    param(
        [string]$ExplicitRunnerPath
    )

    if ($ExplicitRunnerPath) {
        return $ExplicitRunnerPath
    }

    if ($env:GRAPH_GATEWAY_RUNNER) {
        return $env:GRAPH_GATEWAY_RUNNER
    }

    if ($env:MSGRAPH_RUNNER) {
        return $env:MSGRAPH_RUNNER
    }

    $runner = Get-Command 'msgraph' -ErrorAction SilentlyContinue
    if ($runner) {
        return $runner.Source
    }

    throw 'Microsoft Graph runner was not found. Set -RunnerPath, GRAPH_GATEWAY_RUNNER, or MSGRAPH_RUNNER, or install a runner that exposes the msgraph command.'
}

function Assert-Request {
    param(
        [string]$ResolvedMethod,
        [string]$ResolvedPath,
        [bool]$IsWrite,
        [bool]$AllowWriteExecution
    )

    if ([string]::IsNullOrWhiteSpace($ResolvedMethod)) {
        throw 'Method is required.'
    }

    if ([string]::IsNullOrWhiteSpace($ResolvedPath)) {
        throw 'Path is required.'
    }

    if (-not $ResolvedPath.StartsWith('/')) {
        throw 'Path must start with /. Example: /me/messages'
    }

    if ($ResolvedMethod -eq 'DELETE') {
        throw 'DELETE is blocked by the current Microsoft Graph gateway policy.'
    }

    if ($IsWrite -and -not $AllowWriteExecution) {
        throw 'Write execution requires -AllowWrites.'
    }
}

function Get-ImportantBodyFields {
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
            return @('Body JSON could not be parsed for summary generation')
        }
    } else {
        $parsedBody = $ResolvedBody
    }

    if ($parsedBody -isnot [psobject]) {
        return @()
    }

    return @($parsedBody.PSObject.Properties.Name | Select-Object -First 8)
}

function New-ConfirmationPreview {
    param(
        [string]$ResolvedMethod,
        [string]$ResolvedPath,
        [string]$ResolvedApiVersion,
        [string]$ResolvedPermissionProfile,
        [string]$ResolvedIntentSummary,
        [object]$ResolvedBody
    )

    $isWrite = $ResolvedMethod -ne 'GET'
    $importantFields = Get-ImportantBodyFields -ResolvedBody $ResolvedBody

    [pscustomobject]@{
        isWrite            = $isWrite
        target             = $ResolvedPath
        method             = $ResolvedMethod
        apiVersion         = $ResolvedApiVersion
        permissionProfile  = $ResolvedPermissionProfile
        intentSummary      = $ResolvedIntentSummary
        importantBodyFields = $importantFields
    }
}

$requestFromFile = $null
if ($RequestFile) {
    if (-not (Test-Path -LiteralPath $RequestFile)) {
        throw "Request file was not found: $RequestFile"
    }

    $requestFromFile = Get-Content -LiteralPath $RequestFile -Raw -Encoding UTF8 | ConvertFrom-Json -Depth 20
}

$resolvedMethod = Get-RequestValue -ExplicitValue $Method -FileValue $requestFromFile.method
$resolvedPath = Get-RequestValue -ExplicitValue $Path -FileValue $requestFromFile.path
$resolvedApiVersion = Get-RequestValue -ExplicitValue $ApiVersion -FileValue $requestFromFile.apiVersion
$resolvedSelect = Get-RequestValue -ExplicitValue $Select -FileValue $requestFromFile.query.select -AllowEmptyString
$resolvedFilter = Get-RequestValue -ExplicitValue $Filter -FileValue $requestFromFile.query.filter -AllowEmptyString
$resolvedTop = Get-RequestValue -ExplicitValue $Top -FileValue $requestFromFile.query.top
$resolvedExpand = Get-RequestValue -ExplicitValue $Expand -FileValue $requestFromFile.query.expand -AllowEmptyString
$resolvedOrderBy = Get-RequestValue -ExplicitValue $OrderBy -FileValue $requestFromFile.query.orderBy -AllowEmptyString
$resolvedHeaders = Get-RequestValue -ExplicitValue $Headers -FileValue $requestFromFile.headers
$resolvedBody = Get-RequestValue -ExplicitValue $BodyJson -FileValue $requestFromFile.body
$resolvedPermissionProfile = Get-RequestValue -ExplicitValue $PermissionProfile -FileValue $requestFromFile.permissionProfile
$resolvedIntentSummary = Get-RequestValue -ExplicitValue $IntentSummary -FileValue $requestFromFile.intentSummary

$isWrite = $resolvedMethod -ne 'GET'
Assert-Request -ResolvedMethod $resolvedMethod -ResolvedPath $resolvedPath -IsWrite $isWrite -AllowWriteExecution $AllowWrites.IsPresent

$argumentList = [System.Collections.Generic.List[string]]::new()
$argumentList.Add('graph-call')
$argumentList.Add($resolvedMethod)
$argumentList.Add($resolvedPath)

if ($resolvedApiVersion) {
    $argumentList.Add('--api-version')
    $argumentList.Add($resolvedApiVersion)
}

if ($resolvedSelect) {
    $argumentList.Add('--select')
    $argumentList.Add($resolvedSelect)
}

if ($resolvedFilter) {
    $argumentList.Add('--filter')
    $argumentList.Add($resolvedFilter)
}

if ($resolvedTop) {
    $argumentList.Add('--top')
    $argumentList.Add([string]$resolvedTop)
}

if ($resolvedExpand) {
    $argumentList.Add('--expand')
    $argumentList.Add($resolvedExpand)
}

if ($resolvedOrderBy) {
    $argumentList.Add('--orderby')
    $argumentList.Add($resolvedOrderBy)
}

if ($resolvedHeaders) {
    foreach ($header in @($resolvedHeaders)) {
        $argumentList.Add('--headers')
        $argumentList.Add([string]$header)
    }
}

if ($null -ne $resolvedBody -and ($resolvedBody -ne '')) {
    $bodyArgument = if ($resolvedBody -is [string]) { $resolvedBody } else { $resolvedBody | ConvertTo-Json -Depth 20 -Compress }
    $argumentList.Add('--body')
    $argumentList.Add($bodyArgument)
}

if ($isWrite) {
    $argumentList.Add('--allow-writes')
}

$preview = New-ConfirmationPreview `
    -ResolvedMethod $resolvedMethod `
    -ResolvedPath $resolvedPath `
    -ResolvedApiVersion $resolvedApiVersion `
    -ResolvedPermissionProfile $resolvedPermissionProfile `
    -ResolvedIntentSummary $resolvedIntentSummary `
    -ResolvedBody $resolvedBody

if ($DryRun) {
    [pscustomobject]@{
        runnerCommand = if ($RunnerPath) { $RunnerPath } elseif ($env:GRAPH_GATEWAY_RUNNER) { $env:GRAPH_GATEWAY_RUNNER } elseif ($env:MSGRAPH_RUNNER) { $env:MSGRAPH_RUNNER } else { $null }
        arguments = @($argumentList)
        preview = $preview
    }
    return
}

$runnerCommand = Resolve-RunnerCommand -ExplicitRunnerPath $RunnerPath

& $runnerCommand @argumentList