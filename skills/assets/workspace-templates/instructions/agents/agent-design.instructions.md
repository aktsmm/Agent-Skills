```instructions
---
applyTo: ".github/agents/**/*.agent.md"
---

# Agent Workflow Design Instructions

エージェントやワークフロー設計のガイドラインです。

→ **正本（SSOT）**: 詳細な設計原則は以下を参照してください:
  - 英語版: [../../../references/design-principles.md](../../../references/design-principles.md)

---

## Part 1: エージェント設計原則（概要）

| 原則 | 説明 |
|------|------|
| **Single Responsibility** | 1 エージェント = 1 ゴール |
| **Stateless & Idempotency** | ファイル状態で判断、再実行可能 |
| **Orchestration** | 複雑タスクは runSubagent で委譲 |
| **Fail-safe** | 破壊的操作前に確認 |
| **Observability** | 決定事項をログに残す |

→ 各原則の詳細は [design-principles.md](../../../references/design-principles.md) を参照

---

## Part 2: ワークフローアーキテクチャ原則（概要）

| 原則 | 説明 |
|------|------|
| **IR Architecture** | Input → 中間表現 (IR) → Output |
| **Determinism** | 同じ IR → 同じ成果物 |
| **Validation** | 各段階でバリデーション |
| **Logging** | IR と決定をログに保存 |

→ 詳細は [design-principles.md > IR Architecture](../../../references/design-principles.md#intermediate-representation-ir-architecture) を参照

---

## エージェントマニフェスト必須項目

→ [agent-template.md](../../../references/agent-template.md) を参照

| セクション | 必須 | 説明 |
|-----------|------|------|
| Role | ✅ | 1文での責任定義 |
| Goals | ✅ | 達成目標のリスト |
| Done Criteria | ✅ | 検証可能な完了条件 |
| Permissions | ✅ | 許可/禁止事項 |
| I/O Contract | ✅ | 入出力の定義 |

---

## References

- [design-principles.md](../../../references/design-principles.md) - 設計原則の正本
- [agent-template.md](../../../references/agent-template.md) - エージェントテンプレート
- [review-checklist.md](../../../references/review-checklist.md) - レビューチェックリスト
```
