#!/usr/bin/env python3
"""Mix narration (per-line WAVs) and background music into a silent MP4, and write an SRT subtitle file.

  python mix.py --video video.mp4 --placement narr/placement.json --out "Title_20261124.mp4"
                [--bgm auto|none|music.mp3] [--duck-db 8] [--bgm-db -30] [--lufs -16] [--split-mb 190] [--lang en]

- Narration is placed at the start times in placement.json (written by narration.py fit).
- BGM defaults to a small synthesized pad (no copyright concerns). Pass a file to loop/cut it instead (you must hold the rights).
- BGM ducks under the narration; the final mix is normalized to -16 LUFS / -1.5 dBTP.
- The video stream is copied (no re-encode). Audio is AAC 48 kHz stereo 192 kbps. faststart.
- Subtitles use the on-screen wording (before readings) and the real audio timing.
"""
import argparse, json, os, re, subprocess, sys, wave
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import setup_stdio, ffmpeg_or_exit, media_info  # noqa: E402

setup_stdio()
SR = 48000


def read_wav(path):
    with wave.open(path, 'rb') as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float32) / 32768
        if w.getnchannels() == 2:
            x = x.reshape(-1, 2).mean(axis=1)
        if w.getframerate() != SR:
            raise SystemExit(f'{path}: {w.getframerate()} Hz (expected 48 kHz)')
    return x


def decode(path, ch=2):
    raw = subprocess.run([ffmpeg_or_exit(), '-v', 'error', '-i', path, '-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-'], check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, ch).copy()


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def synth_bgm(dur, seed=7):
    """Soft D-major I-V-vi-IV pad + light arpeggio + bass at 92 BPM. Deterministic."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR) + SR
    out = np.zeros((n, 2), np.float32)
    beat = 60 / 92
    bar = beat * 4
    chords = [[50, 54, 57, 62], [45, 49, 52, 57], [47, 50, 54, 59], [43, 47, 50, 55]]  # D A Bm G
    t_all = np.arange(n) / SR
    k = 0
    t0 = 0.0
    while t0 < dur + bar:
        ch = chords[k % 4]
        a, b = int(t0 * SR), min(n, int((t0 + bar * 2 + 1.2) * SR))
        if a >= n:
            break
        tt = t_all[a:b] - t0
        L = b - a
        env = np.minimum(1, tt / 1.2) * np.clip((bar * 2 + 1.2 - tt) / 1.2, 0, 1)
        pad = np.zeros(L, np.float32)
        for m in ch:
            f = midi_hz(m + 12)
            for det in (-0.0015, 0.0015):
                pad += np.sin(2 * np.pi * f * (1 + det) * tt) * 0.5 + 0.12 * np.sin(2 * np.pi * 2 * f * tt)
        pad *= env * 0.05
        out[a:b, 0] += pad * 0.9
        out[a:b, 1] += pad
        for j in range(4):  # bass, every 2 beats
            s = t0 + j * beat * 2
            ia, ib = int(s * SR), min(n, int((s + beat * 2) * SR))
            if ia >= n:
                break
            u = t_all[ia:ib] - s
            bass = np.sin(2 * np.pi * midi_hz(ch[0] - 12) * u) * np.exp(-u * 1.6) * 0.09
            out[ia:ib] += bass[:, None]
        arp = [ch[0] + 24, ch[2] + 12, ch[1] + 24, ch[3] + 12]
        for j in range(16):  # eighth-note e-piano style arpeggio
            s = t0 + j * beat / 2
            ia, ib = int(s * SR), min(n, int((s + 1.4) * SR))
            if ia >= n:
                break
            u = t_all[ia:ib] - s
            f = midi_hz(arp[j % 4])
            note = (np.sin(2 * np.pi * f * u) + 0.25 * np.sin(2 * np.pi * 2 * f * u) * np.exp(-u * 6)) * np.exp(-u * 3.2) * np.minimum(1, u / 0.008)
            g = 0.026 * (0.85 + 0.3 * rng.random())
            pan = 0.35 + 0.3 * ((j % 4) / 3)
            out[ia:ib, 0] += note * g * (1 - pan)
            out[ia:ib, 1] += note * g * pan
        t0 += bar * 2
        k += 1
    # soften: one-pole low-pass implemented as a truncated exponential kernel (fast, no scipy needed)
    alpha = 0.18
    kern = alpha * (1 - alpha) ** np.arange(80)
    for c in range(2):
        out[:, c] = np.convolve(out[:, c], kern)[:n].astype(np.float32)
    return out[:int(dur * SR)]


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-9)


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype('<i2').tobytes())


def srt_time(s):
    s = max(0.0, s)
    h, m = int(s // 3600), int(s // 60) % 60
    return f'{h:02d}:{m:02d}:{int(s) % 60:02d},{int(round((s - int(s)) * 1000)) % 1000:03d}'


def wrap_sub(text, lang, width=None):
    cjk = lang[:2] in ('ja', 'zh', 'ko')
    width = width or (24 if cjk else 46)
    if len(text) <= width:
        return text
    if cjk:
        cands = [m.end() for m in re.finditer(r'[、。！？，]', text) if 0 < m.end() < len(text)]
        ok = [c for c in cands if c <= width + 4 and len(text) - c <= width + 4]
        cut = min(ok, key=lambda c: abs(c - len(text) / 2)) if ok else min(len(text) // 2 + 1, width)
        return text[:cut] + '\n' + text[cut:]
    words = text.split()
    best, acc = len(words) // 2, 0
    half = len(text) / 2
    for i, w in enumerate(words):
        acc += len(w) + 1
        if acc >= half:
            best = i + 1
            break
    return ' '.join(words[:best]) + '\n' + ' '.join(words[best:])


def split_cues(text, lang, start, dur):
    """Split a long narration line into subtitle cues (<= 2 lines each), timed proportionally to length."""
    cjk = lang[:2] in ('ja', 'zh', 'ko')
    maxlen = 44 if cjk else 90
    if len(text) <= maxlen:
        return [(start, dur, text)]
    parts = [p for p in re.split(r'(?<=[。！？!?])|(?<=[.!?])\s+', text) if p and p.strip()]
    if any(len(p) > maxlen for p in parts):
        parts = [q for p in parts for q in ([p] if len(p) <= maxlen else [x for x in re.split(r'(?<=[、，,;:])\s*', p) if x])]
    sep = '' if cjk else ' '
    target = len(text) / max(1, -(-len(text) // maxlen))  # even split between clause boundaries
    chunks, cur = [], ''
    for p in parts:
        joined = (cur + sep + p) if cur else p
        if cur and (len(joined) > maxlen or abs(len(joined) - target) >= abs(len(cur) - target)):
            chunks.append(cur); cur = p
        else:
            cur = joined
    if cur:
        chunks.append(cur)
    total = sum(len(c) for c in chunks)
    out, t0 = [], start
    for c in chunks:
        d = dur * len(c) / total
        out.append((t0, d, c.strip())); t0 += d
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--video', required=True); ap.add_argument('--placement', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--bgm', default='auto'); ap.add_argument('--bgm-db', type=float, default=-30.0, help='BGM level where there is no narration (RMS dBFS)')
    ap.add_argument('--duck-db', type=float, default=8.0, help='extra BGM reduction under narration (dB)'); ap.add_argument('--voice-db', type=float, default=-20.0)
    ap.add_argument('--lufs', type=float, default=-16.0); ap.add_argument('--srt'); ap.add_argument('--split-mb', type=float, default=0, help='split the result into parts if larger than this many MB')
    ap.add_argument('--lang', help='subtitle wrapping language (default: from narr/manifest.json, else en)')
    a = ap.parse_args()
    ffmpeg_or_exit()

    lang = a.lang
    if not lang:
        mp = os.path.join(os.path.dirname(os.path.abspath(a.placement)), 'manifest.json')
        lang = json.load(open(mp, encoding='utf-8')).get('lang', 'en') if os.path.exists(mp) else 'en'

    vdur = media_info(a.video)['duration']
    pl = json.load(open(a.placement, encoding='utf-8'))
    n = int(vdur * SR)
    voice = np.zeros(n, np.float32)
    mask = np.zeros(n, np.float32)
    over = []
    for ln in pl['lines']:
        x = read_wav(ln['file'])
        s = int(ln['start'] * SR)
        e = min(n, s + len(x))
        if s >= n:
            over.append(ln['key']); continue
        voice[s:e] += x[:e - s]
        mask[max(0, s - int(0.12 * SR)):min(n, e + int(0.25 * SR))] = 1
        if s + len(x) > n:
            over.append(ln['key'])
    if over:
        print('WARNING lines that do not fit in the video: ' + ', '.join(over) + ' (check the HTML durations and re-render the MP4)')
    speech = voice[mask > 0]
    if len(speech):
        voice *= 10 ** ((a.voice_db - rms_db(speech[np.abs(speech) > 1e-4])) / 20)

    if a.bgm == 'none':
        bgm = np.zeros((n, 2), np.float32)
    else:
        if a.bgm == 'auto':
            bgm = synth_bgm(vdur)
        else:
            b = decode(a.bgm)
            reps = int(np.ceil(n / len(b))) if len(b) else 1
            bgm = np.tile(b, (reps, 1))[:n]
        bgm = bgm[:n]
        if len(bgm) < n:
            bgm = np.vstack([bgm, np.zeros((n - len(bgm), 2), np.float32)])
        bgm *= 10 ** ((a.bgm_db - rms_db(bgm)) / 20)
        # ducking: down in 0.12 s, back up in 0.9 s, as piecewise-linear ramps
        g_low = 10 ** (-a.duck_db / 20)
        target = np.where(mask > 0, g_low, 1.0).astype(np.float32)
        env = np.empty_like(target)
        down, up = 1 / (0.12 * SR), 1 / (0.9 * SR)
        g = 1.0
        idx = np.flatnonzero(np.diff(target) != 0) + 1
        bounds = np.concatenate([[0], idx, [n]])
        for i in range(len(bounds) - 1):
            s, e = bounds[i], bounds[i + 1]
            tg = target[s]
            step = down if tg < g else up
            L = e - s
            ramp = g + np.sign(tg - g) * step * (1 - g_low) * np.arange(1, L + 1)
            ramp = np.minimum(ramp, tg) if tg > g else np.maximum(ramp, tg)
            env[s:e] = ramp
            g = float(ramp[-1]) if L else g
        fade_in = np.minimum(1, np.arange(n) / (2.0 * SR))
        fade_out = np.clip((n - np.arange(n)) / (4.0 * SR), 0, 1)
        bgm *= (env * fade_in * fade_out)[:, None]

    mix = bgm + voice[:, None]
    tmp = os.path.splitext(a.out)[0] + '.__mix.wav'
    write_wav(tmp, mix * 0.7)
    af = f'loudnorm=I={a.lufs}:TP=-1.5:LRA=11,aresample={SR}'
    subprocess.run([ffmpeg_or_exit(), '-y', '-v', 'error', '-i', a.video, '-i', tmp, '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy',
                    '-af', af, '-c:a', 'aac', '-b:a', '192k', '-ar', str(SR), '-ac', '2', '-t', f'{vdur:.3f}', '-movflags', '+faststart', a.out], check=True)
    os.remove(tmp)

    srt = a.srt or os.path.splitext(a.out)[0] + '.srt'
    L = pl['lines']
    cues = []
    for i, ln in enumerate(L):
        end_limit = (L[i + 1]['start'] - 0.05) if i + 1 < len(L) else vdur
        span = max(0.5, min(ln['dur'] + 0.25, end_limit - ln['start']))
        cues += split_cues(ln['text'], lang, ln['start'], span)
    with open(srt, 'w', encoding='utf-8', newline='\r\n') as f:
        for i, (s0, d0, tx) in enumerate(cues):
            f.write(f"{i + 1}\n{srt_time(s0)} --> {srt_time(min(s0 + d0, vdur))}\n{wrap_sub(tx, lang)}\n\n")

    info = media_info(a.out)
    print(f"Wrote MP4 with audio: {a.out} ({info.get('duration', 0):.1f} s, {info.get('size_mb', 0):.1f} MB)")
    print(f'Subtitles: {srt}')
    print(f"video: {info.get('vcodec')} {info.get('width')}x{info.get('height')} {info.get('fps')}fps | audio: {info.get('acodec')} {info.get('sample_rate')} Hz {info.get('channels')}")
    if a.split_mb and info.get('size_mb', 0) > a.split_mb:
        parts = int(np.ceil(info['size_mb'] / a.split_mb))
        seg = vdur / parts
        base = os.path.splitext(a.out)[0]
        subprocess.run([ffmpeg_or_exit(), '-y', '-v', 'error', '-i', a.out, '-c', 'copy', '-map', '0', '-f', 'segment', '-segment_time', f'{seg:.2f}',
                        '-reset_timestamps', '1', '-movflags', '+faststart', f'{base}_part%02d.mp4'], check=True)
        print(f'Larger than {a.split_mb:.0f} MB, split into {parts} parts: {base}_part01.mp4 ...')


if __name__ == '__main__':
    main()
