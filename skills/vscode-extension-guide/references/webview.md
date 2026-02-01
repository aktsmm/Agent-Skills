# Webview Implementation

Create rich HTML-based UI panels in VS Code.

## Basic Webview Panel

```typescript
import * as vscode from "vscode";

export function createWebviewPanel(context: vscode.ExtensionContext) {
  const panel = vscode.window.createWebviewPanel(
    "myWebview", // Identifier
    "My Webview", // Title
    vscode.ViewColumn.One, // Editor column
    {
      enableScripts: true, // Enable JavaScript
      retainContextWhenHidden: true, // Keep state when hidden
      localResourceRoots: [
        // Allowed local resources
        vscode.Uri.joinPath(context.extensionUri, "media"),
      ],
    },
  );

  panel.webview.html = getWebviewContent(panel.webview, context.extensionUri);

  return panel;
}
```

## HTML Content

```typescript
function getWebviewContent(
  webview: vscode.Webview,
  extensionUri: vscode.Uri,
): string {
  // Get URI for local resources
  const styleUri = webview.asWebviewUri(
    vscode.Uri.joinPath(extensionUri, "media", "style.css"),
  );
  const scriptUri = webview.asWebviewUri(
    vscode.Uri.joinPath(extensionUri, "media", "main.js"),
  );

  // CSP nonce for security
  const nonce = getNonce();

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" 
        content="default-src 'none'; style-src ${webview.cspSource}; script-src 'nonce-${nonce}';">
  <link href="${styleUri}" rel="stylesheet">
</head>
<body>
  <h1>Hello Webview!</h1>
  <button id="btn">Click Me</button>
  <script nonce="${nonce}" src="${scriptUri}"></script>
</body>
</html>`;
}

function getNonce(): string {
  let text = "";
  const chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  for (let i = 0; i < 32; i++) {
    text += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return text;
}
```

## Message Passing

### Extension → Webview

```typescript
// In extension
panel.webview.postMessage({ command: "update", data: { count: 42 } });
```

```javascript
// In webview (media/main.js)
window.addEventListener("message", (event) => {
  const message = event.data;
  if (message.command === "update") {
    console.log("Count:", message.data.count);
  }
});
```

### Webview → Extension

```javascript
// In webview
const vscode = acquireVsCodeApi();

document.getElementById("btn").addEventListener("click", () => {
  vscode.postMessage({ command: "buttonClicked", text: "Hello!" });
});
```

```typescript
// In extension
panel.webview.onDidReceiveMessage(
  (message) => {
    switch (message.command) {
      case "buttonClicked":
        vscode.window.showInformationMessage(message.text);
        return;
    }
  },
  undefined,
  context.subscriptions,
);
```

## State Persistence

```javascript
// In webview - save state
const vscode = acquireVsCodeApi();
vscode.setState({ count: 5 });

// Restore state
const state = vscode.getState();
if (state) {
  console.log("Restored count:", state.count);
}
```

## VS Code Theme Integration

Use CSS variables for consistent theming:

```css
/* media/style.css */
body {
  font-family: var(--vscode-font-family);
  font-size: var(--vscode-font-size);
  color: var(--vscode-foreground);
  background-color: var(--vscode-editor-background);
}

button {
  background-color: var(--vscode-button-background);
  color: var(--vscode-button-foreground);
  border: none;
  padding: 8px 16px;
  cursor: pointer;
}

button:hover {
  background-color: var(--vscode-button-hoverBackground);
}
```

## Sidebar Webview (WebviewViewProvider)

For webviews in the sidebar instead of editor panels:

```typescript
class MyWebviewProvider implements vscode.WebviewViewProvider {
  resolveWebviewView(webviewView: vscode.WebviewView) {
    webviewView.webview.options = { enableScripts: true };
    webviewView.webview.html = getWebviewContent();
  }
}

// Register in extension.ts
vscode.window.registerWebviewViewProvider(
  "myExtSidebarView",
  new MyWebviewProvider(),
);
```

```json
"contributes": {
  "views": {
    "explorer": [{
      "type": "webview",
      "id": "myExtSidebarView",
      "name": "My Webview"
    }]
  }
}
```

## Fallback Patterns

### Promise-based Callback Fallback

When using Promise-based callbacks (e.g., `resolveCreate`), always provide a fallback mechanism:

```typescript
// ❌ Bad: Single callback dependency
case "createTask": {
  if (!resolveCreate) {
    return; // Silent failure if callback not set
  }
  resolveCreate(data);
  break;
}

// ✅ Good: Fallback to alternative handler
case "createTask": {
  const result = buildResult(data);
  if (resolveCreate) {
    resolveCreate(result);
    resolveCreate = undefined;
  } else if (onAction) {
    // Fallback to action handler
    onAction({ action: "create", data: result });
  }
  break;
}
```

### VS Code Internal API Fallback

When using internal/unstable APIs (`vscode.lm`, `vscode.chat`), always implement fallback:

```typescript
// ✅ Good: API availability check + fallback
static async getAvailableModels(): Promise<Model[]> {
  const models: Model[] = [{ id: "", name: "Default" }];

  try {
    if (typeof vscode.lm !== "undefined" && "selectChatModels" in vscode.lm) {
      const available = await (vscode.lm as any).selectChatModels({});
      
      // Null check for API result
      if (available && Array.isArray(available)) {
        for (const model of available) {
          models.push({
            id: model.id || model.family,
            name: model.name || model.family || model.id,
          });
        }
      }
    }
  } catch (error) {
    console.log("API not available, using fallback", error);
  }

  // Return fallback if API returned nothing useful
  if (models.length <= 1) {
    return getFallbackModels();
  }

  return models;
}
```

### Path Consistency

When handling both local and global paths, use consistent format:

```typescript
// ❌ Bad: Mixed path formats
templates.push({
  source: "local",
  path: relativePath,  // Relative
});
templates.push({
  source: "global",
  path: file.fsPath,   // Absolute - inconsistent!
});

// ✅ Good: Consistent relative paths
templates.push({
  source: "local",
  path: path.relative(workspaceRoot, file.fsPath).replace(/\\/g, "/"),
});
templates.push({
  source: "global",
  path: path.relative(globalRoot, file.fsPath).replace(/\\/g, "/"),
});
```


## Reliable Webview Communication Pattern

### Recommended Pattern (Simple & Reliable)

Wrap the entire webview script in an IIFE and send webviewReady at the end:

`	ypescript
function getWebviewContent(): string {
  return <!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy"
        content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
</head>
<body>
  <div id="app"></div>
  
  <script nonce="${nonce}">
    (function() {
      const vscode = acquireVsCodeApi();
      
      // Initialize UI
      // ... DOM setup ...
      
      // Handle messages from extension
      window.addEventListener('message', event => {
        const message = event.data;
        switch (message.type) {
          case 'updateData':
            renderData(message.data);
            break;
        }
      });
      
      // Initial render
      renderUI();
      
      // Notify extension that webview is ready (LAST!)
      vscode.postMessage({ type: 'webviewReady' });
    })();
  </script>
</body>
</html>;
}
`

### Extension Side Handler

`	ypescript
panel.webview.onDidReceiveMessage(message => {
  switch (message.type) {
    case 'webviewReady':
      console.log('[Extension] Webview reported ready');
      webviewReady = true;
      // Send initial data AFTER webview is ready
      panel.webview.postMessage({
        type: 'updateAgents',
        agents: cachedAgents,
      });
      panel.webview.postMessage({
        type: 'updateModels', 
        models: cachedModels,
      });
      break;
  }
});
`

### ❌ Anti-Pattern: Complex Handshakes

Avoid adding complexity like ping/ACK/retry/fallback mechanisms:

`	ypescript
// ❌ Bad: Overly complex handshake
let webviewReadyAcked = false;
let webviewReadyRetryTimer = null;
let webviewReadyAttempts = 0;

function startWebviewReadyHandshake() {
  sendWebviewReady();
  webviewReadyRetryTimer = setInterval(() => {
    if (webviewReadyAcked || webviewReadyAttempts >= 12) {
      clearInterval(webviewReadyRetryTimer);
      return;
    }
    sendWebviewReady(); // Retry
  }, 500);
}

// Host pings webview, webview responds, host ACKs...
// This adds complexity and often fails in unexpected ways
`

**Why it fails:**
- More moving parts = more failure modes
- Race conditions between ping/ACK/retry timers
- Fallback mechanisms mask the real problem

**Simple pattern is best:** One webviewReady message at script end, host waits for it.

### Debugging Tips

1. **Host logs vs Webview logs are separate**
   - Extension host: console.log() appears in Debug Console
   - Webview: console.log() appears in Webview Developer Tools
   - Use Developer: Open Webview Developer Tools command

2. **Verify script execution via message**
   `javascript
   // First line after acquireVsCodeApi
   vscode.postMessage({ type: 'scriptStarted' });
   `
   If host receives this, script is running. If not, check CSP/nonce.

3. **Check CSP errors in Webview DevTools**
   - Open Webview Developer Tools
   - Look for CSP violation errors in Console

## Webview JavaScript Anti-Patterns

Webview内のJavaScriptは通常のブラウザ環境と異なる動作をする場合があります。以下のパターンを避けてください。

### 1. アロー関数 vs 従来関数

Webview環境では従来のfunction構文がより安全です：

```javascript
// ❌ Bad: Arrow function
btn.addEventListener('click', (e) => {
  handleClick(e);
});

// ✅ Good: Traditional function
btn.addEventListener('click', function(e) {
  handleClick(e);
});
```

### 2. nullチェック必須

`getElementById` は null を返す可能性があります。常にnullチェックを行ってください：

```javascript
// ❌ Bad: No null check
document.getElementById('my-input').value = 'xxx';

// ✅ Good: With null check
var element = document.getElementById('my-input');
if (element) element.value = 'xxx';
```

### 3. イベント委譲パターン推奨

NodeListへの直接イベント登録は失敗する可能性があります。イベント委譲を使用してください：

```javascript
// ❌ Bad: Direct event registration on NodeList
document.querySelectorAll('.btn').forEach(function(btn) {
  btn.addEventListener('click', handleClick);
});

// ✅ Good: Event delegation
document.addEventListener('click', function(e) {
  var target = e.target;
  if (target && target.classList && target.classList.contains('btn')) {
    e.preventDefault();
    handleClick(target);
  }
});
```

### 4. var を使用

互換性のため、`const` / `let` より `var` を推奨：

```javascript
// ❌ Bad: const/let
const items = [];
let count = 0;

// ✅ Good: var
var items = [];
var count = 0;
```

### 5. デフォルト引数の回避

ES6のデフォルト引数構文は避けてください：

```javascript
// ❌ Bad: Default parameters
function updateOptions(source, selectedPath = '') {
  // ...
}

// ✅ Good: Manual default
function updateOptions(source, selectedPath) {
  selectedPath = selectedPath || '';
  // ...
}
```

### 6. 初期データの埋め込み

"Loading..."をハードコードせず、初期データがある場合は直接埋め込んでください：

```typescript
// ❌ Bad: Hardcoded loading state
return `<select id="agent-select">
  <option value="">Loading...</option>
</select>`;

// ✅ Good: Embed initial data if available
const options = agents.length > 0
  ? agents.map(a => `<option value="${a.id}">${a.name}</option>`).join('')
  : '<option value="">Loading...</option>';
return `<select id="agent-select">${options}</select>`;
```

### 7. 非同期処理のフォールバック

API呼び出しには常にtry/catchとフォールバックデータを用意してください：

```typescript
// ❌ Bad: No fallback
async function getModels(): Promise<Model[]> {
  return await vscode.lm.selectChatModels({});
}

// ✅ Good: With fallback
async function getModels(): Promise<Model[]> {
  try {
    const models = await vscode.lm.selectChatModels({});
    if (models && models.length > 0) {
      return models;
    }
  } catch {
    // API may not be available
  }
  return getFallbackModels();
}
```
