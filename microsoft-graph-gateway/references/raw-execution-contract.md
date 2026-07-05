# Raw Execution Contract

This document defines the generic Graph executor that preserves full reach across Microsoft Graph.

## Purpose

- Reach arbitrary Microsoft Graph endpoints without waiting for a curated tool.
- Keep a stable execution contract even if the backend substrate changes.
- Preserve enough structure for routing, confirmation, auditing, and future UI work.

## Input Shape

The raw executor should collect the following logical fields before execution.

| Field               | Required | Description                                                                          |
| ------------------- | -------- | ------------------------------------------------------------------------------------ |
| `method`            | Yes      | `GET`, `POST`, `PATCH`, or `PUT` in the first implementation                         |
| `path`              | Yes      | Relative Graph path such as `/me/messages` or `/users/{id}/calendar/events`          |
| `apiVersion`        | No       | `v1.0` by default, `beta` only when justified                                        |
| `query`             | No       | Structured query options such as `$select`, `$filter`, `$expand`, `$top`, `$orderby` |
| `headers`           | No       | Explicit headers such as `Prefer` or `ConsistencyLevel`                              |
| `body`              | No       | JSON payload for write operations                                                    |
| `permissionProfile` | Yes      | Named profile chosen from the permission catalog                                     |
| `intentSummary`     | Yes      | Short plain-language description of what the call is meant to do                     |
| `isWrite`           | Yes      | Derived from method and semantic action                                              |

## Output Shape

The raw executor should normalize its result to the following logical shape.

| Field            | Description                                                                            |
| ---------------- | -------------------------------------------------------------------------------------- |
| `statusCode`     | HTTP status code                                                                       |
| `requestSummary` | Method, version, and path summary                                                      |
| `responseBody`   | Parsed JSON body or raw content summary                                                |
| `nextAction`     | Suggested follow-up such as pagination, consent, retry, or none                        |
| `warnings`       | Throttling, beta usage, broad permission use, large response, or unsupported semantics |

## Execution Rules

1. Default to `v1.0`.
2. Use `beta` only when the required feature does not exist in `v1.0`.
3. Treat `POST`, `PATCH`, and `PUT` as writes.
4. Reject `DELETE` in the first implementation.
5. Require an explicit permission profile before execution.
6. Encourage `$select` for entity reads when practical.
7. Respect `Retry-After` and surface throttling guidance.
8. Preserve the exact path and query semantics instead of silently rewriting them.

## Confirmation Rules For Raw Writes

Before a raw write executes, the confirmation summary should include:

1. the target resource path
2. the action in plain language
3. the important body fields being changed or created
4. whether `beta` is in use
5. whether the permission profile is broader than usual

## Why This Matters

- Curated tools will never cover the full Graph surface.
- The raw executor is what makes the gateway truly "all reachable" instead of just "many convenience commands."

## Current Script Mapping

- [Invoke-GraphGateway.ps1](../scripts/Invoke-GraphGateway.ps1) is the first implementation scaffold of this contract.
- [New-GraphWriteConfirmation.ps1](../scripts/New-GraphWriteConfirmation.ps1) generates the confirmation summary for write operations.
- [Test-GraphGatewayScaffold.ps1](../scripts/Test-GraphGatewayScaffold.ps1) verifies the scaffold against example request files.
- [read-mail.request.json](../assets/read-mail.request.json) and [send-mail.request.json](../assets/send-mail.request.json) provide reusable request examples.
- [New-GraphEventResponseRequest.ps1](../scripts/New-GraphEventResponseRequest.ps1) generates request objects for accept, decline, and tentative meeting responses.
