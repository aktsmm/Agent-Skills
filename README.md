# Agent Skills

A collection of Agent Skills for GitHub Copilot and Claude.

GitHub Copilot と Claude 向けの Agent Skills コレクションです。

## Demo

### OCR Super Surya

![OCR Demo](assets/image.png)

## Skills

| Skill                                             | Description / 説明                                                                                                 |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| [agentic-workflow-guide](agentic-workflow-guide/) | Guide for designing agentic workflows / エージェントワークフロー設計ガイド                                         |
| [azure-env-builder](azure-env-builder/)           | ⚠️ **Alpha** - Azure environment builder with Bicep templates / Azure 環境構築支援（Bicep テンプレート生成・検証） |
| [browser-max-automation](browser-max-automation/) | Browser automation via Playwright MCP / Playwright MCP によるブラウザ自動操作                                      |
| [code-simplifier](code-simplifier/)               | Simplify and refactor complex code / コードの簡略化・リファクタリング支援                                          |
| [drawio-diagram-forge](drawio-diagram-forge/)     | Create draw.io diagrams from text / テキストから draw.io 図を生成                                                  |
| [ocr-super-surya](ocr-super-surya/)               | GPU-optimized OCR using Surya / GPU 最適化 OCR（90+言語対応、Tesseract の 2 倍精度）                               |
| [powerpoint-automation](powerpoint-automation/)   | 🆕 Create PPTX from web articles or existing files / Web記事や既存ファイルからPowerPoint自動生成                   |
| [skill-finder](skill-finder/)                     | Search, install, and manage Agent Skills / Agent Skills の検索・インストール・管理                                 |

## Usage / 使い方

### 🚀 Recommended: Agent Skill Ninja (VS Code Extension)

Install the **Agent Skill Ninja** extension for easy skill management:

**Agent Skill Ninja** 拡張機能でスキル管理が簡単に：

**[📦 Agent Skill Ninja - VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=yamapan.agent-skill-ninja)**

- 🔍 Browse and search skills / スキルの検索・閲覧
- 📥 One-click install to your project / ワンクリックでプロジェクトにインストール
- 🔄 Auto-update installed skills / インストール済みスキルの自動更新
- 📋 View skill details and documentation / スキル詳細とドキュメントの表示

### Manual Installation / 手動インストール

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
├── LICENSE.txt       # License / ライセンス
├── references/       # Reference files / 参照ファイル
└── scripts/          # Helper scripts / ヘルパースクリプト
```

## License / ライセンス

Each skill has its own license in `LICENSE.txt`. Please refer to the license file in each skill folder.

各スキルは個別のライセンスを持ちます。各スキルフォルダ内の `LICENSE.txt` を参照してください。

- **Self-created skills / 自作スキル**: CC BY-NC-SA 4.0
- **External skills / 外部由来**: Original license retained (MIT, Apache 2.0, etc.)


## Changelog / 更新履歴

| Date       | Skill               | Changes                                                                 |
| ---------- | ------------------- | ----------------------------------------------------------------------- |
| 2026-01-19 | drawio-diagram-forge | 🔥 Azure icons 35→80+ (OpenAI, Databricks, IoT Hub, etc.), AWS→Azure migration patterns, ID duplicate check |
| 2026-01-15 | drawio-diagram-forge | Initial release                                                         |
## Author / 作者

yamapan ([@aktsmm](https://github.com/aktsmm))
