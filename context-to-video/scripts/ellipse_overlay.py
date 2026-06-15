"""Apply circular (elliptical) mask + accent ring to the avatar overlay
and composite onto the base slide video.

Usage:
    python ellipse_overlay.py --project D:\path\to\project
    python ellipse_overlay.py --project ... --size 320 --margin 56 --ring 0xFF6B6B
"""
from __future__ import annotations
import argparse
import os
import subprocess
from pathlib import Path


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("0x").lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, type=Path)
    ap.add_argument("--size", type=int, default=360, help="アバター直径 px")
    ap.add_argument("--margin", type=int, default=48)
    ap.add_argument("--ring", default="0x38BDF8", help="リング色 (hex)。例: 0xFF6B6B")
    ap.add_argument("--ffmpeg-dir", default=None)
    args = ap.parse_args()

    project: Path = args.project
    base = project / "output" / "final.mp4"
    avatar = project / "avatar" / "clips" / "_avatar_full.mp4"
    out = project / "output" / "final_with_avatar_ellipse.mp4"

    for p in (base, avatar):
        if not p.exists():
            raise SystemExit(f"missing: {p}")

    if args.ffmpeg_dir:
        os.environ["PATH"] = args.ffmpeg_dir + os.pathsep + os.environ["PATH"]

    S = args.size
    M = args.margin
    cx = S / 2
    r, g, b = hex_to_rgb(args.ring)

    filt = (
        f"[1:v]"
        "crop=min(iw\\,ih):min(iw\\,ih),"
        f"scale={S}:{S},"
        "format=yuva420p,"
        # alpha = inside ellipse
        f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
        f"a='if(lte(hypot((X-{cx})/{cx},(Y-{cx})/{cx}),1),255,0)',"
        # accent ring
        f"geq=r='if(between(hypot((X-{cx})/{cx},(Y-{cx})/{cx}),0.94,1),{r},r(X,Y))':"
        f"g='if(between(hypot((X-{cx})/{cx},(Y-{cx})/{cx}),0.94,1),{g},g(X,Y))':"
        f"b='if(between(hypot((X-{cx})/{cx},(Y-{cx})/{cx}),0.94,1),{b},b(X,Y))':"
        f"a='if(lte(hypot((X-{cx})/{cx},(Y-{cx})/{cx}),1),255,0)'"
        "[av];"
        f"[0:v][av]overlay=W-w-{M}:H-h-{M}:shortest=1[v]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(base),
        "-i", str(avatar),
        "-filter_complex", filt,
        "-map", "[v]", "-map", "0:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "copy",
        str(out),
    ]
    print(">>", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"[ok] wrote {out}")


if __name__ == "__main__":
    main()
