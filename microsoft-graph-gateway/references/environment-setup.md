# Environment Setup

This skill currently assumes a Microsoft Graph execution substrate is available on the machine.

## Current Runner Preference

1. `-RunnerPath` argument on the gateway script
2. `GRAPH_GATEWAY_RUNNER` environment variable
3. `MSGRAPH_RUNNER` environment variable
4. `msgraph` on `PATH`

## Current Expectation

The current scaffold is optimized around the `merill/msgraph` runner.

PowerShell 7 is the common execution layer across Windows, macOS, and Linux for the current scaffold.

## Helper Script

- Use [Get-GraphGatewayRunnerStatus.ps1](../scripts/Get-GraphGatewayRunnerStatus.ps1) to inspect runner discovery and current auth status.
- Use [Install-MsGraphRunner.ps1](../scripts/Install-MsGraphRunner.ps1) to download and unpack the preferred runner when you intentionally want a local substrate.

## Recommended Setup Pattern

### If `msgraph` is already on `PATH`

- No additional configuration is required for runner discovery.

### If the runner is not on `PATH`

- Set `GRAPH_GATEWAY_RUNNER` to the full executable path.
- Or pass `-RunnerPath` explicitly during execution.
- Or bootstrap a local copy with `Install-MsGraphRunner.ps1` and then set `GRAPH_GATEWAY_RUNNER`.

### If the default client app is blocked by tenant consent policy

- Set `MSGRAPH_CLIENT_ID` to a tenant-approved custom app registration.
- Set `MSGRAPH_TENANT_ID` to the target tenant.
- Re-run sign-in with the new client.
- Use [New-GraphGatewayAppConfig.ps1](../scripts/New-GraphGatewayAppConfig.ps1) to generate the environment snippet.

## Live Execution Readiness Checklist

1. Runner command is discoverable.
2. Authentication status can be read.
3. Dry-run works without a runner.
4. Write confirmation is generated before any live write.
5. Least-privileged permission profile is chosen before execution.
6. The active client app and tenant policy actually permit the intended write scopes.

## Scope Boundary

This skill currently documents and scaffolds the runner contract. It does not yet provision runner binaries, app registrations, or tenant consent flows automatically.

The installer helper downloads the preferred runner, but it still leaves authentication and tenant consent as explicit operator steps.

If a live `/me` read succeeds but live mail or calendar writes return `403 ErrorAccessDenied`, treat tenant consent and app registration as a real prerequisite for write validation.
