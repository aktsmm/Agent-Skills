#!/usr/bin/env python3
"""Export a single-html-forge artifact to PDF or PNG.

Needs Playwright. Only the requested format is produced; nothing is generated
speculatively. Exits non-zero with installation guidance when Playwright is
absent, rather than reporting success without producing anything.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

MISSING = (
    "STOP: this export needs Playwright.\n"
    "      pip install playwright && python -m playwright install chromium\n"
    "      Tier 1 verification works without it; only export and Tier 2 need a browser."
)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Export an artifact to PDF or PNG")
    ap.add_argument("artifact", type=Path)
    ap.add_argument("--pdf", type=Path)
    ap.add_argument("--png", type=Path)
    ap.add_argument("--slides-png", type=Path, help="directory for one PNG per slide")
    ap.add_argument("--scale", type=int, default=2)
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--height", type=int, default=900)
    args = ap.parse_args(argv)

    if not (args.pdf or args.png or args.slides_png):
        print("STOP: pass at least one of --pdf, --png, --slides-png", file=sys.stderr)
        return 1
    if not args.artifact.is_file():
        print(f"STOP: no such file: {args.artifact}", file=sys.stderr)
        return 1

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(MISSING, file=sys.stderr)
        return 2

    url = args.artifact.resolve().as_uri()
    produced = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=args.scale,
        )
        # An artifact must never reach the network. Anything that tries is a defect.
        blocked = []
        page.route("**/*", lambda route: (
            route.continue_() if route.request.url.startswith("file:")
            else (blocked.append(route.request.url), route.abort())
        ))
        page.goto(url, wait_until="load")
        page.wait_for_function("document.fonts ? document.fonts.status === 'loaded' : true")
        page.wait_for_function(
            "Array.from(document.images).every(function (i) { return i.complete; })"
        )

        if blocked:
            browser.close()
            print("STOP: the artifact requested external resources:", file=sys.stderr)
            for u in blocked[:10]:
                print(f"       {u}", file=sys.stderr)
            return 1

        if args.pdf:
            args.pdf.parent.mkdir(parents=True, exist_ok=True)
            page.pdf(path=str(args.pdf), print_background=True, prefer_css_page_size=True)
            produced.append(args.pdf)

        if args.png:
            args.png.parent.mkdir(parents=True, exist_ok=True)
            target = page.query_selector("#shf-root") or page
            target.screenshot(path=str(args.png))
            produced.append(args.png)

        if args.slides_png:
            args.slides_png.mkdir(parents=True, exist_ok=True)
            slides = page.query_selector_all("[data-slide-id]")
            # Drive the real runtime instead of toggling `hidden` directly, so the
            # slide counter and any other chrome match the slide being captured.
            page.keyboard.press("Home")
            for i in range(len(slides)):
                if i:
                    page.keyboard.press("ArrowRight")
                page.wait_for_function(
                    "Array.from(document.images).every(function (i) { return i.complete; })"
                )
                out = args.slides_png / f"slide-{i + 1:02d}.png"
                (page.query_selector("#shf-root") or page).screenshot(path=str(out))
                produced.append(out)

        browser.close()

    for path in produced:
        size = path.stat().st_size
        if size == 0:
            print(f"STOP: {path} is empty", file=sys.stderr)
            return 1
        print(f"wrote {path} ({size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
