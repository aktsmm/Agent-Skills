# Chrome and Edge Execution

## Manager and API Surface

| Browser | Manager | Bookmark API namespace |
| --- | --- | --- |
| Google Chrome | `chrome://bookmarks` | `chrome.bookmarks` where exposed |
| Microsoft Edge | `edge://favorites` | Chromium-compatible `chrome.bookmarks` where exposed |

Prefer the browser's normal manager and public/bookmark-owned API surface. If an
internal page does not expose the API in the current context, use the normal
manager UI. Do not install a temporary extension or fall back to direct
profile-file mutation merely to gain bulk access.
Check current tool documentation before using manager pages, evaluation,
DevTools, CDP or native input. If the manager is inaccessible, use an already
available supported API; otherwise report the missing capability and stop at
audit/plan. Do not enable debugging or start an alternate profile just to gain
access, and do not disable CSP protections.

## Safe Batch Pattern

1. Read the current tree and resolve live IDs.
2. Execute one reversible pilot.
3. Verify the destination/title/URL by a fresh read.
4. Process short batches (for example 10-25 operations).
5. Re-read after every batch; do not trust only a console title/toast marker.
6. Stop on profile changes, login redirects, stale contexts, or unexpected
   count changes.

Large pasted console scripts can truncate or execute prematurely. Prefer short
commands or a reviewed helper. Browser-internal pages may block `fetch()` from
localhost through CSP.

## UI Automation

- Avoid physical mouse input when the user is working in Excel or another app.
- Prefer element focus plus keyboard, CDP, or bookmark API calls.
- Accessibility wrappers can become stale after page/DevTools updates; reacquire
  the window and input element between batches.
- Announce a necessary foreground step before proceeding. Restore the previous
  foreground only after key delivery and only if the user has not switched tasks.
- MCP Playwright and another Playwright CDP client must not share one CDP port
  concurrently.

## Edge Notes

Edge may label the feature "Favorites" rather than "Bookmarks" and may expose
different root names. Resolve roots from the live tree instead of hard-coding
Chrome root IDs or localized folder titles. Profiles and sync accounts must be
verified in Edge's own UI. Do not assume the DevTools console on
`edge://favorites` exposes the extension bookmark API.

## Completion Evidence

Use a fresh API/tree read or persisted manager state. A success toast, DevTools
title marker, or command exit code alone is insufficient.
Close only task-owned tabs or automation surfaces, never the user's existing
manager or the last tab of a shared browser.
