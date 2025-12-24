# Agent Skills

A collection of Agent Skills for GitHub Copilot and Claude.

## Skills

| Skill | Description |
|-------|-------------|
| [azure-env-builder](azure-env-builder/) | Azure環境構築を支援するスキル。Bicepテンプレートの生成・検証 |
| [skill-creator](skill-creator/) | 新しいAgent Skillを作成するためのスキル |
| [skill-finder](skill-finder/) | Agent Skillsの検索・インストール・管理ツール |

## Usage

Copy the desired skill folder to your project's `.github/skills/` or `.claude/skills/` directory.

```bash
# Example: Copy skill-finder to your project
cp -r skill-finder /path/to/your/project/.github/skills/
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

yamapan ([@aktsmm](https://github.com/aktsmm))
