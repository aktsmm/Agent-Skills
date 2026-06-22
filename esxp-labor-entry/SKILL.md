---
name: esxp-labor-entry
description: "Enter and reconcile ESXP labor through core/draft API and Edge CDP. Use when entering weekly labor, ROSS/RMOT dispatch hours, non-project/overhead, planning paid utilization, checking contract windows, or saving draft labor for later submit. Triggers on 'ESXP', 'レイバー入力', '工数入力', 'ROSS工数', 'dispatch工数', 'non-project', '有償率', 'contract window', 'draft保存', 'Out of office 祝日'."
argument-hint: "週、assignment ID、入れたい hours、non-project category、または今やりたい操作"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# ESXP Labor Entry

ESXP の dispatch / non-project labor を **Edge CDP + core/draft API** で扱う portable skill。
このフォルダだけで、認証前提、API 形、契約期間解釈、主要スクリプト、落とし穴まで持つ。
もし別の workspace に stricter な運用 instruction があっても、この skill を **portable baseline** として扱う。

## When to Use

- 「ESXPに今週の工数を入れたい」「レイバー入力して」「dispatch 工数を計上したい」
- 「non-project / overhead / Unified Presales を入れたい」「Out of office 祝日を先行投入したい」
- 「契約期間で来週に分けてよいか判断したい」「draft 保存して後で Submit したい」
- 「API で安全に入れたい」「CDP で正しい Edge profile か確認したい」

## What This Bundle Contains

- `scripts/esxp_client.py`: CDP WebSocket client
- `scripts/labor_api_tools.py`: fetch-week / add-dispatch / add-nonproject / submit-drafts / delete
- `scripts/get_weekview_summary.py`: Week View DOM summary
- `scripts/verify_esxp_profile.py`: wrong profile / Home / sign-in の検出
- `references/api-reference.md`: endpoint / payload / auth capture
- `references/cdp-setup.md`: Edge launch / env vars / health check
- `references/contract-window-rules.md`: Request End を使う配分ルール
- `references/category-id-map.md`: category / reason の確認済み値
- `references/gotchas.md`: save_ui 消失、NP 404、dirty page など

## Canonical Flow

1. **Start Edge for CDP**: `references/cdp-setup.md` の手順で Edge を起動し、ESXP Week View に手動ログインする。
2. **Verify profile**: `python scripts/verify_esxp_profile.py --strict-account --expected-account you@company.com`
3. **Read before state**: `python scripts/labor_api_tools.py fetch-week --start-date YYYY-MM-DD --end-date YYYY-MM-DD --format table`
4. **Plan with contract window**: `references/contract-window-rules.md` を見て、delivery 日ではなく **Request End** で今週投入か週またぎかを決める。
5. **Write safely**: 既定は `--draft --apply`。最終 Submit を人がやる前提で draft に残す。
6. **Verify after state**: `fetch-week` の after summary と `python scripts/get_weekview_summary.py --format markdown` を両方確認する。
7. **Submit only when clean**: final submit は ESXP UI か draft submit flow で行う。dirty page や partial success を疑う時は `references/gotchas.md` を確認する。

## Fast Commands

Read current week:

```powershell
python scripts/labor_api_tools.py fetch-week --start-date 2026-06-15 --end-date 2026-06-21 --format table
python scripts/get_weekview_summary.py --format markdown
```

Save dispatch labor as draft:

```powershell
python scripts/labor_api_tools.py add-dispatch `
	--date 2026-06-18 --hours 4 `
	--assignment-id 5206766 `
	--assignment-name RMOT2026021305200000 `
	--customer-name "Customer" `
	--product-name "Technical Update Briefing - Azure" `
	--reason-code-id 333177 `
	--draft --apply
```

Add non-project labor:

```powershell
python scripts/labor_api_tools.py add-nonproject `
	--date 2026-06-19 --hours 8 `
	--category-id 982947 `
	--category-name "Out of office" `
	--notes "Japanese Holiday" `
	--omit-action-details --apply
```

## Key Rules

- **Use API first.** `save_dispatch_labor_ui.py`-style UI save can look successful and still disappear after reload.
- **Draft is the safe default.** Draft POST target is `lmt-draftapi`, and the body must be `[payload]`.
- **Plan by Request End.** RMOT uses request-level Start/End as the real window. ROSS/EDE can also show a broader agreement period; do not use the umbrella agreement alone.
- **Do not brute-force IDs.** `reasonId`, `laborCategoryId`, assignment IDs must come from known-good records or confirmed UI values.
- **Use `Delivery`, not `(ISD only) Delivery`.**
- **Non-project verification is special.** NP can be real even when core/draft fetch looks empty; verify NP through Week View summary.
- **Week total is not enough.** Check week total, day total, and draft/core state together.
- **Do not reload dirty pages.** beforeunload and unsaved state can make CDP look broken when the page state is the real problem.
- **API success beats stale DOM, but do not blindly reload.** If API returns a created `laborId` while Week View still shows old totals, record API success + UI stale, do not re-run the write, and verify later through read API or a clean reload.
- **Scope tab clicks.** In Select a Dispatch style modals, tab names such as Current / Upcoming / Reports Pending must be clicked inside the tab container, not by global text search.

## Portable Defaults You Can Reuse

- Host: `https://professionalservices.microsoft.com`
- Core path: `/lmt-coreapi/api/v1/labor`
- Draft path: `/lmt-draftapi/api/v1/draftLabor`
- Auth source: CDP `Network.requestWillBeSent` from a live Week View tab
- Time zone in confirmed JST environment: `laborTimeZoneId = 87`
- Common NP category IDs in one confirmed environment:
  - `Out of office = 982947`
  - `Unified Presales = 368713`
  - `General Admin , Meetings & Events = 1013309`

## What This Skill Does Not Assume

- a specific ledger path
- a specific customer list
- a specific report directory
- a specific workspace instruction file

If you want local ledger reconciliation or audit output, add that as a caller-specific wrapper around these scripts.

## Done Criteria

- [ ] CDP session points to the correct authenticated ESXP profile
- [ ] before state and after state are both captured
- [ ] Request End / contract window was checked before splitting work across weeks
- [ ] mutation used API (`--apply`), not an unverified UI save path
- [ ] week total, day total, and core/draft state all look correct
- [ ] final submit responsibility is explicit: draft left for human submit, or submit completed and verified
