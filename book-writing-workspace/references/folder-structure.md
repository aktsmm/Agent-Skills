# Workspace Folder Structure

Generated projects use the following top-level layout.

## Required Folders

| Folder                   | Purpose                                                |
| ------------------------ | ------------------------------------------------------ |
| `.github/agents/`        | Writing, review, conversion, and orchestration agents  |
| `.github/instructions/`  | Writing and git instructions used by the agents        |
| `.github/prompts/`       | Reusable git prompts such as `/gc_Commit`              |
| `01_contents_keyPoints/` | Outline and section key points                         |
| `02_contents/`           | Draft and final manuscript files                       |
| `04_images/`             | Figures and image assets by chapter                    |
| `docs/`                  | Page allocation, schedule, naming rules, workflow docs |
| `scripts/`               | Helper scripts for counting and Re:VIEW conversion     |
| `output_sessions/`       | Temporary working output from agent sessions           |

## Optional Folders

| Folder               | Created When                                     |
| -------------------- | ------------------------------------------------ |
| `03_re-view_output/` | Default. Skip only when `--no-review` is used    |
| `99_material/`       | Default. Skip only when `--no-materials` is used |

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
