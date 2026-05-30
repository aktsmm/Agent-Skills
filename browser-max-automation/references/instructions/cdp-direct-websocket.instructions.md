# Direct CDP WebSocket Automation

Use this reference when Playwright MCP or Playwright `connect_over_cdp()` is unstable, when an existing Edge/Chrome session must be reused, or when direct Chrome DevTools Protocol (CDP) commands are safer than browser-level automation.

## When to Prefer Direct WebSocket CDP

- Existing browser session must be reused without creating another Playwright session.
- Playwright `connect_over_cdp()` fails because of extension service worker targets or browser-context assertions.
- MCP and Python automation would otherwise compete for the same CDP endpoint.
- The task needs low-level `Runtime.evaluate`, `Page.captureScreenshot`, or hash-based SPA navigation.

## Browser Launch Flags

Launch Edge or Chrome with a dedicated debugging port.

```powershell
Start-Process 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe' `
  -ArgumentList '--remote-debugging-port=9223', '--remote-allow-origins=*', '--restore-last-session'
```

If you need `--profile-directory=Profile 2` or any other argument whose value contains spaces, pass that flag as one quoted argument. Otherwise PowerShell can split it and launch the wrong profile.

```powershell
Start-Process 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe' `
  -ArgumentList '--remote-debugging-port=9223', '--remote-allow-origins=*', '"--profile-directory=Profile 2"'
```

Rules:

- `--remote-debugging-port=<port>` exposes the CDP endpoint.
- `--remote-allow-origins=*` avoids WebSocket `403 Forbidden` in environments that enforce origin checks.
- `--restore-last-session` is useful when the existing tab/session matters.
- If only one browser profile has the right login state, keep the default browser user data and pin `--profile-directory=<known profile>` instead of creating an ad-hoc `--user-data-dir`.
- Use a separate port when Playwright MCP already owns another CDP endpoint.

## Direct WebSocket Connection

Use `websocket-client` for raw CDP access. Avoid adding a second Playwright CDP session when MCP is already attached.

```python
import json
import urllib.request
import websocket

# List page targets.
tabs = json.loads(urllib.request.urlopen('http://localhost:9223/json').read())
page_tabs = [tab for tab in tabs if tab.get('type') == 'page']

target_tab = page_tabs[0]
ws = websocket.create_connection(
    target_tab['webSocketDebuggerUrl'],
    timeout=60,
    suppress_origin=True,
)
```

If the task depends on an already-open draft/editor tab, do not stop at `/json/version`. Query `/json/list`, filter for `type == 'page'`, and pick the tab by URL/title pattern before sending commands.

```python
tabs = json.loads(urllib.request.urlopen('http://localhost:9223/json/list').read())
draft_tabs = [
  tab for tab in tabs
  if tab.get('type') == 'page' and 'qiita.com/drafts/' in (tab.get('url') or '')
]
target_tab = draft_tabs[0]
```

## Command Helper

CDP targets can emit many events. Always wait for the matching command `id` rather than reading the next message blindly.

```python
import itertools
import json
import time
import websocket

_next_id = itertools.count(1)

def cdp(ws, method, params=None, timeout=30):
    message_id = next(_next_id)
    ws.send(json.dumps({'id': message_id, 'method': method, 'params': params or {}}))
    end = time.time() + timeout
    while time.time() < end:
        ws.settimeout(max(1, end - time.time()))
        try:
            message = json.loads(ws.recv())
            if message.get('id') == message_id:
                return message
        except websocket.WebSocketTimeoutException:
            continue
    raise TimeoutError(f'CDP command timed out: {method}')
```

Enable required domains before use:

```python
cdp(ws, 'Page.enable')
cdp(ws, 'Runtime.enable')
```

## SPA Navigation

For single-page apps, full `Page.navigate` can reset client state or trigger a full reload. Prefer in-app navigation when the app supports hash routing.

```python
cdp(ws, 'Runtime.evaluate', {
    'expression': 'window.location.hash = "#/target-route"',
    'returnByValue': True,
})
```

Some SPAs (e.g., Angular with `HashLocationStrategy`) do not respond to `location.hash` assignment alone. If the route change does not take effect, use full `location.href` assignment instead:

```python
cdp(ws, 'Runtime.evaluate', {
    'expression': 'location.href = "https://app.example.com/#/target-route"',
    'returnByValue': True,
})
```

Never use `Page.navigate` for hash-based SPA routes — the SPA router will not fire, and the page may reload to a default/home route.

## Screenshot and Text Extraction

```python
import base64

screenshot = cdp(ws, 'Page.captureScreenshot', {'format': 'png'})
image_bytes = base64.b64decode(screenshot['result']['data'])

text = cdp(ws, 'Runtime.evaluate', {
    'expression': 'document.body.innerText.substring(0, 10000)',
    'returnByValue': True,
})['result']['result']['value']
```

## Hidden File Input Upload

For editors that hide `input[type=file]` behind custom buttons, raw CDP can upload without Playwright `connect_over_cdp()` or a visible file chooser.

```python
cdp(ws, 'DOM.enable')
cdp(ws, 'Runtime.enable')

root = cdp(ws, 'DOM.getDocument', {'depth': -1, 'pierce': True})['result']['root']
node_id = cdp(ws, 'DOM.querySelector', {
  'nodeId': root['nodeId'],
  'selector': 'input[type="file"]',
})['result']['nodeId']

before_urls = cdp(ws, 'Runtime.evaluate', {
  'expression': '(document.documentElement.outerHTML.match(/https://qiita-image-store\\.s3[^"\'\\s)]+/g) || [])',
  'returnByValue': True,
})['result']['result']['value']

cdp(ws, 'DOM.setFileInputFiles', {
  'nodeId': node_id,
  'files': [image_path],  # absolute local path resolved by the caller
})
cdp(ws, 'Runtime.evaluate', {
  'expression': '''(() => {
    const input = document.querySelector('input[type="file"]');
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
  })()''',
  'awaitPromise': True,
})
```

Rules:

- Reuse the already-open draft/editor tab; do not navigate away from an unsaved page.
- Prefer HTML-diff URL detection after upload instead of assuming the last image on the page is the new one.
- Use this fallback when Playwright `connect_over_cdp()` reaches `<ws connected>` and then times out, or when MCP cannot drive the file chooser cleanly.
- If upload still times out on an existing draft/editor tab, open a **fresh draft** (`/drafts/new`) in a separate tab and retry there. Some long-lived unsaved drafts do not trigger upload reliably even when `DOM.setFileInputFiles` succeeds.

## Azure Portal OOPIF and Trusted Event Notes

Azure Portal often renders blade content inside `sandbox-*.reactblade.portal.azure.net` iframe targets. In CDP, these can appear as separate `type=iframe` targets.

```python
targets = cdp(browser_ws, 'Target.getTargets')['result']['targetInfos']
portal_iframes = [
  t for t in targets
  if t.get('type') == 'iframe' and 'reactblade.portal.azure.net' in (t.get('url') or '')
]
```

If outer-frame DOM inspection cannot see the content, attach directly to the iframe target:

```python
attach = cdp(browser_ws, 'Target.attachToTarget', {
  'targetId': iframe_target_id,
  'flatten': True,
})
session_id = attach['result']['sessionId']

cdp(browser_ws, 'Runtime.enable', session_id=session_id)
```

Important:

- Some Azure Portal actions call internal SDK methods such as `openBlade()`.
- You may be able to inspect React handlers or invoke `onClick`, but blade navigation can still fail because the Portal expects a **trusted user event**.
- When iframe text is visible but programmatic click / handler invocation does not navigate, treat this as a Portal constraint and switch the last click to a human.

## Session Extraction and Headless Handoff

If the browser already holds the valid login state, prefer extracting session material at runtime and moving the bulk operation out of visible UI flows.

- Use CDP to read cookies, local storage, CSRF tokens, or in-page bootstrap state from the live browser session.
- Pass the extracted values directly to a headless HTTP/API helper in the same run.
- Keep the browser UI for login, target verification, and before/after evidence only.
- Do not persist tokens, cookies, or auth headers to tracked files.

## Virtual Scroll and Modal Patterns

For Angular/Material or other virtual-scroll UIs, combine scroll, element detection, click, and post-click polling into one async `Runtime.evaluate` call. Splitting these steps across multiple CDP calls can lose DOM references.

```javascript
(async () => {
  const findRows = (scope, targetText) =>
    [...scope.querySelectorAll("*")].filter(
      (el) =>
        (el.innerText || "").includes(targetText) &&
        el.querySelectorAll("*").length < 30,
    );

  const pickClickable = (rows) => {
    const candidates = [];
    for (const row of rows) {
      let node = row;
      for (let depth = 0; depth < 8; depth++) {
        if (!node || !node.offsetParent) break;
        if (getComputedStyle(node).cursor === "pointer") candidates.push(node);
        node = node.parentElement;
      }
    }
    return candidates[0] || rows[rows.length - 1];
  };

  const scope = document.body;
  const targetText = "Target text";
  let rows = findRows(scope, targetText);

  if (rows.length === 0) {
    const scroller = scope.querySelector('[style*="overflow-y"]') || scope;
    for (let step = 0; step <= 30; step++) {
      scroller.scrollTop = (scroller.scrollHeight * step) / 30;
      await new Promise((resolve) => setTimeout(resolve, 180));
      rows = findRows(scope, targetText);
      if (rows.length > 0) break;
    }
  }

  if (rows.length === 0) return "not-found";

  const element = pickClickable(rows);
  element.scrollIntoView({ block: "center" });
  await new Promise((resolve) => setTimeout(resolve, 400));
  element.click();

  for (let i = 0; i < 25; i++) {
    await new Promise((resolve) => setTimeout(resolve, 200));
    if (document.body.innerText.includes("Expected next state")) return "ok";
  }
  return "timeout";
})();
```

Rules:

- Search ancestors for clickable elements; the deepest text node often has no click handler.
- Prefer `getComputedStyle(node).cursor === 'pointer'` as one signal, but still verify the next UI state.
- For modal chains, close overlays and reopen the modal from a known state between iterations.
- Before looping by date/week, verify that changing the date actually changes modal content.

## Encoding for Windows Python Scripts

When Python scripts print Japanese or emoji in Windows terminals, configure UTF-8 on both sides.

```powershell
chcp 65001 | Out-Null
$env:PYTHONIOENCODING = 'utf-8'
```

```python
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
```

## Troubleshooting

| Symptom                                     | Likely Cause                               | Fix                                                              |
| ------------------------------------------- | ------------------------------------------ | ---------------------------------------------------------------- |
| WebSocket `403 Forbidden`                   | Missing `--remote-allow-origins=*`         | Restart browser with the flag                                    |
| Playwright assertion / service worker crash | Extension service worker targets           | Use direct WebSocket CDP                                         |
| `Runtime.evaluate` timeout                  | Domain not enabled or event stream ignored | `Runtime.enable` and filter responses by `id`                    |
| Session resets after navigation             | Full page reload in SPA                    | Use hash or in-app navigation                                    |
| Click does nothing in virtual scroll        | DOM reference lost or wrong target node    | Use one async eval and ancestor clickable search                 |
| Later modal operations fail                 | Overlay state is stale                     | Close overlays and reopen from a known state                     |
| `UnicodeEncodeError: cp932`                 | Windows default console encoding           | Set `chcp 65001`, `PYTHONIOENCODING`, and stdout/stderr encoding |
| CDP connects to wrong tab (e.g. `sw.js`)   | SPA registers service worker tabs          | Filter `/json` results: exclude `sw.js` URLs and `type !== "page"` tabs. Pass verified `webSocketDebuggerUrl` or filter in helper |
| Date-click or `select_date` fails silently  | SPA updated CSS classes for date buttons   | Do not rely on fixed CSS class selectors (e.g. `.carousel-date-btn`). Match buttons by visible `innerText` with day number + weekday pattern instead |
