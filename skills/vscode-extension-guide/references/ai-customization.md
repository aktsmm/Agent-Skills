# VS Code AI Customization Guide

VS Code での AI カスタマイズ方法の包括的ガイド。

## ファイル種別と用途

| ファイル種別 | パス/命名規則 | 用途 | 適用範囲 |
|-------------|--------------|------|----------|
| **copilot-instructions.md** | `.github/copilot-instructions.md` | プロジェクト全体のコーディング規約 | 全チャットリクエストに自動適用 |
| **Instructions Files** | `*.instructions.md` | 言語/フレームワーク別ルール | `applyTo` パターンで条件適用 |
| **Prompt Files** | `*.prompt.md` | 再利用可能なタスク定義 | 手動で実行 |
| **Custom Agents** | `*.agent.md` | 専門エージェント | エージェント選択時に適用 |
| **AGENTS.md** | ルート or サブフォルダ | マルチエージェント環境用 | 全チャットに自動適用 |
| **SKILLS.md** | `~/.claude/skills/*/` or `.claude/skills/` | 複数ツール横断スキル | エージェント判断で適用 |

## Instructions File フォーマット

### ヘッダー（YAML frontmatter）

```yaml
---
name: Code Review              # UI表示名
description: Expert code review guidelines
applyTo: "**/*.{ts,tsx,js,jsx}"  # 自動適用パターン
---
```

### 主要プロパティ

| プロパティ | 説明 |
|-----------|------|
| `name` | UI表示名（未指定時はファイル名） |
| `description` | 説明文 |
| `applyTo` | 自動適用 glob パターン（未指定時は手動添付のみ） |

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
  ],
  "chat.instructionsFilesLocations": {
    ".github/instructions": true
  }
}
```

## 設定可能なシナリオ

| シナリオ | 設定キー |
|---------|---------|
| コードレビュー | `github.copilot.chat.reviewSelection.instructions` |
| コミットメッセージ | `github.copilot.chat.commitMessageGeneration.instructions` |
| PR タイトル/説明 | `github.copilot.chat.pullRequestDescriptionGeneration.instructions` |

## Custom Agent フォーマット

```markdown
---
name: Code Reviewer
description: Expert code reviewer
tools:
  - codebase
  - terminal
  - githubRepo
---

# Code Reviewer Agent

You are a senior code reviewer...

## Your Role
- Conduct thorough code reviews
- Identify bugs, security issues, and performance problems
```

## ディレクトリ構造例

```
.github/
├── copilot-instructions.md      # プロジェクト全体
├── instructions/
│   ├── code-review.instructions.md
│   ├── typescript.instructions.md
│   └── security.instructions.md
├── prompts/
│   ├── review-pr.prompt.md
│   └── refactor-file.prompt.md
└── agents/
    ├── code-reviewer.agent.md
    └── planner.agent.md
```

## 公式リソース

| リソース | URL |
|----------|-----|
| Custom Instructions | https://code.visualstudio.com/docs/copilot/customization/custom-instructions |
| Prompt Files | https://code.visualstudio.com/docs/copilot/customization/prompt-files |
| Custom Agents | https://code.visualstudio.com/docs/copilot/customization/custom-agents |
| Agent Skills | https://code.visualstudio.com/docs/copilot/customization/agent-skills |
| Awesome Copilot | https://github.com/github/awesome-copilot |

## Tips

- **glob パターン**: `applyTo: "**/*.py"` で Python ファイルのみに適用
- **ツール参照**: 本文内で `#tool:githubRepo` でツールを参照可能
- **生成コマンド**: `Chat: Configure Instructions` から Instructions ファイルを自動生成可能
- **同期**: Settings Sync で Instructions ファイルをデバイス間同期可能
