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

## Gateway Returns `Access denied for <verb> path`

Symptom:

- A WorkIQ MCP call returns `statusCode 400` with `Access denied for POST path: ...` (observed for `/shares/.../workbook/worksheets/add` and `/me/drive/items/<id>/createLink`; a workbook `usedRange` GET was denied too), while mail/chat writes through the same gateway succeeded.

Meaning:

- The gateway's path allowlist refuses that endpoint; it is not a token or consent failure. The same file may also open read-only in Excel for the web (`閲覧限定`, sheet-add button disabled) when it is owned by another team.

What to do:

1. Do not retry or swap routes to bypass it. Report the denied path.
2. For a file you do not own, deliver the need through a new file you own (copy only the requested rows and columns) and share it (create the link in the signed-in browser when allowed, otherwise ask the user), rather than editing the original.

## External Or Personal Teams Accounts Return No Directory User

Symptom:

- `GET /users?$filter=mail eq '<address>'`, or a chat-members read, returns 0 rows or a member without a display name for a person who is visible in the Teams member list.

Meaning:

- The person is a personal or external Teams identity outside the tenant directory, so directory-based Graph calls cannot resolve or add them. Observed where guests had directory entries but personal-account participants did not.

What to do:

1. Do not report the person as missing. Read the member list in Teams itself and match by display name and the External label.
2. Add or verify membership in the Teams UI. Decide whether to share chat history before adding; it cannot be changed afterwards.
3. Read the member count and the system message back after adding.

## Useful Helpers

- [Get-GraphGatewayRunnerStatus.ps1](../scripts/Get-GraphGatewayRunnerStatus.ps1)
- [New-GraphGatewayAppConfig.ps1](../scripts/New-GraphGatewayAppConfig.ps1)
- [custom-app.env.example](../assets/custom-app.env.example)
