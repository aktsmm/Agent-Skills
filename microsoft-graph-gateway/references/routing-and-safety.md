# Routing And Safety

Read / write routing is defined in SKILL.md "Routing Rules". Writes additionally include `forward` and any action visible to other people.

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
