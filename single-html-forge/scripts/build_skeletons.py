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

RUNTIME_VERSION = "3"
CSS_VERSION = "3"

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
<button type="button" data-shf-action="prev">前へ</button>
<span id="shf-slide-counter">1 / 3</span>
<button type="button" data-shf-action="next">次へ</button>
<button type="button" data-shf-action="presenter">発表者</button>
<button type="button" data-shf-action="print">PDF</button>
</div>
</main>
<div id="shf-presenter" hidden>
<div class="shf-presenter-head">
<h4>PRESENTER</h4>
<span id="shf-presenter-clock">00:00</span>
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
    layout_attr = f' data-shf-layout="{layout}"' if layout else ""
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
        f"{body or BODIES[archetype]}\n"
        f'<script id="shf-model" type="application/json">{MODEL}</script>\n'
        f'<script id="shf-runtime">{runtime}</script>\n'
        "</body>\n"
        "</html>\n"
    )


def main() -> int:
    runtime = read_text(RUNTIME)
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

    registry["runtime"][RUNTIME_VERSION] = sha(runtime)
    for archetype in ("deck", "doc", "poster"):
        css = read_text(CSS_DIR / f"shf-{archetype}.css")
        registry["css"].setdefault(archetype, {})[CSS_VERSION] = sha(css)
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

    with open(reg_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(registry, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")
    versions = ", ".join(sorted(registry["runtime"]))
    print(f"wrote {reg_path.relative_to(SKILL)} (runtime versions: {versions})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
