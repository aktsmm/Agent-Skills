# One-Update-One-Slide Pattern

Content pattern proven on a JSON-driven, one-update-per-slide digest (GA / Preview / Retirement / Announcement). It is renderer-agnostic: use it to decide what a single update slide carries, whether it is drawn by COM, `python-pptx`, or HTML-to-PDF.

## Slide anatomy (1 update = 1 slide)

1. **Title row**: Japanese headline, one-line subtitle stating the benefit or change, English original title with the published date beside it, kind badge (GA / Preview / 廃止 / アナウンス) at top right. Do not repeat the status or date elsewhere.
2. **Audience strip** (three cells): 誰に関係するか (the target group in **bold**), 嬉しい点 (for a retirement or breaking change use 変わること／嬉しくない変更), 対応の要否 (要対応 / 任意 / 対応不要 plus one short reason and the deadline).
3. **Before → After** card when a first-party source states the previous behaviour; otherwise a single 何が嬉しいのか card. Never invent the "before".
4. **Kind-specific panels**: GA = 仕組み / 設定の流れ + 前提・制限 / 似た機能との違い / 使いどころ・注意; Preview = プレビューの範囲 / 制約・注意 + 評価ポイント; Retirement = timeline (announce date → end date) / 移行先 / 影響・アクション; Announcement = 適用範囲 / 知っておくべき点 + 影響・アクション. Recommendations are labelled 提案 and are never presented as facts.
5. **Glossary** (4–6 terms): every product name in the title, the key feature, the unfamiliar jargon, and the GA / Preview label. Definitions come only from first-party docs, one short sentence, no "(beginner)" suffix.
6. **Footer**: 発表 link and 詳細 links (max 3 official pages, **prefer the `ja-jp` page when it exists**, never fill with unrelated product landing pages), category and ID in quiet text, and the region stamp at bottom right.

## Region stamp

Draw a stamp (グローバル / 東日本・西日本対応 / 東日本のみ / 西日本のみ / 日本リージョン非対応) only with first-party evidence (service-level availability counts). When nothing confirms it, draw no stamp at all.

## Wording gate

Slides never show internal-state wording: 未確認 / 記載なし / 要確認 / 推定 / 未発表 / 判定保留 / 「AI 生成」/ 「データ時点」. If a fact can be verified, state it; if not, omit the element. Enforce with a forbidden-phrase check over all rendered text, and keep a claim-level record (origin, assertion fact/inference/recommendation, verification, evidence URLs) in the data so omissions are decided mechanically.

## Dates

Show the published date as a calendar date. Keep availability at the granularity the source gives (month stays month; never invent a day). Generated-at timestamps belong on cover/export metadata only, not on individual slides.
