# External References (Prompts / Reviews) — Summary Instructions

このファイルは、README の External References を実務に落とし込むための要点まとめ。各 URL は必ず参照元として残し、詳細は原文を確認する。

---

## クイックリファレンス — いつ何を見る？

| ジャンル             | いつ使う？                                       | 参照先                                                     |
| -------------------- | ------------------------------------------------ | ---------------------------------------------------------- |
| **プロンプト基礎**   | プロンプトの書き方・構成を学ぶとき               | OpenAI / Microsoft / Google / Amazon / IBM                 |
| **技法カタログ**     | CoT, RAG, few-shot など特定技法を調べるとき      | Prompt Engineering Guide                                   |
| **エージェント設計** | マルチエージェント・ワークフロー設計時           | OpenAI Agents / Anthropic (Building Agents) / Agent Skills |
| **コンテキスト管理** | 長いタスク・記憶管理・情報の取捨選択             | Anthropic (Context Engineering)                            |
| **実践・コード例**   | 具体的な実装パターン・API の使い方               | OpenAI Cookbook                                            |
| **ツール運用**       | Claude Code / Copilot での実装ベストプラクティス | Claude Code / GitHub Copilot Best Practices                |

---

# 1️⃣ プロンプトエンジニアリング基礎

> **いつ使う？** プロンプトの書き方を学ぶ / 出力を安定させたい / 各クラウドベンダーの推奨を確認したいとき

## OpenAI — Prompt Engineering

- URL: https://platform.openai.com/docs/guides/prompt-engineering
- 要点:
  - モデル選択は性能/コスト/速度のトレードオフを意識して選ぶ。
  - `instructions`/メッセージロールで指示の優先度を分ける。
  - 明確な指示・例示（few-shot）・構造化（Markdown/XML）で意図を伝える。
  - コンテキストは必要十分にし、タスクは分割して指示する。
  - 出力形式の指定・プライミング（cue）で結果の形を制御する。
  - プロンプトは evals で評価し、モデル更新時の劣化を監視する。

## Microsoft — Azure OpenAI Prompt Engineering

- URL: https://learn.microsoft.com/azure/ai-services/openai/concepts/prompt-engineering
- 要点:
  - GPT 系向けの基本手法（推論モデル向けは別ガイド）。
  - 指示・主コンテンツ・例示・キュー・補助情報を組み立てる。
  - 明確な指示、出力形式の指定、タスク分割が効果的。
  - 順序・反復（recency bias）を意識し、必要なら指示を再掲する。
  - 事実性が重要な用途は「根拠データを同梱」してグラウンディングする。
  - 具体性・記述性・逃げ道（not found など）を用意する。

## Google Cloud — Prompt Engineering Tips

- URL: https://cloud.google.com/blog/products/application-development/five-best-practices-for-prompt-engineering
- 要点:
  - モデルの強み/弱みとバイアスを理解する。
  - 具体的・文脈付きの指示にする。
  - 例示やペルソナ指定で出力を安定化する。
  - 反復・試行で最適化し、段階分解で複雑タスクを解く。

## Amazon Bedrock — Prompt Engineering Guidelines

- URL: https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-engineering-guidelines.html
- 要点:
  - プロンプトは LLM への入力で、指示やコンテキストが結果に直結する。
  - プロンプトは「指示」「コンテンツ」「例示」などの構成要素を意識する。
  - 例示（few-shot）で期待動作を示すと安定する。
  - 幻覚対策として、プロンプト最適化・関連データの追加・モデル選択を検討する。

## IBM Think — Prompt Engineering

- URL: https://www.ibm.com/think/prompt-engineering
- 要点:
  - プロンプト設計は生成AI活用のコアスキルとして位置付け。
  - コンテキスト設計（RAG/要約/構造化入力）を重視する。
  - 実例・チュートリアル・ツールを通じた学習導線を提供。

---

# 2️⃣ 技法カタログ・学習リソース

> **いつ使う？** CoT, ReAct, RAG など特定の技法を調べたい / 用語を整理したい / 網羅的に手法を俯瞰したいとき

## Prompt Engineering Guide

- URL: https://www.promptingguide.ai/
- 要点:
  - 基礎〜高度までの技法カタログ（few-shot, CoT, ReAct, prompt chaining, RAG など）。
  - AIエージェント/コンテキストエンジニアリングの学習導線がある。
  - 手法の俯瞰・用語整理の参照先として使う。

---

# 3️⃣ エージェント設計・アーキテクチャ

> **いつ使う？** マルチエージェント構成を設計する / ワークフローパターンを選ぶ / サブエージェント分割を検討するとき

## OpenAI — Agents Guide

- URL: https://platform.openai.com/docs/guides/agents
- 要点:
  - AgentKit で Build → Deploy → Optimize のライフサイクル管理。
  - Responses API = Chat Completions + Assistants のいいとこ取り。
  - Agents SDK でマルチエージェントのオーケストレーション（ハンドオフ、ガードレール、トレース）。
  - ビルトインツール: ウェブ検索 / ファイル検索 / コンピューター使用。

## Anthropic — Building Effective Agents

- URL: https://www.anthropic.com/engineering/building-effective-agents
- 要点:
  - まず最小構成で始め、必要に応じて複雑化する。
  - 「ワークフロー（固定経路）」と「エージェント（動的判断）」を区別する。
  - 代表的パターン: prompt chaining / routing / parallelization / orchestrator-workers / evaluator-optimizer。
  - エージェントはツール結果で進捗確認し、明確な停止条件を設ける。
  - フレームワークは便利だが抽象化の弊害に注意し、内部を理解する。

## Agent Skills — Open Standard for Agent Capabilities

- URL: https://agentskills.io/home
- 要点:
  - エージェントに再利用可能な「スキル」を提供するオープン標準（Anthropic 発）。
  - スキル = 手続き的知識・コンテキストをオンデマンドで読み込み可能なパッケージ。
  - ドメイン専門知識・新機能・繰り返しワークフローをスキル化できる。
  - Claude Code / GitHub Copilot / VS Code など主要ツールで採用が進んでいる。
  - `SKILL.md` 形式で定義し、スクリプト・リソースと一緒にフォルダ管理する。
  - 仕様: https://agentskills.io/specification
  - 例: https://github.com/anthropics/skills

---

# 4️⃣ コンテキストエンジニアリング

> **いつ使う？** 長時間タスクで記憶管理が必要 / コンテキスト窓を効率的に使いたい / 情報の取捨選択を最適化したいとき

## Anthropic — Effective Context Engineering

- URL: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- 要点:
  - コンテキストは有限資源。高シグナル最小集合を目指す。
  - システム指示は具体すぎず曖昧すぎない「適正な粒度」を保つ。
  - ツールは役割を明確化し、冗長・重複を避ける。
  - 例示は「代表例」を少数に絞り、網羅の詰め込みは避ける。
  - 長期タスクでは compaction / ノート取り / サブエージェントで記憶管理。
  - 事前取得とジャストインタイム取得のハイブリッドを検討する。

---

# 5️⃣ 実践ガイド・コード例

> **いつ使う？** 具体的な実装パターンを調べる / API の使い方を確認する / 実践的なレシピが欲しいとき

## OpenAI Cookbook

- URL: https://cookbook.openai.com/
- GitHub: https://github.com/openai/openai-cookbook
- 要点:
  - 250+ の実践レシピ集（エージェント、MCP、RAG、Evals など）。
  - Agents SDK を使ったマルチエージェント構成の実装例が豊富。
  - コンテキストエンジニアリング・セッション管理の実践パターン。
  - MCP サーバー構築・Deep Research API の活用例。
  - GPT-5 系の最新プロンプティングガイドも掲載。

---

# 6️⃣ ツール運用・ベストプラクティス

> **いつ使う？** Claude Code / GitHub Copilot で実際にコードを書くとき / セッション管理・検証基準の設計

## Claude Code — Best Practices

- URL: https://code.claude.com/docs/en/best-practices
- 要点:
  - 検証基準（テスト/期待出力/スクショ）を明示して自己検証させる。
  - 探索→計画→実装→コミットの分離が効果的。
  - 具体的な文脈・参照ファイル・制約条件を明示する。
  - 永続ルールは専用のガイドファイルに簡潔に記載し、肥大化を避ける。
  - 権限設定・CLI・サブエージェント/役割分担で作業を分割する。
  - カスタムコマンドやサブエージェント定義は frontmatter でメタ情報を明示する。
  - セッション管理（/clear, /rewind）で文脈汚染を防ぐ。

## GitHub Copilot — Best Practices

- URL: https://docs.github.com/en/copilot/using-github-copilot/best-practices-for-using-github-copilot
- 要点:
  - Copilot の得意分野: テスト・繰り返しコード・デバッグ・正規表現生成。
  - インライン補完 vs Chat の使い分けを意識する。
  - 複雑なタスクは分割し、具体的な要件・例示を含める。
  - 提案コードは必ず検証（理解・レビュー・テスト）してから採用。
  - 関連ファイルを開く / 不要なファイルを閉じてコンテキストを調整。
  - プロンプトを言い換えて異なる提案を引き出す。

---

## 運用ルール（共通）

- 参照 URL は削除しない。
- 重要事項は「短い要点」に落とし、詳細は元ページで確認する。
- ガイドラインが更新されるため、定期的に見直す。

---

## 実務テンプレ（汎用）

### 1) プロンプト構成テンプレ

- 目的（やること/やらないこと）
- 入力（対象データ/前提）
- 出力形式（箇条書き/JSON/表/長さ制限）
- 例示（1〜3件の代表例）
- 検証基準（テスト/期待出力/禁止事項）
- 追加文脈（必要最小限の補足情報）

### 2) 検証基準テンプレ

- 検証方法: 例）テスト名、コマンド、手順
- 期待結果: 例）「テストが全通過」「スクショで差分ゼロ」
- 失敗時対応: 例）再試行/原因特定/差分報告

### 3) コンテキスト運用チェックリスト

- 高シグナル最小集合になっているか
- 指示は具体すぎず曖昧すぎないか（適正粒度）
- 例示は代表例に絞れているか
- 長期タスクは compaction/ノート/サブエージェントを併用しているか
- 事前取得とジャストインタイム取得の使い分けができているか

---

## 参照ソース

- https://platform.openai.com/docs/guides/prompt-engineering
- https://learn.microsoft.com/azure/ai-services/openai/concepts/prompt-engineering
- https://cloud.google.com/blog/products/application-development/five-best-practices-for-prompt-engineering
- https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-engineering-guidelines.html
- https://www.ibm.com/think/prompt-engineering
- https://www.promptingguide.ai/
- https://www.anthropic.com/engineering/building-effective-agents
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- https://platform.openai.com/docs/guides/agents
- https://code.claude.com/docs/en/best-practices
- https://docs.github.com/en/copilot/using-github-copilot/best-practices-for-using-github-copilot
- https://cookbook.openai.com/
- https://agentskills.io/home
