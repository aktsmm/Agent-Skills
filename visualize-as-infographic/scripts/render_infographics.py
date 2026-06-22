"""Render self-contained infographic HTML files to PNG with Playwright.

Usage:
  python render_infographics.py <output-dir>

The script detects poster size from a viewport meta tag like:
  <meta name="viewport" content="width=1200,height=675,initial-scale=1" />

It renders every .html file in the directory except files starting with '_' and
writes PNGs next to them using the same stem.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

VIEWPORT_RE = re.compile(r"content=[\"'][^\"']*width=(\d+),height=(\d+)[^\"']*[\"']", re.I)


def detect_size(html_path: Path) -> tuple[int, int]:
    text = html_path.read_text(encoding="utf-8", errors="ignore")
    match = VIEWPORT_RE.search(text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 1200, 675


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python render_infographics.py <output-dir>", file=sys.stderr)
        return 2

    out_dir = Path(sys.argv[1]).resolve()
    if not out_dir.is_dir():
        print(f"Not a directory: {out_dir}", file=sys.stderr)
        return 2

    html_files = sorted(p for p in out_dir.glob("*.html") if not p.name.startswith("_"))
    if not html_files:
        print(f"No HTML files found in {out_dir}", file=sys.stderr)
        return 1

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for html_path in html_files:
                width, height = detect_size(html_path)
                png_path = html_path.with_suffix(".png")
                page = browser.new_page(
                    viewport={"width": width, "height": height},
                    device_scale_factor=2,
                )
                page.goto(html_path.as_uri(), wait_until="load")
                page.wait_for_timeout(1400)
                page.screenshot(path=str(png_path), full_page=True)
                page.close()
                print(f"rendered {png_path.name} {width}x{height}")
        finally:
            browser.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
