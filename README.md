# Agent Skills

A collection of Agent Skills for GitHub Copilot and Claude.

GitHub Copilot と Claude 向けの Agent Skills コレクションです。

## Skills

| Skill                                   | Description / 説明                                                  | License                         |
| --------------------------------------- | ------------------------------------------------------------------- | ------------------------------- |
| [azure-env-builder](azure-env-builder/) | Azure environment builder with Bicep templates / Azure 環境構築支援 | MIT                             |
| [skill-creator](skill-creator/)         | Create new Agent Skills / 新しい Agent Skill を作成                 | Apache 2.0 (based on Anthropic) |
| [skill-finder](skill-finder/)           | Search, install, and manage Agent Skills / スキル検索・管理         | MIT                             |

## Usage / 使い方

Copy the desired skill folder to your project's `.github/skills/` or `.claude/skills/` directory.

使いたいスキルフォルダをプロジェクトの `.github/skills/` または `.claude/skills/` にコピーしてください。

```bash
# Example / 例
cp -r skill-finder /path/to/your/project/.github/skills/
```

## Structure / 構成

Each skill follows this structure / 各スキルは以下の構成です：

```
skill-name/
├── SKILL.md          # Skill definition / スキル定義
├── README.md         # Documentation / ドキュメント (optional)
├── LICENSE.txt       # License / ライセンス
├── references/       # Reference files / 参照ファイル
└── scripts/          # Helper scripts / ヘルパースクリプト
```

## License / ライセンス

**Each skill has its own license. See the LICENSE file in each skill directory.**

**各スキルには個別のライセンスがあります。各スキルディレクトリ内の LICENSE ファイルを参照してください。**

| Skill             | License    | Source                                                                                                  |
| ----------------- | ---------- | ------------------------------------------------------------------------------------------------------- |
| azure-env-builder | MIT        | Original                                                                                                |
| skill-creator     | Apache 2.0 | Based on [Anthropic skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) |
| skill-finder      | MIT        | Original                                                                                                |

## Author / 作者

yamapan ([@aktsmm](https://github.com/aktsmm))
