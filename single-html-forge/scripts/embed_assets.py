#!/usr/bin/env python3
"""Turn an image into an embeddable asset for a single-html-forge artifact.

Metadata stripping is standard library only, so it works everywhere. Resizing
and re-encoding need Pillow; when Pillow is missing this fails loudly instead of
quietly embedding an unprocessed image.

Default is a dry run. Pass --apply to write the artifact.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import struct
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent

PNG_ALLOWED = {b"IHDR", b"PLTE", b"IDAT", b"IEND", b"tRNS", b"gAMA", b"cHRM", b"sRGB", b"bKGD", b"pHYs"}
JPEG_ALLOWED = {0xC0, 0xC1, 0xC2, 0xC4, 0xDB, 0xDA, 0xDD, 0xD9, 0xD8}
JFIF_APP0 = 0xE0


class Stop(Exception):
    """A condition the caller must resolve; never swallowed."""


def sniff(payload: bytes) -> str:
    if payload.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if payload.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if payload.startswith(b"RIFF") and payload[8:12] == b"WEBP":
        return "image/webp"
    raise Stop("unrecognised image format; supported: PNG, JPEG, WebP")


def strip_png(payload: bytes) -> bytes:
    out = bytearray(payload[:8])
    i = 8
    while i + 8 <= len(payload):
        length = int.from_bytes(payload[i:i + 4], "big")
        ctype = payload[i + 4:i + 8]
        end = i + 12 + length
        if ctype in PNG_ALLOWED:
            out += payload[i:end]
        i = end
    return bytes(out)


def strip_jpeg(payload: bytes) -> bytes:
    out = bytearray(payload[:2])
    i = 2
    while i + 4 <= len(payload):
        if payload[i] != 0xFF:
            break
        marker = payload[i + 1]
        if marker == 0xD9:
            break
        seglen = int.from_bytes(payload[i + 2:i + 4], "big")
        end = i + 2 + seglen
        keep = marker in JPEG_ALLOWED
        if marker == JFIF_APP0 and payload[i + 4:i + 9] == b"JFIF\x00":
            keep = True
        if keep:
            out += payload[i:end]
        if marker == 0xDA:
            out += payload[end:]
            return bytes(out)
        i = end
    return bytes(out)


def png_size(payload: bytes):
    w, h = struct.unpack(">II", payload[16:24])
    return w, h


def jpeg_size(payload: bytes):
    i = 2
    while i + 4 <= len(payload):
        if payload[i] != 0xFF:
            break
        marker = payload[i + 1]
        seglen = int.from_bytes(payload[i + 2:i + 4], "big")
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", payload[i + 5:i + 9])
            return w, h
        i += 2 + seglen
    raise Stop("could not read JPEG dimensions")


def dimensions(mime: str, payload: bytes):
    if mime == "image/png":
        return png_size(payload)
    if mime == "image/jpeg":
        return jpeg_size(payload)
    raise Stop("WebP dimensions need Pillow; convert to PNG or JPEG first")


def load(source: str, allow_network: bool) -> bytes:
    if re.match(r"^https?://", source):
        if not allow_network:
            raise Stop(
                f"'{source}' is a remote image. Re-run with --allow-network, or download it "
                "and pass the local path. Remote images are always inlined at build time; "
                "an artifact never keeps an external reference."
            )
        import urllib.request

        with urllib.request.urlopen(source, timeout=30) as resp:  # noqa: S310
            if resp.status != 200:
                raise Stop(f"fetch failed with HTTP {resp.status}: {source}")
            return resp.read()
    path = Path(source)
    if not path.is_file():
        raise Stop(f"no such file: {source}")
    return path.read_bytes()


def resize(payload: bytes, mime: str, max_w: int):
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise Stop(
            "resizing and re-encoding need Pillow, which is not installed. "
            "Install it with 'pip install Pillow', or drop --max-width to embed as-is."
        ) from exc
    import io

    with Image.open(io.BytesIO(payload)) as img:
        img = ImageOps.exif_transpose(img)  # bake orientation before metadata is dropped
        if img.width > max_w:
            ratio = max_w / img.width
            img = img.resize((max_w, max(1, round(img.height * ratio))), Image.LANCZOS)
        buf = io.BytesIO()
        if mime == "image/jpeg":
            img.convert("RGB").save(buf, format="JPEG", quality=85, optimize=True)
        else:
            img.save(buf, format="PNG", optimize=True)
            mime = "image/png"
        return buf.getvalue(), mime


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Prepare an image for embedding")
    ap.add_argument("source", help="local path or http(s) URL")
    ap.add_argument("--asset-id", required=True)
    ap.add_argument("--alt", required=True, help="alt text; required, never generated for you")
    ap.add_argument("--max-width", type=int, help="resize before embedding (needs Pillow)")
    ap.add_argument("--allow-network", action="store_true")
    ap.add_argument("--sanitized", action="store_true",
                    help="assert the image carries no confidential content")
    ap.add_argument("--budget", type=Path, default=HERE / "budget.json")
    ap.add_argument("--out", type=Path, help="write the asset JSON here")
    ap.add_argument("--apply", action="store_true", help="write output instead of a dry run")
    args = ap.parse_args(argv)

    budget = json.loads(args.budget.read_text(encoding="utf-8"))

    try:
        raw = load(args.source, args.allow_network)
        mime = sniff(raw)
        if args.max_width:
            raw, mime = resize(raw, mime, args.max_width)
        if mime == "image/png":
            clean = strip_png(raw)
        elif mime == "image/jpeg":
            clean = strip_jpeg(raw)
        else:
            raise Stop(
                "WebP metadata stripping is not implemented with the standard library. "
                "Convert to PNG or JPEG first."
            )
        width, height = dimensions(mime, clean)
    except Stop as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 1

    if not args.sanitized:
        print(
            "STOP: confirm the image is sanitized for publication before embedding.\n"
            "      A text scan cannot see a tenant name, subscription name, or customer\n"
            "      name rendered inside an image. Mask it first (scripts/mask_image.py),\n"
            "      then re-run with --sanitized.",
            file=sys.stderr,
        )
        return 1

    uri = f"data:{mime};base64,{base64.b64encode(clean).decode('ascii')}"
    size = len(uri.encode("utf-8"))
    limit = budget["perImageBytes"]["fail"]
    warn = budget["perImageBytes"]["warn"]
    if size > limit:
        print(
            f"STOP: the encoded asset is {size} bytes, over the hard limit {limit}.\n"
            f"      Re-run with --max-width to shrink it, or split the content.",
            file=sys.stderr,
        )
        return 1
    if size > warn:
        print(f"warn: encoded asset is {size} bytes, over the warning threshold {warn}", file=sys.stderr)

    asset = {
        "id": args.asset_id,
        "mime": mime,
        "alt": args.alt,
        "w": width,
        "h": height,
        "sha256": hashlib.sha256(clean).hexdigest(),
    }
    # The build record keeps the origin. It is not part of the distributed HTML.
    build_record = dict(asset, source=args.source, encodedBytes=size)
    result = {"asset": asset, "dataUri": uri, "buildRecord": build_record}

    if not args.apply:
        print(json.dumps({"dryRun": True, "asset": asset, "encodedBytes": size}, ensure_ascii=False, indent=2))
        print("\nRe-run with --apply to write the asset.", file=sys.stderr)
        return 0

    if args.out:
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
