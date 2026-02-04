# Repository Copilot Instructions for Agent Workflows

このリポジトリでは、Copilot を自律的なエージェントワークフローの一部として扱います。
以下のガードレールは、単発のコード補完だけでなく、複雑なタスクの計画・実行・検証を支援するために設計されています。

## エージェント行動指針 (Agent Behavior)

1.  **計画重視 (Plan First)**:
    - 複雑なタスク（機能追加、リファクタリング、デバッグ）に着手する前に、必ずステップバイステップの計画を提示してください。
    - ユーザーの承認を得てから実行に移ることを基本とします（明示的な許可がある場合を除く）。

2.  **コンテキスト認識 (Context Awareness)**:
    - 作業前に必ず関連ファイル（`README.md`, `package.json`, 関連ソースコード）を読み込み、プロジェクトの文脈を理解してください。
    - 推測でコードを書かず、`grep_search` や `file_search` を活用して既存の実装パターンを確認してください。

3.  **自律的な検証 (Self-Correction)**:
    - コードを変更した後は、可能な限り検証（ビルド、テスト実行、リンターチェック）を行ってください。
    - エラーが発生した場合は、エラーメッセージを分析し、修正案を提示・実行してください。

4.  **コンテキスト最小化 (Context Minimalism)**:
    - 目的達成に必要な最小限の情報だけを読み込み、不要な長文の貼り付けや広範な検索を避けてください。
    - 参照は高信号のファイル/セクションに限定し、根拠を明示してください。

5.  **フェイルファースト (Fail Fast)**:
    - 作業開始前に「Phase 0: 事前チェック」を実施してください。
    - 主要ファイル/設定の存在確認（例: `AGENTS.md`, `.github/instructions/**`, 対象ファイルパスの検証）。
    - `manage_todo_list` にゲート条件を設定し、未充足なら中断・是正してから再開。

## コミュニケーションスタイル

- **結論ファースト**: 結論を先に述べ、その後に理由や詳細を記述する
- **日本語で回答**: ユーザーが日本語なら日本語で応答する
- 詳細ルール: [Communication Rules](instructions/core/communication.instructions.md)（存在する場合）
- **成果物は構造化**: 出力は箇条書き/表/コードフェンスで構造化しフォーマル、会話はカジュアルでOK。

## コーディング規約 & ツール使用

- **DRY & SOLID**: 重複を避け、単一責任の原則に従ったコード生成を心がけてください。
- **SSOT (Single Source of Truth)**: 情報は一箇所で管理し、他はそこを参照する。設定やドキュメントの重複を避け、変更時の不整合を防ぐ。
- **MCP 活用**: 利用可能な MCP ツール（Azure, GitHub, Docs 等）を積極的に活用し、最新の公式情報に基づいた回答を行ってください。
- **参照の明記**: 回答には必ず参照元 URL と根拠（どのファイル/公式ページか）を明記してください。
- **詳細ルール**: 以下のインストラクションファイルに従ってください（存在する場合）。
  - [Terminal Rules](instructions/dev/terminal.instructions.md) (PowerShell 互換、破壊的操作の禁止)
  - [Git Rules](instructions/dev/git.instructions.md) (コミット規約、Push 禁止)
  - [Python Rules](instructions/dev/python.instructions.md) (仮想環境必須、uv 推奨)
  - [Node.js Rules](instructions/dev/nodejs.instructions.md) (nvm 推奨、パッケージマネージャー)
  - [Microsoft Docs](instructions/integrations/microsoft-docs.instructions.md) (MCP 連携、ソース明記) - Microsoft Docs MCP ツール名（正規）: `mcp_microsoftdocs_microsoft_docs_search`, `mcp_microsoftdocs_microsoft_code_sample_search`, `mcp_microsoftdocs_microsoft_docs_fetch`

## エージェント設計

- 詳細ルール: [Agent Design](instructions/agents/agent-design.instructions.md)（存在する場合）

## セキュリティとコンプライアンス

- 詳細ルール: [Security Rules](instructions/core/security.instructions.md)（存在する場合）

## Skills の活用

プロンプト / エージェント / インストラクションを作成・編集する際は、以下の Skills を参照してください。

| Skill                                                            | 用途                              | トリガー                                          |
| ---------------------------------------------------------------- | --------------------------------- | ------------------------------------------------- |
| [agentic-workflow-guide](skills/agentic-workflow-guide/SKILL.md) | ワークフロー設計・レビュー・改善  | `.github/` 配下のファイル編集、エージェント設計時 |
| skill-finder（存在する場合）                                     | Skills の検索・インストール・管理 | 新しい Skill を探すとき                           |

## ファイルマップ

エージェント一覧・関連アセットの詳細は [AGENTS.md](../AGENTS.md) を参照してください（存在する場合）。
