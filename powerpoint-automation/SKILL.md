---
name: powerpoint-automation
description: Create professional PowerPoint presentations from various sources including web articles, blog posts, and existing PPTX files. Ideal for tech presentations, reports, and documentation.
license: Complete terms in LICENSE.txt
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# PowerPoint Automation

AI-powered PPTX generation using Orchestrator-Workers pattern.

## When to Use

- Convert web articles/blog posts to presentations
- Translate English PPTX to Japanese
- Create presentations using custom templates
- Generate technical presentations with code blocks

## Quick Start

**From Web Article:**

```
Create a 15-slide presentation from: https://zenn.dev/example/article
```

**From Existing PPTX:**

```
Translate this presentation to Japanese: input/presentation.pptx
```

## Workflow

```
TRIAGE → PLAN → PREPARE_TEMPLATE → EXTRACT → TRANSLATE → BUILD → REVIEW → DONE
```

| Phase   | Script/Agent              | Description            |
| ------- | ------------------------- | ---------------------- |
| EXTRACT | `extract_images.py`       | Content → content.json |
| BUILD   | `create_from_template.py` | Generate PPTX          |
| REVIEW  | PPTX Reviewer             | Quality check          |

## Key Scripts

→ **[references/SCRIPTS.md](references/SCRIPTS.md)** for complete reference

| Script                    | Purpose                                |
| ------------------------- | -------------------------------------- |
| `create_from_template.py` | Generate PPTX from content.json (main) |
| `reconstruct_analyzer.py` | Convert PPTX → content.json            |
| `extract_images.py`       | Extract images from PPTX/web           |
| `validate_content.py`     | Validate content.json schema           |
| `validate_pptx.py`        | Detect text overflow                   |

## content.json (IR)

All agents communicate via this intermediate format:

```json
{
  "slides": [
    { "type": "title", "title": "Title", "subtitle": "Sub" },
    { "type": "content", "title": "Topic", "items": ["Point 1"] }
  ]
}
```

→ **[references/schemas/content.schema.json](references/schemas/content.schema.json)**

## Templates

| Template                    | Purpose                 | Layouts    |
| --------------------------- | ----------------------- | ---------- |
| `assets/base_template.pptx` | Full-featured (English) | 11 layouts |
| `assets/template.pptx`      | Legacy (Japanese names) | 4 layouts  |

## Agents

→ **[references/agents/](references/agents/)** for definitions

| Agent         | Purpose               |
| ------------- | --------------------- |
| Orchestrator  | Pipeline coordination |
| Localizer     | Translation (EN ↔ JA) |
| PPTX Reviewer | Final quality check   |

## Design Principles

- **SSOT**: content.json is canonical
- **SRP**: Each agent/script has one purpose
- **Fail Fast**: Max 3 retries per phase
- **Human in Loop**: User confirms at PLAN phase

## References

| File                                    | Content              |
| --------------------------------------- | -------------------- |
| [SCRIPTS.md](references/SCRIPTS.md)     | Script documentation |
| [USE_CASES.md](references/USE_CASES.md) | Workflow examples    |
| [agents/](references/agents/)           | Agent definitions    |
| [schemas/](references/schemas/)         | JSON schemas         |
