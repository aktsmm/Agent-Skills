"""ESXP (Enterprise Services Experience) CDP client library.

既存 Edge の CDP 接続経由で ESXP Labor Entry 画面を操作する共通ライブラリ。

前提:
    - Edge が `--remote-debugging-port=9222 --remote-allow-origins=*` で起動済み
    - ESXP (https://esxp.microsoft.com/#/time/weekview) にログイン済みのタブがある

MCPと排他制御が必要: 実行前に Playwright MCP の browser_close を実行すること。

使い方:
    from esxp_client import EsxpClient
    with EsxpClient() as c:
        dispatches = c.list_dispatches("Reports Pending")
        for d in dispatches:
            print(d)
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
import json
import os
import time
import urllib.request
from dataclasses import dataclass
from typing import Any, Iterable

import websocket

CDP_PORT = int(os.environ.get("ESXP_CDP_PORT", "9222"))
ESXP_URL_FRAGMENT = "esxp.microsoft.com"


@dataclass
class Dispatch:
    """1 件の Dispatch / Assignment 情報."""

    customer: str
    assignment_id: str
    rmot_id: str
    solution: str
    start: str
    end: str
    tab: str

    def to_dict(self) -> dict[str, str]:
        return {
            "customer": self.customer,
            "assignment_id": self.assignment_id,
            "rmot_id": self.rmot_id,
            "solution": self.solution,
            "start": self.start,
            "end": self.end,
            "tab": self.tab,
        }


class EsxpClient:
    """ESXP の Labor Entry Week View を CDP で操作."""

    def __init__(self, cdp_port: int = CDP_PORT, timeout: int = 30) -> None:
        self.cdp_port = cdp_port
        self.timeout = timeout
        self.ws: websocket.WebSocket | None = None
        self._msg_id = 0

    def __enter__(self) -> "EsxpClient":
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # --- CDP low-level ---

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

    def connect(self) -> None:
        tabs_url = f"http://127.0.0.1:{self.cdp_port}/json"
        tabs = self._urlopen_retry(tabs_url)
        esxp_tabs = [t for t in tabs if t.get("type") == "page" and ESXP_URL_FRAGMENT in t.get("url", "")]
        if not esxp_tabs:
            raise RuntimeError(f"ESXP tab not found. Open {ESXP_URL_FRAGMENT} first.")
        # Prefer Week View URL over Home
        target = next((t for t in esxp_tabs if "weekview" in t.get("url", "")), esxp_tabs[0])
        # Force IPv4 loopback to avoid ephemeral port exhaustion from localhost dual-stack resolution
        ws_url = target["webSocketDebuggerUrl"].replace("ws://localhost:", "ws://127.0.0.1:")
        self.ws = self._ws_connect_retry(ws_url)
        self._cmd("Page.enable")
        self._cmd("Runtime.enable")
        # Ensure we are on Week View (redirect if needed)
        if "weekview" not in target.get("url", ""):
            self._cmd(
                "Page.navigate",
                {"url": f"https://{ESXP_URL_FRAGMENT}/#/time/weekview"},
            )
            time.sleep(3)
        self.ensure_esxp_ready()

    def ensure_esxp_ready(self) -> None:
        """Fail fast when CDP is attached to a wrong or unauthenticated profile."""
        state = self.eval_js(
            r"""
            (() => {
                const text = document.body ? (document.body.innerText || '') : '';
                return {
                    href: location.href,
                    title: document.title,
                    text: text.slice(0, 4000),
                };
            })()
            """
        ) or {}
        href = str(state.get("href") or "")
        title = str(state.get("title") or "")
        text = str(state.get("text") or "")
        if ESXP_URL_FRAGMENT not in href:
            raise RuntimeError(f"Connected page is not ESXP: {href}")
        if href.rstrip("/").endswith("/#") or href.rstrip("/").endswith("/#/") or title.lower() == "home":
            raise RuntimeError(
                "ESXP page resolved to Home. This usually means the CDP browser is using the wrong profile or account. "
                "Run verify_esxp_profile.py and reconnect with the correct Edge profile."
            )
        if "sign in" in text.lower() or "login.microsoftonline.com" in href.lower():
            raise RuntimeError(
                "ESXP page is not authenticated. Open ESXP with the intended work profile and sign in before running automation."
            )

    def close(self) -> None:
        if self.ws:
            self.ws.close()
            self.ws = None

    def _next_id(self) -> int:
        self._msg_id += 1
        return self._msg_id

    def _cmd(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any] | None:
        if not self.ws:
            raise RuntimeError("Not connected")
        msg_id = self._next_id()
        self.ws.send(
            json.dumps({"id": msg_id, "method": method, "params": params or {}})
        )
        timeout = timeout or self.timeout
        end = time.time() + timeout
        while time.time() < end:
            self.ws.settimeout(max(1, end - time.time()))
            try:
                msg = json.loads(self.ws.recv())
            except websocket.WebSocketTimeoutException:
                continue
            if msg.get("id") == msg_id:
                return msg
        return None

    def eval_js(self, expression: str, timeout: float | None = None) -> Any:
        """ページコンテキストで JavaScript を実行して値を返す."""
        resp = self._cmd(
            "Runtime.evaluate",
            {"expression": expression, "returnByValue": True, "awaitPromise": True},
            timeout=timeout,
        )
        if not resp or "result" not in resp:
            return None
        inner = resp["result"].get("result", {})
        if inner.get("type") == "undefined":
            return None
        return inner.get("value")

    # --- ESXP-specific ---

    # 対応タブ名 -> 内部ラベル (ESXP UI の表示と一致)
    TABS = ("Quick Select", "Current", "Upcoming", "Reports Pending")

    def force_close_all_overlays(self) -> int:
        """開いている全 overlay pane を力ずくで閉じる.

        Dispatch 選択モーダルが重複していたり、Dispatch Details が残存している場合に使用。
        Returns: 閉じた pane の数。
        """
        # まずは正規ボタンで閉じる試み
        for _ in range(8):
            result = self.eval_js(
                r"""
                (() => {
                    const closeSelectors = [
                        'span.close-button',
                        '[aria-label*="dialogue close" i]',
                        '[aria-label*="dialog close" i]',
                    ];
                    for (const sel of closeSelectors) {
                        const el = [...document.querySelectorAll(sel)].find(b => b.offsetParent);
                        if (el) { el.click(); return 'close-btn'; }
                    }
                    const cancelBtn = [...document.querySelectorAll('button')].find(b =>
                        b.offsetParent && /^(Cancel|Close)$/.test((b.innerText || '').trim())
                    );
                    if (cancelBtn) { cancelBtn.click(); return 'cancel'; }
                    return 'no-btn';
                })()
                """
            )
            if result == "no-btn":
                break
            time.sleep(0.3)

        # それでも残った overlay は DOM から強制削除（Angular CDK は再オープン時に新規生成する）
        removed = self.eval_js(
            r"""
            (() => {
                const overlays = [...document.querySelectorAll('.cdk-overlay-pane, mat-dialog-container, .cdk-overlay-backdrop, .cdk-overlay-container > div')]
                    .filter(d => d.offsetParent);
                let count = 0;
                for (const o of overlays) {
                    o.remove();
                    count++;
                }
                return count;
            })()
            """
        )
        time.sleep(0.4)
        return int(removed or 0)

    def open_dispatches_tile(self) -> None:
        """DISPATCHES タイルをクリックして Dispatch 選択モーダルを開く.

        実行前に既存の overlay を全部閉じる（モーダル重複防止）。
        """
        # 1. force-close ALL existing overlays (avoid stacked modals from prior runs)
        self.force_close_all_overlays()
        time.sleep(0.3)
        # 2. open dispatches tile
        opened = self.eval_js(
            """
            (() => {
                const btn = document.querySelector(
                    'button[aria-label="Click here to enter time for Dispatches"]'
                );
                if (btn) { btn.click(); return 'opened'; }
                return 'not-found';
            })()
            """
        )
        if opened == "not-found":
            raise RuntimeError(
                "DISPATCHES tile button not found. Ensure Week View is loaded."
            )
        time.sleep(2.5)

    def switch_tab(self, tab_name: str) -> bool:
        """Dispatch 選択モーダル内のタブを切り替える.

        モーダルが閉じていた場合は自動的に再オープンする。
        タブ要素が未描画の場合は最大 3 回リトライする。
        """
        if tab_name not in self.TABS:
            raise ValueError(f"Unknown tab: {tab_name}. Use one of {self.TABS}")
        for attempt in range(3):
            # モーダルが開いているか確認、閉じていたら再オープン
            modal_open = self.eval_js(
                """
                (() => [...document.querySelectorAll('.cdk-overlay-pane, mat-dialog-container')]
                    .some(d => d.offsetParent && /Select a Dispatch/i.test(d.innerText || '')))()
                """
            )
            if not modal_open:
                self.open_dispatches_tile()
                time.sleep(1.0)
            # Scope tab search to the Select a Dispatch modal tab header.
            # A global text search can hit unrelated "Current" / "Reports Pending" labels.
            script = f"""
            (() => {{
                const dlgs = [...document.querySelectorAll('.cdk-overlay-pane, mat-dialog-container')]
                    .filter(d => d.offsetParent && /Select a Dispatch/i.test(d.innerText || ''));
                const modal = dlgs[dlgs.length - 1];
                if (!modal) return false;
                const pattern = /^{tab_name}\\s*\\(\\d+\\)/;
                const roots = [modal.querySelector('.selector-buttons'), modal.querySelector('[role="tablist"]'), modal]
                    .filter(Boolean);
                for (const root of roots) {{
                    const cands = [...root.querySelectorAll('button, a, [role="tab"], [role="button"], span, div')].filter(el => {{
                        const text = (el.innerText || el.textContent || '').trim();
                        return el.offsetParent && pattern.test(text) && (!el.children.length || String(el.className || '').includes('view-selector'));
                    }});
                    if (cands[0]) {{ cands[0].click(); return true; }}
                }}
                return false;
            }})()
            """
            result = self.eval_js(script)
            if result:
                time.sleep(2)
                return True
            # 見つからなかった場合は少し待って再試行
            time.sleep(1.5)
        return False

    def extract_dispatches(self, tab_label: str = "") -> list[Dispatch]:
        """現在表示中のタブから Dispatch 情報を抽出.

        virtual scroll 対応: スクロール可能コンテナを段階的にスクロールし、
        各段階で描画された行情報を蓄積する（スクロールで DOM から消える前に収集）。
        """
        raw = self.eval_js(
            r"""
            (async () => {
                const dlgs = [...document.querySelectorAll('.cdk-overlay-pane, mat-dialog-container')]
                    .filter(d => d.offsetParent && /Select a Dispatch/i.test(d.innerText || ''));
                const scope = dlgs[dlgs.length - 1];
                if (!scope) return [];
                const visibleBodies = [...scope.querySelectorAll('.mat-tab-body, [role="tabpanel"], .mat-mdc-tab-body')]
                    .filter(el => el.offsetParent && getComputedStyle(el).visibility !== 'hidden');
                const activeBody = visibleBodies.find(el =>
                    el.classList.contains('mat-tab-body-active')
                    || el.classList.contains('mat-mdc-tab-body-active')
                    || el.getAttribute('aria-hidden') === 'false'
                ) || visibleBodies[0] || scope;
                const collected = new Map(); // aid -> full text
                const collect = () => {
                    const items = [...activeBody.querySelectorAll('*')].filter(
                        el => /Assignment ID:/i.test(el.innerText || '')
                              && el.querySelectorAll('*').length < 20
                    );
                    for (const el of items) {
                        const text = el.innerText.replace(/\n+/g, ' | ');
                        if (!/Start:/.test(text)) continue;
                        const aidMatch = text.match(/Assignment ID:\s*(\d+)/);
                        if (!aidMatch) continue;
                        const aid = aidMatch[1];
                        // 既に収集済みなら、より長い（詳細な）テキストがあれば更新
                        const existing = collected.get(aid);
                        if (!existing || text.length > existing.length) {
                            collected.set(aid, text);
                        }
                    }
                };
                // 初回収集
                collect();
                // スクロール可能コンテナを段階的にスクロールして全項目描画 + 収集
                const scrollables = [...activeBody.querySelectorAll('*')].filter(el => {
                    const cs = getComputedStyle(el);
                    return (cs.overflowY === 'auto' || cs.overflowY === 'scroll')
                        && el.scrollHeight > el.clientHeight + 5;
                });
                for (const s of scrollables) {
                    const steps = 15;
                    for (let i = 0; i <= steps; i++) {
                        s.scrollTop = (s.scrollHeight * i) / steps;
                        await new Promise(r => setTimeout(r, 180));
                        collect();
                    }
                    s.scrollTop = 0;
                    await new Promise(r => setTimeout(r, 200));
                    collect();
                }
                return [...collected.values()];
            })()
            """
        )
        time.sleep(0.3)
        if not raw:
            return []
        results: list[Dispatch] = []
        for line in raw:
            parsed = _parse_dispatch_line(line, tab_label)
            if parsed:
                results.append(parsed)
        return results

    def list_dispatches(self, tab_name: str) -> list[Dispatch]:
        """指定タブの Dispatch を一覧取得."""
        self.open_dispatches_tile()
        if not self.switch_tab(tab_name):
            raise RuntimeError(f"Failed to switch to tab: {tab_name}")
        return self.extract_dispatches(tab_label=tab_name)

    def list_all_dispatches(
        self, tabs: Iterable[str] | None = None
    ) -> list[Dispatch]:
        """複数タブの Dispatch を一括取得."""
        tabs = tabs or self.TABS
        self.open_dispatches_tile()
        all_items: list[Dispatch] = []
        for t in tabs:
            if not self.switch_tab(t):
                continue
            all_items.extend(self.extract_dispatches(tab_label=t))
        return all_items

    # --- Week View ナビゲーション + Hours 取得 ---

    def close_modal(self) -> None:
        """残存モーダルを Cancel で閉じる（複数回試行）."""
        for _ in range(3):
            closed = self.eval_js(
                """
                (() => {
                    const btn = [...document.querySelectorAll('button')].find(b =>
                        b.offsetParent && (b.innerText?.trim() === 'Cancel' || b.innerText?.trim() === 'Close')
                    );
                    if (btn) { btn.click(); return true; }
                    return false;
                })()
                """
            )
            if not closed:
                break
            time.sleep(0.5)

    def get_current_week_label(self) -> str:
        """Week View に現在表示中の週ラベル（例: '12 SUNDAY ... 18 SATURDAY'）."""
        return (
            self.eval_js(
                """
                (() => {
                    const dates = [...document.querySelectorAll('button, [role="button"]')]
                        .filter(el => /^\\d{1,2}\\s+[A-Z]/i.test((el.innerText || '').replace(/\\n/g, ' ').trim()));
                    if (!dates.length) return '';
                    return dates.map(d => d.innerText.replace(/\\n/g, ' ')).join(' / ');
                })()
                """
            )
            or ""
        )

    def navigate_week(self, direction: str = "prev") -> bool:
        """Week View で前週/次週に移動.

        Args:
            direction: 'prev' or 'next'
        """
        assert direction in ("prev", "next")
        self.close_modal()
        label = "previous" if direction == "prev" else "next"
        clicked = self.eval_js(
            f"""
            (() => {{
                const btn = [...document.querySelectorAll('button, [role=button], i')]
                    .find(b => {{
                        const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                        const cls = (b.className?.toString() || '').toLowerCase();
                        return b.offsetParent && (
                            aria.includes('{label}') ||
                            cls.includes('carousel-{direction}') ||
                            cls.includes('{direction}-week') ||
                            cls.includes('icon-chevron{("left" if direction == "prev" else "right")}')
                        );
                    }});
                if (btn) {{ btn.click(); return true; }}
                return false;
            }})()
            """
        )
        if clicked:
            time.sleep(2.5)
        return bool(clicked)

    def get_visible_week_days(self) -> list[dict[str, str | bool]]:
        """現在表示中の週の日付ボタンを実日付つきで返す.

        Returns:
            [{full_date: 'YYYY-MM-DD', day_of_month: '23', weekday: 'FRIDAY', selected: True}, ...]
        """
        data = self.eval_js(
            r"""
            (() => {
                const clean = (s) => (s || '').replace(/\u200b/g, '').trim();
                const bodyText = document.body ? (document.body.innerText || '') : '';
                const headerDateMatch = bodyText.match(/(\d{1,2}-[A-Za-z]{3}-\d{4})/);
            const buttons = [...document.querySelectorAll('button, [role="button"]')]
                .filter(el => /^\d{1,2}\s+[A-Z]+/i.test((el.innerText || '').replace(/\n+/g, ' ').trim()))
                .map((el, idx) => {
                    const compact = clean(el.innerText).replace(/\n+/g, ' ');
                    const m = compact.match(/^(\d{1,2})\s+([A-Z]+)/i);
                    return {
                        index: idx,
                        day_of_month: m ? m[1] : '',
                        weekday: m ? m[2].toUpperCase() : '',
                        selected: el.classList.contains('selected') || /selected/.test(el.className || ''),
                    };
                });
                return {
                    header_date: headerDateMatch ? headerDateMatch[1] : '',
                    buttons,
                };
            })()
            """
        ) or {}
        header_date_raw = str(data.get("header_date") or "")
        buttons = list(data.get("buttons") or [])
        if not header_date_raw or not buttons:
            return []
        try:
            selected_date = datetime.strptime(header_date_raw, "%d-%b-%Y").date()
        except ValueError:
            return []
        selected_index = next((idx for idx, item in enumerate(buttons) if item.get("selected")), None)
        if selected_index is None:
            weekday_name = selected_date.strftime("%A").upper()
            selected_index = next(
                (idx for idx, item in enumerate(buttons)
                 if item.get("weekday") == weekday_name
                 and str(item.get("day_of_month")).zfill(2) == str(selected_date.day).zfill(2)),
                None,
            )
        if selected_index is None:
            return []
        result: list[dict[str, str | bool]] = []
        for idx, item in enumerate(buttons):
            actual = selected_date + timedelta(days=idx - selected_index)
            result.append(
                {
                    "full_date": actual.isoformat(),
                    "day_of_month": str(item.get("day_of_month") or ""),
                    "weekday": str(item.get("weekday") or ""),
                    "selected": bool(item.get("selected")),
                }
            )
        return result

    def select_date(self, target_date: str, max_hops: int = 12) -> bool:
        """指定日付を含む週まで移動し、その日を選択する.

        Args:
            target_date: YYYY-MM-DD
            max_hops: prev/next week 移動の最大回数
        """
        wanted = date.fromisoformat(target_date)
        self.close_modal()
        for _ in range(max_hops + 1):
            visible = self.get_visible_week_days()
            if not visible:
                return False
            by_date = {str(item.get("full_date")): item for item in visible}
            if target_date in by_date:
                meta = by_date[target_date]
                clicked = self.eval_js(
                    rf"""
                    (() => {{
                        const wantedDay = {json.dumps(meta['day_of_month'])};
                        const wantedWeekday = {json.dumps(meta['weekday'])};
                        const btn = [...document.querySelectorAll('button, [role="button"]')].find(el => {{
                            const compact = (el.innerText || '').replace(/\n+/g, ' ').trim().toUpperCase();
                            return /^\d{{1,2}}\s+[A-Z]/.test(compact) && compact.startsWith(wantedDay + ' ' + wantedWeekday);
                        }});
                        if (btn) {{ btn.click(); return true; }}
                        return false;
                    }})()
                    """
                )
                if clicked:
                    time.sleep(0.8)
                return bool(clicked)
            dates = [date.fromisoformat(str(item.get("full_date"))) for item in visible if item.get("full_date")]
            if not dates:
                return False
            if wanted < min(dates):
                if not self.navigate_week("prev"):
                    return False
            elif wanted > max(dates):
                if not self.navigate_week("next"):
                    return False
            else:
                return False
        return False

    def list_week_dispatches(self) -> list[dict[str, str]]:
        """Week View の DISPATCHES タイルに表示中の Dispatch 行を抽出.

        Returns:
            [{assignment_id, customer, rmot, week_hours}, ...]
        """
        return (
            self.eval_js(
                r"""
                (() => {
                    const h3 = [...document.querySelectorAll('h3, .label-tile-title, *')]
                        .find(el => /^DISPATCHES$/i.test((el.innerText || '').trim()));
                    if (!h3) return [];
                    let tile = h3;
                    for (let i = 0; i < 12; i++) { if (tile.parentElement) tile = tile.parentElement; }
                    // assignment rows: contain "Assignment ID:"
                    const rows = [...tile.querySelectorAll('*')].filter(el => {
                        const t = el.innerText || '';
                        return /Assignment ID:\s*\d+/.test(t)
                            && el.querySelectorAll('*').length < 30
                            && el.offsetParent !== null;
                    });
                    const seen = new Set();
                    const out = [];
                    for (const r of rows) {
                        const txt = r.innerText || '';
                        const aid = (txt.match(/Assignment ID:\s*(\d+)/) || [])[1];
                        if (!aid || seen.has(aid)) continue;
                        seen.add(aid);
                        const rmot = (txt.match(/(RMOT\d+|ROSS\d+|SCOP\d+)/) || [])[1] || '';
                        const customerLine = txt.split('\n')[0]?.trim() || '';
                        // week hours displayed somewhere in the row (e.g., "5h" or "5:00")
                        const hoursStr = (txt.match(/(\d{1,2}):(\d{2})\s*HRS?/i) || [])[0]
                            || (txt.match(/(\d+(?:\.\d+)?)\s*h\b/i) || [])[0]
                            || '';
                        out.push({
                            assignment_id: aid,
                            customer: customerLine,
                            rmot: rmot,
                            week_hours: hoursStr,
                            raw: txt.substring(0, 300)
                        });
                    }
                    return out;
                })()
                """
            )
            or []
        )

    def _open_labor_entry(self, assignment_id: str) -> bool:
        """Dispatch 選択モーダルから対象 assignment の Labor Entry フォームを開く."""
        click_result = self.eval_js(
            f"""
            (async () => {{
                const target = '{assignment_id}';
                const findRows = (scope) => [...scope.querySelectorAll('*')].filter(el =>
                    (el.innerText || '').includes('Assignment ID: ' + target)
                    && el.querySelectorAll('*').length < 30
                );
                const pickClickable = (rows) => {{
                    const candidates = [];
                    for (const r of rows) {{
                        let p = r;
                        for (let i = 0; i < 8; i++) {{
                            if (!p || !p.offsetParent) break;
                            const cs = getComputedStyle(p);
                            const cls = (p.className && p.className.toString) ? p.className.toString() : '';
                            if (cs.cursor === 'pointer'
                                || /dispatch-item|assignment-item|dispatch-row|clickable/.test(cls)) {{
                                candidates.push({{ el: p, priority: cs.cursor === 'pointer' ? 2 : 1 }});
                            }}
                            p = p.parentElement;
                        }}
                    }}
                    candidates.sort((a, b) => b.priority - a.priority);
                    return candidates.length > 0 ? candidates[0].el : rows[rows.length - 1];
                }};
                const dlgs = [...document.querySelectorAll('.cdk-overlay-pane, mat-dialog-container')]
                    .filter(d => d.offsetParent && /Select a Dispatch/i.test(d.innerText || ''));
                const scope = dlgs[dlgs.length - 1];
                if (!scope) return 'no-modal';
                let rows = findRows(scope);
                // 見えなければスクロールしながら探す
                if (rows.length === 0) {{
                    const scrollables = [...scope.querySelectorAll('*')].filter(el => {{
                        const cs = getComputedStyle(el);
                        return (cs.overflowY === 'auto' || cs.overflowY === 'scroll')
                            && el.scrollHeight > el.clientHeight + 5;
                    }});
                    if (scrollables.length === 0) return 'no-scrollable';
                    const s = scrollables[0];
                    for (let i = 0; i <= 30; i++) {{
                        s.scrollTop = (s.scrollHeight * i) / 30;
                        await new Promise(r => setTimeout(r, 180));
                        rows = findRows(scope);
                        if (rows.length > 0) break;
                    }}
                }}
                if (rows.length === 0) return 'row-not-found';
                // クリック可能な祖先を選んで scrollIntoView → 短く待機 → click
                const el = pickClickable(rows);
                el.scrollIntoView({{ block: 'center', behavior: 'instant' }});
                await new Promise(r => setTimeout(r, 400));
                // DOM からまだ消えていないか再確認（消えていたら再度 findRows でリトライ）
                let elAlive = document.contains(el) ? el : null;
                if (!elAlive) {{
                    const rows2 = findRows(scope);
                    if (rows2.length === 0) return 'row-disappeared';
                    elAlive = pickClickable(rows2);
                    elAlive.scrollIntoView({{ block: 'center', behavior: 'instant' }});
                    await new Promise(r => setTimeout(r, 300));
                }}
                elAlive.click();
                // Labor Entry フォーム出現をポーリング（最大 5 秒）
                for (let i = 0; i < 25; i++) {{
                    await new Promise(r => setTimeout(r, 200));
                    const forms = [...document.querySelectorAll('.cdk-overlay-pane, mat-dialog-container')]
                        .filter(d => d.offsetParent
                            && (d.innerText || '').includes('Assignment ID: ' + target)
                            && /Labor Hours|Select Labor Category/i.test(d.innerText || ''));
                    if (forms.length > 0) return 'labor-entry-open';
                }}
                return 'labor-entry-not-open';
            }})()
            """
        )
        if click_result != "labor-entry-open":
            self._cancel_labor_entry()
            return False
        time.sleep(0.3)
        return True

    def get_dispatch_details(self, assignment_id: str) -> dict[str, str] | None:
        """Dispatch 選択モーダル → 行クリック → Labor Entry フォーム → info(ⓘ) で Total Hours Logged 取得.

        前提: Dispatch 選択モーダルが開いていて、対象のタブに assignment_id が表示されていること。
        フロー: 行クリック → Labor Entry フォームが右に開く → Assignment ID 横の info(ⓘ) クリック
                → Dispatch Details ダイアログ → 値読取 → ダイアログ閉じる → Labor Entry の Cancel
        """
        if not self._open_labor_entry(assignment_id):
            return None

        # 2. Labor Entry フォーム内の info(ⓘ) ボタンをクリック
        clicked_info = self.eval_js(
            f"""
            (() => {{
                const target = '{assignment_id}';
                // Labor Entry フォームを探す（Assignment ID: <target> + Select Labor Category / Labor Hours を含む）
                const forms = [...document.querySelectorAll('.cdk-overlay-pane, mat-dialog-container')]
                    .filter(d => d.offsetParent
                        && (d.innerText || '').includes('Assignment ID: ' + target)
                        && /Labor Hours|Select Labor Category|Labor Category/i.test(d.innerText || ''));
                const form = forms[forms.length - 1];
                if (!form) return 'form-not-found';
                const btn = form.querySelector(
                    '.info-icon-label, [aria-label*="dispatch info" i], [mattooltip="Dispatch Info"], i.icon-info-fill'
                );
                if (!btn) return 'info-btn-not-found';
                btn.click();
                return 'clicked';
            }})()
            """
        )
        if clicked_info != "clicked":
            # Labor Entry をキャンセルして戻る
            self._cancel_labor_entry()
            return None
        time.sleep(1.8)

        # 3. Dispatch Details ダイアログから値読取
        details = self.eval_js(
            r"""
            (() => {
                const dlg = [...document.querySelectorAll('.cdk-overlay-pane, mat-dialog-container')]
                    .find(d => d.offsetParent && /Total Hours Logged|Dispatch Details/i.test(d.innerText || ''));
                if (!dlg) return null;
                const text = dlg.innerText;
                const pick = (label) => {
                    const escaped = label.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&');
                    const re = new RegExp(escaped + '\\s*:?[\\s\\n]+([^\\n]+)', 'i');
                    const m = text.match(re);
                    return m ? m[1].trim() : '';
                };
                return {
                    total_hours_logged: pick('Total Hours Logged'),
                    approved_hours: pick('Approved Hours'),
                    hours_pending_approval: pick('Hours Pending Approval'),
                    start_date: pick('Start Date'),
                    end_date: pick('End Date'),
                    axis_status: pick('Axis Status'),
                    fixed_fee: pick('Fixed Fee'),
                    grm_request_id: pick('GRM Resource Request ID'),
                    raw: text.substring(0, 1500)
                };
            })()
            """
        )

        # 4. Dispatch Details ダイアログを閉じる（span.close-button 等）
        for _ in range(5):
            result = self.eval_js(
                r"""
                (() => {
                    const dlgs = [...document.querySelectorAll('.cdk-overlay-pane, mat-dialog-container')]
                        .filter(d => d.offsetParent && /Total Hours Logged|Dispatch Details/i.test(d.innerText || ''));
                    if (!dlgs.length) return 'closed';
                    const dlg = dlgs[0];
                    const closeBtn = dlg.querySelector(
                        'span.close-button, [aria-label*="dialogue close" i], button[aria-label*="close" i], button.close-btn'
                    );
                    if (closeBtn && closeBtn.offsetParent) { closeBtn.click(); return 'click'; }
                    document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
                    return 'escape';
                })()
                """
            )
            if result == "closed":
                break
            time.sleep(0.5)

        # 5. Labor Entry の Cancel（保存せず元の Dispatch 選択モーダルへ戻る）
        self._cancel_labor_entry()
        return details

    def save_labor_entry_ui(
        self,
        assignment_id: str,
        labor_hours: str,
        notes: str = "",
        labor_category_name: str | None = None,
        late_reason: str | None = None,
    ) -> dict[str, str] | None:
        """Labor Entry フォームを UI で保存する.

        API add-dispatch が core/draft 404 で mutation を拒否する週の fallback 用。
        前提: Dispatch 選択モーダルが開いていて、対象 assignment が現在のタブに表示されていること。

        late_reason: 過去日の場合に必要。None の場合でも Update が disabled なら
                     "Missed Daily Time Entry" を自動選択して再試行する。
        """
        if not self._open_labor_entry(assignment_id):
            return None

        result = self.eval_js(
            f"""
            (async () => {{
                const target = '{assignment_id}';
                const requestedCategory = {json.dumps(labor_category_name)};
                const requestedNotes = {json.dumps(notes)};
                const requestedHours = {json.dumps(labor_hours)};
                const requestedLateReason = {json.dumps(late_reason)};
                const [hoursPart, minutesPart] = requestedHours.split(':');

                const forms = [...document.querySelectorAll('.cdk-overlay-pane, mat-dialog-container')]
                    .filter(d => d.offsetParent
                        && (d.innerText || '').includes('Assignment ID: ' + target)
                        && /Labor Hours|Select Labor Category|Labor Category/i.test(d.innerText || ''));
                const form = forms[forms.length - 1];
                if (!form) return {{ status: 'form-not-found' }};

                const setNativeValue = (el, value) => {{
                    const prototype = Object.getPrototypeOf(el);
                    const descriptor = Object.getOwnPropertyDescriptor(prototype, 'value');
                    if (descriptor && descriptor.set) descriptor.set.call(el, value);
                    else el.value = value;
                    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    el.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                }};

                // Reject forbidden categories
                if (requestedCategory && requestedCategory.includes('ISD only')) {{
                    return {{ status: 'rejected', reason: 'ISD only category is forbidden' }};
                }}

                if (requestedCategory) {{
                    const combo = form.querySelector('[role="combobox"], mat-select, .mat-mdc-select');
                    if (!combo) return {{ status: 'category-combobox-not-found' }};
                    const currentText = (combo.innerText || '').trim();
                    if (currentText !== requestedCategory) {{
                        combo.click();
                        await new Promise(r => setTimeout(r, 400));
                        const options = [...document.querySelectorAll('[role="option"], mat-option, .mat-mdc-option')]
                            .filter(o => o.offsetParent && (o.innerText || '').trim() === requestedCategory);
                        if (!options.length) return {{ status: 'category-option-not-found', requestedCategory, currentText }};
                        options[0].click();
                        await new Promise(r => setTimeout(r, 400));
                    }}
                }}

                const timeInputs = [...form.querySelectorAll('input')]
                    .filter(i => i.offsetParent && (i.getAttribute('placeholder') || '') === '00');
                if (timeInputs.length < 2) return {{ status: 'time-inputs-not-found' }};
                setNativeValue(timeInputs[0], hoursPart.padStart(2, '0'));
                setNativeValue(timeInputs[1], (minutesPart || '00').padStart(2, '0'));

                const notesBox = [...form.querySelectorAll('textarea, input')]
                    .find(el => el.offsetParent && /Brief description|Customer Notes/i.test((el.getAttribute('placeholder') || '') + ' ' + (el.getAttribute('aria-label') || '')));
                if (notesBox && requestedNotes) {{
                    setNativeValue(notesBox, requestedNotes);
                }}

                // Late Reason selection
                const lateReasonToSelect = requestedLateReason || 'Missed Daily Time Entry';
                const lrSelect = form.querySelector('[formcontrolname="lateReason"], [aria-label="Late Reason"]');
                if (lrSelect && lrSelect.offsetParent) {{
                    const trigger = lrSelect.querySelector('.mat-select-trigger');
                    if (trigger) trigger.click(); else lrSelect.click();
                    await new Promise(r => setTimeout(r, 500));
                    const lrOpts = [...document.querySelectorAll('[role="option"], mat-option')]
                        .filter(o => o.offsetParent && (o.innerText || '').trim() === lateReasonToSelect);
                    if (lrOpts.length) {{
                        lrOpts[0].click();
                        await new Promise(r => setTimeout(r, 400));
                    }}
                }}

                await new Promise(r => setTimeout(r, 300));
                const updateBtn = [...form.querySelectorAll('button')].find(b => b.offsetParent && /^Update$/.test((b.innerText || '').trim()));
                if (!updateBtn) return {{ status: 'update-btn-not-found' }};
                if (updateBtn.disabled) return {{ status: 'update-disabled' }};
                updateBtn.click();

                for (let i = 0; i < 30; i++) {{
                    await new Promise(r => setTimeout(r, 250));
                    const stillOpen = [...document.querySelectorAll('.cdk-overlay-pane, mat-dialog-container')]
                        .some(d => d.offsetParent
                            && (d.innerText || '').includes('Assignment ID: ' + target)
                            && /Labor Hours|Select Labor Category|Labor Category/i.test(d.innerText || ''));
                    if (!stillOpen) {{
                        return {{
                            status: 'saved',
                            assignment_id: target,
                            labor_hours: requestedHours,
                            labor_category_name: requestedCategory || '',
                            notes: requestedNotes,
                        }};
                    }}
                }}
                return {{ status: 'save-timeout' }};
            }})()
            """
        )
        return result if isinstance(result, dict) else None

    def _cancel_labor_entry(self) -> None:
        """Labor Entry フォームを Cancel ボタンで閉じる."""
        for _ in range(3):
            result = self.eval_js(
                r"""
                (() => {
                    const forms = [...document.querySelectorAll('.cdk-overlay-pane, mat-dialog-container')]
                        .filter(d => d.offsetParent && /Labor Hours|Select Labor Category/i.test(d.innerText || ''));
                    if (!forms.length) return 'already-closed';
                    const form = forms[forms.length - 1];
                    const cancel = [...form.querySelectorAll('button')].find(b =>
                        b.offsetParent && /^Cancel$/.test((b.innerText || '').trim())
                    );
                    if (cancel) { cancel.click(); return 'cancel'; }
                    return 'no-cancel-btn';
                })()
                """
            )
            if result == "already-closed":
                break
            time.sleep(0.7)

    def collect_week_view_hours(self) -> list[dict[str, str]]:
        """現在の Week View に表示中の全 Dispatch の info を順番に開いて hours を取得."""
        results: list[dict[str, str]] = []
        rows = self.list_week_dispatches()
        for row in rows:
            aid = row["assignment_id"]
            details = self.get_dispatch_details(aid) or {}
            results.append({**row, **details})
        return results


def _parse_dispatch_line(line: str, tab_label: str) -> Dispatch | None:
    """ESXP 一覧行を Dispatch dataclass に変換.

    例: "株式会社SCREEN | Assignment ID: 5086745 | RMOT... | solution | Start: 18-Apr-2026 | 09:04:00 | End: 20-Apr-2026 | 17:04:00"
    """
    parts = [p.strip() for p in line.split("|")]
    customer = ""
    assignment_id = ""
    rmot_id = ""
    solution = ""
    start = ""
    end = ""
    for i, p in enumerate(parts):
        if p.startswith("Assignment ID:"):
            aid = p.replace("Assignment ID:", "").strip()
            assignment_id = aid
            # customer は Assignment ID より前の最後の非ラベル要素
            for prev in reversed(parts[:i]):
                if prev and prev not in ("Recommended", "LABOR ASSIST"):
                    customer = prev
                    break
        elif p.startswith(("RMOT", "ROSS", "SCOP")):
            rmot_id = p
            # solution は RMOT の次
            if i + 1 < len(parts) and not parts[i + 1].startswith("Start:"):
                solution = parts[i + 1]
        elif p.startswith("Start:"):
            start = p.replace("Start:", "").strip()
            if i + 1 < len(parts) and not parts[i + 1].startswith("End:"):
                start = f"{start} {parts[i+1]}"
        elif p.startswith("End:"):
            end = p.replace("End:", "").strip()
            if i + 1 < len(parts):
                end = f"{end} {parts[i+1]}"
    if not assignment_id:
        return None
    return Dispatch(
        customer=customer,
        assignment_id=assignment_id,
        rmot_id=rmot_id,
        solution=solution,
        start=start,
        end=end,
        tab=tab_label,
    )
