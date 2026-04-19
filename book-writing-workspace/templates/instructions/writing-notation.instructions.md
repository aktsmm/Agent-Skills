---
applyTo: "02_contents/**/*.md"
---

# Writing Notation Instructions

Consistent notation and terminology rules.

## Numbers

| Type        | Rule           | Example     |
| ----------- | -------------- | ----------- |
| Quantities  | Half-width     | 100個、5章  |
| Years       | Half-width     | 2024年      |
| Percentages | Half-width + % | 80%、50%    |
| Ranges      | Half-width + ~ | 1~10、5~6章 |

## Punctuation

| Symbol        | Japanese | Usage               |
| ------------- | -------- | ------------------- |
| Period        | 。       | End of sentence     |
| Comma         | 、       | Clause separator    |
| Colon         | ：       | Full-width in prose |
| Parentheses   | （）     | Full-width in prose |
| Quotes        | 「」     | Terminology, titles |
| Double quotes | 『』     | Book titles         |

## Technical Terms

### First Occurrence

Format: 日本語（English）

Examples:

- 機密性（Confidentiality）
- 多層防御（Defense in Depth）
- データ損失防止（Data Loss Prevention、DLP）

### Subsequent Occurrences

Use Japanese only, or the acronym if already introduced.

## Product Names

- Write exactly as official documentation
- Examples:
  - Microsoft Purview
  - Azure Active Directory
  - GitHub Copilot

## Diagram Labels

- Default diagram labels, box titles, and helper text to the main manuscript language.
- Keep original-language operation names, feature names, or product names only when they are the terms readers are expected to recognize.
- When needed, combine both forms instead of choosing one rigidly.
  - Example: `pull (pull)` or `pull (fetch updates)` depending on the audience language and book style
- Do not leave the entire diagram in English when the surrounding manuscript is not, unless you are reproducing an official UI or quoting a source artifact.
- Keep explanatory text in diagrams reader-facing and plain; avoid tool-author jargon.

## Consistency Checklist

- [ ] Numbers are half-width
- [ ] Punctuation follows rules
- [ ] Terms explained on first use
- [ ] Product names match official
- [ ] Acronyms introduced properly
- [ ] Diagram labels follow the manuscript language policy
