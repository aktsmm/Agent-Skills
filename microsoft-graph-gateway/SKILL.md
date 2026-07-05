---
name: microsoft-graph-gateway
description: "Route Microsoft Graph work in this workspace. Use when users want to read or write Outlook mail, calendar events, contacts, OneDrive or SharePoint files, Teams, Planner, To Do, users, groups, directory data, or arbitrary Microsoft Graph endpoints from VS Code. Prefer WorkIQ for common read scenarios. Use Microsoft Graph for write actions and gap-read scenarios that need exact Graph properties, filters, permissions, or endpoints."
argument-hint: "Describe the Graph task, target resource, and any draft payload, endpoint, or constraints"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Microsoft Graph Gateway

Use this skill as the orchestration shell for Microsoft Graph work in this workspace.

This skill does not try to abstract all of Microsoft Graph into a fixed checklist. Instead, it does two things:

1. Route common read requests to the right source.
2. Enforce safe execution rules before Graph writes or advanced reads.

## When To Use

- The user wants to read or write Microsoft 365 data from VS Code.
- The request mentions mail, email, inbox, Outlook, meetings, calendar, contacts, OneDrive, SharePoint, Teams, Planner, To Do, users, groups, or Microsoft Graph.
- The user wants an exact Microsoft Graph endpoint, permission, query option, or payload.
- WorkIQ can likely answer a common read request, but Graph may be needed as a fallback.

## Routing Rules

### Read Routing

- Prefer WorkIQ first for common read scenarios such as inbox checks, meeting lookups, file discovery, and lightweight summaries.
- Use Microsoft Graph for gap-read scenarios when WorkIQ cannot answer, returns insufficient detail, or the user asks for exact Graph semantics.
- Go straight to Microsoft Graph when the user asks for:
  - exact endpoint names or raw REST calls
  - precise properties, `$select`, `$filter`, `$expand`, or API version control
  - Teams, Planner, To Do, directory, or permission-oriented data
  - schema, permission, throttling, batching, delta, or webhook behavior

### Write Routing

- Use Microsoft Graph for all writes.
- Treat send, create, update, move, upload, reply, assign, and respond operations as writes.
- Require explicit confirmation before any write.
- Keep delete actions disabled by default or behind a stronger confirmation step.

## Operating Model

- This skill is a thin shell.
- The execution substrate can be a Graph CLI, a self-hosted MCP server, or another Graph gateway.
- Do not invent endpoints or permissions from memory when an authoritative lookup is available.
- Keep delegated and application permission flows separate.
- Prefer least-privileged scopes and minimal projections.

## Procedure

1. Classify the request as common read, gap-read, or write.
2. For common read, try the WorkIQ route first.
3. For gap-read or write, identify the target Microsoft Graph surface.
4. Check the capability, routing, and substrate references before choosing the execution path.

- raw execution contract
- permission profiles
- curated tool catalog

5. For Microsoft Graph execution, determine:
   - resource area
   - endpoint or tool
   - API version
   - least-privileged permission profile
   - minimal response shape
6. Before any write, present a concise confirmation summary covering target, action, and payload intent.
7. Execute through the chosen substrate.
8. Report the result, including any permission, throttling, or follow-up concerns.

## Script Entry Points

- Use [Invoke-GraphGateway.ps1](./scripts/Invoke-GraphGateway.ps1) for raw Graph execution through the selected substrate.
- Use [invoke-graph-gateway.sh](./scripts/invoke-graph-gateway.sh) on macOS or Linux when `pwsh` is installed.
- Use [New-GraphWriteConfirmation.ps1](./scripts/New-GraphWriteConfirmation.ps1) to generate a concise write confirmation summary before execution.
- Use [Test-GraphGatewayScaffold.ps1](./scripts/Test-GraphGatewayScaffold.ps1) to smoke-test the current scaffold without live Graph execution.
- Use [test-graph-gateway-scaffold.sh](./scripts/test-graph-gateway-scaffold.sh) on macOS or Linux when `pwsh` is installed.
- Use [Get-GraphGatewayRunnerStatus.ps1](./scripts/Get-GraphGatewayRunnerStatus.ps1) to inspect runner discovery and auth readiness.
- Use [get-graph-gateway-runner-status.sh](./scripts/get-graph-gateway-runner-status.sh) on macOS or Linux when `pwsh` is installed.
- Use [Install-MsGraphRunner.ps1](./scripts/Install-MsGraphRunner.ps1) to bootstrap the preferred `merill/msgraph` runner into the workspace when you explicitly want local setup.
- Use [New-GraphEventResponseRequest.ps1](./scripts/New-GraphEventResponseRequest.ps1) to generate accept, decline, and tentative meeting-response requests.
- Use [New-GraphGatewayAppConfig.ps1](./scripts/New-GraphGatewayAppConfig.ps1) to generate environment snippets for a tenant-approved custom app registration.

## Example Assets

- [Read Mail Request](./assets/read-mail.request.json)
- [Send Mail Request](./assets/send-mail.request.json)
- [List Events Request](./assets/list-events.request.json)
- [Create Event Request](./assets/create-event.request.json)
- [Accept Event Request](./assets/accept-event.request.json)
- [Decline Event Request](./assets/decline-event.request.json)
- [Tentative Event Request](./assets/tentative-event.request.json)
- [Custom App Env Example](./assets/custom-app.env.example)

## Done Criteria

- The request was routed to WorkIQ or Microsoft Graph for an explicit reason.
- Graph calls used least-privileged intent and minimal response shape where practical.
- Writes were confirmed before execution.
- Deletes were blocked or separately escalated.
- The response states what happened and any remaining risk or next action.

## References

- [Capability Matrix](./references/capability-matrix.md)
- [Routing And Safety](./references/routing-and-safety.md)
- [Substrate Selection](./references/substrate-selection.md)
- [Raw Execution Contract](./references/raw-execution-contract.md)
- [Permission Profiles](./references/permission-profiles.md)
- [Curated Tools First Wave](./references/curated-tools-first-wave.md)
- [Environment Setup](./references/environment-setup.md)
- [Prerequisites](./references/prerequisites.md)
- [Troubleshooting](./references/troubleshooting.md)
