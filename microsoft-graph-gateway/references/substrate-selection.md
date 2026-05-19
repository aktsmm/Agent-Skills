# Substrate Selection

The gateway skill needs an execution substrate. This reference captures the current recommendation.

## Recommended Core

### `merill/msgraph`

Use as the primary generic Graph substrate when you need:

- arbitrary endpoint reach
- permission and schema lookup
- direct Graph execution
- strong write guardrails

Why it fits:

- broad Graph coverage
- explicit safety model for writes
- strong discovery story for endpoints and permissions

## Domain Helpers

### `elyxlz/microsoft-mcp`

Best when you need curated productivity tools for:

- mail
- calendar
- OneDrive
- contacts
- multi-account flows

### `XenoXilus/outlook-mcp`

Best when you need curated productivity tools for:

- Outlook mail
- calendar
- SharePoint links and files
- attachment and document processing

## Not A Primary Substrate

### Microsoft MCP Server for Enterprise

Useful as a read-only supplement for directory and Entra questions, but not as the main execution substrate for Outlook and productivity writes.

### VS Code Marketplace Extensions

Current marketplace candidates are mainly:

- development helpers
- autocomplete helpers
- read-only viewers

They are not the recommended foundation for a full Graph gateway.

## Current Recommendation

1. Use `merill/msgraph` as the generic Graph core.
2. Add a thin skill shell for routing, confirmation, and policy.
3. Evaluate a productivity-focused MCP helper only where curated tools clearly improve operator experience.
4. Consider a VS Code extension only after the gateway behavior is stable.

## Operational Follow-Up

- Pair this reference with [Environment Setup](./environment-setup.md) before attempting live execution.
