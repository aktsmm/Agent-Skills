"""Create one TimeTree event through the signed-in dedicated browser (CDP) and read it back.

Env: TIMETREE_CALENDAR_URL (e.g. https://timetreeapp.com/calendars/<id>),
     CALENDAR_BROWSER_CDP (default http://127.0.0.1:9331).
Start the browser first with start-calendar-browser.ps1. Requires: playwright (Python).
Aborts when an event with the same title already exists in that month (no duplicates).
Notes: the UI is English; Label is left at the calendar default (e.g. Soft violet).
"""
import argparse
import os
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


def pick_time(page, idx, value):
    page.locator("input").nth(idx).click()
    page.wait_for_timeout(700)
    opts = page.get_by_text(value, exact=True)
    for i in range(opts.count()):
        box = opts.nth(i).bounding_box()
        if box and box["x"] > 600:  # the visible dropdown item, not hidden copies
            opts.nth(i).click()
            break
    page.wait_for_timeout(700)


y, mo, _ = args.date.split("-")
with sync_playwright() as pw:
    page = pw.chromium.connect_over_cdp(cdp).contexts[0].pages[0]

    page.goto(f"{base}/monthly/{y}/{int(mo)}")
    page.wait_for_timeout(3000)
    if args.title in page.evaluate("document.body.innerText"):
        sys.exit("A same-title event already exists this month; update it instead.")

    # A fresh navigation drops a restored unsaved draft from an earlier run.
    page.goto(f"{base}/events/new?date={args.date}")
    page.wait_for_timeout(3000)
    page.get_by_placeholder("Event title (required)").fill(args.title)
    vals = page.evaluate("[...document.querySelectorAll('input')].map(e=>e.value)")
    idx = [i for i, v in enumerate(vals) if v.endswith(("AM", "PM"))]
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
    print("form:", [v for v in got if v and v != "on"][:6])
    page.get_by_role("button", name="Save").click(timeout=8000)
    page.wait_for_timeout(2500)

    page.goto(f"{base}/monthly/{y}/{int(mo)}")
    page.wait_for_timeout(3000)
    page.get_by_text(args.title, exact=False).first.click()
    page.wait_for_timeout(1500)
    text = page.evaluate("document.body.innerText")
    print("readback:", text[text.find("Event details"):][:400].replace("\n", " | "))
