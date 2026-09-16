#!/usr/bin/env python3

import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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


class ExportContractTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.artifact = self.root / 'input.html'
        skeleton = Path(__file__).resolve().parent.parent / 'assets/skeletons/deck-skeleton.html'
        self.original = skeleton.read_bytes()
        self.artifact.write_bytes(self.original)

    def invoke(self, arguments):
        stderr = io.StringIO()
        stdout = io.StringIO()
        with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout):
            code = export_html.main([str(self.artifact)] + arguments)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_invalid_options_do_not_dispatch_or_write(self):
        target = str(self.root / 'result.html')
        invalid = [
            ['--finalize', target, '--pdf', str(self.root / 'result.pdf')],
            ['--finalize', target, '--png', str(self.root / 'result.png')],
            ['--finalize', target, '--slides-png', str(self.root / 'slides')],
            ['--png', str(self.root / 'result.png'), '--thumbnails'],
            ['--png', str(self.artifact)],
            ['--pdf', target, '--png', target],
            ['--pdf', str(self.root / 'nested'), '--png', str(self.root / 'nested/page.png')],
            ['--pdf', str(self.root)],
            ['--slides-png', str(self.artifact)],
        ]
        for parameter in ('--scale', '--width', '--height'):
            invalid.append(['--png', str(self.root / 'result.png'), parameter, '0'])
        with patch.object(export_html, 'finalize_deck') as finalize, patch.object(export_html, 'export_formats') as formats:
            for arguments in invalid:
                with self.subTest(arguments=arguments):
                    code, stdout, stderr = self.invoke(arguments)
                    self.assertEqual(code, 1)
                    self.assertEqual(stdout, '')
                    self.assertIn('STOP:', stderr)
            finalize.assert_not_called()
            formats.assert_not_called()
        self.assertEqual(self.artifact.read_bytes(), self.original)
        self.assertEqual(list(self.root.iterdir()), [self.artifact])

    def test_hardlink_to_source_is_rejected(self):
        target = self.root / 'alias.png'
        try:
            os.link(self.artifact, target)
        except OSError as exc:
            self.skipTest(str(exc))
        code, _, stderr = self.invoke(['--png', str(target)])
        self.assertEqual(code, 1)
        self.assertIn('source HTML', stderr)
        self.assertEqual(self.artifact.read_bytes(), self.original)

    def test_finalize_in_place_is_explicitly_supported(self):
        with patch.object(export_html, 'finalize_deck', return_value=0) as finalize:
            self.assertEqual(self.invoke(['--finalize', str(self.artifact)])[0], 0)
            finalize.assert_called_once_with(self.artifact, self.artifact, False)

    def test_errors_are_reported_on_both_dispatch_paths(self):
        from playwright.sync_api import Error
        from embed_assets import Stop
        for operation, arguments in [('finalize_deck', ['--finalize', str(self.root / 'out.html')]), ('export_formats', ['--png', str(self.root / 'out.png')])]:
            for failure in [OSError('disk denied'), Error('browser closed'), ValueError('invalid input'), Stop('image processing failed')]:
                with self.subTest(operation=operation, failure=type(failure).__name__), patch.object(export_html, operation, side_effect=failure):
                    code, stdout, stderr = self.invoke(arguments)
                    self.assertEqual(code, 1)
                    self.assertEqual(stdout, '')
                    self.assertIn('STOP:', stderr)
                    self.assertNotIn('Traceback', stderr)

    def test_missing_imaging_dependency_reports_unavailable(self):
        from embed_assets import Stop
        failure = Stop('Pillow is not installed')
        failure.__cause__ = ImportError('PIL')
        with patch.object(export_html, 'finalize_deck', side_effect=failure):
            code, stdout, stderr = self.invoke(['--finalize', str(self.root / 'out.html'), '--thumbnails'])
        self.assertEqual(code, 2)
        self.assertEqual(stdout, '')
        self.assertIn('STOP: Pillow is not installed', stderr)

    def test_generation_failure_preserves_all_outputs(self):
        from playwright.sync_api import Error
        pdf, png = self.root / 'previous.pdf', self.root / 'previous.png'
        pdf.write_bytes(b'original pdf')
        png.write_bytes(b'original png')
        with patch('playwright.sync_api.sync_playwright') as playwright, patch('verify_html.check_print_layout', return_value=[]):
            page = playwright.return_value.__enter__.return_value.chromium.launch.return_value.new_page.return_value
            page.evaluate.return_value = True
            page.pdf.side_effect = lambda **kwargs: Path(kwargs['path']).write_bytes(b'new pdf')
            page.query_selector.return_value.screenshot.side_effect = Error('PNG failed after PDF generation')
            code, stdout, stderr = self.invoke(['--pdf', str(pdf), '--png', str(png)])
        self.assertEqual(code, 1)
        self.assertEqual(stdout, '')
        self.assertIn('PNG failed', stderr)
        self.assertEqual(pdf.read_bytes(), b'original pdf')
        self.assertEqual(png.read_bytes(), b'original png')

    def test_failed_replace_preserves_original_file(self):
        staged, target = self.root / 'pending', self.root / 'existing'
        staged.write_bytes(b'new')
        target.write_bytes(b'old')
        with patch('export_html.os.replace', side_effect=PermissionError('locked')):
            with self.assertRaises(PermissionError):
                export_html.publish_file(staged, target)
        self.assertEqual(target.read_bytes(), b'old')
        self.assertFalse(any(path.is_dir() for path in self.root.iterdir()))

    def test_pdf_print_overflow_stops_before_publication(self):
        target = self.root / 'previous.pdf'
        target.write_bytes(b'previous pdf')
        with patch('playwright.sync_api.sync_playwright') as playwright, patch('verify_html.check_print_layout', return_value=['print page 0: content overflow']) as check:
            page = playwright.return_value.__enter__.return_value.chromium.launch.return_value.new_page.return_value
            page.evaluate.return_value = True
            code, stdout, stderr = self.invoke(['--pdf', str(target)])
            check.assert_called_once_with(page)
            page.pdf.assert_not_called()
        self.assertEqual(code, 1)
        self.assertEqual(stdout, '')
        self.assertIn('content overflow', stderr)
        self.assertEqual(target.read_bytes(), b'previous pdf')

    def test_thumbnail_capture_errors_do_not_publish(self):
        import verify_html
        from test_verify import tiny_png
        target = self.root / 'final.html'
        target.write_bytes(b'previous final')
        for event in ('pageerror', 'console', 'wrong-state'):
            with self.subTest(event=event), patch('verify_html.verify', return_value=verify_html.Report()), patch('verify_html.run_tier2', return_value='ok'), patch('playwright.sync_api.sync_playwright') as playwright:
                page = playwright.return_value.__enter__.return_value.chromium.launch.return_value.new_page.return_value
                handlers = {}
                position = [0]
                page.on.side_effect = lambda name, callback: handlers.update({name: callback})
                page.keyboard.press.side_effect = lambda key: position.__setitem__(0, 0 if key == 'Home' else position[0] + 1)
                page.evaluate.side_effect = lambda expression: (['wrong' if event == 'wrong-state' else f's{position[0] + 1}', 0] if expression.startswith('[') else None)
                def capture(**kwargs):
                    if event == 'pageerror':
                        handlers[event](ValueError('capture-only error'))
                    elif event == 'console':
                        from types import SimpleNamespace
                        handlers[event](SimpleNamespace(type='error', text='capture-only console error'))
                    return tiny_png()
                page.locator.return_value.screenshot.side_effect = capture
                with self.assertRaisesRegex(ValueError, 'no HTML was published'):
                    export_html.finalize_deck(self.artifact, target, True)
                self.assertEqual(target.read_bytes(), b'previous final')

    def test_finalization_failure_does_not_create_target_directory(self):
        import verify_html
        target = self.root / 'not-created/final.html'
        report = verify_html.Report()
        report.error('DERIVED', 'candidate invalid')
        with patch('verify_html.verify', side_effect=[verify_html.Report(), report]), patch('verify_html.run_tier2', return_value='ok'):
            with self.assertRaisesRegex(ValueError, 'candidate invalid'):
                export_html.finalize_deck(self.artifact, target, False)
        self.assertFalse(target.parent.exists())

    def test_slides_only_rejects_doc_instead_of_empty_success(self):
        document = Path(__file__).resolve().parent.parent / 'assets/skeletons/doc-skeleton.html'
        self.artifact.write_bytes(document.read_bytes())
        code, stdout, stderr = self.invoke(['--slides-png', str(self.root / 'slides')])
        self.assertEqual(code, 1)
        self.assertEqual(stdout, '')
        self.assertIn('requires a deck', stderr)
        self.assertFalse((self.root / 'slides').exists())


if __name__ == "__main__":
    unittest.main()