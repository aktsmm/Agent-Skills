# Slide Structure & Content Rules

Merged from `pptx-slide-structure.instructions.md` + `pptx-content-rules.instructions.md`.
`applyTo` (as repo instruction): `**/*.pptx,**/unpacked/**`. Customer name is abstracted to **"お客様
システム"**; fill the real name only via the customer profile / config.

## Slide composition

| #     | Content                     | Section           |
| ----- | --------------------------- | ----------------- |
| P1    | 表紙                        | 表紙              |
| P2    | Weekly News Topics サマリ   | サマリ            |
| P3…Pn | Weekly Topics スライド      | Weekly New Topics |
| Pn+1  | 今週の UPDATE Points        | UPDATE Points     |
| Pn+2  | Appendix ヘッダー（hidden） | Appendix          |
| Pn+3… | Appendix スライド（hidden） | Appendix          |
| last  | Ending                      | Ending            |

**Section order (SSOT)**: 表紙(P1) → サマリ(P2) → Weekly New Topics(P3…) → UPDATE Points(after
Weekly) → Appendix(hidden) → Ending. **UPDATE Points goes AFTER Weekly Topics, never at P3.** Multi-page
UPDATE Points continuation slides stay in the UPDATE Points section right after Weekly — never treat a
continuation as the Appendix start.

## Reference footer

Visible update slides must distinguish reference types. Use short, linked labels rather than raw URL walls:

```text
詳細：Microsoft Learn | 発表：Azure Updates
```

- `Microsoft Learn` links to `learnUrl` and means implementation details, prerequisites, limitations, or examples.
- `Azure Updates` links to `sourceUrl` and means the official announcement/release communication.
- Speaker notes carry the full URLs with the same labels.

## Weekly body composition

Use the service name, not the customer category, in `対象：`. The full-width upper body is one ordinary left-aligned text frame: `対象：`, `更新内容：`, `価値：`, `影響：`, and optional `課金：`. Do not turn those lines into separate cards. `更新内容` explains the actual change in one or two lines; `価値` explains the benefit; `影響` shows constraints or action without internal `【…】` tokens.

- Render Before / After in the first two lower panels, not a combined `変更：` sentence.
- Render the mode content below Before / After as one full-width, left-aligned row: `対応の要点` / `技術の要点` / `基礎知識`. Heading is 16pt; body is 13-15pt.
- Do not render `keypoint` as a separate band in any mode; use it as source text for `updateSummary` or `対応の要点`.
- Keep graphical containers for comparison and the mode row, but keep ordinary descriptive text unboxed.
- Keep body fill ratio (`BoundHeight / shape.Height`) within 0.55-0.92.
- Reserve the title space before the status badge. If a title is too long, wrap it inside the title region (up to two lines) and validate a rendered saved slide; never clip into the badge or hide the text by over-shrinking it.

## Ending slide

Ending is a simple formal closure, not a next-action or summary slide by default. Use the visible ending variant that matches the visible cover variant.

Required ending text:

```text
以上
Azure アップデート情報
```

The template may keep three ending variants aligned to the three cover variants: Indigo Amber, Azure Blue, and Teal Fresh. Only the matching variant is visible in the generated deck; the others are hidden. Do not put next actions, update counts, reference URLs, region notes, contact prompts, `Thank you`, or placeholder scaffolding on the default Ending.

## Weekly order (SSOT)

Within Weekly New Topics, order slides: 1) **【廃止】** 2) **【GA】** 3) **【Preview】** 4) **【アナウンス】/【更新】**. Priority reads as: needs-action → now-usable → future → notice/other.

### Label decision (SSOT — `PptxCommon.psm1 Get-SlideLabel` reads here)

Match the source status wording from title / body head / reference, first hit wins:

| Priority | Label              | Regex                                                                  |
| -------- | ------------------ | ---------------------------------------------------------------------- |
| 1        | **【廃止】**       | `サービス終了\|提供終了\|廃止\|Retirement\|Deprecated\|End of Support` |
| 2        | **【GA】**         | `一般公開\|一般提供\|利用可能になりました\|Generally Available`        |
| 3        | **【Preview】**    | `プレビュー\|Preview\|Public Preview\|Private Preview`                 |
| 4        | **【アナウンス】** | `アナウンス\|Announcement`                                             |
| 5        | **【更新】**       | fallback (no match above)                                              |

## Label placement

| Place               | Label? | Why                                                           |
| ------------------- | ------ | ------------------------------------------------------------- |
| Slide title         | ❌ no  | source slide already has a top-right badge (avoid redundancy) |
| P2 TOC              | ✅ yes | grasp priority without opening the slide                      |
| UPDATE Points table | ✅ yes | same                                                          |
| Speaker note (P2)   | ✅ yes | same                                                          |

🔴 **GA/Preview state must match across body + UPDATE Points + notes** (one stale path = contradiction;
watch Azure Updates `status` feed lag — see [validation-rules.md](validation-rules.md)).

## Hidden-slide rules

- Hide ONLY Appendix slides (header + contents). Never hide Weekly New Topics slides.
- Source PPTX hidden slides (`SlideShowTransition.Hidden -eq -1`) → **excluded** from merge (author
  intentionally dropped them; `Prepare-CustomerPptx.ps1` skips them).
- Template's own hidden slides (Appendix structure, reference slides) → **kept**.

## P2 TOC rules

- Weekly New Topics only (exclude Appendix/hidden). Always mark `[GA]`/`[Preview]`. ~80-100 chars/item,
  all items listed (no omission).
- Truncation: max 40 chars, full-width `…` (half-width `...` forbidden), label part not truncated.

## P2 Summary

List every Weekly Topic as a numbered bullet with count + label, e.g. `■ 今週の Weekly New Topics（7
件）` then `1. 【廃止】…`. Required: item count, label on every item, all items (omission forbidden).

## UPDATE Points table (5 columns)

| Col                | Content          | Rule                                                                                                    |
| ------------------ | ---------------- | ------------------------------------------------------------------------------------------------------- |
| #                  | number           | 1.. sequential, 2-digit safe width (no wrap)                                                            |
| キーワード         | service/category | ~20 chars; **display the Japanese category name**, never internal values (`IaaS`/`Network`/`AIReview`…) |
| アップデート内容   | concrete content | **15-25 chars**, `【label】` prefixed, "詳細は P4 参照" forbidden                                       |
| キーポイント       | user value       | **30-40 chars**, benefit + impact on お客様システム, with ★ rules below                                 |
| リージョン対応状況 | region           | per [region-stamp.md](region-stamp.md)                                                                  |

### Key-point column

State **impact presence** so the customer instantly knows relevance: 影響なし / 活用推奨 / 要対応 /
参考情報. Examples: `NAT Gateway利用済みのため影響なし`, `ゾーン分散構成に活用可能`,
`2026/3/31までに移行必要`, `AI Agent活用の参考事例`.

🔴 **"利用中" determination**: only assert "利用中" if the service is listed in the customer profile's
in-use section; otherwise use `○○利用中なら要注目`. Never assert in-use from a keyword match alone. When
writing a usage figure ("約○○本利用中"), back it with a real `az graph query` (Resource Graph) — never a
guessed number in customer material; otherwise stay conditional ("～を利用している場合").

When listing supported regions in body, don't enumerate all — give representatives in **nearest-to-Japan
order** (e.g. East Asia / Southeast Asia / Korea Central) and, if Japan is out, note "日本リージョンは
対象外" to double-match the stamp.

### ★ mark

Prefix ★ to topics the customer especially cares about. Rules:

| Type     | Style                                         | Example                                                |
| -------- | --------------------------------------------- | ------------------------------------------------------ |
| 廃止     | action + deadline (no "未使用のため影響なし") | `★ 利用していればAMAへの移行が必要（期限2026/7/31）`   |
| GA       | ★ + benefit (don't write "利用中")            | `★ DRS 2.2自動更新でセキュリティルールが最新化`        |
| Preview  | ★ + evaluation point (no "利用中なら")        | `★ Vaulted Backupで長期保持・ランサムウェア対策に有効` |
| 更新     | ★ + scenario/benefit                          | `★ XFFベースのレート制限でBot対策に有効`               |
| 参考情報 | no ★, brief                                   | `AI Agent活用の参考事例`                               |

🔴 **★ cap = 30-40% of Weekly count** (5-8件→2-3 ★; 9-12件→3-5; 13-17件→4-7). All-★ forbidden (loses
priority signal). Each key point must contain a benefit OR an action (廃止 = required action + deadline).

### Title normalization (Japanese display title, raw join key)

Keep `classification.title` as the byte-exact Azure Updates title and manifest join key. Use
`classification.titleJa` as the customer-visible display title on P2, Weekly slides, and UPDATE Points.
The display title should be a concise natural Japanese summary, normally within 36 full-width characters
and two rendered lines; validate the saved deck when an official name makes it longer.

Do not place `Generally Available`, `Public Preview`, `Retirement`, `GA`, `Preview`, `廃止`, or
`一般提供` in `titleJa`; the existing label badge communicates status. Preserve official product, SKU, and
protocol names, and read the Azure Updates body plus Microsoft Learn before a plain-language rewrite so the
feature effect does not change. The raw title, status, and announcement URL remain available through
`title`, `label`, and `sourceUrl` for notes and audit.

If `titleJa` is changed after Prepare, regenerate the classification-derived notes and reviewed-region
artifacts before Build. Do not replace or freely edit `title`, because scripts use it as the join key.
Titles must be unique and must not be prefix-related after 12 normalized characters so prefix matching cannot attach
the wrong slide, note, or region entry.

### Table splitting

> 10 items → split across pages (no omission). ≤10/page; 11+ → balanced ≤10/page (8→8, 10→10, 11→6+5,
> 17→9+8). Duplicate the UPDATE Points slide and insert before Appendix. Don't shrink to absorb overflow —
> overflow goes to the next page. Add table rows dynamically if the template has too few
> (`$table.Rows.Add()` up to `weekly.Count + 1`); never `break` — show every item.

### Mandatory rules

1. アップデート内容 always has a `【label】` (GA/Preview/廃止/アナウンス/更新).
2. Key point always contains benefit or action (new feature = benefit; 廃止 = action + deadline;
   更新 = scenario/benefit).
3. Key point ★ + impact wording per the table above ("未使用のため影響なし" forbidden for 廃止).

## ⚠️ Direct body editing forbidden

No direct append/overwrite to slide body text (breaks formatting). Region info → use the template's
RegionStamp shape. Extra info → add a NEW textbox, never `+= "\nリージョン: …"`.

## Category (classification.json `category`)

🔴 The **AI agent** decides `category` at classification time; scripts only read the field (no pattern
match). Display the Japanese category name in UPDATE Points (normalize per
[customer-profile.md](customer-profile.md)). Use `その他` only when the title can't be classified.

## Speaker notes

**Do NOT note** what's visible on-slide: 概要 (from title/content), label (top-right badge), region
(bottom-right stamp).

**DO note** what the slide alone can't show:

- **basics**: 基礎知識・キーワード解説 (bulleted "what even is this?")
- **technical**: technical補足・注意点 (base technology)
- `customerConcerns` (Q/A) and full Learn / Azure Updates / region evidence URLs

Do not repeat visible value, impact, Before/After, or keypoint lines verbatim in notes.

### notes.json (Notes Generator output → `{dateFolder}/manifest/notes.json`)

```json
{
  "weekly": [
    {
      "title": "既定の送信アクセスの廃止日を 2026 年 3 月 31 日へ延長",
      "basics": [
        "既定の送信アクセス: VM が明示的な送信設定なしで…",
        "NAT Gateway: …",
        "暗黙的 vs 明示的: …"
      ],
      "userValue": "移行準備の時間を6ヶ月確保。…",
      "technical": "VM/VMSS の既定送信は NAT Gateway、Azure Firewall、…",
      "beforeAfter": "Before: 期限 2025/9/30 → After: 2026/3/31 まで延長",
      "systemImpact": "【影響なし】お客様システムは … 構成済み。追加対応不要。",
      "customerConcerns": ["Q: … → A: …"]
    }
  ],
  "appendix": [
    {
      "title": "…",
      "basics": ["…"],
      "userValue": "…",
      "technical": "…",
      "beforeAfter": "…",
      "systemImpact": "…",
      "excludeReason": "Weekly 不要（運用影響少）"
    }
  ]
}
```

`Enrich-CustomerPptx.ps1` writes facts only: 表紙 = count; サマリ = Weekly list (number+label+title);
Weekly = basics + technical + Q/A + full reference URLs; Appendix = placement reason + its detailed notes; UPDATE Points = nothing (table is
self-evident).

## After output

Always open the deck (`Start-Process <out>.pptx`) and check: section structure, Appendix hidden, P2 TOC,
UPDATE Points table filled, speaker notes present.
