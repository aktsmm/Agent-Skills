---
name: browser-bookmark-organizer
description: "Safely audit, classify, deduplicate, and reorganize Chrome or Edge browser bookmarks/favorites while preserving toolbar shortcuts, active profiles, and observable sync state. Use for browser bookmark cleanup, duplicate bookmarks, folder redesign, or login/reference/self-hosted link classification. Not for X saved posts."
argument-hint: "対象ブラウザー（Chrome / Edge）、やりたいこと（棚卸し / 整理 / 重複削除）"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Browser Bookmark Organizer

Chrome / Edge のブックマーク（お気に入り）を、プロファイルと sync 状態を壊さずに棚卸し、分類、重複削除、再設計する Skill。

## When to Use

- "ブックマークを整理して", "お気に入りを分類して", "重複を消して"
- Chrome / Edge bookmark or favorites cleanup
- Folder-taxonomy redesign, depth reduction, or login/reference separation
- Bulk title cleanup or transient URL replacement

Do not use for browser history, passwords, cookies, sessions, or reading-list
cleanup unless the user separately requests those scopes.

## Non-Negotiable Safety Rules

1. Work only in the user's active, normal browser profile.
2. Never edit `Bookmarks`, `AccountBookmarks`, `Preferences`, `Local State`,
   sync databases, or equivalent Edge profile files directly.
3. Never use a copied profile, directory junction, alternate `--user-data-dir`,
   or temporary profile to mutate the real account's bookmarks.
4. Use browser-owned bookmark/favorites APIs or the normal manager UI. Do not
   automate password, cookie, or session stores.
5. Before bulk mutation, always create a browser export. Also capture a
   structured tree when the active browser safely exposes its bookmark API;
   record baseline counts/order and define the available recovery path.
6. Perform a reversible pilot, then short batches. Stop after two unchanged or
   ambiguous persistent-state checks; stop mutating and report before continuing.
7. Delete folders only after proving they are empty. Never recursively remove a
   non-empty folder as cleanup.
8. Treat URL replacement as a new deduplication event; recheck duplicates after
   canonicalizing transient URLs.
9. Apply only the authorized plan; audit approval is not delete approval.
   Keep backups private and scoped to bookmarks, not unrelated profile data.
10. Verify current tool documentation and available manager/API controls;
    references do not prove CDP, DevTools, or native input is available.
    If no supported route can perform the task, stop at audit/plan.

→ Recovery details: [references/safety-and-recovery.md](references/safety-and-recovery.md)

## Workflow

### 1. Identify the Correct Profile

Confirm browser, profile display name, profile directory, signed-in account, and
observable bookmark sync state in the normal UI. Report unavailable checks;
do not infer the profile from a process list alone. Use a task-owned manager tab
when supported, preserving existing tabs and foreground:

- Chrome: `chrome://bookmarks`
- Edge: `edge://favorites`

### 2. Audit Before Designing

Inventory the tree to its lowest accessible level and capture:

- URL/folder counts, exact duplicate groups, empty folders, maximum depth
- direct toolbar/root bookmarks and their relative order
- empty/weak titles and authentication/session/completion URLs
- mixed login/action, reference/memo, owned-service, and archive content

Do not use `date_last_used` as deletion evidence when it is missing or sparse.
Mark incomplete coverage; visible rows alone do not prove a complete tree.
Do not infer baseline counts or paths from the example log template.

### 3. Freeze User Intent

Identify intentional toolbar shortcuts and preserve their surviving relative
order. Confirm or reasonably infer the folder-depth target; default to two
folder levels for a compact taxonomy, not zero or unlimited nesting.

Classify ambiguous service URLs conservatively. A cloud host or GitHub Pages URL
may be the user's own deployed service, not generic documentation.

→ Classification model: [references/classification-model.md](references/classification-model.md)

### 4. Produce a Dry-Run Plan

Generate explicit operations with bookmark ID, current path, destination path,
reason, title change, and URL change. Separate these phases:

1. exact duplicate removal
2. destination-folder creation
3. bookmark moves
4. title cleanup
5. stable URL replacement
6. empty legacy-folder removal

Use [assets/dry-run-plan-template.json](assets/dry-run-plan-template.json) as
the operation-log shape. Omit IDs only when the chosen UI path cannot expose
them, and compensate with exact paths, titles, and URLs.

Avoid a parallel root such as `整理済み` / `Organized`; integrate into one
taxonomy to prevent double management. For a large plan, obtain a rubber-duck
review before mutation, focusing on data loss, reversibility, MECE quality,
toolbar preservation, and browser/profile safety. If independent review is
unavailable or unauthorized, report the unresolved requirement and stop before
the affected large or destructive changes.

### 5. Execute in the Active Profile

Use stable IDs from the live tree and browser-owned APIs where available. Run a
small pilot, verify persisted state, then use short batches. Reacquire UI or API
state between batches rather than trusting stale wrappers or success markers.

Prefer supported API/element actions that preserve the user's mouse and
foreground. Native keyboard/window controls must actually be available. If
activation is necessary, explain the bounded step first; restore focus only
when the user has not meanwhile switched tasks.

→ Browser-specific execution: [references/chrome-edge-execution.md](references/chrome-edge-execution.md)

### 6. Verify the Persisted Result

Re-read the live tree within the verified coverage and compare with the approved plan:

- expected URL count and no unintended duplicates or empty folders; retain
  explicitly approved exceptions
- maximum depth meets the agreed target
- direct toolbar/root order is preserved
- every obsolete folder was empty before removal
- title/URL updates persisted and did not create duplicates
- observable signed-in profile and sync health, with unavailable checks marked
- no password, cookie, session, or unrelated profile data changed

Close only task-owned surfaces, not the user's existing manager or shared last
tab. Report verified before/after counts, coverage limitations, intentionally
retained items, unknown outcomes, and the recovery artifact.

## References

- [Classification model](references/classification-model.md)
- [Chrome and Edge execution](references/chrome-edge-execution.md)
- [Safety and recovery](references/safety-and-recovery.md)
- [Provenance](PROVENANCE.md)
