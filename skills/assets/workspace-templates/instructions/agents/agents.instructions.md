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
