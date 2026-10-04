# Skill Finder VS Code Extension - Design Spec

## Overview

Agent Skill の「skill-finder」を VS Code 拡張機能化する設計仕様書。

> 注記 (2026-10 確認): VS Code / Copilot は `.github/skills/`・`.claude/skills/`・`.agents/skills/`（personal は `~/.copilot/skills/` 等）をネイティブに発見し、skill は slash command としても出る。instruction file への登録は必須ではなく、拡張から配布する場合は `contributes.chatSkills` を使う。出典: https://code.visualstudio.com/docs/agent-customization/agent-skills

## Why Extension?

| 項目             | Agent Skill                          | VS Code 拡張機能             |
| ---------------- | ------------------------------------ | ---------------------------- |
| **トークン消費** | 毎回 SKILL.md + スクリプト読み込み   | ゼロ                         |
| **UI**           | テキストベース                       | TreeView, QuickPick, Webview |
| **速度**         | Python/PowerShell 起動オーバーヘッド | ネイティブ TypeScript        |
| **配布**         | 手動コピー                           | Marketplace からワンクリック |
| **更新**         | 手動実行                             | 自動更新可能                 |

## Core Concept

拡張機能が「スキルのインストーラー」になる。発見は VS Code / Copilot の native skill discovery に任せ、instruction file への登録は任意（legacy 互換）とする。

```
ユーザー: "<skill> スキル入れて"
     ↓
┌─────────────────────────────────────────┐
│  VS Code 拡張機能                        │
│  1. skill-index.json から <skill> を検索 │
│  2. GitHub から skills/<skill>/ を DL    │
│  3. .github/skills/<skill>/ へ配置       │
└─────────────────────────────────────────┘
     ↓
Copilot: native discovery で SKILL.md を認識 → slash command としても使える
```

---

## Features

### Phase 1: MVP

- [ ] QuickPick 検索
- [ ] skill-index.json プレインストール
- [ ] .github/skills/ へインストール
- [ ] （任意・legacy）instruction file への登録。native discovery では不要

### Phase 2: UX 改善

- [ ] サイドバー TreeView
- [ ] Star 管理（ワークスペース設定）
- [ ] GitHub API 連携（最新スキル取得）

### Phase 3: リッチ機能

- [ ] Webview でスキル詳細・プレビュー
- [ ] 自動更新通知
- [ ] Marketplace 公開

---

## Project Structure

```
skill-finder-vscode/
├── package.json              # 拡張機能マニフェスト
├── tsconfig.json
├── src/
│   ├── extension.ts          # エントリポイント
│   ├── skillIndex.ts         # インデックス管理
│   ├── skillSearch.ts        # 検索ロジック
│   ├── skillInstaller.ts     # インストール機能
│   ├── instructionManager.ts # agents.md 更新
│   ├── treeProvider.ts       # サイドバー TreeView (Phase 2)
│   └── webviewPanel.ts       # スキル詳細表示 (Phase 3)
├── resources/
│   └── skill-index.json      # プレインストールインデックス
└── README.md
```

---

## Settings (package.json contributes.configuration)

```jsonc
{
  "skillFinder.instructionFile": {
    "type": "string",
    "default": "AGENTS.md",
    "enum": [
      "AGENTS.md",
      ".github/copilot-instructions.md",
      "CLAUDE.md",
      "custom",
    ],
    "enumDescriptions": [
      "AGENTS.md (default)",
      "GitHub Copilot Instructions",
      "Claude Code",
      "Specify custom path",
    ],
    "description": "File to register installed skills (optional; native discovery does not need it)",
  },
  "skillFinder.customInstructionPath": {
    "type": "string",
    "default": "",
    "description": "Custom path when 'custom' is selected",
  },
  "skillFinder.skillsDirectory": {
    "type": "string",
    "default": ".github/skills",
    "description": "Directory to install skills",
  },
  "skillFinder.autoUpdateInstruction": {
    "type": "boolean",
    "default": false,
    "description": "Automatically update instruction file on install/uninstall",
  },
  "skillFinder.autoCheckUpdates": {
    "type": "boolean",
    "default": true,
    "description": "Check for index updates on startup",
  },
  "skillFinder.updateCheckInterval": {
    "type": "number",
    "default": 7,
    "description": "Days between update checks",
  },
}
```

---

## Commands

| Command                          | Description                    |
| -------------------------------- | ------------------------------ |
| `skillFinder.search`             | Search skills by keyword/tag   |
| `skillFinder.browse`             | Browse skills by category      |
| `skillFinder.install`            | Install a skill                |
| `skillFinder.uninstall`          | Uninstall a skill              |
| `skillFinder.showInstalled`      | Show installed skills          |
| `skillFinder.showStarred`        | Show starred skills            |
| `skillFinder.star`               | Star a skill                   |
| `skillFinder.unstar`             | Unstar a skill                 |
| `skillFinder.updateIndex`        | Update skill index from remote |
| `skillFinder.addSource`          | Add custom source repository   |
| `skillFinder.refreshInstruction` | Regenerate instruction file    |

---

## Instruction File Format

### Section Marker Approach

既存のインストラクションを壊さないように、マーカーで囲む:

```markdown
# My Custom Instructions

ここは手動で書いた内容...

<!-- SKILL-FINDER-START -->

## Installed Skills

The following skills are available in this workspace.

- [skill-a](.github/skills/skill-a/SKILL.md) - Example skill A
- [skill-b](.github/skills/skill-b/SKILL.md) - Example skill B

<!-- SKILL-FINDER-END -->

ここも手動の内容...
```

### Enable/Disable by Comment

```markdown
<!-- SKILL-FINDER-START -->

## Installed Skills

### Active

- [skill-a](.github/skills/skill-a/SKILL.md) - Example skill A

### Disabled

<!-- - [skill-b](.github/skills/skill-b/SKILL.md) - Example skill B -->

<!-- SKILL-FINDER-END -->
```

---

## Index Management

### 2-Layer Structure

```
┌─────────────────────────────────────────────────┐
│  Extension Package (.vsix)                       │
│  └── resources/skill-index.json  ← Pre-installed │
└─────────────────────────────────────────────────┘
                    ↓ Copy on first launch
┌─────────────────────────────────────────────────┐
│  User Data (globalStorageUri)                    │
│  └── skill-index.json            ← Updatable     │
│  └── starred-skills.json         ← User data     │
│  └── custom-sources.json         ← User added    │
└─────────────────────────────────────────────────┘
```

### Update Flow

```
Extension Startup
    ↓
Local index exists?
    ├── NO → Copy bundled index
    └── YES → Check for updates (if setting enabled)
                ↓
          Older than N days?
              ├── YES → Show "Update available" notification
              └── NO → Use local index
```

### Merge Strategy on Update

```typescript
interface SkillIndex {
  version: string;
  lastUpdated: string;
  sources: Source[]; // Merge (keep user additions)
  skills: Skill[]; // Overwrite (update to latest)
}

// Separate user data files
interface UserData {
  starred: string[]; // Preserve
  customSources: Source[]; // Preserve
}
```

---

## Agent Compatibility Matrix

| Agent           | Instruction File                                            | Skills Directory                                        |
| --------------- | ----------------------------------------------------------- | ------------------------------------------------------- |
| **Copilot**     | `AGENTS.md` or `.github/copilot-instructions.md` (optional) | `.github/skills/`, `.claude/skills/`, `.agents/skills/` |
| **Claude Code** | `CLAUDE.md` / `.claude/CLAUDE.md` (optional)                | `.claude/skills/`                                       |
| **Custom**      | User-defined                                                | User-defined                                            |

---

## Source Files to Reference

既存の Python 実装から移植する:

- `skill-finder/scripts/search_skills.py` - 検索ロジック
- `skill-finder/references/skill-index.json` - インデックス構造
- `skill-finder/references/starred-skills.json` - Star 保存形式

---

## Development Notes

### Dependencies

```json
{
  "devDependencies": {
    "@types/node": "^20.x",
    "@types/vscode": "^1.85.0",
    "typescript": "^5.x",
    "esbuild": "^0.20.x"
  }
}
```

### Key VS Code APIs

- `vscode.window.showQuickPick()` - 検索 UI
- `vscode.window.createTreeView()` - サイドバー
- `vscode.workspace.fs` - ファイル操作
- `vscode.ExtensionContext.globalStorageUri` - ユーザーデータ保存
- `vscode.workspace.getConfiguration()` - 設定取得
