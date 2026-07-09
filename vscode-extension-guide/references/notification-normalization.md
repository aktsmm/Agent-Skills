# Notification Normalization

Centralize extension notifications behind one helper when commands, background jobs, and error handlers otherwise produce inconsistent or duplicated messages.

The helper should:

- map internal outcomes to stable user-facing severity and wording
- suppress duplicate messages for the same operation
- keep logs more detailed than notifications
- expose action buttons only when the action is available
- avoid displaying stack traces, local paths, or secrets

Keep the concrete TypeScript implementation aligned with the extension's existing logger, localization, and command APIs. Validate success, warning, error, duplicate suppression, and action-button paths with the extension's normal test framework.
