# Private Skill Intake Workflow

Intake brings existing skills into the private repository before optional curation. Run it only when the user explicitly asks to intake, import, or refresh. Two sources exist; pick by the request, never merge their outputs.

| Request                    | Action                                        |
| -------------------------- | --------------------------------------------- |
| Intake and improve         | Intake first, then run normal retro authoring |
| Intake only                | Intake and stop before curation               |
| Normal private-skill retro | Skip intake                                   |

## Source A: Local Copilot skill mirror

Run `<private-repo>/scripts/Sync-CopilotSkillsToPrivateRepo.ps1`. It mirrors local skill sources into separate `copilot-skills/skills/` and `copilot-skills/m-skills/` trees and regenerates the mirror README.

This pre-step alone may write under `<private-repo>/copilot-skills/**`. Never mix mirror output and curated edits in the same target tree.

## Source B: Workspace skill

Source is `.github/skills/<skill>` of the workspace the user named or the active workspace; never substitute the current directory or create an external folder. If no workspace resolves, stop. Treat it as a read-only source.

Read it, then write an abstracted version to `<private-repo>/.github/skills/<skill>/`: replace customer, project, file-structure and operating-rule specifics with portable wording. If a specific cannot be abstracted, do not copy it; stop with `scope 不一致` for that skill. Never leave a raw copy in the private repo.

## Duplicate check (both sources)

Before writing, check whether `.github/skills/<skill>/` already contains a curated skill with the same name. Stop and ask for an explicit coexistence or rename decision instead of creating an ambiguous raw duplicate.
