# Code Review Prompts & Templates

拡張機能リポジトリで AI レビューを回すときの最小テンプレート。一般的なレビュー観点（バグ、セキュリティ、性能、保守性、テスト、ドキュメント）は現行モデルが既定で扱えるため、ここでは出力形式と拡張機能固有の観点だけを固定する。

## 出力形式

- ❌ **Critical**: 必須修正（マージ前に修正必須）
- ⚠️ **Warning**: 推奨修正
- 💡 **Suggestion**: 改善案

指摘には行番号と具体的な修正案を付け、問題がなければ簡潔に承認する。

## 拡張機能固有の観点

- `package.json` の commands / views / configuration / menus とコード上の ID・設定キーの一致、`package.nls*.json` の同期
- Webview の CSP / nonce / `localResourceRoots` / workspace 由来値の escape
- LM Tools の `prepareInvocation` に副作用がないこと、変更系の確認、秘密値を引数で受けないこと
- VSIX に `src/`、テスト、sourcemap、ログが混入していないこと

## code-review.instructions.md

```markdown
---
name: Code Review
description: Use when reviewing changes in this VS Code extension
applyTo: "src/**/*.ts"
---

Review for correctness, security and maintainability. Also check the extension-specific
items: manifest/ID consistency, Webview CSP and escaping, LM Tool confirmation, and VSIX payload.
Report as Critical / Warning / Suggestion with line references.
```

## code-reviewer.agent.md

```markdown
---
name: Code Reviewer
description: Read-only reviewer for extension pull requests
tools: ["search/codebase", "search/changes", "read/problems", "githubRepo"]
---

Review the current changes. Do not edit files. Report Critical / Warning / Suggestion with line references.
```

ツール ID の現行形式は [AI Customization](ai-customization.md#custom-agent-フォーマット) を参照。

| リソース        | 説明               | URL                                       |
| --------------- | ------------------ | ----------------------------------------- |
| Awesome Copilot | 公式コミュニティ例 | https://github.com/github/awesome-copilot |
