# Setup Guide

Requirements and setup instructions for Skill Finder.

## Requirements

### Required Tools

| Tool           | Version | Purpose                           | Install                                   |
| -------------- | ------- | --------------------------------- | ----------------------------------------- |
| **GitHub CLI** | 2.0+    | Search/install skills from GitHub | [cli.github.com](https://cli.github.com/) |
| **curl**       | Any     | Download files                    | Pre-installed on most systems             |

### Optional (choose one)

| Runtime    | Version | Script                      |
| ---------- | ------- | --------------------------- |
| PowerShell | 7+      | `scripts/Search-Skills.ps1` |
| Python     | 3.8+    | `scripts/search_skills.py`  |

## Installation

### 1. Install GitHub CLI

```bash
# Windows (winget)
winget install GitHub.cli

# macOS (Homebrew)
brew install gh

# Linux (apt)
sudo apt install gh
```

### 2. Authenticate

```bash
gh auth login
```

### 3. Verify

```bash
gh --version
curl --version
```

### Verify Dependencies

```bash
python scripts/search_skills.py --check
pwsh scripts/Search-Skills.ps1 -Check
```

**Expected output:**

```
✅ gh: installed (version 2.x.x)
✅ curl: installed
✅ All dependencies satisfied
```

## Troubleshooting

| Issue                   | Solution                                    |
| ----------------------- | ------------------------------------------- |
| `gh: command not found` | Install GitHub CLI and add to PATH          |
| `gh auth login` fails   | Run `gh auth login` and follow prompts      |
| Rate limit exceeded     | Wait or use authenticated requests          |
| curl SSL errors         | Update curl or check network/proxy settings |

## Popular Repositories

### Official (type: `official`)

- [anthropics/skills](https://github.com/anthropics/skills) - Official Claude Skills by Anthropic
- [github/awesome-copilot](https://github.com/github/awesome-copilot) - Official Copilot resources by GitHub

### Curated Lists (type: `awesome-list`)

- [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)

### Community (type: `community`)

- [obra/superpowers](https://github.com/obra/superpowers)
- Run `--list-sources` for full list

## Categories

Dynamically extracted from skill-index.json. Run `--list-categories` for current list.

Common: `development`, `testing`, `document`, `azure`, `web`, `git`, `agents`, `mcp`, `cloud`, `creative`, `planning`
