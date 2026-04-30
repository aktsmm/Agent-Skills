---
name: powerpoint-automation
description: Create and edit professional PowerPoint presentations from web articles, blog posts, existing PPTX files, or templates. Use when creating PPTX, converting articles to slides, translating presentations, editing open PowerPoint files, or doing COM Automation / RefURL / overflow review work.
argument-hint: "変換したい URL・PPTX・テンプレート、または編集内容"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# PowerPoint Automation

AI-powered PPTX generation using Orchestrator-Workers pattern.

## When to Use

- Web 記事やブログをスライド化したいとき
- 既存 PPTX を翻訳・再構成したいとき
- 開いている PPTX を COM Automation で直接編集したいとき
- テンプレートベースで PPTX を生成したいとき
- content.json を SSOT にして、抽出・翻訳・生成・レビューを分離したいとき

## Quick Start

**From Web Article**

```text
Create a 15-slide presentation from: https://zenn.dev/example/article
```

**From Existing PPTX**

```text
Translate this presentation to Japanese: input/presentation.pptx
```

**Edit Open PPTX with COM**

```text
Edit the currently open PowerPoint deck with COM Automation and verify RefURL, notes, overflow, and hyperlinks.
```

## Workflow

```text
TRIAGE → PLAN → PREPARE_TEMPLATE → EXTRACT → TRANSLATE → BUILD → REVIEW → DONE
```

| Phase   | Main Actor                | Purpose                          |
| ------- | ------------------------- | -------------------------------- |
| EXTRACT | `extract_images.py`       | Source -> content.json           |
| BUILD   | `create_from_template.py` | content.json -> PPTX             |
| REVIEW  | PPTX Reviewer             | Overflow / consistency / quality |

## Core Assets

### Scripts

| Script                    | Purpose                                           |
| ------------------------- | ------------------------------------------------- |
| `create_from_template.py` | content.json から PPTX を生成するメインスクリプト |
| `reconstruct_analyzer.py` | 既存 PPTX を content.json に戻す                  |
| `extract_images.py`       | PPTX / Web から画像を抽出する                     |
| `validate_content.py`     | content.json のスキーマ検証                       |
| `validate_pptx.py`        | overflow などの検証                               |

詳細は [references/SCRIPTS.md](references/SCRIPTS.md) を参照。

### content.json

`content.json` はこの skill の SSOT。抽出、翻訳、生成、レビューの間は常にこれを基準にする。

```json
{
  "slides": [
    { "type": "title", "title": "Title", "subtitle": "Sub" },
    { "type": "content", "title": "Topic", "items": ["Point 1"] }
  ]
}
```

スキーマ詳細は [references/schemas/content.schema.json](references/schemas/content.schema.json) を参照。

### Template

標準テンプレートは `assets/template.pptx`。レイアウトや用途の詳細は template 側で管理し、main SKILL には最小限だけ残す。

```bash
python scripts/create_from_template.py assets/template.pptx content.json output.pptx --config assets/template_layouts.json
```

### Agents

| Agent         | Purpose                 |
| ------------- | ----------------------- |
| Orchestrator  | Pipeline coordination   |
| Localizer     | Translation (EN <-> JA) |
| PPTX Reviewer | Final quality check     |

定義詳細は [references/agents/](references/agents/) を参照。

## Operating Rules

- **SSOT**: content.json を正とする
- **One phase, one purpose**: 抽出・翻訳・生成・レビューを混ぜない
- **Fail fast**: 問題が出たら次フェーズへ無理に進めない
- **Human in loop**: PLAN でユーザー確認を入れる
- **Technical content is verified content**: Azure / Microsoft の内容は MCP で一次情報確認してから入れる
- **PowerPoint lock first**: 開いている PPTX に対して python-pptx で上書きしない
- **COM for open decks**: 開いている PPTX や既存 deck の直接編集は [references/instructions/com-automation.instructions.md](references/instructions/com-automation.instructions.md) を参照する
- **Operational text stays in notes**: 運営メモはスライド面に出さない
- **Architecture diagrams use shapes**: ASCII art ではなく図形で組む
- **Appendix URLs use Title - URL**: 参考 URL の表示形式は統一する

## Reference Map

### Frequently Needed

- [references/SCRIPTS.md](references/SCRIPTS.md)
- [references/USE_CASES.md](references/USE_CASES.md)
- [references/content-guidelines.md](references/content-guidelines.md)
- [references/IMPLEMENTATION_PATTERNS.md](references/IMPLEMENTATION_PATTERNS.md)
- [references/instructions/com-automation.instructions.md](references/instructions/com-automation.instructions.md)

### Go to Implementation Patterns For

- technical content verification workflow
- shape-based architecture diagrams
- hyperlink batch processing
- font theme token resolution
- section / layout XML manipulation
- hidden slide cleanup
- COM Automation editing rules
- RefURL placement and hyperlink auditing
- file-lock workaround and post-processing
- 16:9 centering issues
- template corruption recovery
- video embedding via ZIP direct manipulation

## Done Criteria

- source と goal が固定されている
- content.json を正として各フェーズが分離されている
- template / layout の前提が確認できている
- technical content は一次情報確認が済んでいる
- operational text がスライド面に出ていない
- build 後に overflow / consistency / hyperlink をレビューできている
