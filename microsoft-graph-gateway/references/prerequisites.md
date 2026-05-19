# Prerequisites

Keep prerequisites short and explicit.

## Required

1. VS Code with GitHub Copilot Chat agent mode enabled
2. PowerShell 7 or later for the current scaffold
3. Network access to Microsoft Graph and Microsoft Entra sign-in endpoints
4. A Microsoft Graph execution substrate such as `merill/msgraph`
5. A signed-in Microsoft account with consent for the required delegated scopes
6. For live write tests, the current tenant and client app must allow the required write scopes such as `Mail.Send` and `Calendars.ReadWrite`

## Recommended

1. `msgraph` available on `PATH`, or `GRAPH_GATEWAY_RUNNER` set
2. A workspace-local runner install if you do not want to depend on global tools
3. WorkIQ available for common read routing

## Current Platform Note

- Windows is supported through the PowerShell scripts directly.
- macOS and Linux are supported through the `pwsh`-backed `.sh` wrappers in `scripts/`.
- The current scaffold is cross-platform at the entrypoint level, but live behavior still depends on the installed runner and auth flow.

## Light Setup Checklist

1. Run the scaffold smoke test
2. Install or point to a runner
3. Check runner status
4. Sign in to Graph
5. Perform a read test before a write test

## Write Test Note

- A successful delegated sign-in does not guarantee write access.
- Live mail and calendar writes can still fail with `403 ErrorAccessDenied` if the current client app or tenant policy does not allow the requested write scopes.
- If that happens, use a custom Entra ID app registration or a tenant-approved client configuration for live write validation.

## Admin Approval Note

- If the sign-in screen says that administrator approval is required for Microsoft Graph Command Line Tools, the tenant is blocking consent for the current client app.
- In that case, re-signing alone is not enough.
- Use one of these paths:
  - ask a tenant admin to approve the app and required delegated scopes
  - switch the runner to a tenant-approved custom app registration
- Use [New-GraphGatewayAppConfig.ps1](../scripts/New-GraphGatewayAppConfig.ps1) or [custom-app.env.example](../assets/custom-app.env.example) to prepare the environment for a custom app quickly.
