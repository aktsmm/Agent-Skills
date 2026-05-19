# Routing And Safety

## Read Responsibility

- Prefer WorkIQ for common read requests that map naturally to inbox, meetings, and file discovery.
- Use Microsoft Graph when WorkIQ cannot answer, lacks detail, or the user needs exact Graph semantics.
- Go directly to Graph for:
  - endpoint discovery
  - permission lookup
  - exact filters or projections
  - directory, Teams, Planner, To Do, reports, or schema-heavy requests

## Write Responsibility

- All writes go through Microsoft Graph.
- Treat the following as writes even if they feel lightweight:
  - send
  - create
  - update
  - reply
  - forward
  - move
  - upload
  - respond
  - assign

## Confirmation Policy

Before any write, provide a short confirmation summary with:

1. target resource
2. intended action
3. payload intent in plain language
4. noteworthy risk, if any

Do not execute until the user confirms.

## Delete Policy

- Block delete by default in the first implementation.
- If delete is later enabled, require a stronger confirmation step than standard writes.

## Permission Policy

- Default to delegated permissions for interactive use.
- Keep application permissions in a separate future profile.
- Use least privilege and avoid broad directory or file scopes unless the operation requires them.

## Performance Policy

- Use `$select` whenever practical.
- Use minimal response handling for write operations when supported.
- Respect `Retry-After` on throttling.
- Prefer delta query and change notifications over polling for sync scenarios.
- Keep JSON batching within the platform limit of 20 requests.
