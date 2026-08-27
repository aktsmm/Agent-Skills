#!/usr/bin/env python3
"""Tier 1 verifier for single-html-forge artifacts.

Standard library only. See references/artifact-grammar.md for the normative rules.

The artifact is tokenised by a strict lexer that accepts only the canonical
grammar. `html.parser` is deliberately not used: it disagrees with browsers on
constructs such as `<script/>`, so a region it locates cannot be trusted. Input
that could be read two ways is rejected instead of parsed.

Exit codes: 0 PASS, 1 FAIL, 2 UNVERIFIED.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent

RAW_TEXT = {"script", "style", "textarea", "title"}
VOID = {"meta", "br", "hr", "img", "col"}

ELEMENTS = {
    "html", "head", "meta", "title", "style", "body",
    "main", "section", "article", "header", "footer", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "li", "dl", "dt", "dd",
    "table", "thead", "tbody", "tfoot", "tr", "th", "td", "caption", "colgroup", "col",
    "figure", "figcaption", "blockquote", "pre", "code", "kbd", "samp",
    "strong", "em", "b", "i", "u", "s", "small", "sub", "sup", "mark", "abbr", "time",
    "span", "div", "hr", "br", "a", "img", "button",
    "template", "data", "script",
}

GLOBAL_ATTRS = {"id", "class", "lang", "dir", "title", "hidden", "role"}

ELEMENT_ATTRS = {
    "html": {"lang"},
    "meta": {"charset", "name", "content"},
    "style": {"id"},
    "a": {"href"},
    "img": {"src", "alt", "width", "height", "decoding"},
    "th": {"colspan", "rowspan", "scope", "headers"},
    "td": {"colspan", "rowspan", "scope", "headers"},
    "col": {"span"},
    "colgroup": {"span"},
    "ol": {"start", "reversed", "type"},
    "time": {"datetime"},
    "button": {"type", "disabled"},
    "data": {"value", "data-asset-id", "data-mime"},
    "template": {"id"},
    "script": {"id", "type"},
}

SVG_ELEMENTS = {
    "svg", "g", "title", "desc", "defs", "symbol",
    "path", "rect", "circle", "ellipse", "line", "polyline", "polygon",
    "text", "tspan", "marker", "lineargradient", "radialgradient", "stop",
    "clippath", "mask",
}

SVG_ATTRS = {
    "xmlns", "viewbox", "width", "height", "fill", "stroke", "stroke-width",
    "stroke-linecap", "stroke-linejoin", "stroke-dasharray", "opacity",
    "fill-opacity", "stroke-opacity", "d", "x", "y", "x1", "y1", "x2", "y2",
    "cx", "cy", "r", "rx", "ry", "points", "transform", "text-anchor",
    "dominant-baseline", "font-size", "font-weight", "font-family",
    "id", "class", "role", "offset", "stop-color", "stop-opacity",
    "gradientunits", "gradienttransform", "clip-path", "mask",
    "marker-end", "marker-start", "preserveaspectratio",
}

SVG_NS = "http://www.w3.org/2000/svg"

TOKEN_GRAMMAR = [
    (re.compile(r"^--shf-color-[a-z0-9-]+$"), re.compile(r"^#[0-9a-f]{6}$")),
    (re.compile(r"^--shf-space-[a-z0-9-]+$"), re.compile(r"^-?\d{1,3}(\.\d)?(px|rem)$")),
    (re.compile(r"^--shf-size-[a-z0-9-]+$"), re.compile(r"^\d{1,4}(\.\d{1,2})?(px|rem|ch)$")),
    (re.compile(r"^--shf-scale-[a-z0-9-]+$"), re.compile(r"^\d(\.\d{1,3})?$")),
    (re.compile(r"^--shf-radius-[a-z0-9-]+$"), re.compile(r"^\d{1,3}(px|rem)$")),
    (re.compile(r"^--shf-weight-[a-z0-9-]+$"), re.compile(r"^[1-9]00$")),
    (re.compile(r"^--shf-ratio-[a-z0-9-]+$"), re.compile(r"^\d{1,2}(\.\d{1,3})?$")),
]

MAGIC = {
    "image/png": lambda b: b.startswith(b"\x89PNG\r\n\x1a\n"),
    "image/jpeg": lambda b: b.startswith(b"\xff\xd8\xff"),
    "image/webp": lambda b: b.startswith(b"RIFF") and b[8:12] == b"WEBP",
}

PNG_ALLOWED = {b"IHDR", b"PLTE", b"IDAT", b"IEND", b"tRNS", b"gAMA", b"cHRM", b"sRGB", b"bKGD", b"pHYs"}
JPEG_ALLOWED = {0xC0, 0xC1, 0xC2, 0xC4, 0xDB, 0xDA, 0xDD, 0xD9, 0xD8, 0xE0}
WEBP_ALLOWED = {b"VP8 ", b"VP8L", b"VP8X", b"ALPH"}

NAMED_REFS = {"amp", "lt", "gt", "quot", "apos", "nbsp"}
REF_RE = re.compile(r"&(?:([a-z]+)|#(\d{1,7})|#x([0-9a-fA-F]{1,6}));")

FRAGMENT_RE = re.compile(r"^#[A-Za-z][\w:.-]*$")


class Fail(Exception):
    pass


class Unsupported(Exception):
    pass


@dataclass
class Tag:
    name: str
    attrs: dict
    self_closing: bool
    pos: int


@dataclass
class Raw:
    name: str
    attrs: dict
    content: str
    pos: int


@dataclass
class Report:
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def error(self, code: str, msg: str) -> None:
        self.errors.append(f"[{code}] {msg}")

    def warn(self, code: str, msg: str) -> None:
        self.warnings.append(f"[{code}] {msg}")


# --------------------------------------------------------------------------
# canonical lexer
# --------------------------------------------------------------------------

# SVG names are camelCase (viewBox, foreignObject, linearGradient), so the lexer
# accepts mixed case and the lowercase rule for HTML is enforced during the walk.
NAME_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*")
ATTR_NAME_RE = re.compile(r"[A-Za-z][A-Za-z0-9:-]*")


def lex(text: str) -> list:
    """Tokenise the canonical subset. Raises Fail on anything ambiguous."""
    tokens = []
    i = 0
    n = len(text)
    svg_depth = 0
    if not text.startswith("<!DOCTYPE html>\n"):
        raise Fail("document must start with '<!DOCTYPE html>' followed by a newline")
    i = len("<!DOCTYPE html>\n")

    while i < n:
        lt = text.find("<", i)
        if lt == -1:
            check_text(text[i:])
            break
        if lt > i:
            check_text(text[i:lt])
        if text.startswith("<!--", lt):
            end = text.find("-->", lt + 4)
            if end == -1:
                raise Fail("unterminated comment")
            body = text[lt + 4:end]
            if "--" in body or body.startswith(">") or body.startswith("->"):
                raise Fail("non-canonical comment content")
            i = end + 3
            continue
        if text.startswith("<!", lt):
            raise Fail("markup declaration other than the leading doctype")
        if text.startswith("</", lt):
            m = NAME_RE.match(text, lt + 2)
            if not m:
                raise Fail(f"malformed end tag at offset {lt}")
            name = m.group(0)
            if not text.startswith(">", m.end()):
                raise Fail(f"end tag '{name}' must close immediately with '>'")
            if name.lower() == "svg":
                svg_depth -= 1
            tokens.append(("end", name, lt))
            i = m.end() + 1
            continue

        tag, i = lex_start_tag(text, lt)
        lname = tag.name.lower()
        in_svg = svg_depth > 0 or lname == "svg"
        if lname in RAW_TEXT and tag.self_closing:
            raise Fail(
                f"'{tag.name}' is a raw-text element and must not use the self-closing form; "
                "browsers keep it open while naive parsers do not"
            )
        if tag.self_closing and not in_svg and lname not in VOID:
            raise Fail(f"self-closing syntax is not allowed on '{tag.name}'")
        if lname in RAW_TEXT and not tag.self_closing:
            closer = f"</{lname}>"
            end = text.find(closer, i)
            if end == -1:
                raise Fail(f"unterminated raw-text element '{tag.name}'")
            content = text[i:end]
            if f"</{lname}" in content.lower():
                raise Fail(f"raw-text content of '{tag.name}' contains its own end tag")
            tokens.append(("raw", Raw(lname, tag.attrs, content, tag.pos)))
            i = end + len(closer)
            continue
        if lname == "svg" and not tag.self_closing:
            svg_depth += 1
        tokens.append(("start", tag))
    return tokens


def lex_start_tag(text: str, lt: int):
    m = NAME_RE.match(text, lt + 1)
    if not m:
        raise Fail(f"malformed start tag at offset {lt}")
    name = m.group(0)
    i = m.end()
    attrs = {}
    self_closing = False
    while True:
        j = i
        while j < len(text) and text[j] in " \t\r\n":
            j += 1
        if j >= len(text):
            raise Fail(f"unterminated start tag '{name}'")
        if text.startswith("/>", j):
            self_closing = True
            i = j + 2
            break
        if text[j] == ">":
            i = j + 1
            break
        if j == i:
            raise Fail(f"missing whitespace between attributes in '{name}'")
        am = ATTR_NAME_RE.match(text, j)
        if not am:
            raise Fail(f"malformed attribute in '{name}' at offset {j}")
        attr = am.group(0)
        if attr in attrs:
            raise Fail(f"duplicate attribute '{attr}' on '{name}'")
        k = am.end()
        if k < len(text) and text[k] == "=":
            if k + 1 >= len(text) or text[k + 1] != '"':
                raise Fail(f"attribute '{attr}' on '{name}' must use a double-quoted value")
            close = text.find('"', k + 2)
            if close == -1:
                raise Fail(f"unterminated attribute value for '{attr}'")
            value = text[k + 2:close]
            if "<" in value:
                raise Fail(f"attribute '{attr}' value contains '<'")
            check_text(value)
            attrs[attr] = value
            i = close + 1
        else:
            attrs[attr] = ""
            i = k
    return Tag(name, attrs, self_closing, lt), i


def check_text(chunk: str) -> None:
    for ch in chunk:
        o = ord(ch)
        if o == 0 or (o < 32 and ch not in "\t\n\r"):
            raise Fail("control character in document text")
    pos = 0
    while True:
        amp = chunk.find("&", pos)
        if amp == -1:
            return
        m = REF_RE.match(chunk, amp)
        if not m:
            raise Fail("'&' that does not start a valid character reference")
        if m.group(1) and m.group(1) not in NAMED_REFS:
            raise Fail(f"unsupported named character reference '&{m.group(1)};'")
        pos = m.end()


# --------------------------------------------------------------------------
# structure and allowlist
# --------------------------------------------------------------------------

def attr_allowed(tag: str, attr: str, in_svg: bool) -> bool:
    if in_svg:
        low = attr.lower()
        if low.startswith("on"):
            return False
        return low in SVG_ATTRS or low.startswith("aria-") or low.startswith("data-shf-")
    if attr in GLOBAL_ATTRS:
        return True
    if re.fullmatch(r"aria-[a-z-]+", attr):
        return True
    if re.fullmatch(r"data-shf-[a-z0-9-]+", attr):
        return True
    if attr in {"data-slide-id", "data-asset-ref", "data-citation-id", "data-shf-navlink"}:
        return True
    return attr in ELEMENT_ATTRS.get(tag, set())


def walk(tokens: list, rep: Report) -> dict:
    stack = []
    svg_depth = 0
    ctx = {
        "pinned": {},
        "asset_refs": [],
        "asset_payloads": [],
        "img_srcs": [],
        "hrefs": [],
        "slide_ids": [],
        "goto_targets": [],
        "root_attrs": {},
    }
    for token in tokens:
        kind = token[0]
        if kind == "raw":
            raw: Raw = token[1]
            handle_raw(raw, rep, ctx)
            continue
        if kind == "end":
            name = token[1]
            if name in VOID:
                rep.error("STRUCT", f"void element '{name}' must not have an end tag")
                continue
            if not stack or stack[-1] != name:
                rep.error("STRUCT", f"unbalanced end tag '{name}'")
                return ctx
            stack.pop()
            if name == "svg":
                svg_depth -= 1
            continue

        tag: Tag = token[1]
        in_svg = svg_depth > 0
        lname = tag.name.lower()
        if in_svg or lname == "svg":
            if lname not in SVG_ELEMENTS:
                rep.error("SVG_ELEMENT", f"'{tag.name}' is not in the SVG subset")
        else:
            if tag.name != lname:
                rep.error("CANONICAL", f"HTML tag name '{tag.name}' must be lowercase")
            if lname not in ELEMENTS:
                rep.error("ELEMENT", f"'{tag.name}' is not in the HTML allowlist")

        for attr, value in tag.attrs.items():
            if not (in_svg or lname == "svg") and attr != attr.lower():
                rep.error("CANONICAL", f"HTML attribute name '{attr}' must be lowercase")
            if not attr_allowed(lname, attr, in_svg or lname == "svg"):
                rep.error("ATTR", f"attribute '{attr}' is not allowed on '{tag.name}'")
            if in_svg or lname == "svg":
                if "url(" in value.lower():
                    rep.error("SVG_URL", f"SVG attribute '{attr}' contains 'url('")
                if attr == "xmlns" and value != SVG_NS:
                    rep.error("SVG_NS", f"xmlns must be exactly {SVG_NS}")

        if lname == "html":
            ctx["root_attrs"] = dict(tag.attrs)
        if "data-slide-id" in tag.attrs:
            ctx["slide_ids"].append(tag.attrs["data-slide-id"])
        if "data-shf-goto" in tag.attrs:
            ctx["goto_targets"].append(tag.attrs["data-shf-goto"])
        if lname == "img":
            ref = tag.attrs.get("data-asset-ref", "")
            ctx["img_srcs"].append((tag.attrs.get("src", ""), tag.attrs.get("alt"), ref))
            if "alt" not in tag.attrs:
                rep.error("ALT", "img without an alt attribute")
            if ref:
                ctx["asset_refs"].append(ref)
                ctx["asset_payloads"].append(
                    (ref, tag.attrs.get("src", ""), tag.attrs.get("alt", ""))
                )
        if lname == "a" and "href" in tag.attrs:
            ctx["hrefs"].append(tag.attrs["href"])

        if lname == "svg":
            svg_depth += 1
        if not tag.self_closing and lname not in VOID:
            stack.append(lname)

    if stack:
        rep.error("STRUCT", f"unclosed elements: {', '.join(reversed(stack))}")
    return ctx


def handle_raw(raw: Raw, rep: Report, ctx: dict) -> None:
    if raw.name == "title":
        return
    if raw.name == "textarea":
        rep.error("ELEMENT", "textarea is not allowed")
        return
    ident = raw.attrs.get("id", "")
    if raw.name == "style":
        if ident not in {"shf-theme", "shf-css"}:
            rep.error("PINNED", f"style element with id '{ident}' is not one of the pinned regions")
            return
    elif raw.name == "script":
        if ident == "shf-model":
            if raw.attrs.get("type") != "application/json":
                rep.error("PINNED", "shf-model must declare type=\"application/json\"")
        elif ident != "shf-runtime":
            rep.error("PINNED", f"script element with id '{ident}' is not one of the pinned regions")
            return
    if ident in ctx["pinned"]:
        rep.error("PINNED", f"duplicate pinned region '{ident}'")
    ctx["pinned"][ident] = raw


# --------------------------------------------------------------------------
# individual checks
# --------------------------------------------------------------------------

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_pinned(ctx: dict, registry: dict, rep: Report) -> None:
    root = ctx["root_attrs"]
    for ident, kind in (("shf-css", "css"), ("shf-runtime", "runtime")):
        raw = ctx["pinned"].get(ident)
        if raw is None:
            rep.error("PINNED", f"required region '{ident}' is missing")
            continue
        declared = root.get("data-shf-css" if kind == "css" else "data-shf-runtime")
        if not declared:
            rep.error("PINNED", f"<html> must declare data-shf-{kind}")
            continue
        if kind == "css":
            archetype = root.get("data-shf-archetype", "")
            approved = registry.get("css", {}).get(archetype, {})
        else:
            approved = registry.get("runtime", {})
        if declared not in approved:
            raise Unsupported(f"{kind} version '{declared}' is not in the registry")
        actual = sha(raw.content.encode("utf-8"))
        if actual != approved[declared]:
            rep.error("TAMPERED", f"{ident} content does not match the approved hash for version {declared}")


def check_theme(ctx: dict, rep: Report) -> None:
    raw = ctx["pinned"].get("shf-theme")
    if raw is None:
        return
    body = raw.content.strip()
    m = re.fullmatch(r":root\s*\{(.*)\}", body, re.S)
    if not m:
        rep.error("THEME", "shf-theme must contain exactly one :root { ... } block")
        return
    inner = m.group(1)
    for bad in ("url(", "var(", "expression", "\\", "@", "<"):
        if bad in inner:
            rep.error("THEME", f"shf-theme contains forbidden token '{bad}'")
    for decl in inner.split(";"):
        decl = decl.strip()
        if not decl:
            continue
        if ":" not in decl:
            rep.error("THEME", f"malformed declaration '{decl}'")
            continue
        prop, value = decl.split(":", 1)
        prop, value = prop.strip(), value.strip()
        for name_re, value_re in TOKEN_GRAMMAR:
            if name_re.fullmatch(prop):
                if not value_re.fullmatch(value):
                    rep.error("THEME", f"value '{value}' is not valid for '{prop}'")
                break
        else:
            rep.error("THEME", f"custom property '{prop}' has no declared grammar")


def parse_model(ctx: dict, rep: Report) -> dict:
    raw = ctx["pinned"].get("shf-model")
    if raw is None:
        return {"schemaVersion": 1, "assets": []}
    if "<" in raw.content:
        rep.error("MODEL", "shf-model contains a literal '<'; it must be escaped as \\u003c")
    try:
        model = json.loads(raw.content)
    except json.JSONDecodeError as exc:
        rep.error("MODEL", f"shf-model is not valid JSON: {exc}")
        return {"schemaVersion": 1, "assets": []}
    if model.get("schemaVersion") != 1:
        rep.error("MODEL", f"unsupported schemaVersion {model.get('schemaVersion')!r}; only 1 is readable")
    if not isinstance(model.get("assets", []), list):
        rep.error("MODEL", "assets must be a list")
        model["assets"] = []
    return model


def decode_data_uri(value: str):
    m = re.fullmatch(r"data:([a-z]+/[a-z0-9.+-]+);base64,([A-Za-z0-9+/=]+)", value)
    if not m:
        raise Fail("img src must be a base64 data URI")
    mime = m.group(1)
    try:
        payload = base64.b64decode(m.group(2), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise Fail(f"data URI does not decode: {exc}")
    return mime, payload


def check_metadata(mime: str, payload: bytes) -> list:
    problems = []
    if mime == "image/png":
        i = 8
        while i + 8 <= len(payload):
            length = int.from_bytes(payload[i:i + 4], "big")
            ctype = payload[i + 4:i + 8]
            if ctype not in PNG_ALLOWED:
                problems.append(f"PNG chunk '{ctype.decode('ascii', 'replace')}' is not in the allowlist")
            i += 12 + length
    elif mime == "image/jpeg":
        i = 2
        while i + 4 <= len(payload):
            if payload[i] != 0xFF:
                break
            marker = payload[i + 1]
            if marker == 0xD9:
                break
            if marker not in JPEG_ALLOWED:
                problems.append(f"JPEG segment 0xFF{marker:02X} is not in the allowlist")
            seglen = int.from_bytes(payload[i + 2:i + 4], "big")
            if marker == 0xDA:
                break
            i += 2 + seglen
    elif mime == "image/webp":
        i = 12
        while i + 8 <= len(payload):
            ctype = payload[i:i + 4]
            length = int.from_bytes(payload[i + 4:i + 8], "little")
            if ctype not in WEBP_ALLOWED:
                problems.append(f"WebP chunk '{ctype.decode('ascii', 'replace')}' is not in the allowlist")
            i += 8 + length + (length & 1)
    return problems


def check_assets(ctx: dict, model: dict, budget: dict, rep: Report) -> None:
    """Close the manifest against the images that actually carry the bytes.

    In v1 the payload lives once, in the img's own data URI. A separate asset
    store would hold the same base64 a second time.
    """
    declared = [a for a in model.get("assets", []) if isinstance(a, dict)]
    declared_ids = [a.get("id") for a in declared]
    ref_ids = list(ctx["asset_refs"])

    if len(declared_ids) != len(set(declared_ids)):
        rep.error("ASSET", "duplicate asset ids in the manifest")
    if len(ref_ids) != len(set(ref_ids)):
        rep.error("ASSET", "duplicate data-asset-ref values")
    for ref in ref_ids:
        if ref not in declared_ids:
            rep.error("ASSET", f"data-asset-ref '{ref}' is not declared in the manifest")
    for aid in declared_ids:
        if aid not in ref_ids:
            rep.error("ASSET", f"manifest asset '{aid}' is never referenced")

    by_id = {a.get("id"): a for a in declared}
    per_image_max = budget["perImageBytes"]["fail"]
    per_image_warn = budget["perImageBytes"]["warn"]

    for aid, value, alt in ctx["asset_payloads"]:
        try:
            mime, payload = decode_data_uri(value)
        except Fail as exc:
            rep.error("ASSET", f"asset '{aid}': {exc}")
            continue
        size = len(value.encode("utf-8"))
        if size > per_image_max:
            rep.error("BUDGET", f"asset '{aid}' is {size} bytes, over the hard limit {per_image_max}")
        elif size > per_image_warn:
            rep.warn("BUDGET", f"asset '{aid}' is {size} bytes, over the warning threshold {per_image_warn}")
        checker = MAGIC.get(mime)
        if checker is None:
            rep.error("ASSET", f"asset '{aid}' declares unsupported mime '{mime}'")
            continue
        if not checker(payload):
            rep.error("MIME", f"asset '{aid}' declares '{mime}' but the bytes do not match that format")
            continue
        for problem in check_metadata(mime, payload):
            rep.error("METADATA", f"asset '{aid}': {problem}")
        manifest = by_id.get(aid)
        if manifest is None:
            continue
        if manifest.get("mime") != mime:
            rep.error("ASSET", f"asset '{aid}' manifest mime '{manifest.get('mime')}' disagrees with the payload")
        if manifest.get("sha256") and manifest["sha256"] != sha(payload):
            rep.error("ASSET", f"asset '{aid}' manifest sha256 does not match the payload")
        if manifest.get("alt") is not None and manifest["alt"] != alt:
            rep.error("ASSET", f"asset '{aid}' manifest alt disagrees with the alt attribute")


def check_navigation(ctx: dict, rep: Report) -> None:
    """The outline list is authored, not generated, so it can drift from the slides."""
    slides = ctx["slide_ids"]
    if len(slides) != len(set(slides)):
        rep.error("NAV", "duplicate data-slide-id values")
    targets = ctx["goto_targets"]
    if len(targets) != len(set(targets)):
        rep.error("NAV", "duplicate data-shf-goto values")
    for target in targets:
        if target not in slides:
            rep.error("NAV", f"data-shf-goto '{target}' does not match any slide")
    if ctx["root_attrs"].get("data-shf-layout") == "outline":
        missing = [s for s in slides if s not in targets]
        if missing:
            rep.error(
                "NAV",
                "outline layout is missing list entries for: " + ", ".join(missing),
            )


def check_urls(ctx: dict, rep: Report) -> None:
    for href in ctx["hrefs"]:
        value = html_unescape(href).strip()
        if FRAGMENT_RE.fullmatch(value):
            continue
        parts = urlsplit(value)
        if parts.scheme.lower() not in {"http", "https"}:
            rep.error("URL", f"href '{href}' resolves to scheme '{parts.scheme}'; only http and https are allowed")

    # Every image is validated here, not only the ones the manifest knows about.
    # Validating only referenced images let a malformed data URI through.
    for src, _alt, ref in ctx["img_srcs"]:
        if not src.startswith("data:"):
            rep.error("IMG", f"img src '{src[:40]}' is not a data URI")
            continue
        try:
            mime, payload = decode_data_uri(src)
        except Fail as exc:
            rep.error("IMG", f"img src is not a usable data URI: {exc}")
            continue
        checker = MAGIC.get(mime)
        if checker is None:
            rep.error("IMG", f"img declares unsupported mime '{mime}'")
        elif not checker(payload):
            rep.error("MIME", f"img declares '{mime}' but the bytes do not match that format")
        if not ref:
            rep.error("ASSET", "img without data-asset-ref; every image must be declared in the model")


def html_unescape(value: str) -> str:
    def repl(m):
        if m.group(1):
            return {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'", "nbsp": "\u00a0"}[m.group(1)]
        if m.group(2):
            return chr(int(m.group(2)))
        return chr(int(m.group(3), 16))
    return REF_RE.sub(repl, value)


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify(path: Path, registry: dict, budget: dict) -> Report:
    rep = Report()
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        rep.error("ENCODING", "file starts with a UTF-8 BOM")
        return rep
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        rep.error("ENCODING", f"file is not valid UTF-8: {exc}")
        return rep

    # A browser reads CRLF and LF the same way, and Windows editors and git
    # checkout both produce CRLF. Normalise before lexing and hashing so a line
    # ending can never decide PASS or FAIL.
    text = text.replace("\r\n", "\n")
    if "\r" in text:
        rep.error("ENCODING", "stray carriage return outside a CRLF pair")
        return rep

    whole = len(data)
    if whole > budget["wholeFileBytes"]["fail"]:
        rep.error("BUDGET", f"file is {whole} bytes, over the hard limit {budget['wholeFileBytes']['fail']}")
    elif whole > budget["wholeFileBytes"]["warn"]:
        rep.warn("BUDGET", f"file is {whole} bytes, over the warning threshold {budget['wholeFileBytes']['warn']}")

    try:
        tokens = lex(text)
    except Fail as exc:
        rep.error("CANONICAL", str(exc))
        return rep

    ctx = walk(tokens, rep)
    try:
        check_pinned(ctx, registry, rep)
    except Unsupported as exc:
        rep.error("UNSUPPORTED_VERSION", str(exc))
        return rep
    check_theme(ctx, rep)
    model = parse_model(ctx, rep)
    check_assets(ctx, model, budget, rep)
    check_navigation(ctx, rep)
    check_urls(ctx, rep)
    return rep


def run_tier2(path: Path, rep: Report) -> str:
    """Runtime checks. Returns 'ok', 'unavailable', or 'failed'.

    Completion is event-based: every slide is visited and every image is waited
    on. Nothing here is cut short by a timer, because a timed sample would let a
    slow image or a late state escape inspection.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return "unavailable"

    problems = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 900})
        blocked = []
        page.on("console", lambda m: problems.append(f"console {m.type}: {m.text}") if m.type == "error" else None)
        page.on("pageerror", lambda e: problems.append(f"page error: {e}"))
        # No egress at all during verification; citations are checked statically.
        page.route("**/*", lambda route: (
            route.continue_() if route.request.url.startswith("file:")
            else (blocked.append(route.request.url), route.abort())
        ))
        page.goto(path.resolve().as_uri(), wait_until="load")
        page.wait_for_function("document.fonts ? document.fonts.status === 'loaded' : true")

        states = page.evaluate("document.querySelectorAll('[data-slide-id]').length") or 1
        if states > 1:
            page.keyboard.press("Home")
        for i in range(states):
            if states > 1 and i:
                # Advance through the real navigation path so chrome state is checked too.
                page.keyboard.press("ArrowRight")
            page.wait_for_function(
                "Array.from(document.images).every(function (i) { return i.complete; })"
            )
            broken = page.evaluate(
                "Array.from(document.images)"
                ".filter(function (i) { return i.naturalWidth === 0 || i.naturalHeight === 0; })"
                ".map(function (i) { return i.alt || '(no alt)'; })"
            )
            for alt in broken:
                problems.append(f"state {i}: image '{alt}' decoded to zero size")
            bad_svg = page.evaluate(
                "Array.from(document.querySelectorAll('svg')).filter(function (s) {"
                " var b = s.getBoundingClientRect();"
                " return !s.getAttribute('viewBox') || b.width === 0 || b.height === 0; }).length"
            )
            if bad_svg:
                problems.append(f"state {i}: {bad_svg} inline svg without a viewBox or with zero size")
            overflow = page.evaluate(
                "(function () { var r = document.getElementById('shf-root') || document.body;"
                " return [r.scrollWidth - r.clientWidth, r.scrollHeight - r.clientHeight]; })()"
            )
            if overflow[0] > 2 or overflow[1] > 2:
                problems.append(
                    f"state {i}: content overflows by {overflow[0]}x{overflow[1]} px at 1600x900"
                )
        browser.close()

    for url in blocked:
        problems.append(f"external request attempted: {url}")
    for problem in problems:
        rep.error("TIER2", problem)
    return "failed" if problems else "ok"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Tier 1 verifier for single-html-forge artifacts")
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--registry", type=Path, default=HERE / "runtime-registry.json")
    ap.add_argument("--budget", type=Path, default=HERE / "budget.json")
    ap.add_argument("--tier2", action="store_true", help="also run the browser checks")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    registry = load_json(args.registry)
    budget = load_json(args.budget)

    worst = 0
    for path in args.paths:
        rep = verify(path, registry, budget)
        unsupported = any(e.startswith("[UNSUPPORTED_VERSION]") for e in rep.errors)
        status = "PASS" if not rep.errors else ("UNVERIFIED" if unsupported else "FAIL")
        if status == "PASS" and args.tier2:
            outcome = run_tier2(path, rep)
            if outcome == "unavailable":
                status = "UNVERIFIED"
                rep.warn("TIER2", "Playwright is not installed, so the browser checks did not run")
            elif outcome == "failed":
                status = "FAIL"
        if not args.quiet or rep.errors:
            print(f"{status}  {path}")
            for line in rep.errors:
                print(f"    {line}")
            for line in rep.warnings:
                print(f"    warn {line}")
        if status == "FAIL":
            worst = max(worst, 1)
        elif status == "UNVERIFIED":
            worst = max(worst, 2)
    return worst


if __name__ == "__main__":
    sys.exit(main())
