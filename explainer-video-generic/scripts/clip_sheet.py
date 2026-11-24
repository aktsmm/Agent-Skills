#!/usr/bin/env python3
"""Contact sheets and a clip inventory for demo recordings (pattern C).

  python clip_sheet.py clips/*.mp4 --out sheets [--max 24] [--cols 4] [--warn-mb 200]

- Extracts up to 24 evenly spaced frames per clip into one PNG with timestamps (open it with the image viewer tool to read the clip).
- Writes sheets/clips.json with duration, resolution, size. Warns when a clip exceeds --warn-mb (some agents/uploaders cap attachment size).
"""
import argparse, glob, json, math, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import setup_stdio, ffmpeg_or_exit, media_info  # noqa: E402

setup_stdio()
FONT_CANDIDATES = [
    r'C:\Windows\Fonts\segoeui.ttf', r'C:\Windows\Fonts\arial.ttf', '/System/Library/Fonts/Supplemental/Arial.ttf', '/Library/Fonts/Arial.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
]
FONT = next((f for f in FONT_CANDIDATES if os.path.exists(f)), '')


def ffilter_path(p):
    """Escape a path for an ffmpeg filter argument (Windows drive colon and backslashes)."""
    return p.replace('\\', '/').replace(':', r'\:')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('clips', nargs='+'); ap.add_argument('--out', default='sheets'); ap.add_argument('--max', type=int, default=24); ap.add_argument('--cols', type=int, default=4)
    ap.add_argument('--warn-mb', type=float, default=200)
    a = ap.parse_args()
    ffmpeg = ffmpeg_or_exit()
    os.makedirs(a.out, exist_ok=True)
    files = sorted({f for c in a.clips for f in glob.glob(c)})
    info = []
    for f in files:
        i = media_info(f)
        dur = i.get('duration') or 0
        n = max(1, min(a.max, int(dur // 2) or 1))
        step = dur / n
        rows = math.ceil(n / a.cols)
        dt = f"drawtext=fontfile='{ffilter_path(FONT)}':text='%{{pts\\:hms}}':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6," if FONT else ''
        vf = f"{dt}fps=1/{step:.3f},scale=480:-2,tile={a.cols}x{rows}:padding=6:color=white"
        out = os.path.join(a.out, os.path.splitext(os.path.basename(f))[0] + '_sheet.png')
        subprocess.run([ffmpeg, '-y', '-v', 'error', '-i', f, '-vf', vf, '-frames:v', '1', out], check=True)
        i['sheet'] = out; i['interval_sec'] = round(step, 2)
        info.append(i)
        warn = f"  <- over {a.warn_mb:.0f} MB (consider splitting)" if i.get('size_mb', 0) >= a.warn_mb else ''
        print(f"{os.path.basename(f)}: {dur:.1f} s, {i.get('width')}x{i.get('height')}, {i.get('size_mb')} MB, {n} frames (every {step:.1f} s) -> {out}{warn}")
    json.dump(info, open(os.path.join(a.out, 'clips.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
