#!/usr/bin/env python3
"""Collect logos/icons for the video and embed them in the HTML.

  import  : bring in the user's own icon set (a folder or .zip of SVG/PNG) under normalized names
      python icons.py import --src ./my-icons-or.zip --out icons
  extract : pull images out of an icon-set .pptx (SVG preferred), named by nearby labels
      python icons.py extract --pptx IconSet.pptx --out icons [--find Monitor,Alerts]
  fetch   : download from the web and record source + license in icons/ATTRIBUTION.json
      python icons.py fetch --out icons --simple nvidia,openai --color brand     # Simple Icons (CC0 artwork)
      python icons.py fetch --out icons --url nvidia=https://example.com/logo.svg  # any direct SVG/PNG URL
      python icons.py fetch --out icons --search nvidia                            # look up Simple Icons slugs
  sheet   : render a labeled contact sheet PNG of a folder (open it and CHECK every icon before use)
      python icons.py sheet --dir icons --out iconsheet.png
  embed   : write images into VIDEO.images of the HTML as data URIs (one self-contained file)
      python icons.py embed --html video.html --map nvidia=icons/nvidia.svg openai=icons/openai.svg

Draw an embedded image in a scene with oi(ctx, 'nvidia', centerX, centerY, size) or img(ctx, 'nvidia', x, y, w, h).
"""
import argparse, base64, datetime, io, json, os, re, shutil, subprocess, sys, urllib.error, urllib.request, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import HERE, setup_stdio  # noqa: E402

setup_stdio()
UA = {'User-Agent': 'explainer-video-skill/1.0'}
SI_CDN = 'https://cdn.jsdelivr.net/npm/simple-icons@latest'
SI_RAW = 'https://raw.githubusercontent.com/simple-icons/simple-icons/develop'
IMG_EXT = ('.svg', '.png', '.jpg', '.jpeg', '.webp')


def slug(s):
    return re.sub(r'[^\w\-.()]+', '_', s.strip())[:80].strip('_').lower()


def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def log_attribution(out, entry):
    p = os.path.join(out, 'ATTRIBUTION.json')
    cur = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else []
    cur = [e for e in cur if e.get('name') != entry['name']] + [entry]
    json.dump(cur, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


# ------------------------------------------------------------------ import
def cmd_import(a):
    os.makedirs(a.out, exist_ok=True)
    n = 0
    if a.src.lower().endswith('.zip'):
        z = zipfile.ZipFile(a.src)
        for m in z.namelist():
            if m.lower().endswith(IMG_EXT) and not m.endswith('/'):
                name = slug(os.path.splitext(os.path.basename(m))[0]) + os.path.splitext(m)[1].lower()
                open(os.path.join(a.out, name), 'wb').write(z.read(m)); n += 1
    else:
        for root, _, files in os.walk(a.src):
            for f in files:
                if f.lower().endswith(IMG_EXT):
                    name = slug(os.path.splitext(f)[0]) + os.path.splitext(f)[1].lower()
                    shutil.copyfile(os.path.join(root, f), os.path.join(a.out, name)); n += 1
    print(f'Imported {n} image(s) -> {a.out}')
    log_attribution(a.out, {'name': '(user-provided set)', 'source': a.src, 'license': 'provided by the user; the user is responsible for usage rights', 'fetched': str(datetime.date.today())})


# ------------------------------------------------------------------ extract (pptx)
def cmd_extract(a):
    z = zipfile.ZipFile(a.pptx)
    names = z.namelist()
    os.makedirs(a.out, exist_ok=True)
    found = {}
    slides = sorted([n for n in names if re.match(r'ppt/slides/slide\d+\.xml$', n)], key=lambda x: int(re.findall(r'\d+', x)[0]))
    for s in slides:
        x = z.read(s).decode('utf-8', 'ignore')
        relp = s.replace('slides/', 'slides/_rels/').replace('.xml', '.xml.rels')
        rel = z.read(relp).decode('utf-8', 'ignore') if relp in names else ''
        rmap = {}
        for m in re.finditer(r'<Relationship [^>]*>', rel):
            t = m.group(0); i = re.search(r'Id="([^"]+)"', t); g = re.search(r'Target="\.\./media/([^"]+)"', t)
            if i and g:
                rmap[i.group(1)] = g.group(1)
        pics, labels = [], []
        for m in re.finditer(r'<p:pic>.*?</p:pic>', x, re.S):
            b = m.group(0)
            off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>\s*<a:ext cx="(\d+)" cy="(\d+)"', b)
            svg = re.findall(r'svgBlip[^>]*r:embed="([^"]+)"', b); emb = re.findall(r'r:embed="([^"]+)"', b)
            nm = re.search(r'<p:cNvPr [^>]*name="([^"]*)"', b); ds = re.search(r'<p:cNvPr [^>]*descr="([^"]*)"', b)
            media = rmap.get((svg or emb or [None])[0])
            if off and media:
                pics.append(dict(x=int(off[1]), y=int(off[2]), w=int(off[3]), h=int(off[4]), media=media, name=(ds.group(1) if ds and ds.group(1) else nm.group(1) if nm else '')))
        for m in re.finditer(r'<p:sp>.*?</p:sp>', x, re.S):
            b = m.group(0); t = ''.join(re.findall(r'<a:t>([^<]*)</a:t>', b)).strip()
            off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>\s*<a:ext cx="(\d+)" cy="(\d+)"', b)
            if off and t and len(t) < 120:
                labels.append(dict(x=int(off[1]), y=int(off[2]), w=int(off[3]), h=int(off[4]), t=t))
        for p in pics:
            cx, by = p['x'] + p['w'] / 2, p['y'] + p['h']
            near = [l for l in labels if abs(l['x'] + l['w'] / 2 - cx) < max(p['w'], l['w']) and -p['h'] * 0.2 < l['y'] - by < p['h'] * 1.5]
            lab = min(near, key=lambda l: abs(l['y'] - by) + abs(l['x'] + l['w'] / 2 - cx) * 0.5)['t'] if near else p['name']
            key = re.sub(r'\.(svg|png)$', '', lab or p['media'])
            key = re.sub(r'^\d+-icon-service-', '', key)
            if key not in found:
                found[key] = dict(media=p['media'], slide=os.path.basename(s))
    index = {}
    for key, v in found.items():
        ext = os.path.splitext(v['media'])[1]
        fn = re.sub(r'[^\w\-.()]+', '_', key)[:80] + ext
        open(os.path.join(a.out, fn), 'wb').write(z.read('ppt/media/' + v['media']))
        index[key] = dict(file=fn, slide=v['slide'])
    json.dump(index, open(os.path.join(a.out, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'Extracted {len(index)} image(s) -> {a.out}/index.json')
    log_attribution(a.out, {'name': '(pptx icon set)', 'source': a.pptx, 'license': 'check the icon set\'s own terms', 'fetched': str(datetime.date.today())})
    if a.find:
        for w in a.find.split(','):
            hits = [k for k in index if w.strip().lower() in k.lower()]
            print(f'  "{w.strip()}": ' + (', '.join(f"{k} -> {index[k]['file']}" for k in hits[:6]) if hits else 'not found'))


# ------------------------------------------------------------------ fetch (web)
def si_data(out):
    cache = os.path.join(out, '.simple-icons.json')
    if os.path.exists(cache):
        return json.load(open(cache, encoding='utf-8'))
    for u in (SI_CDN + '/data/simple-icons.json', SI_RAW + '/data/simple-icons.json', SI_RAW + '/_data/simple-icons.json'):
        try:
            d = json.loads(http_get(u, 60))
            d = d.get('icons', d) if isinstance(d, dict) else d
            json.dump(d, open(cache, 'w', encoding='utf-8'))
            return d
        except Exception:
            continue
    return []


def si_lookup(data, name):
    n = slug(name).replace('_', '')
    for e in data:
        t = re.sub(r'[^a-z0-9]', '', (e.get('slug') or e.get('title', '')).lower())
        if t == n or re.sub(r'[^a-z0-9]', '', e.get('title', '').lower()) == n:
            return e
    return None


def tint_svg(svg, hexcolor):
    hexcolor = hexcolor.lstrip('#')
    return re.sub(r'<svg\b', f'<svg fill="#{hexcolor}"', svg, count=1) if 'fill=' not in svg.split('>', 1)[0] else svg


def cmd_fetch(a):
    os.makedirs(a.out, exist_ok=True)
    today = str(datetime.date.today())
    if a.search:
        data = si_data(a.out)
        hits = [e for e in data if a.search.lower() in (e.get('title', '') + ' ' + (e.get('slug') or '')).lower()]
        print(f'{len(hits)} match(es) in Simple Icons for "{a.search}":')
        for e in hits[:25]:
            print(f"  slug={e.get('slug') or re.sub(r'[^a-z0-9]', '', e['title'].lower())}  title={e['title']}  brand={e.get('hex')}")
        return
    for item in a.url or []:
        name, u = item.split('=', 1)
        data = http_get(u)
        ext = os.path.splitext(u.split('?')[0])[1].lower()
        ext = ext if ext in IMG_EXT else ('.svg' if data.lstrip()[:5] in (b'<svg ', b'<?xml') or b'<svg' in data[:300] else '.png')
        fn = slug(name) + ext
        open(os.path.join(a.out, fn), 'wb').write(data)
        log_attribution(a.out, {'name': name, 'file': fn, 'source': u, 'license': a.license or 'UNVERIFIED: check the site terms / brand guidelines before publishing', 'fetched': today})
        print(f'Downloaded {name} -> {fn} (record: {a.license or "license unverified"})')
    if a.simple:
        data = si_data(a.out) if a.color == 'brand' else []
        for nm in [x.strip() for x in a.simple.split(',') if x.strip()]:
            ent = si_lookup(data, nm) if data else None
            sl = (ent.get('slug') if ent and ent.get('slug') else re.sub(r'[^a-z0-9]', '', nm.lower()))
            svg = None
            for base in (SI_CDN, SI_RAW):
                try:
                    svg = http_get(f'{base}/icons/{sl}.svg').decode('utf-8'); src = f'{base}/icons/{sl}.svg'; break
                except Exception:
                    continue
            if not svg:
                print(f'  {nm}: not found in Simple Icons (try --search {nm}, or use --url with the vendor\'s brand-asset page)')
                continue
            color = None
            if a.color == 'brand' and ent and ent.get('hex'):
                color = ent['hex']
            elif a.color and a.color not in ('brand', 'none'):
                color = a.color
            if color:
                svg = tint_svg(svg, color)
            fn = sl + '.svg'
            open(os.path.join(a.out, fn), 'w', encoding='utf-8').write(svg)
            log_attribution(a.out, {'name': nm, 'file': fn, 'source': src, 'license': 'Simple Icons artwork is CC0-1.0; the logo/trademark itself belongs to its owner (follow the brand guidelines)',
                                    'color': color or 'default (black)', 'fetched': today})
            print(f'  {nm}: {fn}' + (f' (brand color #{color.lstrip("#")})' if color else ''))
    print(f'Source and license notes: {os.path.join(a.out, "ATTRIBUTION.json")}')


# ------------------------------------------------------------------ sheet
def cmd_sheet(a):
    files = sorted(f for f in os.listdir(a.dir) if f.lower().endswith(IMG_EXT))
    d = os.path.abspath(a.dir)
    html = ('<html><body style="margin:8px;font:13px sans-serif;display:flex;flex-wrap:wrap;width:1180px;background:#fff">' + ''.join(
        f'<div style="width:140px;height:132px;text-align:center;margin:3px;overflow:hidden"><img src="{f}" style="width:80px;height:80px;object-fit:contain"><br>{f}</div>' for f in files) + '</body></html>')
    tmp = os.path.join(d, '.__iconsheet.html')
    open(tmp, 'w', encoding='utf-8').write(html)
    try:
        r = subprocess.run(['node', os.path.join(HERE, 'browser_shot.mjs'), tmp, os.path.abspath(a.out), '--width', '1200'], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit('Could not render the sheet: ' + (r.stderr or r.stdout)[-600:])
    finally:
        os.remove(tmp)
    print(f'Saved icon sheet: {a.out} ({len(files)} images)')


# ------------------------------------------------------------------ embed
def normalize_svg(raw):
    """Give viewBox-only SVGs an explicit width/height so canvas drawing keeps the right aspect ratio."""
    s = raw.decode('utf-8', 'ignore')
    head = re.search(r'<svg\b[^>]*>', s)
    if not head or re.search(r'\swidth=', head.group(0)):
        return s.encode('utf-8')
    vb = re.search(r'viewBox="\s*[-\d.]+[ ,]+[-\d.]+[ ,]+([\d.]+)[ ,]+([\d.]+)', head.group(0))
    if not vb:
        return s.encode('utf-8')
    w, h = float(vb[1]), float(vb[2])
    k = 256 / max(w, h)
    new = head.group(0).replace('<svg', f'<svg width="{w * k:.0f}" height="{h * k:.0f}"', 1)
    return s.replace(head.group(0), new, 1).encode('utf-8')


def cmd_embed(a):
    out = {}
    for item in a.map:
        k, p = item.split('=', 1)
        ext = os.path.splitext(p)[1].lower()
        if ext == '.svg':
            out[k] = 'data:image/svg+xml;base64,' + base64.b64encode(normalize_svg(open(p, 'rb').read())).decode()
        else:
            try:
                from PIL import Image
                im = Image.open(p).convert('RGBA'); bb = im.getbbox(); im = im.crop(bb) if bb else im
                im.thumbnail((a.max_png, a.max_png)); buf = io.BytesIO(); im.save(buf, 'PNG', optimize=True)
                out[k] = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
            except Exception:
                mime = 'image/png' if ext == '.png' else 'image/jpeg'
                out[k] = f'data:{mime};base64,' + base64.b64encode(open(p, 'rb').read()).decode()
    s = open(a.html, encoding='utf-8').read()
    m = re.search(r'const VIDEO = \{.*?\n\};', s, re.S)
    if not m:
        sys.exit('VIDEO definition not found in the HTML.')
    blk = m.group(0)
    existing = re.search(r'images:\s*(\{[^\n]*\})', blk)
    merged = {}
    if existing:
        try:
            merged = json.loads(existing.group(1))
        except Exception:
            merged = {}
    merged.update(out)
    blk2, n = re.subn(r'images:\s*\{[^\n]*\}', lambda _: 'images: ' + json.dumps(merged), blk, count=1)
    if n == 0:
        sys.exit('VIDEO.images not found (keep an `images: {}` line inside VIDEO).')
    s = s.replace(blk, blk2)
    open(a.html, 'w', encoding='utf-8').write(s)
    print(f'Embedded {len(out)} image(s) (HTML is now {len(s.encode()) / 1024:.0f} KB): ' + ', '.join(out))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('import'); p.add_argument('--src', required=True); p.add_argument('--out', required=True)
    p = sub.add_parser('extract'); p.add_argument('--pptx', required=True); p.add_argument('--out', required=True); p.add_argument('--find')
    p = sub.add_parser('fetch'); p.add_argument('--out', required=True); p.add_argument('--simple', help='comma-separated Simple Icons names/slugs')
    p.add_argument('--color', help="'brand' (Simple Icons brand color), a hex like 76B900, or 'none'"); p.add_argument('--url', nargs='+', help='NAME=URL (direct SVG/PNG)')
    p.add_argument('--license', help='license/terms note to record for --url downloads'); p.add_argument('--search', help='search Simple Icons slugs')
    p = sub.add_parser('sheet'); p.add_argument('--dir', required=True); p.add_argument('--out', required=True)
    p = sub.add_parser('embed'); p.add_argument('--html', required=True); p.add_argument('--map', nargs='+', required=True); p.add_argument('--max-png', type=int, default=360)
    a = ap.parse_args()
    {'import': cmd_import, 'extract': cmd_extract, 'fetch': cmd_fetch, 'sheet': cmd_sheet, 'embed': cmd_embed}[a.cmd](a)


if __name__ == '__main__':
    main()
