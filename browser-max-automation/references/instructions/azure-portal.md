# Azure Portal Automation Notes

Azure Portal is a hash-routed app with iframe/OOPIF content. Use these notes when deep links or blade operations behave differently from normal pages.

## Deep Links

- If a new tab opens a Portal deep link and falls back to login, reuse an existing logged-in Portal tab first.
- Verify arrival with URL, title, and visible body text; URL alone is not enough.
- Subview URLs can land on overview or spin indefinitely. Capture a screenshot before switching paths.

## iframe / OOPIF

- Portal content often renders inside `sandbox-*.reactblade.portal.azure.net` iframes.
- If `page.evaluate()` only sees the outer frame, search `page.frames()` and evaluate inside the content frame.
- If Playwright frames do not expose it, CDP `Target.getTargets()` may show an OOPIF target. Attach with `Target.attachToTarget(flatten=true)` when needed.

```javascript
const contentFrame = page.frames().find(frame => frame.url().includes('reactblade.portal.azure.net'));
if (contentFrame) {
  const text = await contentFrame.evaluate(() => document.body.innerText);
}
```

## Trusted Event Boundary

- Some `openBlade()` transitions require a trusted user event.
- If iframe text and handlers are visible but blade open does not fire from JS, switch only that final action to a real click/manual operation.