# Webview Safety Checklist

- Embed initial data via `<script type="application/json" id="initial-data">` and parse with `JSON.parse`; escape `<` and U+2028/2029; never use `document.write` or Base64-injected scripts.
- Bind UI actions with `data-action`/`data-id` plus delegated click handler; avoid inline `onclick` and avoid TypeScript casts (`as HTMLElement`) inside template strings.
- Escape HTML/attribute values before injecting into templates; prefer `escapeHtml`/`escapeAttr` helpers.
- After each build, open the emitted `debug-webview.html` (or equivalent) and check for SyntaxError/quote issues; then open Webview Developer Tools Console to verify no CSP or runtime errors.
- Smoke test critical interactions (tab switch, dropdowns, buttons) once after build; watch console logs for errors.
