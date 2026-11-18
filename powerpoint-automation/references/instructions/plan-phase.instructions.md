# PLAN Phase Confirmation Process

**Before starting PPTX generation, always get user confirmation. Do not proceed automatically.**

---

## New PPTX from a Manuscript, Outline, or JSON

1. **PLAN**: Present a recommended method and approximate slide count for confirmation. Ask about audience, purpose, or design only when the answer changes the plan; do not re-ask known requirements or reconfirm a plan already approved. Offer user-facing choices (e.g.「標準デザインで初稿」or「指定テンプレートに合わせる」), not library names.
   - **Simple draft**: Use `create_ja_pptx.py` for supported text-first layouts when no design is prescribed. A divider slide is not a PowerPoint section.
   - **Specified design**: When a template or design must be preserved, prepare and verify its layouts and use `create_from_template.py` if it supports the required features. Do not substitute the simple draft route without approval.
   - **Required features**: Check builder support for native tables, editable diagrams, PowerPoint sections, hidden slides, and other requirements. If the proposed builder cannot preserve them, confirm a compatible method. If none is available, stop and offer a custom build or a reduced scope for approval; never silently drop features.
2. **BUILD**: Map agreed content into the [bundled schema](../schemas/content.schema.json); retain stable topic-to-slide mapping and separate visible text from permitted notes. [Validate the input](../SCRIPTS.md#quality-assurance); do not build if schema validation fails or did not run. Schema validity does not prove builder support. Use `--no-signature` with the Python builders unless the approved plan includes a signature. Use the next unused versioned `.pptx` path on every build; never overwrite a previous draft or a hand-edited deck.
3. **REVIEW**: Check slide count, order, text, required links and features against the plan. Compare all output notes against the approved notes, including on hidden or template-derived slides; reject extras. Render every slide for overflow and overlap before handoff, even for a draft. If rendering is unavailable, state that visual QA is pending; do not report the deck as verified.

## Items to Confirm (Web/Blog Source)

1. **Detail level/slide count**: Detailed / Standard / Summary version
2. **Template**: Select from available templates
3. **Image inclusion**: All (recommended) / Main only / None
4. **Code blocks**: Include (recommended) / Exclude ★ For tech articles

---

## Items to Confirm (PPTX Input)

### Questions to Ask

| Question              | Options                                                       |
| --------------------- | ------------------------------------------------------------- |
| **Q1: Slide count**   | As-is / 2/3 / 1/2 / 1/4 / Custom                              |
| **Q2: Design method** | Source PPTX (default) / Template / pptxgenjs / create_ja_pptx |

---

## Design Methods (All Sources)

### Common Generation Methods (A-C)

| #     | Method             | Features                                            | When Shown         |
| ----- | ------------------ | --------------------------------------------------- | ------------------ |
| **A** | **Source PPTX**    | Use source PPTX master (colors, fonts, background)  | ⚠️ PPTX input only |
| **B** | **pptxgenjs**      | JavaScript custom generation, code blocks, diagrams | Always             |
| **C** | **create_ja_pptx** | Simple generation from scratch (python-pptx)        | Always             |

### Template Methods (D+)

Templates from `assets/` folder are assigned D, E, F... in order:

| #   | Method               | Description              | When Shown |
| --- | -------------------- | ------------------------ | ---------- |
| D   | (template.pptx)      | General-purpose template | Always     |
| E   | (base_template.pptx) | Minimal template         | Always     |
| F+  | (additional...)      | Any additional templates | If exist   |

---

## Recommended Combinations

| Source Type                 | Recommended            | Reason                    |
| --------------------------- | ---------------------- | ------------------------- |
| **PPTX input**              | **A (Source PPTX)**    | Design inheritance stable |
| **Code-heavy tech article** | **B (pptxgenjs)**      | Code block support        |
| **Diagrams needed**         | **B (pptxgenjs)**      | Shapes, arrows, colors    |
| **Web/blog article**        | **D+ (Template)**      | Compare and choose        |
| **Keep it simple**          | **C (create_ja_pptx)** | Minimal design            |

---

## Proposal Format Example (Web/Blog)

```
## 📋 Generation Plan Confirmation

**Input**: [Article Title]
**Source**: [URL]

---

### 🎯 Slide Count / Detail Level

| # | Count  | Detail  | Images | Description        |
|---|--------|---------|--------|--------------------|
| **1** | 6-8  | Summary | 2 main | Key points only    |
| **2** | 10-14| Standard| 4-5    | Balanced (recommended)|
| **3** | 16-25| Detailed| All    | Step-by-step detail|

---

### 📝 Generation Method Selection

| # | Method | Features | Best For |
|---|--------|----------|----------|
| **B** | **pptxgenjs** | JavaScript, code blocks | Tech content |
| **C** | **create_ja_pptx** | Simple (python-pptx) | Minimal design |
| **D** | **template.pptx** | General template | Most cases |

> 🎯 **Recommended**: Standard (2) + Template (D)

---

**Which would you like?** (count + method)

Examples:
- "2D" → Standard, template
- "2B" → Standard, pptxgenjs (code blocks)
- "3C" → Detailed, minimal design
```

---

## Proposal Format Example (PPTX Input)

```
## 📋 PPTX Localization Plan

**Input**: [Filename]
**Detected**: PPTX ({N} slides)

### 📊 Analysis Result
| Type | Count |
|------|-------|
| Title slides | {N} |
| Content slides | {N} |
| Image slides | {N} |

---

### 🎯 Slide Count / Compression

| # | Output | Compression | Description |
|---|--------|-------------|-------------|
| **1** | {N} slides | As-is | Full version |
| **2** | {N×2/3} | 2/3 | Merge similar |
| **3** | {N×1/2} | 1/2 | Half compression |
| **4** | {N×1/4} | 1/4 | Key points only |

---

### 📝 Design Method Selection

| # | Method | Features | Best For |
|---|--------|----------|----------|
| **A** | **Source PPTX** | Inherit master design | Default for PPTX |
| **B** | **pptxgenjs** | Code block support | Technical content |
| **D** | **template.pptx** | Use different design | New branding |

> 🎯 **Default**: Full translation (1A)

---

**Which would you like?** (count + method, default: 1A)

Examples:
- "1A" → Full translation (source design)
- "1" → Full translation (default: source design)
- "3A" → 1/2 compression (source design)
- "2D" → 2/3 compression, use template
```

---

**Proceeding to BUILD without confirmation is prohibited.**
