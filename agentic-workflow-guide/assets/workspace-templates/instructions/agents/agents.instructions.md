---
applyTo: ".github/agents/**"
---

# Agent Instructions

Rules applied when editing files in the `.github/agents/` directory.

> **詳細は [agent-design.instructions.md](agent-design.instructions.md) を参照（存在する場合）**

## Quick Reference

### Agent Definition Structure

各エージェントは以下のセクションを持つ（詳細は agent-design.instructions.md 参照）：

| セクション    | 必須 | 説明               |
| ------------- | ---- | ------------------ |
| Role          | ✅   | 1文での責任定義    |
| Goals         | ✅   | 達成目標のリスト   |
| Done Criteria | ✅   | 検証可能な完了条件 |
| Permissions   | ✅   | 許可/禁止事項      |
| I/O Contract  | ✅   | 入出力の定義       |

## Best Practices

1. **1 Agent = 1 Responsibility** - 複数の責任がある場合は分割
2. **Clear I/O** - 曖昧な定義を避ける
3. **Explicit Constraints** - エッジケースを考慮
4. **Subagent-only agents use `user-invocable: false`** - ピッカーに出したくない agent は正式キーで明示する
5. **Avoid deprecated/invalid manifest keys** - `user-invokable` や `infer` などの旧記法は新規追加しない

## Manifest Validation

`.agent.md` を複数編集した場合は、少なくとも以下を確認すること:

- front matter に `user-invokable` などの誤記が混入していない
- `user-invocable: false` を設定した agent が意図どおり subagent 専用になっている
- front matter 編集後も本文先頭の `## Role` など必須セクションが崩れていない
