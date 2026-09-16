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
- When a private event has no requested destination, register it in every
  configured calendar integration with a supported write route. Report any
  route blocked by authentication or configuration; do not silently omit it.
- Before updating an event, read its complete current state. Write the complete
  intended state for title, start, end, time zone, location, notes, categories or
  labels, availability, and visibility. Do not perform a location-only or
  notes-only update that can discard other fields.
- Put the official facility name and postal-code address in both the location
  field and the event notes. Research a missing address from a reliable source
  before writing it.
- Keep a user-selected source of truth for every event. Prefer the official
  Google Calendar API for Google writes; recover the existing connection below
  before proposing setup. Browser fallback requires explicit approval. TimeTree
  requires its own visible-UI write unless a supported integration is verified.
  A Google calendar named "TimeTree sync" is not evidence of automatic syncing;
  distinguish separate copies, external-calendar display, and verified sync.
  Never rename or delete a misleadingly named calendar without approval.
- If a browser session expires, return to the appropriate login page, have the
  user authenticate, then re-read the target calendar and check for duplicates
  before resuming.
- If an image or message does not establish a time, duration, location, target
  calendar, or whether the event is confirmed, ask only for the missing detail.
- Check OOF first; exclude full-day OOF dates unless an explicit exception is
  permitted. Holiday OOF titles do not establish personal availability or cancel
  recurring work meetings. Clarify their scope and ask whether tentative or
  unaccepted blocks should count as busy or available.
- For a meeting reschedule, verify the proposed slot against every required
  attendee. Preserve the original attendees, organizer, online-meeting link,
  location, category, and visibility when changing the time.
- Before sending a meeting update, preview its recipient, new time, and exact
  message. Use a concise generic explanation; do not disclose private calendar
  details in the update or a follow-up chat.

## Recover an Existing Google API Connection

- If the user reports prior setup, trace the successful operation in earlier
  session history and its helper/configuration references, not only recent turns.
  Inspect those locations before a bounded search of user configuration folders;
  filename searches for "Google" or "Calendar" miss `service-account.json`.
- Distinguish service-account credentials, dedicated user OAuth, and gcloud ADC.
  An ADC scope error or logged-out browser says nothing about another route.
  Reuse the established identity and calendar; do not overwrite unrelated ADC
  credentials, broaden scopes, or repeat a blocked default-client login.
- Load credentials only into the official authentication client; never print
  keys/tokens or copy them into artifacts. Read calendar metadata and ACLs to
  confirm the intended calendar, user access, and sharing before writing.
  Report failures per route, not as proof that no integration exists.

## Workflow

1. Extract the event's title, actual time, duration, place, notes, confirmation
   status, privacy level, and requested destinations from the user message,
   attachment, or source event.
2. Inspect every affected calendar for duplicates, conflicts, full-day OOF, and
   tentative holds before offering date/time choices or recommendations. Include
   travel margins and flag unknown store hours. Resolve ambiguous holds, then
   offer viable alternatives; wait for the user's selection before moving events.
   Setting `showAs=free` or transparency never resolves a real booking conflict.
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
5. Update existing event IDs in every approved destination; create only missing
   copies. For TimeTree, use visible UI and the requested label, not an
   undocumented API. Match screenshots to their service/calendar before
   diagnosing missing events.
6. Read back title, start/end, location, notes, privacy, reminders, and category
   or label from each destination; confirm the old slot no longer contains the moved event.
   Restore missing fields before reporting completion. Name each service/calendar
   and its saved, visibly confirmed, or blocked state; never describe an API
   readback as proof of client display or another service's synchronization.
7. For a rescheduled meeting, confirm that the update notification was sent. If
   the user approves a Teams follow-up, send a separate concise message only
   after the meeting update succeeds.

## Privacy Routing

- For a private event, set the requested privacy level in each private calendar.
- For a provisional hold that may be visible to others, use a neutral title such
  as `調整中（仮）` and leave the location blank; record its purpose only in an
  approved event body or comment. Set Outlook sensitivity to `normal` only when
  the user has confirmed that their sharing settings expose titles and locations
  but not the detailed body.
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
