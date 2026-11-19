"""Idempotently create or update one event in a Google Calendar via a service account.

Env: GOOGLE_CALENDAR_SA_JSON (key file path), GOOGLE_CALENDAR_ID.
Requires: google-api-python-client, google-auth. The key is only loaded into the
auth client and is never printed.
"""
import argparse
import os
import re
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ap = argparse.ArgumentParser()
ap.add_argument("--key", required=True, help="stable event id: 5-1024 chars, a-v and 0-9 only")
ap.add_argument("--title", required=True)
ap.add_argument("--date", required=True, help="YYYY-MM-DD")
ap.add_argument("--start", required=True, help="HH:MM")
ap.add_argument("--end", required=True, help="HH:MM")
ap.add_argument("--tz-offset", default="+09:00")
ap.add_argument("--tz", default="Asia/Tokyo")
ap.add_argument("--location", default="")
ap.add_argument("--notes", default="")
ap.add_argument("--visibility", default="private", choices=["default", "public", "private"])
ap.add_argument("--tentative", action="store_true", help="status=tentative and show as free")
args = ap.parse_args()
if not re.fullmatch(r"[a-v0-9]{5,1024}", args.key):
    sys.exit("--key must be 5-1024 chars of a-v and 0-9 only")

sa = os.environ.get("GOOGLE_CALENDAR_SA_JSON")
cal = os.environ.get("GOOGLE_CALENDAR_ID")
if not sa or not cal:
    sys.exit("Set GOOGLE_CALENDAR_SA_JSON and GOOGLE_CALENDAR_ID")

creds = service_account.Credentials.from_service_account_file(
    sa, scopes=["https://www.googleapis.com/auth/calendar"]
)
svc = build("calendar", "v3", credentials=creds)

body = {
    "id": args.key,
    "summary": args.title,
    "description": args.notes,
    "visibility": args.visibility,
    "start": {"dateTime": f"{args.date}T{args.start}:00{args.tz_offset}", "timeZone": args.tz},
    "end": {"dateTime": f"{args.date}T{args.end}:00{args.tz_offset}", "timeZone": args.tz},
}
if args.location:
    body["location"] = args.location
if args.tentative:
    body["status"] = "tentative"
    body["transparency"] = "transparent"

try:
    svc.events().get(calendarId=cal, eventId=args.key).execute()
    svc.events().update(calendarId=cal, eventId=args.key, body=body).execute()
    action = "updated"
except HttpError as e:
    if e.resp.status != 404:
        raise
    svc.events().insert(calendarId=cal, body=body).execute()
    action = "created"

ev = svc.events().get(calendarId=cal, eventId=args.key).execute()
print(
    action,
    ev["summary"],
    ev["start"]["dateTime"],
    ev["end"]["dateTime"],
    ev.get("location", ""),
    ev.get("visibility", ""),
    sep=" | ",
)
