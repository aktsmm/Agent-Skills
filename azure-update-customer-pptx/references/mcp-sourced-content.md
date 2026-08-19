# MCP-sourced Content Contract

MCP fetch and research are agent-mediated. PowerShell scripts consume JSON and do not call MCP directly.

## Required Manifests

| File                                 | Producer                     | Consumer                   |
| ------------------------------------ | ---------------------------- | -------------------------- |
| `manifest/fetched-updates.json`      | Azure Updates MCP agent step | `Prepare-CustomerPptx.ps1` |
| `manifest/classification.json`       | Prepare / AI classification  | Build / Enrich             |
| `manifest/region_info_reviewed.json` | Review agent step            | Enrich / Verify            |
| `manifest/notes.json`                | Notes agent step             | Enrich / Verify            |
| `manifest/verify_status.json`        | Pipeline script              | Final report               |

If `fetched-updates.json` is missing, do not start raw PowerShell build. Fetch through the MCP path first.

`verify_status.json` schema v2 owns one NFC-normalized workspace-relative output key per deck under
`results`. Writers must preserve other entries. Each result records `runId`, state, requested/actual engine,
contract versions, output hash, verifier exit code, and error state; readers must match both path and hash.

## Per-Item Reference Rules

### Title fields

- `title`: Azure Updates announcement title retained unchanged as the immutable manifest join key for
  classification, notes, and reviewed-region data; use it for label, category, exclusion, and fallback
  keypoint derivation together with `products` / `productCategories`.
- `titleJa`: customer-visible Japanese display title. For each new customer date folder, write a concise
  Japanese title in `fetched-updates.json` before running `Prepare-CustomerPptx.ps1`; the starter config
  sets `content.requireTitleJa=true`, so Prepare fails if it is missing. The script carries it into
  `classification.json` and the build prefers it on visible slides.
- Preserve official product, SKU, and protocol names in `titleJa`, but do not copy the raw English
  announcement title. Keep GA/Preview/Retirement wording in `label`, not in `titleJa`.
- `titleJa` values must be unique and must not be prefix-related after 12 normalized characters. `notes.json` must use raw `title` as its join key. If `titleJa` changes after Prepare, rerun Prepare,
  region review, notes generation, and the saved-deck verifier together. Do not edit only one manifest
  because `title` remains the raw join key.

Each `fetched-updates.json` item should carry both reference layers when possible:

- `sourceUrl`: Azure Updates / Release Communications announcement URL.
- `learnUrl`: closest Microsoft Learn or official Docs page for the underlying service feature, found through Microsoft Learn Docs MCP. Leave `null` only when no relevant first-party documentation exists after a targeted search.
- `relatedLearnReferences`: optional array of at most two additional Learn pages. Add one only when it has a distinct role (implementation, feature reference, region/availability); reject duplicate URLs and generic overview duplication.
- Visible slides must label these roles explicitly: `参考：Microsoft Learn（詳細）` for `learnUrl`, and `参考：Azure Updates（発表）` for `sourceUrl`. Never put `スピーカーノート参照` or a similar notes pointer on a visible slide.
- Put the visible label in one dedicated reference shape (for example, `OfficialReference`) and set its shape-level `ActionSettings.Item(1).Hyperlink.Address`. Do not rely only on a text-range hyperlink because PowerPoint COM saves can drop it.
- Saved-deck QA must inspect every visible Weekly reference shape for a nonempty hyperlink URL and compare its page URL (ignoring an optional `#fragment`) with the manifest URL.
- Speaker notes should carry the full source trail: `Microsoft Learn 詳細: <url>` and `Azure Updates 発表: <url>`.
- If `learnUrl` is `null`, add a review note such as `learnUrl_note` explaining whether no first-party page was found or the page is still unverified.

### Historical Source URL Recovery

When imported source slides predate `sourceUrl`, recover the Azure Updates record by normalized title, then confirm product/service and announcement window. Accept only one unique candidate. Record `azureUpdateId`, `sourceUrl`, `targetService`, `matchMethod`, and `confidence` in `manifest/url-recovery.json`; leave ambiguous matches unresolved for review instead of guessing. Merge recovered metadata without replacing an already verified `learnUrl`.

## Visible Content Boundary

Visible slide body fields must be reusable across decks. The customer-facing contract is `targetService`, `updateSummary`, `useCase`, `impactStatement` (rendered under the `impactLabel` derived from `impactType`), `action`, `condition` (rendered under `conditionLabel`), `beforeAfter`, and the mode-specific lower-row content. Keep `impactType` as internal classification only; never render `【…】` inside `impactStatement`. `updateSummary` must explain what was added, changed, or retired instead of repeating the title. Region wording belongs to the RegionStamp only and must not appear in any body line.

### Per-Item Layout Mode

Write `layoutMode` to every classified Weekly item; presentation logic must use this field rather than infer a layout from whether a topic is AI.

| Mode        | Use when                                                                           | Full-width lower row                             |
| ----------- | ---------------------------------------------------------------------------------- | ------------------------------------------------ |
| `action`    | Retirement, deadline, or migration action                                          | `対応の要点` from the action text                |
| `technical` | AI, security, operations, storage, or other technical concepts affect the decision | `技術の要点` from the first two `basics` entries |
| `change`    | General update without a specialized technical/action need                         | `基礎知識` from the first two `basics` entries   |

`layoutMode` must be reviewable manifest data written during classification, not an implicit renderer heuristic. A renderer may deterministically default retirement items to `action`, but it must preserve an explicit `technical` or `change` value and never use `isAI` alone as the presentation decision. Use a text-first upper block, graphical `Before / After`, and a full-width left-aligned mode row. Do not render a duplicate keypoint band.

Use the Azure Updates `created` value as the common visible publication date (`掲載: YYYY/MM/DD`). Keep GA/Preview availability and retirement timing as separate timeline facts in notes and action text.

Do not put customer name, system name, tenant domain, subscription IDs, or internal environment labels in visible body fields. Put customer-specific impact or applicability in `notes.json` speaker notes or a review-only artifact.

Examples:

- Use: `GCS から Azure Blob Storage への移行予定がなければ直接影響は限定的です。`
- Avoid: `現行の {SYSTEM} で GCS 利用がなければ直接影響は限定的です。`
