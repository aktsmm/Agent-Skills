---
name: browser-max-automation
description: Browser automation using Playwright MCP, CDP, and direct WebSocket CDP for web testing, UI verification, and form automation. Use when navigating websites, clicking elements, filling forms, taking screenshots, testing web applications, reusing an existing browser session, or troubleshooting CDP / iframe / modal / file chooser / passkey (WebAuthn) issues.
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

- **API / CLI を先に検討**: 公式 API（YouTube Data API、Microsoft Graph、GitHub API 等）や CLI で read/write が完結するならそちらを優先し、UI が脆い兆候（native file chooser / shadow DOM / 多段ウィザード / レンダラーを止める modal）で固執せず切り替える（例: YouTube Studio UI → `captions.insert`）
- API / CLI だけで完結するなら、該当 domain skill / script を使う
- PowerPoint / Loop / Dynamics 365 の expense entry 画面など専用 skill がある UI は、該当 skill の操作ルールを優先する
- 認証情報、秘密情報、MFA 応答をチャットで受け取らない。必要な入力はブラウザ上でユーザーに処理してもらう
- 例外: 対象サイトが passkey / FIDO2 / WebAuthn 対応なら、CDP 仮想認証機で完全無人化できる。優先順位は **passkey (仮想認証機) > メール OTP > SMS > 物理キー / 生体**。詳細は [references/instructions/webauthn-virtual-authenticator.md](references/instructions/webauthn-virtual-authenticator.md) を参照する

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

API と DOM の状態が一時的にずれるケースがある。API が stale / capture failure を返しても、画面上の cell / row の `aria-label` や status text が進展した状態を示しているなら DOM も正本候補として扱う。API 単独で「未完了」と断定しない。

## Decision Patterns

| Situation | Action |
| --- | --- |
| Flow or selectors are still unknown | Use MCP interactively |
| Flow is stable and must run for many items | Switch to a CLI/API helper |
| Snapshot returns a ref | Use normal click/type |
| Element is visible but has no ref | Confirm visually, then use evaluate or the relevant UI fallback |
| Element is not visible | Wait or reload before forcing interaction |
| Read-only tabular extraction | Keep navigation evidence, then return compact JSON from DOM evaluation |

### unsaved editor / draft タブを壊さない

未保存 form を持つ editor / SPA タブに別 URL を踏ませると `beforeunload` dialog で upload や遷移が崩れる。既存タブは再利用し、新規作業は別タブで開く。`dialog.accept()` / `page.reload()` / API トリガー目的の reload で dirty を踏み越さない。詳細と Qiita / CMS 例は [references/instructions/unsaved-form-tabs.md](references/instructions/unsaved-form-tabs.md) を参照する。

Azure Portal iframe / OOPIF / trusted event の注意は [references/instructions/azure-portal.md](references/instructions/azure-portal.md) を参照する。
Angular Material / `mat-select` / `cdk-overlay` / disabled save の注意は [references/instructions/angular-material.md](references/instructions/angular-material.md) を参照する。

iframe、force click、file chooser、hidden input、evaluate+fetchは [UI Fallbacks](references/instructions/ui-fallbacks.md) を参照する。`force: true` は要素の実在と可視性を確認した後の最終手段とする。

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
| WebAuthn virtual authenticator / passkey | [references/instructions/webauthn-virtual-authenticator.md](references/instructions/webauthn-virtual-authenticator.md) |
| CDP recovery and context selection | [references/instructions/cdp-recovery-and-context.md](references/instructions/cdp-recovery-and-context.md) |
| Azure Portal iframe / OOPIF | [references/instructions/azure-portal.md](references/instructions/azure-portal.md) |
| Angular Material forms | [references/instructions/angular-material.md](references/instructions/angular-material.md) |
| Hidden upload, evaluate+fetch, UI fallback | [references/instructions/ui-fallbacks.md](references/instructions/ui-fallbacks.md) |
| Unsaved editor / draft tab safety | [references/instructions/unsaved-form-tabs.md](references/instructions/unsaved-form-tabs.md) |
| Windows subprocess stability | [references/instructions/windows-subprocess-cdp.md](references/instructions/windows-subprocess-cdp.md) |

## Done Criteria

- MCP または CDP 設定が完了している
- 対象ページまで安定して到達できる
- 目的の操作が完了している
- 成功判定を toast だけに頼らず、DOM / URL / API read / screenshot / status artifact のいずれかで確認している
- modal / file chooser / iframe / CDP context のどこで詰まるか説明できる
- 一括処理が必要なら MCP から CLI / API helper へ切り替える判断ができている
