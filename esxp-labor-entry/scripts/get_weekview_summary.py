"""ESXP Week View の現在表示値を DOM から取得する CLI.

目的:
    - API が 404 / 空応答でも、Week View 画面に見えている実値を確認する
    - THIS WEEK 合計、日別 HRS、各タイル合計、Overhead/Non Project の行合計を構造化する

使い方:
    python get_weekview_summary.py
    python get_weekview_summary.py --format markdown
    python get_weekview_summary.py --format json --output output/esxp-weekview-summary.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from esxp_client import EsxpClient  # noqa: E402


def fetch_summary() -> dict:
    with EsxpClient() as client:
        summary = client.eval_js(
            r"""
            (() => {
                const clean = (s) => (s || '').replace(/\u200b/g, '').replace(/\s+$/g, '').trim();
                const parseDay = (text) => {
                    const compact = clean(text).replace(/\n+/g, ' ');
                    const dayMatch = compact.match(/^(\d{2})\s+([A-Z]+)\s+(\d{1,2}:\d{2})\s+HRS/i);
                    return dayMatch ? {
                        day_of_month: dayMatch[1],
                        weekday: dayMatch[2],
                        hours: dayMatch[3],
                        raw: compact,
                    } : {
                        raw: compact,
                    };
                };

                const tiles = [...document.querySelectorAll('.tm-tile')];
                const tileSummary = {};
                for (const tile of tiles) {
                    const text = clean(tile.innerText || '');
                    if (!text) continue;
                    const lines = text.split(/\n+/).map(clean).filter(Boolean);
                    if (!lines.length) continue;
                    const title = lines[0];
                    const hoursMatch = text.match(/(\d{1,2}:\d{2})\s*$/m);
                    tileSummary[title] = {
                        total: hoursMatch ? hoursMatch[1] : '',
                        raw: text,
                    };
                }

                const dayButtons = [...document.querySelectorAll('.carousel-date-btn')].map((el) => ({
                    ...parseDay(el.innerText || ''),
                    selected: el.classList.contains('selected') || /selected/.test(el.className || ''),
                }));

                const weekMatch = (document.body.innerText || '').match(/(\d{1,2}:\d{2})\s*HRS\s*THIS WEEK/i);

                const overheadTile = tiles.find((tile) => /OVERHEAD\/NON PROJECT HOURS/i.test(tile.innerText || ''));
                const overheadRows = [];
                if (overheadTile) {
                    const rowTexts = (overheadTile.innerText || '')
                        .split(/\n+/)
                        .map(clean)
                        .filter((line) => line && line !== ':');
                    const labelRe = /^(Out of office|Vacation|General Admin, Meetings & Events|Unified Presales|Training & Accreditation Taken|Mentor\/Community\/ Practice Contribution)$/i;
                    for (let index = 0; index < rowTexts.length; index++) {
                        const label = rowTexts[index];
                        if (!labelRe.test(label)) continue;
                        let total = '';
                        for (let cursor = index + 1; cursor < rowTexts.length; cursor++) {
                            if (labelRe.test(rowTexts[cursor])) break;
                            if (/^\d{1,2}:\d{2}$/.test(rowTexts[cursor])) {
                                total = rowTexts[cursor];
                            }
                        }
                        overheadRows.push({ name: label, total });
                    }
                }

                const dispatchTile = tiles.find((tile) => /DISPATCHES/i.test(tile.innerText || ''));
                const dispatchRows = [];
                if (dispatchTile) {
                    const rows = [...dispatchTile.querySelectorAll('*')].filter((el) => {
                        const text = el.innerText || '';
                        return el.offsetParent && /Assignment ID:\s*\d+/.test(text) && el.querySelectorAll('*').length < 30;
                    });
                    const seen = new Set();
                    for (const row of rows) {
                        const text = clean(row.innerText || '');
                        const aid = (text.match(/Assignment ID:\s*(\d+)/) || [])[1] || '';
                        if (!aid || seen.has(aid)) continue;
                        seen.add(aid);
                        dispatchRows.push({
                            assignment_id: aid,
                            rmot_id: (text.match(/(RMOT\d+|ROSS\d+|SCOP\d+)/) || [])[1] || '',
                            raw: text,
                        });
                    }
                }

                return {
                    current_url: location.href,
                    title: document.title,
                    this_week_hours: weekMatch ? weekMatch[1] : '',
                    days: dayButtons,
                    tiles: tileSummary,
                    overhead_rows: overheadRows,
                    dispatch_rows: dispatchRows,
                };
            })()
            """
        )
    return summary or {}


def format_markdown(summary: dict) -> str:
    lines = [
        "# ESXP Week View Summary",
        "",
        f"- URL: {summary.get('current_url', '')}",
        f"- THIS WEEK: {summary.get('this_week_hours', '') or 'N/A'}",
        "",
        "## 日別 HRS",
        "",
        "| Day | Weekday | Hours | Selected |",
        "|---|---|---:|---|",
    ]
    for day in summary.get("days", []):
        lines.append(
            f"| {day.get('day_of_month', '')} | {day.get('weekday', '')} | {day.get('hours', '')} | {'yes' if day.get('selected') else 'no'} |"
        )

    lines += ["", "## タイル合計", "", "| Tile | Total |", "|---|---:|"]
    for title, info in summary.get("tiles", {}).items():
        lines.append(f"| {title} | {info.get('total', '')} |")

    rows = summary.get("overhead_rows", [])
    if rows:
        lines += ["", "## Overhead / Non Project 明細", "", "| Category | Total |", "|---|---:|"]
        for row in rows:
            lines.append(f"| {row.get('name', '')} | {row.get('total', '')} |")

    dispatch_rows = summary.get("dispatch_rows", [])
    if dispatch_rows:
        lines += ["", "## Week View に表示中の Dispatch", "", "| Assignment ID | RMOT/ROSS |", "|---|---|"]
        for row in dispatch_rows:
            lines.append(f"| {row.get('assignment_id', '')} | {row.get('rmot_id', '')} |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    summary = fetch_summary()
    text = json.dumps(summary, ensure_ascii=False, indent=2) if args.format == "json" else format_markdown(summary)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())