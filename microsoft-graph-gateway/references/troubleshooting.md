# Troubleshooting

## Admin Approval Required

Symptom:

- The sign-in page says administrator approval is required for Microsoft Graph Command Line Tools.

Meaning:

- The tenant does not allow user consent for the current client app and requested delegated scopes.

What to do:

1. Ask a tenant admin to approve the app.
2. Or switch to a tenant-approved custom app registration.
3. Re-sign in after switching the client ID and tenant ID.

## `403 ErrorAccessDenied` On Writes

Symptom:

- `GET /me` works, but `POST /me/sendMail` or `POST /me/events` returns `403 ErrorAccessDenied`.

Meaning:

- Authentication succeeded, but the token or app policy does not allow the requested write scopes.

What to do:

1. Check whether the tenant approved `Mail.Send` or `Calendars.ReadWrite` for the active client app.
2. Re-sign in with a tenant-approved app registration.
3. Retry a read first, then retry the write.

## Useful Helpers

- [Get-GraphGatewayRunnerStatus.ps1](../scripts/Get-GraphGatewayRunnerStatus.ps1)
- [New-GraphGatewayAppConfig.ps1](../scripts/New-GraphGatewayAppConfig.ps1)
- [custom-app.env.example](../assets/custom-app.env.example)
