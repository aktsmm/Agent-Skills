#!/usr/bin/env python3

import unittest

import export_html


class FakeLocator:
    def __init__(self):
        self.expression = None

    def evaluate_all(self, expression):
        self.expression = expression


class FakePage:
    def __init__(self):
        self.selector = None
        self.result = FakeLocator()

    def locator(self, selector):
        self.selector = selector
        return self.result


class HidePngChromeTests(unittest.TestCase):
    def test_hides_print_action_before_capture(self):
        page = FakePage()

        export_html.hide_png_chrome(page)

        self.assertEqual('[data-shf-action="print"]', page.selector)
        self.assertIn("element.hidden = true", page.result.expression)


if __name__ == "__main__":
    unittest.main()