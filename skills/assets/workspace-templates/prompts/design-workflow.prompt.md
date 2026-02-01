---
description: 新しいエージェントワークフローの設計
---

# Prompt: Design New Agent Workflow

新しいエージェントワークフロー（複数のエージェントが連携するシステム）を設計するためのプロンプトです。
「自動コードレビューのワークフローを作りたい」「バグ修正の自動化ラインを作りたい」といった要望に対して使用します。

## 前提条件

- 参照: `.github/instructions/agents/agent-design.instructions.md` (オーケストレーションの原則、存在する場合)

> 参照ファイルが無い場合は、ユーザーに追加要件を確認し、ここに書かれた指示のみで設計する。

## 指示

ユーザーの要望に基づいて、以下の項目を含むワークフロー設計書を作成してください。

1. **ワークフローの目的**: 何を解決するためのフローか。
2. **エージェント構成**: 必要なエージェントの役割定義（Role）と責任範囲。
   - 例: `Orchestrator`, `Researcher`, `Coder`, `Reviewer`
3. **インタラクションフロー**: エージェント間でどのようなデータ（成果物）を受け渡すか。
4. **ディレクトリ構成案**: `.github/agents/` 配下のファイル構成。

## 出力フォーマット

```markdown
# [Workflow Name] Design

## Overview

...

## Agents

- **[Agent A]**: ...
- **[Agent B]**: ...

## Interaction Flow

1. [Agent A] creates ...
2. [Agent B] reads ...

## Proposed Files

- .github/agents/orchestrator.agent.md
- .github/agents/worker-a.agent.md
  ...
```
