# VS Code Custom Agents — 配置・アクセス制御リファレンス

## 配置ルール（Critical）

### `.github/agents/` は直下に置く

```
✅ 認識される
.github/agents/
├── orchestrator.agent.md
├── coding.executor.md
└── quality.reviewer.md

❌ 認識されない
.github/agents/
├── executors/
│   └── coding.executor.md    ← 無視される
└── reviewers/
    └── quality.reviewer.md   ← 無視される
```

> **根拠**: 公式は `"VS Code detects any .md files in the .github/agents folder of your workspace as custom agents."` とだけ記載。
> サブディレクトリが認識されない点は 2026-02 の実証テストによる（instructions は再帰スキャンされるので混同しない）。

### 配置場所の選択肢

| 場所                                     | 用途                                                          |
| ---------------------------------------- | ------------------------------------------------------------- |
| `.github/agents/` (ワークスペース)       | チーム共有。そのワークスペースでのみ有効                      |
| `.claude/agents/` (ワークスペース)       | Claude 形式（`name` 必須、`tools` はカンマ区切り文字列）      |
| `~/.copilot/agents` / `~/.claude/agents` | 個人用。全ワークスペースで有効                                |
| GitHub organization                      | `github.copilot.chat.organizationCustomAgents.enabled` で検出 |

- Agent Host セッション（Copilot 等）は user agent を VS Code profile ではなく host のフォルダー（上表）から読む。profile 内の旧 user agent は migration が必要。
- `chat.agentFilesLocations` / `chat.modeFilesLocations` は非推奨（Local agent のみ参照）。追加パスやサブフォルダ指定に使わず、上表の場所へ移す。
- monorepo で親 repo の agent を使うには `chat.useCustomizationsInParentRepositories` を有効にする。

### ファイル拡張子

| 場所              | 拡張子                                         |
| ----------------- | ---------------------------------------------- |
| `.github/agents/` | `.agent.md` または `.md`（どちらも認識される） |
| `.claude/agents/` | `.md`（Claude Code 互換）                      |

## アクセス制御（3段階）

### frontmatter プロパティ

| プロパティ                 | デフォルト   | 効果                                      |
| -------------------------- | ------------ | ----------------------------------------- |
| `user-invocable`           | `true`       | `false` → ピッカーに非表示                |
| `disable-model-invocation` | `false`      | `true` → サブエージェントとして呼ばれない |
| `agents` (親側)            | `*` (全許可) | 特定エージェント名リスト → 許可リスト     |

> **重要**: `agents` リストに明示すると `disable-model-invocation: true` をオーバーライドできる。

### パターン早見表

```yaml
# 1. ユーザーが直接呼ぶ + サブエージェントとしても呼ばれる（デフォルト）
user-invocable: true    # (省略可)

# 2. サブエージェント専用（ピッカー非表示）
user-invocable: false

# 3. ユーザー専用（他エージェントから呼ばれない）
disable-model-invocation: true

# 4. 特定の親からのみ呼ばれるサブエージェント
user-invocable: false
disable-model-invocation: true
# → 親側の agents リストに明示して呼ぶ
```

### ⚠️ Deprecated プロパティ

| 旧             | 新                                                         | 移行方法                                                   |
| -------------- | ---------------------------------------------------------- | ---------------------------------------------------------- |
| `infer: true`  | `user-invocable: true` (デフォルト)                        | 行を削除するか置換                                         |
| `infer: false` | `user-invocable: false` / `disable-model-invocation: true` | 隠したいのがピッカーか subagent 呼び出しかで選ぶ（両方可） |
| `.chatmode.md` | `.agent.md`                                                | リネームして対応場所へ                                     |

`target` は非推奨ではない（`vscode` / `github-copilot`）。GitHub Copilot cloud agent 向けに `mcp-servers` を使うときは `target: github-copilot`。

## Orchestrator + Workers パターン

```yaml
# orchestrator.agent.md
---
name: orchestrator
user-invocable: true
disable-model-invocation: true
tools: ["search", "execute", "agent"] # "agent" が必須
agents:
  - coding-executor
  - quality-reviewer
---
```

```yaml
# coding.executor.md
---
name: coding-executor
user-invocable: false
tools: ["search", "execute"]
---
```

**ポイント:**

- orchestrator に `agent` ツールを含めないとサブエージェント呼び出しが機能しない
- `agents` リストで呼び出せるサブエージェントを制限する
- `agents: []` で全サブエージェント利用を禁止
- `agents: ['*']` または省略で全許可
- agent 名は大文字小文字を区別する（`name` と完全一致）

## トラブルシューティング

| 症状                             | 原因                      | 対処                          |
| -------------------------------- | ------------------------- | ----------------------------- |
| ピッカーに出ない                 | サブフォルダに配置        | `.github/agents/` 直下に移動  |
| ピッカーに出ない                 | `user-invocable: false`   | 意図的なら OK                 |
| `runSubagent` で "not found"     | 認識されていない          | 直下に配置されているか確認    |
| サブエージェントが呼ばれない     | 親に `agent` ツールがない | `tools` に `"agent"` を追加   |
| 意図しないエージェントが呼ばれる | `agents` リスト未指定     | 親側で `agents: [...]` を明示 |

## デバッグ方法

1. **Chat Diagnostics**: チャットビューで右クリック → Diagnostics で認識エージェント一覧とエラーを確認（詳細は Agent Debug Logs）
2. **`runSubagent` テスト**: サブエージェントを直接呼び出して応答確認
3. **セッションコンテキスト確認**: `<agents>` タグに何が注入されているかで認識状態を判定
