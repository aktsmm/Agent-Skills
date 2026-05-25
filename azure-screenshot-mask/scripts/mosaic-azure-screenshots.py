"""Pixel-style mosaic for Azure Portal (or any) screenshots.

Use when publishing screenshots that contain environment-sensitive info such as:
- Top-right tenant name / user avatar strip (Azure Portal header)
- Subscription name or subscription ID values shown inside the page

By default, the script applies a pixel mosaic to the **top-right tenant strip**,
which has roughly the same shape across Azure Portal screenshots taken at the
standard 1912 px-wide viewport (last 320 px wide, top 44 px tall).

Additional regions can be specified with `--region L,T,R,B` (in pixels) and
the flag is repeatable.

Examples
--------
# Mask only the top-right tenant strip on every PNG in a folder (overwrite in place):
python scripts/mosaic-azure-screenshots.py images/qiita/some-article

# Single file, plus an extra region (e.g. subscription name row):
python scripts/mosaic-azure-screenshots.py images/qiita/.../overview.png --region 450,277,740,304

# Custom top-right strip size, or skip the default strip entirely:
python scripts/mosaic-azure-screenshots.py images/foo.png --topright-width 280 --topright-height 40
python scripts/mosaic-azure-screenshots.py images/foo.png --no-topright --region 100,200,500,240

Notes
-----
- Files are overwritten in place. Use `--backup` to keep `<name>.bak.png` copies.
- Body-content region coordinates depend on the page layout, so they stay
  article-specific. Capture them once per page and pass via `--region` flags.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image


def pixelate(img: Image.Image, box: tuple[int, int, int, int], block: int = 14) -> None:
    """Mosaic the given (l, t, r, b) box in place by downscaling then upscaling."""
    l, t, r, b = box
    iw, ih = img.size
    l, t = max(0, l), max(0, t)
    r, b = min(iw, r), min(ih, b)
    if r - l <= 0 or b - t <= 0:
        return
    region = img.crop((l, t, r, b))
    sw = max(1, (r - l) // block)
    sh = max(1, (b - t) // block)
    small = region.resize((sw, sh), Image.NEAREST)
    region = small.resize((r - l, b - t), Image.NEAREST)
    img.paste(region, (l, t))


def parse_region(spec: str) -> tuple[int, int, int, int]:
    parts = [int(p.strip()) for p in spec.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError(f"--region expects L,T,R,B (got: {spec!r})")
    return tuple(parts)  # type: ignore[return-value]


def iter_targets(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(path.glob("*.png"))
    raise FileNotFoundError(path)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Mosaic env-sensitive areas of screenshots.")
    ap.add_argument("path", type=Path, help="PNG file or directory of PNGs.")
    ap.add_argument(
        "--region",
        action="append",
        type=parse_region,
        default=[],
        help="Extra mosaic region as L,T,R,B (pixel coords). Repeatable.",
    )
    ap.add_argument("--topright-width", type=int, default=320, help="Top-right strip width.")
    ap.add_argument("--topright-height", type=int, default=44, help="Top-right strip height.")
    ap.add_argument("--no-topright", action="store_true", help="Skip default top-right strip.")
    ap.add_argument("--block", type=int, default=14, help="Mosaic block size (px).")
    ap.add_argument("--backup", action="store_true", help="Write <name>.bak.png before overwrite.")
    args = ap.parse_args(argv)

    targets = iter_targets(args.path)
    if not targets:
        print(f"no PNG found at: {args.path}", file=sys.stderr)
        return 1

    for p in targets:
        with Image.open(p) as src:
            img = src.convert("RGB")
            W, H = img.size
        regions = list(args.region)
        if not args.no_topright:
            regions.append((W - args.topright_width, 0, W, args.topright_height))
        if not regions:
            print(f"skip (no regions): {p.name}")
            continue
        if args.backup:
            bak = p.with_suffix(".bak.png")
            if not bak.exists():
                img.save(bak)
        for region in regions:
            pixelate(img, region, block=args.block)
        img.save(p)
        print(f"masked: {p.name} ({W}x{H}) regions={len(regions)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
