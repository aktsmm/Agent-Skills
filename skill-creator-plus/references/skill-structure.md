# Skill Structure

Detailed guide for skill anatomy, bundled resources, and progressive disclosure patterns.

## Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts)
```

## SKILL.md Structure

Every SKILL.md consists of:

- **Frontmatter** (YAML): Contains `name` and `description` fields. These are the only fields Claude reads to determine when the skill gets used.
- **Body** (Markdown): Instructions and guidance. Only loaded AFTER the skill triggers.

## Bundled Resources

### Scripts (`scripts/`)

Executable code for tasks requiring deterministic reliability or repeatedly rewritten.

- **When to include**: Same code rewritten repeatedly or deterministic reliability needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, executed without loading into context

### References (`references/`)

Documentation loaded as needed into context.

- **When to include**: Documentation Claude should reference while working
- **Examples**: `references/schema.md`, `references/api_docs.md`
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in ONE place only

### Assets (`assets/`)

Files used in output, not loaded into context.

- **When to include**: Files used in final output
- **Examples**: `assets/logo.png`, `assets/template.pptx`
- **Use cases**: Templates, images, icons, boilerplate code

## What NOT to Include

Do NOT create extraneous documentation:

- ❌ README.md
- ❌ INSTALLATION_GUIDE.md
- ❌ CHANGELOG.md
- ❌ QUICK_REFERENCE.md

## Progressive Disclosure

Skills use a three-level loading system:

| Level       | Location    | Size        | Loaded When         |
| ----------- | ----------- | ----------- | ------------------- |
| 1. Metadata | Frontmatter | ~100 words  | Always              |
| 2. Body     | SKILL.md    | < 150 lines | When skill triggers |
| 3. Details  | references/ | Unlimited   | On demand           |

### Pattern 1: High-level guide with references

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber: [code example]

## Advanced features

- **Form filling**: See [FORMS.md](FORMS.md)
- **API reference**: See [REFERENCE.md](REFERENCE.md)
```

### Pattern 2: Domain-specific organization

```
bigquery-skill/
├── SKILL.md (overview)
└── references/
    ├── finance.md
    ├── sales.md
    └── product.md
```

When user asks about sales, Claude only reads sales.md.

### Pattern 3: Variant-based organization

```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

### Guidelines

- **Avoid deeply nested references** - Keep references one level deep from SKILL.md
- **Structure longer files** - For files > 100 lines, include TOC at top
