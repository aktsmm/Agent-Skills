import tempfile
import unittest
from pathlib import Path

import build_review_viewer

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

SKEL = Path(__file__).resolve().parent.parent / "assets" / "skeletons" / "deck-outline-skeleton.html"


@unittest.skipIf(sync_playwright is None, "playwright is not installed")
class ReviewViewerTest(unittest.TestCase):
    def test_slide_image_opens_and_closes_lightbox(self):
        with tempfile.TemporaryDirectory() as tmp:
            deck = Path(tmp) / "deck.html"
            pixel = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
            deck.write_text(
                SKEL.read_text(encoding="utf-8").replace(
                    "<h1>タイトルをここに置く</h1>",
                    '<h1>タイトルをここに置く</h1><img src="' + pixel + '" alt="検証画像">',
                    1,
                ),
                encoding="utf-8",
            )
            out = Path(tmp) / "review.html"
            build_review_viewer.build(deck, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1400, "height": 800})
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                image = page.frame_locator("#deck").locator('[data-slide-id="s1"] img[alt="検証画像"]')
                image.click()
                self.assertTrue(page.is_visible("#lightbox"))
                self.assertEqual(page.get_attribute("#lightboximage", "alt"), "検証画像")
                self.assertEqual(page.inner_text("#lightboxcaption"), "検証画像")
                page.keyboard.press("Escape")
                self.assertFalse(page.is_visible("#lightbox"))
                image.press("Enter")
                self.assertTrue(page.is_visible("#lightbox"))
                page.click("#lightboxclose")
                self.assertFalse(page.is_visible("#lightbox"))
                browser.close()

    def test_comment_follows_slide_persists_and_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                context = browser.new_context(accept_downloads=True)
                page = context.new_page()
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                self.assertIn("スライド 1 / 3", page.inner_text("#where"))

                page.fill("#comment", "最初のコメント")
                page.click("#next")
                page.wait_for_function("document.querySelector('#where').textContent.includes('スライド 2 / 3')")
                self.assertEqual(page.input_value("#comment"), "")
                page.fill("#comment", "二枚目の指摘")
                page.select_option("#ctype", "fix")

                page.reload()
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                page.click("#list button:nth-child(1)")
                page.wait_for_function("document.querySelector('#where').textContent.includes('スライド 1 / 3')")
                self.assertEqual(page.input_value("#comment"), "最初のコメント")

                with page.expect_download() as info:
                    page.click("#save")
                saved = Path(info.value.path()).read_text(encoding="utf-8")
                self.assertIn("最初のコメント", saved)
                self.assertIn("二枚目の指摘", saved)
                self.assertIn("[要修正]", saved)
                browser.close()

    def test_split_drags_persists_and_resets(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1400, "height": 800})
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                before = page.evaluate("document.getElementById('panel').getBoundingClientRect().width")
                box = page.locator("#split").bounding_box()
                x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
                page.mouse.move(x, y)
                page.mouse.down()
                page.mouse.move(x - 200, y, steps=5)
                page.mouse.up()
                after = page.evaluate("document.getElementById('panel').getBoundingClientRect().width")
                self.assertAlmostEqual(after, before + 200, delta=6)
                deck_w = page.evaluate("document.getElementById('deck').getBoundingClientRect().width")
                self.assertAlmostEqual(deck_w + after + 10, 1400, delta=2)

                page.reload()
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                kept = page.evaluate("document.getElementById('panel').getBoundingClientRect().width")
                self.assertAlmostEqual(kept, after, delta=2)

                page.dblclick("#split")
                reset = page.evaluate("document.getElementById('panel').getBoundingClientRect().width")
                self.assertAlmostEqual(reset, before, delta=2)
                browser.close()

    def test_deck_outline_width_drags_and_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1500, "height": 800})
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                deck = page.frame_locator("#deck")
                deck.locator('[data-shf-action="outline"]').click()
                width = lambda: deck.locator("#shf-outline").evaluate("e => e.getBoundingClientRect().width")
                stage = lambda: deck.locator("#shf-root").evaluate("e => e.getBoundingClientRect().width")
                before, stage_before = width(), stage()
                self.assertAlmostEqual(before, 264, delta=2)
                box = deck.locator("#shf-ow-handle").bounding_box()
                x, y = box["x"] + box["width"] / 2, box["y"] + 200
                page.mouse.move(x, y)
                page.mouse.down()
                page.mouse.move(x + 100, y, steps=5)
                page.mouse.up()
                self.assertAlmostEqual(width(), before + 100, delta=6)
                self.assertLess(stage(), stage_before)

                page.reload()
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                deck = page.frame_locator("#deck")
                deck.locator('[data-shf-action="outline"]').click()
                self.assertAlmostEqual(width(), before + 100, delta=6)
                browser.close()

    def test_external_links_open_in_a_new_tab(self):
        with tempfile.TemporaryDirectory() as tmp:
            deck = Path(tmp) / "deck.html"
            deck.write_text(
                SKEL.read_text(encoding="utf-8").replace(
                    "<h1>タイトルをここに置く</h1>",
                    '<h1>タイトルをここに置く</h1>\n<p><a href="https://example.invalid/doc">外部の資料</a></p>',
                    1,
                ),
                encoding="utf-8",
            )
            out = Path(tmp) / "review.html"
            build_review_viewer.build(deck, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                context = browser.new_context()
                context.route("https://example.invalid/**", lambda route: route.fulfill(body="ok", content_type="text/plain"))
                page = context.new_page()
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                link = page.frame_locator("#deck").locator('a[href^="https://example.invalid"]')
                self.assertEqual(link.get_attribute("target"), "_blank")
                with context.expect_page() as popup:
                    link.click()
                self.assertIn("example.invalid", popup.value.url)
                self.assertEqual(page.evaluate("document.getElementById('deck').contentWindow.location.href"), "about:srcdoc")
                self.assertIn("スライド 1 / 3", page.inner_text("#where"))
                browser.close()

    def test_deck_fullscreen_button_works_inside_the_viewer(self):
        # allow="fullscreen" on a srcdoc iframe blocks the API (origin mismatch); allowfullscreen works.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1400, "height": 800})
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                page.frame_locator("#deck").locator('[data-shf-action="fullscreen"]').click()
                page.wait_for_function("!!document.fullscreenElement")
                browser.close()

    def test_grid_overview_jump_and_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1400, "height": 800})
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                page.keyboard.press("g")
                self.assertTrue(page.is_visible("#gridview"))
                self.assertEqual(page.locator("#gridbody button.card").count(), 3)
                page.click("#gridbody button.card:nth-child(3)")
                self.assertFalse(page.is_visible("#gridview"))
                page.wait_for_function("document.querySelector('#where').textContent.includes('3 / 3')")
                page.keyboard.press("g")
                page.keyboard.press("Escape")
                self.assertFalse(page.is_visible("#gridview"))
                page.fill("#jump", "2")
                page.press("#jump", "Enter")
                page.wait_for_function("document.querySelector('#where').textContent.includes('2 / 3')")
                page.fill("#q", "比較")
                self.assertEqual(page.locator("#list button").count(), 1)
                self.assertIn("比較", page.inner_text("#list"))
                browser.close()

    def test_deep_link_and_resume_last_slide(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                context = browser.new_context(viewport={"width": 1400, "height": 800})
                page = context.new_page()
                page.goto(out.as_uri() + "#s2")
                page.wait_for_function("document.querySelector('#where').textContent.includes('2 / 3')")
                page.click("#next")
                page.wait_for_function("document.querySelector('#where').textContent.includes('3 / 3')")
                self.assertTrue(page.url.endswith("#s3"))
                fresh = context.new_page()
                fresh.goto(out.as_uri())
                fresh.wait_for_function("document.querySelector('#where').textContent.includes('3 / 3')")
                browser.close()

    def test_types_filter_summary_and_ai_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                context = browser.new_context(viewport={"width": 1400, "height": 800}, permissions=["clipboard-read", "clipboard-write"])
                page = context.new_page()
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                page.select_option("#ctype", "q")
                page.fill("#comment", "これは何ですか")
                page.click("#next")
                page.wait_for_function("document.querySelector('#where').textContent.includes('2 / 3')")
                page.select_option("#ctype", "fix")
                page.fill("#comment", "直す")
                summary = page.inner_text("#summary")
                self.assertIn("コメント 2 件", summary)
                self.assertIn("要修正 1 件", summary)
                page.select_option("#filter", "fix")
                self.assertEqual(page.locator("#list button").count(), 1)
                page.select_option("#filter", "all")
                page.click("#copyai")
                page.wait_for_function("document.querySelector('#status').textContent.includes('依頼文')")
                text = page.evaluate("navigator.clipboard.readText()")
                self.assertIn("反映してスライドを修正", text)
                self.assertIn("[質問]", text)
                self.assertIn("[要修正]", text)
                self.assertIn("直す", text)
                browser.close()

    def test_export_then_import_json_and_markdown_merge_without_overwriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                context = browser.new_context(viewport={"width": 1400, "height": 800}, accept_downloads=True)
                page = context.new_page()
                page.on("dialog", lambda d: d.accept())
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                page.select_option("#ctype", "fix")
                page.fill("#comment", "元のコメント（かっこ付き）")
                with page.expect_download() as j:
                    page.click("#savejson")
                json_path = Path(tmp) / "c.json"
                Path(j.value.path()).replace(json_path)
                with page.expect_download() as m:
                    page.click("#save")
                md_path = Path(tmp) / "c.md"
                Path(m.value.path()).replace(md_path)
                page.click("#clear")
                self.assertEqual(page.input_value("#comment"), "")
                page.set_input_files("#importfile", str(json_path))
                page.wait_for_function("document.querySelector('#comment').value.includes('元のコメント')")
                self.assertEqual(page.input_value("#ctype"), "fix")
                page.click("#clear")
                page.set_input_files("#importfile", str(md_path))
                page.wait_for_function("document.querySelector('#comment').value.includes('元のコメント')")
                self.assertEqual(page.input_value("#ctype"), "fix")
                page.fill("#comment", "手元で書き換えた")
                page.set_input_files("#importfile", str(md_path))
                page.wait_for_function("document.querySelector('#comment').value.includes('取り込み')")
                value = page.input_value("#comment")
                self.assertIn("手元で書き換えた", value)
                self.assertIn("元のコメント", value)
                browser.close()

    def test_quote_selected_slide_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1400, "height": 800})
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                page.frames[1].evaluate(
                    "(function(){var p=document.querySelector('.shf-lead');var r=document.createRange();r.selectNodeContents(p);var s=getSelection();s.removeAllRanges();s.addRange(r);document.dispatchEvent(new MouseEvent('mouseup',{bubbles:true}));})()"
                )
                page.frame_locator("#deck").locator("#review-quote").click()
                self.assertIn("> 副題", page.input_value("#comment"))
                browser.close()

    def test_laser_pointer_follows_the_mouse(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1400, "height": 800})
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                deck = page.frame_locator("#deck")
                deck.locator("[data-review-laser]").click()
                self.assertEqual(deck.locator("[data-review-laser]").get_attribute("aria-pressed"), "true")
                page.mouse.move(300, 300)
                page.mouse.move(420, 360, steps=4)
                dot = page.frames[1].evaluate("(function(){var d=document.getElementById('review-laser');return [d.style.display,parseFloat(d.style.left),parseFloat(d.style.top)]})()")
                self.assertEqual(dot[0], "block")
                self.assertGreater(dot[1], 100)
                page.keyboard.press("Escape")
                page.keyboard.press("l")
                self.assertEqual(deck.locator("[data-review-laser]").get_attribute("aria-pressed"), "false")
                browser.close()

    def test_presenter_window_syncs_with_the_audience_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                context = browser.new_context(viewport={"width": 1400, "height": 800})
                main = context.new_page()
                main.goto(out.as_uri())
                main.wait_for_function("document.querySelectorAll('#list button').length === 3")
                main.click("#next")
                main.wait_for_function("document.querySelector('#where').textContent.includes('2 / 3')")
                pres = context.new_page()
                pres.goto(out.as_uri() + "#presenter")
                pres.wait_for_function("document.querySelectorAll('#list button').length === 3")
                pres.wait_for_function("document.querySelector('#where').textContent.includes('2 / 3')")
                self.assertTrue(pres.evaluate("document.body.classList.contains('pres')"))
                self.assertTrue(pres.is_visible("#presextra"))
                self.assertFalse(pres.is_visible("#editor"))
                self.assertIn("次: 3.", pres.inner_text("#nexttitle"))
                main.click("#next")
                pres.wait_for_function("document.querySelector('#where').textContent.includes('3 / 3')")
                pres.click("#prev")
                main.wait_for_function("document.querySelector('#where').textContent.includes('2 / 3')")
                pres.wait_for_function("document.querySelector('#clock').textContent !== ''")
                browser.close()

    def test_panel_closes_reopens_and_toggles_with_shortcut(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1400, "height": 800})
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                width = lambda: page.evaluate("document.getElementById('deck').getBoundingClientRect().width")
                self.assertLess(width(), 1100)
                toggle = page.frame_locator("#deck").locator("[data-review-toggle]")
                self.assertEqual(toggle.get_attribute("aria-pressed"), "true")
                page.click("#close")
                self.assertAlmostEqual(width(), 1400, delta=2)
                self.assertEqual(toggle.get_attribute("aria-pressed"), "false")
                self.assertFalse(page.is_visible("#reopen"))
                toggle.click()
                self.assertLess(width(), 1100)
                page.keyboard.press("Alt+c")
                self.assertAlmostEqual(width(), 1400, delta=2)
                page.reload()
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                self.assertAlmostEqual(width(), 1400, delta=2)
                page.keyboard.press("Alt+c")
                self.assertLess(width(), 1100)
                browser.close()

    def test_panel_fullscreen_button_hides_panel_and_restores(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1400, "height": 800})
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                page.click("#fs")
                page.wait_for_function("!!document.fullscreenElement")
                self.assertFalse(page.is_visible("#panel"))
                page.evaluate("document.exitFullscreen()")
                page.wait_for_function("!document.fullscreenElement")
                page.wait_for_function("document.getElementById('panel').offsetWidth > 0")
                browser.close()

    def test_ctrl_enter_moves_to_next_slide_and_notes_are_shown(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1400, "height": 800})
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                self.assertIn("話者メモ", page.text_content("#notesBody"))
                page.fill("#comment", "確認")
                page.press("#comment", "Control+Enter")
                page.wait_for_function("document.querySelector('#where').textContent.includes('スライド 2 / 3')")
                page.press("#comment", "Control+Shift+Enter")
                page.wait_for_function("document.querySelector('#where').textContent.includes('スライド 1 / 3')")
                browser.close()

    def test_comments_survive_a_deck_revision_and_flag_changed_slides(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1400, "height": 800})
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                page.fill("#comment", "最初のコメント")
                revised = Path(tmp) / "deck2.html"
                revised.write_text(
                    SKEL.read_text(encoding="utf-8").replace("副題。1 行で主張を言い切る。", "副題を書き換えた。"),
                    encoding="utf-8",
                )
                build_review_viewer.build(revised, out)
                page.reload()
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                self.assertEqual(page.input_value("#comment"), "最初のコメント")
                self.assertTrue(page.is_visible("#stale"))
                browser.close()

    def test_typing_right_after_navigation_goes_to_the_new_slide(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1400, "height": 800})
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                page.fill("#comment", "A")
                page.press("#comment", "Control+Enter")
                page.fill("#comment", "B")
                page.press("#comment", "Control+Shift+Enter")
                page.wait_for_function("document.querySelector('#where').textContent.includes('スライド 1 / 3')")
                self.assertEqual(page.input_value("#comment"), "A")
                page.press("#comment", "Control+Enter")
                page.wait_for_function("document.querySelector('#where').textContent.includes('スライド 2 / 3')")
                self.assertEqual(page.input_value("#comment"), "B")
                browser.close()

    def test_stale_banner_stays_until_confirmed(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1400, "height": 800})
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                page.fill("#comment", "最初")
                revised = Path(tmp) / "deck2.html"
                revised.write_text(
                    SKEL.read_text(encoding="utf-8").replace("副題。1 行で主張を言い切る。", "副題を書き換えた。"),
                    encoding="utf-8",
                )
                build_review_viewer.build(revised, out)
                page.reload()
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                self.assertTrue(page.is_visible("#stale"))
                page.fill("#comment", "最初に一文字足した")
                self.assertTrue(page.is_visible("#stale"))
                page.click("#confirm")
                self.assertFalse(page.is_visible("#stale"))
                page.reload()
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                self.assertFalse(page.is_visible("#stale"))
                browser.close()

    def test_focus_moves_with_the_panel_and_controls_are_labelled(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1400, "height": 800})
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                active = lambda: page.evaluate("document.activeElement && document.activeElement.id")
                page.click("#close")
                self.assertTrue(page.frames[1].evaluate("document.activeElement.hasAttribute('data-review-toggle')"))
                page.frame_locator("#deck").locator("[data-review-toggle]").click()
                self.assertEqual(active(), "comment")
                self.assertTrue(page.get_attribute("#comment", "aria-label"))
                self.assertEqual(page.get_attribute("#list button.current", "aria-current"), "true")
                self.assertEqual(page.get_attribute("#panel #status", "role"), "status")
                browser.close()

    def test_small_screen_panel_scrolls(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            build_review_viewer.build(SKEL, out)
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 700, "height": 500})
                page.goto(out.as_uri())
                page.wait_for_function("document.querySelectorAll('#list button').length === 3")
                self.assertEqual(page.evaluate("getComputedStyle(document.getElementById('panel')).overflowY"), "auto")
                self.assertEqual(page.get_attribute("#split", "aria-orientation"), "horizontal")
                browser.close()

    def test_extract_recovers_the_deck(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.html"
            back = Path(tmp) / "deck.html"
            build_review_viewer.build(SKEL, out)
            build_review_viewer.extract(out, back)
            self.assertEqual(back.read_text(encoding="utf-8"), SKEL.read_text(encoding="utf-8"))

    def test_rejects_non_deck_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "x.html"
            src.write_text("<!DOCTYPE html><html><head><title>x</title></head><body></body></html>", encoding="utf-8")
            with self.assertRaises(SystemExit):
                build_review_viewer.build(src, Path(tmp) / "out.html")


if __name__ == "__main__":
    unittest.main()
