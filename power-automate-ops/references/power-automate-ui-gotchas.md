# Power Automate UI Gotchas

This reference captures Power-Automate-specific UI and verification lessons. Generic browser automation mechanics are out of scope here.

## Copilot Drafts Are Starting Points

Power Automate Copilot can create a useful skeleton, but verify every action.

- It may choose **Post message in a chat or channel** when the requirement is a thread reply.
- It may invent short dynamic-content paths such as `body/answers/登壇者`.
- It may add comments instead of actually changing action parameters.

Always inspect the action parameters and run Flow Checker.

## Teams Reply Action

For replying to a channel thread, use:

```text
Microsoft Teams -> チャネル内のメッセージで応答します
```

Required parameters commonly include:

- `投稿先`: channel
- `メッセージ ID`: parent top-level message ID
- `チーム`: target Team
- `チャネル`: target channel
- `メッセージ`: body

Do not add a custom `replyToId` advanced parameter to the generic Teams post action. It is not in that action schema.

## Dynamic Content

- Forms trigger output only identifies the response.
- Use **Get response details** to access actual answer fields.
- In code/expression view, answer fields often appear as internal keys like `body/r...`.
- Prefer inserting tokens from the dynamic-content picker once, then use those exact internal keys in expressions if needed.

## Message Editor

- The rich text editor can show HTML code view, but full action code view may be read-only.
- Clipboard paste into the message editor can be more reliable than typing long HTML.
- After pasting HTML or expressions, run Flow Checker before saving.
- If line breaks are important, replace newlines with `<br>` in expressions.

## Verification

Flow Checker proves the flow is structurally valid. It does not prove:

- the parent Teams message still exists,
- the channel or Team ID is correct,
- the connector account has access,
- the Forms responses link is usable by recipients,
- or the final Teams message is readable.

Verify with an actual test response after explicit approval.

## Failure Handling

For production flows, consider adding a failure branch after the Teams post/reply action:

- Configure run after: has failed, timed out, or skipped.
- Send a minimal owner-only alert with the Response ID and flow run link.

If adding the branch is risky in the UI, document it as a residual operational risk rather than pretending it is done.
