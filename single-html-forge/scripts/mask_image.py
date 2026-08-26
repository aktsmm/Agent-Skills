#!/usr/bin/env python3
"""Mask rectangles in an image before it is embedded.

Optional utility. Needs Pillow. Solid fill is the default because a blur can
leave enough signal to read short strings such as a tenant or subscription name.

This does not find sensitive regions for you. You pass the rectangles, and the
final visual check stays with you.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_rect(value: str):
    try:
        x, y, w, h = (int(part) for part in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("rectangle must be x,y,width,height in pixels") from exc
    if w <= 0 or h <= 0:
        raise argparse.ArgumentTypeError("rectangle width and height must be positive")
    return x, y, w, h


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Mask rectangles in an image")
    ap.add_argument("source", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--rect", type=parse_rect, action="append", default=[],
                    help="x,y,width,height in pixels; repeatable")
    ap.add_argument("--crop", type=parse_rect, help="keep only this region")
    ap.add_argument("--mode", choices=("fill", "blur"), default="fill")
    ap.add_argument("--fill", default="#111111")
    args = ap.parse_args(argv)

    if not args.rect and not args.crop:
        print("STOP: pass at least one --rect or --crop", file=sys.stderr)
        return 1

    try:
        from PIL import Image, ImageDraw, ImageFilter, ImageOps
    except ImportError:
        print(
            "STOP: this utility needs Pillow. Install it with 'pip install Pillow'.\n"
            "      The rest of the skill works without it; only masking and resizing need it.",
            file=sys.stderr,
        )
        return 1

    if not args.source.is_file():
        print(f"STOP: no such file: {args.source}", file=sys.stderr)
        return 1

    with Image.open(args.source) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        if args.crop:
            x, y, w, h = args.crop
            img = img.crop((x, y, x + w, y + h))
        applied = []
        for x, y, w, h in args.rect:
            box = (x, y, x + w, y + h)
            if args.mode == "blur":
                region = img.crop(box).filter(ImageFilter.GaussianBlur(radius=max(w, h) / 8))
                img.paste(region, box)
            else:
                ImageDraw.Draw(img).rectangle(box, fill=args.fill)
            applied.append(box)
        img.save(args.output)

    # Confirm the fill actually landed, so a mistyped rectangle is not mistaken for a mask.
    if args.mode == "fill" and applied:
        with Image.open(args.output) as check:
            check = check.convert("RGB")
            target = tuple(int(args.fill[i:i + 2], 16) for i in (1, 3, 5))
            for box in applied:
                region = check.crop(box)
                colours = region.getcolors(maxcolors=4) or []
                if len(colours) != 1 or colours[0][1] != target:
                    print(f"STOP: rectangle {box} is not a solid fill in the output", file=sys.stderr)
                    return 1

    print(f"wrote {args.output} ({len(applied)} rectangle(s), mode={args.mode})")
    print("Check the result visually before embedding. This tool cannot tell you what is sensitive.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
