#!/usr/bin/env python3
"""Export a single-html-forge artifact to PDF or PNG.

Needs Playwright. Only the requested format is produced; nothing is generated
speculatively. Exits non-zero with installation guidance when Playwright is
absent, rather than reporting success without producing anything.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

MISSING = (
    "STOP: this export needs Playwright.\n"
    "      pip install playwright && python -m playwright install chromium\n"
    "      Tier 1 verification works without it; only export and Tier 2 need a browser."
)


def hide_png_chrome(page) -> None:
    page.locator('[data-shf-action="print"]').evaluate_all(
        "elements => elements.forEach(element => { element.hidden = true; })"
    )


def same_path(left: Path, right: Path) -> bool:
    return left.resolve() == right.resolve() or (left.exists() and right.exists() and left.samefile(right))


def validate_destinations(artifact: Path, targets: list, allow_source: bool = False) -> None:
    for position, target in enumerate(targets):
        if target.exists() and not target.is_file():
            raise ValueError(f"Output is not a file: {target}")
        if not allow_source and same_path(target, artifact):
            raise ValueError("Export output must not overwrite the source HTML")
        if any(same_path(target, prior) for prior in targets[:position]):
            raise ValueError("Requested outputs must use different paths")
        for parent in target.parents:
            if parent.exists() and not parent.is_dir():
                raise ValueError(f"Output parent is not a directory: {parent}")
        if any(prior.resolve() in target.resolve().parents or target.resolve() in prior.resolve().parents for prior in targets[:position]):
            raise ValueError("Output file paths must not contain other output paths")


def publish_file(staged: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target.parent) as folder:
        pending = Path(folder) / target.name
        shutil.copyfile(staged, pending)
        os.replace(pending, target)


def finalize_deck(artifact: Path, target: Path, thumbnails: bool) -> int:
    import derived_assets as derived
    import verify_html as verifier
    from embed_assets import resize, strip_png
    from playwright.sync_api import sync_playwright

    registry = verifier.load_json(Path(__file__).with_name("runtime-registry.json"))
    budget = verifier.load_json(Path(__file__).with_name("budget.json"))
    report = verifier.verify(artifact, registry, budget)
    fatal = [error for error in report.errors if not error.startswith("[DERIVED]")]
    if fatal:
        raise ValueError("\n".join(fatal))
    source = artifact.read_text(encoding="utf-8").replace("\r\n", "\n")
    derived.validate_steps(source)
    pages = derived.slides(source)
    if not pages:
        raise ValueError("Finalize requires a deck with slides")
    report = verifier.Report()
    if verifier.run_tier2(artifact, report, require_print=False) != "ok":
        raise ValueError("\n".join(report.errors))
    images = []
    if thumbnails:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 1600, "height": 900}, reduced_motion="reduce")
                blocked = []
                browser_errors = []
                page.on("pageerror", lambda error: browser_errors.append(str(error)))
                page.on("console", lambda message: browser_errors.append(message.text) if message.type == "error" else None)
                page.route("**/*", lambda route: route.continue_() if route.request.url == artifact.resolve().as_uri() else (blocked.append(route.request.url), route.abort()))
                page.goto(artifact.resolve().as_uri())
                page.evaluate("document.documentElement.classList.add('shf-exporting')")
                page.wait_for_function("document.fonts.status === 'loaded' && [...document.images].every(image => image.complete && image.naturalWidth > 0)")
                page.keyboard.press("Home")
                for ordinal, (slide_id, step) in enumerate(derived.states(source)):
                    if ordinal:
                        page.keyboard.press("ArrowRight")
                    actual = page.evaluate("[document.querySelector('[data-slide-id].is-active')?.getAttribute('data-slide-id'), Number(document.documentElement.getAttribute('data-shf-current-step') || 0)]")
                    if actual != [slide_id, step]:
                        raise ValueError("Slide state differs from requested thumbnail; no HTML was published")
                    slide = next(slide for slide in pages if slide.attrs["data-slide-id"] == slide_id)
                    if step != derived.step_count(slide) - 1:
                        continue
                    payload, _ = resize(page.locator("#shf-root").screenshot(animations="disabled"), "image/png", 320)
                    payload = strip_png(payload)
                    asset = {"id": "shf-thumb-" + str(len(images) + 1), "mime": "image/png", "sha256": hashlib.sha256(payload).hexdigest(), "alt": ""}
                    images.append((slide_id, step, "data:image/png;base64," + base64.b64encode(payload).decode("ascii"), asset))
                if blocked or browser_errors:
                    raise ValueError("Browser or external-resource error during thumbnail rendering; no HTML was published")
            finally:
                browser.close()
    candidate = derived.finalize(source, images)
    with tempfile.TemporaryDirectory() as folder:
        temporary = Path(folder) / "candidate.html"
        temporary.write_text(candidate, encoding="utf-8", newline="\n")
        report = verifier.verify(temporary, registry, budget)
        if report.errors:
            raise ValueError("\n".join(report.errors))
        if verifier.run_tier2(temporary, report) != "ok":
            raise ValueError("\n".join(report.errors))
        publish_file(temporary, target)
    print(f"wrote {target} ({target.stat().st_size} bytes; {len(images)} thumbnails; Tier 1/2 PASS)")
    return 0


def parse_options(argv=None):
    ap = argparse.ArgumentParser(description="Export an artifact to PDF or PNG")
    ap.add_argument("artifact", type=Path)
    ap.add_argument("--pdf", type=Path)
    ap.add_argument("--png", type=Path)
    ap.add_argument("--slides-png", type=Path, help="directory for one PNG per slide")
    ap.add_argument("--scale", type=int, default=2)
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--finalize", type=Path, help="write a verified HTML with static print pages")
    ap.add_argument("--thumbnails", action="store_true", help="include embedded thumbnails with --finalize")
    args = ap.parse_args(argv)

    if not (args.pdf or args.png or args.slides_png or args.finalize):
        raise ValueError("Pass at least one of --pdf, --png, --slides-png, --finalize")
    if args.finalize and any((args.pdf, args.png, args.slides_png)):
        raise ValueError("--finalize cannot be combined with export options; finalize first, then export")
    if args.thumbnails and not args.finalize:
        raise ValueError("--thumbnails requires --finalize")
    if min(args.width, args.height, args.scale) <= 0:
        raise ValueError("--width, --height and --scale must be positive integers")
    if not args.artifact.is_file():
        raise ValueError(f"No such file: {args.artifact}")
    if args.slides_png and args.slides_png.exists() and not args.slides_png.is_dir():
        raise ValueError("--slides-png must name a directory, not a file")
    targets = [path for path in (args.pdf, args.png, args.finalize) if path is not None]
    if args.slides_png:
        targets.append(args.slides_png / "manifest.json")
    validate_destinations(args.artifact, targets, allow_source=bool(args.finalize))
    return args


def export_formats(args) -> int:
    import derived_assets as derived
    import verify_html as verifier
    from playwright.sync_api import sync_playwright
    source = args.artifact.read_text(encoding="utf-8").replace("\r\n", "\n")
    report = verifier.verify(args.artifact, verifier.load_json(Path(__file__).with_name("runtime-registry.json")), verifier.load_json(Path(__file__).with_name("budget.json")))
    if report.errors:
        raise ValueError("; ".join(report.errors))
    if any(step > 0 for _, step in derived.states(source)) and 'id="shf-print"' not in source:
        raise ValueError("Finalize step decks before export")

    slides = derived.slides(source)
    if args.slides_png and not slides:
        raise ValueError("--slides-png requires a deck with slides")
    exports = []
    manifest = []
    if args.slides_png:
        for index, slide in enumerate(slides):
            count = derived.step_count(slide)
            selected = range(count) if slide.attrs.get("data-shf-print") == "all" else [count - 1]
            for step in selected:
                suffix = f"-step-{step + 1:02d}" if count > 1 and slide.attrs.get("data-shf-print") == "all" else ""
                name = f"slide-{index + 1:02d}{suffix}.png"
                manifest.append({"file": name, "slideId": slide.attrs["data-slide-id"], "step": step})
        exports = [args.slides_png / item["file"] for item in manifest] + [args.slides_png / "manifest.json"]
    validate_destinations(args.artifact, [path for path in (args.pdf, args.png) if path is not None] + exports)

    url = args.artifact.resolve().as_uri()
    produced = []

    with tempfile.TemporaryDirectory() as staging, sync_playwright() as pw:
        staging = Path(staging)
        browser = pw.chromium.launch()
        page = browser.new_page(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=args.scale,
        )
        # An artifact must never reach the network. Anything that tries is a defect.
        blocked = []
        browser_errors = []
        page.on("pageerror", lambda error: browser_errors.append(str(error)))
        page.on("console", lambda message: browser_errors.append(message.text) if message.type == "error" else None)
        page.route("**/*", lambda route: (
            route.continue_() if route.request.url == url
            else (blocked.append(route.request.url), route.abort())
        ))
        page.goto(url, wait_until="load")
        page.wait_for_function("document.fonts ? document.fonts.status === 'loaded' : true")
        page.wait_for_function(
            "Array.from(document.images).every(function (i) { return i.complete; })"
        )
        if not page.evaluate("Array.from(document.images).every(image => image.naturalWidth > 0 && image.naturalHeight > 0)"):
            raise ValueError("Image decoding failed; no exports were published")

        if blocked:
            raise ValueError("The artifact requested external resources; no exports were published")

        if args.pdf:
            if slides:
                print_errors = verifier.check_print_layout(page)
                if print_errors:
                    raise ValueError("; ".join(print_errors) + "; no exports were published")
            staged = staging / "document.pdf"
            pdf_options = {"width": "16in", "height": "9in", "margin": {"top": "0", "bottom": "0", "left": "0", "right": "0"}} if slides else {}
            page.pdf(path=str(staged), print_background=True, prefer_css_page_size=True, **pdf_options)
            produced.append((staged, args.pdf))

        if args.png or args.slides_png:
            hide_png_chrome(page)
            page.evaluate("document.documentElement.classList.add('shf-exporting')")

        if args.png:
            target = page.query_selector("#shf-root") or page
            staged = staging / "document.png"
            target.screenshot(path=str(staged), animations="disabled")
            produced.append((staged, args.png))

        if args.slides_png:
            # Drive the real runtime instead of toggling `hidden` directly, so the
            # slide counter and any other chrome match the slide being captured.
            page.keyboard.press("Home")
            for ordinal, (slide_id, step) in enumerate(derived.states(source)):
                if ordinal:
                    page.keyboard.press("ArrowRight")
                item = next((item for item in manifest if item["slideId"] == slide_id and item["step"] == step), None)
                if item is None:
                    continue
                actual = page.evaluate("[document.querySelector('[data-slide-id].is-active')?.getAttribute('data-slide-id'), Number(document.documentElement.getAttribute('data-shf-current-step') || 0)]")
                if actual != [slide_id, step]:
                    raise ValueError("Slide state differs from requested export; no exports were published")
                page.wait_for_function(
                    "Array.from(document.images).every(function (i) { return i.complete; })"
                )
                staged = staging / item["file"]
                (page.query_selector("#shf-root") or page).screenshot(path=str(staged), animations="disabled")
                produced.append((staged, args.slides_png / item["file"]))
            staged = staging / "manifest.json"
            staged.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            produced.append((staged, args.slides_png / "manifest.json"))

        browser.close()
        if blocked or browser_errors:
            raise ValueError("Browser or external-resource error during export; no exports were published")
        if any(not path.is_file() or not path.stat().st_size for path, _ in produced):
            raise ValueError("An export is missing or empty; no exports were published")
        for staged, target in produced:
            publish_file(staged, target)
            print(f"wrote {target} ({target.stat().st_size} bytes)")
    return 0


def main(argv=None) -> int:
    try:
        args = parse_options(argv)
    except (ValueError, OSError) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 1
    try:
        from playwright.sync_api import Error as BrowserError
    except ImportError:
        print(MISSING, file=sys.stderr)
        return 2
    from embed_assets import Stop as AssetError
    try:
        return finalize_deck(args.artifact, args.finalize, args.thumbnails) if args.finalize else export_formats(args)
    except ImportError:
        print("STOP: a required export dependency is unavailable; install scripts/requirements.txt", file=sys.stderr)
        return 2
    except (ValueError, OSError, KeyError, StopIteration, BrowserError, AssetError) as exc:
        print(f"STOP: {str(exc) or 'Export could not resolve required artifact data'}", file=sys.stderr)
        return 2 if isinstance(exc.__cause__, ImportError) else 1


if __name__ == "__main__":
    sys.exit(main())
