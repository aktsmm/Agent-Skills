#!/usr/bin/env python3
"""Check that the toolchain for the explainer-video skill is ready, and say how to fix what is missing.

  python check_env.py [--lang ja] [--backend edge]

Checks: Python deps (numpy, edge-tts, Pillow optional), ffmpeg + an H.264 encoder, node, Playwright, a Chromium-family browser,
and (for CJK languages) a CJK-capable system font. Exit code 0 when the required pieces are present.
"""
import argparse, glob, json, os, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import HERE, setup_stdio, find_ffmpeg, encoders  # noqa: E402

setup_stdio()
ok_all = True


def row(name, ok, detail, fix='', required=True):
    global ok_all
    mark = 'OK  ' if ok else ('MISS' if required else 'opt ')
    print(f'[{mark}] {name:22s} {detail}')
    if not ok and fix:
        print(f'       fix: {fix}')
    if not ok and required:
        ok_all = False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--lang', default='en'); ap.add_argument('--backend', default='edge')
    a = ap.parse_args()

    row('python', sys.version_info >= (3, 9), sys.version.split()[0], 'install Python 3.9+')
    try:
        import numpy
        row('numpy', True, numpy.__version__)
    except ImportError:
        row('numpy', False, 'not installed', 'pip install numpy')
    if a.backend == 'edge':
        try:
            import edge_tts  # noqa: F401
            row('edge-tts', True, 'installed (sends text to Microsoft\'s online Edge TTS service)')
        except ImportError:
            row('edge-tts', False, 'not installed', 'pip install edge-tts')
    try:
        import PIL
        row('Pillow', True, PIL.__version__, required=False)
    except ImportError:
        row('Pillow', False, 'only needed to shrink PNG icons', 'pip install pillow', required=False)

    ff = find_ffmpeg()
    row('ffmpeg', bool(ff), ff or 'not found', 'winget install Gyan.FFmpeg | brew install ffmpeg | apt install ffmpeg | pip install imageio-ffmpeg')
    if ff:
        enc = encoders()
        h264 = [e for e in ('libx264', 'libopenh264', 'h264_nvenc', 'h264_qsv', 'h264_amf', 'h264_videotoolbox', 'h264_mf') if e in enc]
        row('H.264 encoder', bool(h264), ', '.join(h264) or 'none', 'use an ffmpeg build with libx264 or libopenh264')

    node = shutil.which('node')
    row('node', bool(node), node or 'not found', 'install Node.js 18+ (https://nodejs.org)')
    if node:
        r = subprocess.run(['node', os.path.join(HERE, 'env_probe.mjs')], capture_output=True, text=True)
        try:
            pr = json.loads(r.stdout.strip().splitlines()[-1])
        except Exception:
            pr = {'playwright': False, 'browser': False, 'detail': (r.stderr or r.stdout)[:160]}
        row('playwright', pr['playwright'], 'found' if pr['playwright'] else pr['detail'], 'npm i -g playwright   (or: npm i playwright in the working folder)')
        if pr['playwright']:
            row('headless browser', pr['browser'], 'launches' if pr['browser'] else pr['detail'], 'npx playwright install chromium   (or set XV_CHROME to a Chrome/Edge executable)')

    if a.lang[:2] in ('ja', 'zh', 'ko'):
        cands = ['/usr/share/fonts/**/*CJK*', '/usr/share/fonts/**/*Noto*Sans*CJK*', r'C:\Windows\Fonts\YuGoth*', r'C:\Windows\Fonts\meiryo*', r'C:\Windows\Fonts\msgothic*',
                 r'C:\Windows\Fonts\msyh*', r'C:\Windows\Fonts\malgun*', '/System/Library/Fonts/*Hiragino*', '/System/Library/Fonts/PingFang*', '/System/Library/Fonts/AppleSDGothic*']
        found = [p for c in cands for p in glob.glob(c, recursive=True)]
        row('CJK font', bool(found), found[0] if found else 'none found', 'install Noto Sans CJK (apt install fonts-noto-cjk) so captions render', required=False)

    print('\nREADY' if ok_all else '\nNOT READY: fix the MISS items above')
    sys.exit(0 if ok_all else 1)


if __name__ == '__main__':
    main()
