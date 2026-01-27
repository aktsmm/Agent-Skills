# Publishing to Marketplace

Complete guide for publishing your VS Code extension.

## Prerequisites

1. **Publisher account** at [marketplace.visualstudio.com/manage](https://marketplace.visualstudio.com/manage)
2. **Personal Access Token (PAT)** from Azure DevOps
3. **vsce CLI** installed: `npm install -g @vscode/vsce`

## Creating a Publisher

1. Go to [marketplace.visualstudio.com/manage](https://marketplace.visualstudio.com/manage)
2. Sign in with Microsoft account
3. Click "Create publisher"
4. Fill in:
   - **ID**: Unique identifier (used in extension ID)
   - **Name**: Display name
   - **Description**: Optional

## Getting Personal Access Token (PAT)

1. Go to [dev.azure.com](https://dev.azure.com)
2. Sign in → User Settings (top right) → **Personal access tokens**
3. Click **New Token**
4. Configure:
   - **Name**: "VS Code Marketplace" (or any descriptive name)
   - **Organization**: **All accessible organizations** ← Critical!
   - **Expiration**: Up to 1 year
   - **Scopes**: Custom defined → **Marketplace** → ✅ **Manage**
5. Click **Create** and **copy token immediately** (shown only once)

## Login and Publish

```bash
# Login (first time or when token expires)
npx @vscode/vsce login <publisher-id>
# Paste PAT when prompted

# Verify login
npx @vscode/vsce ls-publishers

# Publish new version
npx @vscode/vsce publish

# Publish with version bump
npx @vscode/vsce publish minor  # 0.1.0 → 0.2.0
npx @vscode/vsce publish patch  # 0.1.0 → 0.1.1
```

## Pre-publish Checklist

| Item                        | Check                               |
| --------------------------- | ----------------------------------- |
| `publisher` in package.json | Matches your publisher ID           |
| `version`                   | Incremented from previous           |
| `README.md`                 | Exists (lowercase!) and has content |
| `LICENSE`                   | Included                            |
| `icon`                      | 128x128 PNG, path in package.json   |
| `.vscodeignore`             | Excludes unnecessary files          |

## package.json Requirements

```json
{
  "name": "my-extension",
  "displayName": "My Extension",
  "description": "Brief description for Marketplace",
  "version": "1.0.0",
  "publisher": "your-publisher-id",
  "icon": "images/icon.png",
  "repository": {
    "type": "git",
    "url": "https://github.com/user/repo"
  },
  "categories": ["Other"],
  "keywords": ["keyword1", "keyword2"]
}
```

## Valid Categories

```
Programming Languages, Snippets, Linters, Themes, Debuggers,
Formatters, Keymaps, SCM Providers, Other, Extension Packs,
Language Packs, Data Science, Machine Learning, Visualization,
Notebooks, Education, Testing, AI, Chat
```

## Version Constraints

- ✅ Valid: `1.0.0`, `1.2.3`, `0.0.1`
- ❌ Invalid: `1.0.0-beta.1`, `1.0.0-rc1` (prerelease tags rejected)
- Use GitHub Releases for beta distribution instead

## Inspect Package Before Publishing

```bash
# List files that will be included
npx @vscode/vsce ls

# Create VSIX without publishing (for inspection)
npx @vscode/vsce package
```

## .vscodeignore

Minimize package size:

```ignore
**
!package.json
!README.md
!LICENSE
!CHANGELOG.md
!out/**
!images/icon.png

src/**
test/**
node_modules/**
*.ts
tsconfig*.json
.github/**
.vscode/**
*.vsix
```

## Updating Published Extensions

```bash
# Increment version and publish
npx @vscode/vsce publish patch

# Or manually update version first
npm version patch
npx @vscode/vsce publish
```

## Unpublishing

```bash
# Unpublish specific version
npx @vscode/vsce unpublish <publisher>.<extension> --version <version>

# Unpublish entire extension (use with caution!)
npx @vscode/vsce unpublish <publisher>.<extension>
```

## Common Errors

| Error                      | Cause                        | Fix                                |
| -------------------------- | ---------------------------- | ---------------------------------- |
| `Missing publisher`        | No publisher in package.json | Add `"publisher": "your-id"`       |
| `Personal Access Token...` | PAT invalid or expired       | Regenerate PAT with correct scopes |
| `version already exists`   | Same version published       | Increment version number           |
| `README not found`         | File missing or wrong case   | Create `README.md` (lowercase)     |
| `invalid prerelease`       | Version like `1.0.0-beta`    | Use standard version format        |

## Marketplace URLs

- **Your extensions**: `https://marketplace.visualstudio.com/manage/publishers/<publisher-id>`
- **Published extension**: `https://marketplace.visualstudio.com/items?itemName=<publisher>.<extension>`
- **Statistics**: Available in manage portal after publish
