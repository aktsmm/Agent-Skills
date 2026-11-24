#!/usr/bin/env python3
"""Narration pipeline: prepare -> synth (or split) -> fit.

  prepare : read the narration lines from the video HTML, apply pronunciation readings, write the TTS script
      python narration.py prepare --html video.html --work narr [--lang en] [--readings extra.tsv] [--voice NAME]
  synth   : synthesize EVERY LINE separately with a TTS backend (parallel, cached) -> narr/wav/*.wav + audio_lines.json
      python narration.py synth --work narr --backend edge|openai|azure|voicevox|command [--voice NAME] [--rate +0%] [--jobs 3]
  split   : alternative for audio produced outside this script: cut batch MP3s (one file per batch, one line per
            utterance, silence between lines) into per-line WAVs by detecting silences
      python narration.py split --work narr --audio batch01=/path/a.mp3 [batch02=...]
  fit     : write the real line durations into the HTML (FIT block) so scenes and captions match the audio
      python narration.py fit --html video.html --work narr [--gap 0.7 --tail 1.3] [--keep]

Needs: python 3.9+, numpy, ffmpeg (or imageio-ffmpeg), node (render.mjs reads the HTML timing).
Backends: edge needs `pip install edge-tts`; openai needs OPENAI_API_KEY; azure needs AZURE_SPEECH_KEY + AZURE_SPEECH_REGION;
voicevox needs a running engine (VOICEVOX_URL, default http://127.0.0.1:50021). See references/tts-backends.md.
"""
import argparse, concurrent.futures as cf, hashlib, json, os, re, subprocess, sys, tempfile, time, unicodedata, urllib.error, urllib.request, wave
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import HERE, SKILL, setup_stdio, ffmpeg_or_exit, run_ffmpeg  # noqa: E402

setup_stdio()
SR = 48000
CJK_LANGS = ('ja', 'zh', 'ko')
SEC_PER_CHAR = 0.13   # CJK, normal speed
SEC_PER_WORD = 0.40   # Latin scripts, normal speed
SEC_PER_LINE = 1.0    # pause between lines

DEFAULT_VOICES = {
    'edge': {'ja': 'ja-JP-NanamiNeural', 'en': 'en-US-AriaNeural', 'zh': 'zh-CN-XiaoxiaoNeural', 'ko': 'ko-KR-SunHiNeural',
             'es': 'es-ES-ElviraNeural', 'fr': 'fr-FR-DeniseNeural', 'de': 'de-DE-KatjaNeural', 'pt': 'pt-BR-FranciscaNeural', 'it': 'it-IT-ElsaNeural'},
    'openai': {'*': 'alloy'},
    'voicevox': {'*': '2'},
}
DEFAULT_VOICES['azure'] = DEFAULT_VOICES['edge']


def is_cjk(lang):
    return (lang or 'en').lower()[:2] in CJK_LANGS


def default_voice(backend, lang):
    d = DEFAULT_VOICES.get(backend, {})
    return d.get((lang or 'en').lower()[:2]) or d.get('*')


# ------------------------------------------------------------------ HTML timing via render.mjs
def html_timing(html, strip_fit=False):
    """Read the scene/line timing with render.mjs check. strip_fit=True reads the raw values, ignoring any FIT block."""
    ffmpeg_or_exit()
    src, tmp = html, None
    if strip_fit:
        s = open(html, encoding='utf-8').read()
        s2 = re.sub(r'/\*FIT-BEGIN\*/.*?/\*FIT-END\*/', '/*FIT-BEGIN*/const FIT = null;/*FIT-END*/', s, flags=re.S)
        tmp = os.path.join(os.path.dirname(os.path.abspath(html)), '.__xv_nofit.html')
        open(tmp, 'w', encoding='utf-8').write(s2)
        src = tmp
    out = os.path.join(os.path.dirname(os.path.abspath(html)), '.__xv_timing.json')
    try:
        r = subprocess.run(['node', os.path.join(HERE, 'render.mjs'), 'check', src, '--json', out], capture_output=True, text=True)
        if not os.path.exists(out):
            sys.exit('render.mjs check failed:\n' + (r.stdout + r.stderr)[-1500:])
        return json.load(open(out, encoding='utf-8'))
    finally:
        for f in (tmp, out):
            if f and os.path.exists(f):
                os.remove(f)


# ------------------------------------------------------------------ readings / text normalization
def load_readings(paths):
    pairs = []
    for p in paths:
        if not p or not os.path.exists(p):
            continue
        for ln in open(p, encoding='utf-8-sig'):
            ln = ln.rstrip('\r\n')
            if not ln.strip() or ln.lstrip().startswith('#') or '\t' not in ln:
                continue
            a, b = ln.split('\t', 1)
            pairs.append((a.strip(), b.strip()))
    # later files (per-project additions) win; longer surface forms are applied first
    seen, uniq = set(), []
    for a, b in reversed(pairs):
        if a not in seen:
            seen.add(a); uniq.append((a, b))
    return sorted(uniq, key=lambda x: -len(x[0]))


def to_tts(text, readings, lang):
    s = unicodedata.normalize('NFKC', text)

    def pad(m, b):
        # surround a replaced Latin word with spaces only where it touches other ASCII text (no stray pauses next to CJK)
        src = m.string
        l = src[m.start() - 1] if m.start() else ''
        r = src[m.end()] if m.end() < len(src) else ''
        return (' ' if l and l.isascii() and not l.isspace() else '') + b + (' ' if r and r.isascii() and not r.isspace() else '')

    for a, b in readings:
        if re.match(r'^[A-Za-z0-9 .+\-]+$', a):
            s = re.sub(r'(?<![A-Za-z0-9])' + re.escape(a) + r'(?![A-Za-z0-9])', lambda m, b=b: pad(m, b), s)
        else:
            s = s.replace(a, b)
    if (lang or 'en').lower()[:2] == 'ja':
        s = s.replace('／', '、').replace('/', '、').replace('｜', '、').replace('→', '、').replace('〜', 'から').replace('~', 'から').replace('%', 'パーセント')
        s = re.sub(r'[「」『』]', '', s)
        s = re.sub(r'\s+', ' ', s).strip()
        s = re.sub(r' ?([、。！？]) ?', r'\1', s)
    else:
        s = s.replace('→', ', ').replace('->', ', ').replace('|', ', ')
        s = re.sub(r'\s+', ' ', s).strip()
    return s


def nchars(s):
    return len(re.sub(r'[\s、。，．・：；！？「」『』（）()…\-,.!?:;"\']', '', s))


def units(s, lang):
    """Speech-length units: characters for CJK, words otherwise."""
    return max(1, nchars(s)) if is_cjk(lang) else max(1, len(s.split()))


def est(s, lang):
    return (nchars(s) * SEC_PER_CHAR if is_cjk(lang) else len(s.split()) * SEC_PER_WORD) + SEC_PER_LINE


# ------------------------------------------------------------------ prepare
def cmd_prepare(a):
    os.makedirs(a.work, exist_ok=True)
    tm = html_timing(a.html, strip_fit=True)
    lang = (a.lang or tm.get('lang') or 'en').lower()
    voice = a.voice or default_voice(a.backend, lang) or ''
    base = [] if a.no_default_readings else [os.path.join(SKILL, 'assets', f'readings.{lang[:2]}.tsv')]
    readings = load_readings(base + (a.readings or []))
    lines = []
    for sc in tm['scenes']:
        for ln in sc['lines']:
            lines.append({'key': f"{sc['id']}:{ln['idx']}", 'scene': sc['id'], 'idx': ln['idx'], 'text': ln['text'], 'tts': to_tts(ln['text'], readings, lang)})
    if not lines:
        sys.exit('No narration lines found (SCENES[].narration is empty).')
    prefix = 'batch'
    if a.only:
        # re-synthesize only the lines that changed (batch/external route); other lines keep their audio
        keys = {k.strip() for k in a.only.split(',') if k.strip()}
        lj = os.path.join(a.work, 'lines.json')
        old = {l['key']: l for l in json.load(open(lj, encoding='utf-8'))} if os.path.exists(lj) else {}
        n = 1 + sum(1 for f in os.listdir(a.work) if f.startswith('patch') and f.endswith('_turns.json'))
        prefix = f'patch{n:02d}-'
        for ln in lines:
            if ln['key'] not in keys and ln['key'] in old:
                ln['batch'] = old[ln['key']].get('batch')
        todo = [ln for ln in lines if ln['key'] in keys]
        if not todo:
            sys.exit('--only matched no lines (example: --only s2:1,s3:0)')
    else:
        todo = lines
    batches, cur, cur_sec, cur_chars = [], [], 0.0, 0
    for ln in todo:
        e = est(ln['tts'], lang)
        if cur and (cur_sec + e > a.max_sec or cur_chars + len(ln['tts']) > 17000 or len(cur) >= 380):
            batches.append(cur); cur, cur_sec, cur_chars = [], 0.0, 0
        cur.append(ln); cur_sec += e; cur_chars += len(ln['tts'])
    if cur:
        batches.append(cur)
    manifest = {'title': tm['title'], 'slug': tm['slug'], 'lang': lang, 'voice': voice, 'voice_set': bool(a.voice), 'batches': []}
    for bi, b in enumerate(batches, 1):
        name = f'{prefix}{bi:02d}' if prefix != 'batch' else f'batch{bi:02d}'
        for ln in b:
            ln['batch'] = name
        turns = [{'speaker': 'host', 'text': ln['tts']} for ln in b]
        json.dump(turns, open(os.path.join(a.work, f'{name}_turns.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        with open(os.path.join(a.work, f'{name}_script.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(ln['tts'] for ln in b) + '\n')
        manifest['batches'].append({'name': name, 'lines': len(b), 'est_sec': round(sum(est(l['tts'], lang) for l in b), 1),
                                    'filename': f"{tm['slug']}-{name}", 'title': f"{tm['title']} narration {bi}"})
    json.dump(lines, open(os.path.join(a.work, 'lines.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(manifest, open(os.path.join(a.work, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    changed = [l for l in lines if l['tts'] != unicodedata.normalize('NFKC', l['text'])]
    print(f"## {tm['title']}: {len(lines)} narration lines, language={lang}, voice={voice or '(set --voice)'}")
    for b in manifest['batches']:
        print(f"  {b['name']}: {b['lines']} lines, estimated {b['est_sec']} s  (external/batch route: filename={b['filename']})")
    if changed:
        print('## Lines changed by readings (TTS script only; screen and subtitles are untouched)')
        for l in changed[:40]:
            print(f"  {l['key']}: {l['tts']}")
    left = sorted(set(re.findall(r'[A-Za-z][A-Za-z0-9.+\-]*', ' '.join(l['tts'] for l in lines))))
    if left and lang[:2] == 'ja':
        print('WARNING Latin words left in the script (check how they will be read): ' + ', '.join(left[:30]))
    elif lang[:2] != 'ja':
        acr = [w for w in left if re.fullmatch(r'[A-Z]{2,6}s?', w)]
        if acr:
            print('NOTE acronyms in the script (add readings if the voice mispronounces them): ' + ', '.join(acr[:30]))


# ------------------------------------------------------------------ audio helpers
def decode(path):
    raw = subprocess.run([ffmpeg_or_exit(), '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def silences(x, min_len=0.22):
    hop = int(SR * 0.01)
    n = len(x) // hop
    fr = x[:n * hop].reshape(n, hop)
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(axis=1)) + 1e-9)
    speech = db[db > -60]
    ref = np.percentile(speech, 90) if len(speech) else -20
    thr = max(-55.0, ref - 32.0)
    quiet = db < thr
    runs, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) * 0.01 >= min_len:
                runs.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    return runs, thr


def trim(seg, thr_db):
    hop = int(SR * 0.01)
    n = len(seg) // hop
    if n == 0:
        return seg
    db = 20 * np.log10(np.sqrt((seg[:n * hop].reshape(n, hop) ** 2).mean(axis=1)) + 1e-9)
    loud = np.where(db > thr_db)[0]
    if len(loud) == 0:
        return seg
    a = max(0, loud[0] * hop - int(SR * 0.03))
    b = min(len(seg), (loud[-1] + 1) * hop + int(SR * 0.06))
    out = seg[a:b].copy()
    f = int(SR * 0.005)
    if len(out) > 2 * f:
        out[:f] *= np.linspace(0, 1, f); out[-f:] *= np.linspace(1, 0, f)
    return out


def write_wav(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm)


# ------------------------------------------------------------------ synth backends
def _http(url, data=None, headers=None, timeout=120, method=None):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'HTTP {e.code} from {url.split("?")[0]}: {e.read()[:300].decode("utf-8", "replace")}')


def synth_edge(text, voice, a, out):
    try:
        import asyncio, edge_tts
    except ImportError:
        sys.exit('edge-tts is not installed. Run: pip install edge-tts')

    async def go():
        await edge_tts.Communicate(text, voice, rate=a.rate, volume=a.volume, pitch=a.pitch).save(out)
    asyncio.run(go())
    return out


def synth_openai(text, voice, a, out):
    key = os.environ.get('OPENAI_API_KEY')
    if not key:
        sys.exit('OPENAI_API_KEY is not set.')
    base = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
    body = {'model': a.model or 'gpt-4o-mini-tts', 'voice': voice, 'input': text, 'response_format': 'mp3'}
    if a.instructions:
        body['instructions'] = a.instructions
    if a.speed:
        body['speed'] = float(a.speed)
    data = _http(base + '/audio/speech', json.dumps(body).encode(), {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    open(out, 'wb').write(data)
    return out


def synth_azure(text, voice, a, out):
    key, region = os.environ.get('AZURE_SPEECH_KEY'), os.environ.get('AZURE_SPEECH_REGION')
    if not key or not region:
        sys.exit('Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION (e.g. japaneast).')
    from xml.sax.saxutils import escape
    lang = '-'.join(voice.split('-')[:2]) or 'en-US'
    ssml = f"<speak version='1.0' xml:lang='{lang}'><voice name='{voice}'>{escape(text)}</voice></speak>"
    data = _http(f'https://{region}.tts.speech.microsoft.com/cognitiveservices/v1', ssml.encode('utf-8'),
                 {'Ocp-Apim-Subscription-Key': key, 'Content-Type': 'application/ssml+xml', 'X-Microsoft-OutputFormat': 'audio-24khz-96kbitrate-mono-mp3', 'User-Agent': 'explainer-video'})
    open(out, 'wb').write(data)
    return out


def synth_voicevox(text, voice, a, out):
    from urllib.parse import quote
    base = os.environ.get('VOICEVOX_URL', 'http://127.0.0.1:50021').rstrip('/')
    q = _http(f'{base}/audio_query?speaker={quote(str(voice))}&text={quote(text)}', b'', method='POST')
    if a.speed:
        qj = json.loads(q); qj['speedScale'] = float(a.speed); q = json.dumps(qj).encode()
    wav = _http(f'{base}/synthesis?speaker={quote(str(voice))}', q, {'Content-Type': 'application/json'})
    open(out, 'wb').write(wav)
    return out


def synth_command(text, voice, a, out):
    """Any CLI TTS: --cmd 'mytts --voice {voice} --in {text_file} --out {out}' (output may be wav/mp3/ogg: anything ffmpeg can read)."""
    if not a.cmd_tpl:
        sys.exit('--backend command needs --cmd with {text_file} and {out} placeholders.')
    tf = out + '.txt'
    open(tf, 'w', encoding='utf-8').write(text)
    cmd = a.cmd_tpl.format(text_file=tf, out=out, voice=voice, text=text.replace('"', '\\"'))
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(out):
        raise RuntimeError(f'command failed ({r.returncode}): {(r.stderr or r.stdout)[-300:]}')
    return out


BACKENDS = {'edge': (synth_edge, '.mp3'), 'openai': (synth_openai, '.mp3'), 'azure': (synth_azure, '.mp3'), 'voicevox': (synth_voicevox, '.wav'), 'command': (synth_command, '.audio')}


def cmd_synth(a):
    lj = os.path.join(a.work, 'lines.json')
    if not os.path.exists(lj):
        sys.exit('Run `prepare` first (lines.json is missing).')
    lines = json.load(open(lj, encoding='utf-8'))
    man = json.load(open(os.path.join(a.work, 'manifest.json'), encoding='utf-8'))
    lang = man.get('lang', 'en')
    # a voice chosen with `prepare --voice` is kept; otherwise the backend/language default applies
    voice = a.voice or (man.get('voice') if man.get('voice_set') else None) or default_voice(a.backend, lang)
    if not voice:
        sys.exit('Set --voice for this backend/language.')
    if man.get('voice_set') and a.voice and a.voice != man.get('voice'):
        print(f"NOTE: --voice {a.voice} overrides the voice given to prepare ({man.get('voice')}).")
    print(f"voice: {voice} ({a.backend})")
    fn, ext = BACKENDS[a.backend]
    wavdir = os.path.join(a.work, 'wav'); os.makedirs(wavdir, exist_ok=True)
    cache_p = os.path.join(a.work, 'synth_cache.json')
    cache = json.load(open(cache_p, encoding='utf-8')) if os.path.exists(cache_p) else {}
    sel = {k.strip() for k in a.only.split(',')} if a.only else None
    todo = [l for l in lines if sel is None or l['key'] in sel]

    def key_of(l):
        return hashlib.sha1(json.dumps([a.backend, voice, a.rate, a.pitch, a.volume, a.model, a.speed, a.instructions, a.cmd_tpl, l['tts']], ensure_ascii=False).encode()).hexdigest()

    def work(l):
        out_wav = os.path.join(wavdir, f"{l['scene']}_{l['idx']:02d}.wav")
        k = key_of(l)
        if not a.force and cache.get(l['key']) == k and os.path.exists(out_wav):
            return l, out_wav, True
        last = None
        for attempt in range(4):
            tmp = os.path.join(tempfile.gettempdir(), f"xv_{os.getpid()}_{l['scene']}_{l['idx']}{ext}")
            try:
                fn(l['tts'], voice, a, tmp)
                x = decode(tmp)
                if len(x) < SR * 0.2:
                    raise RuntimeError('audio too short / empty')
                write_wav(out_wav, trim(x, -50.0))
                return l, out_wav, False
            except SystemExit:
                raise
            except Exception as e:  # network hiccups, rate limits
                last = e; time.sleep(1.5 * (attempt + 1))
            finally:
                for f in (tmp, tmp + '.txt'):
                    if os.path.exists(f):
                        os.remove(f)
        raise RuntimeError(f"{l['key']}: synthesis failed after retries: {last}")

    done = {}
    try:
        with cf.ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
            for l, f, hit in ex.map(work, todo):
                cache[l['key']] = key_of(l)
                done[l['key']] = (f, hit)
                print(f"  {l['key']:8s} {'cached' if hit else 'synth '}  {l['tts'][:60]}")
    except RuntimeError as e:
        json.dump(cache, open(cache_p, 'w', encoding='utf-8'))
        sys.exit(f'ERROR ({a.backend}): {e}\nHint: see references/tts-backends.md (credentials, engine URL, edge-tts upgrade for HTTP 403).')
    json.dump(cache, open(cache_p, 'w', encoding='utf-8'))

    prev_p = os.path.join(a.work, 'audio_lines.json')
    prev = {l['key']: l for l in json.load(open(prev_p, encoding='utf-8'))} if os.path.exists(prev_p) else {}
    for l in todo:
        f = done[l['key']][0]
        with wave.open(f, 'rb') as w:
            dur = w.getnframes() / w.getframerate()
        prev[l['key']] = dict(l, file=f, dur=round(dur, 3))
    final = [prev[l['key']] for l in lines if l['key'] in prev]
    json.dump(final, open(prev_p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    lo, hi = (4.0, 12.0) if is_cjk(lang) else (1.2, 4.6)
    bad = 0
    print('line      sec   units/s')
    for e in final:
        ups = units(e['tts'], lang) / e['dur'] if e['dur'] else 0
        flag = '' if lo <= ups <= hi else '  <- unusual pace, check the audio'
        bad += bool(flag)
        print(f"{e['key']:8s} {e['dur']:5.2f}  {ups:5.1f}{flag}")
    print(f"Synthesized {len(todo)} line(s) with {a.backend}/{voice} -> {prev_p}")
    if bad:
        print('WARNING some lines have an unusual speaking pace; listen to narr/wav/ and re-run with --only KEY --force if needed.')


# ------------------------------------------------------------------ split (external batch audio)
def choose_cuts(runs, n_lines, weights, s0, s1):
    """Pick n_lines-1 silences, close to the character-ratio expectation and preferring long ones (DP)."""
    need = n_lines - 1
    if need <= 0:
        return [], 'ok'
    inner = [r for r in runs if r[0] > s0 + 0.05 and r[1] < s1 - 0.05]
    if len(inner) < need:
        return None, 'too-few'
    long_ = [r for r in inner if r[1] - r[0] >= 0.85]
    if len(long_) == need:
        return [(r[0] + r[1]) / 2 for r in long_], 'ok'
    span = s1 - s0
    cum = np.cumsum(weights)[:-1] / np.sum(weights)
    exp_ = s0 + cum * span
    M = len(inner)
    mids = [(r[0] + r[1]) / 2 for r in inner]
    lens = [r[1] - r[0] for r in inner]
    INF = 1e18
    cost = np.full((need, M), INF)
    back = np.full((need, M), -1, dtype=int)
    for m in range(M):
        cost[0, m] = abs(mids[m] - exp_[0]) / span * 10 - np.log(lens[m] + 0.05)
    for k in range(1, need):
        for m in range(k, M):
            prev = cost[k - 1, :m]
            p = int(np.argmin(prev))
            if prev[p] >= INF:
                continue
            cost[k, m] = prev[p] + abs(mids[m] - exp_[k]) / span * 10 - np.log(lens[m] + 0.05)
            back[k, m] = p
    m = int(np.argmin(cost[need - 1]))
    picks = [m]
    for k in range(need - 1, 0, -1):
        m = back[k, m]
        picks.append(m)
    picks.reverse()
    return [mids[i] for i in picks], 'DP'


def cmd_split(a):
    lines = json.load(open(os.path.join(a.work, 'lines.json'), encoding='utf-8'))
    lang = json.load(open(os.path.join(a.work, 'manifest.json'), encoding='utf-8')).get('lang', 'en')
    audio = dict(x.split('=', 1) for x in a.audio)
    os.makedirs(os.path.join(a.work, 'wav'), exist_ok=True)
    prev_path = os.path.join(a.work, 'audio_lines.json')
    prev = {l['key']: l for l in json.load(open(prev_path, encoding='utf-8'))} if os.path.exists(prev_path) else {}
    out, report = [], []
    for bname in sorted(audio):
        bl = [l for l in lines if l.get('batch') == bname]
        if not bl:
            sys.exit(f'No batch named {bname} in lines.json')
        x = decode(audio[bname])
        runs, thr = silences(x)
        total = len(x) / SR
        head = runs[0][1] if runs and runs[0][0] <= 0.02 else 0.0
        tail = runs[-1][0] if runs and runs[-1][1] >= total - 0.02 else total
        skip = a.skip_head
        weights = [units(l['tts'], lang) for l in bl]
        cuts, how = choose_cuts(runs, len(bl) + skip, ([weights[0]] * skip) + weights, head, tail)
        if cuts is None:
            sys.exit(f'{bname}: not enough silent gaps ({len(runs)}). Merge lines or re-synthesize this batch.')
        bounds = ([head] + cuts + [tail])[skip:]
        for k, l in enumerate(bl):
            seg = trim(x[int(bounds[k] * SR):int(bounds[k + 1] * SR)], thr)
            f = os.path.join(a.work, 'wav', f"{l['scene']}_{l['idx']:02d}.wav")
            write_wav(f, seg)
            dur = len(seg) / SR
            out.append(dict(l, file=f, dur=round(dur, 3)))
            report.append((l['key'], bname, how, dur, units(l['tts'], lang) / dur if dur > 0 else 0))
    merged = dict(prev)
    merged.update({l['key']: l for l in out})
    order = [l['key'] for l in lines]
    final = [merged[k] for k in order if k in merged]
    missing = [k for k in order if k not in merged]
    json.dump(final, open(prev_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if missing:
        print('WARNING no audio yet for: ' + ', '.join(missing))
    lo, hi = (4.0, 12.0) if is_cjk(lang) else (1.2, 4.6)
    print('line          batch     cut     sec   units/s')
    bad = 0
    for key, b, how, dur, ups in report:
        flag = '' if lo <= ups <= hi else '  <- cut may be wrong'
        bad += bool(flag)
        print(f'{key:12s}  {b:8s}  {how:6s} {dur:5.2f}  {ups:5.1f}{flag}')
    print(f"Split {len(out)} lines -> {prev_path}")
    if bad:
        print('WARNING some lines have an extreme pace. Compare against the script; re-synthesize that batch or check --skip-head.')


# ------------------------------------------------------------------ fit
def cmd_fit(a):
    al = {l['key']: l for l in json.load(open(os.path.join(a.work, 'audio_lines.json'), encoding='utf-8'))}
    tm = html_timing(a.html, strip_fit=True)
    fit, place, T = {}, [], 0.0
    for sc in tm['scenes']:
        lines = []
        prev_end = None
        for ln in sc['lines']:
            key = f"{sc['id']}:{ln['idx']}"
            if key not in al:
                sys.exit(f'No audio for {key}. Run synth (or split) again.')
            d = al[key]['dur']
            at = ln['at'] if prev_end is None else (max(ln['at'], prev_end + a.gap) if a.keep else prev_end + a.gap)
            at = round(at, 2)
            lines.append({'at': at, 'dur': round(d, 3)})
            prev_end = at + d
            place.append({'key': key, 'scene': sc['id'], 'idx': ln['idx'], 'start': round(T + at, 3), 'dur': round(d, 3), 'file': al[key]['file'], 'text': ln['text']})
        tail = max(a.tail, float(sc.get('hold') or 0))
        need = (prev_end + tail) if prev_end is not None else sc['duration']
        dur = round(max(sc['duration'], need) if a.keep or prev_end is None else need, 2)
        fit[sc['id']] = {'duration': dur, 'lines': lines}
        T += dur
    fitobj = {'source': 'narration', 'gap': a.gap, 'tail': a.tail, 'mode': 'keep' if a.keep else 'tight', 'scenes': fit}
    s = open(a.html, encoding='utf-8').read()
    if '/*FIT-BEGIN*/' not in s:
        sys.exit('The HTML has no /*FIT-BEGIN*/ ... /*FIT-END*/ block (rebuild it from the template).')
    s = re.sub(r'/\*FIT-BEGIN\*/.*?/\*FIT-END\*/', lambda m: '/*FIT-BEGIN*/const FIT = ' + json.dumps(fitobj, ensure_ascii=False) + ';/*FIT-END*/', s, flags=re.S)
    open(a.html, 'w', encoding='utf-8').write(s)
    json.dump({'total': round(T, 3), 'lines': place}, open(os.path.join(a.work, 'placement.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'Timing fitted to the narration audio (total {T:.1f} s)')
    for sc in tm['scenes']:
        f = fit[sc['id']]
        print(f"  {sc['id']:5s} {sc['duration']:5.1f}s -> {f['duration']:5.1f}s  line starts {[l['at'] for l in f['lines']]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('prepare'); p.add_argument('--html', required=True); p.add_argument('--work', required=True)
    p.add_argument('--lang', help='override VIDEO.lang (ja, en, zh, ko, es, ...)'); p.add_argument('--readings', action='append', help='extra readings TSV (surface<TAB>reading); overrides the defaults')
    p.add_argument('--backend', default='edge', help='only used to choose the default voice'); p.add_argument('--voice')
    p.add_argument('--max-sec', type=float, default=140, help='batch size for the external/batch route'); p.add_argument('--only', help='prepare only these lines, e.g. s2:1,s3:0')
    p.add_argument('--no-default-readings', action='store_true')
    p = sub.add_parser('synth'); p.add_argument('--work', required=True); p.add_argument('--backend', choices=sorted(BACKENDS), default='edge')
    p.add_argument('--voice'); p.add_argument('--rate', default='+0%', help='edge: speaking rate such as +10%% or -10%%'); p.add_argument('--pitch', default='+0Hz'); p.add_argument('--volume', default='+0%')
    p.add_argument('--model', help='openai: model (default gpt-4o-mini-tts)'); p.add_argument('--instructions', help='openai gpt-4o-mini-tts: tone/style instructions'); p.add_argument('--speed', help='openai/voicevox speed multiplier')
    p.add_argument('--cmd', dest='cmd_tpl', help='command backend template with {text_file} {out} {voice}'); p.add_argument('--jobs', type=int, default=3)
    p.add_argument('--only', help='synthesize only these line keys, e.g. s2:1,s3:0'); p.add_argument('--force', action='store_true', help='ignore the cache')
    p = sub.add_parser('split'); p.add_argument('--work', required=True); p.add_argument('--audio', nargs='+', required=True); p.add_argument('--skip-head', type=int, default=0)
    p = sub.add_parser('fit'); p.add_argument('--html', required=True); p.add_argument('--work', required=True)
    p.add_argument('--gap', type=float, default=0.7); p.add_argument('--tail', type=float, default=1.3); p.add_argument('--keep', action='store_true', help='never make line starts/scene durations shorter than the HTML values')
    a = ap.parse_args()
    {'prepare': cmd_prepare, 'synth': cmd_synth, 'split': cmd_split, 'fit': cmd_fit}[a.cmd](a)


if __name__ == '__main__':
    main()
