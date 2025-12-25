#!/usr/bin/env python3
"""
scaffold_workflow.py - エージェントワークフローのディレクトリ構成を生成

Usage:
    python scaffold_workflow.py <workflow-name> [--pattern <pattern>] [--path <output-dir>]

Examples:
    python scaffold_workflow.py my-workflow
    python scaffold_workflow.py code-review --pattern evaluator-optimizer
    python scaffold_workflow.py data-pipeline --pattern orchestrator-workers --path ./projects
"""

import argparse
import os
from pathlib import Path

# 共通テンプレート（全パターンで使用）
COMMON_TEMPLATES = {
    "Agent.md": '''# {workflow_name} - Agent Workflow

## Overview

This workflow implements the **{pattern}** pattern for {purpose}.

## Agents

| Agent | Role | Done Criteria |
|-------|------|---------------|
| | | |

## Workflow Flow

```mermaid
graph TD
    A[Input] --> B[Agent 1]
    B --> C[Output]
```

## I/O Contract

- **Input**: [入力形式の説明]
- **Output**: [出力形式の説明]
- **IR Format**: （該当する場合）中間表現の仕様

## Design Principles

This workflow follows:
- **SSOT**: Single source of truth for all data
- **SRP**: Each agent has one responsibility
- **Fail Fast**: Errors are caught early
- **Iterative**: Small, verifiable steps
- **Idempotency**: Same input → same output

## Quick Start

1. Configure agents in `agents/`
2. Set up prompts in `prompts/`
3. Run with your orchestration framework

## References

- [Design Document](docs/design.md)
- [agentic-workflow-guide](https://github.com/aktsmm/Agent-Skills/tree/master/agentic-workflow-guide)
''',
    
    ".github/copilot-instructions.md": '''# Repository Copilot Instructions for {workflow_name}

このワークフローでは、Copilot を自律的なエージェントワークフローの一部として扱います。

## エージェント行動指針 (Agent Behavior)

1. **計画重視 (Plan First)**:
   - 複雑なタスクに着手する前に、必ずステップバイステップの計画を提示
   - ユーザーの承認を得てから実行に移る

2. **コンテキスト認識 (Context Awareness)**:
   - 作業前に関連ファイルを読み込み、プロジェクトの文脈を理解
   - 推測でコードを書かず、既存の実装パターンを確認

3. **自律的な検証 (Self-Correction)**:
   - コードを変更した後は、可能な限り検証を実行
   - エラー発生時は分析し、修正案を提示・実行

## ワークフローパターン

**{pattern}** - {pattern_description}

## コーディング規約

- **DRY & SOLID**: 重複を避け、単一責任の原則に従う
- **SSOT**: 情報は一箇所で管理し、他はそこを参照
- **Fail Fast**: エラーは早期に検出・報告

## コミュニケーションスタイル

- **結論ファースト**: 結論を先に述べ、その後に理由・詳細
- **日本語で回答**: ユーザーが日本語なら日本語で応答

## ファイル構成

- エージェント定義: `agents/*.agent.md`
- プロンプト: `prompts/*.prompt.md`
- 設定: `config/*.yaml`
- インストラクション: `.github/instructions/`

## 参照

- [Agent.md](../Agent.md) - ワークフロー概要
- [docs/design.md](../docs/design.md) - 設計ドキュメント
''',
    
    ".github/instructions/workflow.instructions.md": '''---
applyTo: "**"
---

# Workflow Instructions

このワークフロー全体に適用されるルール。

## 基本原則

- 各エージェントは単一責務を持つ
- エラーは早期に検出し、明確なメッセージを出力
- 中間状態は必ず確認可能にする

## 命名規則

- エージェント: `{{role}}_agent.md`
- プロンプト: `{{purpose}}_prompt.md`
- 設定: `{{scope}}_config.yaml`

## ファイル構成

```
{workflow_name}/
├── Agent.md                 # ワークフロー概要
├── .github/
│   ├── copilot-instructions.md
│   └── instructions/
│       └── workflow.instructions.md
├── agents/                  # エージェント定義
├── prompts/                 # プロンプトテンプレート
├── docs/                    # 設計ドキュメント
└── config/                  # 設定ファイル
```
''',
    
    ".github/instructions/agents.instructions.md": '''---
applyTo: "agents/**"
---

# Agent Instructions

`agents/` ディレクトリのファイル編集時に適用されるルール。

## エージェント定義の構成

```markdown
# Agent: {{name}}

## Role
エージェントの役割を1文で記述

## Responsibilities
- 責務1
- 責務2

## Input
- input1: 説明

## Output
- output1: 説明

## Constraints
- 制約事項
```

## ベストプラクティス

1. **1エージェント1責務** - 複数の責務は分割
2. **明確な入出力** - 曖昧な定義を避ける
3. **制約を明記** - エッジケースを考慮
''',
    
    ".github/instructions/prompts.instructions.md": '''---
applyTo: "prompts/**"
---

# Prompt Instructions

`prompts/` ディレクトリのファイル編集時に適用されるルール。

## プロンプト構成

```markdown
# {{Purpose}} Prompt

## Context
背景情報

## Task
タスクの説明

## Guidelines
1. ガイドライン1
2. ガイドライン2

## Output Format
期待する出力形式
```

## ベストプラクティス

1. **明確な指示** - 曖昧な表現を避ける
2. **具体例を含める** - 期待する出力の例を示す
3. **制約を明記** - やってはいけないことを書く
4. **変数は `{{placeholder}}` 形式** - 動的に置換可能に
''',
    
    "prompts/system_prompt.md": '''# System Prompt

You are a specialized agent in the {workflow_name} workflow.

## Your Role

[エージェントの役割を1文で記述]

## Guidelines

1. **Plan First**: 複雑なタスクは計画を提示してから実行
2. **Single Responsibility**: 自分の責務に集中し、他は委譲
3. **Validate First**: 入力を検証してから処理開始
4. **Fail Fast**: エラーは早期に検知・報告
5. **Transparency**: 進捗を明示的に報告

## Constraints

- 推測でデータを補完しない（不明点は確認）
- 検証に失敗したら処理を停止
- 破壊的操作の前に確認を求める
- `git push` は原則禁止

## Output Format

- 結論ファースト（結論 → 理由 → 詳細）
- 構造化された出力を心がける
''',
    
    "prompts/create-agent.prompt.md": '''# Prompt: Create New Agent

新しいエージェント定義 (`.agent.md`) を作成するためのプロンプトです。

## 前提条件

- 参照: `agents/sample.agent.md` (テンプレート)
- 参照: `.github/instructions/agents.instructions.md`

## 指示

1. ユーザーの要望から **Role** (役割) と **Goals** (ゴール) を定義
2. **Done Criteria** を検証可能な形で記述
3. **Permissions** は最小権限の原則に従う
4. **I/O Contract** を明確に定義
5. **Workflow** は具体的なステップに分解

## 出力フォーマット

```markdown
# [Agent Name]

## Role
[役割を1文で]

## Goals
- [ゴール1]
- [ゴール2]

## Done Criteria
- [検証可能な完了条件1]
- [検証可能な完了条件2]

## Permissions
- **Allowed**: [許可される操作]
- **Denied**: `git push`, ユーザー許可なき削除

## I/O Contract
- **Input**: [入力形式]
- **Output**: [出力形式]

## Workflow
1. **Plan**: 要求を分析し、手順を提示
2. **Act**: 承認を得て実行
3. **Verify**: 結果を検証

## Error Handling
- エラー発生時は分析して修正を試みる
- 3回連続失敗で人間に報告

## Idempotency
- 既存状態を確認してから操作
- 重複処理を避ける
```
''',
    
    "prompts/design-workflow.prompt.md": '''# Prompt: Design Agent Workflow

エージェントワークフローを設計するためのプロンプトです。

## 前提条件

- 参照: `docs/design.md`
- 原則: SSOT, SRP, Simplicity First, Fail Fast

## 指示

ユーザーの要望に基づいて、以下を設計してください。

### Step 1: 複雑さレベルの判断

| レベル | エージェント数 | 適用ケース |
|--------|--------------|-----------|
| Simple | 1 | 単一タスク、シンプルな処理 |
| Medium | 2-3 | オーケストレーター + ワーカー |
| Complex | 4+ | 専門エージェント複数 |

**原則: Start Simple** - まず最小構成で試す

### Step 2: 設計書作成

1. **ワークフローの目的**: 何を解決するか
2. **エージェント構成**: 役割と責務
3. **I/O Contract**: 入出力の定義
4. **インタラクションフロー**: データの流れ
5. **検証ポイント**: Gate/Checkpoint の配置
6. **エラー処理**: 失敗時の対応

## 出力フォーマット

```markdown
# [Workflow Name] Design

## Overview
- **Purpose**: 
- **Complexity**: Simple | Medium | Complex
- **Pattern**: [Prompt Chaining | Routing | Parallelization | Orchestrator-Workers | Evaluator-Optimizer]

## Agents
| Agent | Role | Input | Output |
|-------|------|-------|--------|

## Flow
```mermaid
graph TD
    A[Input] --> B[Agent 1]
    B --> C{{Gate}}
    C -->|Pass| D[Agent 2]
    C -->|Fail| E[Error Handler]
```

## Checkpoints
1. [ステップ間の検証ポイント]

## Error Handling
- [エラー時の対応]
```
''',
    
    "prompts/plan-workflow.prompt.md": '''# Prompt: Plan Agent Workflow

複数のエージェントを組み合わせる計画を立てるプロンプトです。

## 前提条件

- 参照: `Agent.md` (利用可能なエージェント一覧)

## 指示

ユーザーのタスクを達成するために、以下のステップで計画を立ててください。

1. **タスク分解**: 独立したサブタスクに分解
2. **エージェント選定**: 各サブタスクに最適なエージェントを選ぶ
3. **フロー定義**: データの受け渡しと順序を定義
4. **検証ポイント**: 各ステップ後の検証方法
5. **実行計画**: 具体的な実行手順

## 出力例

### Step 1: 要件定義
- **Agent**: orchestrator
- **Goal**: ユーザーの要望を整理
- **Output**: `docs/requirements.md`
- **Validation**: ユーザー確認

### Step 2: 実装
- **Agent**: worker
- **Input**: Step 1 の requirements.md
- **Goal**: 実装を行う
- **Output**: 実装ファイル
- **Validation**: テスト実行
''',
    
    "prompts/review-agent.prompt.md": '''# Prompt: Review Agent Definition

エージェント定義をレビューするためのプロンプトです。

## 設計原則チェックリスト

### Tier 1: コア原則（必須）
- [ ] **SRP**: 1エージェント1責務になっているか？
- [ ] **SSOT**: 情報が一元管理されているか？
- [ ] **Fail Fast**: エラー時の早期検知ができるか？

### Tier 2: 品質原則（推奨）
- [ ] **I/O Contract**: 入出力が明確に定義されているか？
- [ ] **Done Criteria**: 完了条件が検証可能か？
- [ ] **Idempotency**: リトライ可能な設計か？
- [ ] **Error Handling**: エラー処理が明記されているか？

### 構造チェック
- [ ] Role が1文で明確か？
- [ ] Goals が具体的か？
- [ ] Permissions が最小権限か？
- [ ] Workflow がステップに分解されているか？

## 出力フォーマット

```markdown
## Review Result

### ✅ Good Points
- [良い点]

### ⚠️ Improvements Needed
- [改善点]

### Recommendation
[総合評価と推奨アクション]
```
''',
    
    "prompts/error_handling_prompt.md": '''# Error Handling Prompt

エラー発生時のプロトコルです。

## Error Classification

| Type | Description | Recovery |
|------|-------------|----------|
| ValidationError | 入力データ不正 | 入力を修正して再試行 |
| ProcessingError | 処理中の失敗 | 原因分析して再試行 |
| TimeoutError | タイムアウト | リトライまたはスキップ |
| DependencyError | 外部サービス障害 | フォールバック |

## Response Format

```yaml
error:
  type: {{error_type}}
  message: {{error_message}}
  context: {{relevant_context}}
  recovery:
    possible: true/false
    suggestion: {{recovery_suggestion}}
    retry_count: {{current_retry}}/3
```

## Escalation Rules

1. **リトライ**: 同じエラーは最大3回まで
2. **フォールバック**: 可能なら代替手段を試す
3. **ハンドオフ**: 3回失敗で人間に報告
4. **ログ**: 全コンテキストを記録

## Fail Fast Principle

- エラーは早期に検知
- 問題があれば即座に報告
- 曖昧な状態で続行しない
'''
}

# ワークフローパターンごとのテンプレート
PATTERNS = {
    "basic": {
        "description": "基本的なワークフロー構成",
        "structure": {
            "agents": {
                "__description__": "エージェント定義",
                "sample.agent.md": '''# Sample Agent

## Role

あなたは [役割名] です。[対象] に対して [アクション] を行います。

## Goals

- [ゴール1]
- [ゴール2]

## Done Criteria

- [完了条件1: 検証可能な形で記述]
- [完了条件2]

## Permissions

- **Allowed**: ファイルの読み込み、提案の作成
- **Denied**: `git push`、ユーザー許可なきファイル削除

## I/O Contract

- **Input**: [入力形式の説明]
- **Output**: [出力形式の説明]
- **IR Format**: （該当する場合）構造化データの仕様

## References

- [Workflow Instructions](../.github/instructions/workflow.instructions.md)

## Workflow

1. **Plan**: ユーザーの要求を分析し、手順を提示
2. **Act**: 承認を得たら実行
3. **Verify**: 結果を確認

## Error Handling

- エラー発生時はエラーメッセージを分析し、修正を試みる
- 3回連続で失敗した場合は人間に報告
- 破壊的操作の前には必ず確認を求める

## Idempotency

- 既存ファイルの存在を確認してから操作
- 重複処理を避けるため、状態を必ずチェック
''',
                "orchestrator.agent.md": '''# Orchestrator Agent

## Role

あなたはオーケストレーター（司令塔）です。ユーザーの要求を分析し、適切なサブエージェントに作業を委譲して、全体の進行を管理します。

## Goals

- ユーザーの要求を理解し、タスクを分解する
- 各サブエージェントに適切な作業を割り当てる
- 進捗を監視し、結果をユーザーに報告する

## Done Criteria

- すべてのサブタスクが `completed` または `skipped` ステータスになっている
- 最終報告がユーザーに提示されている

## Permissions

- **Allowed**: タスク分解、サブエージェントへの委譲、進捗報告
- **Denied**: 直接のコード編集、ファイル削除、`git push`

## Non-Goals (やらないこと)

- コードを直接書かない（実装は専用エージェントに委譲）
- レビューを自分でしない（レビューは専用エージェントに委譲）
- ユーザーの意図を勝手に補完しない（不明点は確認）

## I/O Contract

- **Input**: ユーザーからの自然言語リクエスト
- **Output**:
  - タスク分解結果
  - 最終報告（成果物一覧 + ステータス）

## Workflow

1. **Analyze**: ユーザーの要求を分析し、必要なタスクを洗い出す
2. **Plan**: タスクを分解し、どのサブエージェントに委譲するか計画を提示
3. **Delegate**: ユーザーの承認後、サブエージェントを呼び出す
4. **Monitor**: 各サブエージェントの結果を確認し、問題があれば対処
5. **Report**: 全体の結果をユーザーに報告

## Error Handling

- サブエージェントが3回連続で失敗した場合は、人間に報告してハンドオフ
- 失敗したタスクはログに記録し、再試行可能な状態を維持

## Idempotency

- タスクの状態は常にファイルから読み取る（会話履歴に依存しない）
- 既に完了したタスクは再実行しない
'''
            },
            "prompts": {
                "__description__": "プロンプトテンプレート"
            },
            "docs": {
                "__description__": "設計ドキュメント",
                "design.md": '''# Workflow Design Document

## Overview
- **Name**: 
- **Purpose**: 
- **Pattern**: 

## Agents
| Agent | Role | Input | Output |
|-------|------|-------|--------|
| | | | |

## Flow
```mermaid
graph TD
    A[Start] --> B[Agent 1]
    B --> C[Agent 2]
    C --> D[End]
```

## Design Principles Check
- [ ] SSOT: 情報は一元管理されているか？
- [ ] SRP: 各エージェントは1責務か？
- [ ] Fail Fast: エラー時に即停止か？
- [ ] Iterative: 小さく分割されているか？
- [ ] Feedback Loop: 成果確認できるか？
''',
                "review_notes.md": '''# Review Notes

## Review Date
- 

## Reviewer
- 

## Checklist Results
See: agentic-workflow-guide/references/review-checklist.md

## Issues Found
1. 

## Action Items
1. 
'''
            },
            "config": {
                "__description__": "設定ファイル",
                "workflow_config.yaml": '''# Workflow Configuration

name: "{workflow_name}"
version: "1.0.0"

# Agents
agents:
  - name: agent_1
    prompt: prompts/system_prompt.md
    
# Flow
flow:
  - step: 1
    agent: agent_1
    next: 2
    
# Error handling
error_handling:
  max_retries: 3
  on_failure: stop
'''
            }
        }
    },
    "prompt-chaining": {
        "description": "順次処理パターン",
        "structure": {
            "agents": {
                "__description__": "順次実行されるエージェント",
                "step1_agent.md": "# Step 1 Agent\n\n## Role\n最初のステップを担当\n",
                "step2_agent.md": "# Step 2 Agent\n\n## Role\n2番目のステップを担当\n",
                "step3_agent.md": "# Step 3 Agent\n\n## Role\n最終ステップを担当\n"
            },
            "prompts": {
                "__description__": "各ステップのプロンプト"
            },
            "gates": {
                "__description__": "ステップ間の検証ゲート",
                "gate_template.md": '''# Gate: Step N → Step N+1

## Validation Criteria
- [ ] 条件1
- [ ] 条件2

## On Pass
次のステップへ進む

## On Fail
エラー処理またはリトライ
'''
            },
            "docs": {
                "__description__": "設計ドキュメント",
                "design.md": "# Prompt Chaining Workflow\n\n## Pattern: Prompt Chaining\n順次処理、各ステップで検証\n"
            },
            "config": {
                "__description__": "設定ファイル"
            }
        }
    },
    "parallelization": {
        "description": "並列処理パターン",
        "structure": {
            "agents": {
                "__description__": "並列実行されるエージェント",
                "worker1_agent.md": "# Worker 1 Agent\n\n## Role\n並列タスク1を担当\n",
                "worker2_agent.md": "# Worker 2 Agent\n\n## Role\n並列タスク2を担当\n",
                "worker3_agent.md": "# Worker 3 Agent\n\n## Role\n並列タスク3を担当\n",
                "aggregator_agent.md": "# Aggregator Agent\n\n## Role\n全ワーカーの結果を集約\n"
            },
            "prompts": {
                "__description__": "ワーカー用プロンプト"
            },
            "docs": {
                "__description__": "設計ドキュメント",
                "design.md": "# Parallelization Workflow\n\n## Pattern: Parallelization\n独立タスクを同時実行\n"
            },
            "config": {
                "__description__": "設定ファイル"
            }
        }
    },
    "orchestrator-workers": {
        "description": "オーケストレーター + ワーカーパターン",
        "structure": {
            "agents": {
                "__description__": "オーケストレーターとワーカー",
                "orchestrator_agent.md": '''# Orchestrator Agent

## Role
タスクを動的に分割し、ワーカーに割り当て

## Responsibilities
1. 入力を分析
2. サブタスクを生成
3. ワーカーを起動
4. 結果を統合
''',
                "worker_agent.md": '''# Worker Agent Template

## Role
割り当てられたサブタスクを実行

## Input
- task: サブタスクの内容
- context: 必要なコンテキスト

## Output
- result: タスク結果
- status: 成功/失敗
''',
                "synthesizer_agent.md": '''# Synthesizer Agent

## Role
全ワーカーの結果を統合して最終出力を生成
'''
            },
            "prompts": {
                "__description__": "各エージェントのプロンプト"
            },
            "docs": {
                "__description__": "設計ドキュメント",
                "design.md": "# Orchestrator-Workers Workflow\n\n## Pattern: Orchestrator-Workers\n動的にタスク分割→ワーカーへ\n"
            },
            "config": {
                "__description__": "設定ファイル"
            }
        }
    },
    "evaluator-optimizer": {
        "description": "評価・改善ループパターン",
        "structure": {
            "agents": {
                "__description__": "生成器と評価器",
                "generator_agent.md": '''# Generator Agent

## Role
コンテンツを生成

## Input
- request: 生成リクエスト
- feedback: 前回のフィードバック（あれば）

## Output
- content: 生成されたコンテンツ
''',
                "evaluator_agent.md": '''# Evaluator Agent

## Role
生成されたコンテンツを評価

## Criteria
- [ ] 基準1
- [ ] 基準2
- [ ] 基準3

## Output
- passed: true/false
- feedback: 改善点（失敗時）
'''
            },
            "prompts": {
                "__description__": "生成・評価プロンプト"
            },
            "docs": {
                "__description__": "設計ドキュメント",
                "design.md": '''# Evaluator-Optimizer Workflow

## Pattern: Evaluator-Optimizer
生成→評価→改善ループ

## Flow
```mermaid
graph TD
    A[Input] --> B[Generator]
    B --> C[Output]
    C --> D[Evaluator]
    D -->|Not Good| E[Feedback]
    E --> B
    D -->|Good| F[Final Output]
```

## Loop Control
- max_iterations: 5
- on_max_reached: return_best
'''
            },
            "config": {
                "__description__": "設定ファイル",
                "loop_config.yaml": '''# Evaluator-Optimizer Loop Configuration

max_iterations: 5
evaluation_criteria:
  - name: criteria_1
    weight: 0.4
  - name: criteria_2
    weight: 0.3
  - name: criteria_3
    weight: 0.3

threshold: 0.8
on_max_reached: return_best  # or: fail
'''
            }
        }
    },
    "routing": {
        "description": "ルーティングパターン",
        "structure": {
            "agents": {
                "__description__": "ルーターと専門ハンドラー",
                "router_agent.md": '''# Router Agent

## Role
入力を分類し、適切なハンドラーに振り分け

## Categories
- type_a: Handler A へ
- type_b: Handler B へ
- type_c: Handler C へ
''',
                "handler_a_agent.md": "# Handler A Agent\n\n## Role\nType A の処理を担当\n",
                "handler_b_agent.md": "# Handler B Agent\n\n## Role\nType B の処理を担当\n",
                "handler_c_agent.md": "# Handler C Agent\n\n## Role\nType C の処理を担当\n"
            },
            "prompts": {
                "__description__": "ルーティング・ハンドラープロンプト"
            },
            "docs": {
                "__description__": "設計ドキュメント",
                "design.md": "# Routing Workflow\n\n## Pattern: Routing\n入力を分類→専門処理へ振り分け\n"
            },
            "config": {
                "__description__": "設定ファイル"
            }
        }
    }
}


def create_structure(base_path: Path, structure: dict, workflow_name: str):
    """ディレクトリ構造を再帰的に作成"""
    for name, content in structure.items():
        if name == "__description__":
            continue
            
        path = base_path / name
        
        if isinstance(content, dict):
            # ディレクトリを作成
            path.mkdir(parents=True, exist_ok=True)
            # .gitkeep を作成（空ディレクトリ対策）
            if not any(k for k in content.keys() if k != "__description__"):
                (path / ".gitkeep").touch()
            else:
                create_structure(path, content, workflow_name)
        else:
            # ファイルを作成
            file_content = content.format(
                workflow_name=workflow_name,
                name=workflow_name,
                role_description="",
                context="",
                task_description="",
                output_format=""
            )
            path.write_text(file_content, encoding="utf-8")


def scaffold_workflow(name: str, pattern: str = "basic", output_path: str = "."):
    """ワークフローのディレクトリ構成を生成"""
    
    if pattern not in PATTERNS:
        print(f"❌ Unknown pattern: {pattern}")
        print(f"   Available patterns: {', '.join(PATTERNS.keys())}")
        return False
    
    pattern_info = PATTERNS[pattern]
    base_path = Path(output_path) / name
    
    if base_path.exists():
        print(f"❌ Directory already exists: {base_path}")
        return False
    
    print(f"🚀 Creating workflow: {name}")
    print(f"   Pattern: {pattern} - {pattern_info['description']}")
    print(f"   Location: {base_path.absolute()}")
    print()
    
    # ディレクトリ構造を作成
    base_path.mkdir(parents=True, exist_ok=True)
    create_structure(base_path, pattern_info["structure"], name)
    
    # .github ディレクトリと instructions を作成
    github_dir = base_path / ".github"
    github_dir.mkdir(parents=True, exist_ok=True)
    instructions_dir = github_dir / "instructions"
    instructions_dir.mkdir(parents=True, exist_ok=True)
    
    # 共通テンプレートを生成
    for filename, template in COMMON_TEMPLATES.items():
        file_path = base_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = template.format(
            workflow_name=name,
            pattern=pattern,
            pattern_description=pattern_info['description'],
            purpose="your use case",
            agent_role="Describe your agent's role here",
            context="",
            task_description="",
            input_data="",
            output_format="",
            good_example="",
            bad_example=""
        )
        file_path.write_text(content, encoding="utf-8")
    
    # README.md を生成
    readme_content = f'''# {name}

## Overview
Generated with `agentic-workflow-guide` skill.

## Pattern
**{pattern}** - {pattern_info['description']}

## Directory Structure
```
{name}/
├── Agent.md                    # ワークフロー概要
├── .github/
│   ├── copilot-instructions.md # Copilot 用インストラクション
│   └── instructions/           # 個別インストラクション
│       ├── workflow.instructions.md
│       ├── agents.instructions.md
│       └── prompts.instructions.md
'''
    
    for dir_name, dir_content in pattern_info["structure"].items():
        if dir_name != "__description__":
            desc = dir_content.get("__description__", "")
            readme_content += f"├── {dir_name}/                    # {desc}\n"
    
    readme_content += '''```

## Quick Start

1. **Agent.md** を編集してワークフロー概要を記述
2. **agents/** でエージェント定義を作成
3. **prompts/** でプロンプトテンプレートをカスタマイズ
4. **docs/design.md** で設計を文書化
5. **config/** で設定を調整

## Files

| File | Purpose |
|------|---------|
| `Agent.md` | ワークフロー全体の概要・エージェント一覧 |
| `.github/copilot-instructions.md` | GitHub Copilot 用の開発ガイドライン |
| `.github/instructions/*.instructions.md` | ファイルパターン別のルール |
| `prompts/system_prompt.md` | エージェント用システムプロンプト |
| `prompts/task_prompt.md` | タスク用プロンプトテンプレート |
| `prompts/error_handling_prompt.md` | エラー処理用プロンプト |

## Design Principles

This workflow should follow:

- **SSOT** - Single Source of Truth（情報の一元管理）
- **SRP** - Single Responsibility Principle（単一責務）
- **Fail Fast** - エラーは早期検出
- **Iterative Refinement** - 小さく反復
- **Feedback Loop** - 成果確認

See: `agentic-workflow-guide` for full checklist.

## References

- [agentic-workflow-guide](https://github.com/aktsmm/Agent-Skills/tree/master/agentic-workflow-guide)
- [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
'''
    
    (base_path / "README.md").write_text(readme_content, encoding="utf-8")
    
    print("✅ Created structure:")
    print(f"   📄 Agent.md")
    print(f"   📄 README.md")
    print(f"   📁 .github/")
    print(f"      📄 copilot-instructions.md")
    print(f"      📁 instructions/")
    print(f"         📄 workflow.instructions.md")
    print(f"         📄 agents.instructions.md")
    print(f"         📄 prompts.instructions.md")
    for dir_name in pattern_info["structure"].keys():
        if dir_name != "__description__":
            print(f"   📁 {dir_name}/")
            print(f"   📁 {dir_name}/")
    
    print(f"\n✅ Workflow '{name}' scaffolded successfully!")
    print("\nGenerated files:")
    print("  📄 Agent.md - ワークフロー概要")
    print("  📄 .github/copilot-instructions.md - Copilot 用インストラクション")
    print("  📄 .github/instructions/*.instructions.md - 個別ルール")
    print("  📄 prompts/*.md - プロンプトテンプレート")
    print("\nNext steps:")
    print("1. Edit Agent.md to describe your workflow")
    print("2. Customize agents/ for your use case")
    print("3. Update prompts/ with your prompts")
    print("4. Review with agentic-workflow-guide checklist")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Generate agent workflow directory structure"
    )
    parser.add_argument("name", help="Workflow name")
    parser.add_argument(
        "--pattern", "-p",
        choices=list(PATTERNS.keys()),
        default="basic",
        help="Workflow pattern (default: basic)"
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "--list-patterns",
        action="store_true",
        help="List available patterns"
    )
    
    args = parser.parse_args()
    
    if args.list_patterns:
        print("Available patterns:\n")
        for name, info in PATTERNS.items():
            print(f"  {name}")
            print(f"    {info['description']}")
            print()
        return
    
    scaffold_workflow(args.name, args.pattern, args.path)


if __name__ == "__main__":
    main()
