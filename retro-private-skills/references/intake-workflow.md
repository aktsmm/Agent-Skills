# Private Skill Intake Workflow

Intake mechanically mirrors local Copilot skills into the private repository before optional curation. Run it only when the user explicitly asks to intake, import, or refresh local copies.

| Request                    | Action                                        |
| -------------------------- | --------------------------------------------- |
| Intake and improve         | Mirror first, then run normal retro authoring |
| Intake only                | Mirror and stop before curation               |
| Normal private-skill retro | Skip intake                                   |

Run `<private-repo>/scripts/Sync-CopilotSkillsToPrivateRepo.ps1`. It mirrors local skill sources into separate `copilot-skills/skills/` and `copilot-skills/m-skills/` trees and regenerates the mirror README.

This pre-step alone may write under `<private-repo>/copilot-skills/**`. Curated authoring remains limited to `.github/skills/<skill>/`. Never mix mirror output and curated edits in the same target tree.

Before mirroring, check whether `.github/skills/<skill>/` already contains a curated skill with the same name. Stop and ask for an explicit coexistence or rename decision instead of creating an ambiguous raw duplicate.
