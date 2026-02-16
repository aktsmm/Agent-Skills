---
description: 複数エージェントのオーケストレーション計画
---

# Prompt: Plan Agent Workflow

複雑なタスクを解決するために、複数のエージェントをどのように組み合わせるか（オーケストレーション）を計画するプロンプトです。

## 前提条件

- 参照: `AGENTS.md` (利用可能なエージェント一覧、存在する場合)
- 参照: `.github/instructions/agents/agent-design.instructions.md` (設計原則、存在する場合)

> 参照ファイルが無い場合は、利用可能なエージェント一覧と制約をユーザーに確認する。

## 指示

ユーザーのタスクを達成するために、以下のステップで計画を立ててください。

1. **タスク分解**: タスクを独立したサブタスクに分解する。
2. **エージェント選定**: 各サブタスクに最適なエージェントを `AGENTS.md` から選ぶ（なければ新規作成を提案）。
3. **フロー定義**: エージェント間のデータの受け渡し（成果物）と順序を定義する。
4. **実行計画**: `agent`（旧 runSubagent）を使用した具体的な実行手順を示す。

## 出力例

### ステップ形式

1. **Step 1: 要件定義**
   - Agent: `.github/agents/orchestrator.agent.md`
   - Goal: ユーザーの要望を整理し、必要なら新規エージェント作成を提案する。
   - Output: `docs/requirements.md`（要件の叩き台）
2. **Step 2: 実装計画**
   - Agent: `.github/agents/sample.agent.md`（※用途に応じて適切なエージェントに差し替え）
   - Input: Step 1 の `docs/requirements.md`
   - Goal: 実装方針を `docs/plan.md` にまとめる。

### agent 呼び出し例

```javascript
// Step 1: 要件整理（オーケストレーター）
agent({
  prompt: `
    ユーザーの要望を分析し、必要なタスクを洗い出してください。
    出力: docs/requirements.md に要件をまとめる。
  `,
  description: "要件整理",
});

// Step 2: 実装（直列実行 - 前のステップの結果を待つ）
agent({
  prompt: `
    docs/requirements.md を読み込み、実装計画を立ててください。
    出力: docs/plan.md に計画をまとめる。
  `,
  description: "実装計画",
});

// Step 3: レビュー
agent({
  prompt: `
    docs/plan.md をレビューし、問題点があれば指摘してください。
    出力: レビュー結果をユーザーに報告。
  `,
  description: "計画レビュー",
});
```

## 注意事項

- **直列実行推奨**: agent は並列も可能だがオーバーヘッドがあるため、前のステップ完了を待ってから次へ。
- **サマリ粒度**: 各ステップの成果物は明確に定義し、次のステップで参照可能にする。
- **エラーハンドリング**: 途中で失敗した場合の対応方針も計画に含める。
- **人間チェックポイント**: 重要な判断が必要な箇所では確認を挟む。
