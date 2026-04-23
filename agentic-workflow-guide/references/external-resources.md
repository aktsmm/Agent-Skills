# External Resources for AI Agents

AI エージェント開発に役立つ外部リソース集。

## First-Hop References

まず最初に当たるリンク。設計判断や platform behavior を確認したいときはここから入る。

| リソース                                     | 説明                                                  | URL                                                                                             |
| -------------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| **GitHub Docs: Chat in IDE**                 | Copilot Chat / IDE 内での基本動作                     | https://docs.github.com/en/copilot/how-tos/chat-with-copilot/chat-in-ide                        |
| **VS Code: Custom Agents**                   | VS Code 側の custom agents 全体像                     | https://code.visualstudio.com/docs/copilot/customization/custom-agents                          |
| **GitHub Docs: Create Custom Agents**        | GitHub Copilot agents の作成手順                      | https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents |
| **Anthropic: Building Effective Agents**     | workflow pattern と agent 設計の基本原則              | https://www.anthropic.com/engineering/building-effective-agents                                 |
| **Anthropic: Effective Context Engineering** | context engineering / compaction / retrieval の考え方 | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents               |
| **Anthropic: Writing Tools for Agents**      | agent 向け tool 設計                                  | https://www.anthropic.com/engineering/writing-tools-for-agents                                  |

## Deep References

深掘り用。設計原則の確認後に、具体的な prompt / skill / hook / orchestration の実装例を探すときに使う。

## プロンプト・インストラクション

| リソース                   | 説明                              | URL                                                 |
| -------------------------- | --------------------------------- | --------------------------------------------------- |
| **Awesome Copilot**        | GitHub 公式コミュニティプロンプト | https://github.com/github/awesome-copilot           |
| **Awesome Claude Prompts** | Claude 向けプロンプト集 (4.2k★)   | https://github.com/langgptai/awesome-claude-prompts |
| **Awesome Reviewers**      | 3000+ コードレビュープロンプト    | https://github.com/baz-scm/awesome-reviewers        |

## Claude Code 関連

| リソース                       | 説明                              | URL                                                      |
| ------------------------------ | --------------------------------- | -------------------------------------------------------- |
| **Awesome Claude Code**        | スキル・フック・コマンド集 (22k★) | https://github.com/hesreallyhim/awesome-claude-code      |
| **Claude Code System Prompts** | 公式システムプロンプト抽出        | https://github.com/Piebald-AI/claude-code-system-prompts |
| **Claude Code Docs Mirror**    | Anthropic ドキュメントミラー      | https://github.com/ericbuess/claude-code-docs            |

## VS Code カスタマイズ

| リソース                        | 説明             | URL                                                                          |
| ------------------------------- | ---------------- | ---------------------------------------------------------------------------- |
| **VS Code Custom Instructions** | 公式ドキュメント | https://code.visualstudio.com/docs/copilot/customization/custom-instructions |
| **VS Code Prompt Files**        | 公式ドキュメント | https://code.visualstudio.com/docs/copilot/customization/prompt-files        |
| **VS Code Custom Agents**       | 公式ドキュメント | https://code.visualstudio.com/docs/copilot/customization/custom-agents       |
| **VS Code Agent Skills**        | 公式ドキュメント | https://code.visualstudio.com/docs/copilot/customization/agent-skills        |

## ツール・ユーティリティ

| リソース                          | 説明                               | URL                                        |
| --------------------------------- | ---------------------------------- | ------------------------------------------ |
| **claudekit**                     | 20+ 専門サブエージェント           | https://github.com/carlrannaberg/claudekit |
| **Trail of Bits Security Skills** | セキュリティ監査スキル             | https://github.com/trailofbits/skills      |
| **Claude Squad**                  | マルチエージェントオーケストレータ | https://github.com/smtg-ai/claude-squad    |

## Community Exploration

コミュニティ資産の探索用。first-hop の代わりではなく補助として使う。

### 注目カテゴリ（Awesome Claude Code より）

### Agent Skills

- DevOps スキル、セキュリティスキル、Web 資産生成など

### Workflows & Knowledge Guides

- AB Method, RIPER Workflow, Ralph Wiggum パターン

### Tooling

- IDE 統合、使用量モニター、オーケストレータ

### Hooks

- TDD Guard, TypeScript Quality Hooks, Britfix

## How to Use This List

1. **プロジェクトに合わせて選択**: 全てを導入せず、必要なものだけ
2. **カスタマイズ**: そのまま使わず、プロジェクト固有の要件を追加
3. **定期更新**: これらのリソースは頻繁に更新されるのでチェック
4. **ライセンス確認**: 各リソースのライセンスを確認してから使用

## Selection Rule

- 設計判断に迷ったら **First-Hop References** を先に使う
- 実装パターンや周辺事例を広く探したいときだけ **Deep References / Community Exploration** へ進む
- 本体 SKILL に戻す外部リンクは First-Hop の中から少数だけ選ぶ
