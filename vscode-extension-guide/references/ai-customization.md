# VS Code AI Customization Guide

拡張機能から AI カスタマイズ資産を同梱・検出・表示するときに必要な最小知識。詳細は公式 [Agent customization](https://code.visualstudio.com/docs/agent-customization/overview) を正とする（2026-09-30 版で確認）。

## ファイル種別と用途

| ファイル種別                | パス/命名規則                                                                                                  | 用途                               | 適用範囲                                                                                          |
| --------------------------- | -------------------------------------------------------------------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------- |
| **copilot-instructions.md** | `.github/copilot-instructions.md`                                                                              | プロジェクト全体のコーディング規約 | 全チャットリクエストに自動適用                                                                    |
| **Instructions Files**      | `.github/instructions/**/*.instructions.md`                                                                    | 言語/フレームワーク別ルール        | `applyTo` 一致、または `description` で task 関連時に読込                                         |
| **Prompt Files**            | `.github/prompts/*.prompt.md`                                                                                  | 再利用可能なタスク定義             | `/` で手動実行。Agent Host セッションでは非推奨・未読込（Local agent のみ。skill への移行を推奨） |
| **Custom Agents**           | `.github/agents/*.agent.md`                                                                                    | 専門エージェント                   | エージェント選択時、または subagent として                                                        |
| **AGENTS.md**               | ルート（入れ子は experimental）                                                                                | 複数ハーネス共通の指示             | 全チャットに自動適用                                                                              |
| **Agent Skills**            | `.github/skills/<name>/SKILL.md`（ほか `.claude/skills/`, `.agents/skills/`, user は `~/.copilot/skills/` 等） | スクリプト・資料付きの手順         | `description` 一致で自動読込、`/<name>` でも実行                                                  |

## 拡張機能からの同梱

- Skill は `contributes.chatSkills: [{ "path": "./skills/<name>/SKILL.md" }]`。フォルダ名と frontmatter `name` が一致しないと読み込まれない（小文字・数字・ハイフン、最大 64 文字、名前空間 prefix 不可）。
- 他拡張の同梱資産を検出する場合の既知 root と manifest 宣言は SKILL.md の Extension Host 境界を参照する。

## Instructions File フォーマット

```yaml
---
name: Code Review # UI表示名（未指定時はファイル名）
description: Use when reviewing TypeScript changes # task 関連での読込判定に使われる
applyTo: "**/*.{ts,tsx,js,jsx}" # 自動適用パターン（未指定かつ description なしなら手動添付のみ）
---
```

## VS Code 設定

```json
{
  "github.copilot.chat.codeGeneration.useInstructionFiles": true,
  "github.copilot.chat.reviewSelection.instructions": [
    { "text": "Review for bugs, security, and performance." },
    { "file": ".github/instructions/code-review.instructions.md" }
  ],
  "github.copilot.chat.commitMessageGeneration.instructions": [
    { "text": "Use Conventional Commits format." }
  ]
}
```

- 設定ベースの指示で残っているのは review / commit message / PR description（`github.copilot.chat.pullRequestDescriptionGeneration.instructions`）だけ。code generation / test generation の設定ベース指示は 1.102 で非推奨。
- `chat.instructionsFilesLocations`、`chat.agentSkillsLocations`、`chat.agentFilesLocations`、`chat.modeFilesLocations` は非推奨（Local agent のみ）。サポート済みの場所へ移す。

## Custom Agent フォーマット

```markdown
---
name: Code Reviewer
description: Expert code reviewer
tools: ["search/codebase", "execute/runInTerminal", "githubRepo"]
---

You are a senior code reviewer...
```

- ツール ID は `search/codebase`、`edit/editFiles`、`execute/runInTerminal`、`web/fetch` のような `<set>/<tool>` 形式。旧フラット名（`codebase`、`terminal`、`runCommands`、`fetch`）は使わない。
- `infer` は非推奨。`user-invocable`（picker 表示）と `disable-model-invocation`（subagent 呼出し抑止）を使う。拡張の agent picker では `user-invocable: false` を除外する。
- `.prompt.md` の `tools:` は allowlist で、選択中/参照先 agent のツールを上書きする。汎用 prompt では省略し、恒常的なロール/ツール境界は `.agent.md` に置く。prompt の frontmatter は `mode:` ではなく `agent:`。
- 本文でのツール参照は `#tool:web/fetch` のように書く。

## 公式リソース

| リソース            | URL                                                                        |
| ------------------- | -------------------------------------------------------------------------- |
| Custom Instructions | https://code.visualstudio.com/docs/agent-customization/custom-instructions |
| Prompt Files        | https://code.visualstudio.com/docs/agent-customization/prompt-files        |
| Custom Agents       | https://code.visualstudio.com/docs/agent-customization/custom-agents       |
| Agent Skills        | https://code.visualstudio.com/docs/agent-customization/agent-skills        |
| Tools reference     | https://code.visualstudio.com/docs/agents/reference/tools-reference        |

読込状況の確認は Chat view 右クリック → Diagnostics、または **Developer: Open Agent Debug Logs**。
