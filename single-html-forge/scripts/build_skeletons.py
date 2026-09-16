#!/usr/bin/env python3
"""Assemble the archetype skeletons and pin the approved hashes.

Standard library only. The skeletons embed the runtime and CSS verbatim, and the
registry records the SHA-256 of exactly the text that ends up inline, so the
verifier's hash comparison and the artifacts can never drift apart.

Run this after changing anything under assets/runtime or assets/css.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
RUNTIME = SKILL / "assets" / "runtime" / "shf-runtime.js"
CSS_DIR = SKILL / "assets" / "css"
OUT_DIR = SKILL / "assets" / "skeletons"

RUNTIME_VERSION = "8"
CSS_VERSION = "8"

THEME = {
    "deck": """:root{--shf-color-accent:#0067b8;--shf-color-bg:#ffffff;--shf-color-fg:#1b1f27;--shf-size-base:20px}""",
    "doc": """:root{--shf-color-accent:#0067b8;--shf-color-accent-deep:#0b3a63;--shf-size-base:15px}""",
    "poster": """:root{--shf-color-accent:#0067b8;--shf-size-canvas-w:1200px;--shf-size-canvas-h:630px}""",
}

MODEL = '{"schemaVersion":1,"profileId":"base","profileVersion":1,"assets":[]}'

DECK_BODY = """<main id="shf-root">
<section data-slide-id="s1" class="is-active">
<p class="shf-eyebrow">SINGLE HTML FORGE</p>
<h1>タイトルをここに置く</h1>
<p class="shf-lead">副題。1 行で主張を言い切る。</p>
<p data-shf-notes>話者メモ。発表者モードにだけ出る。</p>
</section>
<section data-slide-id="s2" hidden>
<h2>3 つの論点</h2>
<div class="shf-cards">
<div class="shf-card"><h3>論点 1</h3><p>短く書く。読ませるのではなく見せる。</p></div>
<div class="shf-card"><h3>論点 2</h3><p>1 枚に詰め込まない。</p></div>
<div class="shf-card"><h3>論点 3</h3><p>数字は表に逃がす。</p></div>
</div>
<p data-shf-notes>ここで一度止まって質問を取る。</p>
</section>
<section data-slide-id="s3" hidden>
<h2>比較</h2>
<table>
<thead><tr><th>観点</th><th>従来</th><th>今回</th></tr></thead>
<tbody>
<tr><td>配布</td><td>専用アプリが要る</td><td>ブラウザーだけ</td></tr>
<tr><td>依存</td><td>外部リソース</td><td>単一ファイル</td></tr>
</tbody>
</table>
<p data-shf-notes>表は 5 行を超えたら分割する。</p>
</section>
<div id="shf-chrome">
<button type="button" data-shf-action="prev" title="Previous" aria-label="Previous">&#8592;</button>
<span id="shf-slide-counter">1 / 3</span>
<span id="shf-step-counter" hidden></span>
<button type="button" data-shf-action="next" title="Next" aria-label="Next">&#8594;</button>
<button type="button" data-shf-action="outline" title="Slide sidebar" aria-label="Slide sidebar" aria-expanded="false">&#9776;</button>
<button type="button" data-shf-action="fullscreen" title="Fullscreen" aria-label="Fullscreen" aria-pressed="false">&#9974;</button>
<button type="button" data-shf-action="mute" title="Mute" aria-label="Mute" hidden>M</button>
<details id="shf-menu">
<summary title="Settings" aria-label="Settings">&#8943;</summary>
<div class="shf-settings">
<label><input id="shf-sound" type="checkbox"> Sound</label>
<label>Volume <input id="shf-volume" type="range" min="0" max="100" step="1" value="30" aria-label="Volume"></label>
<button type="button" data-shf-action="test-sound">Test sound</button>
<label><input id="shf-motion" type="checkbox" aria-describedby="shf-motion-status" checked> Motion</label>
<p id="shf-motion-status" role="status" hidden>Reduced motion is enabled by the system.</p>
<button type="button" data-shf-action="list-style" aria-pressed="false" hidden>Title list</button>
<button type="button" data-shf-action="presenter">Presenter notes (shared screen)</button>
<button type="button" data-shf-action="print">Print / PDF</button>
</div>
</details>
</div>
</main>
<p id="shf-status" class="shf-sr" role="status" aria-live="polite"></p>
<div id="shf-presenter" role="dialog" aria-modal="true" aria-label="Presenter notes" hidden>
<div class="shf-presenter-head">
<h4>PRESENTER</h4>
<span id="shf-presenter-clock">00:00</span>
<button type="button" data-shf-action="presenter" aria-label="Close presenter">Close</button>
</div>
<div class="shf-pane">
<h4>現在</h4>
<p id="shf-presenter-now"></p>
<h4>次</h4>
<p id="shf-presenter-next"></p>
</div>
<div class="shf-pane">
<h4>メモ</h4>
<p id="shf-presenter-notes"></p>
</div>
</div>"""

DOC_BODY = """<nav>
<p class="shf-brand">資料タイトル<span>単一 HTML 説明資料</span></p>
<ol>
<li><a href="#overview" data-shf-navlink="overview">概要</a></li>
<li><a href="#detail" data-shf-navlink="detail">詳細</a></li>
<li><a href="#sources" data-shf-navlink="sources">出典</a></li>
</ol>
<p class="shf-nav-note">この資料は単一ファイルで、外部リソースを読み込みません。</p>
<button type="button" class="shf-print" data-shf-action="print">PDF として保存</button>
</nav>
<main>
<header class="shf-hero">
<p class="shf-eyebrow">EXPLAINER</p>
<h1>読ませるための資料タイトル</h1>
<p class="shf-lead">導入。何を、誰に、なぜ説明するのかを 2 文で書く。</p>
<div class="shf-meta"><span class="shf-pill">2026-08</span><span class="shf-pill">単一 HTML</span></div>
</header>
<section id="overview">
<h2>概要</h2>
<p>本文。1 段落 3 文を目安にする。根拠が要る主張には出典番号を付ける<a class="shf-refmark" href="#ref-1" data-citation-id="c1">1</a>。</p>
<div class="shf-callout"><p>補足はコールアウトに逃がすと本文が読みやすい。</p></div>
<div class="shf-flow">
<div class="shf-col is-bad"><h3>従来</h3><ol><li>外部 CSS を読む</li><li>フォントを取りに行く</li><li>オフラインで崩れる</li></ol></div>
<div class="shf-col is-ok"><h3>今回</h3><ol><li>全部埋め込む</li><li>システムフォントで組む</li><li>どこでも同じに開く</li></ol></div>
</div>
</section>
<section id="detail">
<h2>詳細</h2>
<div class="shf-pillars">
<div class="shf-pillar"><h3>単一ファイル</h3><p>配布はファイル 1 個で完結する。</p></div>
<div class="shf-pillar"><h3>依存ゼロ</h3><p>ブラウザー以外に何も要らない。</p></div>
<div class="shf-pillar"><h3>検証可能</h3><p>機械で崩れを検出できる。</p></div>
</div>
<div class="shf-concern">
<p class="shf-worry">端末によって見た目が変わるのでは</p>
<p class="shf-fact">システムフォントを使うため字形は環境依存になる。レイアウトは崩れないよう設計している。</p>
<p class="shf-why">Web フォントを埋め込むと単一ファイルの容量が跳ね上がるため、v1 では採用していない。</p>
</div>
<div class="shf-qa">
<p class="shf-q">印刷できますか</p>
<p class="shf-a">できる。印刷時はサイドナビを落として本文だけを出す。</p>
</div>
</section>
<section id="sources">
<h2>出典</h2>
<ol class="shf-cites">
<li id="ref-1"><span class="shf-cite-title">出典タイトル</span><span class="shf-cite-url">https://example.com/</span></li>
</ol>
<p class="shf-footer">作成: 2026-08 / single-html-forge</p>
</section>
</main>"""

POSTER_BODY = """<main id="shf-root">
<p class="shf-eyebrow">SUMMARY</p>
<h1>1 枚で伝わる見出し</h1>
<p class="shf-lead">読み手が持ち帰る 1 文をここに置く。</p>
<div class="shf-points">
<div class="shf-point"><h3>要点 1</h3><p>短く。長い説明は資料側に置く。</p></div>
<div class="shf-point"><h3>要点 2</h3><p>数値を出すなら単位まで書く。</p></div>
<div class="shf-point"><h3>要点 3</h3><p>行動につながる一言で締める。</p></div>
</div>
<div class="shf-footer"><span>single-html-forge</span><span>2026-08</span></div>
</main>
<button type="button" class="shf-print" data-shf-action="print">PDF として保存</button>"""

BODIES = {"deck": DECK_BODY, "doc": DOC_BODY, "poster": POSTER_BODY}
TITLES = {"deck": "Deck skeleton", "doc": "Doc skeleton", "poster": "Poster skeleton"}

SLIDE_RE = re.compile(
    r'data-slide-id="([^"]+)"[^>]*>\s*(?:<p[^>]*>.*?</p>\s*)?<h[12][^>]*>(.*?)</h[12]>',
    re.S,
)
TAG_RE = re.compile(r"<[^>]+>")


CONTROL_ICONS = {
    "prev": '<path d="m12 19-7-7 7-7M5 12h14"/>',
    "next": '<path d="m12 5 7 7-7 7M19 12H5"/>',
    "outline": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18"/>',
    "fullscreen": '<path d="M8 3H5a2 2 0 0 0-2 2v3m13-5h3a2 2 0 0 1 2 2v3M3 16v3a2 2 0 0 0 2 2h3m13-5v3a2 2 0 0 1-2 2h-3"/>',
    "mute": '<path d="m11 5-6 4H3v6h2l6 4V5m6 4 5 6m0-6-5 6"/>',
}


def outline_nav(body: str) -> str:
    """Build the slide list from the slides themselves, so the two cannot drift."""
    items = []
    for slide_id, heading in SLIDE_RE.findall(body):
        label = TAG_RE.sub("", heading).strip()
        items.append(
            f'<li><button type="button" data-shf-goto="{slide_id}">{label}</button></li>'
        )
    if not items:
        raise SystemExit("outline variant found no slides to list")
    entries = "\n".join(items)
    return (
        '<nav id="shf-outline">\n'
        '<p class="shf-outline-title">SLIDES</p>\n'
        f"<ol>\n{entries}\n</ol>\n"
        "</nav>"
    )


def read_text(path: Path) -> str:
    with open(path, encoding="utf-8", newline="") as handle:
        return handle.read().replace("\r\n", "\n")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build(archetype: str, runtime: str, layout: str = "", title: str = "", body: str = "") -> str:
    css = read_text(CSS_DIR / f"shf-{archetype}.css")
    body = body or BODIES[archetype]
    if archetype == "deck":
        for action, paths in CONTROL_ICONS.items():
            icon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + paths + '</svg>'
            body = re.sub(r'(<button[^>]*data-shf-action="' + action + r'"[^>]*>)[^<]*(</button>)', lambda match: match[1] + icon + match[2], body)
        if '<nav id="shf-outline">' not in body:
            body = outline_nav(body) + "\n" + body
        body = re.sub(r'<section data-slide-id="([^"]+)"', r'<section tabindex="-1" data-slide-id="\1"', body)
        layout_attr = ' data-shf-layout="outline"' + (' class="shf-outline-off"' if not layout else '')
    else:
        layout_attr = ""
    return (
        "<!DOCTYPE html>\n"
        f'<html lang="ja" data-shf-archetype="{archetype}"{layout_attr}'
        f' data-shf-runtime="{RUNTIME_VERSION}" data-shf-css="{CSS_VERSION}">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{title or TITLES[archetype]}</title>\n"
        f'<style id="shf-theme">{THEME[archetype]}</style>\n'
        f'<style id="shf-css">{css}</style>\n'
        "</head>\n"
        "<body>\n"
        f"{body}\n"
        f'<script id="shf-model" type="application/json">{MODEL}</script>\n'
        f'<script id="shf-runtime">{runtime}</script>\n'
        "</body>\n"
        "</html>\n"
    )


def register_hash(entries: dict, version: str, digest: str) -> None:
    if version in entries and entries[version] != digest:
        raise ValueError(f"Version {version} already has a different hash; bump the version")
    entries[version] = digest


def check_runtime_policy(runtime: str) -> None:
    code = re.sub(r"/\*.*?\*/|//[^\n]*", "", runtime, flags=re.S)
    prohibited = r"\b(innerHTML|outerHTML|insertAdjacentHTML|createElement|createElementNS|appendChild|fetch|XMLHttpRequest|WebSocket|Worker|eval|Function|insertRule|replaceSync|setProperty|adoptedStyleSheets)\b|document\.(write|writeln)\b|\bimport\s*\("
    if re.search(prohibited, code):
        raise ValueError("Runtime violates the fixed-player API policy")


def main() -> int:
    runtime = read_text(RUNTIME)
    check_runtime_policy(runtime)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # The registry is append-only. Dropping an old version would report every
    # artifact built before this run as TAMPERED, which is not what happened to it.
    reg_path = HERE / "runtime-registry.json"
    if reg_path.exists():
        registry = json.loads(reg_path.read_text(encoding="utf-8"))
    else:
        registry = {"runtime": {}, "css": {}}
    registry.setdefault("runtime", {})
    registry.setdefault("css", {})

    register_hash(registry["runtime"], RUNTIME_VERSION, sha(runtime))
    for archetype in ("deck", "doc", "poster"):
        register_hash(registry["css"].setdefault(archetype, {}), CSS_VERSION,
                      sha(read_text(CSS_DIR / f"shf-{archetype}.css")))
    for archetype in ("deck", "doc", "poster"):
        css = read_text(CSS_DIR / f"shf-{archetype}.css")
        out = OUT_DIR / f"{archetype}-skeleton.html"
        with open(out, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(build(archetype, runtime))
        print(f"wrote {out.relative_to(SKILL)}")

    outline_body = (
        outline_nav(DECK_BODY)
        + "\n"
        + DECK_BODY.replace(
            '<button type="button" data-shf-action="print">PDF</button>',
            '<button type="button" data-shf-action="outline">目次</button>\n'
            '<button type="button" data-shf-action="print">PDF</button>',
            1,
        )
    )
    out = OUT_DIR / "deck-outline-skeleton.html"
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            build("deck", runtime, layout="outline", title="Deck skeleton (outline)", body=outline_body)
        )
    print(f"wrote {out.relative_to(SKILL)}")

    demo_slides = '''<section data-slide-id="s1" class="is-active">
<p class="shf-eyebrow">SINGLE HTML FORGE / PLAYER</p>
<h1>Ideas, one step at a time.</h1>
<p class="shf-lead">A focused explanation, with the whole story within reach.</p>
</section>
<section data-slide-id="s2" hidden>
<h2>A signal becomes a decision</h2>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 240" width="900" height="240" aria-label="Observe, compare, decide">
<g><rect x="20" y="60" width="230" height="100" rx="8" fill="#dcefe5"/><text x="135" y="120" text-anchor="middle" font-size="28" fill="#20362c">Observe</text></g>
<g data-shf-step="1" data-shf-effect="fade"><path d="M270 110h65" stroke="#34825e" stroke-width="5"/><rect x="350" y="60" width="230" height="100" rx="8" fill="#e3ecf7"/><text x="465" y="120" text-anchor="middle" font-size="28" fill="#20362c">Compare</text></g>
<g data-shf-step="2" data-shf-effect="fade"><path d="M600 110h45" stroke="#34825e" stroke-width="5"/><rect x="660" y="60" width="220" height="100" rx="8" fill="#f4e9c9"/><text x="770" y="120" text-anchor="middle" font-size="28" fill="#20362c">Decide</text></g>
</svg>
<p data-shf-step="1" data-shf-effect="rise">Compare the evidence before choosing a response.</p>
<p data-shf-step="2" data-shf-effect="emphasis">Make the decision and keep its rationale.</p>
</section>
<section data-slide-id="s3" data-shf-print="all" hidden>
<h2>Change the conclusion, not the context</h2>
<p data-shf-step="0" data-shf-until="0">Before: a conclusion without supporting evidence.</p>
<p data-shf-step="1" data-shf-effect="rise">After: a decision linked to observations and alternatives.</p>
<p class="shf-lead">The complete explanation remains in the handout.</p>
</section>
'''
    demo_body = '<main id="shf-root">\n' + demo_slides + DECK_BODY[DECK_BODY.index('<div id="shf-chrome">'):]
    (OUT_DIR / "deck-motion-skeleton.html").write_text(build("deck", runtime, "outline", "Slide player demo", demo_body), encoding="utf-8", newline="\n")

    with open(reg_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(registry, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")
    versions = ", ".join(sorted(registry["runtime"]))
    print(f"wrote {reg_path.relative_to(SKILL)} (runtime versions: {versions})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
