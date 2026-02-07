---
name: browser-max-automation
description: Browser automation using Playwright MCP for web testing, UI verification, and form automation. Use when navigating websites, clicking elements, filling forms, taking screenshots, or testing web applications. Supports iframe operations and complex JavaScript execution.
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

## Basic Workflow

```
1. browser_navigate(url)
2. browser_snapshot → get ref
3. browser_click/type(ref)
4. browser_snapshot → verify
```

## Commands

### Navigate

```
mcp_playwright_browser_navigate
  url: "https://example.com"
```

### Snapshot

```
mcp_playwright_browser_snapshot
```

Returns accessibility tree with `ref` values for each element.

### Click

```
mcp_playwright_browser_click
  element: "Submit button"
  ref: "f2e123"
```

### Type

```
mcp_playwright_browser_type
  element: "Username"
  ref: "f2e456"
  text: "user@example.com"
  submit: true  # Press Enter
```

### Screenshot

```
mcp_playwright_browser_take_screenshot
  filename: "result.png"
```

### Wait

```
mcp_playwright_browser_wait_for
  text: "Loading complete"  # or
  time: 3
```

### Tabs

```
mcp_playwright_browser_tabs
  action: "list" | "new" | "close" | "select"
  index: 0
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

## Reference

| Type       | Use Case        | Selection |
| ---------- | --------------- | --------- |
| `radio`    | Single choice   | One only  |
| `checkbox` | Multiple choice | 0 to many |
