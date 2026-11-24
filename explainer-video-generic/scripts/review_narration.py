#!/usr/bin/env python3
"""Pronunciation review for synthesized narration.

  python review_narration.py --work narr [--asr auto|whisper|none] [--transcripts DIR] [--readings extra.tsv]
                             [--out narr/review.md] [--listen-wav narr/listen.wav]

What it does
1. Picks the words a TTS voice is most likely to misread in each line: Latin words/acronyms, numbers with counters, and
   context-dependent kanji (assets/risky.<lang>.tsv, ja only).
2. Optional ASR check of the per-line audio. The transcript is compared WORD BY WORD: the expected form of each risky word
   must appear. Do not diff whole sentences (kanji/kana variants and dropped long vowels produce mostly false alarms).
   ASR back-transcribes what it hears, so a misread usually shows up as a different word
   (e.g. the TTS says "nin" for "人" and the transcript says "忍"). Any ASR works:
     --asr whisper       OpenAI Whisper if installed (an example, not a requirement)
     --transcripts DIR   plain-text files DIR/<scene>_<idx>.txt (e.g. s2_01.txt) from any other ASR
     --asr none          skip the ASR check
3. Writes a report and, with --listen-wav, one short WAV of only the lines that deserve a human listen.
An ASR pass is a screen, not proof (ASR can also "correct" a misreading): listen to the flagged and risky lines.
"""
import argparse, json, os, re, subprocess, sys, unicodedata, wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import SKILL, setup_stdio, ffmpeg_or_exit  # noqa: E402
from narration import load_readings  # noqa: E402

setup_stdio()
PUNCT = re.compile(r'[\s、。，．,.!?！？「」『』（）()・:：;；/／\-–—〜~"\']+')
KANJI_NUM = {'〇': 0, '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}


def hira(s):
    return ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in s)


def norm(s):
    return hira(PUNCT.sub('', unicodedata.normalize('NFKC', s).lower()))


def kanji_to_int(s):
    n, cur = 0, 0
    for c in s:
        if c in KANJI_NUM:
            cur = KANJI_NUM[c]
        elif c in '十百千':
            n += (cur or 1) * {'十': 10, '百': 100, '千': 1000}[c]; cur = 0
    return n + cur


def number_forms(digits):
    """Accepted spellings of a number in a transcript: digits (with or without separators)."""
    return {digits.replace(',', '')}


def load_risky(lang):
    p = os.path.join(SKILL, 'assets', f'risky.{lang[:2]}.tsv')
    out = []
    if os.path.exists(p):
        for ln in open(p, encoding='utf-8-sig'):
            ln = ln.rstrip('\r\n')
            if ln.strip() and not ln.startswith('#') and '\t' in ln:
                rx, note = ln.split('\t', 1)
                out.append((re.compile(rx), note.strip()))
    return out


def risky_tokens(text, readings, risky, lang):
    """-> list of (kind, written, accepted_forms, note)."""
    t = unicodedata.normalize('NFKC', text)
    rd = {unicodedata.normalize('NFKC', a).lower(): b for a, b in readings}
    toks = []
    # registered Latin phrases first (e.g. "NAT Gateway"), so their words are not checked one by one
    for key in sorted((k for k in rd if re.match(r'^[a-z0-9 .+\-]*[a-z]', k) and ' ' in k), key=len, reverse=True):
        m = re.search(r'(?<![A-Za-z0-9])' + re.escape(key) + r'(?![A-Za-z0-9])', t, re.I)
        if m:
            toks.append(('latin', m.group(0), {norm(key), norm(rd[key])}, 'reading: ' + rd[key]))
            t = t[:m.start()] + ' ' * (m.end() - m.start()) + t[m.end():]
    for w in dict.fromkeys(re.findall(r'[A-Za-z][A-Za-z0-9.+\-]*', t)):
        forms = {norm(w)}
        note = 'no reading registered' if w.lower() not in rd else 'reading: ' + rd[w.lower()]
        if w.lower() in rd:
            forms.add(norm(rd[w.lower()]))
        # without a registered reading the ASR may write the word in katakana, so absence proves nothing: listen only
        toks.append(('latin' if w.lower() in rd else 'latin?', w, forms, note))
    for m in dict.fromkeys(re.findall(r'\d[\d,.]*[^\s\d、。,.]{0,2}', t)):
        digits = re.match(r'\d[\d,.]*', m).group(0)
        toks.append(('number', m, number_forms(digits), 'number/counter'))
    for rx, note in risky:
        for m in rx.finditer(t):
            toks.append(('kanji', m.group(0), {norm(m.group(0))}, note))
    return toks


def heard_has(heard_norm, forms, kind):
    if any(f and f in heard_norm for f in forms):
        return True
    if kind == 'number':  # also accept kanji numerals (三つ for 3つ)
        digits = next(iter(forms))
        return any(kanji_to_int(k) == int(digits) for k in re.findall(r'[〇零一二三四五六七八九十百千]+', heard_norm) if digits.isdigit())
    return False


class Asr:
    def __init__(self, mode, model, transcripts):
        self.transcripts, self.model_name, self.m, self.name = transcripts, model, None, 'none'
        if transcripts:
            self.name = 'transcripts'
        elif mode in ('auto', 'whisper'):
            try:
                import whisper
                self.m, self.name = whisper.load_model(model), f'whisper-{model}'
            except Exception as e:
                if mode == 'whisper':
                    sys.exit(f'--asr whisper requested but whisper is not available ({e}). Use --transcripts DIR or --asr none.')

    def hear(self, wav, stem, lang):
        if self.transcripts:
            p = os.path.join(self.transcripts, stem + '.txt')
            return open(p, encoding='utf-8').read() if os.path.exists(p) else None
        if self.m:
            import numpy as np
            raw = subprocess.run([ffmpeg_or_exit(), '-v', 'error', '-i', wav, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], check=True, capture_output=True).stdout
            x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
            return self.m.transcribe(x, language=lang[:2], fp16=False, temperature=0, condition_on_previous_text=False)['text']
        return None


def write_listen_wav(files, out, gap=0.8):
    params, chunks = None, []
    for f in files:
        with wave.open(f, 'rb') as w:
            p = (w.getnchannels(), w.getsampwidth(), w.getframerate())
            params = params or p
            if p != params:
                continue
            chunks.append(w.readframes(w.getnframes()))
    if not chunks:
        return False
    silence = b'\x00' * (int(gap * params[2]) * params[0] * params[1])
    with wave.open(out, 'wb') as w:
        w.setnchannels(params[0]); w.setsampwidth(params[1]); w.setframerate(params[2])
        w.writeframes(silence.join(chunks))
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--work', required=True); ap.add_argument('--asr', default='auto', choices=['auto', 'whisper', 'none'])
    ap.add_argument('--model', default='small'); ap.add_argument('--transcripts'); ap.add_argument('--readings', nargs='*')
    ap.add_argument('--out'); ap.add_argument('--listen-wav')
    a = ap.parse_args()
    man = json.load(open(os.path.join(a.work, 'manifest.json'), encoding='utf-8'))
    lang = man.get('lang', 'en')
    lines = json.load(open(os.path.join(a.work, 'lines.json'), encoding='utf-8'))
    for p in a.readings or []:
        if not os.path.exists(p):
            print(f'WARNING --readings file not found (ignored): {p}')
    readings = load_readings([os.path.join(SKILL, 'assets', f'readings.{lang[:2]}.tsv')] + (a.readings or []))
    risky = load_risky(lang)
    asr = Asr('none' if a.asr == 'none' else a.asr, a.model, a.transcripts)
    rows, listen = [], []
    for ln in lines:
        stem = f"{ln['scene']}_{ln['idx']:02d}"
        wav = os.path.join(a.work, 'wav', stem + '.wav')
        toks = risky_tokens(ln['text'], readings, risky, lang)
        heard = asr.hear(wav, stem, lang) if os.path.exists(wav) else None
        missing = []
        if heard is not None:
            hn = norm(heard)
            missing = [t for t in toks if t[0] != 'latin?' and not heard_has(hn, t[2], t[0])]
        verdict = 'FLAG' if missing else ('ok' if not toks else ('listen' if heard is None or any(t[0] in ('latin?', 'number') for t in toks) else 'ok'))
        if verdict != 'ok':
            listen.append(wav)
        rows.append((ln, toks, missing, heard, verdict))
    n_flag = sum(r[4] == 'FLAG' for r in rows)
    rep = ['# Narration pronunciation review', '',
           f'ASR: {asr.name}. FLAG = an expected word was not heard (a misreading, an ASR error, or a dropped word): listen to it. '
           '"listen" = the line was not ASR-checked, or has words ASR cannot verify (Latin words without a registered reading, numbers). "ok" = no risky words, or all were heard. This is a screen, not proof.', '',
           '| # | line | script | risky words | missing in transcript | heard | verdict |', '|---|---|---|---|---|---|---|']
    for i, (ln, toks, missing, heard, v) in enumerate(rows, 1):
        rep.append(f"| {i} | {ln['key']} | {ln['text']} | {'; '.join(f'{t[1]} ({t[3]})' for t in toks) or '-'} | {'; '.join(t[1] for t in missing) or '-'} | {(heard or '-').strip()} | {v} |")
    rep += ['', f'FLAG: {n_flag} / listen: {sum(r[4] == "listen" for r in rows)} / ok: {sum(r[4] == "ok" for r in rows)} (of {len(rows)} lines)']
    out = a.out or os.path.join(a.work, 'review.md')
    open(out, 'w', encoding='utf-8', newline='\n').write('\n'.join(rep) + '\n')
    for r in rows:
        if r[4] != 'ok':
            print(f"{r[0]['key']:8s} {r[4]:6s} {'missing: ' + ', '.join(t[1] for t in r[2]) if r[2] else ''}")
    print(f'report: {out}  (FLAG {n_flag}, {len(listen)} line(s) to listen to)')
    if a.listen_wav:
        print('listen wav: ' + (a.listen_wav if write_listen_wav(listen, a.listen_wav) else 'not written (no audio found)'))


if __name__ == '__main__':
    main()
