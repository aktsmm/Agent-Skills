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

Browser automation via Playwright MCP.

## When to Use

- ブラウザ自動化、UI 確認、フォーム操作、スクリーンショット取得
- MCP で手順を確立してから Python で一括実行したいとき
- 既存ブラウザのログイン状態を CDP 経由で使いたいとき
- Playwright MCP / `connect_over_cdp()` が不安定で、raw CDP WebSocket に切り替えたいとき
- モーダルや file chooser など、通常クリックが壊れやすい UI を扱うとき

## Choose Mode First

| モード             | 向く場面                                               | メリット                       | 注意点                     |
| ------------------ | ------------------------------------------------------ | ------------------------------ | -------------------------- |
| 新規ブラウザ       | まず安定して動かしたい                                 | 設定が簡単                     | 既存ログイン状態は使えない |
| 既存ブラウザ (CDP) | 普段のブラウザ状態をそのまま使いたい                   | ログイン済み状態を再利用できる | デバッグモード起動が必要   |
| 直接 CDP WebSocket | Playwright CDP が不安定、または MCP と競合させたくない | 低レベル操作で安定しやすい     | CDP コマンドを自前管理する |

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

#### 既存CDPを再利用する場合

既にデバッグポート付きブラウザが起動しているなら、毎回再起動する必要はない。ただし、**ポートが開いていること** と **目的のプロファイル/ログイン状態であること** は別問題として確認する。

```powershell
# 9222 を握っているプロセスを確認
$conn = Get-NetTCPConnection -LocalPort 9222 -ErrorAction SilentlyContinue | Select-Object -First 1
if ($conn) {
  Get-CimInstance Win32_Process -Filter "ProcessId=$($conn.OwningProcess)" |
    Select-Object ProcessId, Name, CommandLine
}
```

- `--profile-directory` や `--user-data-dir` を見て、意図したプロファイルか確認する
- 既存CDPが別プロファイルなら、既存ブラウザを落とす前に別ポートで目的プロファイルを起動できるか検討する
- 自動化スクリプト側は `http://localhost:9222` 固定にせず、検出・起動したCDP URLを引数で受け取れるようにする

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

### `browser_run_code` / `page.evaluate` の速度 vs 証跡

`browser_run_code` + `page.evaluate(JS)` で直接 DOM 操作すると、`browser_snapshot` → `browser_click` の MCP 標準フローより速い。ただし snapshot が出ないため、操作の証跡が残りにくい。

| 方式                          | 速度                     | 証跡              | 使い分け                         |
| ----------------------------- | ------------------------ | ----------------- | -------------------------------- |
| MCP 標準 (snapshot → click)   | 遅い（snapshot 数秒/回） | YAML + ref で明確 | 初回探索、デバッグ、重要操作     |
| `browser_run_code` + evaluate | 速い                     | テキスト返却のみ  | 手順確立済みの定型操作、大量入力 |

判断基準: **発注確定など不可逆操作の直前・直後は `browser_take_screenshot` で証跡を残し、中間のフォーム入力は evaluate で高速化**するのが実用的なバランス。

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

### CDP 断線復帰

ブラウザがクラッシュ・終了した場合（`Target page, context or browser has been closed` エラー）:

1. CDP ポート確認: `Invoke-WebRequest -Uri 'http://localhost:<port>/json/version' -TimeoutSec 5` — 接続拒否ならブラウザが落ちている
2. ブラウザ再起動: 同じ `--remote-debugging-port` と `--user-data-dir` で起動する
3. CDP 起動確認: 上の確認コマンドで `Browser:` が返ること
4. MCP 再接続: `browser_close`（古いセッション破棄）→ `browser_navigate` で新しいページを開く
5. 認証が必要なサイトは、MCP を `browser_close` してから Python ログインスクリプトを実行し、完了後に MCP で再接続する

### CDP context / page 選択

`connect_over_cdp()` では、複数プロファイルや複数 browser context が見えることがある。`browser.contexts[0]` や `context.pages[0]` 固定は、別アカウント・未ログイン・別タブを掴む原因になる。

安全な選び方:

1. すべての `browser.contexts` を走査する
2. 各 context の既存 page を、目的ドメインや管理画面URLを優先して並べる
3. 候補 page ごとにログイン/権限/目的画面への到達を確認する preflight を実行する
4. preflight が通った context/page だけを以後の操作に使う
5. 全候補が失敗したら、失敗したURL・title・理由をJSONに残して停止する

```python
async def select_ready_page(browser, preflight):
  failures = []
  for context_index, context in enumerate(browser.contexts):
    pages = list(context.pages) or [await context.new_page()]
    for page_index, page in enumerate(pages):
      result = await preflight(page)
      result.update({"context_index": context_index, "page_index": page_index})
      if result.get("ok"):
        return context, page, result
      failures.append(result)
  raise RuntimeError(f"No usable browser context found: {failures[:5]}")
```

preflight では最低限、以下を確認する:

- 目的ドメインに到達できている
- ログイン画面へリダイレクトされていない
- 操作に必要な管理画面・権限リンク・APIが見えている

### 破綻しやすい場面

- modal overlay が snapshot に出ない
- file chooser が残って後続操作を塞ぐ
- CDP 二重接続で入力先が混線する
- CDP の別 context/page を使い、未ログイン画面や別アカウントを操作してしまう
- 「見えているがクリックできない」状態を無理に通常 click で押し切る

## Done Criteria

- MCP または CDP 設定が完了している
- 対象ページまで安定して到達できる
- 目的の操作が完了している
- modal / file chooser / iframe のどこで詰まるか説明できる
- 一括処理が必要なら MCP から CLI へ切り替える判断ができている
