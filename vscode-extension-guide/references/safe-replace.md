# Safe Replace (update / reinstall of user-owned files)

Use when a feature overwrites a folder or file set the user may have edited: reinstall one item, "update changed items", repair. Delete-then-install is not acceptable for a single-item action, because any failure after the delete loses the user's copy.

## Sequence

1. Resolve the exact target (root + relative path; match by name only when it is unique) and pin the source to one revision. A passive update needs a recorded source; only an explicit user action may rebind an install that has none.
2. Ask before overwriting possible local edits. Declining must cause no download and no write. Stop (never auto-save) when a dirty editor document is inside the target.
3. Download into a hidden transaction folder on the **same filesystem and inside the managed root**, so renames stay atomic, and exclude it from scanners and ignore-file sync. Verify completeness (no placeholder-only, partial or unsafe entries) before touching the old copy.
4. Re-check right before the swap: the content snapshot equals the one taken before the download, no dirty documents, ownership metadata unchanged.
5. Move the old copy aside inside the transaction folder, place the new one, and compare both against their snapshots. Any conflict, cancellation or failure restores the old copy.
6. If restoring fails or the destination changed, keep the backup, report where it is, and stop automatic work for that item. Delete the transaction folder only when no backup is retained.
7. After a verified success, delete the staged copy and the old copy; keep the old copy and show its location only when saved local edits were overwritten. Keeping every old copy forever piles up silent leftovers.
8. Before the first rename, write a per-target recovery record (target, transaction, backup) outside every scanned root. Remove it only after verified success or rollback; while it exists, refuse further updates of that target. A host exit mid-swap then leaves evidence instead of a skill that is silently missing.

## Comparison details

- Hash file contents, but above the size/count caps degrade to size + mtime. A cap that refuses to compare turns into "this item can never update" and also breaks retry.
- Do not hash inode, device or link count: they differ across filesystems (exFAT, network drives, sync clients) and create false conflicts without adding safety.
- Exclude user-editable metadata (custom descriptions, enable/disable toggles) from the content baseline. Merge it into the staged metadata right before the swap, then read the moved-aside copy's metadata after the rename; a mismatch means the change was lost, so restore.
- While reading a file for the snapshot, confirm size and mtime did not change during the read.
- Git tree modes: treat `100644` and `100755` as ordinary files when the installer copies bytes only; refuse symlinks (`120000`) and submodules (`160000`). Refusing `100755` makes every script-bearing folder permanently non-updatable.

## Scope of the guarantee

Exclusion against another window, app or extension cannot be proven. Do not require a service, ACL or shared lock to ship a user-initiated update. Detect what is detectable (dirty documents, changed content or metadata, failed rename), abort, restore, retain the backup, and state the residual race in the docs. Never widen the claim silently: a feature that runs unattended or touches shared roots stays on hold or needs explicit confirmation.

When a "shared or network location" check lists Windows shares (`Win32_Share`), a stock `Users` share of the profile folder can exist and would block every workspace under it. Exempt only the exact stock share (name and path), and test that a custom share with the same name or another path still blocks.

## Periodic check

- Gate the "last successful check" timestamp on a complete scan: a scanner that swallows read errors returns a partial list that looks like success, so give it a completeness result. An incomplete scan, a failed request or a rate limit must not advance the clock.
- The check never writes. Replacement happens only after the user presses an action; closing the notification changes nothing.

## Batch and retry

- A batch "repair / reinstall all" may keep trash-first removal as a separate, explicit semantics. Document it, do not describe it as staged, and test that removal uses the trash so the old copy stays recoverable.
- A failed-only retry keeps the failed entries keyed by root, relative path, source and install identity, rechecks them when clicked, skips anything changed or awaiting manual recovery, and confirms with the target list before writing.

## Tests

Inject a failure at each boundary (backup rename, placement rename, cancellation after the backup, failed rollback) and assert the old bytes and metadata are identical afterwards. Also cover a save during the backup rename, an oversized file, a dirty document, a declined confirmation, same-name items in different roots, and a legacy install without a recorded source.

Stubbed tests miss environment assumptions. Before calling an updater done, run it once end to end against a real public repository (an older commit installed into a temporary workspace, detected, updated, compared byte for byte with upstream, re-checked as unchanged) and confirm no staging folder remains. Such a run found the stock-share and executable-mode defects above.
