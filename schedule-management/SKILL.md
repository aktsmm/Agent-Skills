---
name: schedule-management
description: "Plan, create, update, and verify personal calendar events across Outlook, Google Calendar, and TimeTree. Use when the user asks to add, change, move, organize, synchronize, or check a schedule, travel, hotel, appointment, or calendar event."
argument-hint: "予定の内容、日時、場所、登録先、公開範囲、または変更内容"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan
---

# Schedule Management

## When to Use

- Use for "予定入れて", "予定を変更", "予定をずらして", "カレンダーに追加",
  "空いている時間", "新幹線", "ホテル", "予約", "Outlook", "Google Calendar",
  "TimeTree", or "同期".
- Use for both new events and updates to existing events.
- Do not use for booking a third-party service, replying to an invitation, or
  creating a Teams meeting unless the user explicitly requests that action.

## Core Rules

- Treat calendar content as private. Confirm the target calendar and visibility
  before writing sensitive personal, medical, financial, relationship, or travel
  details to a shared calendar.
- Never infer that a write reached the intended account or calendar from a single
  backend result. Identify the account and calendar, then read the saved event
  back from every requested destination. If the client display is delayed, say
  it is pending visual sync rather than claiming it is visible.
- Use a stable source key or idempotency identifier when an API supports it so
  retries update the same event instead of creating duplicates.
- Before updating an event, read its complete current state. Write the complete
  intended state for title, start, end, time zone, location, notes, categories or
  labels, availability, and visibility. Do not perform a location-only or
  notes-only update that can discard other fields.
- Put the official facility name and postal-code address in both the location
  field and the event notes. Research a missing address from a reliable source
  before writing it.
- Keep a user-selected source of truth for every event. Use an API for supported
  destinations, but treat TimeTree as a visible-UI workflow unless the user
  provides an official supported integration; do not claim automatic TimeTree
  extraction or synchronization.
- If a browser session expires, return to the appropriate login page, have the
  user authenticate, then re-read the target calendar and check for duplicates
  before resuming.
- If an image or message does not establish a time, duration, location, target
  calendar, or whether the event is confirmed, ask only for the missing detail.
- When evaluating available times, check OOF blocks first. Do not offer a
  full-day OOF date; ask whether tentative or unaccepted events should be treated
  as busy or available.
- For a meeting reschedule, verify the proposed slot against every required
  attendee. Preserve the original attendees, organizer, online-meeting link,
  location, category, and visibility when changing the time.
- Before sending a meeting update, preview its recipient, new time, and exact
  message. Use a concise generic explanation; do not disclose private calendar
  details in the update or a follow-up chat.

## Workflow

1. Extract the event's title, actual time, duration, place, notes, confirmation
   status, privacy level, and requested destinations from the user message,
   attachment, or source event.
2. Inspect every affected calendar for duplicates, conflicts, full-day OOF, and
   tentative holds. Present a compact plan before a large or ambiguous batch.
3. Resolve missing facility addresses and format a shared location string as
   `施設名｜〒郵便番号 住所`. Copy it into the notes as `場所` and `住所`.
4. Apply the appropriate event pattern:
   - **Travel:** block in 30-minute increments beginning at least 15 minutes
     before the actual departure. Use
     `HH:MM発｜移動（出発駅 → 到着駅／新幹線）` as the title and record
     carrier, service number, and actual departure/arrival in notes. Apply the
     purple `移動` category in Outlook and the `Soft violet` label in TimeTree.
   - **Hotel:** use a one-hour check-in block. Put the check-in time in the title
     as `HH:MM チェックイン｜ホテル名`, apply the same purple travel label, and
     include hotel name, address, check-in, and check-out in notes.
   - **Appointment:** when a travel buffer is requested, block the requested
     buffer while keeping the confirmed appointment time in notes. Mark an
     unconfirmed appointment as provisional.
5. Write or update every approved destination. For TimeTree, use visible UI
   automation and the requested label; do not rely on an undocumented API.
6. Read back title, start/end, location, notes, privacy, and category or label
   from each destination. If a field is missing, restore the full intended event
   state and re-verify before reporting completion.
7. For a rescheduled meeting, confirm that the update notification was sent. If
   the user approves a Teams follow-up, send a separate concise message only
   after the meeting update succeeds.

## Privacy Routing

- For a private event, set the requested privacy level in each private calendar.
- For a shared calendar, use a generic blocker without names or notes only when
  the user explicitly asks for a dummy event. Add its location only when the user
  explicitly requests it.
- Always set a TimeTree dummy event to `Soft violet` unless the user explicitly
  chooses another label; never retain the label of an event being converted into
  a dummy.
- Keep detailed information out of destinations the user has not approved.

## Done Criteria

- Every requested calendar contains exactly one intended event.
- The displayed account and calendar match the requested destination.
- Time, location, notes, visibility, and category or label are present after
  readback.
- Travel and hotel events use their standardized title and purple category or
  label.
- Updates retain required existing information unless the user explicitly removed
  it.
