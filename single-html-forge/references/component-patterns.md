# Component patterns

The blocks the fixed CSS already styles. Nothing here needs new CSS; adding any would fail verification.

## Both archetypes

**Callout** — an aside that should not interrupt the sentence flow.

```html
<div class="shf-callout"><p>text</p></div>
<div class="shf-callout is-warn"><p>caveat</p></div>
<div class="shf-callout is-ok"><p>confirmed</p></div>
<div class="shf-callout is-bad"><p>do not do this</p></div>
```

**Table** — wrap it so a wide table scrolls instead of breaking the layout.

```html
<div class="shf-table-wrap">
  <table>
    <thead>
      <tr>
        <th>観点</th>
        <th>A</th>
        <th>B</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>…</td>
        <td>…</td>
        <td>…</td>
      </tr>
    </tbody>
  </table>
</div>
```

Five rows is about the limit on a slide. A doc can carry more.

**Cards**

```html
<div class="shf-grid3">
  <div class="shf-card">
    <h3>見出し</h3>
    <p>本文</p>
  </div>
</div>
```

`shf-grid2` and `shf-grid3` exist; in a deck use `shf-cards`, which fits the column count to what is inside.

**Figure**

```html
<figure>
  <img src="data:image/png;base64,…" alt="説明" data-asset-ref="a1" />
  <figcaption>図 1: 説明</figcaption>
</figure>
```

## Doc only

**Two-column step comparison** — the before/after that carries most of the argument.

```html
<div class="shf-flow">
  <div class="shf-col is-bad">
    <h3>従来</h3>
    <ol>
      <li>手順</li>
    </ol>
  </div>
  <div class="shf-col is-ok">
    <h3>今回</h3>
    <ol>
      <li>手順</li>
    </ol>
  </div>
</div>
```

Keep both columns the same length. Uneven ones read as an unfair comparison.

**Pillars** — three parallel ideas of equal weight.

```html
<div class="shf-pillars">
  <div class="shf-pillar">
    <h3>見出し</h3>
    <p>一文</p>
  </div>
</div>
```

**Concern → fact → why** — for the objection a reader is already holding.

```html
<div class="shf-concern">
  <p class="shf-worry">懸念</p>
  <p class="shf-fact">事実</p>
  <p class="shf-why">背景</p>
</div>
```

Answering the worry before explaining the background is what makes this work. Reversed, the reader stops reading.

**Q&A**

```html
<div class="shf-qa">
  <p class="shf-q">質問</p>
  <p class="shf-a">回答</p>
</div>
```

**Hero** — once, at the top.

```html
<header class="shf-hero">
  <p class="shf-eyebrow">CATEGORY</p>
  <h1>見出し</h1>
  <p class="shf-lead">導入</p>
  <div class="shf-meta"><span class="shf-pill">2026-08</span></div>
</header>
```

## Diagrams

Inline SVG within the subset. Suitable: flows, concept maps, event-order timelines, comparison boxes.

```html
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 120" role="img">
  <title>処理の流れ</title>
  <rect
    x="10"
    y="30"
    width="110"
    height="56"
    rx="8"
    fill="#eef5ff"
    stroke="#0067b8"
  />
  <text x="65" y="64" text-anchor="middle" font-size="14">入力</text>
</svg>
```

Always give a `viewBox` and a `<title>`. Without a viewBox the export can render it at zero size, and Tier 2 fails on that.

**Bar and line charts with a numeric scale are out of scope in v1.** Placing an axis by hand means computing the scale by hand, and a chart that looks plausible while being numerically wrong is worse than a table. Use a table, or wait for the deterministic generator in v2.

## Choosing

| Content                  | Block                                 |
| ------------------------ | ------------------------------------- |
| Two options side by side | table, or `shf-flow` if order matters |
| Three peers              | `shf-pillars` or `shf-grid3`          |
| An objection             | `shf-concern`                         |
| An aside                 | `shf-callout`                         |
| A process                | `shf-flow`, or an SVG if it branches  |
| Numbers                  | a table                               |
