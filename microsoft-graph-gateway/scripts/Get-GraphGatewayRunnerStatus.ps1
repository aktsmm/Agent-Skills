param(
    [string]$RunnerPath
)

$ErrorActionPreference = 'Stop'

function Resolve-RunnerPath {
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

    return $null
}

$resolvedRunner = Resolve-RunnerPath -ExplicitRunnerPath $RunnerPath
$authStatus = $null
$authError = $null

if ($resolvedRunner) {
    try {
        $authStatus = & $resolvedRunner auth status 2>&1
    } catch {
        $authError = $_.Exception.Message
    }
}

[pscustomobject]@{
    runnerPath = $resolvedRunner
    runnerDetected = [bool]$resolvedRunner
    graphGatewayRunnerEnv = $env:GRAPH_GATEWAY_RUNNER
    msgraphRunnerEnv = $env:MSGRAPH_RUNNER
    authStatus = $authStatus
    authError = $authError
}