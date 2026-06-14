---
name: browser-max-automation
description: Browser automation using Playwright MCP, CDP, and direct WebSocket CDP for web testing, UI verification, and form automation. Use when navigating websites, clicking elements, filling forms, taking screenshots, testing web applications, reusing an existing browser session, or troubleshooting CDP / iframe / modal / file chooser issues.
argument-hint: "自動化したい URL、操作内容、使いたいモード"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Browser Max Automation

Browser automation via Playwright MCP, existing-browser CDP, and direct CDP helpers.

## When to Use

- ブラウザ自動化、UI 確認、フォーム操作、スクリーンショット取得
- MCP で手順を確立してから Python で一括実行したいとき
- 既存ブラウザのログイン状態を CDP 経由で使いたいとき
- Playwright MCP / `connect_over_cdp()` が不安定で、raw CDP WebSocket に切り替えたいとき
- モーダルや file chooser など、通常クリックが壊れやすい UI を扱うとき

## Not the Best Fit

- API や CLI だけで完結する read/write は、まず該当 domain skill / script を使う
- PowerPoint / Loop / Dynamics 365 MyExpense など専用 skill がある UI は、該当 skill の操作ルールを優先する
- 認証情報、秘密情報、MFA 応答をチャットで受け取らない。必要な入力はブラウザ上でユーザーに処理してもらう

## Choose Mode First

| モード             | 向く場面                                               | メリット                       | 注意点                     |
| ------------------ | ------------------------------------------------------ | ------------------------------ | -------------------------- |
| 新規ブラウザ       | まず安定して動かしたい                                 | 設定が簡単                     | 既存ログイン状態は使えない |
| 既存ブラウザ (CDP) | 普段のブラウザ状態をそのまま使いたい                   | ログイン済み状態を再利用できる | デバッグモード起動が必要   |
| 直接 CDP WebSocket | Playwright CDP が不安定、または MCP と競合させたくない | 低レベル操作で安定しやすい     | CDP コマンドを自前管理する |

既存ブラウザ CDP の起動、profile 確認、port drift、認証 URL encode は [references/instructions/cdp-existing-browser.md](references/instructions/cdp-existing-browser.md) を参照する。
直接 WebSocket CDP の起動フラグ、`websocket-client` 接続、SPA hash navigation、virtual scroll 操作は [references/instructions/cdp-direct-websocket.instructions.md](references/instructions/cdp-direct-websocket.instructions.md) を参照する。

## Quick Reference

| Command                   | Purpose           |
| ------------------------- | ----------------- |
| `browser_navigate`        | URL を開く        |
| `browser_snapshot`        | 要素 ref を取る   |
| `browser_click`           | ref でクリック    |
| `browser_type`            | テキスト入力      |
| `browser_take_screenshot` | 画面確認          |
| `browser_wait_for`        | 表示待機          |
| `browser_evaluate`        | DOM 直接操作      |
| `browser_file_upload`     | file chooser 対応 |

## Core Loop

```text
1. browser_navigate(url)
2. browser_snapshot で ref を取る
3. browser_click / browser_type で操作する
4. browser_snapshot or screenshot で結果確認する
```

UI verification では、操作前に期待する state と確認方法を決める。成功 toast やボタン押下だけを成功判定にせず、DOM、URL、永続化された一覧行、API の read 結果、または screenshot / trace などの証跡で確認する。

保存・提出系 UI では、API と DOM の状態が一時的にずれることがある。API が stale / capture failure を返しても、画面上の cell / row の `aria-label` や status text が `PENDING APPROVAL` / `SUBMITTED` 等を示しているなら、その DOM status も正本候補として扱う。API だけで「未提出」「Draft のまま」と断定しない。

## Decision Patterns

### MCP で続けるか、CLI に切り替えるか

- **MCP**: 1 件ずつ画面を見ながら UI フロー、セレクタ、待機時間を確立する
- **Python CLI**: 手順が固まった後に N 件一括処理する

切り替え基準は単純で、**操作手順をまだ探っているなら MCP、手順が固まったら CLI**。

### snapshot で取れない要素をどう扱うか

- `browser_snapshot` で ref が取れるなら通常操作する
- 画面には見えるのに ref が取れないなら `browser_evaluate` で DOM 直接操作する
- 画面にも見えていないなら、待機かページ再読込を優先する

```text
snapshot で ref 取得
  ├─ 取れた → click / type
  └─ 取れない → screenshot で可視確認
      ├─ 見えている → evaluate で直接操作
      └─ 見えていない → wait / reload
```

### read-only データ抽出を高速化する

一覧表、残高、ステータス確認など、**読み取りだけ** の fallback では、巨大な `browser_snapshot` を何度も解析しない。手順が分かっている画面は `browser_evaluate` で DOM から必要な行だけを JSON 化して返す。

- ページ到達やログイン状態の判定: `browser_snapshot` で証跡を残す
- 表・明細・残高などの定型抽出: `browser_evaluate` で `document.querySelectorAll("tr")` や `document.body.innerText` を処理して JSON を返す
- 不可逆操作の直前・直後: snapshot または screenshot を残す

また、helper / probe / cache の JSON artifact を一次ソースにする場合は、内容を見る前に `timestamp` や対象日を確認する。日付が現在の実行日と合わない artifact は stale とみなし、`ok` や `fast_path_ok` が true でも確定情報として使わない。

### unsaved editor / draft タブを壊さない

Qiita や CMS の draft editor のように、未保存変更を持つタブへそのまま別 URL を開かせると、`beforeunload` dialog が出て upload や遷移が壊れることがある。

- 既に目的の editor / draft タブが開いているなら、そのタブを優先して再利用する
- 新しい draft が必要でも、**既存タブを別 URL へ飛ばさず、新しいタブを開く**
- `dialog.accept()` で無理に吸収する設計を通常フローにしない。beforeunload は race で失敗しやすい
- file upload の前に、現在タブが本当に editor 本体かを URL と title で確認する
- dirty な form / SPA では `page.reload()`、`location.reload()`、API 捕捉目的の reload trigger を使わない。まず保存・キャンセル・画面上の status 読み取りで clean にする。reload 確認や unsaved alert が出たら、追加自動化を止めて手動 Cancel / Stay を優先する

このパターンは、Qiita に限らず「未保存フォームを持つ管理画面」全般で効く。

Azure Portal iframe / OOPIF / trusted event の注意は [references/instructions/azure-portal.md](references/instructions/azure-portal.md) を参照する。
Angular Material / `mat-select` / `cdk-overlay` / disabled save の注意は [references/instructions/angular-material.md](references/instructions/angular-material.md) を参照する。

### iframe と force click

- iframe が多段なら `contentFrame()` を順に辿る
- SVG オーバーレイなどで塞がれているだけなら `force: true` を検討する
- ただし `force: true` は最後の手段で、まず要素の実在確認と可視確認を優先する

### file chooser が残ったとき

- `browser_file_upload(paths=[])` で空送信して閉じる
- ダメなら別ページへ移動する
- CDP 競合が疑わしいなら Python プロセスや MCP 接続を整理する

hidden file input、evaluate + fetch、API write の UI fallback は [references/instructions/ui-fallbacks.md](references/instructions/ui-fallbacks.md) を参照する。

## Safety Rules

### CDP 排他制御

MCP Playwright と Python スクリプトは **同じ CDP ポートへ同時接続しない**。
とくに Python 側も `connect_over_cdp()` を使う場合、MCP と Playwright セッションが二重になり、ページ操作が競合して「遷移先が想定外」「フォーム送信が効かない」等の不定失敗が起きる。

| ルール        | 内容                                                                                                               |
| ------------- | ------------------------------------------------------------------------------------------------------------------ |
| 同時接続禁止  | MCP と Python を同じ CDP に同時接続しない                                                                          |
| MCP 切断優先  | Python 実行前に **`browser_close` で MCP ページを解放** してから実行する                                           |
| プロセス確認  | 実行前にゾンビ Python を確認する                                                                                   |
| 標準フロー    | MCP で手順確立 → `browser_close` → Python 単独実行 → 完了後に MCP 再接続して検証                                   |
| raw WebSocket | `websocket-client` 等で CDP WebSocket に直接繋ぐスクリプトは MCP と共存可能（Playwright セッションを張らないため） |

raw WebSocket を使う場合は、CDP command id で応答をフィルタし、`Runtime.enable` / `Page.enable` など必要な domain を先に有効化する。詳細は [references/instructions/cdp-direct-websocket.instructions.md](references/instructions/cdp-direct-websocket.instructions.md) を参照する。

CDP recovery、blocking dialog、context/page selection は [references/instructions/cdp-recovery-and-context.md](references/instructions/cdp-recovery-and-context.md) を参照する。

### 破綻しやすい場面

- modal overlay が snapshot に出ない
- file chooser が残って後続操作を塞ぐ
- CDP 二重接続で入力先が混線する
- CDP の別 context/page を使い、未ログイン画面や別アカウントを操作してしまう
- 「見えているがクリックできない」状態を無理に通常 click で押し切る

## Subprocess + CDP Stability (Windows)

Windows の PIPE デッドロック、VS Code terminal の SIGINT、JSON status artifact、taskkill tree kill は [references/instructions/windows-subprocess-cdp.md](references/instructions/windows-subprocess-cdp.md) を参照する。

## Reference Map

| Need | Reference |
| --- | --- |
| Existing browser CDP, profile, port drift | [references/instructions/cdp-existing-browser.md](references/instructions/cdp-existing-browser.md) |
| Raw CDP WebSocket | [references/instructions/cdp-direct-websocket.instructions.md](references/instructions/cdp-direct-websocket.instructions.md) |
| CDP recovery and context selection | [references/instructions/cdp-recovery-and-context.md](references/instructions/cdp-recovery-and-context.md) |
| Azure Portal iframe / OOPIF | [references/instructions/azure-portal.md](references/instructions/azure-portal.md) |
| Angular Material forms | [references/instructions/angular-material.md](references/instructions/angular-material.md) |
| Hidden upload, evaluate+fetch, UI fallback | [references/instructions/ui-fallbacks.md](references/instructions/ui-fallbacks.md) |
| Windows subprocess stability | [references/instructions/windows-subprocess-cdp.md](references/instructions/windows-subprocess-cdp.md) |

## Done Criteria

- MCP または CDP 設定が完了している
- 対象ページまで安定して到達できる
- 目的の操作が完了している
- 成功判定を toast だけに頼らず、DOM / URL / API read / screenshot / status artifact のいずれかで確認している
- modal / file chooser / iframe / CDP context のどこで詰まるか説明できる
- 一括処理が必要なら MCP から CLI / API helper へ切り替える判断ができている
