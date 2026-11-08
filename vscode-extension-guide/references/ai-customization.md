# VS Code AI Customization Guide

拡張機能から AI カスタマイズ資産を同梱・検出・表示するときに必要な最小知識。先に harness を選び、editor での検出・schema 検証と runtime への転送・実行を分けて確認する。詳細は公式 [Agent customization](https://code.visualstudio.com/docs/agent-customization/overview) を正とする。

## ファイル種別と用途

| ファイル種別                | パス/命名規則                                                                                                  | 用途                               | 適用範囲                                                                                          |
| --------------------------- | -------------------------------------------------------------------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------- |
| **copilot-instructions.md** | `.github/copilot-instructions.md`                                                                              | プロジェクト全体のコーディング規約 | 全チャットリクエストに自動適用                                                                    |
| **Instructions Files** | `.github/instructions/**/*.instructions.md` | 対象別ルール | Copilot は作業対象の `applyTo`。Local は一致する file context または `description` による on-demand 読込 |
| **Prompt Files**            | `.github/prompts/*.prompt.md`                                                                                  | 再利用可能なタスク定義             | `/` で手動実行。Agent Host セッションでは非推奨・未読込（Local agent のみ。skill への移行を推奨） |
| **Custom Agents**           | `.github/agents/*.agent.md`                                                                                    | 専門エージェント                   | エージェント選択時、または subagent として                                                        |
| **AGENTS.md** | ルート／対象 directory | 複数ハーネス共通の形式 | Copilot は対象 file path、Codex は root→cwd の chain。Local の nested 読込は experimental、`chat.useAgentsMdFile` と `chat.useNestedAgentsMdFiles` が必要 |
| **Agent Skills**            | `.github/skills/<name>/SKILL.md`（ほか `.claude/skills/`, `.agents/skills/`, user は `~/.copilot/skills/` 等） | スクリプト・資料付きの手順         | `description` 一致で自動読込、`/<name>` でも実行                                                  |

## 拡張機能からの同梱

- Skill は `contributes.chatSkills: [{ "path": "./skills/<name>/SKILL.md" }]`。フォルダ名と frontmatter `name` が一致しないと読み込まれない（小文字・数字・ハイフン、最大 64 文字、名前空間 prefix 不可）。
- 他拡張の同梱資産を検出する場合の既知 root と manifest 宣言は SKILL.md の Extension Host 境界を参照する。

## Instructions File フォーマット

```yaml
---
name: Code Review # UI表示名（未指定時はファイル名）
description: Use when reviewing TypeScript changes # Local の on-demand 判定
applyTo: "**/*.{ts,tsx,js,jsx}" # optional、既定 pattern なし
---
```

Local で `description` と `applyTo` を両方省略すると手動添付のみ。description は pattern の追加条件ではない。Claude rules は `paths` 配列（省略時は general）。`excludeAgent` は Copilot feature 別の属性で harness 切替ではない。表にない field を即 unsupported とせず、[instruction reference](https://code.visualstudio.com/docs/agents/reference/custom-instructions-reference) の support matrix を確認する。リンク先本文も自動読込保証はなく、Local の `chat.includeReferencedInstructions` は既定 off。

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
- `chat.instructionsFilesLocations` / `chat.agentFilesLocations` は supported。`chat.agentSkillsLocations` は deprecated だが互換用に残り、いずれも VS Code は追加 location の資産を Agent Host へ転送する。旧 `chat.modeFilesLocations` は deprecated。独立 CLI/app は editor 設定を継承しないため native folders を推奨（[agents](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference#_local-harness-locations-and-migration)、[skills](https://code.visualstudio.com/docs/agent-customization/agent-skills#_local)）。

## Custom Agent フォーマット

Local example:

```markdown
---
name: Code Reviewer
description: Expert code reviewer
tools: ["search/codebase", "execute/runInTerminal", "githubRepo"]
---

You are a senior code reviewer...
```

- Local 個別 ID は上例の `<set>/<tool>` を使い、旧フラット名を避ける。Copilot では built-in aliases (`read` / `edit` / `search` / `execute` / `agent` / `web` / `todo`) と実 inventory を確認する。client/extension の canonical prefix や MCP `<server>/*` は保持し、prefix だけで Local-only と判定しない。
- `infer` は非推奨。`user-invocable`（picker 表示）と `disable-model-invocation`（subagent 呼出し抑止）を使う。拡張の agent picker では `user-invocable: false` を除外する。
- `.prompt.md` の `tools:` は allowlist で、選択中/参照先 agent のツールを上書きする。汎用 prompt では省略し、恒常的なロール/ツール境界は `.agent.md` に置く。prompt の frontmatter は `mode:` ではなく `agent:`。
- Local 本文では `#tool:web/fetch` のように参照する。Copilot の delegation は native `task`。`target` は editor 解釈のみを変え、Local の `agents` allowlist / handoffs は Copilot に移植されない（[field compatibility](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference#_harness-compatibility)）。

## 公式リソース

| リソース            | URL                                                                        |
| ------------------- | -------------------------------------------------------------------------- |
| Custom Instructions | https://code.visualstudio.com/docs/agent-customization/custom-instructions |
| Prompt Files        | https://code.visualstudio.com/docs/agent-customization/prompt-files        |
| Custom Agents       | https://code.visualstudio.com/docs/agent-customization/custom-agents       |
| Agent Skills        | https://code.visualstudio.com/docs/agent-customization/agent-skills        |
| Tools reference     | https://code.visualstudio.com/docs/agents/reference/tools-reference        |

読込状況の確認は Chat view 右クリック → Diagnostics、または **Developer: Open Agent Debug Logs**。
