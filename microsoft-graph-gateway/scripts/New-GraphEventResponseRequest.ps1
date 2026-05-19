param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('accept', 'decline', 'tentativelyAccept')]
    [string]$ResponseType,

    [Parameter(Mandatory = $true)]
    [string]$EventId,

    [string]$ScopePath = '/me/events',

    [string]$Comment,

    [bool]$SendResponse = $true,

    [switch]$AsJson
)

$ErrorActionPreference = 'Stop'

if (-not $ScopePath.StartsWith('/')) {
    throw 'ScopePath must start with /. Example: /me/events or /users/user@example.com/events'
}

$normalizedScopePath = $ScopePath.TrimEnd('/')
$requestObject = [ordered]@{
    method = 'POST'
    path = "$normalizedScopePath/$EventId/$ResponseType"
    apiVersion = 'v1.0'
    permissionProfile = 'calendar-write'
    intentSummary = switch ($ResponseType) {
        'accept' { 'Accept a meeting request' }
        'decline' { 'Decline a meeting request' }
        'tentativelyAccept' { 'Tentatively accept a meeting request' }
    }
    body = [ordered]@{
        comment = $Comment
        sendResponse = $SendResponse
    }
}

if ($AsJson) {
    $requestObject | ConvertTo-Json -Depth 20
    return
}

[pscustomobject]$requestObject