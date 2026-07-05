param(
    [Parameter(Mandatory = $true)]
    [string]$ClientId,

    [Parameter(Mandatory = $true)]
    [string]$TenantId,

    [ValidateSet('powershell', 'bash', 'json')]
    [string]$Format = 'powershell',

    [string]$RunnerPath
)

$ErrorActionPreference = 'Stop'

$resolvedRunnerPath = if ($RunnerPath) {
    $RunnerPath
} elseif ($env:GRAPH_GATEWAY_RUNNER) {
    $env:GRAPH_GATEWAY_RUNNER
} elseif ($env:MSGRAPH_RUNNER) {
    $env:MSGRAPH_RUNNER
} else {
    '$GRAPH_GATEWAY_RUNNER'
}

switch ($Format) {
    'powershell' {
        @(
            "$env:MSGRAPH_CLIENT_ID = '$ClientId'"
            "$env:MSGRAPH_TENANT_ID = '$TenantId'"
            "$env:GRAPH_GATEWAY_RUNNER = '$resolvedRunnerPath'"
        ) -join [Environment]::NewLine
    }
    'bash' {
        @(
            "export MSGRAPH_CLIENT_ID='$ClientId'"
            "export MSGRAPH_TENANT_ID='$TenantId'"
            "export GRAPH_GATEWAY_RUNNER='$resolvedRunnerPath'"
        ) -join [Environment]::NewLine
    }
    'json' {
        [pscustomobject]@{
            MSGRAPH_CLIENT_ID = $ClientId
            MSGRAPH_TENANT_ID = $TenantId
            GRAPH_GATEWAY_RUNNER = $resolvedRunnerPath
        } | ConvertTo-Json -Depth 5
    }
}