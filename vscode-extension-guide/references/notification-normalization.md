# Notification Normalization

Centralize extension notifications behind one helper when commands, background jobs, and error handlers otherwise produce inconsistent or duplicated messages.

The helper should:

- map internal outcomes to stable user-facing severity and wording
- suppress duplicate messages for the same operation
- keep logs more detailed than notifications
- expose action buttons only when the action is available
- avoid displaying stack traces, local paths, or secrets

Keep the concrete TypeScript implementation aligned with the extension's existing logger, localization, and command APIs. Validate success, warning, error, duplicate suppression, and action-button paths with the extension's normal test framework.

## Recurring Failures (startup and background refresh)

- Classify a failure by a typed error `kind`, never by message text: messages are localized, so text matching sorts one failure differently per language.
- A failure a retry cannot fix (empty result, moved repository) is recorded and shown once per cause. Key the record to a fingerprint of the definition (URL, branch, paths) so an edited definition starts clean, retry on a long interval, and clear it when a manual run succeeds. Failures the user can act on (auth, network, rate limit) stay shown every time.
- Zero results from candidates that could not be read is a failed read, not an empty source: do not stamp freshness and do not silence it.
- Cap notices per run and keep the rest recorded as unshown, so they appear on the next run without rescanning.
- In a batch loop, a failing item that already persisted state must hand that state to the next item; otherwise the next save overwrites it.
- Mark opted-out items where the user looks (for example a tree badge) and say how to restore them.
