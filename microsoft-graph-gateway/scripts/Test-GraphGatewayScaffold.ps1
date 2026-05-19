param()

$ErrorActionPreference = 'Stop'

$skillRoot = Split-Path -Parent $PSScriptRoot
$invokeScript = Join-Path $PSScriptRoot 'Invoke-GraphGateway.ps1'
$confirmScript = Join-Path $PSScriptRoot 'New-GraphWriteConfirmation.ps1'
$eventResponseScript = Join-Path $PSScriptRoot 'New-GraphEventResponseRequest.ps1'
$appConfigScript = Join-Path $PSScriptRoot 'New-GraphGatewayAppConfig.ps1'
$readRequest = Join-Path $skillRoot 'assets\read-mail.request.json'
$writeRequest = Join-Path $skillRoot 'assets\send-mail.request.json'

$dryRunResult = & $invokeScript -RequestFile $readRequest -DryRun
if (-not $dryRunResult) {
    throw 'Dry-run result was empty.'
}

if ($dryRunResult.preview.target -ne '/me/messages') {
    throw 'Dry-run preview target did not match the expected path.'
}

if ($dryRunResult.preview.permissionProfile -ne 'mail-read-basic') {
    throw 'Dry-run preview permission profile did not match the expected value.'
}

$writeRequestObject = Get-Content -LiteralPath $writeRequest -Raw -Encoding UTF8 | ConvertFrom-Json -Depth 20
$confirmationSummary = & $confirmScript `
    -Method $writeRequestObject.method `
    -Path $writeRequestObject.path `
    -ApiVersion $writeRequestObject.apiVersion `
    -PermissionProfile $writeRequestObject.permissionProfile `
    -IntentSummary $writeRequestObject.intentSummary `
    -BodyJson ($writeRequestObject.body | ConvertTo-Json -Depth 20 -Compress)

if ($confirmationSummary -notmatch 'Target: /me/sendMail') {
    throw 'Confirmation summary did not include the expected target.'
}

if ($confirmationSummary -notmatch 'Permission profile: mail-write') {
    throw 'Confirmation summary did not include the expected permission profile.'
}

$acceptRequest = & $eventResponseScript -ResponseType accept -EventId 'sample-event-id'
if ($acceptRequest.path -ne '/me/events/sample-event-id/accept') {
    throw 'Accept event request path did not match the expected value.'
}

if ($acceptRequest.permissionProfile -ne 'calendar-write') {
    throw 'Accept event request permission profile did not match the expected value.'
}

$appConfig = & $appConfigScript -ClientId '11111111-1111-1111-1111-111111111111' -TenantId 'contoso.onmicrosoft.com' -Format json | ConvertFrom-Json
if ($appConfig.MSGRAPH_CLIENT_ID -ne '11111111-1111-1111-1111-111111111111') {
    throw 'Custom app config did not preserve the expected client ID.'
}

if ($appConfig.MSGRAPH_TENANT_ID -ne 'contoso.onmicrosoft.com') {
    throw 'Custom app config did not preserve the expected tenant ID.'
}

[pscustomobject]@{
    dryRunVerified = $true
    confirmationVerified = $true
    eventResponseVerified = $true
    appConfigVerified = $true
    readRequest = $readRequest
    writeRequest = $writeRequest
}