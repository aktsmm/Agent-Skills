# Agent Skills

A collection of Agent Skills for GitHub Copilot and Claude.

GitHub Copilot と Claude 向けの Agent Skills コレクションです。

## Demo

### OCR Super Surya

![OCR Demo](assets/image.png)

### Draw.io Diagram Forge

![Diagram Demo](https://github.com/user-attachments/assets/095bd5b7-e435-45ad-b102-f1d63cb52c6e)

## Skills

| Skill | Description / 説明 |
| ----- | ------------------ |
| [agentic-workflow-guide](agentic-workflow-guide/) | Guide for designing agentic workflows / エージェントワークフロー設計ガイド |
| [azure-env-builder](azure-env-builder/) | ⚠️ **Alpha** - Azure environment builder with Bicep templates / Azure 環境構築支援（Bicep テンプレート生成・検証） |
| [browser-max-automation](browser-max-automation/) | Browser automation via Playwright MCP / Playwright MCP によるブラウザ自動操作 |
| [code-simplifier](code-simplifier/) | Guide for simplifying code after coding sessions / コーディング後のコード整理・簡略化ガイド |
| [drawio-diagram-forge](drawio-diagram-forge/) | Generate draw.io editable diagrams from text/images / テキスト・画像から draw.io 図面を生成 |
| [ocr-super-surya](ocr-super-surya/) | GPU-optimized OCR using Surya / GPU 最適化 OCR（90+言語対応、Tesseract の 2 倍精度） |
| [skill-creator](skill-creator/) | Create new Agent Skills / 新しい Agent Skill を作成 |
| [skill-finder](skill-finder/) | Search, install, and manage Agent Skills / Agent Skills の検索・インストール・管理 |

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
├── LICENSE           # License / ライセンス (optional)
├── references/       # Reference files / 参照ファイル
└── scripts/          # Helper scripts / ヘルパースクリプト
```

## License / ライセンス

Each skill has its own license. See [LICENSE](LICENSE) for details.

各スキルは個別のライセンスを持ちます。詳細は [LICENSE](LICENSE) を参照してください。

- **Self-created skills / 自作スキル**: CC BY-NC-SA 4.0
- **External skills / 外部由来**: Original license retained (MIT, Apache 2.0, etc.)

## Author / 作者

yamapan ([@aktsmm](https://github.com/aktsmm))
