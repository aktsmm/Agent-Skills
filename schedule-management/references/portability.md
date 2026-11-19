# Portability and Calendar Routes

What another environment needs to run `schedule-management` end to end.

## Assets

| Kind | Item | Notes |
|---|---|---|
| Rules | `SKILL.md` | Copy the whole skill folder. |
| Preferences | Default destinations, address verification, provisional-hold style | Live in the user's memory, not here; restate them in the target harness's instructions. |
| Outlook | A Microsoft Graph calendar route (WorkIQ MCP or Graph API) | Read, create, update, availability, sensitivity. |
| Google | `scripts/google_calendar_upsert.py` | Env `GOOGLE_CALENDAR_SA_JSON`, `GOOGLE_CALENDAR_ID`; the service account must have owner access to the target calendar. |
| TimeTree | `scripts/start-calendar-browser.ps1` + `scripts/timetree_create_event.py` | Env `TIMETREE_CALENDAR_URL`, `CALENDAR_BROWSER_CDP`; needs a persistent signed-in Edge profile. |
| Secrets | Service-account key, TimeTree login | Never copy into the repo; re-provision per machine and keep only the location in the host's private notes. |
| Packages | `google-api-python-client`, `google-auth`, `playwright` (Python) | Install on first failure only. |

## Gotchas

- TimeTree has no supported write API; the CDP browser writes through the visible UI. The browser may need a relaunch and a re-check of the signed-in calendar before use.
- TimeTree restores an unsaved draft after a relaunch. Navigate to a fresh `events/new` URL and confirm the form fields before saving, or a draft of another event can be saved by mistake.
- The TimeTree Note field opens a modal that blocks Save until OK is pressed.
- A screenshot taken right after a click can show the previous state; read field values from the DOM before trusting it.
- Time dropdown options exist as hidden duplicates (tiny month-cell labels also match the text); click only the dropdown item (width > 100 px), then confirm both times in the form before saving.
- A timed-out readback does not mean the save failed. Re-running the creation after a timeout or a partial form creates duplicates (one retry produced four events with wrong end times). Count same-title events in the month view first, edit or delete by event URL, and never blindly retry.
- The month view may still show the previous month right after navigation, and its header renders before the events do (a count taken too early returns a false 0 and leads to a duplicate); wait for the header plus a few seconds before counting events.
- To delete in the TimeTree UI: open the event, Menu, Delete, then click the confirmation Delete (a forced click is needed because an overlay intercepts it). Delete only by event id after reading its time.
- Google event ids accept only a-v and 0-9 (base32hex); the script rejects other keys before calling the API.
- A Google calendar named like a sync target is a separate calendar, not proof of sync.

## Shared Availability Sheets

- Rows are people; names may differ from the user's by one character. Confirm which row is the user's before writing.
- Treat a cell marked partially available with a stated limit (for example "after 18:00") as available only inside that limit and block just that window; note the original range in the notes.
- Register provisional holds with a leading `【仮】`, showAs tentative, no attendees and no location.
- Work-related holds go to the work calendar first; ask before copying them to personal calendars.
