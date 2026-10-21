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
| Last edit missing after navigating away                   | Autosave race                                   | `wait_saved()`, then reopen and read back      |
| Two empty untitled forms appear                           | "new form" clicked twice (also by a text match) | Click once; delete only forms this run created |
| Japanese text unreadable in the console                   | PowerShell pipe encoding                        | `PYTHONUTF8=1`, write results to a UTF-8 file  |

## Sign-in

A fresh profile lands on the account picker. Choosing the entry marked "Windows に接続済み" signs in silently. Do not type credentials. A personal account on the same picker is not the right owner for work forms.

## Sharing and verification

- "すべてのユーザーが回答可能" means anonymous, no sign-in. External respondents cannot answer under the organisation-only default.
- Verify with `browser.new_context()` (no cookies): the response URL must stay on `forms.cloud.microsoft`, show the title and the expected number of question items. A real submission is not made.
- A collapsed "N. 質問のタイトル …" label proves title, type and required flag only; it does not show the options. Option text is asserted while typing.

## Delete recipe (own test forms only)

My forms tab, not Recent: Recent offers only "最近使用した項目から削除". Open the tile menu "<title> その他のオプション", click the item named "削 除" (it contains a space; match `削\s*除`), then the confirmation button "削除". The confirmation is not a `dialog` role and does not name the form, so confirm only right after opening the menu of the intended tile. The form goes to the trash and can be restored.

## Not tried

Quick import (file upload), the Copilot draft, rating/date/ranking/upload questions, sections and branching, forms owned by a group, English UI labels, a test submission.
