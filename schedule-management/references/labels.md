# Calendar Label Scheme

Assign one category per event, deciding by who is involved and how much it matters. Importance runs red > orange > yellow > blue; green and purple sit outside that order. Match by **color**, not name: the owner may rename categories, so read the live category list and use the entry with the color below. The API tools cannot create or rename categories; rename them in Outlook settings (procedure below) only when the owner asks.

## Decision order (first match wins)

1. Travel (flight, train, hotel) → purple.
2. Private (gym, clinic, leisure) → green.
3. A customer attends, or the owner is the main speaker or presenter (including an internal meeting), or the owner is on duty for a customer (on-call or standby shifts, even when no customer is in a meeting) → red.
4. Work done for a customer that is not customer-facing: an internal meeting with others, or the owner's own preparation or verification block (【準備】【検証】) → orange.
5. Work done alone that is not for a specific customer (learning time, self-study, watching a session) → yellow.
6. Any other internal recurring meeting, 1:1, V-TEAM, or relationship meeting (1:3, career talk) → blue (lowest priority).

## Colors and names (as of the last setup)

| Color | Category name | Typical events |
|---|---|---|
| Red | 🔴 顧客・メイン | customer deliveries, workshops, hearings, customer events, talks, internal meetings the owner leads, on-call or standby shifts |
| Orange | 🟠 顧客のための準備・社内会議 | internal customer-case meetings, rehearsals, reviews, 【準備】【検証】 blocks |
| Yellow | 🟡 個人ワーク・研修 | Learning Time, self-study, general solo work |
| Blue | 🔵 内部定例・1on1・V-TEAM | team syncs, V-TEAM, 1:1, 1:3, career conversations |
| Green | 🟢 私用 | gym, clinic, leisure |
| Purple | 🟣 移動 | flights, trains, hotels |

Leave the separate maroon "Important" category alone.

## Rules

- Tentative holds keep the color of their purpose; the 【仮】 prefix and the tentative availability mark them.
- Leave leave-of-absence entries (年休) uncategorized: their out-of-office status is the signal.
- When the user states a color for a specific event, follow it even if the decision order gives another.
- Past events are not relabeled when the scheme changes; only new events follow it. Renaming a category in Outlook renames it on every event that carries it.
- Apply labels one write at a time: parallel writes to the same mailbox get throttled (HTTP 429) and are not replayed, so re-read before retrying. After changing categories on an event with attendees, read back that the attendees were not altered.
- TimeTree: use the nearest label for the same purpose (red → Apple red, blue → Deep sky blue, purple → Soft violet, orange → Bright orange, green → Emerald green). Google has no labels; rely on the title.

## Renaming categories in Outlook on the web (when asked)

Open any calendar view → Categories → Review categories → Open in Settings (Settings > Account > Categories). Use each row's labeled Edit button (aria-label "Edit <name>"), change the name field, then press Save; the color list in that panel is only needed to change colors. Never click by coordinates: the trash icon sits beside the pencil and opens a delete confirmation (Cancel it).
