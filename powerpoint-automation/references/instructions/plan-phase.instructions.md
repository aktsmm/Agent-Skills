# PLAN Phase Confirmation Process

**Before starting PPTX generation, always get user confirmation. Do not proceed automatically.**

---

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
