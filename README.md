# Agent Skills

A collection of Agent Skills for GitHub Copilot and Claude.

GitHub Copilot と Claude 向けの Agent Skills コレクションです。

## Skills

| Skill                                           | Description / 説明                                                                                  |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| [agentic-workflow-guide](agentic-workflow-guide/) | Guide for designing agentic workflows / エージェントワークフロー設計ガイド                          |
| [azure-env-builder](azure-env-builder/)         | Azure environment builder with Bicep templates / Azure 環境構築支援（Bicep テンプレート生成・検証） |
| [ocr-super-surya](ocr-super-surya/)             | GPU-optimized OCR using Surya / GPU最適化OCR（90+言語対応、Tesseractの2倍精度）                     |
| [skill-creator](skill-creator/)                 | Create new Agent Skills / 新しい Agent Skill を作成                                                 |
| [skill-finder](skill-finder/)                   | Search, install, and manage Agent Skills / Agent Skills の検索・インストール・管理                  |

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

MIT License - see [LICENSE](LICENSE) for details.

MIT ライセンス - 詳細は [LICENSE](LICENSE) を参照してください。

## Author / 作者

yamapan ([@aktsmm](https://github.com/aktsmm))
