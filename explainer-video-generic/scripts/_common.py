"""Shared helpers for the explainer-video scripts (stdlib only, plus optional imageio_ffmpeg)."""
import os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)


def setup_stdio():
    """Windows consoles default to a legacy code page; force UTF-8 so non-ASCII text never crashes a script."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass


def find_ffmpeg():
    """FFMPEG env var > ffmpeg on PATH > imageio_ffmpeg's bundled binary. Returns a path or None."""
    p = os.environ.get('FFMPEG')
    if p and os.path.exists(p):
        return p
    p = shutil.which('ffmpeg')
    if p:
        return p
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def ffmpeg_or_exit():
    p = find_ffmpeg()
    if not p:
        sys.exit('ffmpeg not found. Install it (winget install Gyan.FFmpeg / brew install ffmpeg / apt install ffmpeg), '
                 'or `pip install imageio-ffmpeg`, or set the FFMPEG environment variable to the binary path.')
    os.environ['FFMPEG'] = p  # child processes (node render.mjs) reuse the same binary
    return p


def run_ffmpeg(args, **kw):
    return subprocess.run([ffmpeg_or_exit()] + args, **kw)


def encoders():
    out = subprocess.run([ffmpeg_or_exit(), '-hide_banner', '-encoders'], capture_output=True, text=True).stdout
    return set(re.findall(r'^\s*V\S+\s+(\S+)', out, re.M))


def media_info(path):
    """ffprobe-free probe: parse `ffmpeg -i` output. Returns duration (s), video size/fps and audio info when present."""
    err = subprocess.run([ffmpeg_or_exit(), '-hide_banner', '-i', path], capture_output=True, text=True).stderr
    info = {'file': path}
    m = re.search(r'Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)', err)
    if m:
        info['duration'] = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    v = re.search(r'Video:\s*([^\s,]+).*?,\s*(\d{2,5})x(\d{2,5})', err)
    if v:
        info.update(vcodec=v[1], width=int(v[2]), height=int(v[3]))
        f = re.search(r'([\d.]+)\s*fps', err)
        if f:
            info['fps'] = float(f[1])
    a = re.search(r'Audio:[^\n]*', err)
    if a:
        line = a.group(0)
        info['acodec'] = line.split()[1].rstrip(',')
        hz = re.search(r'(\d+)\s*Hz', line)
        ch = re.search(r'Hz,\s*([^,\n]+)', line)
        if hz:
            info['sample_rate'] = int(hz[1])
        if ch:
            info['channels'] = ch[1].strip()
    if os.path.exists(path):
        info['size_mb'] = round(os.path.getsize(path) / 1048576, 2)
    return info
