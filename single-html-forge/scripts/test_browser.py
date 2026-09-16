"""Browser regressions; requires Playwright and its Chromium browser."""

import tempfile
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

import verify_html as verifier


SKILL = Path(__file__).resolve().parent.parent
SKELETON = (SKILL / "assets/skeletons/deck-skeleton.html").read_text(encoding="utf-8")


class SvgVisibilityTests(unittest.TestCase):
    def artifact(self, second_svg=None):
        diagram = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 80" width="200" height="80"><title>Flow</title><rect x="10" y="10" width="100" height="40" fill="#ffffff"/></svg>'
        pages = ('<section data-slide-id="first" class="is-active"><h2>First</h2>' + diagram + '</section>'
                 '<section data-slide-id="second" hidden="hidden"><h2>Second</h2>' +
                 (diagram if second_svg is None else second_svg) + '</section>')
        start = SKELETON.index('<main id="shf-root">') + len('<main id="shf-root">')
        end = SKELETON.index('<div id="shf-chrome">', start)
        return SKELETON[:start] + pages + SKELETON[end:]

    def run_browser(self, source):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'fixture.html'
            path.write_text(source, encoding='utf-8')
            report = verifier.Report()
            result = verifier.run_tier2(path, report)
        return result, report.errors

    def test_hidden_slide_is_checked_when_navigated_to(self):
        result, errors = self.run_browser(self.artifact())
        self.assertEqual(result, 'ok', errors)

    def test_zero_size_on_later_slide_fails(self):
        diagram = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 80" width="0" height="0"><title>Broken</title></svg>'
        result, errors = self.run_browser(self.artifact(diagram))
        self.assertEqual(result, 'failed')
        self.assertTrue(any('state 1:' in error and 'inline svg' in error for error in errors))

    def test_missing_viewbox_even_on_hidden_slide_fails(self):
        diagram = '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="80"><title>Broken</title></svg>'
        result, errors = self.run_browser(self.artifact(diagram))
        self.assertEqual(result, 'failed')
        self.assertTrue(any('state 0:' in error and 'viewBox' in error for error in errors))


class GroupedOutlineTests(unittest.TestCase):
    def test_group_navigation_and_keyboard(self):
        from playwright.sync_api import sync_playwright

        document = (SKILL / 'assets/skeletons/deck-outline-skeleton.html').read_text(encoding='utf-8')
        start = document.index('<nav id="shf-outline">')
        end = document.index('</nav>', start) + len('</nav>')
        groups = ('<nav id="shf-outline">'
                  '<details data-shf-section="intro" open="open"><summary>Introduction</summary><ol>'
                  '<li><button type="button" data-shf-page="01" data-shf-goto="s1">First</button></li>'
                  '<li><button type="button" data-shf-page="02" data-shf-goto="s2">Second</button></li>'
                  '</ol></details><details data-shf-section="examples"><summary>Examples</summary><ol>'
                  '<li><button type="button" data-shf-page="03" data-shf-goto="s3">Third</button></li>'
                  '</ol></details></nav>')
        document = document[:start] + groups + document[end:]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'grouped.html'
            path.write_text(document, encoding='utf-8')
            registry = json.loads((SKILL / 'scripts/runtime-registry.json').read_text(encoding='utf-8'))
            budget = json.loads((SKILL / 'scripts/budget.json').read_text(encoding='utf-8'))
            self.assertEqual(verifier.verify(path, registry, budget).errors, [])
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                try:
                    page = browser.new_page(viewport={'width': 1600, 'height': 900})
                    page.goto(path.as_uri())
                    first = page.locator('details').nth(0)
                    second = page.locator('details').nth(1)
                    first.locator('summary').click()
                    self.assertFalse(first.evaluate('element => element.open'))
                    second.locator('summary').click()
                    second.locator('button').click()
                    self.assertEqual(page.locator('[data-slide-id]:not([hidden])').get_attribute('data-slide-id'), 's3')
                    self.assertEqual(second.get_attribute('class'), 'is-current-section')
                    page.keyboard.press('ArrowLeft')
                    self.assertTrue(first.evaluate('element => element.open'))
                    self.assertEqual(page.locator('[data-shf-goto][aria-current="true"]').count(), 1)
                    first.locator('summary').focus()
                    page.keyboard.press('Space')
                    self.assertFalse(first.evaluate('element => element.open'))
                    self.assertEqual(page.locator('[data-slide-id]:not([hidden])').get_attribute('data-slide-id'), 's2')
                    page.keyboard.press('Enter')
                    self.assertTrue(first.evaluate('element => element.open'))
                    page.keyboard.press('End')
                    self.assertTrue(second.evaluate('element => element.open'))
                    self.assertEqual(page.locator('#shf-slide-counter').inner_text(), '3 / 3')
                finally:
                    browser.close()


class PlayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        import derived_assets
        cls.engine = sync_playwright().start()
        cls.browser = cls.engine.chromium.launch()
        cls.folder = tempfile.TemporaryDirectory()
        cls.path = Path(cls.folder.name) / 'player.html'
        source = (SKILL / 'assets/skeletons/deck-motion-skeleton.html').read_text(encoding='utf-8')
        cls.source = derived_assets.finalize(source, [])
        cls.path.write_text(cls.source, encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.engine.stop()
        cls.folder.cleanup()

    def setUp(self):
        self.page = self.browser.new_page(viewport={'width': 1280, 'height': 720})
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.goto(self.path.as_uri())

    def tearDown(self):
        self.page.close()
        self.assertEqual(self.errors, [])

    def state(self):
        return self.page.evaluate("[document.querySelector('[data-slide-id].is-active').getAttribute('data-slide-id'), document.documentElement.getAttribute('data-shf-current-step')]")

    def test_steps_modes_focus_and_boundaries(self):
        page = self.page
        page.locator('[data-shf-goto="s2"]').click()
        page.locator('[data-shf-action="next"]').click()
        self.assertEqual(self.state(), ['s2', '1'])
        self.assertFalse(page.locator('svg g[data-shf-step="2"]').is_visible())
        self.assertTrue(page.locator('svg g[data-shf-step="1"]').is_visible())
        page.locator('[data-shf-action="outline"]').click()
        self.assertEqual(self.state(), ['s2', '1'])
        self.assertFalse(page.locator('#shf-outline').is_visible())
        page.locator('#shf-menu summary').click()
        page.locator('#shf-volume').focus()
        page.keyboard.press('ArrowRight')
        self.assertEqual(self.state(), ['s2', '1'])
        page.keyboard.press('Escape')
        self.assertTrue(page.locator('#shf-menu summary').evaluate('node => node === document.activeElement'))
        page.keyboard.press('ArrowRight')
        self.assertEqual(self.state(), ['s2', '2'])
        page.keyboard.press('ArrowRight')
        page.keyboard.press('ArrowLeft')
        self.assertEqual(self.state(), ['s2', '2'])
        page.keyboard.press('End')
        self.assertEqual(self.state(), ['s3', '1'])
        self.assertTrue(page.locator('[data-shf-action="next"]').is_disabled())
        page.keyboard.press('Home')
        self.assertTrue(page.locator('[data-shf-action="prev"]').is_disabled())
        page.keyboard.press('o')
        page.locator('[data-shf-goto="s1"]').focus()
        page.keyboard.press('o')
        self.assertTrue(page.locator('[data-shf-action="outline"]').evaluate('node => node === document.activeElement'))

    def test_audio_pending_resume_mute_and_failure(self):
        page = self.page
        page.evaluate("""() => {
          window.audioCreated = 0; window.audioStarted = 0; window.audioResumes = [];
          window.AudioContext = class {
            constructor() { window.audioCreated++; this.currentTime = 0; this.destination = {}; }
            resume() { return new Promise((resolve, reject) => window.audioResumes.push({resolve, reject})); }
            createOscillator() { return {frequency:{setValueAtTime(){}}, connect(){}, disconnect(){}, stop(){}, start(){window.audioStarted++;}}; }
            createGain() { return {gain:{setValueAtTime(){},linearRampToValueAtTime(){},exponentialRampToValueAtTime(){}},connect(){},disconnect(){}}; }
          };
        }""")
        self.assertEqual(page.evaluate('audioCreated'), 0)
        page.locator('#shf-menu summary').click()
        page.locator('#shf-sound').check()
        self.assertEqual(page.evaluate('audioCreated'), 1)
        page.locator('#shf-sound').uncheck()
        page.evaluate('audioResumes.shift().resolve()')
        self.assertEqual(page.evaluate('audioStarted'), 0)
        page.locator('#shf-sound').check()
        page.evaluate('audioResumes.shift().resolve()')
        self.assertEqual(page.evaluate('audioStarted'), 1)
        page.locator('#shf-volume').fill('0')
        page.locator('[data-shf-action="test-sound"]').click()
        page.evaluate('audioResumes.shift().resolve()')
        self.assertEqual(page.evaluate('audioStarted'), 1)
        page.locator('[data-shf-action="test-sound"]').click()
        page.evaluate("audioResumes.shift().reject(new Error('denied'))")
        self.assertFalse(page.locator('#shf-sound').is_checked())
        page.keyboard.press('Escape')
        page.keyboard.press('ArrowRight')
        self.assertEqual(self.state(), ['s2', '0'])

    def test_fullscreen_failure_does_not_change_state(self):
        page = self.page
        page.evaluate("() => { document.documentElement.requestFullscreen = () => Promise.reject(new Error('denied')); }")
        page.locator('[data-shf-action="fullscreen"]').click()
        self.assertEqual(self.state(), ['s1', '0'])
        self.assertIn('Fullscreen unavailable', page.locator('#shf-status').inner_text())

    def test_runtime_does_not_use_forbidden_dom_or_network_apis(self):
        page = self.page
        page.evaluate(
            "() => { window.policyViolations = [];"
            "for (const name of ['createElement','createElementNS','write','writeln']) {"
            "document[name] = () => { policyViolations.push(name); throw new Error(name); }; }"
            "for (const name of ['fetch','XMLHttpRequest','WebSocket','Worker']) {"
            "window[name] = () => { policyViolations.push(name); throw new Error(name); }; } }")
        for key in ['ArrowRight', 'ArrowRight', 'o', 'o', 'ArrowRight', 'ArrowRight', 'ArrowLeft', 'End', 'Home']:
            page.keyboard.press(key)
        page.locator('#shf-menu summary').click()
        page.locator('#shf-motion').uncheck()
        page.keyboard.press('Escape')
        self.assertEqual(page.evaluate('policyViolations'), [])

    def test_thumbnail_finalize_and_export_pipeline(self):
        import derived_assets
        source = SKILL / 'assets/skeletons/deck-motion-skeleton.html'
        output = Path(self.folder.name) / 'thumbs.html'
        command = [sys.executable, '-B', str(SKILL / 'scripts/export_html.py')]
        result = subprocess.run(command + [str(source), '--finalize', str(output), '--thumbnails'], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = output.read_text(encoding='utf-8')
        model = json.loads(next(token[1].content for token in verifier.lex(text) if token[0] == 'raw' and token[1].attrs.get('id') == 'shf-model'))
        derived_assets.check_derived(text, model)
        self.assertEqual(len(model['thumbnails']), 3)
        self.page.goto(output.as_uri())
        self.assertEqual(self.page.locator('[data-shf-thumbnail]').count(), 3)
        self.page.locator('[data-shf-goto="s2"]').click()
        self.page.keyboard.press('ArrowRight')
        self.page.locator('#shf-menu summary').click()
        self.page.locator('[data-shf-action="list-style"]').click()
        self.assertFalse(self.page.locator('[data-shf-thumbnail]').first.is_visible())
        self.assertEqual(self.state(), ['s2', '1'])
        folder = Path(self.folder.name) / 'png'
        result = subprocess.run(command + [str(output), '--slides-png', str(folder), '--scale', '1'], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual([(item['slideId'], item['step']) for item in manifest], [('s1', 0), ('s2', 2), ('s3', 0), ('s3', 1)])
        self.assertEqual(manifest[0]['file'], 'slide-01.png')

    def test_responsive_menu_and_reduced_motion(self):
        page = self.page
        for width, height in [(1280, 720), (1920, 1080), (390, 844)]:
            page.set_viewport_size({'width': width, 'height': height})
            page.emulate_media(reduced_motion='reduce')
            page.keyboard.press('Home')
            page.keyboard.press('ArrowRight')
            page.keyboard.press('ArrowRight')
            self.assertEqual(self.state(), ['s2', '1'])
            self.assertEqual(page.locator('[data-slide-id].is-active').evaluate('node => getComputedStyle(node).animationName'), 'none')
            page.locator('#shf-menu summary').click()
            rectangle = page.locator('.shf-settings').bounding_box()
            self.assertGreaterEqual(rectangle['x'], 0)
            self.assertLessEqual(rectangle['x'] + rectangle['width'], width + 1)
            self.assertGreaterEqual(rectangle['y'], 0)
            page.keyboard.press('Escape')
            if width == 390:
                self.assertFalse(page.locator('#shf-outline').is_visible())
                page.locator('[data-shf-action="outline"]').click()
                page.locator('[data-shf-goto="s3"]').click()
                self.assertFalse(page.locator('#shf-outline').is_visible())
                self.assertEqual(self.state(), ['s3', '0'])
            if os.environ.get('SHF_SCREENSHOTS'):
                folder = Path(os.environ['SHF_SCREENSHOTS'])
                folder.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(folder / f'player-{width}.png'))

    def test_real_audio_and_fullscreen_apis(self):
        page = self.page
        page.evaluate(
            "() => { const NativeAudio = window.AudioContext; window.realAudioStarted = 0;"
            "window.AudioContext = class extends NativeAudio { createOscillator() {"
            "const oscillator = super.createOscillator(); const start = oscillator.start.bind(oscillator);"
            "oscillator.start = (...args) => { window.realAudioStarted++; return start(...args); }; return oscillator; } }; }")
        page.locator('#shf-menu summary').click()
        page.locator('#shf-sound').check()
        page.wait_for_function('window.realAudioStarted === 1')
        page.locator('#shf-sound').uncheck()
        page.keyboard.press('Escape')
        page.locator('[data-shf-action="fullscreen"]').click()
        page.wait_for_function('document.fullscreenElement !== null')
        self.assertEqual(self.state(), ['s1', '0'])
        page.locator('[data-shf-action="fullscreen"]').click()
        page.wait_for_function('document.fullscreenElement === null')
        self.assertEqual(self.state(), ['s1', '0'])

    def test_motion_control_shows_system_override_and_restores_choice(self):
        page = self.page
        page.emulate_media(reduced_motion='no-preference')
        page.locator('#shf-menu summary').click()
        control = page.locator('#shf-motion')
        self.assertTrue(control.is_checked())
        page.emulate_media(reduced_motion='reduce')
        page.wait_for_function("document.getElementById('shf-motion').disabled")
        self.assertFalse(control.is_checked())
        self.assertTrue(page.locator('#shf-motion-status').is_visible())
        if os.environ.get('SHF_SCREENSHOTS'):
            folder = Path(os.environ['SHF_SCREENSHOTS'])
            folder.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(folder / 'player-system-motion.png'))
        page.emulate_media(reduced_motion='no-preference')
        page.wait_for_function("!document.getElementById('shf-motion').disabled")
        self.assertTrue(control.is_checked())
        self.assertFalse(page.locator('#shf-motion-status').is_visible())
        control.uncheck()
        page.emulate_media(reduced_motion='reduce')
        page.wait_for_function("document.getElementById('shf-motion').disabled")
        page.emulate_media(reduced_motion='no-preference')
        page.wait_for_function("!document.getElementById('shf-motion').disabled")
        self.assertFalse(control.is_checked())

    def test_print_all_replacement_states_and_restore(self):
        page = self.page
        page.keyboard.press('End')
        previous = self.state()
        self.assertEqual(page.locator('[data-shf-print-slide]').count(), 4)
        page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        page.emulate_media(media='print')
        self.assertFalse(page.locator('#shf-root').is_visible())
        self.assertFalse(page.locator('#shf-chrome').is_visible())
        self.assertTrue(page.locator('#shf-print').is_visible())
        text = page.locator('#shf-print').inner_text()
        self.assertIn('Before:', text)
        self.assertIn('After:', text)
        page.emulate_media(media='screen')
        page.evaluate("window.dispatchEvent(new Event('afterprint'))")
        self.assertEqual(self.state(), previous)

    def test_print_gate_detects_print_only_overflow_and_restores_screen(self):
        page = self.page
        page.keyboard.press('End')
        state, viewport = self.state(), page.viewport_size
        self.assertEqual(verifier.check_print_layout(page), [])
        page.add_style_tag(content='@media print { [data-shf-print-slide] p { transform: translateY(1000px); } }')
        errors = verifier.check_print_layout(page)
        self.assertTrue(any('outside page' in error or 'content overflow' in error for error in errors), errors)
        self.assertEqual(page.viewport_size, viewport)
        self.assertEqual(self.state(), state)
        self.assertFalse(page.evaluate("matchMedia('print').matches"))

    def test_print_accessible_names_and_links_resolve_inside_handout(self):
        import derived_assets as derived
        source = (SKILL / 'assets/skeletons/deck-motion-skeleton.html').read_text(encoding='utf-8')
        source = source.replace('<h2>A signal becomes a decision</h2>', '<h2 id="flow-heading">A signal becomes a decision</h2><a href="#summary-target" aria-describedby="flow-heading">Summary</a>')
        source = source.replace('<h2>Change the conclusion, not the context</h2>', '<h2 id="summary-target">Change the conclusion, not the context</h2>')
        source = source.replace('aria-label="Observe, compare, decide">', 'aria-labelledby="flow-name"><title id="flow-name">Observe, compare, decide</title>')
        target = Path(self.folder.name) / 'print-reference.html'
        target.write_text(derived.finalize(source, []), encoding='utf-8')
        self.page.goto(target.as_uri())
        self.assertEqual(verifier.check_print_layout(self.page), [])
        self.page.emulate_media(media='print')
        actual = self.page.evaluate(
            "() => { const root = document.getElementById('shf-print'); const link = root.querySelector('a');"
            "const svg = root.querySelector('svg'); const title = document.getElementById(svg.getAttribute('aria-labelledby'));"
            "const target = document.getElementById(link.getAttribute('href').slice(1));"
            "const description = document.getElementById(link.getAttribute('aria-describedby'));"
            "return {targetInside:root.contains(target), titleInside:svg.contains(title), descriptionInside:root.contains(description), title:title.textContent, targetVisible:target.getBoundingClientRect().height > 0}; }")
        self.assertEqual(actual, {'targetInside': True, 'titleInside': True, 'descriptionInside': True, 'title': 'Observe, compare, decide', 'targetVisible': True})
        if os.environ.get('SHF_SCREENSHOTS'):
            folder = Path(os.environ['SHF_SCREENSHOTS'])
            folder.mkdir(parents=True, exist_ok=True)
            self.page.locator('[data-shf-print-slide="s2"]').screenshot(path=str(folder / 'print-reference-check.png'))
            self.page.pdf(path=str(folder / 'print-reference-check.pdf'), width='16in', height='9in', print_background=True, prefer_css_page_size=True)

    def test_all_steps_tier2_and_finalization_gate(self):
        command = [sys.executable, '-B', str(SKILL / 'scripts/verify_html.py')]
        result = subprocess.run(command + [str(self.path), '--tier2'], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        draft = SKILL / 'assets/skeletons/deck-motion-skeleton.html'
        result = subprocess.run(command + [str(draft), '--tier2'], capture_output=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(b'--finalize', result.stdout + result.stderr)


class ThumbnailCapacityTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get('SHF_LARGE_DECKS'), 'Set SHF_LARGE_DECKS=1 for the release capacity gate')
    def test_thumbnail_capacity(self):
        import base64
        import hashlib
        import io
        import random
        import build_skeletons as builder
        from PIL import Image

        buffer = io.BytesIO()
        Image.frombytes('RGB', (128, 72), random.Random(41).randbytes(128 * 72 * 3)).save(buffer, format='PNG')
        payload = buffer.getvalue()
        uri = 'data:image/png;base64,' + base64.b64encode(payload).decode('ascii')
        measured = []
        with tempfile.TemporaryDirectory() as folder:
            for count in (10, 30, 60):
                pages, assets = [], []
                for index in range(count):
                    identity = 'slide-' + str(index + 1)
                    pages.append('<section data-slide-id="' + identity + '"' + (' class="is-active"' if index == 0 else ' hidden') + '><h2>Evidence ' + str(index + 1) + '</h2><img src="' + uri + '" data-asset-ref="asset-' + identity + '" alt="Synthetic test image" width="128" height="72"></section>')
                    assets.append({'id': 'asset-' + identity, 'mime': 'image/png', 'alt': 'Synthetic test image', 'sha256': hashlib.sha256(payload).hexdigest()})
                body = '<main id="shf-root">' + ''.join(pages) + builder.DECK_BODY[builder.DECK_BODY.index('<div id="shf-chrome">'):]
                source = builder.build('deck', builder.read_text(builder.RUNTIME), 'outline', body=body)
                source = source.replace(builder.MODEL, json.dumps({'schemaVersion': 1, 'assets': assets}))
                draft, final = Path(folder) / 'draft.html', Path(folder) / 'final.html'
                draft.write_text(source, encoding='utf-8')
                result = subprocess.run([sys.executable, '-B', str(SKILL / 'scripts/export_html.py'), str(draft), '--finalize', str(final), '--thumbnails'], capture_output=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                model = json.loads(next(token[1].content for token in verifier.lex(final.read_text(encoding='utf-8')) if token[0] == 'raw' and token[1].attrs.get('id') == 'shf-model'))
                self.assertEqual(len(model['thumbnails']), count)
                self.assertLess(final.stat().st_size, json.loads((SKILL / 'scripts/budget.json').read_text())['wholeFileBytes']['fail'])
                measured.append({'slides': count, 'bytes': final.stat().st_size, 'thumbnails': len(model['thumbnails'])})
        print('CAPACITY ' + json.dumps(measured))


if __name__ == '__main__':
    unittest.main()