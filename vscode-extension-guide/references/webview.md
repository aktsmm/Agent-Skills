# Webview Implementation

The basic API (`createWebviewPanel`, `postMessage` / `onDidReceiveMessage`, `acquireVsCodeApi`, `getState` / `setState`) follows the official [Webview API guide](https://code.visualstudio.com/api/extension-guides/webview). This file keeps only non-obvious rules and gotchas.

## Core Rules

- Prefer native UI (TreeView, QuickPick, etc.) when it suffices; webviews are resource heavy.
- Enable `enableScripts` only when needed. Limit `localResourceRoots` to the folders actually loaded (for example `media/`, `images/`); never pass the whole `extensionUri`.
- Start the CSP from `default-src 'none'` and open only `${webview.cspSource}` and a per-render script nonce. Generate the nonce with a cryptographic RNG (for example `crypto.randomBytes(16).toString("base64")`), not `Math.random`.
- Resolve local files with `webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, ...))`.
- Call `acquireVsCodeApi()` once per session, keep it inside an IIFE/module scope, and never leak it to the global scope.
- Prefer `getState` / `setState` for view state. `retainContextWhenHidden: true` has high memory overhead; use it only for complex UI that cannot be restored. Restore across restarts with `registerWebviewPanelSerializer` plus the `onWebviewPanel:<viewType>` activation event.
- Reassigning `webview.html` resets script state; send incremental updates with `postMessage`.
- Escape every workspace-derived value (file contents, paths, settings) before embedding it in HTML.
- Use `var(--vscode-*)` theme variables and check `body.vscode-high-contrast` as well as light/dark.
- For a sidebar webview, implement `WebviewViewProvider` and declare the view with `"type": "webview"` under `contributes.views`.

### Embed initial data safely (no document.write)

```html
<script id="initial-data" type="application/json">
  ${serializeForWebview(initialData)}
</script>
<script nonce="${nonce}">
  (function () {
    var vscode = acquireVsCodeApi();
    var initialData = {};
    try {
      var el = document.getElementById("initial-data");
      if (el && el.textContent) initialData = JSON.parse(el.textContent) || {};
    } catch (e) {
      initialData = {};
    }
    // ... use initialData ...
  })();
</script>
```

```typescript
function serializeForWebview(value: unknown): string {
  const json = JSON.stringify(value ?? null) ?? "null";
  return json
    .replace(/</g, "\\u003c")
    .replace(/\u2028/g, "\\u2028")
    .replace(/\u2029/g, "\\u2029");
}
```

- Avoid Base64 + `document.write`; inject JSON as text and parse.
- Escape `<`, U+2028/2029 before embedding to keep the script tag valid.
- Keep the CSP nonce on the executable script only.

## Edit Form Baselines

When an edit form shows values derived from current settings defaults, capture a
normalized baseline **when edit starts** and diff against that frozen baseline
on submit. Do not recompute the original side of the diff from current defaults,
or unchanged fields can become false updates if settings change mid-edit.

For persisted edits, send that baseline to the host and compare it with current
data before confirmation and again inside the storage transaction. A browser
save lock cannot protect other windows. Reject stale edits without restoring
revoked consent; recheck cancellation and trust at commit. Compare settings only
when unrelated history updates should not conflict; revision-based callers may
intentionally use a stricter whole-store check. Reset must load a fresh baseline
and disclose that unsaved input is discarded.

```javascript
let editingTaskSnapshot = null;
let editingTaskNormalizedSnapshot = null;

function normalizeTaskForDiff(task, currentDefaults) {
  const source = task || {};
  return {
    jitterSeconds:
      source.jitterSeconds != null
        ? Number(source.jitterSeconds)
        : currentDefaults.jitterSeconds,
    autoMode: source.autoMode === true,
    chatSession:
      source.chatSession === "new" || source.chatSession === "continue"
        ? source.chatSession
        : "default",
  };
}

function beginEdit(task, currentDefaults) {
  editingTaskSnapshot = { ...task };
  editingTaskNormalizedSnapshot = normalizeTaskForDiff(task, currentDefaults);
}

function buildUpdateData(formData, currentDefaults) {
  const current = normalizeTaskForDiff(formData, currentDefaults);
  const original =
    editingTaskNormalizedSnapshot ||
    normalizeTaskForDiff(editingTaskSnapshot, currentDefaults);
  const diff = {};

  for (const key of Object.keys(current)) {
    if (current[key] !== original[key]) {
      diff[key] = formData[key];
    }
  }

  return diff;
}
```

This matters when you correctly keep create-form defaults reactive but avoid
overwriting active edit forms during `updateDefaults` / configuration-change
events.

Keep persistence and presentation outcomes separate. After a confirmed save,
a failed refresh or notification must retain the saved ID/success and return a
sanitized warning, not an apparent save failure that invites duplicate retries.
Actual write failures and standalone refresh failures remain errors. Persist a
new folder approval with the successful task save, not as an earlier side effect.
Test revoked consent during a queued save, changes during confirmation, stale
form/reset, unrelated updates and presenter failure against real fixture storage.

## Fallback Patterns

### Keyboard Tabs

Use one tab stop: the selected tab has `tabindex="0"`, others `-1`, with matching `aria-selected` and panel associations in both initial HTML and every switch. Left/Right wrap; Home/End select endpoints. Reuse the click switch path and retain native Enter/Space activation to avoid double handling. Ignore modifiers, composition and non-tab fields; reject missing targets before hiding the current panel. Move focus off hidden panels or deactivated tab buttons, but do not steal unrelated focus.

Test actual handlers and registration with real key presses, active element, selected state and visible panel assertions. An extracted production-code browser fixture can verify those interactions; label it as partial evidence, not full VS Code host or screen-reader verification. Remove its owned server and temporary files afterward.

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

### Language Model List Fallback

`vscode.lm.selectChatModels()` can return an empty array or throw. Reconcile both
states; display fallbacks must not silently replace an explicitly selected
execution model/provider. Do not feature-detect a stable API already covered by
`engines.vscode`; separately gate newer configuration capabilities.

- Derive option controls and preview notices from the selected model's current schema and host support, not a global experiment flag. If each option can inherit shared settings, omit a redundant enable checkbox unless OFF has a distinct required meaning.
- Preserve enum values and numeric types. Migrate only schema-confirmed equivalents; do not infer speed or compound modes from effort alone. Explicit new options replace inherited legacy fields, but reject explicitly conflicting old/new inputs. Retain invalid or future values until explicit repair.
- Use one reconciliation path for empty catalogs, unavailable saved selections, refresh failures and normal changes. Remove stale editable choices/notices without deleting saved identity or overrides; restore typed values when advertised choices return.
- Pass selected variant identity and options through the resolver before rendering; do not lose the chosen value by redrawing from an empty selection or inheritance default.
- Before replacing or hiding controls, move focus only when the active element is inside them, to a stable visible control. Cover both schema fields and legacy variant fields; never steal unrelated focus.
- Test available -> empty/unavailable -> restored transitions, typed values, selected options and actual keyboard focus with production handlers. Extracted-code real-DOM fixtures are component evidence, not full host or screen-reader proof.

### Path Consistency

When one list mixes local and global resources, store each path relative to its own root with `/` separators (`path.relative(root, file.fsPath).replace(/\\/g, "/")`); do not mix relative and absolute `fsPath` values.

## Reliable Webview Communication Pattern

Wrap the webview script in an IIFE and post a single `webviewReady` message as its **last** statement. The host sends initial data only after receiving it.

```javascript
(function () {
  const vscode = acquireVsCodeApi();
  window.addEventListener("message", (event) => {
    if (event.data.type === "updateData") renderData(event.data.data);
  });
  renderUI();
  vscode.postMessage({ type: "webviewReady" }); // last
})();
```

```typescript
panel.webview.onDidReceiveMessage((message) => {
  if (message.type === "webviewReady") {
    panel.webview.postMessage({ type: "updateAgents", agents: cachedAgents });
  }
});
```

Avoid ping/ACK/retry handshakes with timers: they add race conditions and fallbacks mask the real failure (usually a script error or CSP block).

### Debugging Tips

1. Host and webview logs are separate: extension host logs go to the Debug Console / Output Channel; webview logs appear in **Developer: Toggle Developer Tools** (use **Developer: Open Webview Developer Tools** only for webviews with `enableFindWidget`). Select the active frame in the console to evaluate in the webview context.
2. Post `{ type: "scriptStarted" }` right after `acquireVsCodeApi()`. If the host never receives it, check CSP/nonce and syntax errors.
3. Look for CSP violation errors in the webview console.

## Inline Script Gotchas

A webview runs a modern Chromium, so arrow functions, `const`/`let` and default parameters work. Breakage usually comes from writing the script inside a TypeScript template literal:

- JS template literals or `${...}` inside the inline script are expanded by the outer TypeScript template.
- TypeScript syntax (`as HTMLElement`, type annotations) is not compiled there and becomes a SyntaxError.
- Backslashes are consumed (see below).

Moving the script to an external file (below) removes all three classes of bugs.

### Initial render without "Loading..."

When data is already available at render time, embed it (via the JSON block above or rendered options) instead of hard-coding a `Loading...` placeholder that waits for a message.

### data-action + delegation

Re-rendering with `innerHTML` drops listeners attached to old nodes. Render `data-action` / `data-id` attributes and register one delegated listener:

```javascript
// ✅ Good: render attributes, delegate once
function renderTasks(tasks) {
  return tasks
    .map(function (task) {
      var id = escapeAttr(task.id || "");
      return '<button data-action="run" data-id="' + id + '">Run</button>';
    })
    .join("");
}

document.addEventListener("click", function (e) {
  var target = e.target;
  var host =
    target && typeof target.closest === "function"
      ? target.closest("[data-action]")
      : null;
  if (!host) return;
  var action = host.getAttribute("data-action");
  var id = host.getAttribute("data-id");
  if (!action || !id) return;
  if (action === "run") window.runTask(id);
  if (action === "edit") window.editTask(id);
  // ... other actions ...
});
```

- ❌ `script-src 'nonce-...'` は `onclick="..."` などのインラインイベント属性を許可しない。nonce 付き script 内で `addEventListener` を登録し、実機クリックと Webview の DevTools の CSP エラーを確認する。ソース検査だけで動作確認済みとしない。
- ✅ 未信頼の Markdown リンクは Webview からの URL を信用せず、Extension Host 側でスキームを許可リスト照合し、相対パスを信頼できる配布元 URL に解決してから `vscode.env.openExternal` で開く。
- ✅ 属性は必ず escape し、委譲で処理する。

### ビルド後 HTML の健全性チェック

- ビルド時に `debug-webview.html` を出力し、実ファイルをブラウザ/VS Codeで開いて SyntaxError を確認する。
- DevTools の Console を確認し、CSP/quote崩れ/`document.write` などのエラーを検知する。
- タブ切り替え・プルダウンなど主要動作を1回ずつ手動で触り、ログにエラーが出ないか見る。

## 正規表現リテラルの二重エスケープ

テンプレートリテラル内で正規表現を記述する際、バックスラッシュが消える問題があります：

```typescript
// ❌ Bad: Backslash gets stripped in template literal
const html = `<script>var everyN = /^\*\/(\d+)$/.exec(minute);</script>`;
// Result in browser: /^*/(\d+)$/ → SyntaxError: Nothing to repeat

// ✅ Good: Double-escape backslashes
const html = `<script>var everyN = /^\\*\\/(\\d+)$/.exec(minute);</script>`;
// Result in browser: /^\*\/(\d+)$/ → Works correctly
```

`\d` `\s` `\*` `\/` などすべて二重化する。症状は Console の `Invalid regular expression: /^*/: Nothing to repeat`。ビルド出力 (`out/extension.js`) で該当の正規表現を確認する。

## 設定変更の即時反映

`onDidChangeConfiguration` で `e.affectsConfiguration("<ext>.<key>")` を判定し、表示言語の変更はパネルを dispose → 再作成、パス系設定の変更はキャッシュを破棄して再取得する。watcher は `context.subscriptions` に登録する。

## Moving Inline JS to an External File (Recommended)

Large inline `<script>` blocks inside TypeScript template literals are hard to edit,
cause merge conflicts, and invite the inline-script bugs above. Keep only the HTML skeleton and initial-data injection in TypeScript and put all logic in `media/webview.js`.

```typescript
// myWebview.ts – only the skeleton remains in TypeScript
const scriptUri = webview.asWebviewUri(
  vscode.Uri.joinPath(extensionUri, "media", "webview.js"),
);

return `<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="Content-Security-Policy"
        content="default-src 'none';
                 style-src ${webview.cspSource};
                 script-src 'nonce-${nonce}';
                 img-src ${webview.cspSource};
                 font-src ${webview.cspSource};">
</head>
<body>
  <script id="initial-data"
          type="application/json">${serializeForWebview(data)}</script>
  <script nonce="${nonce}" src="${scriptUri}"></script>
</body>
</html>`;
```

`media/webview.js` reads `#initial-data` exactly as in [Embed initial data safely](#embed-initial-data-safely-no-documentwrite). Add `'unsafe-inline'` to `style-src` only if inline `style=` attributes are unavoidable.

## Prompting Reload After Extension Update

Because `activationEvents: ["onStartupFinished"]` fires only once per VS Code
startup, users who update the extension **without restarting VS Code** will keep
running stale code. Show a "Reload Now" notification when the version changes.

```typescript
// extension.ts
const LAST_VERSION_KEY = "lastKnownVersion";

export function activate(context: vscode.ExtensionContext): void {
  const currentVersion =
    (context.extension.packageJSON as { version?: string }).version ?? "0.0.0";
  const lastVersion = context.globalState.get<string>(LAST_VERSION_KEY);

  if (lastVersion && lastVersion !== currentVersion) {
    void vscode.window
      .showInformationMessage(
        `Extension updated to v${currentVersion}. Reload to activate.`,
        "Reload Now",
      )
      .then((choice) => {
        if (choice === "Reload Now") {
          void vscode.commands.executeCommand("workbench.action.reloadWindow");
        }
      });
  }
  void context.globalState.update(LAST_VERSION_KEY, currentVersion);
}
```

> **Why not `vscode.env.reload()`?** It reloads immediately without user consent.
> The pattern above lets users finish their current work first.
