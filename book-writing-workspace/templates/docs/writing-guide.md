# Writing Workflow Guide

Book writing workflow for "{{BOOK_TITLE}}".

## Quick Reference

### Writing Workflow

| Step       | Action                            | Description     |
| ---------- | --------------------------------- | --------------- |
| Key Points | Write in `01_contents_keyPoints/` | Create outline  |
| Draft      | Write in `02_contents/`           | Full manuscript |
| Review     | `@writing-reviewer`               | P1/P2/P3 review |
| Convert    | `@converter`                      | Re:VIEW to PDF  |

### Git Prompts

| Prompt             | Action          |
| ------------------ | --------------- |
| `/gc_Commit`       | Commit          |
| `/gcp_Commit_Push` | Commit and push |
| `/gpull`           | Pull            |

## Folder Structure

```text
01_contents_keyPoints/  # Outlines
02_contents/            # Final manuscripts
03_re-view_output/      # Re:VIEW and PDF
04_images/              # Images
99_material/            # Reference materials
docs/                   # Documentation
scripts/                # Utility scripts
```

## Templates

| Template                                                         | Usage                  |
| ---------------------------------------------------------------- | ---------------------- |
| [template-chapter-intro.md](templates/template-chapter-intro.md) | `ch*-00` chapter intro |
| [template-section.md](templates/template-section.md)             | `ch*-01~` section file |

## Reference Documents

| File                                                                                                 | Content           |
| ---------------------------------------------------------------------------------------------------- | ----------------- |
| [writing.instructions.md](../.github/instructions/writing/writing.instructions.md)                   | Style rules       |
| [writing-notation.instructions.md](../.github/instructions/writing/writing-notation.instructions.md) | Notation rules    |
| [writing-heading.instructions.md](../.github/instructions/writing/writing-heading.instructions.md)   | Heading levels    |
| [naming-conventions.md](naming-conventions.md)                                                       | File naming       |
| [page-allocation.md](page-allocation.md)                                                             | Word counts       |
| [AGENTS.md](../AGENTS.md)                                                                            | Agent definitions |

## Git Commit Format

```text
<type>(<scope>): <subject>
```

Examples:

- `feat(ch01): Add introduction`
- `fix(ch02): Correct terminology`
