# Artifact Grammar and Allowlist

The normative specification the verifier enforces. Everything here is decidable with the Python standard library.

## Why a lexical preflight exists

`html.parser` is not an HTML5 tree builder. Measured difference:

```
input:       <div><script/>alert(1)</div><p>after</p>
html.parser: [('start','div'), ('startend','script'), ('data','alert(1)'), ('end','div'), ('start','p'), ...]
```

`html.parser` treats `<script/>` as self-closing and reads `alert(1)` as ordinary text. HTML5 does not acknowledge the self-closing flag on raw-text elements, so a browser keeps the script open and treats that same text as script content. Hashing a region located by a parser that disagrees with the browser proves nothing.

The preflight therefore runs **before** any parsing and rejects every construct where the two could disagree. Only input that survives the preflight is parsed.

## 1. Canonical artifact grammar

A conforming artifact satisfies all of the following. Any violation is `FAIL`.

### 1.1 Encoding

- Valid UTF-8, decodable strictly.
- No BOM.
- No NUL byte.
- The only control characters permitted are `\t` (U+0009), `\n` (U+000A), `\r` (U+000D).

### 1.2 Document shell

- Starts with exactly `<!DOCTYPE html>` followed by `\n`.
- Exactly one `<html`, `<head`, `<body` start tag.

### 1.3 Tag syntax

- Tag names are lowercase ASCII letters and digits only.
- Attribute names are lowercase ASCII letters, digits and `-` only.
- **Every attribute value is double-quoted.** Unquoted and single-quoted values are rejected.
- Attribute values contain no `<` and no `"`.
- **No duplicate attribute names within one tag.**
- The self-closing form `/>` is permitted **only** on void elements (`meta`, `br`, `hr`, `img`) and on SVG elements. It is rejected everywhere else.
- Void elements never have an end tag.

### 1.4 Raw-text elements

`script`, `style`, `textarea`, `title` are raw-text elements.

- **The self-closing form is rejected outright** (`<script/>`, `<style/>`, ...). This is the construct that breaks parser agreement.
- Raw-text content is terminated only by the exact lowercase sequence `</script>`, `</style>`, `</textarea>`, `</title>`.
- Raw-text content must not contain the substring `</` followed by the element's own name in any case folding. Escape it (`\u003c/script>` inside JSON) instead.

### 1.5 Comments

- Comments are permitted only in the form `<!--` ... `-->`.
- The content must not contain `--`, `<!`, or `>` immediately after `<!--`.

### 1.6 Character references

- Only named references from a fixed list (`&amp; &lt; &gt; &quot; &#39;`) and numeric references matching `&#[0-9]{1,7};` or `&#x[0-9a-fA-F]{1,6};`.
- Every `&` must begin a valid reference.

## 2. HTML allowlist

Closed world. An element or attribute not listed here is `FAIL` — there is no denylist to keep in sync.

### 2.1 Elements

```
html head meta title style body
main section article header footer nav aside
h1 h2 h3 h4 h5 h6 p ul ol li dl dt dd
table thead tbody tfoot tr th td caption colgroup col
figure figcaption blockquote pre code kbd samp
strong em b i u s small sub sup mark abbr time
span div hr br a img button
template data svg
script
```

`script` is permitted **only** as the two pinned elements in section 4.

### 2.2 Global attributes

```
id class lang dir title hidden role
aria-*            (name matches aria-[a-z-]+)
data-shf-*        (name matches data-shf-[a-z0-9-]+)
```

`style` as an attribute is **not** allowed. `on*` handlers are **not** allowed.

### 2.3 Element-specific attributes

| Element           | Allowed                                     |
| ----------------- | ------------------------------------------- |
| `html`            | `lang`, `data-shf-*`                        |
| `meta`            | `charset`, `name`, `content`                |
| `style`           | `id`                                        |
| `a`               | `href`                                      |
| `img`             | `src`, `alt`, `width`, `height`, `decoding` |
| `th`, `td`        | `colspan`, `rowspan`, `scope`, `headers`    |
| `col`, `colgroup` | `span`                                      |
| `ol`              | `start`, `reversed`, `type`                 |
| `time`            | `datetime`                                  |
| `button`          | `type`, `disabled`                          |
| `data`            | `value`, `data-asset-id`, `data-mime`       |
| `template`        | `id`                                        |
| `script`          | `id`, `type`                                |

### 2.4 URL-bearing attributes

The complete set is `a[href]` and `img[src]`. Nothing else in the allowlist can carry a URL.

- `a[href]`: resolved scheme must be `http` or `https`, or the value is a same-document fragment matching `#[A-Za-z][\w:.-]*`. Resolution uses `urllib.parse.urlsplit` on the decoded value, not a string prefix test, so entity- and whitespace-obfuscated schemes are caught.
- `img[src]`: must be `data:` matching section 5.

### 2.5 Elements that are absent by construction

Because the allowlist is closed, these need no rule and cannot reappear: `object`, `embed`, `iframe`, `video`, `audio`, `source`, `track`, `picture`, `link`, `base`, `form`, `input`, `canvas`, `noscript`, `frame`, `frameset`, `applet`, `marquee`. Likewise `srcset`, `srcdoc`, `poster`, and `http-equiv` are simply not allowed attributes.

## 3. Inline SVG subset

SVG is accepted by allowlist. Anything outside it fails without conversion.

### 3.1 Elements

```
svg g title desc defs symbol
path rect circle ellipse line polyline polygon
text tspan marker linearGradient radialGradient stop clipPath mask
```

### 3.2 Attributes

```
xmlns viewBox width height fill stroke stroke-width stroke-linecap
stroke-linejoin stroke-dasharray opacity fill-opacity stroke-opacity
d x y x1 y1 x2 y2 cx cy r rx ry points transform
text-anchor dominant-baseline font-size font-weight font-family
id class role aria-* offset stop-color stop-opacity
gradientUnits gradientTransform clip-path mask marker-end marker-start
preserveAspectRatio
```

`xmlns` must equal `http://www.w3.org/2000/svg` exactly. It is the only external-looking value permitted anywhere in the document and is recognised as a namespace literal, not a URL.

### 3.3 Excluded from v1

`style`, `use`, `image`, `feImage`, `foreignObject`, `script`, `set`, `animate`, `@font-face`, `filter`, and every `on*` attribute. `use` is excluded because same-document indirection would need its own reachability analysis; `style` and `image` because they reintroduce CSS and a second image carrier.

No attribute value in an SVG subtree may contain `url(`.

## 4. Pinned regions

Exactly these `script` and `style` elements may appear, each at most once, in this order inside their parent.

| Element                                           | Required attributes | Content rule                        |
| ------------------------------------------------- | ------------------- | ----------------------------------- |
| `<style id="shf-theme">`                          | `id`                | Custom properties only, section 6   |
| `<style id="shf-css">`                            | `id`                | SHA-256 must match a registry entry |
| `<script id="shf-model" type="application/json">` | `id`, `type`        | Inert JSON, section 5               |
| `<script id="shf-runtime">`                       | `id`                | SHA-256 must match a registry entry |

`shf-css` and `shf-runtime` are required. `shf-theme` and `shf-model` are optional but at most one each.

Any other `script` or `style` element is `FAIL`, including one that would otherwise be empty. `textarea` is rejected outright: it is a raw-text element with no role in these artifacts.

### 4.1 Version registry

`scripts/runtime-registry.json` maps a declared version to an approved SHA-256. It is **append-only**: `build_skeletons.py` merges into the existing file rather than replacing it, because dropping an old version would report every artifact built before that change as `TAMPERED` when nothing was tampered with. Bump the version when the pinned content changes, and leave the previous entry in place.

```json
{ "runtime": { "1": "<sha256>" }, "css": { "deck": { "1": "<sha256>" } } }
```

`<html>` declares `data-shf-runtime` and `data-shf-css` version values. A declared version absent from the registry yields `UNSUPPORTED_VERSION`, which is distinct from a content hash mismatch (`TAMPERED`). This keeps an older but legitimate artifact from being reported as tampering after the skill updates itself.

## 5. Model and assets

### 5.1 Model

`<script id="shf-model" type="application/json">` is inert data. It is never executed.

- Content must parse as JSON.
- `schemaVersion` must be exactly `1`. Any other value is rejected rather than treated as readable.
- Every `<` in the serialisation is escaped as `\u003c`, so a raw `</script>` can never terminate the block early. A literal `<` in the content is `FAIL`.

### 5.2 Asset closure

In v1 the payload lives exactly once, in the `img`'s own `src` data URI. A separate asset store would hold the same base64 a second time, so v1 does not have one.

Two sets must correspond exactly:

- `model.assets[].id`
- `img[data-asset-ref]` in the document

Rules: ids are unique in each set; every `data-asset-ref` resolves to a declared id; every declared id is referenced. Orphans, duplicates and unregistered references all `FAIL`.

### 5.3 Manifest agrees with bytes

For each asset the manifest `mime` and `sha256` must match the decoded payload of the referencing `img`, and `alt` must equal that element's `alt` attribute. An id match alone does not prove agreement.

### 5.4 Data URI

`img[src]` must be `data:<mime>;base64,<data>` where:

- `mime` is one of `image/png`, `image/jpeg`, `image/webp`
- base64 decodes strictly (`validate=True`)
- the decoded bytes' magic number matches the declared mime
- SVG is **not** permitted as a data URI; use inline SVG (section 3). GIF is out of scope for v1 because its extension blocks would need their own allowlist.

### 5.5 Metadata allowlist

After re-encoding, only these survive. Anything else present is `FAIL`.

| Format | Permitted                                                                      |
| ------ | ------------------------------------------------------------------------------ |
| PNG    | `IHDR`, `PLTE`, `IDAT`, `IEND`, `tRNS`, `gAMA`, `cHRM`, `sRGB`, `bKGD`, `pHYs` |
| JPEG   | SOI, SOF0/1/2, DHT, DQT, SOS, DRI, EOI, APP0 (`JFIF` only)                     |
| WebP   | `VP8 `, `VP8L`, `VP8X`, `ALPH`                                                 |

Allowlisting rather than listing forbidden chunks closes gaps like JPEG APP13/IPTC and PNG `tIME`. EXIF orientation is applied to pixels before the segment is dropped.

## 6. Theme token schema

`<style id="shf-theme">` may contain only a single `:root{...}` block of custom property declarations. No selectors, no at-rules, no `url(`, no `var(`, no `expression`, no `\`.

| Property         | Grammar                            |
| ---------------- | ---------------------------------- |
| `--shf-color-*`  | `#[0-9a-f]{6}`                     |
| `--shf-space-*`  | `-?\d{1,3}(\.\d)?(px\|rem)`        |
| `--shf-size-*`   | `\d{1,4}(\.\d{1,2})?(px\|rem\|ch)` |
| `--shf-scale-*`  | `\d(\.\d{1,3})?`                   |
| `--shf-radius-*` | `\d{1,3}(px\|rem)`                 |
| `--shf-weight-*` | `[1-9]00`                          |
| `--shf-ratio-*`  | `\d{1,2}(\.\d{1,3})?`              |

A property whose name is not covered, or whose value does not match its grammar, is `FAIL`. Values are matched anchored, so trailing junk cannot ride along.

## 7. Runtime dataflow invariants

The pinned runtime is trusted only because its hash is fixed **and** it obeys these invariants. Hash equality proves identity, not safe dataflow, so the invariants are stated here and enforced by fixture.

The runtime must not use, at all:

```
innerHTML  outerHTML  insertAdjacentHTML  document.write  document.writeln
eval  Function  setTimeout(string)  setInterval(string)
style.cssText  setProperty  insertRule  replaceSync  adoptedStyleSheets
createElement  createElementNS  appendChild  fetch  XMLHttpRequest
WebSocket  Worker  importScripts  import(
```

The runtime may only:

- read `dataset`, `getAttribute` for `data-shf-*`, `classList`, `textContent`
- write `classList`, `hidden`, `textContent`, `aria-*`
- call `scrollIntoView`, `focus`, `addEventListener`, `postMessage`, `window.print`
- open a presenter window via `window.open("about:blank", name)` from a user gesture

Because the runtime never creates elements and never writes markup, an artifact value cannot become a new element, a new style rule, or a URL.
