# Forms to Teams Flow Runbook

Use this runbook when a Microsoft Forms submission should notify a Teams channel or thread.

## Inputs to Confirm

| Input | Notes |
| --- | --- |
| Form ID | For group forms, paste the Form ID manually if it does not appear in the dropdown. |
| Trigger | Microsoft Forms: **When a new response is submitted**. |
| Details action | Microsoft Forms: **Get response details** using the trigger Response ID. |
| Teams destination | Team, channel, and whether this is a new channel post or a reply to an existing parent message. |
| Message content | Preview exact visible text before testing. |
| Link policy | Decide whether recipients can open a sign-in-gated Forms responses URL. |

## Recommended Build Order

1. Add the Forms trigger and set the Form ID.
2. Add **Get response details** with the same Form ID and trigger Response ID.
3. Add the Teams action:
   - New channel post: **Post message in a chat or channel**.
   - Existing thread reply: **Reply with a message in a channel** / `チャネル内のメッセージで応答します`.
4. Insert answer tokens from **Get response details**, not from the trigger.
5. Use clear link text for long URLs.
6. Run Flow Checker, save, then submit a test form response.
7. Verify the actual Teams message and Response ID.

## Compact Teams Template

Use a compact message when the thread is used for triage:

```html
<p>🎤 <strong>新しい登壇希望（スピーカーネーム）</strong>: {speaker_name}</p>
<p>形式: {session_type} / 希望月: {preferred_month}<br>
連絡先: {email} / Teams: {teams_contact}<br>
氏名: {name}（{furigana}） / 企業名: {company}</p>
<p><strong>登壇内容:</strong><br>
{session_title_and_summary}</p>
<p>詳細: <a href="{forms_responses_url}">Forms回答一覧を開く</a><br>
Response ID: {response_id}</p>
```

For optional values, use Power Automate expressions such as:

```text
if(empty(<token>), '未記入', <token>)
```

For Teams contact, `なし` is often better than `未記入`:

```text
if(empty(<teams_contact_token>), 'なし', <teams_contact_token>)
```

For multi-line text, preserve line breaks:

```text
replace(<multiline_token>, decodeUriComponent('%0A'), '<br>')
```

## Link Guidance

- Prefer `Forms回答一覧を開く` as link text.
- Do not paste a long raw Forms URL into the Teams body; Teams may wrap it and make it look broken.
- If the URL opens a sign-in page in a fresh browser, verify whether it opens correctly for an authorized, signed-in owner. Sign-in requirement is not the same as a broken URL.

## Test Data

Use obviously fake data for tests:

```text
Name: テスト 太郎
Email: test-speaker@example.com
Speaker name: 架空株式会社 Azure漫談師 テスト太郎
```

Avoid real personal data in tests unless the user explicitly asks for it and the destination is approved.
