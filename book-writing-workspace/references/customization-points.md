# Customization Points

These files are expected to be edited immediately after workspace creation.

## Project Metadata

| File                                 | Why edit it                                                                                    |
| ------------------------------------ | ---------------------------------------------------------------------------------------------- |
| `README.md`                          | Describe the book scope, workflow, and repository usage                                        |
| `.github/copilot-instructions.md`    | Define readers, goals, and project-specific constraints                                        |
| `config/review-metadata/common.yml`  | Tune stable shared defaults such as cover palette and colophon defaults                        |
| `config/review-metadata/project.yml` | Set project-specific metadata such as author list, publisher, title, subtitle, and cover badge |

## Writing Management

| File                                                            | Why edit it                                                         |
| --------------------------------------------------------------- | ------------------------------------------------------------------- |
| `docs/page-allocation.md`                                       | Set chapter and file-level character targets                        |
| `docs/schedule.md`                                              | Replace placeholder milestones and track progress                   |
| `docs/naming-conventions.md`                                    | Adjust file and image naming if the team uses a different scheme    |
| `.github/instructions/writing/writing.instructions.md`          | Tune table-first writing, figure usage, and section structure rules |
| `.github/instructions/writing/writing-notation.instructions.md` | Tune language, notation, and diagram label rules for the manuscript |

## Outline vs Manuscript Presentation Rules

If the workspace uses both outline files and final manuscript files, define early which ideas should be planned as diagrams and which should be rendered as tables in the full text.

### Recommended Rule

- Put diagram candidates in the outline or key-points side before drafting the full prose
- For each diagram candidate, capture the reader goal, not just the topic name
- Use tables in the final manuscript when comparing 3 or more terms, roles, plans, tools, or options
- Use diagrams for flow, direction, sequence, hierarchy, or source/target relationships
- Do not leave comparison-heavy sections as long bullet lists if a table would let the reader re-scan faster

### Why This Matters

Diagram needs are often discovered too late if they are deferred until section drafting.
Likewise, comparison-heavy sections become harder to read when they stay as prose or bullets instead of being normalized into tables.

## Verification and Diagram Language Rules

Before large-scale drafting begins, decide two policy points explicitly.

### Recommended Rule

- Keep unverified items in outline or key-points material as explicit follow-up notes
- Do not let unresolved facts drift into final prose as plausible-sounding explanation
- Decide whether diagrams should default to the manuscript language, and document the limited cases where original-language labels stay visible
- Keep operation names or official feature names in their original language only when readers are expected to recognize them that way

### Why This Matters

Speculative prose becomes expensive to detect once it has spread across multiple chapters.
Likewise, diagrams often drift into all-English labeling even when the manuscript is written for another language audience, which creates avoidable reading friction.

## Automation

| File                              | Why edit it                                              |
| --------------------------------- | -------------------------------------------------------- |
| `.github/agents/*.agent.md`       | Tune permissions or prompts for your team workflow       |
| `.github/prompts/*.prompt.md`     | Update branch or git conventions if needed               |
| `scripts/convert_md_to_review.py` | Extend conversion rules when the manuscript format grows |
| `scripts/build_review_pdf.py`     | Build the final PDF and regenerate cover assets          |
| `scripts/review_metadata.py`      | Merge metadata defaults and generate config/cover files  |

## Metadata Layer

If the workspace uses a shared metadata layer for Re:VIEW/PDF output, separate stable defaults from project-specific fields.

### Recommended Rule

- Put only stable shared defaults in `config/review-metadata/common.yml`
- Keep author lists, publisher, title, subtitle, and other project-specific fields in `config/review-metadata/project.yml`
- Do not place contributor-specific names in the common metadata file
- Keep cover author typography settings such as suffix, font size, and position in metadata/helper defaults
- If the repo contains a series, compare title patterns across books before finalizing one book's `booktitle` or `subtitle`
- Regenerate `config.yml` and cover assets from the metadata layer instead of editing generated files by hand

### Why This Matters

People, publisher details, title wording, and cover readability vary per project. If they are stored in a common metadata file or fixed only in exported images, they leak across projects and are easy to forget during setup or retrofits.

## LaTeX Style Injection Point

Build scripts that use `vvakame/review` Docker images typically copy the gem's default
`review-jsbook` files into `sty/` at the start of each build, overwriting any local edits.

### Rule

- **Never edit `sty/review-jsbook.cls` or `sty/review-base.sty` directly** — changes will be lost
- Place all LaTeX customizations in the **custom sty content** that the build script injects as `sty/review-custom.sty`
- In PowerShell build scripts, this is typically a heredoc variable (e.g. `$customStyContent`) written to a file before the Docker run
- In shell-based workflows, append to `sty/review-style.sty` **after** the gem copy step

### Why This Matters

If you add `\usepackage{xurl}` or other fixes directly to `sty/review-jsbook.cls`,
the next build silently reverts those changes. The fix appears to work in manual testing
but fails in CI or clean builds.

## Heading Rename Safety

When changing chapter titles that are also reflected in folder names, file names, or planning docs,
do not stop at the first rename.

### Recommended Rule

- Rename the manuscript heading and every synchronized path together
- Check that the old folder or file no longer exists physically
- Grep the old chapter title after the rename to catch leftovers in docs, prompts, or instructions
- Rebuild Re:VIEW/PDF output and confirm the old path is not still being converted

### Why This Matters

If the old chapter path remains on disk, build scripts may pick up both old and new files.
That can produce duplicated chapters or stale generated output that is hard to diagnose from PDF alone.

## Sync-Back from Final Manuscripts to Author Drafts

If your workflow keeps both final manuscripts and author draft folders, define a
clear sync-back rule before copying text from the final manuscript side back into
drafts.

### Recommended Rule

- Sync the prose that should stay aligned between final manuscript and draft
- Preserve draft-local relative asset paths if the draft folder uses a different image layout
- Do not blindly copy generated output back into draft folders
- Do not update unrelated sibling draft files just because they share the same author folder
- Keep keypoints, notes, and draft-only planning files as separate sources unless the task explicitly says to synchronize them
- After sync-back, verify matched manuscript pairs with `git diff --no-index`, hashes, or an equivalent exact comparison
- Treat chapter intro files such as `ch*-00_*.md` as mandatory sync-check targets because they drift easily

### Typical Example

If the final manuscript uses:

```markdown
![Azure Ops Dashboard GUI](images/image.png)
```

but the author draft keeps the image next to the draft file:

```markdown
![Azure Ops Dashboard GUI](image.png)
```

then sync the prose but preserve the draft-local image path instead of copying the final path verbatim.

### Why This Matters

Draft folders often serve as working sources for individual authors. They may have:

- different relative paths
- rough notes not intended for final manuscript
- additional sibling files such as keypoints or partial section drafts

Treat sync-back as a selective editorial sync, not as a raw mirror operation.
