---
name: microsoft-forms-builder
description: "Create and configure Microsoft Forms surveys through an owned browser session (Playwright over CDP): title, description, text/choice questions, free-text 'Other', required flags, external-respondent sharing, short URL and an anonymous-access check. Use for Microsoft Forms, forms.cloud.microsoft, アンケート作成, 事前アンケート, 事前ヒアリングフォーム, Forms の共有範囲, 短縮URL, or building a survey from a question table. Not for reading or analysing responses, quizzes, Power Automate flows or Forms Pro."
argument-hint: "アンケートのタイトル・設問表（または spec.json）、回答者（社内/社外）、使うサインインアカウント"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Microsoft Forms Builder

Build a survey in Microsoft Forms from a question spec. Forms has no public API to create a form, so this drives the editor UI. The bundled scripts hold the working recipe; read [UI notes](references/ui-notes.md) before changing them.

## When to Use

- 「Forms でアンケートを作って」「事前アンケートを Forms にして」「共有範囲を外部にして」「短縮 URL がほしい」
- A question table (Markdown, Excel, chat) must become a live Microsoft Form.
- An existing form must become answerable by external users, with a verified anonymous link.

## Not the Best Fit

- Reading, exporting or analysing responses, quizzes, branching/sections, rating/date/ranking/file-upload questions (the scripts only build text and choice questions), Power Automate. Do those by hand or with another route.
- Credentials, MFA and tokens stay with the user. Never type them, and never read a sign-in page's secrets.

## Safety Gates

- **External respondents are a decision, not a default.** The tenant default is "organisation only". Run `--share anyone` only after the user states that respondents are external and anonymous. Bind the approval to the form and the audience.
- Sign in only by choosing the Windows-connected account on the account picker. If sign-in does not complete, stop and ask the user to finish it in that window.
- Use your own Edge window (own port, throwaway profile). Never attach to another tool's CDP browser. The profile holds tokens: stop the window and delete the profile when done.
- A test form may be deleted only if this run created it and its title matches exactly with one tile (My forms tab). Deletion goes to the Forms trash.
- Do not click "new form" repeatedly: each click opens a new tab and leaves an empty untitled form.

## Workflow

1. **Spec first.** Turn the question table into `spec.json` (see below). Always include an optional long free-text question such as "anything else you would like to tell us?"; the validator rejects specs without one. For choice questions use `other: true` instead of listing "その他" as a plain option.
2. `python scripts/build_form.py spec.json --dry-run` (spec check, no browser).
3. Start the session: `scripts/browser_session.ps1 -Action Start`.
4. `python scripts/build_form.py spec.json --account <work account on the picker>`. It creates the form, fills it, waits for "saved", reopens it and compares titles and required flags. Exit code 3 means the read-back failed.
5. External respondents approved: `python scripts/build_form.py spec.json --only-share <form id>` (sets "anyone can respond", turns on a short URL, opens it in a cookie-less context). Report `anonymousOk`.
6. Report the response URL (short URL when it exists), the sharing scope, and what was not checked (no test submission is made). Then `browser_session.ps1 -Action Stop`.

Run Python Playwright from an interpreter that has it installed; set `PYTHONUTF8=1` and write Japanese output to a UTF-8 file, because the PowerShell pipe garbles it.

## spec.json

```json
{ "title": "...", "description": ["line 1", "line 2"],
  "questions": [
    {"type": "text", "title": "お名前", "required": true},
    {"type": "choice", "title": "...", "multiple": true, "required": false, "options": ["A", "B"], "other": true},
    {"type": "text", "title": "自由記述", "long": true, "required": false} ] }
```

`assets/spec.example.json` is a runnable sample. Put examples inside the question title, for example "(例: ...)": the subtitle control is not scripted.

## Gotchas That Cost a Rerun

- Every typing step must select-all first, or a resumed run appends a second copy of the text.
- Match type tiles with exact names: collapsed question cards also contain "テキスト".
- Added options come pre-filled ("オプション 3"); a plain option named "その他" is not the free-text "Other".
- New questions inherit the previous required switch; the script sets it explicitly.
- Leaving the page right after the last edit can lose it; wait for "保存済み", then reopen and verify.
- The built-in "Other" must be added after the other options; it always renders last.

More selectors, failure signatures and the delete recipe: [UI notes](references/ui-notes.md).

## Done Criteria

- [ ] Question titles, types, options and required flags match the spec after the editor was closed and reopened.
- [ ] Sharing scope reported; external scope only with the user's approval, with `anonymousOk: true`.
- [ ] The response link was opened in a cookie-less context and showed the title and question count.
- [ ] The owned browser and its profile are removed; any test form created by this run is deleted.
- [ ] Unverified items are stated: English UI, question types beyond text/choice, a real test submission.