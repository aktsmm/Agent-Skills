# {{BOOK_TITLE}}

This repository contains the manuscript workspace for "{{BOOK_TITLE}}".

## Quick Start

1. Review `docs/page-allocation.md` and set character targets
2. Review `docs/schedule.md` and replace placeholder dates
3. Edit `.github/copilot-instructions.md` for audience and goals
4. Start outlining in `keypoints/`
5. Write drafts in `sections/`

## Repository Structure

| Path                    | Purpose                                  |
| ----------------------- | ---------------------------------------- |
| `keypoints/`            | Outline and key-point drafts             |
| `sections/`             | Main manuscript files                    |
| `re-view-output/`       | Optional Re:VIEW source and PDF output   |
| `images/`               | Figures and screenshots                  |
| `materials/`            | Reference sources                        |
| `.github/agents/`       | Writing workflow agents                  |
| `.github/instructions/` | Writing conventions                      |
| `docs/`                 | Schedule, naming rules, and writing docs |
| `scripts/`              | Counting and conversion helpers          |

## Common Commands

```powershell
python scripts/count_chars.py

# If Re:VIEW/PDF support is enabled:
# python scripts/convert_md_to_review.py
# python scripts/build_review_pdf.py
# python scripts/inspect_pdf.py pdf/book.pdf
```

## Workflow

1. Draft the structure in `keypoints/`
2. Write the manuscript in `sections/`
3. Review with `@writing-reviewer`
4. Convert with `scripts/convert_md_to_review.py` if Re:VIEW support is enabled
5. Build or polish PDF assets only when PDF output is in scope

## Metadata Layer

1. Put stable shared cover and colophon defaults in `config/review-metadata/common.yml`
2. Put project-specific author, publisher, title, subtitle, and series badge values in `config/review-metadata/project.yml`
3. If the repo contains a series, compare title naming patterns across books before fixing one title alone
4. Regenerate Re:VIEW config and cover assets through the helper scripts instead of editing generated files directly
