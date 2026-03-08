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

- **Browser automation**, **Playwright**, **web testing**, **screenshot**
- Automating browser-based workflows or QA checks
- Verifying UI states, DOM changes, or visual regressions
- Filling forms, clicking elements, or capturing screenshots
- **MCP → CLI 切り替え**: MCP で手順確立後、Python スクリプトで一括実行
- **CDP 接続**: 既存ブラウザのログイン状態を活用した自動化
- **モーダルダイアログ対策**: snapshot で見えない要素の操作

## セットアップ（初回確認）

**このスキルを使う前に、以下を確認してください：**

### 1. ブラウザの選択

どのブラウザを使いますか？

| 選択肢 | 説明 |
|--------|------|
| **Edge** | Windows標準、企業環境向け |
| **Chrome** | 汎用、拡張機能が豊富 |

### 2. 接続モードの選択

| モード | 説明 | メリット | デメリット |
|--------|------|----------|------------|
| **新規ブラウザ** | Playwrightが新しいブラウザを起動 | 設定が簡単、安定 | 別ウィンドウが開く |
| **既存ブラウザ (CDP)** | 今開いているブラウザを操作 | 普段のブラウザをそのまま使える | 事前にデバッグモード起動が必要 |

---

### 設定A: 新規ブラウザモード（推奨）

`mcp.json` に以下を設定：

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

> `--browser` の値: `msedge` (Edge) / `chrome` (Chrome) / `firefox` (Firefox)

---

### 設定B: 既存ブラウザモード (CDP接続)

#### Step 1: ブラウザをデバッグモードで起動

**すべての対象ブラウザを閉じてから**実行：

```powershell
# Edge の場合
Start-Process "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" -ArgumentList "--remote-debugging-port=9222"

# Chrome の場合
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList "--remote-debugging-port=9222"
```

#### Step 2: mcp.json を設定

```json
{
  "servers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--cdp-endpoint", "http://localhost:9222"],
      "type": "stdio"
    }
  }
}
```

#### Step 3: VS Codeをリロード

`Ctrl+Shift+P` → `Developer: Reload Window`

#### 💡 Tips

- ショートカット作成を推奨: `msedge.exe --remote-debugging-port=9222`
- CDPポート確認: `http://localhost:9222/json/version`

---

## Quick Reference

| Command                   | Purpose                               |
| ------------------------- | ------------------------------------- |
| `browser_navigate`        | Open URL                              |
| `browser_snapshot`        | Get element refs (accessibility tree) |
| `browser_click`           | Click element by ref                  |
| `browser_type`            | Input text                            |
| `browser_take_screenshot` | Capture screen                        |
| `browser_wait_for`        | Wait for text/time                    |
| `browser_run_code`        | Execute JavaScript                    |
| `browser_evaluate`        | Run JS function (modal workaround)    |
| `browser_file_upload`     | Handle file chooser dialogs           |

## Basic Workflow

```
1. browser_navigate(url)
2. browser_snapshot → get ref
3. browser_click/type(ref)
4. browser_snapshot → verify
```

## Advanced

### iframe Operations

```javascript
async (page) => {
  const frame1 = page.locator('iframe[name="Content"]').contentFrame();
  const frame2 = frame1.locator('iframe[title="Player"]').contentFrame();
  await frame2.getByRole("radio", { name: "Option A" }).click({ force: true });
  return "Selected";
};
```

### force: true

Use when element is covered by another (e.g., SVG overlay):

```javascript
await element.click({ force: true });
```

### When browser_run_code is disabled

Use snapshot + click instead:

```
browser_snapshot → get ref → browser_click(ref)
```

## Done Criteria

- [ ] MCP server configured in `mcp.json`
- [ ] Browser navigation successful
- [ ] Target action (click/type/screenshot) completed

## MCP → CLI 切り替えパターン

ブラウザ自動化の効率的なアプローチ。**MCP で手順を確立 → Python CLI で一括実行**。

### いつ切り替えるか

| フェーズ | ツール | 目的 |
|----------|--------|------|
| **手順確立** | Playwright MCP | 1件ずつ対話的に操作し、UIフロー・セレクタ・待機時間を特定 |
| **一括実行** | Python + playwright | 確立した手順をスクリプト化し、N件を自動処理 |

### メリット

- MCP は **スクリーンショットで視覚確認** しながらセレクタを調査できる
- Python スクリプトは **エラーハンドリング・ログ・進捗管理** が容易
- 同じ CDP 接続を使うため、ログイン状態を共有可能

### 実装パターン

```python
# CDP 接続で既存ブラウザを操作
async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = context.pages[0]
    
    for item in work_items:
        await page.goto(item["url"])
        await page.wait_for_timeout(3000)
        # MCP で確立した手順をそのまま実行
        await page.get_by_role("button", name="対象ボタン").click()
        # ...
```

### 🔴 CDP 排他制御（必須）

MCP Playwright と Python スクリプトは **同一 CDP ポートに同時接続禁止**。

> **根拠**: 同時接続するとページ操作・ファイルチューザーが混線し、間違った入力が間違った対象に送信される事例あり。

| ルール | 内容 |
|--------|------|
| **同時接続禁止** | MCP と Python を同一 CDP に同時接続しない |
| **MCP 切断優先** | Python 実行前に `browser_close` で MCP を切断 |
| **プロセス確認** | 実行前に `Get-Process python*` でゾンビプロセスを確認 |
| **フロー** | MCP で手順確立 → MCP 切断 → Python 単独実行 → 完了後 MCP で検証 |

---

## モーダルダイアログの制限と対策

### 問題

一部の Web アプリ（例: モーダルオーバーレイ）では、`browser_snapshot` のアクセシビリティツリーにダイアログ要素が**表示されない**。

- `browser_snapshot` → 要素なし
- `browser_take_screenshot` → ダイアログは視覚的に表示されている
- `browser_click(ref)` → `modal intercepts pointer events` エラー

### 対策: evaluate() でDOM直接操作

```javascript
// browser_evaluate で直接操作
await page.evaluate(() => {
    // テキスト入力（React 互換）
    const textarea = document.querySelector('textarea[placeholder*="キーワード"]');
    if (textarea) {
        const setter = Object.getOwnPropertyDescriptor(
            window.HTMLTextAreaElement.prototype, 'value'
        ).set;
        setter.call(textarea, '入力テキスト');
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
    }
    // ボタンクリック
    const buttons = document.querySelectorAll('button');
    for (const btn of buttons) {
        if (btn.textContent.includes('対象ボタン名')) {
            btn.click();
            break;
        }
    }
});
```

### 判断フロー

```
browser_snapshot で ref 取得を試みる
  ├─ 取得できた → browser_click(ref) で操作
  └─ 取得できない → browser_take_screenshot で確認
      ├─ 表示されている → browser_evaluate でDOM直接操作
      └─ 表示されていない → 待機 or ページ再読込
```

---

## ファイルチューザー (File Chooser) の注意点

### ファイルチューザー残存問題

CDP 接続競合やページ遷移後に、File Chooser モーダルがブラウザに残存し後続操作をブロックすることがある。

**症状**: `browser_click` や他の操作で `Modal state: [File chooser]` エラー

**対処**:
1. `browser_file_upload(paths=[])` で空ファイルを送信してクリア
2. それでもダメなら `browser_navigate` で別ページへ移動
3. Python プロセスがゾンビ化していれば `Stop-Process` で kill

### Playwright での正しいファイルアップロード

```python
# expect_file_chooser でインターセプト
async with page.expect_file_chooser(timeout=10000) as fc_info:
    await page.get_by_role("button", name="ファイルアップロード").click()
file_chooser = await fc_info.value
await file_chooser.set_files("/path/to/file.csv")
```

## Reference

| Type       | Use Case        | Selection |
| ---------- | --------------- | --------- |
| `radio`    | Single choice   | One only  |
| `checkbox` | Multiple choice | 0 to many |
