"""Verify that a CDP Edge session points at the intended ESXP profile/page.

This script is read-only. It connects to an already running CDP port, inspects ESXP
tabs, and fails fast when the tab is Home/sign-in/wrong request. It cannot attach
to an Edge instance that was not launched with --remote-debugging-port.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any

import websocket


ESXP_HOST = "esxp.microsoft.com"


class CdpPage:
    def __init__(self, websocket_url: str, timeout: float = 10) -> None:
        self.websocket_url = websocket_url
        self.timeout = timeout
        self.ws: websocket.WebSocket | None = None
        self._msg_id = 0

    def __enter__(self) -> "CdpPage":
        self.ws = websocket.create_connection(self.websocket_url, timeout=self.timeout, suppress_origin=True)
        self.cmd("Runtime.enable")
        return self

    def __exit__(self, *args: Any) -> None:
        if self.ws:
            self.ws.close()

    def cmd(self, method: str, params: dict[str, Any] | None = None, timeout: float | None = None) -> dict[str, Any] | None:
        if not self.ws:
            raise RuntimeError("CDP is not connected")
        self._msg_id += 1
        msg_id = self._msg_id
        self.ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
        end = time.time() + (timeout or self.timeout)
        while time.time() < end:
            self.ws.settimeout(max(1, end - time.time()))
            try:
                msg = json.loads(self.ws.recv())
            except websocket.WebSocketTimeoutException:
                continue
            if msg.get("id") == msg_id:
                return msg
        return None

    def eval(self, expression: str, timeout: float | None = None) -> Any:
        response = self.cmd(
            "Runtime.evaluate",
            {"expression": expression, "returnByValue": True, "awaitPromise": True},
            timeout=timeout,
        )
        if not response or "result" not in response:
            return None
        return response["result"].get("result", {}).get("value")


def fetch_json(url: str) -> Any:
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def find_target(tabs: list[dict[str, Any]], request_id: str | None) -> dict[str, Any] | None:
    pages = [tab for tab in tabs if tab.get("type") == "page" and ESXP_HOST in str(tab.get("url") or "")]
    if request_id:
        request_pages = [tab for tab in pages if request_id.lower() in str(tab.get("url") or "").lower()]
        if request_pages:
            return request_pages[0]
    for fragment in ("supportdelivery/requestdetails", "time/weekview", ESXP_HOST):
        hit = next((tab for tab in pages if fragment in str(tab.get("url") or "")), None)
        if hit:
            return hit
    return None


def build_probe_script(expected_account: str | None, expected_texts: list[str]) -> str:
    account = json.dumps((expected_account or "").lower())
    texts = json.dumps([text.lower() for text in expected_texts])
    return f"""
    (() => {{
        const text = document.body ? (document.body.innerText || '') : '';
        const haystack = (location.href + '\\n' + document.title + '\\n' + text).toLowerCase();
        const expectedAccount = {account};
        const expectedTexts = {texts};
        const storageHits = [];
        for (const store of [localStorage, sessionStorage]) {{
            for (let i = 0; i < store.length; i++) {{
                const key = store.key(i);
                const value = store.getItem(key) || '';
                const combined = (key + '=' + value).toLowerCase();
                if (expectedAccount && combined.includes(expectedAccount)) {{
                    storageHits.push(key);
                }}
            }}
        }}
        return {{
            href: location.href,
            title: document.title,
            readyState: document.readyState,
            textSample: text.slice(0, 1200),
            expectedTextResults: expectedTexts.map(t => [t, haystack.includes(t)]),
            accountInPage: expectedAccount ? haystack.includes(expectedAccount) : null,
            accountInStorage: expectedAccount ? storageHits.length > 0 : null,
            storageHitKeys: storageHits.slice(0, 20),
        }};
    }})()
    """


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cdp-port", type=int, default=int(os.environ.get("ESXP_CDP_PORT", "9222")))
    parser.add_argument("--expected-account", default=os.environ.get("ESXP_EXPECTED_ACCOUNT", ""))
    parser.add_argument("--request-id", help="Request ID that must be present in the ESXP URL or page text")
    parser.add_argument("--expected-text", action="append", default=[], help="Additional text that must be present")
    parser.add_argument("--strict-account", action="store_true", help="Fail if expected account is not visible in page/storage")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    expected_texts = list(args.expected_text)
    if args.request_id:
        expected_texts.append(args.request_id)

    result: dict[str, Any] = {"ok": False, "cdp_port": args.cdp_port, "errors": [], "warnings": []}
    try:
        tabs = fetch_json(f"http://localhost:{args.cdp_port}/json")
    except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
        result["errors"].append(
            f"CDP port {args.cdp_port} is not reachable. Start Edge with --remote-debugging-port={args.cdp_port}. ({error})"
        )
        return emit(result, args.json)

    target = find_target(tabs, args.request_id)
    result["esxp_tabs"] = [
        {"title": tab.get("title"), "url": tab.get("url")} for tab in tabs if ESXP_HOST in str(tab.get("url") or "")
    ]
    if not target:
        result["errors"].append(f"No ESXP tab found on CDP port {args.cdp_port}.")
        return emit(result, args.json)

    result["target"] = {"title": target.get("title"), "url": target.get("url")}
    with CdpPage(target["webSocketDebuggerUrl"]) as page:
        probe = page.eval(build_probe_script(args.expected_account, expected_texts), timeout=10) or {}
    result["probe"] = probe

    href = str(probe.get("href") or target.get("url") or "")
    title = str(probe.get("title") or target.get("title") or "")
    text = str(probe.get("textSample") or "")
    if href.rstrip("/").endswith("/#") or href.rstrip("/").endswith("/#/") or title.lower() == "home":
        result["errors"].append("ESXP resolved to Home. This usually means the CDP browser is not the intended work profile/account.")
    if "login.microsoftonline.com" in href.lower() or "sign in" in text.lower():
        result["errors"].append("The ESXP tab appears unauthenticated or on a sign-in page.")

    missing = [text for text, found in probe.get("expectedTextResults") or [] if not found]
    if missing:
        result["errors"].append("Expected text not found: " + ", ".join(missing))

    if args.expected_account and not (probe.get("accountInPage") or probe.get("accountInStorage")):
        message = f"Expected account {args.expected_account} was not visible in ESXP page/storage. Browser chrome profile may still be correct, but CDP cannot prove it from the page."
        if args.strict_account:
            result["errors"].append(message)
        else:
            result["warnings"].append(message)

    result["ok"] = not result["errors"]
    return emit(result, args.json)


def emit(result: dict[str, Any], as_json: bool) -> int:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "OK" if result["ok"] else "FAILED"
        print(f"ESXP profile preflight: {status}")
        print(f"CDP port: {result.get('cdp_port')}")
        target = result.get("target") or {}
        if target:
            print(f"Target: {target.get('title')} | {target.get('url')}")
        for warning in result.get("warnings") or []:
            print(f"WARNING: {warning}")
        for error in result.get("errors") or []:
            print(f"ERROR: {error}")
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())