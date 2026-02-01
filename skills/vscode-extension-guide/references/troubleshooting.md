# Troubleshooting

Common issues and solutions for VS Code extension development.

## Extension Not Loading

| Symptom                     | Cause                      | Solution                                                         |
| --------------------------- | -------------------------- | ---------------------------------------------------------------- |
| Extension never activates   | Missing `activationEvents` | Add to package.json: `"activationEvents": ["onStartupFinished"]` |
| "Extension is not active"   | Wrong activation trigger   | Use `"*"` to always activate (dev only) or specific event        |
| Works in dev, not installed | Build output not included  | Check `.vscodeignore`, ensure `out/` is included                 |

### Debug Activation

```typescript
// Add at top of activate()
console.log("Extension activating...");
vscode.window.showInformationMessage("Extension activated!");
```

Check: **Help** → **Toggle Developer Tools** → **Console**

## Command Not Found

| Symptom                   | Cause                        | Solution                                             |
| ------------------------- | ---------------------------- | ---------------------------------------------------- |
| "command not found"       | ID mismatch                  | Ensure same ID in package.json and registerCommand() |
| Command not in palette    | Missing contributes.commands | Add command definition to package.json               |
| Command defined but fails | Extension not activated      | Check activationEvents includes the command          |

### Verify Command Registration

```typescript
// In activate()
const commands = await vscode.commands.getCommands();
console.log(
  "Registered:",
  commands.filter((c) => c.includes("myExt")),
);
```

## Keyboard Shortcuts Not Working

| Symptom               | Cause                             | Solution                           |
| --------------------- | --------------------------------- | ---------------------------------- |
| Shortcut does nothing | `when` clause too restrictive     | Remove or broaden `when` condition |
| Works sometimes       | Context-dependent `when`          | Check active editor, focus state   |
| Conflict with other   | Another extension/VS Code uses it | Use unique key combination         |

### Check for Conflicts

1. **Ctrl+K Ctrl+S** → Open Keyboard Shortcuts
2. Search for your key combination
3. Look for conflicts (multiple entries)

### Common `when` Issues

```json
// ❌ Doesn't work in editor
"when": "!inputFocus"

// ✅ Works everywhere
"when": ""  // or omit entirely

// ✅ Only in editor with text focus
"when": "editorTextFocus"
```

## Packaging Issues

| Symptom               | Cause                  | Solution                                    |
| --------------------- | ---------------------- | ------------------------------------------- |
| VSIX too large        | node_modules included  | Add to .vscodeignore                        |
| Files missing in VSIX | Over-aggressive ignore | Use `npx @vscode/vsce ls` to check          |
| Icon not showing      | Wrong path or format   | Use 128x128 PNG, check path in package.json |

### Inspect VSIX Contents

```bash
# List what will be packaged
npx @vscode/vsce ls

# Extract and inspect VSIX
unzip -l my-extension-1.0.0.vsix
```

## Publishing Errors

| Symptom             | Cause                  | Solution                                 |
| ------------------- | ---------------------- | ---------------------------------------- |
| PAT invalid         | Wrong scope or expired | Regenerate with Marketplace Manage scope |
| Publisher not found | ID mismatch            | Verify publisher ID matches exactly      |
| Version exists      | Already published      | Increment version number                 |
| README not showing  | Wrong filename case    | Must be `README.md` not `README.MD`      |

## Runtime Errors

| Symptom              | Cause                  | Solution                                            |
| -------------------- | ---------------------- | --------------------------------------------------- |
| "Cannot find module" | Dependency not bundled | Add to dependencies (not devDependencies) or bundle |
| API undefined        | Wrong VS Code version  | Check `engines.vscode` matches API used             |
| Permission denied    | Restricted API         | Check extension permissions/capabilities            |

### Check VS Code API Version

```json
// package.json - specify minimum VS Code version
"engines": {
  "vscode": "^1.80.0"
}
```

## Debug Tips

### Enable Verbose Logging

```typescript
const outputChannel = vscode.window.createOutputChannel("My Extension");
outputChannel.appendLine("Debug message");
outputChannel.show();
```

### Extension Host Logs

1. **Help** → **Toggle Developer Tools**
2. **Console** tab
3. Filter by your extension name

### Reload Without Restart

- **Ctrl+Shift+P** → "Developer: Reload Window"

## Quick Fixes Summary

```bash
# Clean rebuild
rm -rf out/ node_modules/
npm install
npm run compile

# Reset installed extension
code --uninstall-extension publisher.extension-id
npx @vscode/vsce package
code --install-extension ./extension-1.0.0.vsix

# Check what's in your VSIX
npx @vscode/vsce ls
```

## Webview 真っ白 / SyntaxError

| 症状 | 原因 | 解決策 |
|------|------|--------|
| 画面真っ白 | JavaScript SyntaxError | Webview DevTools Console でエラー確認 |
| `Invalid regular expression: /^*/` | 正規表現のバックスラッシュが消えた | テンプレート内で二重エスケープ (`\\d`, `\\s`) |
| `Unexpected token` | minify時にクォートが崩れた | `data-action` + イベント委譲パターンに変更 |
| ボタンが反応しない | innerHTML後の onclick が効かない | `document.addEventListener` で委譲 |

### デバッグ手順

1. **Developer: Open Webview Developer Tools** を実行
2. Console タブでエラーを確認
3. ビルド出力 `out/extension.js` で該当行を検索
4. ソースの正規表現/クォートを修正し再ビルド

## 命名の不一致

| 症状 | 原因 | 解決策 |
|------|------|--------|
| 設定が効かない | 設定キーがコードと不一致 | package.json と getConfiguration() を統一 |
| コマンドが見つからない | コマンドIDがpackage.jsonと不一致 | 全箇所で同じIDを使用 |

### 命名一貫性チェック

```bash
# package.json のコマンド/設定キーを抽出
grep -E '"myExt\.' package.json

# ソースコードの使用箇所を検索
grep -r "myExt\." src/
```

公開前に統一することを強く推奨（公開後は既存ユーザーの設定が壊れる）。
