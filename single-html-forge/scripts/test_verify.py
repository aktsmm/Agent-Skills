#!/usr/bin/env python3
"""Fixture suite for verify_html.

Standard library only. Negative fixtures prove the allowlist has no hole;
positive fixtures prove the extractor actually finds things, so that a PASS
cannot be an empty scan in disguise.

Run: python scripts/test_verify.py
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))

import verify_html as V  # noqa: E402

REGISTRY = json.loads((HERE / "runtime-registry.json").read_text(encoding="utf-8"))
BUDGET = json.loads((HERE / "budget.json").read_text(encoding="utf-8"))
SKELETON = (SKILL / "assets" / "skeletons" / "deck-skeleton.html").read_text(encoding="utf-8")
OUTLINE = (SKILL / "assets" / "skeletons" / "deck-outline-skeleton.html").read_text(
    encoding="utf-8"
)


def tiny_png(extra_chunk: bytes = b"") -> bytes:
    def chunk(ctype: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + ctype
            + data
            + struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 0, 0, 0, 0)
    idat = zlib.compress(b"\x00\x00")
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + extra_chunk
        + chunk(b"IDAT", idat)
        + chunk(b"IEND", b"")
    )


def png_with_text() -> bytes:
    data = b"Comment\x00secret tenant name"
    body = struct.pack(">I", len(data)) + b"tEXt" + data
    body += struct.pack(">I", zlib.crc32(b"tEXt" + data) & 0xFFFFFFFF)
    return tiny_png(body)


def data_uri(mime: str, payload: bytes) -> str:
    import base64

    return f"data:{mime};base64,{base64.b64encode(payload).decode('ascii')}"


def run(text: str, budget=None, registry=None) -> V.Report:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "artifact.html"
        path.write_text(text, encoding="utf-8", newline="")
        return V.verify(path, registry or REGISTRY, budget or BUDGET)


def codes(rep: V.Report) -> set:
    return {line.split("]")[0].lstrip("[") for line in rep.errors}


def with_body(fragment: str) -> str:
    """Insert a fragment just before the model script of the good skeleton."""
    marker = '<script id="shf-model"'
    return SKELETON.replace(marker, fragment + "\n" + marker, 1)


def with_model(model: str) -> str:
    start = SKELETON.index('<script id="shf-model" type="application/json">')
    open_len = len('<script id="shf-model" type="application/json">')
    end = SKELETON.index("</script>", start)
    return SKELETON[: start + open_len] + model + SKELETON[end:]


class RegistryTests(unittest.TestCase):
    def test_print_rewrites_links_and_accessible_references(self):
        import derived_assets as derived
        fragment = '<p id="evidence">Evidence</p><a href="#evidence" aria-describedby="evidence">Read evidence</a><label for="choice">Choice</label><input id="choice" type="checkbox">'
        source = SKELETON.replace('<h2>比較</h2>', '<h2>比較</h2>' + fragment)
        printed, _ = derived.print_markup(source)
        self.assertIn('id="shf-print-3-0-evidence"', printed)
        self.assertIn('href="#shf-print-3-0-evidence"', printed)
        self.assertIn('aria-describedby="shf-print-3-0-evidence"', printed)
        self.assertIn('for="shf-print-3-0-choice"', printed)
        self.assertEqual(run(derived.finalize(source, [])).errors, [])

    def test_print_svg_name_and_decoration_survive(self):
        import derived_assets as derived
        diagram = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 80" aria-labelledby="chart-title" aria-describedby="chart-desc"><title id="chart-title">Revenue</title><desc id="chart-desc">A comparison</desc><circle aria-hidden="true" cx="40" cy="40" r="10"/></svg>'
        source = SKELETON.replace('<h2>比較</h2>', '<h2>比較</h2>' + diagram)
        printed, _ = derived.print_markup(source)
        self.assertIn('aria-labelledby="shf-print-3-0-chart-title"', printed)
        self.assertIn('aria-describedby="shf-print-3-0-chart-desc"', printed)
        self.assertIn('<title id="shf-print-3-0-chart-title">Revenue</title>', printed)
        self.assertIn('<circle aria-hidden="true"', printed)
        self.assertEqual(run(derived.finalize(source, [])).errors, [])
        with self.assertRaisesRegex(ValueError, 'Duplicate slide content id'):
            derived.print_markup(source.replace('<desc id="chart-desc">', '<desc id="chart-title">'))

    def test_print_refs_across_pages_and_steps(self):
        import derived_assets as derived
        source = SKELETON.replace('<section tabindex="-1" data-slide-id="s2" hidden>', '<section tabindex="-1" data-slide-id="s2" data-shf-print="all" hidden>')
        source = source.replace('<h2>3 つの論点</h2>', '<h2 id="destination">3 つの論点</h2><p data-shf-step="1" aria-labelledby="destination">Step</p>')
        source = source.replace('<h2>比較</h2>', '<h2>比較</h2><a href="#destination">Earlier page</a><a href="https://example.com/#destination">External</a>')
        printed, _ = derived.print_markup(source)
        self.assertIn('aria-labelledby="shf-print-2-1-destination"', printed)
        self.assertIn('href="#shf-print-2-0-destination"', printed)
        self.assertIn('href="https://example.com/#destination"', printed)
        self.assertEqual(run(derived.finalize(source, [])).errors, [])

    def test_print_missing_or_omitted_references_fail(self):
        import derived_assets as derived
        for fragment in ['<a href="#missing">Missing</a>', '<p id="notes" data-shf-notes>Private note</p><a href="#notes">Omitted</a>', '<p id="hidden-target" hidden>Hidden</p><a href="#hidden-target">Hidden</a>']:
            with self.subTest(fragment=fragment), self.assertRaisesRegex(ValueError, 'Print reference has no visible target'):
                derived.print_markup(SKELETON.replace('<h2>比較</h2>', '<h2>比較</h2>' + fragment))

    def test_test_methods_are_discoverable(self):
        import ast
        nested = []
        for path in HERE.glob('test_*.py'):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test_') and not isinstance(parents.get(node), ast.ClassDef):
                    nested.append(f'{path.name}:{node.lineno} {node.name}')
        self.assertEqual(nested, [], 'Test methods must belong directly to their test class')

    def test_thumbnail_real_dimensions_are_checked(self):
        import derived_assets as derived
        thumbnails = [(slide_id, 0, data_uri('image/png', tiny_png()), {'id': 'thumb-' + slide_id, 'mime': 'image/png', 'alt': '', 'sha256': hashlib.sha256(tiny_png()).hexdigest()}) for slide_id in ('s1', 's2', 's3')]
        result = derived.finalize(SKELETON, thumbnails)
        self.assertTrue(any('dimensions' in error for error in run(result).errors))

    def test_self_closing_svg_and_raw_attributes_survive_print(self):
        import derived_assets as derived
        fragment = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" aria-label="A &amp; B > C"><defs/><g/></svg>'
        result = derived.finalize(SKELETON.replace('<h2>比較</h2>', '<h2>比較</h2>' + fragment), [])
        self.assertEqual(run(result).errors, [])
        printed, _ = derived.print_markup(result)
        self.assertIn('A &amp; B > C', printed)
        self.assertIn('<defs />', printed)
        self.assertNotIn('&amp;amp;', printed)

    def test_finalize_without_model_reports_reason(self):
        import derived_assets as derived
        source = re.sub(r'<script id="shf-model".*?</script>', '', SKELETON, flags=re.S)
        with self.assertRaisesRegex(ValueError, 'requires a shf-model'):
            derived.finalize(source, [])

    def test_runtime_policy_rejects_unsafe_apis(self):
        from build_skeletons import check_runtime_policy
        runtime = (SKILL / 'assets/runtime/shf-runtime.js').read_text(encoding='utf-8')
        check_runtime_policy(runtime)
        for code in ['node.innerHTML = value;', 'document.createElement("img");', 'fetch(value);', 'window.eval(value);']:
            with self.assertRaises(ValueError):
                check_runtime_policy(runtime + code)

    def test_invalid_inputs_and_steps_fail(self):
        self.assertIn('INPUT', codes(run(with_body('<input type="range" min="0" max="100" step="1" value="999">'))))
        self.assertIn('DERIVED', codes(run(SKELETON.replace('<h2>比較</h2>', '<h2>比較</h2><p data-shf-step="1" data-shf-until="1">Replace</p>'))))
        self.assertIn('MODEL', codes(run(with_model('[]'))))

    def test_legacy_v4_still_valid(self):
        fixtures = list((HERE / "fixtures").glob("legacy-v4-*.html"))
        self.assertEqual(len(fixtures), 4)
        for fixture in fixtures:
            self.assertEqual(V.verify(fixture, REGISTRY, BUDGET).errors, [], fixture.name)

    def test_finalized_model_passes(self):
        import derived_assets as derived
        result = derived.finalize(SKELETON, [])
        self.assertEqual(run(result).errors, [])
        self.assertIn("DERIVED", codes(run(result.replace('SINGLE HTML FORGE', 'CHANGED', 1))))

    def test_derived_states_and_print(self):
        import derived_assets as derived
        source = SKELETON.replace('<h2>比較</h2>', '<h2>比較</h2><p data-shf-step="1">Second step</p>')
        derived.validate_steps(source)
        self.assertEqual(derived.states(source), [("s1", 0), ("s2", 0), ("s3", 0), ("s3", 1)])
        result = derived.finalize(source, [])
        model = json.loads(next(item[1].content for item in V.lex(result) if item[0] == "raw" and item[1].attrs.get("id") == "shf-model"))
        derived.check_derived(result, model)
        with self.assertRaises(ValueError):
            derived.check_derived(result.replace("Second step", "Changed step", 1), model)

    def test_non_contiguous_steps_rejected(self):
        import derived_assets as derived
        with self.assertRaises(ValueError):
            derived.validate_steps(SKELETON.replace('<h2>比較</h2>', '<h2>比較</h2><p data-shf-step="2">Gap</p>'))

    def test_registration_preserves_old_versions(self):
        from build_skeletons import register_hash
        entries = {"1": "old"}
        register_hash(entries, "2", "new")
        register_hash(entries, "2", "new")
        self.assertEqual(entries, {"1": "old", "2": "new"})
        with self.assertRaises(ValueError):
            register_hash(entries, "1", "changed")
        self.assertEqual(entries["1"], "old")


class Negative(unittest.TestCase):
    """Every case here must FAIL, and for the stated reason."""

    def assertFails(self, text, code, budget=None, registry=None):
        rep = run(text, budget, registry)
        self.assertTrue(rep.errors, "expected at least one error, got a clean pass")
        self.assertIn(code, codes(rep), f"expected {code}, got {rep.errors}")

    def test_malformed_model_types_fail_without_exceptions(self):
        invalid = [
            {"schemaVersion": True, "assets": []},
            {"schemaVersion": 1.0, "assets": []},
            {"schemaVersion": 1, "assets": [None]},
            {"schemaVersion": 1, "assets": ["not an asset"]},
            {"schemaVersion": 1, "assets": [{"id": []}]},
            {"schemaVersion": 1, "assets": [{"id": {}}]},
        ]
        for model in invalid:
            with self.subTest(model=model):
                self.assertFails(with_model(json.dumps(model)), "MODEL")

    def test_json_duplicates_and_nonfinite_values_fail(self):
        for model in ['{"schemaVersion":1,"schemaVersion":2}', '{"schemaVersion":1,"assets":[],"number":NaN}', '{"schemaVersion":1,"assets":[],"number":Infinity}', '{"schemaVersion":1,"assets":[],"number":1e999}', '[' * 1100 + '0' + ']' * 1100]:
            with self.subTest(model=model):
                self.assertFails(with_model(model), "MODEL")

    def test_thumbnail_metadata_requires_exact_types(self):
        import derived_assets
        valid = derived_assets.finalize(SKELETON, [])
        raw = next(token[1] for token in V.lex(valid) if token[0] == "raw" and token[1].attrs.get("id") == "shf-model")
        base = json.loads(raw.content)
        invalid = [None, {"slideId": [], "assetId": "thumb", "step": 0, "width": 320, "height": 180}]
        for key, value in [("step", False), ("step", 0.0), ("width", 320.0), ("height", True)]:
            item = {"slideId": "s1", "assetId": "thumb", "step": 0, "width": 320, "height": 180}
            item[key] = value
            invalid.append(item)
        for item in invalid:
            model = dict(base, thumbnails=[item])
            with self.subTest(item=item):
                self.assertFails(valid.replace(raw.content, json.dumps(model)), "MODEL")

    def test_malformed_http_links_fail_without_exceptions(self):
        for href in ["http://exa[mple.com", "https://[::1", "https://example.com:invalid", "https:///missing-host", "http://example.com:0"]:
            with self.subTest(href=href):
                self.assertFails(with_body('<a href="' + href + '">Link</a>'), "URL")

    # --- canonical grammar ---

    def test_self_closing_script(self):
        # The construct that makes html.parser disagree with browsers.
        self.assertFails(with_body('<script id="x"/>'), "CANONICAL")

    def test_duplicate_attribute(self):
        self.assertFails(with_body('<p class="a" class="b">x</p>'), "CANONICAL")

    def test_unquoted_attribute(self):
        self.assertFails(with_body("<p class=a>x</p>"), "CANONICAL")

    def test_single_quoted_attribute(self):
        self.assertFails(with_body("<p class='a'>x</p>"), "CANONICAL")

    def test_raw_script_breakout_in_model(self):
        # The raw close truncates the JSON, so the model no longer parses.
        self.assertFails(with_model('{"schemaVersion":1,"x":"</script><img>"}'), "MODEL")

    def test_raw_script_breakout_with_valid_json_prefix(self):
        # Harder case: the part before the break is valid JSON, so the model check
        # alone would be happy. The injected markup must still be caught.
        text = with_model('{"schemaVersion":1,"assets":[]}</script><img src="https://evil.example/a.png">')
        rep = run(text)
        self.assertTrue(rep.errors)
        self.assertTrue({"STRUCT", "PINNED", "IMG"} & codes(rep), rep.errors)

    def test_bare_ampersand(self):
        self.assertFails(with_body("<p>A & B</p>"), "CANONICAL")

    def test_control_character(self):
        self.assertFails(with_body("<p>bad\x07char</p>"), "CANONICAL")

    def test_bom(self):
        self.assertFails("\ufeff" + SKELETON, "ENCODING")

    def test_stray_carriage_return(self):
        self.assertFails(SKELETON.replace("<body>\n", "<body>\r", 1), "ENCODING")

    def test_unbalanced_end_tag(self):
        self.assertFails(with_body("<p>x</div>"), "STRUCT")

    # --- element and attribute allowlist ---

    def test_iframe(self):
        self.assertFails(with_body('<iframe src="https://example.com"></iframe>'), "ELEMENT")

    def test_iframe_srcdoc(self):
        self.assertFails(with_body('<iframe srcdoc="&lt;p&gt;x"></iframe>'), "ELEMENT")

    def test_object(self):
        self.assertFails(with_body('<object data="https://example.com/a.svg"></object>'), "ELEMENT")

    def test_embed(self):
        self.assertFails(with_body('<embed src="https://example.com/a.svg">'), "ELEMENT")

    def test_video_poster(self):
        self.assertFails(with_body('<video poster="https://example.com/p.png"></video>'), "ELEMENT")

    def test_link_icon(self):
        self.assertFails(with_body('<link rel="icon" href="https://example.com/f.ico">'), "ELEMENT")

    def test_picture_source_srcset(self):
        self.assertFails(
            with_body('<picture><source srcset="https://example.com/a.png"></picture>'), "ELEMENT"
        )

    def test_canvas(self):
        self.assertFails(with_body("<canvas></canvas>"), "ELEMENT")

    def test_input_image(self):
        self.assertFails(with_body('<input type="image" src="https://example.com/a.png">'), "ELEMENT")

    def test_base(self):
        self.assertFails(with_body('<base href="https://example.com/">'), "ELEMENT")

    def test_style_attribute(self):
        self.assertFails(with_body('<p style="background-image:url(https://e.com/a.png)">x</p>'), "ATTR")

    def test_event_handler(self):
        self.assertFails(with_body('<p onclick="x()">y</p>'), "ATTR")

    def test_img_srcset(self):
        self.assertFails(
            with_body('<img src="data:image/png;base64,AA==" srcset="https://e.com/a.png" alt="a">'),
            "ATTR",
        )

    # --- pinned regions ---

    def test_extra_script(self):
        self.assertFails(with_body('<script id="evil">alert(1)</script>'), "PINNED")

    def test_extra_style(self):
        self.assertFails(with_body('<style id="evil">p{color:red}</style>'), "PINNED")

    def test_textarea(self):
        self.assertFails(with_body("<textarea>x</textarea>"), "ELEMENT")

    def test_tampered_runtime(self):
        text = SKELETON.replace('<script id="shf-runtime">', '<script id="shf-runtime">/*x*/', 1)
        self.assertFails(text, "TAMPERED")

    def test_tampered_css(self):
        text = SKELETON.replace('<style id="shf-css">', '<style id="shf-css">/*x*/', 1)
        self.assertFails(text, "TAMPERED")

    def test_unsupported_runtime_version(self):
        # Derived from the skeleton so the fixture survives a version bump.
        text = re.sub(r'data-shf-runtime="\d+"', 'data-shf-runtime="99"', SKELETON, count=1)
        self.assertNotEqual(text, SKELETON, "the version attribute was not found")
        self.assertFails(text, "UNSUPPORTED_VERSION")

    # --- theme tokens ---

    def test_theme_url(self):
        text = SKELETON.replace(
            '<style id="shf-theme">', '<style id="shf-theme">:root{--shf-color-x:url(https://e.com/a)}</style><style id="shf-theme">', 1
        )
        self.assertFails(text, "PINNED")

    def test_theme_bad_value(self):
        start = SKELETON.index('<style id="shf-theme">') + len('<style id="shf-theme">')
        end = SKELETON.index("</style>", start)
        text = SKELETON[:start] + ":root{--shf-color-accent:red}" + SKELETON[end:]
        self.assertFails(text, "THEME")

    def test_theme_unknown_property(self):
        start = SKELETON.index('<style id="shf-theme">') + len('<style id="shf-theme">')
        end = SKELETON.index("</style>", start)
        text = SKELETON[:start] + ":root{--evil:#ffffff}" + SKELETON[end:]
        self.assertFails(text, "THEME")

    # --- model ---

    def test_schema_version_mismatch(self):
        self.assertFails(with_model('{"schemaVersion":2,"assets":[]}'), "MODEL")

    def test_model_not_json(self):
        self.assertFails(with_model("{not json"), "MODEL")

    # --- images ---

    def test_external_img(self):
        self.assertFails(with_body('<img src="https://example.com/a.png" alt="a">'), "IMG")

    def test_missing_alt(self):
        self.assertFails(with_body('<img src="data:image/png;base64,AA==">'), "ALT")

    def test_broken_data_uri(self):
        self.assertFails(with_body('<img src="data:image/png;base64,!!!!" alt="a">'), "IMG")

    def test_mime_spoof(self):
        uri = data_uri("image/png", b"\xff\xd8\xff\xe0jpegbytes")
        text = self._artifact_with_image(uri, mime="image/png", sha_ok=False)
        self.assertFails(text, "MIME")

    def test_metadata_chunk_present(self):
        payload = png_with_text()
        text = self._artifact_with_image(data_uri("image/png", payload), payload=payload)
        self.assertFails(text, "METADATA")

    def test_unregistered_asset_ref(self):
        payload = tiny_png()
        uri = data_uri("image/png", payload)
        text = with_model('{"schemaVersion":1,"assets":[]}')
        text = text.replace(
            '<script id="shf-model"',
            f'<img src="{uri}" alt="a" data-asset-ref="ghost">\n<script id="shf-model"',
            1,
        )
        self.assertFails(text, "ASSET")

    def test_orphan_manifest_asset(self):
        model = '{"schemaVersion":1,"assets":[{"id":"a1","mime":"image/png","alt":"a"}]}'
        self.assertFails(with_model(model), "ASSET")

    def test_manifest_sha_mismatch(self):
        payload = tiny_png()
        text = self._artifact_with_image(data_uri("image/png", payload), payload=payload, sha_ok=False)
        self.assertFails(text, "ASSET")

    def test_over_budget(self):
        payload = tiny_png()
        text = self._artifact_with_image(data_uri("image/png", payload), payload=payload)
        tight = json.loads(json.dumps(BUDGET))
        tight["perImageBytes"] = {"warn": 1, "fail": 10}
        self.assertFails(text, "BUDGET", budget=tight)

    # --- svg subset ---

    def test_svg_script(self):
        self.assertFails(with_body('<svg xmlns="http://www.w3.org/2000/svg"><script>x</script></svg>'), "PINNED")

    def test_svg_image_element(self):
        self.assertFails(
            with_body('<svg xmlns="http://www.w3.org/2000/svg"><image href="https://e.com/a.png"/></svg>'),
            "SVG_ELEMENT",
        )

    def test_svg_foreign_object(self):
        self.assertFails(
            with_body('<svg xmlns="http://www.w3.org/2000/svg"><foreignObject></foreignObject></svg>'),
            "SVG_ELEMENT",
        )

    def test_svg_use(self):
        self.assertFails(with_body('<svg xmlns="http://www.w3.org/2000/svg"><use href="#a"/></svg>'), "SVG_ELEMENT")

    def test_svg_url_value(self):
        self.assertFails(
            with_body('<svg xmlns="http://www.w3.org/2000/svg"><rect fill="url(#g)"/></svg>'), "SVG_URL"
        )

    def test_svg_wrong_namespace(self):
        self.assertFails(with_body('<svg xmlns="http://evil.example/"><rect/></svg>'), "SVG_NS")

    def test_svg_event_handler(self):
        self.assertFails(
            with_body('<svg xmlns="http://www.w3.org/2000/svg"><rect onclick="x()"/></svg>'), "ATTR"
        )

    # --- urls ---

    def test_javascript_href(self):
        self.assertFails(with_body('<a href="javascript:alert(1)">x</a>'), "URL")
    def test_file_href(self):
        self.assertFails(with_body('<a href="file:///etc/passwd">x</a>'), "URL")

    def test_entity_obfuscated_scheme(self):
        self.assertFails(with_body('<a href="&#106;avascript:alert(1)">x</a>'), "URL")

    def test_protocol_relative_href(self):
        self.assertFails(with_body('<a href="//example.com/a">x</a>'), "URL")

    # --- outline navigation ---

    def test_goto_without_matching_slide(self):
        self.assertFails(
            with_body('<button type="button" data-shf-goto="ghost">x</button>'), "NAV"
        )

    def test_outline_missing_an_entry(self):
        text = re.sub(
            r'<li><button type="button" data-shf-goto="s2">.*?</button></li>\n',
            "",
            OUTLINE,
            count=1,
        )
        self.assertNotEqual(text, OUTLINE, "the entry to drop was not found")
        self.assertFails(text, "NAV")

    def test_duplicate_slide_id(self):
        self.assertFails(
            with_body('<section data-slide-id="s1" hidden><h2>dup</h2></section>'), "NAV"
        )

    # --- helper ---

    def _artifact_with_image(self, uri, mime="image/png", payload=None, sha_ok=True):
        digest = hashlib.sha256(payload).hexdigest() if payload is not None else "0" * 64
        if not sha_ok:
            digest = "1" * 64
        model = json.dumps(
            {"schemaVersion": 1, "assets": [{"id": "a1", "mime": mime, "alt": "a", "sha256": digest}]},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        text = with_model(model)
        return text.replace(
            '<script id="shf-model"',
            f'<img src="{uri}" alt="a" data-asset-ref="a1">\n<script id="shf-model"',
            1,
        )


class Positive(unittest.TestCase):
    """These must PASS, so that a PASS is not an empty scan."""

    def assertPasses(self, text):
        rep = run(text)
        self.assertEqual(rep.errors, [], f"expected a clean pass, got {rep.errors}")

    def test_all_skeletons(self):
        for path in sorted((SKILL / "assets" / "skeletons").glob("*.html")):
            rep = V.verify(path, REGISTRY, BUDGET)
            self.assertEqual(rep.errors, [], f"{path.name}: {rep.errors}")

    def test_crlf_artifact_still_passes(self):
        # git checkout and Windows editors produce CRLF. The pinned-region hashes
        # are computed from LF, so without normalisation this would report TAMPERED.
        self.assertPasses(SKELETON.replace("\n", "\r\n"))

    def test_escaped_script_close_in_model(self):
        # The escaped form must pass, or the negative test above proves nothing.
        self.assertPasses(with_model('{"schemaVersion":1,"note":"\\u003c/script>","assets":[]}'))

    def test_known_image_count_is_found(self):
        payload = tiny_png()
        digest = hashlib.sha256(payload).hexdigest()
        model = json.dumps(
            {
                "schemaVersion": 1,
                "assets": [
                    {"id": f"a{i}", "mime": "image/png", "alt": f"figure {i}", "sha256": digest}
                    for i in (1, 2)
                ],
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        uri = data_uri("image/png", payload)
        imgs = "\n".join(
            f'<img src="{uri}" alt="figure {i}" data-asset-ref="a{i}">' for i in (1, 2)
        )
        text = with_model(model).replace(
            '<script id="shf-model"', imgs + '\n<script id="shf-model"', 1
        )
        rep = run(text)
        self.assertEqual(rep.errors, [], rep.errors)
        # the extractor must really have seen both images, not zero
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.html"
            path.write_text(text, encoding="utf-8", newline="")
            tokens = V.lex(path.read_text(encoding="utf-8"))
            ctx = V.walk(tokens, V.Report())
        self.assertEqual(len(ctx["asset_payloads"]), 2)

    def test_inline_svg_subset(self):
        self.assertPasses(
            with_body(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10" role="img">'
                "<title>figure</title>"
                '<rect x="0" y="0" width="10" height="10" fill="#0067b8"/>'
                "</svg>"
            )
        )

    def test_https_and_fragment_links(self):
        self.assertPasses(with_body('<a href="https://example.com/a">x</a> <a href="#s1">y</a>'))


if __name__ == "__main__":
    unittest.main(verbosity=2)
