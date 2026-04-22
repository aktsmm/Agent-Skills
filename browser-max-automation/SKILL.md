---
name: browser-max-automation
description: Browser automation using Playwright MCP for web testing, UI verification, and form automation. Use when navigating websites, clicking elements, filling forms, taking screenshots, or testing web applications. Supports iframe operations, complex JavaScript execution, MCP-to-CLI workflow switching (MCP for prototyping, Python CLI for bulk execution), CDP exclusive control, modal dialog workarounds, and file chooser handling.
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Browser Max Automation

Browser automation via Playwright MCP.

## When to Use

- ブラウザ自動化、UI 確認、フォーム操作、スクリーンショット取得
- MCP で手順を確立してから Python で一括実行したいとき
- 既存ブラウザのログイン状態を CDP 経由で使いたいとき
- モーダルや file chooser など、通常クリックが壊れやすい UI を扱うとき

## Choose Mode First

| モード | 向く場面 | メリット | 注意点 |
| --- | --- | --- | --- |
| 新規ブラウザ | まず安定して動かしたい | 設定が簡単 | 既存ログイン状態は使えない |
| 既存ブラウザ (CDP) | 普段のブラウザ状態をそのまま使いたい | ログイン済み状態を再利用できる | デバッグモード起動が必要 |

### 新規ブラウザモード

`mcp.json` 例:

```json
{
  "servers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--browser", "msedge"],
      "type": "stdio"
    }
  }
}
```

### 既存ブラウザ (CDP)

1. 対象ブラウザを全部閉じる
2. デバッグポート付きで起動する
3. `mcp.json` で `--cdp-endpoint http://localhost:9222` を指定する
4. VS Code をリロードする

```powershell
Start-Process "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" -ArgumentList "--remote-debugging-port=9222"
```

## Quick Reference

| Command | Purpose |
| --- | --- |
| `browser_navigate` | URL を開く |
| `browser_snapshot` | 要素 ref を取る |
| `browser_click` | ref でクリック |
| `browser_type` | テキスト入力 |
| `browser_take_screenshot` | 画面確認 |
| `browser_wait_for` | 表示待機 |
| `browser_evaluate` | DOM 直接操作 |
| `browser_file_upload` | file chooser 対応 |

## Core Loop

```text
1. browser_navigate(url)
2. browser_snapshot で ref を取る
3. browser_click / browser_type で操作する
4. browser_snapshot or screenshot で結果確認する
```

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

### iframe と force click

- iframe が多段なら `contentFrame()` を順に辿る
- SVG オーバーレイなどで塞がれているだけなら `force: true` を検討する
- ただし `force: true` は最後の手段で、まず要素の実在確認と可視確認を優先する

### file chooser が残ったとき

- `browser_file_upload(paths=[])` で空送信して閉じる
- ダメなら別ページへ移動する
- CDP 競合が疑わしいなら Python プロセスや MCP 接続を整理する

## Safety Rules

### CDP 排他制御

MCP Playwright と Python スクリプトは **同じ CDP ポートへ同時接続しない**。

| ルール | 内容 |
| --- | --- |
| 同時接続禁止 | MCP と Python を同じ CDP に同時接続しない |
| MCP 切断優先 | Python 実行前に MCP 側を閉じる |
| プロセス確認 | 実行前にゾンビ Python を確認する |
| 標準フロー | MCP で手順確立 → 切断 → Python 単独実行 → 完了後に検証 |

### 破綻しやすい場面

- modal overlay が snapshot に出ない
- file chooser が残って後続操作を塞ぐ
- CDP 二重接続で入力先が混線する
- 「見えているがクリックできない」状態を無理に通常 click で押し切る

## Done Criteria

- MCP または CDP 設定が完了している
- 対象ページまで安定して到達できる
- 目的の操作が完了している
- modal / file chooser / iframe のどこで詰まるか説明できる
- 一括処理が必要なら MCP から CLI へ切り替える判断ができている
