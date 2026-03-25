# Customization Points

These files are expected to be edited immediately after workspace creation.

## Project Metadata

| File                              | Why edit it                                             |
| --------------------------------- | ------------------------------------------------------- |
| `README.md`                       | Describe the book scope, workflow, and repository usage |
| `.github/copilot-instructions.md` | Define readers, goals, and project-specific constraints |

## Writing Management

| File                         | Why edit it                                                      |
| ---------------------------- | ---------------------------------------------------------------- |
| `docs/page-allocation.md`    | Set chapter and file-level character targets                     |
| `docs/schedule.md`           | Replace placeholder milestones and track progress                |
| `docs/naming-conventions.md` | Adjust file and image naming if the team uses a different scheme |

## Automation

| File                              | Why edit it                                              |
| --------------------------------- | -------------------------------------------------------- |
| `.github/agents/*.agent.md`       | Tune permissions or prompts for your team workflow       |
| `.github/prompts/*.prompt.md`     | Update branch or git conventions if needed               |
| `scripts/convert_md_to_review.py` | Extend conversion rules when the manuscript format grows |

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
