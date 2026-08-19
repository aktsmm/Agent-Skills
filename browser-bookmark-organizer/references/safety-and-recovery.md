# Safety and Recovery

## Backup Set

Before mutation, always create:

1. Browser-native HTML export from the active profile.
2. A structured JSON tree when the active browser context safely exposes the
   bookmark API, including IDs, titles, URLs, parent IDs, indexes, and children.

If API access is unavailable, do not install a temporary extension or edit
profile files solely to obtain IDs. Use the HTML export plus an explicit
path/title/URL dry-run plan, and state that operation-level reversal is limited.

Record baseline:

- browser/profile/account identity
- URL and folder counts
- duplicate groups and empty folders
- root/toolbar bookmark ID order
- maximum folder depth
- sync health

Store backups outside the browser profile directory. Do not store credentials,
cookies, tokens, password databases, or full session data with the bookmark
backup.

## Recovery Hierarchy

1. Reverse the latest known operations through the bookmark API when available.
2. Re-import the HTML export into the same active profile if operation-level
   reversal is insufficient.
3. Stop and involve the user before any whole-profile recovery.

Do not launch a copied profile to "test" recovery: profile copies can be treated
as a different profile and can unlink or alter account/sync state.

## Incident Stop Conditions

Stop mutation immediately when:

- profile name/account changes or sync becomes unhealthy
- URL count changes beyond the approved deletions
- root/toolbar relative order changes unexpectedly
- a target folder is missing or resolves to multiple candidates
- a supposedly empty folder contains children
- unrelated passwords, sessions, cookies, or browser settings appear affected

Preserve the latest tree snapshot and operation log before attempting recovery.

## Deletion Gate

Delete only exact duplicates approved by the plan or empty legacy folders
verified from a fresh tree read. Uncertain, old, inaccessible, 403, timeout, or
certificate-error URLs are not deletion candidates without stronger evidence.
Use HTTP 404/410 plus browser confirmation when link death is part of scope.
