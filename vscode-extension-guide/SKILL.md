---
name: vscode-extension-guide
description: "Guide for creating VS Code extensions and plugins from scratch through Marketplace publication. Use when developing a VS Code extension/plugin, adding commands or keybindings, building TreeView or Webview UI, publishing to Marketplace, or troubleshooting activation and packaging issues."
argument-hint: "作りたい拡張機能、追加したい機能、困っている点"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# VS Code Extension Guide

Create, develop, and publish VS Code extensions.

## When to Use

- **VS Code extension**, **extension development**, **vscode plugin**
- Creating a new VS Code extension from scratch
- Adding commands, keybindings, or settings to an extension
- Publishing to VS Code Marketplace

## Quick Start

```bash
# Scaffold new extension (recommended)
npm install -g yo generator-code
yo code

# Or minimal manual setup
mkdir my-extension && cd my-extension
npm init -y && npm install -D typescript @types/vscode
```

## Project Structure

```
my-extension/
├── package.json          # Extension manifest (CRITICAL)
├── src/extension.ts      # Entry point
├── out/                  # Compiled JS (gitignore)
├── artifacts/vsix/       # Keep local VSIX archives out of the repo root
├── images/icon.png       # 128x128 PNG for Marketplace
└── .vscodeignore         # Exclude files from VSIX
```

## Building & Packaging

```bash
npm run compile      # Build once
npm run watch        # Watch mode (F5 to launch debug)
mkdir -p artifacts/vsix
npx @vscode/vsce package --out artifacts/vsix/my-extension-1.0.0.vsix
```

Keep local `.vsix` archives under `artifacts/vsix/` instead of the repository root, and prune old local builds on a schedule so release artifacts do not pile up.

## Done Criteria

- [ ] Extension activates without errors
- [ ] All commands registered and working
- [ ] Package size < 5MB (use `.vscodeignore`)
- [ ] README.md includes Marketplace/GitHub links
- [ ] Local VSIX artifacts stored outside the repo root and pruned regularly

## Quick Troubleshooting

| Symptom               | Fix                                    |
| --------------------- | -------------------------------------- |
| Extension not loading | Add `activationEvents` to package.json |
| Command not found     | Match command ID in package.json/code  |
| Shortcut not working  | Remove `when` clause, check conflicts  |

## Reference Map

| Topic               | Reference                                                                                                           |
| ------------------- | ------------------------------------------------------------------------------------------------------------------- |
| AI Customization    | [references/ai-customization.md](references/ai-customization.md)                                                    |
| Code Review Prompts | [references/code-review-prompts.md](references/code-review-prompts.md)                                              |
| Code Samples        | [references/ai-customization.md](references/ai-customization.md) and [references/webview.md](references/webview.md) |
| TreeView            | [references/treeview.md](references/treeview.md)                                                                    |
| Webview             | [references/webview.md](references/webview.md)                                                                      |
| Testing             | [references/testing.md](references/testing.md)                                                                      |
| Publishing          | [references/publishing.md](references/publishing.md)                                                                |
| Troubleshooting     | [references/troubleshooting.md](references/troubleshooting.md)                                                      |

## Best Practices

### Extension Host 境界

- Extension Host 上で動く scanner / provider / TreeView は、同じことができるなら Node 固有の `path` / `Buffer` / 生 `fs` より VS Code API を優先する。Problems と実ビルドの環境差を避けやすい。
- 自分の拡張に同梱したリソースは、ユーザーのホーム配下や VS Code のインストール先を推測せず、`context.extensionUri` と `vscode.Uri.joinPath` など extension context から解決する。
- 他の installed extension に同梱されたリソースを読む必要がある場合も、`resources/agents|skills|prompts|instructions|hooks|mcp` の既知 root と、manifest の `chatAgents` / `chatPromptFiles` 宣言を優先して見る。built-in resource とは別の read-only resource として扱い、削除や再インストール導線を混ぜない。
- Runtime の診断ログは `console.log` に散らさず、Output Channel ベースの logger に集約する。ユーザーがログを開ける導線も command / notification / README のどこかに用意する。

### Manifest / Docs / Localization

- `package.json` の commands、views、configuration、menus を変えたら、コード上の command ID / setting key と同時に確認する。
- Marketplace 表示や設定説明をローカライズしている拡張では、`package.nls.json` と対象言語の `package.nls.*.json` を同じ変更で更新する。
- 設定の並び順や説明を変えたら README の設定表、manifest consistency test、release notes の必要有無までまとめて見る。

### Generated Sections

- `START` / `END` marker で囲む generated section は単一の SSOT として扱う。
- 重複した marker pair を見つけたら、両方を残して追記せず、内容を統合して marker pair を1つに戻す。

### 命名の一貫性

公開前にパッケージ名・設定キー・コマンド名を統一：

| 項目         | 例                            |
| ------------ | ----------------------------- |
| パッケージ名 | `copilot-scheduler`           |
| 設定キー     | `copilotScheduler.enabled`    |
| コマンドID   | `copilotScheduler.createTask` |
| ビューID     | `copilotSchedulerTasks`       |

### 通知の一元管理

```typescript
type NotificationMode = "sound" | "silentToast" | "silentStatus";

function getNotificationMode(): NotificationMode {
  const config = vscode.workspace.getConfiguration("myExtension");
  return config.get<NotificationMode>("notificationMode", "sound");
}

function notifyInfo(message: string, timeoutMs = 4000): void {
  const mode = getNotificationMode();
  switch (mode) {
    case "silentStatus":
      vscode.window.setStatusBarMessage(message, timeoutMs);
      break;
    case "silentToast":
      void vscode.window.withProgress(
        { location: vscode.ProgressLocation.Notification, title: message },
        async () => {},
      );
      break;
    default:
      void vscode.window.showInformationMessage(message);
  }
}

function notifyError(message: string, timeoutMs = 6000): void {
  const mode = getNotificationMode();
  if (mode === "silentStatus") {
    vscode.window.setStatusBarMessage(`⚠ ${message}`, timeoutMs);
    console.error(message);
    return;
  }
  void vscode.window.showErrorMessage(message);
}
```

設定で `notificationMode` を選べるようにすることで、ユーザーが通知音を制御可能。
