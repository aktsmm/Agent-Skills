---
name: "x-twitter-browser-ops"
description: "Read-only X/Twitter browser data workflow. Use when collecting X/Twitter followers, following, mutual followers, verified/non-verified splits, rankings, or CSV/HTML outputs via browser automation. Do not use for posting, DM, follow/unfollow, block, mute, or list edits."
argument-hint: "対象アカウント、取得したい followers/following/mutual/verified 情報、出力形式"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# X/Twitter Browser Ops

Use this skill for read-only X/Twitter browser data workflows: collecting followers/following lists, finding mutual followers, splitting verified vs non-verified accounts, ranking by follower count, and producing CSV/Markdown/HTML outputs.

## When to Use

- User asks for X/Twitter follower, following, mutual follower, or verified follower analysis.
- User asks to rank X/Twitter accounts by followers, export CSV/Markdown/HTML, or build a dashboard from collected X data.
- Browser automation is allowed and the task is read-only.

## Do Not Use

- Do not use for posting, replying, liking, reposting, DM, follow/unfollow, block, mute, list edits, or other write actions.
- Do not use to evade X rate limits, bans, access controls, paywalls, or privacy settings.
- Do not save or expose login cookies, auth headers, HAR files, tokens, or browser profile data.

## Safety and Session Rules

1. Confirm the user is logged in before collecting private/session-dependent lists.
2. Treat the browser session as sensitive. Never persist cookies, CSRF tokens, Authorization headers, or HAR captures.
3. Prefer read-only page navigation and response observation over replaying internal API calls.
4. If screenshots or HTML outputs include notification badges, DMs, private handles, or unrelated personal data, mask or omit them.
5. If any outbound action is requested, stop and require explicit preview + confirmation; this skill is otherwise read-only.

## X Page Semantics

Use URL path, not translated UI tab labels, to avoid tab mix-ups:

- `/followers` = all followers.
- `/following` = accounts the target follows.
- `/followers_you_follow` = followers known to the logged-in user; for the target user's own account this is the useful mutual-follower view.
- `/verified_followers` = verified followers only; this is not the same as all mutual followers.

For mutual analysis, collect from `/followers_you_follow` when available, or use `relationship_perspectives.following === true` and `relationship_perspectives.followed_by === true` from follower responses.

## Collection Workflow

1. Open the profile and confirm the target handle and visible counts.
2. Navigate to the correct path explicitly.
3. Attach browser response observers for GraphQL list responses; parse user objects from responses rather than relying only on visible text.
4. Scroll slowly in small batches. Suggested baseline: 4-5 scrolls per batch, 4-9 seconds between scrolls, and pause 30-60 seconds after large batches.
5. If HTTP 429, repeated 403, forced redirects, login prompts, or unusual challenge pages appear, stop collection and report partial results instead of pushing harder.
6. Deduplicate by `rest_id` / user ID. Keep `screen_name`, `name`, `followers_count`, `url`, and relationship flags.

## Verified / Non-Verified Split

1. Collect mutual follower IDs from the mutual source.
2. Collect verified follower IDs from `/verified_followers`; filter those where the logged-in account also follows them when relationship flags are available.
3. Verified mutual = mutual IDs present in verified mutual collection.
4. Non-verified mutual = mutual IDs minus verified mutual IDs.
5. Do not assume a visible blue badge in the DOM is enough; prefer response fields such as `is_blue_verified` or verified list membership.

## Ranking and Output

- Sort descending by `legacy.followers_count` / `followers_count`.
- Output rank, display name, handle, follower count, and profile URL.
- For Top 100, verify there are at least 100 rows; if fewer, say how many were collected.
- For HTML dashboards, delegate visual artifact styling to `web-artifacts-builder` when appropriate.
- For PowerShell-generated HTML, embed JSON safely: use `ConvertTo-Json -Compress`, place it in `<script type="application/json">`, and escape JSON `<`, `>`, and `&` as `\u003c`, `\u003e`, and `\u0026`. Do not HTML-encode JSON as `&quot;` before `JSON.parse`.

## Verification Checklist

Before final delivery, check:

- Target handle and source paths used.
- Collected counts for all mutual, verified mutual, and non-verified mutual.
- Duplicate user IDs removed.
- Top rows are sorted by follower count descending.
- CSV/Markdown/HTML files open and contain the expected row counts.
- For HTML: `JSON.parse` succeeds, stats are not `-`, card/table DOM rows render, and browser console/page errors are zero.
- Edge cases: zero results, fewer than 100 results, and missing follower counts are handled visibly rather than silently.
