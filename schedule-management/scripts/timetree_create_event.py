"""Create one TimeTree event through the signed-in dedicated browser (CDP) and read it back.

Env: TIMETREE_CALENDAR_URL (e.g. https://timetreeapp.com/calendars/<id>),
     CALENDAR_BROWSER_CDP (default http://127.0.0.1:9331).
Start the browser first with start-calendar-browser.ps1. Requires: playwright (Python).
Aborts when the title already exists in that month, aborts without saving if the form times do not match,
and never retries a save: after Save it requires exactly one match and exits non-zero otherwise.
Notes: the UI is English; Label is left at the calendar default (e.g. Soft violet).
"""
import argparse
import os
import re
import sys

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("--date", required=True, help="YYYY-MM-DD")
ap.add_argument("--start", required=True, help="HH:MM (24h)")
ap.add_argument("--end", required=True, help="HH:MM (24h)")
ap.add_argument("--title", required=True)
ap.add_argument("--location", default="")
ap.add_argument("--notes", default="")
args = ap.parse_args()

base = os.environ.get("TIMETREE_CALENDAR_URL")
cdp = os.environ.get("CALENDAR_BROWSER_CDP", "http://127.0.0.1:9331")
if not base:
    sys.exit("Set TIMETREE_CALENDAR_URL")
base = base.rstrip("/")


def fmt(t):
    h, m = map(int, t.split(":"))
    return f"{h % 12 or 12}:{m:02d} {'AM' if h < 12 else 'PM'}"


MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def pick_time(page, idx, value):
    page.locator("input").nth(idx).click()
    page.wait_for_timeout(900)
    opts = page.get_by_text(value, exact=True)
    for i in range(opts.count()):
        box = opts.nth(i).bounding_box()
        if box and box["width"] > 100:  # the dropdown item, not small month-cell labels
            opts.nth(i).click()
            break
    page.wait_for_timeout(900)


def open_month(page, year, month):
    """Open the monthly view and step with Prev/Next until the header shows the requested month."""
    page.goto(f"{base}/monthly/{year}/{month}")
    want = (year, month)
    for _ in range(40):
        page.wait_for_timeout(1500)
        m = re.search(r"(%s), (\d{4})" % "|".join(MONTHS), page.evaluate("document.body.innerText"))
        if m:
            cur = (int(m.group(2)), MONTHS.index(m.group(1)) + 1)
            if cur == want:
                # The header renders before the events do; counting too early gives a false 0.
                page.wait_for_timeout(5000)
                return
            page.get_by_role("button", name="Next month" if cur < want else "Previous month").click()
    sys.exit(f"Could not open {MONTHS[month - 1]}, {year}")

def count_title(page):
    return page.evaluate("document.body.innerText").count(args.title)


y, mo, _ = args.date.split("-")
with sync_playwright() as pw:
    page = pw.chromium.connect_over_cdp(cdp).contexts[0].pages[0]

    open_month(page, int(y), int(mo))
    if count_title(page):
        sys.exit("A same-title event already exists this month; update it instead.")

    # A fresh navigation can still restore an unsaved draft: verify every field below.
    page.goto(f"{base}/events/new?date={args.date}")
    page.wait_for_timeout(3500)
    page.get_by_placeholder("Event title (required)").fill(args.title)
    # The form remembers the last All-day setting; timed events need it off.
    for _ in range(2):
        vals = page.evaluate("[...document.querySelectorAll('input')].map(e=>e.value)")
        idx = [i for i, v in enumerate(vals) if v.endswith(("AM", "PM"))]
        if len(idx) >= 2:
            break
        page.locator("input[type=checkbox]").first.evaluate("e=>e.click()")  # a text click does not toggle it
        page.wait_for_timeout(1000)
    if len(idx) < 2:
        sys.exit("Could not switch off All-day; nothing was saved.")
    pick_time(page, idx[0], fmt(args.start))
    pick_time(page, idx[1], fmt(args.end))
    if args.location:
        page.get_by_placeholder("Add a location").fill(args.location)
    if args.notes:
        page.get_by_text("Note", exact=True).last.click()
        page.wait_for_timeout(800)
        page.locator("textarea").last.fill(args.notes)
        page.get_by_role("button", name="OK").click()  # the modal blocks Save until closed
        page.wait_for_timeout(800)
    got = page.evaluate("[...document.querySelectorAll('input')].map(e=>e.value)")
    times = [v for v in got if v.endswith(("AM", "PM"))]
    print("form:", [v for v in got if v and v != "on"][:6])
    if times[:2] != [fmt(args.start), fmt(args.end)]:
        sys.exit(f"Form times {times[:2]} differ from the request; nothing was saved.")
    page.get_by_role("button", name="Save").click(timeout=8000)
    page.wait_for_timeout(3000)

    # Never re-run after this point: the event is already saved even if readback fails.
    open_month(page, int(y), int(mo))
    n = count_title(page)
    if n != 1:
        sys.exit(f"Expected exactly 1 event after saving, found {n}; check and delete duplicates by hand.")
    page.get_by_text(args.title, exact=True).first.click()
    page.wait_for_timeout(1500)
    text = page.evaluate("document.body.innerText")
    print("readback:", text[text.find("Event details"):][:400].replace("\n", " | "))
