---
name: update-slide-json-pdf
description: >-
  Design and build a one-update-one-slide pipeline that stores each slide as schema-validated JSON, renders it to a PDF page with HTML + headless Chrome, and lets a static site merge selected pages into one PDF in the browser (cover / TOC / summary / ending). Use when asked for slide JSON schema design, cloud (agentic workflow) slide generation, HTML-to-PDF slide rendering, on-demand PDF download from a static site, or "PowerPoint-less" per-item slides. Not for editing .pptx files or template-based PPTX decks.
argument-hint: "対象（更新情報など）と、スライド 1 枚に載せる項目・出力先（JSON / PDF / 静的サイト）"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Update Slide JSON → PDF

One item = one slide. The **JSON is the source of truth**; HTML, PDF and site downloads are regenerated from it. Details and pitfalls: [Pipeline & Gotchas](references/pipeline.md).

## When to Use

- 更新情報・リリース情報などを「1 件 1 枚」で顧客向けに見せたい、JSON と PDF の両方で配りたい
- スライド JSON スキーマ、根拠付き（claim 単位の出典）の文章生成、クラウド（GitHub Agentic Workflows）での自動生成
- 静的サイト（GitHub Pages）で、選択した件だけを 1 つの PDF（または編集できる PPTX）にまとめてダウンロードさせたい

## Design Rules (decide first)

1. **Slide kind decides the panels** (GA / Preview / retirement / announcement / other). Share one JSON schema; vary only panel templates. Rule-based kind from source fields, never guessed from prose.
2. **Fixed info strip on every slide**: 誰に関係するか (bold the target) / 嬉しい点 or 変わること / 対応の要否. Add Before→After only with a first-party source; add 4–6 glossary terms (product, feature, jargon, GA/Preview label) with one-line definitions from official docs.
3. **Write only what is verified; omit the rest.** Rendered text must never contain internal-memo wording (未確認 / 記載なし / 要確認 / 推定 / AI 生成 / データ時点 / （原文）). Absent evidence → drop the element (e.g. no region stamp) instead of showing "unknown". Enforce with a validator, not instructions alone.
4. **Claims carry provenance** (origin, assertion, verification, evidence URLs on an allowlist of official hosts). Recommendations are never `verified`.
5. **Links must be real**: announcement + up to 3 official detail pages, Japanese locale first, locale field must match the URL.
6. Footer holds ID / category / links; per-page "created at" and generator credits belong only on the cover/ending of a bundle.
7. Cover / ending use the vendor-style palette (white field, brand blue, navy footer band); the bundle cover states period and count only.

## Pipeline

JSON (agent writes) → deterministic validate → HTML → Chrome PDF (fit loop) → per-item PDFs at deploy time (not in Git) → browser merges selected ones. Keep generation by an agent and validation/rendering in deterministic steps, then auto-merge only PRs that touch exactly one slide file and pass validation + a render check, pinned to the PR head SHA.

## Access control on a static site (when asked)

Public per-item files defeat any password, so publish only a free sample (the newest item) in plain form and encrypt the rest (AES-GCM, PBKDF2 key; the secret stays in repository secrets, only salt/iterations are published; fail closed without the secret). The browser prompts on the download button and decrypts. Say plainly that this is a light gate: the slide JSON/API stay public. Details: [Pipeline](references/pipeline.md).

## Done Criteria

- Validator passes (schema + forbidden phrases + host allowlist + locale/URL match), render shows zero overflow, and the rendered pages were looked at.
- The merged PDF has uniform page size and working links; Japanese glyphs verified by viewing a page, not only by text extraction.
- An editable PPTX, if requested, is opened in desktop PowerPoint and viewed per slide (text boxes stay inside their cards, links work); a wrap estimator alone is not proof.
