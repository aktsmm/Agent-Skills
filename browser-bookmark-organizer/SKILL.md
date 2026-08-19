---
name: browser-bookmark-organizer
description: "Safely audit, classify, deduplicate, and reorganize bookmarks or favorites in Google Chrome and Microsoft Edge while preserving intentional toolbar shortcuts, signed-in profiles, and sync state. Use when asked to organize browser bookmarks/favorites, clean duplicate bookmarks, redesign bookmark folders, classify login/reference/self-hosted links, or fix an overgrown bookmark tree."
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

→ Recovery details: [references/safety-and-recovery.md](references/safety-and-recovery.md)

## Workflow

### 1. Identify the Correct Profile

Confirm browser, profile display name, profile directory, signed-in account, and
bookmark sync state in the normal UI. Do not infer the profile from a process
list alone. Capture the currently open manager page:

- Chrome: `chrome://bookmarks`
- Edge: `edge://favorites`

### 2. Audit Before Designing

Read the complete tree to its lowest level and capture:

- URL/folder counts, exact duplicate groups, empty folders, maximum depth
- direct toolbar/root bookmarks and their relative order
- empty/weak titles and authentication/session/completion URLs
- mixed login/action, reference/memo, owned-service, and archive content

Do not use `date_last_used` as deletion evidence when it is missing or sparse.

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
toolbar preservation, and browser/profile safety.

### 5. Execute in the Active Profile

Use stable IDs from the live tree and browser-owned APIs where available. Run a
small pilot, verify persisted state, then use short batches. Reacquire UI or API
state between batches rather than trusting stale wrappers or success markers.

Prefer automation that does not physically move the user's mouse. If GUI input
would interfere with other work, use focus/keyboard, CDP, or API operations and
restore the prior foreground window.

→ Browser-specific execution: [references/chrome-edge-execution.md](references/chrome-edge-execution.md)

### 6. Verify the Persisted Result

Re-read the live tree and prove:

- expected URL count, zero unintended duplicates, zero empty folders
- maximum depth meets the agreed target
- direct toolbar/root order is preserved
- every obsolete folder was empty before removal
- title/URL updates persisted and did not create duplicates
- the intended profile remains signed in and bookmark sync is healthy
- no password, cookie, session, or unrelated profile data changed

Close DevTools/automation surfaces and return the user to the normal bookmark
manager. Report exact before/after counts and any intentionally retained
ambiguities.

## References

- [Classification model](references/classification-model.md)
- [Chrome and Edge execution](references/chrome-edge-execution.md)
- [Safety and recovery](references/safety-and-recovery.md)
