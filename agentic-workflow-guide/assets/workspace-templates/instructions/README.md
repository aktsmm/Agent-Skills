# `.github/instructions` ディレクトリ

エージェントが読み込むドメイン別ガイドラインを置く場所。

## フロントマター形式（MANDATORY）

各 `.instructions.md` ファイルは **必ず** 以下のフロントマターで始めること:

```yaml
---
applyTo: "**"
---
```

### applyTo パターン

| パターン       | 適用対象                     |
| -------------- | ---------------------------- |
| `"**"`         | 全ファイル（デフォルト推奨） |
| `"*.py"`       | Pythonファイルのみ           |
| `"src/**"`     | srcフォルダ配下のみ          |
| `"*.ts,*.tsx"` | TypeScript関連のみ           |

### 例

```yaml
---
applyTo: "*.py"
---
# Python Instructions

Pythonコードを書く際のルール...
```

---

## ディレクトリ構成

```
instructions/
├── README.md                              # このファイル
├── core/                                  # コア・共通ルール
│   ├── communication.instructions.md      # コミュニケーションスタイル
│   └── security.instructions.md           # セキュリティガイドライン
├── dev/                                   # 開発ツール系
│   ├── git.instructions.md                # Git操作規約
│   ├── terminal.instructions.md           # ターミナル操作規約
│   ├── python.instructions.md             # Python環境設定
│   └── nodejs.instructions.md             # Node.js環境設定
├── agents/                                # エージェント設計系
│   ├── agent-design.instructions.md       # 設計原則
│   └── agents.instructions.md             # .github/agents 向けルール
└── integrations/                          # 外部連携系
    └── microsoft-docs.instructions.md     # MS Docs MCP連携
```

## カテゴリ説明

| カテゴリ        | 目的                       | 追加例                        |
| --------------- | -------------------------- | ----------------------------- |
| `core/`         | 全エージェント共通のルール | レビュー規約、命名規則        |
| `dev/`          | 開発ツール操作のルール     | Docker, npm, pytest           |
| `agents/`       | エージェント設計・運用     | オーケストレーション、IR 設計 |
| `integrations/` | 外部サービス連携           | Azure CLI, GitHub API, OpenAI |

## カスタマイズ

- ファイル名は `<topic>.instructions.md` のようにしておくと分かりやすい。
- コーディング規約やドキュメント方針など、共有したいルールを簡潔にまとめる。
- agent（旧 runSubagent）の利用条件や「軽量タスクはメインで対応する」といったナレッジもここに書いておけば、各エージェントから参照できる。

新しいインストラクションを追加する場合は、適切なカテゴリフォルダに配置してね。
