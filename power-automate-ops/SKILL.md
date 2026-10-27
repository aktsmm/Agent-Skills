---
name: "power-automate-ops"
description: "Operate and verify Microsoft Power Automate cloud flows in the browser, and migrate them between environments. Use when creating, editing, testing, or troubleshooting Power Automate flows, Forms triggers, Teams connector posts/replies, Flow Checker errors, run history, or Power Automate UI automation; also when rebuilding a flow in another environment and stopping or deleting the old one, when DLP or connection limits block editing or saving, when adding co-owners, or when checking Dataverse for Teams retirement and upgrade. Triggers: フロー移行, 環境移行, 旧フロー削除, DLP で保存できない, 共同所有者, Dataverse for Teams アップグレード. Do not use for Logic Apps IaC or general browser automation unrelated to Power Automate."
argument-hint: "対象フロー、トリガー、アクション、出力先、テスト/修正/移行したい症状（移行なら移行元・移行先の環境と削除してよい旧フローの範囲）"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: aktsmm
---

# Power Automate Ops

Use this skill for hands-on Power Automate cloud-flow work in the browser: create, edit, repair, test, and verify flows that integrate Microsoft Forms, Teams, Outlook, SharePoint, and similar Microsoft 365 connectors.

## When to Use

- User asks to create or edit a Power Automate cloud flow.
- User mentions Power Automate, cloud flow, フロー作成, フロー修正, フローチェッカー, 実行履歴, Forms trigger, Teams connector, or Workflows app.
- A flow posts visible content to Teams/email and needs safe preview, confirmation, testing, and run-history verification.
- The task involves brittle Power Automate browser UI operations, dynamic content tokens, connector parameters, or action replacement.
- A flow must be rebuilt in another environment and the old one stopped or deleted, DLP/ACP blocks editing or saving, a co-owner must be added, or Dataverse for Teams retirement/upgrade needs checking: follow [references/migration.md](references/migration.md).

## Do Not Use

- Do not use for Azure Logic Apps infrastructure-as-code or ARM/Bicep authoring.
- Do not use for Power Apps app-building unless the task is specifically about an embedded Power Automate flow.
- Do not re-teach browser automation mechanics. If Playwright/CDP/UI recovery is the main problem, treat general browser automation as a separate concern and keep this skill focused on Power Automate semantics.

## Safety Gates

1. Freeze the goal, trigger, destination, visible recipients, and done criteria before editing.
2. For any action that sends or posts content visible to others, show the exact recipient/channel/thread and message content, then wait for explicit user confirmation before testing or sending.
3. Treat Forms responses, email addresses, names, company names, and Teams/chat content as private user data. Do not move them outside the approved destination.
4. If a UI step becomes ambiguous, stop before destructive actions such as deleting actions, changing connectors, or posting test messages.
5. Deleting a flow, creating an environment, or changing permissions, sharing or DLP needs the exact target and impact shown and individual approval. If DLP/ACP rejects the same operation, do not retry or route around it; rebuild elsewhere.

## Core Workflow

1. Identify the flow type: new flow, existing-flow edit, failure triage, or test verification.
2. Confirm connectors and target resources: trigger Form ID, Team, channel, parent message ID, recipient, response URL, and service account/user connection.
3. Build or edit in small increments: trigger -> data lookup -> action -> Flow Checker -> save -> test.
4. Use the Power Automate UI, but distrust generated actions until verified. Copilot can draft a flow, but it may choose the wrong Teams action or invent dynamic-content names.
5. Run Flow Checker after structural edits. Require zero errors; warnings must be reviewed and either fixed or explicitly accepted.
6. Save only after the checker is clean.
7. Test with a real but clearly fake submission when the trigger requires external input. Verify the final destination, not just a green flow run.

## High-Signal Gotchas

- **Teams thread replies:** Use **Reply with a message in a channel** / `チャネル内のメッセージで応答します`. Do not add `replyToId` to generic **Post message in a chat or channel**; Flow Checker rejects it.
- **Parent message IDs:** Hardcoded Teams parent message IDs are runtime dependencies. Verify the parent top-level message exists in the exact Team + channel before trusting the flow.
- **Forms dynamic content:** The Forms trigger returns response IDs, not answers. Insert answer tokens from **Get response details**. In expressions, Forms answers usually become internal `r...` keys; do not rely on guessed short names.
- **Links in Teams:** Long raw URLs can wrap and appear broken. Use HTML anchor text such as `<a href="...">Forms回答一覧を開く</a>`.
- **Forms response URLs:** A Forms design/responses URL usually requires sign-in and edit/view permission. That is acceptable when the recipients are authorized, but do not describe it as public.
- **Flow Checker scope:** Flow Checker validates schema, not runtime existence of a Teams message, channel permission, or whether recipients can open a link.

## Common Runbooks

- Forms -> Teams speaker/application notification: [references/forms-teams-flow.md](references/forms-teams-flow.md)
- Power Automate UI gotchas and verification: [references/power-automate-ui-gotchas.md](references/power-automate-ui-gotchas.md)
- Migrating a flow to another environment, deleting the old one, DLP blocks, co-owners, Dataverse for Teams dates: [references/migration.md](references/migration.md)

## Done Criteria

- Flow Checker has zero errors.
- Flow is saved and testable.
- Runtime test confirms the expected destination received the expected content.
- For visible posts, user approved the exact test/send action.
- Any unresolved risk is documented plainly, such as no failure branch, broad channel visibility, or permission-gated links.
- For a migration, the migration runbook's own Done Criteria also hold.
