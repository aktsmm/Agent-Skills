"""Conservative ESXP labor API helper CLI.

This tool promotes the reusable parts of ad-hoc ESXP recovery work:

1. Capture authenticated ESXP core labor API headers from a live Week View tab.
2. Fetch core and draft labor records for a week and summarize them.
3. Convert draft records to submitted core records with an explicit late-submission reason.
4. Add non-project labor entries through the core API.
5. Add dispatch labor entries through the core API.
6. Delete a specific core labor record only after re-fetching its live record identity.
7. Delete a specific draft labor record by laborId (no Late Reason required).

No bearer token, cookie, or subscription key is printed or written to disk. Mutating
commands default to dry-run and require --apply.

Examples:
    python labor_api_tools.py fetch-week --start-date 2026-04-19 --end-date 2026-04-25

    python labor_api_tools.py submit-drafts --start-date 2026-04-19 --end-date 2026-04-25 \
        --reason-code-id 333185 --apply

    python labor_api_tools.py add-nonproject --date 2026-04-24 --hours 8 \
        --category-id 368709 --category-name "Mentor/Community/ Practice Contribution" \
        --reason-code-id 333185 --notes "Community contribution" --apply

    python labor_api_tools.py add-nonproject --dates 2026-05-04,2026-05-05,2026-05-06 --hours 8 \
        --category-id 982947 --category-name "Out of office" --notes "Japanese Holiday" \
        --omit-action-details --inherit-request-headers --apply

    python labor_api_tools.py add-dispatch --date 2026-05-08 --hours 4 \
        --assignment-id 5227797 --assignment-name RMOT2026041705203975 \
        --customer-name "Customer" \
        --product-name "Technical Update Briefing - Azure - Closed Workshop" \
        --reason-code-id 333177 --apply

    # Remove a stray duplicate draft entry without going through the UI.
    python labor_api_tools.py delete-draft --start-date 2026-06-08 --end-date 2026-06-14 \
        --labor-id 40219eaa-0000-0000-0000-000000000000 --apply
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import websocket


ESXP_URL_FRAGMENT = "esxp.microsoft.com"
DEFAULT_HOST = "https://professionalservices.microsoft.com"
CORE_PATH = "/lmt-coreapi/api/v1/labor"
DRAFT_PATH = "/lmt-draftapi/api/v1/draftLabor"
TOKEN_HEADER_RE = re.compile(r"authorization|cookie|subscription|ocp-apim", re.I)


@dataclass
class CapturedApi:
    url: str
    request_headers: dict[str, str]
    payload: Any


class CdpSession:
    def __init__(self, cdp_port: int, timeout: float = 30) -> None:
        self.cdp_port = cdp_port
        self.timeout = timeout
        self.ws: websocket.WebSocket | None = None
        self.msg_id = 0
        self.pending: deque[dict[str, Any]] = deque()

    def _urlopen_retry(self, url: str, attempts: int = 30, delay: float = 0.5) -> Any:
        """Retry urlopen to survive transient ephemeral-port exhaustion (WinError 10048)."""
        last_err: Exception | None = None
        for _ in range(attempts):
            try:
                return json.loads(urllib.request.urlopen(url, timeout=5).read())
            except OSError as exc:
                last_err = exc
                time.sleep(delay)
        raise RuntimeError(f"urlopen failed after {attempts} attempts: {last_err}")

    def _ws_connect_retry(self, ws_url: str, attempts: int = 30, delay: float = 0.5) -> websocket.WebSocket:
        """Retry WebSocket connect to survive transient ephemeral-port exhaustion (WinError 10048)."""
        last_err: Exception | None = None
        for _ in range(attempts):
            try:
                return websocket.create_connection(ws_url, timeout=self.timeout, suppress_origin=True)
            except OSError as exc:
                last_err = exc
                time.sleep(delay)
        raise RuntimeError(f"WebSocket connect failed after {attempts} attempts: {last_err}")

    def __enter__(self) -> "CdpSession":
        tabs = self._urlopen_retry(f"http://127.0.0.1:{self.cdp_port}/json")
        esxp_tabs = [tab for tab in tabs if tab.get("type") == "page" and ESXP_URL_FRAGMENT in tab.get("url", "")]
        if not esxp_tabs:
            raise RuntimeError("ESXP tab not found. Open ESXP Week View in the CDP-enabled browser first.")
        target = next((tab for tab in esxp_tabs if "weekview" in tab.get("url", "")), esxp_tabs[0])
        # Force IPv4 loopback + retry to survive ephemeral-port exhaustion (WinError 10048)
        ws_url = target["webSocketDebuggerUrl"].replace("ws://localhost:", "ws://127.0.0.1:")
        self.ws = self._ws_connect_retry(ws_url)
        self.request("Page.enable")
        try:
            self.request("Runtime.enable", timeout=5)
        except TimeoutError:
            # Network capture does not require Runtime; continue when the page is busy.
            pass
        self.request("Network.enable")
        if "weekview" not in target.get("url", ""):
            self.request("Page.navigate", {"url": "https://esxp.microsoft.com/#/time/weekview"}, timeout=5)
            time.sleep(3)
        return self

    def __exit__(self, *args: Any) -> None:
        if self.ws:
            self.ws.close()
            self.ws = None

    def send(self, method: str, params: dict[str, Any] | None = None) -> int:
        if not self.ws:
            raise RuntimeError("CDP session is not connected")
        self.msg_id += 1
        self.ws.send(json.dumps({"id": self.msg_id, "method": method, "params": params or {}}))
        return self.msg_id

    def recv(self, timeout: float | None = None) -> dict[str, Any] | None:
        if self.pending:
            return self.pending.popleft()
        if not self.ws:
            raise RuntimeError("CDP session is not connected")
        self.ws.settimeout(timeout or self.timeout)
        try:
            return json.loads(self.ws.recv())
        except websocket.WebSocketTimeoutException:
            return None

    def request(self, method: str, params: dict[str, Any] | None = None, timeout: float | None = None) -> dict[str, Any]:
        msg_id = self.send(method, params)
        end_time = time.time() + (timeout or self.timeout)
        while time.time() < end_time:
            msg = self.recv(max(0.5, end_time - time.time()))
            if not msg:
                continue
            if msg.get("id") == msg_id:
                return msg
            # Ignore async CDP events while waiting for a command response.
            # Re-queueing them here causes the same event to be read repeatedly.
        raise TimeoutError(f"CDP command timed out: {method}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cdp-port", type=int, default=int(os.environ.get("ESXP_CDP_PORT", "9222")))
    parser.add_argument("--alias", default=os.environ.get("ESXP_USER_ALIAS", "youralias"))
    parser.add_argument("--trigger", choices=["none", "reload"], default="reload")
    parser.add_argument("--wait-seconds", type=float, default=45)

    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser("fetch-week", help="Fetch and summarize core/draft labor records for a week")
    add_week_args(fetch_parser)
    fetch_parser.add_argument("--format", choices=["json", "markdown", "table"], default="table")
    fetch_parser.add_argument("--include-raw", action="store_true", help="Include raw API records in JSON output")

    submit_parser = subparsers.add_parser("submit-drafts", help="Create core labor records from unmatched draft records")
    add_week_args(submit_parser)
    add_reason_args(submit_parser, required=True)
    submit_parser.add_argument("--comment", default="Late submission after draft correction")
    submit_parser.add_argument("--delete-drafts", action="store_true", help="Delete matching draft records after core POST succeeds")
    submit_parser.add_argument("--apply", action="store_true")

    add_parser = subparsers.add_parser("add-nonproject", help="Add one non-project labor record through the core API")
    add_parser.add_argument("--date", help="Single date, YYYY-MM-DD")
    add_parser.add_argument("--dates", help="Comma-separated dates, e.g. 2026-05-04,2026-05-05")
    add_parser.add_argument("--hours", required=True, help="Decimal hours or HH:MM[:SS]")
    add_parser.add_argument("--category-id", required=True, type=int)
    add_parser.add_argument("--category-name", required=True)
    add_parser.add_argument("--notes", default="")
    add_reason_args(add_parser, required=False)
    add_parser.add_argument("--comment", default="Late submission after correction")
    add_parser.add_argument(
        "--omit-action-details",
        action="store_true",
        help="Do not include actionDetails in the POST payload",
    )
    add_parser.add_argument(
        "--inherit-request-headers",
        action="store_true",
        help="Prefer the freshest captured submitter request headers for POST",
    )
    add_parser.add_argument(
        "--draft",
        action="store_true",
        help="POST to the draft API (lmt-draftapi) instead of core. Saves as Draft for later manual Submit, not Submitted.",
    )
    add_parser.add_argument("--apply", action="store_true")

    dispatch_parser = subparsers.add_parser("add-dispatch", help="Add one dispatch labor record through the core API")
    dispatch_parser.add_argument("--date", help="Single date, YYYY-MM-DD")
    dispatch_parser.add_argument("--dates", help="Comma-separated dates, e.g. 2026-05-07,2026-05-08")
    dispatch_parser.add_argument("--hours", required=True, help="Decimal hours or HH:MM[:SS]")
    dispatch_parser.add_argument("--assignment-id", required=True, type=int)
    dispatch_parser.add_argument("--assignment-name", required=True)
    dispatch_parser.add_argument("--customer-name", required=True)
    dispatch_parser.add_argument("--product-name", required=True)
    dispatch_parser.add_argument("--notes", default="")
    dispatch_parser.add_argument("--labor-category-id", type=int, default=865418)
    dispatch_parser.add_argument("--labor-category-name", default="Delivery")
    dispatch_parser.add_argument("--partner", default="axis")
    add_reason_args(dispatch_parser, required=False)
    dispatch_parser.add_argument("--comment", default="Late submission after correction")
    dispatch_parser.add_argument(
        "--omit-action-details",
        action="store_true",
        help="Do not include actionDetails in the POST payload",
    )
    dispatch_parser.add_argument(
        "--inherit-request-headers",
        action="store_true",
        help="Prefer the freshest captured submitter request headers for POST",
    )
    dispatch_parser.add_argument(
        "--skip-dedupe",
        action="store_true",
        help="Skip the live core/draft dedupe pre-check. Useful when the single-day GET returns 404 even though POST works (e.g. when fetch-week works for the same alias).",
    )
    dispatch_parser.add_argument(
        "--draft",
        action="store_true",
        help="POST to the draft API (lmt-draftapi) instead of core. Saves as Draft for later manual Submit, not Submitted.",
    )
    dispatch_parser.add_argument("--apply", action="store_true")

    delete_parser = subparsers.add_parser("delete-core", help="Delete one live core labor record by laborId after re-fetching its week")
    add_week_args(delete_parser)
    delete_parser.add_argument("--labor-id", required=True)
    add_reason_args(delete_parser, required=True)
    delete_parser.add_argument("--comment", default="Delete incorrect labor record")
    delete_parser.add_argument("--apply", action="store_true")

    delete_draft_parser = subparsers.add_parser(
        "delete-draft",
        help="Delete one draft labor record by laborId after re-fetching its week (no Late Reason required, mirrors submit-drafts --delete-drafts behavior)",
    )
    add_week_args(delete_draft_parser)
    delete_draft_parser.add_argument("--labor-id", required=True)
    delete_draft_parser.add_argument("--apply", action="store_true")

    args = parser.parse_args()

    with CdpSession(args.cdp_port) as cdp:
        captured_core = capture_submitter_api(
            cdp,
            api_kind="core",
            alias=args.alias,
            trigger=args.trigger,
            wait_seconds=args.wait_seconds,
        )
        host = api_host(captured_core.url)
        raw_headers = captured_core.request_headers
        headers = clean_headers(raw_headers)

    if args.command == "fetch-week":
        week = fetch_week(host, headers, args.alias, args.start_date, args.end_date)
        print(format_week_output(week, args.format, args.include_raw))
        return 0

    if args.command == "submit-drafts":
        return submit_drafts(host, headers, args)

    if args.command == "add-nonproject":
        return add_nonproject(host, headers, raw_headers, args)

    if args.command == "add-dispatch":
        return add_dispatch(host, headers, raw_headers, args)

    if args.command == "delete-core":
        return delete_core(host, headers, args)

    if args.command == "delete-draft":
        return delete_draft(host, headers, args)

    raise RuntimeError(f"Unknown command: {args.command}")


def add_week_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--start-date", required=True, help="Week start date, YYYY-MM-DD")
    parser.add_argument("--end-date", help="Week end date, YYYY-MM-DD; defaults to start + 6 days")


def add_reason_args(parser: argparse.ArgumentParser, *, required: bool) -> None:
    parser.add_argument("--reason-code-id", type=int, required=required)
    parser.add_argument("--reason", default="Mistake on Initial Entry")


def capture_submitter_api(
    cdp: CdpSession,
    *,
    api_kind: str,
    alias: str,
    trigger: str,
    wait_seconds: float,
) -> CapturedApi:
    path = CORE_PATH if api_kind == "core" else DRAFT_PATH
    marker = f"{path}/submitter/{alias}"
    requests: dict[str, dict[str, Any]] = {}
    extra_headers: dict[str, dict[str, str]] = {}
    responses: dict[str, str] = {}

    if trigger == "reload":
        cdp.request("Page.reload", {"ignoreCache": True}, timeout=5)

    end_time = time.time() + wait_seconds
    while time.time() < end_time:
        msg = cdp.recv(max(0.5, end_time - time.time()))
        if not msg:
            continue
        method = msg.get("method")
        params = msg.get("params", {})
        request_id = params.get("requestId")
        if method == "Network.requestWillBeSent" and request_id:
            request = params.get("request", {})
            url = request.get("url", "")
            if marker in url:
                requests[request_id] = {"url": url, "headers": stringify_headers(request.get("headers", {}))}
        elif method == "Network.requestWillBeSentExtraInfo" and request_id:
            extra_headers[request_id] = stringify_headers(params.get("headers", {}))
        elif method == "Network.responseReceived" and request_id:
            response_url = params.get("response", {}).get("url", "")
            if marker in response_url:
                responses[request_id] = response_url
        elif method == "Network.loadingFinished" and request_id and request_id in responses:
            body_response = cdp.request("Network.getResponseBody", {"requestId": request_id}, timeout=10)
            body_result = body_response.get("result", {})
            body = body_result.get("body", "")
            if body_result.get("base64Encoded"):
                import base64

                body = base64.b64decode(body).decode("utf-8", errors="replace")
            payload = json.loads(body) if body else None
            headers = requests.get(request_id, {}).get("headers", {}) | extra_headers.get(request_id, {})
            if not any(key.lower() == "authorization" for key in headers):
                raise RuntimeError("Captured ESXP API response without Authorization header. Re-authenticate and retry.")
            return CapturedApi(url=responses[request_id], request_headers=headers, payload=payload)

    raise TimeoutError("No ESXP labor submitter API response captured. Ensure Week View is loaded and authenticated.")


def fetch_week(host: str, headers: dict[str, str], alias: str, start_date: str, end_date: str | None) -> dict[str, Any]:
    end = end_date or default_end_date(start_date)
    core_status, core_payload = request_json("GET", f"{host}{CORE_PATH}/submitter/{alias}?StartDate={start_date}&EndDate={end}", headers)
    draft_status, draft_payload = request_json("GET", f"{host}{DRAFT_PATH}/submitter/{alias}?StartDate={start_date}&EndDate={end}", headers)
    core_records = response_records(core_payload)
    draft_records = response_records(draft_payload)
    return {
        "start_date": start_date,
        "end_date": end,
        "core_status": core_status,
        "draft_status": draft_status,
        "core_records": core_records,
        "draft_records": draft_records,
        "summary": {
            "core": summarize_records(core_records),
            "draft": summarize_records(draft_records),
            "unmatched_drafts": len(unmatched_drafts(core_records, draft_records)),
        },
    }


def submit_drafts(host: str, headers: dict[str, str], args: argparse.Namespace) -> int:
    week = fetch_week(host, headers, args.alias, args.start_date, args.end_date)
    missing = unmatched_drafts(week["core_records"], week["draft_records"])
    plan = [safe_record_summary(record) for record in missing]
    if not args.apply:
        print(json.dumps({"mode": "dry-run", "planned_core_posts": plan, "delete_drafts": args.delete_drafts}, ensure_ascii=False, indent=2))
        return 0 if missing else 0

    created: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for record in missing:
        payload = build_core_payload_from_draft(record, args.alias, args.reason_code_id, args.reason, args.comment)
        status, body = request_json("POST", f"{host}{CORE_PATH}", headers, payload)
        if 200 <= status < 300:
            created.append({"source_labor_id": record.get("laborId"), "status": status, "record": safe_record_summary(record)})
            if args.delete_drafts:
                delete_status, delete_body = request_json("PATCH", f"{host}{DRAFT_PATH}/{record['laborId']}/delete?userAlias={args.alias}", headers)
                created[-1]["draft_delete"] = {"status": delete_status, "ok": 200 <= delete_status < 300, "body": summarize_body(delete_body)}
        else:
            errors.append({"source_labor_id": record.get("laborId"), "status": status, "body": summarize_body(body)})

    after = fetch_week(host, headers, args.alias, args.start_date, args.end_date)
    print(json.dumps({"mode": "apply", "created": created, "errors": errors, "after_summary": after["summary"]}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


def add_nonproject(host: str, headers: dict[str, str], raw_headers: dict[str, str], args: argparse.Namespace) -> int:
    target_headers = clean_headers(raw_headers) if args.inherit_request_headers else headers
    include_action_details = not args.omit_action_details
    if include_action_details and not args.reason_code_id:
        raise RuntimeError("--reason-code-id is required unless --omit-action-details is set")

    dates = resolve_target_dates(args.date, args.dates)
    payloads = [
        build_nonproject_payload(
            date=date,
            hours=args.hours,
            category_id=args.category_id,
            category_name=args.category_name,
            alias=args.alias,
            notes=args.notes,
            include_action_details=include_action_details,
            reason_code_id=args.reason_code_id,
            comment=args.comment,
        )
        for date in dates
    ]

    if not args.apply:
        print(
            json.dumps(
                {
                    "mode": "dry-run",
                    "target": "draft" if getattr(args, "draft", False) else "core",
                    "dates": dates,
                    "header_keys": sorted(target_headers.keys()),
                    "planned_posts": [safe_payload(payload) for payload in payloads],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    post_path = DRAFT_PATH if getattr(args, "draft", False) else CORE_PATH
    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for date, payload in zip(dates, payloads):
        body_to_post = [payload] if getattr(args, "draft", False) else payload
        status, body = request_json("POST", f"{host}{post_path}", target_headers, body_to_post)
        row = {"date": date, "status": status, "ok": 200 <= status < 300, "body": summarize_body(body)}
        results.append(row)
        if not row["ok"]:
            errors.append(row)

    print(
        json.dumps(
            {
                "mode": "apply",
                "dates": dates,
                "header_keys": sorted(target_headers.keys()),
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if errors else 0


def add_dispatch(host: str, headers: dict[str, str], raw_headers: dict[str, str], args: argparse.Namespace) -> int:
    target_headers = clean_headers(raw_headers) if args.inherit_request_headers else headers
    include_action_details = not args.omit_action_details
    if include_action_details and not args.reason_code_id:
        raise RuntimeError("--reason-code-id is required unless --omit-action-details is set")

    dates = resolve_target_dates(args.date, args.dates)
    start_date, end_date = min(dates), max(dates)
    payloads = [
        build_dispatch_payload(
            date=date,
            hours=args.hours,
            assignment_id=args.assignment_id,
            assignment_name=args.assignment_name,
            customer_name=args.customer_name,
            product_name=args.product_name,
            alias=args.alias,
            notes=args.notes,
            labor_category_id=args.labor_category_id,
            labor_category_name=args.labor_category_name,
            partner=args.partner,
            include_action_details=include_action_details,
            reason_code_id=args.reason_code_id,
            comment=args.comment,
        )
        for date in dates
    ]
    before = fetch_week(host, target_headers, args.alias, start_date, end_date)
    plans = dispatch_post_plans(payloads, before)

    if not args.apply:
        print(
            json.dumps(
                {
                    "mode": "dry-run",
                    "target": "draft" if getattr(args, "draft", False) else "core",
                    "dates": dates,
                    "dedupe_status": {"core": before["core_status"], "draft": before["draft_status"]},
                    "before_summary": before["summary"],
                    "header_keys": sorted(target_headers.keys()),
                    "planned_posts": [plan for plan in plans if plan["action"] == "post"],
                    "skipped_existing": [plan for plan in plans if plan["action"] == "skip-existing"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if not (200 <= before["core_status"] < 300):
        if not args.skip_dedupe:
            print(
                json.dumps(
                    {
                        "mode": "apply",
                        "error": "core live dedupe fetch failed; refusing to mutate. Pass --skip-dedupe to bypass if you have verified the day is empty via fetch-week.",
                        "dedupe_status": {"core": before["core_status"], "draft": before["draft_status"]},
                        "before_summary": before["summary"],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 2
        # Operator explicitly accepted dedupe bypass.
        skipped = [plan for plan in plans if plan["action"] == "skip-existing"]

    post_path = DRAFT_PATH if getattr(args, "draft", False) else CORE_PATH
    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    skipped = [plan for plan in plans if plan["action"] == "skip-existing"]
    for plan in [item for item in plans if item["action"] == "post"]:
        date = plan["date"]
        payload = plan["payload"]
        body_to_post = [payload] if getattr(args, "draft", False) else payload
        status, body = request_json("POST", f"{host}{post_path}", target_headers, body_to_post)
        row = {"date": date, "status": status, "ok": 200 <= status < 300, "body": summarize_body(body)}
        results.append(row)
        if not row["ok"]:
            errors.append(row)

    after = fetch_week(host, target_headers, args.alias, start_date, end_date)

    print(
        json.dumps(
            {
                "mode": "apply",
                "dates": dates,
                "dedupe_status": {"core": before["core_status"], "draft": before["draft_status"]},
                "header_keys": sorted(target_headers.keys()),
                "skipped_existing": skipped,
                "results": results,
                "after_status": {"core": after["core_status"], "draft": after["draft_status"]},
                "after_summary": after["summary"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if errors else 0


def dispatch_post_plans(payloads: list[dict[str, Any]], week: dict[str, Any]) -> list[dict[str, Any]]:
    existing: dict[tuple[str, str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in [*week["core_records"], *week["draft_records"]]:
        if record.get("laborStatus") == "Deleted":
            continue
        existing[record_key(record)].append(safe_record_summary(record))

    plans: list[dict[str, Any]] = []
    for payload in payloads:
        matches = existing.get(record_key(payload), [])
        plans.append(
            {
                "date": str(payload.get("laborDate", ""))[:10],
                "action": "skip-existing" if matches else "post",
                "payload": safe_payload(payload),
                "existing_matches": matches,
            }
        )
    return plans


def delete_core(host: str, headers: dict[str, str], args: argparse.Namespace) -> int:
    week = fetch_week(host, headers, args.alias, args.start_date, args.end_date)
    matches = [record for record in week["core_records"] if str(record.get("laborId")) == args.labor_id]
    if len(matches) != 1:
        print(json.dumps({"error": "expected exactly one matching core record", "match_count": len(matches)}, ensure_ascii=False, indent=2))
        return 2
    payload = copy.deepcopy(matches[0])
    payload["updatedDateInUtc"] = payload.get("updatedDateInUtc") or payload.get("updatedDateTimeInUtc") or utc_now()
    payload["actionDetails"] = {
        "actionType": "Adjustment",
        "reasonCodeId": args.reason_code_id,
        "reasonCodeName": args.reason,
        "comments": args.comment,
    }
    if not args.apply:
        print(json.dumps({"mode": "dry-run", "target": safe_record_summary(matches[0])}, ensure_ascii=False, indent=2))
        return 0
    status, body = request_json("PATCH", f"{host}{CORE_PATH}/{args.labor_id}/delete?userAlias={args.alias}", headers, payload)
    after = fetch_week(host, headers, args.alias, args.start_date, args.end_date)
    print(json.dumps({"mode": "apply", "status": status, "ok": 200 <= status < 300, "body": summarize_body(body), "after_summary": after["summary"]}, ensure_ascii=False, indent=2))
    return 0 if 200 <= status < 300 else 1


def delete_draft(host: str, headers: dict[str, str], args: argparse.Namespace) -> int:
    """Delete one draft labor record by laborId.

    Uses the same DELETE endpoint that ``submit-drafts --delete-drafts`` uses
    after a successful core POST: ``PATCH {DRAFT_PATH}/{laborId}/delete?userAlias=<alias>``.
    No payload body and no Late Reason are required because draft records were never
    submitted to the core API.

    Workflow:
      1. Re-fetch the target week to confirm the draft still exists.
      2. Require exactly one match for ``--labor-id``.
      3. Print a dry-run summary unless ``--apply`` is supplied.
      4. PATCH the delete endpoint and re-fetch the week to show the after-summary.
    """
    week = fetch_week(host, headers, args.alias, args.start_date, args.end_date)
    matches = [record for record in week["draft_records"] if str(record.get("laborId")) == args.labor_id]
    if len(matches) != 1:
        print(
            json.dumps(
                {
                    "error": "expected exactly one matching draft record",
                    "labor_id": args.labor_id,
                    "match_count": len(matches),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2
    target = safe_record_summary(matches[0])
    if not args.apply:
        print(json.dumps({"mode": "dry-run", "target": target}, ensure_ascii=False, indent=2))
        return 0
    status, body = request_json(
        "PATCH",
        f"{host}{DRAFT_PATH}/{args.labor_id}/delete?userAlias={args.alias}",
        headers,
    )
    after = fetch_week(host, headers, args.alias, args.start_date, args.end_date)
    print(
        json.dumps(
            {
                "mode": "apply",
                "status": status,
                "ok": 200 <= status < 300,
                "target": target,
                "body": summarize_body(body),
                "after_summary": after["summary"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if 200 <= status < 300 else 1


def request_json(method: str, url: str, headers: dict[str, str], body: Any = None) -> tuple[int, Any]:
    request_headers = clean_headers(headers)
    if body is not None:
        request_headers["Content-Type"] = "application/json"
    request_body = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=request_body, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                parsed = raw
            return response.status, parsed
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw
        return error.code, parsed


def response_records(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []

    def is_labor_record(candidate: Any) -> bool:
        return isinstance(candidate, dict) and any(
            key in candidate for key in ("laborId", "laborDate", "laborHours", "laborCategoryId", "laborCategoryName")
        )

    candidates = [
        payload.get("response"),
        payload.get("data", {}).get("response") if isinstance(payload.get("data"), dict) else None,
    ]
    for candidate in candidates:
        if isinstance(candidate, list):
            return [item for item in candidate if is_labor_record(item)]
        if is_labor_record(candidate):
            return [candidate]
    return []


def unmatched_drafts(core_records: list[dict[str, Any]], draft_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    existing = {record_key(record) for record in core_records if record.get("laborStatus") != "Deleted"}
    return [record for record in draft_records if record_key(record) not in existing]


def record_key(record: dict[str, Any]) -> tuple[str, str, str, str, str]:
    assignment = record.get("assignmentDetails") or {}
    return (
        str(record.get("laborDate", ""))[:10],
        str(assignment.get("assignmentId") or ""),
        str(record.get("laborCategoryId") or ""),
        normalize_hours(record.get("laborHours") or ""),
        str(record.get("partner") or ""),
    )


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_day: dict[str, float] = defaultdict(float)
    by_status: dict[str, float] = defaultdict(float)
    by_category: dict[str, float] = defaultdict(float)
    for record in records:
        if record.get("laborStatus") == "Deleted":
            continue
        hours = hours_to_float(record.get("laborHours"))
        by_day[str(record.get("laborDate", ""))[:10]] += hours
        by_status[str(record.get("laborStatus") or "Unknown")] += hours
        category = str(record.get("laborCategoryName") or record.get("partner") or "Unknown")
        by_category[category] += hours
    return {
        "count": len(records),
        "total_hours": round(sum(by_day.values()), 2),
        "by_day": rounded_dict(by_day),
        "by_status": rounded_dict(by_status),
        "by_category": rounded_dict(by_category),
    }


def build_core_payload_from_draft(record: dict[str, Any], alias: str, reason_code_id: int, reason: str, comment: str) -> dict[str, Any]:
    payload = copy.deepcopy(record)
    for field in ["laborId", "eTag", "submittedDateInUtc", "updatedDateTimeInUtc", "laborStatus", "userActionId", "workflowStatus"]:
        payload.pop(field, None)
    payload["submittedFor"] = alias
    payload["submittedBy"] = alias
    payload["updatedDateInUtc"] = utc_now()
    payload["actionDetails"] = [{"actionType": "LateSubmission", "reasonId": reason_code_id, "comments": comment}]
    return payload


def build_nonproject_payload(
    *,
    date: str,
    hours: str,
    category_id: int,
    category_name: str,
    alias: str,
    notes: str,
    include_action_details: bool,
    reason_code_id: int | None,
    comment: str,
) -> dict[str, Any]:
    payload = {
        "laborDate": f"{normalize_date(date)}T00:00:00",
        "laborHours": normalize_hours(hours),
        "laborTimeZoneId": 87,
        "laborCategoryId": category_id,
        "laborCategoryName": category_name,
        "submittedFor": alias,
        "submittedBy": alias,
        "laborNotes": notes,
        "partner": "nonproject",
        "updatedDateInUtc": utc_now(),
    }
    if include_action_details and reason_code_id is not None:
        payload["actionDetails"] = [{"actionType": "LateSubmission", "reasonId": reason_code_id, "comments": comment}]
    return payload


def build_dispatch_payload(
    *,
    date: str,
    hours: str,
    assignment_id: int,
    assignment_name: str,
    customer_name: str,
    product_name: str,
    alias: str,
    notes: str,
    labor_category_id: int,
    labor_category_name: str,
    partner: str,
    include_action_details: bool,
    reason_code_id: int | None,
    comment: str,
) -> dict[str, Any]:
    payload = {
        "laborDate": f"{normalize_date(date)}T00:00:00",
        "laborHours": normalize_hours(hours),
        "laborTimeZoneId": 87,
        "laborCategoryId": labor_category_id,
        "laborCategoryName": labor_category_name,
        "submittedFor": alias,
        "submittedBy": alias,
        "laborNotes": notes,
        "partner": partner,
        "updatedDateInUtc": utc_now(),
        "assignmentDetails": {
            "assignmentId": assignment_id,
            "assignmentName": assignment_name,
            "customerName": customer_name,
            "productName": product_name,
        },
    }
    if include_action_details and reason_code_id is not None:
        payload["actionDetails"] = [{"actionType": "LateSubmission", "reasonId": reason_code_id, "comments": comment}]
    return payload


def resolve_target_dates(single_date: str | None, date_list: str | None) -> list[str]:
    if bool(single_date) == bool(date_list):
        raise ValueError("Specify exactly one of --date or --dates")
    if single_date:
        return [normalize_date(single_date)]
    assert date_list is not None
    dates = [normalize_date(item) for item in date_list.split(",") if item.strip()]
    if not dates:
        raise ValueError("--dates must contain at least one date")
    return dates


def format_week_output(week: dict[str, Any], output_format: str, include_raw: bool) -> str:
    if output_format == "json":
        payload = copy.deepcopy(week)
        if not include_raw:
            payload.pop("core_records", None)
            payload.pop("draft_records", None)
        return json.dumps(payload, ensure_ascii=False, indent=2)

    summary = week["summary"]
    if output_format == "markdown":
        lines = [
            f"# ESXP Labor API Summary ({week['start_date']} to {week['end_date']})",
            "",
            "| Source | Records | Total Hours | Unmatched Drafts |",
            "|---|---:|---:|---:|",
            f"| Core | {summary['core']['count']} | {summary['core']['total_hours']:g} | - |",
            f"| Draft | {summary['draft']['count']} | {summary['draft']['total_hours']:g} | {summary['unmatched_drafts']} |",
            "",
            "## Core By Day",
            "",
        ]
        lines.extend(f"- {day}: {hours:g}h" for day, hours in summary["core"]["by_day"].items())
        lines.extend(["", "## Draft By Day", ""])
        lines.extend(f"- {day}: {hours:g}h" for day, hours in summary["draft"]["by_day"].items())
        return "\n".join(lines)

    return "\n".join(
        [
            f"ESXP Labor API Summary ({week['start_date']} to {week['end_date']})",
            f"Core : {summary['core']['count']} records, {summary['core']['total_hours']:g}h",
            f"Draft: {summary['draft']['count']} records, {summary['draft']['total_hours']:g}h",
            f"Unmatched drafts: {summary['unmatched_drafts']}",
            "Core by day:",
            *[f"- {day}: {hours:g}h" for day, hours in summary["core"]["by_day"].items()],
            "Draft by day:",
            *[f"- {day}: {hours:g}h" for day, hours in summary["draft"]["by_day"].items()],
        ]
    )


def safe_record_summary(record: dict[str, Any]) -> dict[str, Any]:
    assignment = record.get("assignmentDetails") or {}
    return {
        "laborId": record.get("laborId"),
        "date": str(record.get("laborDate", ""))[:10],
        "hours": normalize_hours(record.get("laborHours") or ""),
        "status": record.get("laborStatus"),
        "partner": record.get("partner"),
        "laborCategoryId": record.get("laborCategoryId"),
        "laborCategoryName": record.get("laborCategoryName"),
        "assignmentId": assignment.get("assignmentId"),
        "demandSourceId": assignment.get("demandSourceId"),
    }


def safe_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key.lower() not in {"authorization", "cookie"}}


def summarize_body(body: Any) -> Any:
    if isinstance(body, dict):
        if "data" in body:
            return {"has_data": True, "keys": sorted(body.keys())}
        return body
    if isinstance(body, str) and len(body) > 1000:
        return body[:1000]
    return body


def clean_headers(headers: dict[str, str]) -> dict[str, str]:
    return {
        key: value
        for key, value in headers.items()
        if not key.startswith(":") and key.lower() not in {"host", "content-length"}
    }


def stringify_headers(headers: dict[str, Any]) -> dict[str, str]:
    return {str(key): str(value) for key, value in headers.items()}


def api_host(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return DEFAULT_HOST


def normalize_date(value: str) -> str:
    text = value.strip()
    if "T" in text:
        text = text.split("T", 1)[0]
    for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%d %b %Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def default_end_date(start_date: str) -> str:
    start = datetime.strptime(normalize_date(start_date), "%Y-%m-%d")
    return (start + timedelta(days=6)).strftime("%Y-%m-%d")


def normalize_hours(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    if re.fullmatch(r"\d+(?:\.\d+)?", text):
        hours = float(text)
        whole = int(hours)
        minutes = int(round((hours - whole) * 60))
        return f"{whole:02d}:{minutes:02d}:00"
    day_match = re.fullmatch(r"(\d+)\.(\d{1,2}):(\d{2}):(\d{2})", text)
    if day_match:
        days, hours, minutes, seconds = day_match.groups()
        return f"{int(days) * 24 + int(hours):02d}:{minutes}:{seconds}"
    match = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?", text)
    if match:
        hour, minute, second = match.groups()
        return f"{int(hour):02d}:{minute}:{second or '00'}"
    match = re.match(r"^(\d+(?:\.\d+)?)\s*h", text, re.I)
    if match:
        return normalize_hours(match.group(1))
    return text


def hours_to_float(value: Any) -> float:
    normalized = normalize_hours(value)
    if not normalized:
        return 0.0
    parts = normalized.split(":")
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) + int(minutes) / 60 + int(seconds) / 3600
    if len(parts) == 2:
        hours, minutes = parts
        return int(hours) + int(minutes) / 60
    if re.fullmatch(r"\d+(?:\.\d+)?", normalized):
        return float(normalized)
    raise ValueError(f"Unsupported laborHours format: {value!r} -> {normalized!r}")


def rounded_dict(values: dict[str, float]) -> dict[str, float]:
    return dict(sorted((key, round(value, 2)) for key, value in values.items() if key))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
