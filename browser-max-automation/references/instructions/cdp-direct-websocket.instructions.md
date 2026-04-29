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

Rules:

- `--remote-debugging-port=<port>` exposes the CDP endpoint.
- `--remote-allow-origins=*` avoids WebSocket `403 Forbidden` in environments that enforce origin checks.
- `--restore-last-session` is useful when the existing tab/session matters.
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

After hash navigation, wait for the target UI state using polling rather than fixed sleeps when possible.

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
