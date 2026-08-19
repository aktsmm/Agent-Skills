# Classification Model

Use this model to create mutually exclusive destinations without losing the
user's mental shortcuts.

## Separate by Intent, Not Only Domain

| Intent | Typical destination |
| --- | --- |
| Open and perform an action | `00_Action-Login` |
| User-owned deployed app/site | `20_Owned-Services` |
| Learn, research, or reference | topic-specific reference folder |
| Publish or maintain content | publishing/workflow folder |
| Keep temporarily without confidence | `90_Review-Archive` |

A Microsoft, Azure, GitHub, or finance URL can belong to any of these intents.
Do not classify from hostname alone.

## Owned-Service Signals

Treat a URL as a candidate owned service when title/path/context suggests:

- deployment dashboard paired with an app endpoint
- Azure Static Web Apps, Front Door, Container Apps, Cloud Run, Render, Vercel,
  Netlify, GitHub Pages, or similar hosting
- a personalized app name, custom domain, admin route, or project slug

If ownership is unclear, retain it in review/archive or ask before destructive
cleanup. Never assume every `github.io` or cloud-hosted page is user-owned.

## Login and Transient URLs

Separate stable login/home URLs from:

- OAuth authorize/callback URLs
- SSO nonce, state, token, conversation, or completion URLs
- session-specific query strings
- post-payment, post-registration, or print-session pages

Replace a transient URL only when a stable official landing/sign-in URL is
clear. Keep the original in the dry-run plan for audit and recovery.

## Duplicate Rules

1. Remove exact URL duplicates first.
2. Preserve the copy in the more intentional path or toolbar position.
3. Do not merge merely similar pages without evidence.
4. After stable-URL replacement, rerun exact duplicate detection.
5. Prefer the pre-existing stable bookmark over the newly canonicalized copy.

When toolbar sparsity conflicts with duplicate preservation, keep the toolbar
copy only for an intentional frequent action/login shortcut; otherwise keep the
categorized folder copy while preserving the remaining toolbar order.

## Folder Design

- Keep direct toolbar shortcuts intentional and sparse.
- Default to at most two folder levels unless the user needs deeper domain
  hierarchy.
- Use numbered prefixes only when order conveys workflow or frequency.
- Keep one taxonomy; never add a second catch-all organized root.
- Create an archive/review folder for uncertain items instead of deleting them.
