---
applyTo: "**"
---

# Git Commit Format Instructions

Standardized commit message format for the book project.

## Format

```
<type>(<scope>): <subject>
```

## Types

| Type       | Usage                                 |
| ---------- | ------------------------------------- |
| `feat`     | New content (chapter, section)        |
| `fix`      | Corrections (typos, errors)           |
| `docs`     | Documentation updates                 |
| `refactor` | Structure changes (no content change) |
| `style`    | Formatting only                       |

## Scope

- Chapter: `ch01`, `ch02`, etc.
- Section: `ch01-a`, `ch05-b`
- Document type: `agents`, `instructions`, `scripts`
- General: `all`, `config`

## Subject

- Imperative mood (Add, Fix, Update)
- No period at end
- Under 50 characters

## Examples

```
feat(ch01): Add introduction section
fix(ch03): Correct terminology for DLP
docs(agents): Update writing agent permissions
refactor(ch05): Split long section into subsections
style(all): Fix heading levels
```

## Japanese Examples

```
feat(ch01): データセキュリティ概要を追加
fix(ch02): 誤字を修正
docs(instructions): 執筆ガイドを更新
```

## Commit Checklist

- [ ] Type matches the change
- [ ] Scope identifies the area
- [ ] Subject is clear and concise
- [ ] No sensitive information included
