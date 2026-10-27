import argparse
import asyncio
import base64
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import time
from pathlib import Path

from playwright.async_api import async_playwright


DEFAULT_ROOT = str(Path.home() / "Pictures" / "Teams Photo Export")


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def find_edge() -> str:
    candidates = [
        shutil.which("msedge"),
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
    ]
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate
    raise FileNotFoundError("Microsoft Edge was not found; install it or add msedge to PATH.")


def safe_name(value: str) -> str:
    value = re.sub(r'[\\/:*?"<>|]', "_", value).strip().rstrip(".")
    return value or "Teams_Photos"


def extension_from_type(content_type: str) -> str:
    content_type = (content_type or "").lower()
    if "jpeg" in content_type or "jpg" in content_type:
        return "jpg"
    if "png" in content_type:
        return "png"
    if "gif" in content_type:
        return "gif"
    if "webp" in content_type:
        return "webp"
    return "bin"


def ensure_output_root(value: str | None) -> Path:
    root = value or os.environ.get("TEAMS_IMAGE_EXPORT_ROOT") or DEFAULT_ROOT
    return Path(root)


def start_edge(port: int, url: str, user_data_dir: Path) -> subprocess.Popen:
    user_data_dir.mkdir(parents=True, exist_ok=True)
    return subprocess.Popen(
        [
            find_edge(),
            f"--remote-debugging-port={port}",
            f"--user-data-dir={user_data_dir}",
            url,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


async def page_from_cdp(port: int, url: str):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else await context.new_page()
    if url and "teams" not in page.url.lower():
        await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    return playwright, browser, page


async def use_teams_web_if_launcher(page) -> None:
    await page.wait_for_timeout(3_000)
    if "launcher" in page.url:
        await page.goto("https://teams.microsoft.com/v2", wait_until="domcontentloaded", timeout=60_000)
        await page.wait_for_timeout(30_000)
    elif "/error/eoa" in page.url:
        await page.goto("https://teams.microsoft.com/v2", wait_until="domcontentloaded", timeout=60_000)
        await page.wait_for_timeout(30_000)


async def collect_visible_media(page):
    return await page.evaluate(
        """
async () => {
  const imgs = Array.from(document.images)
    .map((img, index) => ({
      index,
      src: img.src,
      alt: img.alt,
      w: img.naturalWidth || img.width,
      h: img.naturalHeight || img.height
    }))
    .filter(x =>
      (x.alt === 'メディア' || x.alt === 'Media') &&
      x.src.startsWith('blob:https://teams.cloud.microsoft/') &&
      x.w >= 300 && x.h >= 300
    );

  const seen = new Set();
  const unique = [];
  for (const x of imgs) {
    if (!seen.has(x.src)) {
      seen.add(x.src);
      unique.push(x);
    }
  }

  const out = [];
  for (const x of unique) {
    const res = await fetch(x.src);
    const blob = await res.blob();
    const buf = await blob.arrayBuffer();
    let binary = '';
    const bytes = new Uint8Array(buf);
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) {
      binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
    }
    out.push({
      index: x.index,
      width: x.w,
      height: x.h,
      contentType: blob.type || res.headers.get('content-type') || '',
      b64: btoa(binary)
    });
  }
  return out;
}
"""
    )


async def scroll_and_collect(page, max_scrolls: int):
    all_items = []
    seen_hashes = set()

    for _ in range(max_scrolls):
        for item in await collect_visible_media(page):
            digest = hashlib.sha256(base64.b64decode(item["b64"])).hexdigest()
            if digest not in seen_hashes:
                seen_hashes.add(digest)
                all_items.append(item)

        moved = await page.evaluate(
            """
() => {
  const candidates = [
    document.querySelector('[data-tid="message-list"]'),
    document.querySelector('[role="main"] [role="list"]'),
    document.querySelector('.ts-message-list-container')
  ].filter(Boolean);
  const c = candidates[0] || document.scrollingElement || document.documentElement;
  const before = c.scrollTop;
  c.scrollTop = Math.max(0, c.scrollTop - Math.max(600, c.clientHeight || 800));
  return c.scrollTop !== before;
}
"""
        )
        if not moved:
            break
        await page.wait_for_timeout(2_000)

    return all_items


def save_items(items, folder: Path, date: str, title: str, dry_run: bool):
    if not dry_run:
        folder.mkdir(parents=True, exist_ok=True)
    existing_hashes = {}
    for path in (folder.glob("*") if folder.exists() else []):
        if path.is_file():
            existing_hashes[hashlib.sha256(path.read_bytes()).hexdigest()] = path

    results = []
    seq = 1
    for item in items:
        data = base64.b64decode(item["b64"])
        digest = hashlib.sha256(data).hexdigest()
        if digest in existing_hashes:
            results.append({"status": "skipped_duplicate", "file": str(existing_hashes[digest])})
            continue

        ext = extension_from_type(item.get("contentType", ""))
        while True:
            path = folder / safe_name(f"{date}_{title}_{seq:03d}.{ext}")
            seq += 1
            if not path.exists():
                break

        if not dry_run:
            path.write_bytes(data)
        existing_hashes[digest] = path
        results.append(
            {
                "status": "would_save" if dry_run else "saved",
                "file": str(path),
                "bytes": len(data),
                "contentType": item.get("contentType", ""),
                "width": item.get("width"),
                "height": item.get("height"),
            }
        )
    return results


async def main():
    parser = argparse.ArgumentParser(description="Export visible Microsoft Teams media images.")
    parser.add_argument("--url", required=True, help="Teams chat/thread URL to open.")
    parser.add_argument("--title", required=True, help="Folder/file title component.")
    parser.add_argument("--date", required=True, help="Date component, e.g. 2026-07-02.")
    parser.add_argument("--output-root", help="Override TEAMS_IMAGE_EXPORT_ROOT.")
    parser.add_argument("--port", type=int, default=0, help="CDP port; 0 picks a free loopback port.")
    parser.add_argument("--user-data-dir", default=os.path.join(os.environ.get("TEMP", "."), "teams-photo-export-edge-profile"))
    parser.add_argument("--max-scrolls", type=int, default=0, help="0 means visible images only.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-browser-open", action="store_true")
    args = parser.parse_args()

    root = ensure_output_root(args.output_root)
    folder = root / safe_name(f"{args.date}_{args.title}")
    args.port = args.port or free_port()

    process = None
    try:
        process = start_edge(args.port, args.url, Path(args.user_data_dir))
        time.sleep(5)
        playwright, browser, page = await page_from_cdp(args.port, args.url)
        await use_teams_web_if_launcher(page)
        await page.wait_for_timeout(5_000)

        if args.max_scrolls > 0:
            items = await scroll_and_collect(page, args.max_scrolls)
        else:
            items = await collect_visible_media(page)

        results = save_items(items, folder, args.date, args.title, args.dry_run)
        print(json.dumps({"folder": str(folder), "count": len(results), "results": results}, ensure_ascii=False, indent=2))

        await browser.close()
        await playwright.stop()
    finally:
        if process and not args.keep_browser_open:
            process.terminate()


if __name__ == "__main__":
    asyncio.run(main())
