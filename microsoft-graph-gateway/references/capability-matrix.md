# Capability Matrix

This matrix defines which surfaces belong in the gateway and what kind of support exists today.

| Area                        | Microsoft Graph Surface           | Current Best Fit                    | Notes                                                                                        |
| --------------------------- | --------------------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------- |
| Mail                        | Outlook mail                      | Raw Graph + curated mail tools      | Read, search, send, reply, move, and folder operations are all available in Graph.           |
| Calendar                    | Outlook calendar                  | Raw Graph + curated calendar tools  | Event creation, update, response, and availability checks are first-class Graph scenarios.   |
| Contacts / People           | Outlook contacts, People          | Raw Graph, partial curated support  | Contacts are common; People and relevance-based scenarios usually need exact Graph handling. |
| Files / OneDrive            | OneDrive driveItem APIs           | Raw Graph + curated file tools      | Upload, download, search, browse, and content operations are common.                         |
| SharePoint                  | Sites, drives, lists              | Raw Graph, targeted curated support | SharePoint often needs exact IDs, site paths, permission inspection, or sharing semantics.   |
| Teams                       | Teams, chats, channels, meetings  | Raw Graph first                     | Broad support exists, but current candidate substrates are thinner here.                     |
| Directory                   | Users, groups, apps, devices      | Raw Graph first                     | Exact permissions, filters, and tenant-specific policy handling matter here.                 |
| Planner / Tasks / To Do     | Planner and To Do APIs            | Raw Graph first                     | Useful for later convenience tools, but raw access should exist first.                       |
| Search / Reports / Insights | Search, reports, people, insights | Raw Graph first                     | Often require exact endpoint knowledge and careful permission handling.                      |

## Design Consequence

- Do not try to represent the full Graph surface as only curated commands.
- Preserve a generic raw execution path so the skill can reach arbitrary endpoints.
- Add convenience tools only for high-frequency workflows after the raw path exists.
