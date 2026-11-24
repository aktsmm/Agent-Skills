"""Upbeat synthesized BGM loops (no samples, no copyright concerns). Used by mix.py: --bgm pop | tech.

  pop : bright, 120 BPM, C major (I-V-vi-IV), claps and hats, plucked arpeggio
  tech: driving, 128 BPM, A minor, four-on-the-floor kick, sidechain-style pumping pad
Standalone preview: python bgm_styles.py <style> <out.wav>
"""
import sys
import wave

import numpy as np

SR = 48000
STYLES = {
    'pop': dict(bpm=120, chords=[[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]], roots=[36, 43, 45, 41], kind='A'),
    'tech': dict(bpm=128, chords=[[57, 60, 64], [53, 57, 60], [60, 64, 67], [55, 59, 62]], roots=[33, 29, 36, 31], kind='B'),
}
BARS = 8


def _freq(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _t(n):
    return np.arange(n) / SR


def _saw(f, n):
    return 2 * ((_t(n) * f) % 1.0) - 1


def _tri(f, n):
    return 2 * np.abs(2 * ((_t(n) * f) % 1.0) - 1) - 1


def _sine(f, n):
    return np.sin(2 * np.pi * f * _t(n))


def _lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode='same')


def _build(style, seed=11):
    rng = np.random.default_rng(seed)
    cfg = STYLES[style]
    bpm, chords, roots, kind = cfg['bpm'], cfg['chords'], cfg['roots'], cfg['kind']

    def kick():
        n = int(0.28 * SR); t = _t(n)
        return np.sin(np.cumsum(2 * np.pi * (48 + 110 * np.exp(-t * 28)) / SR)) * np.exp(-t * 9) * 0.95

    def hat(open_=False):
        n = int((0.16 if open_ else 0.05) * SR); t = _t(n)
        return np.diff(rng.standard_normal(n + 1)) * np.exp(-t * (22 if open_ else 70)) * 0.35

    def clap():
        n = int(0.2 * SR); t = _t(n)
        burst = np.exp(-t * 28) + 0.6 * np.exp(-((t - 0.012) ** 2) * 9000)
        return _lowpass(np.diff(rng.standard_normal(n + 1)), 3) * burst * 0.5

    def bass(m, dur):
        n = int(dur * SR); t = _t(n); f = _freq(m)
        return (0.7 * _sine(f, n) + 0.35 * _lowpass(_saw(f, n), 24)) * np.minimum(1, t / 0.005) * np.exp(-t * 4.5)

    def pluck(m, dur=0.22):
        n = int(dur * SR); t = _t(n); f = _freq(m)
        return (0.6 * _tri(f, n) + 0.3 * _sine(2 * f, n)) * np.minimum(1, t / 0.003) * np.exp(-t * 14)

    def pad(ms, dur):
        n = int(dur * SR); t = _t(n)
        e = np.minimum(1, t / 0.25) * np.minimum(1, (dur - t) / 0.15)
        return sum(_tri(_freq(m), n) + 0.5 * _tri(_freq(m) * 1.004, n) for m in ms) * e / len(ms)

    beat = 60.0 / bpm
    bar = 4 * beat
    total = int((BARS * bar + 0.5) * SR)
    L = np.zeros(total, np.float32); R = np.zeros(total, np.float32)

    def put(sig, at, gain=1.0, pan=0.0):
        a = int(at * SR); b = min(total, a + len(sig))
        if a >= total:
            return
        s = sig[: b - a] * gain
        L[a:b] += s * (1 - max(0, pan)); R[a:b] += s * (1 + min(0, pan))

    kck, ht, hto, clp = kick(), hat(), hat(True), clap()
    for bi in range(BARS):
        ch, root, t0 = chords[bi % 4], roots[bi % 4], bi * bar
        p = pad(ch, bar + 0.1)
        if kind == 'B':  # pumping pad
            curve = np.ones(len(p), np.float32)
            for k in range(4):
                s = int(k * beat * SR); m = min(len(p), s + int(beat * SR))
                curve[s:m] = 1 - 0.65 * np.exp(-(np.arange(m - s) / SR / beat) * 7)
            p = p * curve
        put(p, t0, 0.10)
        for k in range(4):
            tb = t0 + k * beat
            if kind == 'A':
                if k in (0, 2):
                    put(kck, tb, 0.9)
                if k in (1, 3):
                    put(clp, tb, 0.7)
                put(ht, tb, 0.7); put(ht, tb + beat / 2, 0.5)
                put(bass(root, beat / 2 * 0.95), tb, 0.55); put(bass(root + (12 if k % 2 else 0), beat / 2 * 0.95), tb + beat / 2, 0.45)
                for s in range(4):
                    put(pluck(ch[[0, 1, 2, 1][s]] + 12), tb + s * beat / 4, 0.22, pan=0.4 if s % 2 else -0.4)
            else:
                put(kck, tb, 0.95)
                put(hto, tb + beat / 2, 0.8)
                if k in (1, 3):
                    put(clp, tb, 0.7)
                if k % 2 == 1:
                    put(ht, tb + beat / 4, 0.4); put(ht, tb + 3 * beat / 4, 0.4)
                put(bass(root, beat / 2 * 0.9), tb + beat / 2, 0.6)
                for s in range(4):
                    put(pluck(ch[[0, 2, 1, 2][s]] + 12, 0.18), tb + s * beat / 4, 0.2, pan=0.5 if s % 2 else -0.5)
    one = int(BARS * bar * SR)
    Lc, Rc = L[:one].copy(), R[:one].copy()
    tail = L[one: one + 4000], R[one: one + 4000]  # fold the tail into the start so the loop is seamless
    Lc[: len(tail[0])] += tail[0]; Rc[: len(tail[1])] += tail[1]
    return np.stack([Lc, Rc], 1).astype(np.float32)


def loop(style):
    """One seamless stereo loop (float32, shape (n, 2), 48 kHz) of the given style."""
    if style not in STYLES:
        raise SystemExit(f'Unknown BGM style {style!r}; use one of: {", ".join(STYLES)}')
    return _build(style)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    x = np.tile(loop(sys.argv[1]), (2, 1))
    x = x / np.abs(x).max() * 0.8
    with wave.open(sys.argv[2], 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype('<i2').tobytes())
    print(sys.argv[2], round(len(x) / SR, 1), 's')
