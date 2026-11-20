# Event Patterns

Patterns that go beyond a plain appointment. The title and category rules in `SKILL.md` and `labels.md` still apply.

## Flight

- Title: `HH:MM発｜移動（出発空港 → 到着空港／航空会社 便名）`. `HH:MM` is the departure in the departure airport's local time.
- Block start = departure minus the user's stated airport lead time (including travel to the airport). Ask when no lead time is given; end at the arrival or a user-chosen buffer.
- Notes: carrier, flight number, local and JST times for both ends (convert explicitly; an overnight arrival falls on the next local date), fare and baggage if shown, ticket status (bought or not), lodging status.
- Location: terminal plus the address from the airport's official page. If the page cannot be read, name the facility only and write "address unverified" in the notes.
- A red-eye flight with an advice to reach the airport the previous day: record the advice in the notes; do not block the previous day unless asked.
- TimeTree time pickers move in 30-minute steps: use the nearest boundary and keep the exact time in the title and notes.

## Leave

- All-day, out of office (Outlook), no category: the out-of-office state is the signal.
- Title `年休予定 | <purpose>`; notes say the leave is not yet approved and that the request is separate.
- All-day end: Google and Outlook store the day after the last leave day (exclusive); TimeTree shows the last day.
- Leave is a work-calendar entry: start with the work calendar and ask before mirroring it to personal calendars (the owner may then ask for all).

## Overlapping all-day banners

A trip-wide all-day event next to a leave event and travel blocks reads as duplicates. Keep one all-day banner per purpose (usually the leave) and let the travel blocks show the trip; ask before adding a trip-wide banner, and delete only after the owner chooses which to keep.
