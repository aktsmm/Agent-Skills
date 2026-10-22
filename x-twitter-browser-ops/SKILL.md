---
name: "x-twitter-browser-ops"
description: "X/Twitter browser analysis and explicitly approved mutations. Use for follower/following/mutual/verified analysis, X saved-post folder management, content/profile operations, or browser-driven troubleshooting. Not for public-post keyword/hashtag research or Chrome/Edge favorites."
argument-hint: "対象のX画面、実行したい操作、対象アカウントまたは投稿"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# X/Twitter Browser Ops

Use this skill for all X/Twitter browser operations: browsing and analysis, follower/following collection, bookmark-folder management, content/profile management, and browser-driven troubleshooting.

## When to Use

- User asks for X/Twitter follower, following, mutual follower, or verified follower analysis.
- User asks to rank X/Twitter accounts by followers, export CSV/Markdown/HTML, or build a dashboard from collected X data.
- User asks to organize bookmarks, create/rename/delete bookmark folders, or move bookmarks between folders.
- User asks to operate X/Twitter in the browser.

## Do Not Use

- Do not use to evade X rate limits, bans, access controls, paywalls, or privacy settings.
- Do not save or expose login cookies, auth headers, HAR files, tokens, or browser profile data.

## Safety and Session Rules

1. Inspect available browser tool documentation before choosing a route. Verify the intended logged-in account for session-dependent lists; do not assume CDP, script evaluation, response observers, native input, or folder features exist.
2. Treat the browser session as sensitive. Never persist cookies, CSRF tokens, Authorization headers, or HAR captures.
3. Prefer read-only page navigation and response observation over replaying internal API calls.
4. If screenshots or HTML outputs include notification badges, DMs, private handles, or unrelated personal data, mask or omit them.
5. Every mutation (including bookmark changes, posts, replies, DMs, engagement, follow/unfollow, block/mute, list edits, and profile changes) requires explicit approval binding account, target, operation, exact body/field value, attachments, and visibility, including explicit absence where applicable. Reuse existing explicit approval only when ALL these dimensions are exactly unchanged; any change requires renewed approval before execution. Drafting, research, or inspection never authorizes sending or mutation.
6. Bookmark folder creation, renaming, deletion, and assignment are permitted after the user explicitly approves the organization plan.
7. Before any write or relationship-changing action, verify the acting account identity from the account switcher or profile UI and confirm it matches the intended account for this task.
8. Reacquire the exact target and current controls before each mutation. Confirm persisted UI state independently afterward; a click, toast, or vanished element is insufficient. If a write result is uncertain, stop writes and inspect before retrying; never blindly repeat a send or toggle.
9. Keep all collection and mutations within finite task-specific bounds. Stop on rate limits, repeated access failures, login redirects, or challenges; report partial results without bypassing refusals or replaying internal APIs with extracted credentials.
10. Use task-owned tabs with stable identifiers when supported; preserve the user's foreground, unrelated tabs, and unsaved work. Close only task-owned tabs. If tool capabilities cannot safely bind a target or verify a write, stop that action as unverified rather than inventing a selector or API.

## Post Draft Validation

- Before treating a draft as ready to post or entering it in the browser, measure it with a `twitter-text` v3-compatible parser using the official configuration: https://raw.githubusercontent.com/twitter/twitter-text/master/config/v3.json
- Require `valid === true` and `weightedLength <= maxWeightedTweetLength` from that configuration for a standard post. For another composer/account format, verify actual constraints instead of treating 280 as universal.
- Let the parser apply URL transformation and emoji parsing. An HTTP(S) URL uses `transformedURLLength` (currently 23), while ZWJ emoji and variation selectors must not be counted by visible glyphs or `String.length`.
- If a compatible parser or configuration is unavailable, report the draft as length-unverified rather than claiming it is ready to post.
- Do not install dependencies globally merely to validate a draft.

## Bookmark Management

1. Inspect existing folders plus representative unfoldered and folder-specific posts before proposing a minimal taxonomy.
2. Show the proposed folder names, merges, renames, and classification priority before mutating bookmarks.
3. Confirm each assignment from the UI before removing a post from its prior folder.
4. In virtualized infinite-scroll feeds, operate in bounded batches using a post's canonical `/status/` URL; re-resolve the post immediately before each mutation and never retain an element ref across scrolls or mutations.
5. Process one visible post at a time and re-scan canonical URLs after each folder-picker mutation; do not pre-capture a whole visible candidate batch because X can recycle the sibling articles immediately.
6. On a shared logged-in browser, use a dedicated work tab and bind its stable identifier, not a positional tab index. Before every write batch, verify account, bookmark view, folder/search query, and exact post. Treat `/i/bookmarks` as a live-verifiable hint, not a guaranteed route; do not assume CDP.
7. Folder membership hydrates after the picker shell. Wait for checkmark/icon state before deciding assigned vs unassigned; an immediately missing checkmark is unknown, not safe to click.
8. X can render duplicate dialog shells. Use the current visible dialog; when geometry is exposed require positive width/height. Prefer its actual close control; use history back only after verifying the picker route (hint: `/i/bookmarks/add`) and its effect. Never issue an extra back after closure.
9. Treat missing folder-picker options, modals, or navigations as unverified—not as success. Keep the source assignment until the destination is visibly confirmed.
10. Never unsave a post to remove a folder assignment; check impact before deleting/merging folders. Log post ID, source, destination, and confirmed/unknown outcome. Deduplicate counts by post ID and report skipped/unverified memberships plus the last processed URL. Stagnant scrolling alone does not prove completion; require an end indicator or exposed cursor evidence.

## X Page Semantics

Use URL path, not translated UI tab labels, to avoid tab mix-ups:

- `/followers` = all followers.
- `/following` = accounts the target follows.
- `/followers_you_follow` = followers known to the logged-in user; for the target user's own account this is the useful mutual-follower view.
- `/verified_followers` = verified followers only; this is not the same as all mutual followers.

For the logged-in user's own account, `/followers_you_follow` is a useful mutual view. For another target it does NOT prove that target follows those users: intersect that target's follower/following IDs or use relationship fields only after verifying their subject.

X changes DOM structure and GraphQL response shapes without notice. Re-verify these paths and field names against the live page instead of relying on remembered selectors.

## Collection Workflow

1. Open the profile and confirm the target handle and visible counts.
2. Navigate to the correct path explicitly.
3. Observe list responses only if actual tools expose read-only observation; otherwise use DOM/screen evidence and report missing fields. Verify live response schema and relationship subject before parsing.
4. Scroll slowly in small batches. Suggested baseline: 4-5 scrolls per batch, 4-9 seconds between scrolls, and pause 30-60 seconds after large batches.
5. If HTTP 429, repeated 403, forced redirects, login prompts, or unusual challenge pages appear, stop collection and report partial results instead of pushing harder.
6. If stopping early, record a resume checkpoint: last collected `rest_id`, canonical URL of the last processed post, and total collected count.
7. Deduplicate by stable user ID where exposed, otherwise canonical profile URL (handles can change). Keep available name/handle, follower count, URL, and relationship flags; absent fields stay unknown. A checkpoint does not guarantee resuming at the same row.

## Verified / Non-Verified Split

1. Collect mutual follower IDs from the mutual source.
2. Collect verified follower IDs from `/verified_followers`; filter those where the logged-in account also follows them when relationship flags are available.
3. Verified mutual = mutual IDs present in verified mutual collection.
4. Non-verified mutual = mutual IDs minus verified mutual IDs ONLY when source coverage proves that comparison; absence from an incomplete verified list means unknown status. Report a separate unknown group.
5. Do not assume a visible blue badge in the DOM is enough; prefer response fields such as `is_blue_verified` or verified list membership.

## Ranking and Output

- Sort descending by `legacy.followers_count` / `followers_count`.
- Rank only known counts; display missing counts explicitly, never as zero.
- Output rank, display name, handle, follower count, and profile URL.
- For Top 100, verify there are at least 100 rows; if fewer, say how many were collected.
- For HTML dashboards, keep styling minimal; polished visual artifact design is out of scope.
- Return analysis in chat unless files are requested or needed by the task; record source views, bounds, missing fields, and coverage alongside any exported rows.
- For PowerShell-generated HTML, embed JSON safely: use `ConvertTo-Json -Compress`, place it in `<script type="application/json">`, and escape JSON `<`, `>`, and `&` as `\u003c`, `\u003e`, and `\u0026`. Do not HTML-encode JSON as `&quot;` before `JSON.parse`.

## Verification Checklist

Before final delivery, check:

- Acting account verified before mutation.
- Target handle and source paths used.
- Collected counts for all mutual, verified mutual, and non-verified mutual.
- Duplicate user IDs removed.
- Partial-stop output includes the resume checkpoint.
- Top rows are sorted by follower count descending.
- CSV/Markdown/HTML files open and contain the expected row counts.
- For HTML: `JSON.parse` succeeds, stats are not `-`, card/table DOM rows render, and browser console/page errors are zero.
- Edge cases: zero results, fewer than 100 results, and missing follower counts are handled visibly rather than silently.
