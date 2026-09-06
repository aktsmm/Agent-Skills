"""Browser regressions; requires Playwright and its Chromium browser."""

import tempfile
import json
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


if __name__ == '__main__':
    unittest.main()