# Workspace Folder Structure

Generated projects use the following top-level layout.

## Required Folders

| Folder                  | Purpose                                                |
| ----------------------- | ------------------------------------------------------ |
| `.github/agents/`       | Writing and review agents                              |
| `.github/instructions/` | Writing instructions used by the agents                |
| `keypoints/`            | Outline and section key points                         |
| `sections/`             | Draft and final manuscript files                       |
| `images/`               | Figures and image assets by chapter                    |
| `docs/`                 | Page allocation, schedule, naming rules, workflow docs |
| `scripts/`              | Helper scripts for manuscript checks                   |

## Optional Folders

| Folder           | Created When                         |
| ---------------- | ------------------------------------ |
| `re-view-output/`| Created when `--with-review` is used |
| `materials/`     | Default reference materials folder   |

## Chapter Layout

Each chapter gets a matching subtree in the manuscript folders.

```text
keypoints/
  00-introduction/
sections/
  00-introduction/
images/
  00-introduction/
```

This symmetry keeps outlines, drafts, and images aligned by chapter.
