# Curated Tools First Wave

This document defines the first convenience tools that sit above the raw Graph executor.

## Goal

- Cover high-frequency productivity actions with short, predictable language.
- Keep the list intentionally small so the gateway does not explode into hundreds of brittle wrappers.
- Preserve the raw executor as the escape hatch for everything else.

## First-Wave Tool Set

| Tool                 | Purpose                                      | Notes                                                  |
| -------------------- | -------------------------------------------- | ------------------------------------------------------ |
| `list-messages`      | Read recent messages with minimal projection | Prefer WorkIQ first for simple inbox reads             |
| `get-message`        | Read a specific message in detail            | Use Graph when exact properties or body content matter |
| `send-message`       | Send a new email                             | Write confirmation required                            |
| `reply-message`      | Reply or reply-all                           | Write confirmation required                            |
| `list-events`        | Read upcoming events                         | Prefer WorkIQ first for simple schedule reads          |
| `create-event`       | Create a meeting or appointment              | Write confirmation required                            |
| `update-event`       | Reschedule or modify an event                | Write confirmation required                            |
| `accept-event`       | Accept a meeting request                     | Write confirmation required                            |
| `decline-event`      | Decline a meeting request                    | Write confirmation required                            |
| `tentative-event`    | Tentatively accept a meeting request         | Write confirmation required                            |
| `check-availability` | Inspect free/busy windows                    | Usually Graph directly                                 |
| `search-files`       | Search OneDrive or SharePoint files          | Prefer WorkIQ first for broad discovery                |
| `get-file`           | Read or download a file reference            | Decide later whether content stays inline or external  |
| `upload-file`        | Upload or replace content                    | Write confirmation required                            |
| `list-contacts`      | Read contacts                                | Convenience wrapper over common contact views          |
| `get-user-or-group`  | Read directory targets by exact identifier   | Helps avoid broad raw directory calls for common cases |
| `raw-graph-call`     | Escape hatch for arbitrary Graph execution   | Always available for unsupported surfaces              |

## Not In The First Wave

- full Teams surface
- Planner plan and task management wrappers
- To Do wrappers
- lifecycle and webhook orchestration
- broad SharePoint administration wrappers
- delete wrappers

These should remain raw-Graph-first until stable usage patterns emerge.

Meeting responses are now important enough to treat as first-wave conveniences because they are common, semantically stable, and easy to confirm safely.

## Selection Criteria

A workflow belongs in the first wave only if it is:

1. common
2. high-value
3. semantically stable
4. easy to confirm safely
5. likely to benefit from shorter language than a raw endpoint call

## Naming Principle

- Use action-oriented names.
- Prefer resource-neutral verbs only when the scope is obvious.
- Avoid adding multiple aliases for the same underlying action.
