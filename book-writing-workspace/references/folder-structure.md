# Workspace Folder Structure

Generated projects use the following top-level layout.

## Required Folders

| Folder                   | Purpose                                                |
| ------------------------ | ------------------------------------------------------ |
| `.github/agents/`        | Writing and review agents                              |
| `.github/instructions/`  | Writing instructions used by the agents                |
| `01_contents_keyPoints/` | Outline and section key points                         |
| `02_contents/`           | Draft and final manuscript files                       |
| `04_images/`             | Figures and image assets by chapter                    |
| `docs/`                  | Page allocation, schedule, naming rules, workflow docs |
| `scripts/`               | Helper scripts for manuscript checks                   |

## Optional Folders

| Folder               | Created When                         |
| -------------------- | ------------------------------------ |
| `03_re-view_output/` | Created when `--with-review` is used |
| `99_material/`       | Default reference materials folder   |

## Chapter Layout

Each chapter gets a matching subtree in the manuscript folders.

```text
01_contents_keyPoints/
  1. Chapter 1/
02_contents/
  1. Chapter 1/
04_images/
  1_Chapter_1/
```

This symmetry keeps outlines, drafts, and images aligned by chapter.
