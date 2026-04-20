# {{BOOK_TITLE}}

This repository contains the manuscript workspace for "{{BOOK_TITLE}}".

## Quick Start

1. Review `docs/page-allocation.md` and set character targets
2. Review `docs/schedule.md` and replace placeholder dates
3. Edit `.github/copilot-instructions.md` for audience and goals
4. Start outlining in `01_contents_keyPoints/`
5. Write drafts in `02_contents/`

## Repository Structure

| Path                     | Purpose                                     |
| ------------------------ | ------------------------------------------- |
| `01_contents_keyPoints/` | Outline and key-point drafts                |
| `02_contents/`           | Main manuscript files                       |
| `03_re-view_output/`     | Re:VIEW source and PDF output               |
| `04_images/`             | Figures and screenshots                     |
| `99_material/`           | Contracts, proposals, and reference sources |
| `.github/agents/`        | Writing workflow agents                     |
| `.github/instructions/`  | Writing and git conventions                 |
| `.github/prompts/`       | Reusable prompts such as `/gc_Commit`       |
| `docs/`                  | Schedule, naming rules, and writing docs    |
| `scripts/`               | Counting and conversion helpers             |

## Common Commands

```powershell
python scripts/count_chars.py
python scripts/convert_md_to_review.py
python scripts/build_review_pdf.py
python scripts/inspect_pdf.py 03_re-view_output/output_pdf/book.pdf
```

## Workflow

1. Draft the structure in `01_contents_keyPoints/`
2. Write the manuscript in `02_contents/`
3. Review with `@writing-reviewer`
4. Convert with `scripts/convert_md_to_review.py`
5. Build or polish PDF assets in `03_re-view_output/`

## Metadata Layer

1. Put stable shared cover and colophon defaults in `config/review-metadata/common.yml`
2. Put project-specific author, publisher, title, subtitle, and series badge values in `config/review-metadata/project.yml`
3. If the repo contains a series, compare title naming patterns across books before fixing one title alone
4. Regenerate Re:VIEW config and cover assets through the helper scripts instead of editing generated files directly
