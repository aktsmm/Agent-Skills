# Microsoft Forms UI notes

Observed on forms.cloud.microsoft with the ja-JP UI in Edge, driven by Python Playwright over CDP (2026-10). Labels are in the `L` table of `scripts/forms_lib.py`; another UI language needs only that table changed (untested).

## Controls

| Task                | Control (role, accessible name)                                                                                      | Note                                                                                                                  |
| ------------------- | -------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| New form            | button "新しいフォームを作成"                                                                                        | Opens the editor in a **new tab**. The landing page URL (`DesignPagev2.aspx`, no `id=`) is not an editor.             |
| Copilot draft panel | text "作成したいフォームの内容…" + its own button "閉じる"                                                           | Appears on a new form and covers the title field. Close it before typing.                                             |
| Title / description | click the heading button "フォームのタイトル …", then textbox "フォームのタイトル" / "フォームの説明"                | Both are contenteditable divs. Line breaks in the description: Shift+Enter.                                           |
| First question      | button "以下でクイック スタート", then tile "テキスト" / "選択肢"                                                    | Later questions: button "新しい質問の追加". Match tile names exactly.                                                 |
| Question            | textbox "質問のタイトル N"                                                                                           | Only the open card exposes it. Collapsed cards are buttons "N. 質問のタイトル <title> <type> [回答するのに必要です]". |
| Switches            | switch "必須", "長い回答" (text), "複数回答" (choice)                                                                | Read `aria-checked`.                                                                                                  |
| Options             | textbox "オプションのテキストの選択…", buttons "オプションを追加", `"その他" オプションの追加`, "削除 <option text>" | The delete button is named after the option text, not its number.                                                     |
| Collect responses   | button "回答を収集", radio "すべてのユーザーが回答可能", checkbox "URL を短縮"                                       | Default scope is organisation only. The short URL looks like `forms.cloud.microsoft/r/<code>`.                        |
| Saved state         | header button label ends with "保存済み"                                                                             |                                                                                                                       |

## Failure signatures

| Symptom                                                   | Cause                                           | Fix                                            |
| --------------------------------------------------------- | ----------------------------------------------- | ---------------------------------------------- |
| Title shows twice ("お名前お名前")                        | Resumed run typed again without select-all      | `replace_text()` (Ctrl+A, then insert)         |
| Click times out, a suggestion bubble sits over the switch | Copilot suggestion popover covers the control   | `click()` falls back to a DOM click            |
| Wrong tile clicked ("単一行テキスト" card)                | Substring name match                            | `exact=True`                                   |
| Options 3+ read "オプション 3業務で…"                     | New option is pre-filled                        | Ctrl+A before typing                           |
| Delete click by number fails                              | The button is named "削除 <text>"               | Use the text                                   |
| Last edit missing after navigating away                   | Autosave race; the header already read "保存済み" before the edit registered | `wait_saved(page, expect=<new text snippet>)`, then reopen and read back |
| Two empty untitled forms appear                           | "new form" clicked twice (also by a text match) | Click once; delete only forms this run created |
| Japanese text unreadable in the console                   | PowerShell pipe encoding                        | `PYTHONUTF8=1`, write results to a UTF-8 file  |

## Sign-in

A fresh profile lands on the account picker. Choosing the entry marked "Windows に接続済み" signs in silently. Do not type credentials. A personal account on the same picker is not the right owner for work forms.

## Sharing and verification

- "すべてのユーザーが回答可能" means anonymous, no sign-in. External respondents cannot answer under the organisation-only default.
- Verify with `browser.new_context()` (no cookies): the response URL must stay on `forms.cloud.microsoft`, show the title and the expected number of question items. A real submission is not made.
- Respondent DOM for finer checks: `[data-automation-id=questionItem]` per question, a `requiredStar` inside required ones, one `input[type=radio]` per option of a single-choice question.
- A collapsed "N. 質問のタイトル …" label proves title, type and required flag only; it does not show the options. Option text is asserted while typing.

## Editing the text of an existing form

- Open the design page, click the header button "フォームのタイトル …", then use the textboxes "フォームのタイトル" / "フォームの説明". Select all, delete, then type line by line with Shift+Enter; an empty line gives a blank line.
- Bold: before each line compare `document.queryCommandState('bold')` with the wanted state and press Ctrl+B when they differ. The respondent view then shows `<b>` (computed weight 700).
- A bare `https://…` in the description becomes a clickable link in the respondent view.
- Finish with `wait_saved(page, expect=<snippet>)` and a cookie-less read-back of the respondent page.
- UI-helper route (no API): open `DESIGN + id`, wait about 8 s, `close_copilot_draft_panel`, then `set_title_desc` (replaces the whole description), `add_spec_question(page, n, q)` with `n` = next question number, and `replace_text(page, title_box(page, n), text)` to reword an existing question (click its collapsed card first). Reload and read the page body to verify; `wait_saved(expect=...)` can raise although the edit was applied, so check the reloaded body before repeating the edit.
- A new form's editor URL can stay on `action=Create` for longer than 30 s before the `id` appears (seen once, tenant under load). Do not click "new form" again: keep waiting (`create_form` timeout 90 s) or attach to the open editor tab and resume with the same helpers.

## Changing an existing form (internal API) and the collaborator link

- Adding a question works from the design tab: `POST /formapi/api/forms('<id>')/questions` with the antiforgery header, a client-made `id` (`r` + 32 hex), `title` and `formsProRTQuestionTitle`, a numeric `order`, `type` (`Question.Choice` / `Question.TextField`) and `questionInfo` as a JSON string (201 on success). For "choose up to N" use `ChoiceType: 2`, `ChoiceRestrictionType: "AtMost"`, `ChoiceMaxBoundary: N`; a subtitle needs `ShowSubtitle: true`.
- Move a question with `PATCH` on `/questions('<qid>')` and a new `order` between its neighbours. Verify wording and order on the respondent page, not from the API reply.
- Collaborator link: "…" → 共同作業または複製 → 共同作業者の追加. The dropdown has three scopes: any work/school account (default, includes other organisations), link-holding users of the owner's organisation, specific users. Pick the narrowest the owner approves, then reload and read the scope and link back from the pane.

## Delete recipe (own test forms only)

My forms tab, not Recent: Recent offers only "最近使用した項目から削除". Open the tile menu "<title> その他のオプション", click the item named "削 除" (it contains a space; match `削\s*除`), then the confirmation button "削除". The confirmation is not a `dialog` role and does not name the form, so confirm only right after opening the menu of the intended tile. The form goes to the trash and can be restored.

## Not tried

Quick import (file upload), the Copilot draft, rating/date/ranking/upload questions, sections and branching, forms owned by a group, English UI labels, a test submission.
