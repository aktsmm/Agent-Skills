# Scheduled Runtime Bindings

Use this when an extension or service stores a scheduled task that points to a prompt, agent, model, or other runtime asset.

## Runtime And Fallback State

- Identify the authoritative runtime source: inline text, local file, global file, or remote asset.
- A scheduler may load the current local file at execution time while retaining a stored snapshot as fallback.
- Verify both the live binding and fallback copy. A valid local binding does not make a stale fallback harmless.

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

Never persist task IDs, local absolute paths, account names, or environment-specific schedules in a portable skill.
