# Writing Workflow Guide

Book writing workflow for "{{BOOK_TITLE}}".

---

## Quick Reference

### Writing Workflow

| Step       | Action                            | Description     |
| ---------- | --------------------------------- | --------------- |
| Key Points | Write in `01_contents_keyPoints/` | Create outline  |
| Draft      | Write in `02_contents/`           | Full manuscript |
| Review     | `@writing-reviewer`               | P1/P2/P3 review |
| Convert    | `@converter`                      | Re:VIEW → PDF   |

### Git Prompts

| Prompt             | Action          |
| ------------------ | --------------- |
| `/gc_Commit`       | Commit          |
| `/gcp_Commit_Push` | Commit and push |
| `/gpull`           | Pull            |

---

## Folder Structure

```
01_contents_keyPoints/  # Outlines (draft)
02_contents/            # Final manuscripts
03_re-view_output/      # Re:VIEW and PDF
04_images/              # Images
99_material/            # Reference materials
docs/                   # Documentation
scripts/                # Utility scripts
```

---

## Agents

| Agent               | Role               | Example                         |
| ------------------- | ------------------ | ------------------------------- |
| `@writing`          | Write manuscripts  | `@writing Write ch01`           |
| `@writing-reviewer` | Review             | `@writing-reviewer Review ch01` |
| `@converter`        | Re:VIEW conversion | `@converter Convert all`        |
| `@orchestrator`     | Coordinate         | `@orchestrator Write chapter 1` |

---

## Reference Documents

| File                                                                                              | Content           |
| ------------------------------------------------------------------------------------------------- | ----------------- |
| [writing.instructions.md](.github/instructions/writing/writing.instructions.md)                   | Style rules       |
| [writing-notation.instructions.md](.github/instructions/writing/writing-notation.instructions.md) | Notation rules    |
| [naming-conventions.md](naming-conventions.md)                                                    | File naming       |
| [page-allocation.md](page-allocation.md)                                                          | Word counts       |
| [AGENTS.md](../AGENTS.md)                                                                         | Agent definitions |

---

## Git Commit Format

```
<type>(<scope>): <subject>

Example: feat(ch01): Add introduction
         fix(ch02): Correct terminology
```

**Types**: `feat` / `fix` / `docs` / `refactor`

⚠️ Do not `git push` unless explicitly instructed
