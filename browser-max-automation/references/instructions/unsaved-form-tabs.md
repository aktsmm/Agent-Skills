# Unsaved Editor / Draft Tab Safety

Qiita、CMS、SPA admin など **未保存 form** を持つタブを壊さない作法。

## 原則

- 既に目的の editor / draft タブが開いているなら、そのタブを優先して再利用する
- 新しい draft が必要でも、**既存タブを別 URL へ飛ばさず、新しいタブを開く**
- `dialog.accept()` で `beforeunload` を強制吸収する設計を通常フローにしない。race で失敗しやすい
- file upload の前に、現在タブが本当に editor 本体かを **URL と title** で確認する
- upload 専用の一時 editor を作った場合は、その exact URL / ID をログに残す。下流の保存・公開・画像表示を確認してからその ID だけ削除し、無題や最新時刻だけで対象を推測しない
- dirty な form / SPA では `page.reload()`、`location.reload()`、API 捕捉目的の reload trigger を使わない
- まず保存・キャンセル・画面上の status 読み取りで clean にする
- If a leave-site confirmation appears, pause page mutations. Cancel/Stay may be automated only after the browser process, selected-tab address, exact warning and button uniquely match the owned task. Otherwise request manual Cancel/Stay. Never automatically accept Leave or discard unknown edits.
- A native `beforeunload` prompt can block the whole browser window while CDP returns `No dialog is showing`; opening another tab does not dismiss it. Use the scoped [native recovery procedure](cdp-recovery-and-context.md#windows-browser-chrome-leave-site-prompt), verify dismissal and same-target readback, then use a clean work tab without navigating the dirty original. Cancel preserves unsaved form values and does not establish that they were saved.

## 典型ケース

- Qiita 記事 editor で投稿前に画像 upload を挟む（タブを動かさない）
- CMS で記事一覧 → 新規作成 → upload（一覧タブと editor タブを分離）
- SPA admin で「保存していません」ダイアログを跨ぐ全自動化（やらない）

このパターンは Qiita に限らず、**未保存フォームを持つ管理画面** 全般で効く。
