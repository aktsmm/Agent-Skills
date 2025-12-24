---
name: skill-finder
description: "Full-featured Agent Skills management: Search 35+ skills, install locally, star favorites, update from sources. Supports tag search (#azure #bicep), category filtering, and similar skill recommendations."
license: MIT
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Skill Finder

Full-featured Agent Skills management tool with search, install, star, and update capabilities.

## When to Use

- Looking for skills for a specific task or domain
- Finding and installing skills locally
- Managing favorite skills with star feature
- Keeping your skill index up-to-date
- Discovering similar skills by category

## Features

- 🔍 **Search** - Local index (35+ skills) + GitHub API + Web fallback
- 🏷️ **Tags** - Search by category tags (`#azure #bicep`)
- 📦 **Install** - Download skills to local directory
- ⭐ **Star** - Mark and manage favorite skills
- 📊 **Stats** - View index statistics
- 🔄 **Update** - Sync all sources from GitHub
- 💡 **Similar** - Get category-based recommendations

## Quick Start

### Search

```bash
# Keyword search
python scripts/search_skills.py "pdf"
pwsh scripts/Search-Skills.ps1 -Query "pdf"

# Tag search (filter by category)
python scripts/search_skills.py "#azure #development"
pwsh scripts/Search-Skills.ps1 -Query "#azure #bicep"
```

### Skill Management

```bash
# Show detailed info (includes SKILL.md content)
python scripts/search_skills.py --info skill-name

# Install to local directory
python scripts/search_skills.py --install skill-name

# Star favorite skills
python scripts/search_skills.py --star skill-name
python scripts/search_skills.py --list-starred
```

### Index Management

```bash
# Update all sources
python scripts/search_skills.py --update

# Add new source repository
python scripts/search_skills.py --add-source https://github.com/owner/repo

# View statistics
python scripts/search_skills.py --stats
```

### List Options

```bash
python scripts/search_skills.py --list-categories
python scripts/search_skills.py --list-sources
python scripts/search_skills.py --similar skill-name
```

### Add New Source

When you find a good repository, add it to your index:

```bash
python scripts/search_skills.py --add-source https://github.com/owner/repo
pwsh scripts/Search-Skills.ps1 -AddSource -RepoUrl "https://github.com/owner/repo"
```

This will:

1. Add the repository as a source
2. Search for skills in `skills/`, `.github/skills/`, `.claude/skills/`
3. Auto-add found skills to your index

## Command Reference

| Command           | Description                                |
| ----------------- | ------------------------------------------ |
| `--info SKILL`    | Show skill details with SKILL.md content   |
| `--install SKILL` | Download skill to ~/.skills or custom dir  |
| `--star SKILL`    | Add skill to favorites                     |
| `--unstar SKILL`  | Remove from favorites                      |
| `--list-starred`  | Show all starred skills                    |
| `--similar SKILL` | Find skills with matching categories       |
| `--stats`         | Show index statistics                      |
| `--update`        | Update all sources from GitHub             |
| `--check`         | Verify tool dependencies (gh, curl)        |
| `#tag` in query   | Filter by category (e.g., `#azure #bicep`) |

## Popular Repositories

### Official

| Repository                                                          | Description                           |
| ------------------------------------------------------------------- | ------------------------------------- |
| [anthropics/skills](https://github.com/anthropics/skills)           | Official Claude Skills by Anthropic   |
| [github/awesome-copilot](https://github.com/github/awesome-copilot) | Official Copilot resources by GitHub  |
| [obra/superpowers](https://github.com/obra/superpowers)             | High-quality skills, agents, commands |

### Awesome Lists

| Repository                                                                              | Description           |
| --------------------------------------------------------------------------------------- | --------------------- |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | Curated Claude Skills |
| [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)     | Claude Code focused   |

## Categories

| ID          | Description            |
| ----------- | ---------------------- |
| development | Software development   |
| testing     | Testing & QA           |
| document    | Document processing    |
| azure       | Azure services         |
| web         | Web development        |
| git         | Git & version control  |
| agents      | AI agents              |
| mcp         | Model Context Protocol |

## Files

| File                             | Description              |
| -------------------------------- | ------------------------ |
| `scripts/Search-Skills.ps1`      | PowerShell script        |
| `scripts/search_skills.py`       | Python script            |
| `references/skill-index.json`    | Skill index (35+ skills) |
| `references/starred-skills.json` | Your starred skills      |

## Requirements

- PowerShell 7+ or Python 3.8+
- GitHub CLI (`gh`) for search/install
- curl for file downloads

---

## Agent Instructions

> ⚠️ **CRITICAL**: AI agents MUST follow these instructions. Prefer action proposals over verbose explanations.

### Core Principle

**Use "Do it? Yes/No?" style proposals.**

- ❌ Bad: "If you want to add new skills, you can run the following command..."
- ✅ Good: "Update the index?"

### Skill Search Workflow

1. **Search ALL sources in local index**

   - Read `references/skill-index.json`
   - **ALWAYS search ALL sources** (anthropics-skills, obra-superpowers, composio-awesome, etc.)
   - Check `lastUpdated` field
   - Suggest matching skills from every source

2. **If not found → Propose web search**

   ```
   Not found locally. Search the web?
   → GitHub: https://github.com/search?q={query}+filename%3ASKILL.md
   ```

3. **🚨 MANDATORY: After returning results → Propose next actions**

   **This step is NOT optional. ALWAYS include the proposal block below.**

   | Situation            | Proposal                     |
   | -------------------- | ---------------------------- |
   | Skill found          | "Install it?"                |
   | Good repo discovered | "Add to sources?"            |
   | lastUpdated > 7 days | "⚠️ Index outdated. Update?" |
   | lastUpdated ≤ 7 days | "Fetch latest?" (optional)   |

### 🚨 Mandatory Proposal Block

**ALWAYS include this block at the end of every search response. No exceptions.**

**CRITICAL: Do NOT show commands. Agent executes directly. Keep proposals SHORT.**

```
**Next?**
1. 📦 Install? (which skill?)
2. 🔍 Details?
3. 🔄 Update index? (last: {date})
4. 🌐 Web search?
5. ➕ Add source?
```

### Checklist Before Responding

Before sending a search result response, verify:

- [ ] Included skill table with results (from ALL sources)
- [ ] Included **source breakdown table** showing count per source
- [ ] Showed `lastUpdated` date from index
- [ ] Added numbered action menu (NOT command examples)
- [ ] Included web search option with GitHub link ready to open
- [ ] Asked user to choose by number or skill name

### Output Format

**Skill Table (include Source with URL):**

```markdown
| Skill | Description | Source                                     | Link                                                       |
| ----- | ----------- | ------------------------------------------ | ---------------------------------------------------------- |
| name  | Description | [source-id](https://github.com/owner/repo) | [View](https://github.com/{owner}/{repo}/tree/main/{path}) |
```

**Source Breakdown Table (MANDATORY):**

```markdown
### 📊 Source Breakdown

| Source              | Skills Found | Repository                                                  |
| ------------------- | ------------ | ----------------------------------------------------------- |
| anthropics-skills   | N            | [View](https://github.com/anthropics/skills)                |
| obra-superpowers    | N            | [View](https://github.com/obra/superpowers)                 |
| composio-awesome    | N            | [View](https://github.com/ComposioHQ/awesome-claude-skills) |
| aktsmm-agent-skills | N            | [View](https://github.com/aktsmm/Agent-Skills)              |
```

**URL Construction:**

- Combine source URL + path from skill-index.json
- Example: `anthropics-skills` + `skills/docx` → `https://github.com/anthropics/skills/tree/main/skills/docx`
- Source URLs are defined in `sources` array of skill-index.json

### Agent Behavior Rules

- ❌ **NEVER** show commands like `python scripts/search_skills.py --install`
- ❌ **NEVER** say "you can run the following command..."
- ✅ **ALWAYS** execute commands directly when user chooses an action
- ✅ **ALWAYS** present options as numbered menu
- ✅ **ALWAYS** include web search option for cases not found locally
