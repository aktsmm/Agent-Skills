# Gotchas

## 1. `save_dispatch_labor_ui.py` can look saved and still vanish

The UI path can show `status: saved` and still fail to persist. A page reload can wipe the entry.

Portable rule:

- trust core/draft API writes first
- treat UI save as fallback only
- verify after reload or via API before moving on

## 2. Draft is the safe default

Use `--draft --apply` when you want the human to do the final submit in ESXP.

Important details:

- draft POST target is `lmt-draftapi`
- body must be `[payload]`
- final submit can be manual or done with a dedicated draft-submit flow

## 3. Non-project verification is different

A non-project POST can succeed while core/draft fetch still shows nothing useful.

Portable rule:

- verify NP through Week View summary
- use core/draft listing mainly for dispatch and draft state, not as the only NP truth

## 4. Do not brute-force IDs

Never guess or brute-force:

- `reasonId`
- `laborCategoryId`
- assignment IDs

Use known-good values or discover them from a live authenticated record.

## 5. Late Reason is not always required

Operational rule extracted from the source environment:

- current day: no late reason
- earlier day in the same week: often no late reason
- previous week or older: late reason required

Validate this in your own tenant before bulk mutation.

## 6. Day totals matter, not only week totals

A week hitting 40h is not enough if one day has 12h and another has 4h.

Portable completion rule:

- verify week total
- verify per-day total
- verify core/draft state

## 7. Do not fall back to non-project just because UI is annoying

If there is real customer delivery work, exhaust the dispatch path first. UI delay, tab confusion, or one failing command is not enough reason to recategorize the work.

## 8. `Agree & Submit All` is dangerous because it is fast

There may be no confirmation dialog, and the result can be partially successful.

After submit:

- check service messages when available
- refetch state
- confirm that draft is empty or in an expected empty-state response

## 9. Dirty pages and reloads do not mix

If ESXP is showing unsaved changes or beforeunload prompts:

- do not reload from automation
- do not assume CDP is broken
- clear the page state first, then continue

## 10. `add-*` validation: omit-action-details and dedupe on draft

When posting via the API without a discovered `reasonId`/action-detail set:

- pass `--omit-action-details` on both `add-nonproject` and `add-dispatch`, otherwise the run stops on missing-reason validation before any POST. Without `--apply` the run is a dry-run (no write); add `--apply` only when the dry-run payload looks right.
- in draft mode the live (core) dedupe fetch can return 404 and abort the dispatch to prevent a blind double-post. If you have already verified the target day's state separately (draft listing / Week View), pass `--skip-dedupe` to proceed. Re-verify with `fetch-week` afterward, since core 404 means the safety pre-check could not run.
