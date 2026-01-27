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
