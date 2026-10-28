# Upcoming Events: Reminders and Post-Event Follow-up

Use when a dated future event (meeting, visit, workshop, deadline) appears in minutes, mail, chat, or task review.

## Ledger

- Keep one ledger file for future events outside the task files (a data-source folder is fine; avoid folders whose every edit triggers dashboard regeneration). Columns: date, time, customer or category, event, preparation due before it, status (`confirmed` / `needs confirmation`), source, result check (`pending` / `done` / `n/a`), result note.
- Register without waiting to be asked. Mark `needs confirmation` for summaries, proposals, or dates that differ between sources; keep one row per date and drop superseded dates once confirmed. Record a date change in the result note.
- A confirmed status needs the organizer's notice or an original message. An AI summary or a user's relay is `needs confirmation` until matched.
- Move rows to an archive section 30 days after the result check is `done` or `n/a`.

## Scheduled run (read-only, unattended)

Use a cheap model, once per business day in the morning. The run:

1. Reminder: list events dated today or the next business day, plus `needs confirmation` events within three business days, with preparation items and open points.
2. Result check: for each past event whose result check is `pending`, query the available workplace data (minutes, mail, chat, shared material) once per event with date, customer, and event name. Write findings only to the result note as `candidate (unverified): <what, source name, date>` or `not found (<query date>)`.
3. Write one dated output file (reminders first, result checks second, unchecked rows with reasons last). A day with nothing due is one line.

Boundaries: do not mark a result `done`, create or complete tasks, edit customer records, send messages, or change events. The user confirms results; suggested next actions stay in the output. On re-authentication, consent, denial, or permission errors, mark the row `unconfirmed (reason)` and stop; do not switch connection routes. Not found is not proof the event did not happen.

## Hook into the workspace

Add a short rule to the task-management instruction (register events found during task or meeting work) and one line to the daily/weekly operation entry so the ledger is read when reports and dashboards are refreshed.
