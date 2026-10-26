"""Playwright helpers for Microsoft Forms (ja-JP UI), driven over an existing CDP browser.

Every helper is idempotent-friendly: it reads the state back and asserts, so a failed
step can be resumed without typing the same text twice.
"""
import re

from playwright.sync_api import TimeoutError as PWTimeout

HOME = "https://forms.cloud.microsoft/"
DESIGN = "https://forms.cloud.microsoft/Pages/DesignPageV2.aspx?origin=NeoPortalPage&subpage=design&id="
RESPONSE = "https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id="

# ja-JP UI labels. For another UI language, change only this table.
L = {
    "new_form": "新しいフォームを作成",
    "form_title": "フォームのタイトル",
    "form_desc": "フォームの説明",
    "quick_start": "以下でクイック スタート",
    "add_question": "新しい質問の追加",
    "kind_text": "テキスト",
    "kind_choice": "選択肢",
    "question_title": "質問のタイトル",
    "option_box": "オプションのテキストの選択",
    "add_option": "オプションを追加",
    "add_other": '"その他" オプションの追加',
    "delete_other": "削除 その他",
    "sw_required": "必須",
    "sw_long": "長い回答",
    "sw_multi": "複数回答",
    "required_mark": "回答するのに必要です",
    "collect": "回答を収集",
    "share_all": "すべてのユーザーが回答可能",
    "short_url": "URL を短縮",
    "saved": "保存済み",
}


def click(loc, timeout=4000):
    """Click, falling back to a DOM click when a Copilot suggestion popover covers the control."""
    try:
        loc.click(timeout=timeout)
    except PWTimeout:
        loc.evaluate("e => e.click()")


def replace_text(page, box, text):
    """Select all, then insert. `type()`/insert alone appends and duplicates text on a re-run."""
    box.click()
    page.keyboard.press("Control+A")
    page.keyboard.insert_text(text)
    page.wait_for_timeout(400)
    assert box.inner_text().strip() == text, text


def sign_in(page, account):
    """Open Forms; on the account picker choose the Windows-connected work account (no password typed)."""
    page.goto(HOME, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    tile = page.get_by_text(account)
    if tile.count():
        tile.first.click()
        for _ in range(30):  # the redirect after the click can take longer than a fixed wait
            if "login.microsoftonline.com" not in page.url:
                break
            page.wait_for_timeout(1000)
    assert "login.microsoftonline.com" not in page.url, "sign-in not completed; ask the user to sign in in this window"


def create_form(ctx, page):
    """Click 'new form'. The editor opens in a NEW tab, so every extra click leaves an empty untitled form."""
    page.goto(HOME, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    btn = page.get_by_role("button", name=L["new_form"])
    try:
        with ctx.expect_page(timeout=15000) as info:
            btn.click()
        new = info.value
    except PWTimeout:
        new = page
    new.wait_for_url(re.compile(r"DesignPage.*[?&]id="), timeout=30000)
    new.wait_for_timeout(5000)
    return new


def form_id(page):
    return re.search(r"[?&]id=([^&]+)", page.url).group(1)


def close_copilot_draft_panel(page):
    """A new form opens with a 'draft with Copilot' panel that covers the title field. Close it first.
    The panel is found through its prompt hint, then its own close button is clicked."""
    closed = page.evaluate(
        """() => {
            const hint = Array.from(document.querySelectorAll('*')).find(
              e => e.children.length === 0 && (e.textContent || '').trim().startsWith('作成したいフォームの内容'));
            for (let n = hint; n; n = n.parentElement) {
              const b = n.querySelector('button[aria-label="閉じる"]');
              if (b) { b.click(); return true; }
            }
            return false;
        }"""
    )
    if closed:
        page.wait_for_timeout(1500)
        assert page.get_by_text("作成したいフォームの内容").count() == 0, "Copilot draft panel is still open"


def set_title_desc(page, title, desc_lines):
    click(page.get_by_role("button", name=re.compile("^" + L["form_title"])).last)
    page.wait_for_timeout(800)
    replace_text(page, page.get_by_role("textbox", name=L["form_title"]), title)
    if desc_lines:
        d = page.get_by_role("textbox", name=L["form_desc"])
        d.click()
        page.keyboard.press("Control+A")
        for i, line in enumerate(desc_lines):
            page.keyboard.insert_text(line)
            if i < len(desc_lines) - 1:
                page.keyboard.press("Shift+Enter")
        page.wait_for_timeout(800)


def title_box(page, n):
    return page.get_by_role("textbox", name=f"{L['question_title']} {n}")


def set_switch(page, name, on):
    sw = page.get_by_role("switch", name=name)
    if (sw.get_attribute("aria-checked") == "true") != on:
        click(sw)
        page.wait_for_timeout(400)
    assert (sw.get_attribute("aria-checked") == "true") == on, name


def add_question(page, n, kind):
    """Add question #n. The first one comes from 'quick start'; later ones from 'add question'.
    Tile names must be matched EXACTLY: collapsed question cards also contain words like 'テキスト'."""
    label = L["kind_choice"] if kind == "choice" else L["kind_text"]
    tile = page.get_by_role("button", name=label, exact=True)
    if not (tile.count() and tile.first.is_visible()):
        first = page.get_by_role("button", name=L["quick_start"])
        click(first if (n == 1 and first.count()) else page.get_by_role("button", name=L["add_question"]))
        page.wait_for_timeout(900)
    page.get_by_role("button", name=label, exact=True).first.click()
    page.wait_for_timeout(1200)


def fill_options(page, options):
    """New options come pre-filled with 'オプション N', so select-all before typing."""
    for i, opt in enumerate(options):
        boxes = page.get_by_role("textbox", name=L["option_box"])
        if i >= boxes.count():
            click(page.get_by_role("button", name=L["add_option"], exact=True))
            page.wait_for_timeout(700)
            boxes = page.get_by_role("textbox", name=L["option_box"])
        boxes.nth(i).click()
        page.keyboard.press("Control+A")
        page.keyboard.insert_text(opt)
        page.wait_for_timeout(300)
    got = [page.get_by_role("textbox", name=L["option_box"]).nth(i).inner_text().strip() for i in range(len(options))]
    assert got == options, got


def add_other_option(page):
    """Built-in free-text 'Other'. It always renders last; a plain option named 'その他' is not free text."""
    plain = [t.strip() for t in page.get_by_role("textbox", name=L["option_box"]).all_inner_texts()]
    if "その他" in plain:
        click(page.get_by_role("button", name=L["delete_other"], exact=True))
        page.wait_for_timeout(800)
    btn = page.get_by_role("button", name=L["add_other"], exact=True)
    if btn.count():
        click(btn.first)
        page.wait_for_timeout(1000)
    assert page.get_by_role("button", name=L["add_other"], exact=True).count() == 0


def add_spec_question(page, n, q):
    add_question(page, n, q["type"])
    replace_text(page, title_box(page, n), q["title"])
    if q["type"] == "choice":
        set_switch(page, L["sw_multi"], bool(q.get("multiple")))
        fill_options(page, q["options"])
        if q.get("other"):
            add_other_option(page)
    else:
        set_switch(page, L["sw_long"], bool(q.get("long")))
    set_switch(page, L["sw_required"], bool(q.get("required")))  # new cards inherit the previous setting


def card_labels(page):
    """Collapsed cards expose 'N. 質問のタイトル <title> <type> [回答するのに必要です]'. The open card is not listed."""
    return page.evaluate(
        "() => Array.from(document.querySelectorAll('button')).map(e => e.getAttribute('aria-label') || '')"
        ".filter(t => /^\\d+\\. 質問のタイトル/.test(t))"
    )


def wait_saved(page, deadline_ms=20000, expect=None):
    """Navigating away right after the last edit can drop it; wait for the header to say 'saved'.
    The header can already read 'saved' before a new edit registers, so pass `expect` (a snippet of the
    new text) after changing text: the header label must contain it too."""
    end = deadline_ms
    while end > 0:
        label = page.get_by_role("button", name=re.compile("^" + L["form_title"])).first.get_attribute("aria-label") or ""
        if label.endswith(L["saved"]) and (expect is None or expect in label):
            return
        page.wait_for_timeout(1000)
        end -= 1000
    raise AssertionError("form was not reported as saved" + (f" with the expected text {expect!r}" if expect else ""))


def verify_questions(page, fid, spec):
    """Leave the editor, reopen it, and compare titles and required flags with the spec."""
    page.goto(HOME, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    page.goto(DESIGN + fid, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    labels = card_labels(page)
    problems = []
    for i, q in enumerate(spec["questions"], 1):
        row = next((t for t in labels if t.startswith(f"{i}. {L['question_title']} {q['title']}")), None)
        if row is None:  # the last card may still be open; it is not listed as a collapsed card
            if i != len(spec["questions"]):
                problems.append(f"missing card {i}")
            continue
        if bool(q.get("required")) != (L["required_mark"] in row):
            problems.append(f"required mismatch on {i}")
    return problems


def open_collect_dialog(page, fid):
    page.goto(DESIGN + fid, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    click(page.get_by_role("button", name=L["collect"]))
    page.wait_for_timeout(3000)


def set_share_anyone(page, fid):
    """Changes who can respond to 'anyone, anonymous'. Only call after the user approved external respondents."""
    open_collect_dialog(page, fid)
    r = page.get_by_role("radio", name=L["share_all"])
    if not r.is_checked():
        r.check()
    page.wait_for_timeout(5000)
    page.goto(HOME, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    open_collect_dialog(page, fid)
    assert page.get_by_role("radio", name=L["share_all"]).is_checked()


def short_url(page, fid):
    open_collect_dialog(page, fid)
    cb = page.get_by_role("checkbox", name=L["short_url"])
    if not cb.is_checked():
        cb.check()
    page.wait_for_timeout(4000)
    links = page.evaluate(
        "() => Array.from(document.querySelectorAll('input, textarea, a')).map(e => e.value || e.innerText || e.href || '')"
        ".filter(t => /forms\\.cloud\\.microsoft\\/r\\//.test(t))"
    )
    return links[0] if links else ""


def anonymous_check(browser, url, expected_title, expected_items):
    """Open the response URL in a cookie-less context: what an external respondent would get."""
    ctx = browser.new_context()
    try:
        pg = ctx.new_page()
        pg.goto(url, wait_until="domcontentloaded")
        pg.wait_for_timeout(10000)
        title = pg.evaluate("() => (document.querySelector('[role=heading], h1') || {}).innerText || ''")
        items = pg.evaluate("() => document.querySelectorAll('[data-automation-id=questionItem], [data-automation-id=questionContent]').length")
        return pg.url.split("/")[2] == "forms.cloud.microsoft" and title.strip().startswith(expected_title[:20]) and items == expected_items
    finally:
        ctx.close()
