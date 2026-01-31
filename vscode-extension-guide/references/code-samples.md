# Code Samples & Templates

Quick reference code for VS Code extension development.

## package.json Template

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

## Keybindings

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

## Settings

**package.json:**

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

**TypeScript:**

```typescript
const config = vscode.workspace.getConfiguration("myExt");
const greeting = config.get<string>("greeting", "Hello");
```

## Quick Pick & Status Bar

```typescript
// Quick selection dialog
const selected = await vscode.window.showQuickPick(["Option A", "Option B"], {
  placeHolder: "Select an option",
});

// Non-intrusive notification (auto-hide 2s)
vscode.window.setStatusBarMessage("SilentlyContinue(check) Done!", 2000);
```

## .vscodeignore (minimize package size)

```ignore
**
!package.json
!README.md
!LICENSE
!out/**
!images/icon.png
```

## .gitignore

```ignore
out/
*.vsix
node_modules/
.vscode/
```
