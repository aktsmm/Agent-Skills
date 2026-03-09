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
