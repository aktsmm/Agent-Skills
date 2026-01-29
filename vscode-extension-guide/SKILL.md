---
name: vscode-extension-guide
description: "Guide for creating VS Code extensions from scratch to Marketplace publication. Use when: (1) Creating a new VS Code extension, (2) Adding commands, keybindings, or settings to an extension, (3) Publishing to VS Code Marketplace, (4) Troubleshooting extension activation or packaging issues, (5) Building TreeView or Webview UI, (6) Setting up extension tests."
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
- Building TreeView or Webview UI

## Quick Start

```bash
# Scaffold new extension (recommended)
npm install -g yo generator-code
yo code

# Or minimal manual setup
mkdir my-extension && cd my-extension
npm init -y
npm install -D typescript @types/vscode
```

## Project Structure

```
my-extension/
├── package.json          # Extension manifest (CRITICAL)
├── src/extension.ts      # Entry point
├── out/                  # Compiled JS (gitignore)
├── images/icon.png       # 128x128 PNG for Marketplace
├── .vscodeignore         # Exclude files from VSIX
├── .gitignore            # Exclude out/, *.vsix, node_modules/
├── tsconfig.json
└── README.md
```

## package.json Essentials

```json
{
  "name": "my-extension",
  "displayName": "My Extension",
  "version": "0.1.0",
  "publisher": "your-publisher-id",
  "engines": { "vscode": "^1.80.0" },
  "activationEvents": ["onStartupFinished"],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "myExt.hello",
        "title": "Hello World",
        "category": "My Extension"
      }
    ]
  }
}
```

**Critical**: Without `activationEvents`, your extension won't load!

## Extension Entry Point

```typescript
// src/extension.ts
import * as vscode from "vscode";

export function activate(context: vscode.ExtensionContext): void {
  const disposable = vscode.commands.registerCommand("myExt.hello", () => {
    vscode.window.showInformationMessage("Hello!");
  });
  context.subscriptions.push(disposable);
}

export function deactivate(): void {}
```

## Common Patterns

### Keybindings

```json
"contributes": {
  "keybindings": [{
    "command": "myExt.hello",
    "key": "ctrl+shift+h",
    "mac": "cmd+shift+h"
  }]
}
```

**Avoid** `"when": "!inputFocus"`—it disables shortcuts in editors.

### Settings

```json
"contributes": {
  "configuration": {
    "title": "My Extension",
    "properties": {
      "myExt.greeting": {
        "type": "string",
        "default": "Hello",
        "description": "Greeting message"
      }
    }
  }
}
```

```typescript
const config = vscode.workspace.getConfiguration("myExt");
const greeting = config.get<string>("greeting", "Hello");
```

### Quick Pick & Status Bar

```typescript
// Quick selection dialog
const selected = await vscode.window.showQuickPick(["Option A", "Option B"], {
  placeHolder: "Select an option",
});

// Non-intrusive notification (auto-hide 2s)
vscode.window.setStatusBarMessage("$(check) Done!", 2000);
```

## Building

```bash
npm run compile      # Build once
npm run watch        # Watch mode
# Press F5 to launch Extension Development Host
```

## Packaging

```bash
npm install -g @vscode/vsce
npx @vscode/vsce package   # Creates .vsix
npx @vscode/vsce ls        # Preview package contents
```

**.vscodeignore** (minimize package size):

```ignore
**
!package.json
!README.md
!LICENSE
!out/**
!images/icon.png
```

**.gitignore**:

```ignore
out/
*.vsix
node_modules/
.vscode/
```

## Advanced Features

For complex UI and functionality, see the reference guides:

- **Sidebar TreeView**: [references/treeview.md](references/treeview.md) — Custom tree views in activity bar/explorer
- **Rich UI (Webview)**: [references/webview.md](references/webview.md) — HTML/CSS/JS panels with message passing
- **Testing**: [references/testing.md](references/testing.md) — @vscode/test-electron setup with Mocha
- **Marketplace Publishing**: [references/publishing.md](references/publishing.md) — PAT setup, vsce commands, versioning
- **Troubleshooting**: [references/troubleshooting.md](references/troubleshooting.md) — Common errors and fixes

## Quick Troubleshooting

| Symptom                   | Fix                                            |
| ------------------------- | ---------------------------------------------- |
| Extension not loading     | Add `activationEvents` to package.json         |
| Command not found         | Ensure command ID matches in package.json/code |
| Shortcut not working      | Remove `when` clause, check conflicts          |
| README not on Marketplace | Must be `README.md` (lowercase)                |

See [references/troubleshooting.md](references/troubleshooting.md) for full list.

## README Template for Your Extension

Include these links in your extension's README:

- **Marketplace**: `https://marketplace.visualstudio.com/items?itemName=<publisher>.<extension>`
- **GitHub Releases**: `https://github.com/<owner>/<repo>/releases`
- **Repository**: `https://github.com/<owner>/<repo>`
