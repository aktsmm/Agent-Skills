# Scheduled Runtime Bindings

Use this when an extension or service stores a scheduled task that points to a prompt, agent, model, or other runtime asset.

## Runtime And Fallback State

- Identify the authoritative runtime source: inline text, local file, global file, or remote asset.
- A scheduler may load the current local file at execution time while retaining a stored snapshot as fallback.
- Verify both the live binding and fallback copy. A valid local binding does not make a stale fallback harmless.
- When migrating a task from inline text to a local file, refresh the stored fallback from the same normalized prompt text. A redirect stub is not an equivalent fallback.

## Read-Only Verification

A deterministic verifier checks:

- task exists exactly once in the intended scope
- task is enabled and owned by the expected workspace
- schedule and selected agent/model are expected
- prompt source and relative path resolve
- the current prompt contains its required runtime contract
- the normalized fallback snapshot matches during strict release or retro validation

Normalize BOM, CRLF/LF, and trailing newlines before comparing prompt text.

## Mutation Rule

The verifier does not auto-repair scheduler state. Read current state, report exact drift, update only the intended fields through the scheduler API or UI, then read the task back.

On an optimistic-concurrency rejection, re-read the task before exactly one retry. A second rejection is a stop condition.

## Scheduled Run Outcome Triage

- For a scheduled run, use the command exit/output and expected artifact as primary result signals. Scheduler history and terminal/PTY warnings are corroborating signals.
- A terminal/PTY exit warning, including a host-specific `-1`, is not a task failure by itself. If primary checks pass and a subsequent terminal command succeeds, record host evidence without changing interpreter or extension configuration. Escalate when a normal terminal cannot be recreated or a required command/artifact fails.

Never persist task IDs, local absolute paths, account names, or environment-specific schedules in a portable skill.
