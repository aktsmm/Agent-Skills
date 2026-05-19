# Permission Profiles

This catalog defines initial permission profiles for interactive delegated use.

## Design Rules

- Default to delegated permissions.
- Use least privilege first.
- Do not mix application permissions into the same interactive profile.
- If a request needs more privilege than the current profile, surface that escalation explicitly.

## Initial Profiles

| Profile                  | Typical Areas                                        | Typical Delegated Scopes                                | Notes                                                         |
| ------------------------ | ---------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------- |
| `mail-read-basic`        | inbox checks, light summaries                        | `Mail.Read`                                             | Common read fallback when WorkIQ is insufficient              |
| `mail-write`             | send, reply, move, update mail                       | `Mail.ReadWrite`, `Mail.Send`                           | Needed for most mail mutation flows                           |
| `calendar-read-basic`    | event lookups, availability checks                   | `Calendars.Read`                                        | Common meeting and event reads                                |
| `calendar-write`         | create, update, or respond to events                 | `Calendars.ReadWrite`                                   | Use for scheduling, updates, and accept or decline workflows  |
| `contacts-basic`         | contact lookup and update                            | `Contacts.Read`, `Contacts.ReadWrite`                   | Split later if needed                                         |
| `files-read-basic`       | OneDrive and simple file reads                       | `Files.Read`                                            | Escalate only when user intent truly needs broader file reach |
| `files-write`            | upload, update, move personal files                  | `Files.ReadWrite`                                       | Personal or signed-in user scope first                        |
| `sharepoint-read-broad`  | site, drive, or document reads beyond personal scope | `Sites.Read.All`, optionally `Files.Read.All`           | Higher-risk profile; call out explicitly                      |
| `sharepoint-write-broad` | site-level file mutation                             | `Sites.ReadWrite.All`, optionally `Files.ReadWrite.All` | Higher-risk profile; require stronger explanation             |
| `directory-read`         | users, groups, apps, devices                         | resource-specific least privilege based on endpoint     | Often tenant-sensitive; avoid broad fallback guesses          |
| `planner-tasks-write`    | Planner, To Do, tasks                                | endpoint-specific least privilege                       | Keep separate because support patterns vary                   |

## Escalation Guidance

- If the requested operation crosses from user-owned data into tenant-wide or site-wide data, call out the escalation before execution.
- If the operation needs a broad directory or SharePoint scope, say so explicitly in the confirmation summary.
- If the exact least-privileged scope is unclear, perform metadata lookup before attempting execution.

## Future Split

This first version intentionally keeps the profile catalog compact. Split profiles further only when:

- user-owned and tenant-wide operations frequently diverge
- consent friction becomes high
- the same profile is being used for too many unrelated operations
