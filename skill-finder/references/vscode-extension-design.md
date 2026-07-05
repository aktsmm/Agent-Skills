# Skill Finder VS Code Extension - Design Spec

## Overview

Agent Skill の「skill-finder」を VS Code 拡張機能化する設計仕様書。

## Why Extension?

| 項目             | Agent Skill                          | VS Code 拡張機能             |
| ---------------- | ------------------------------------ | ---------------------------- |
| **トークン消費** | 毎回 SKILL.md + スクリプト読み込み   | ゼロ                         |
| **UI**           | テキストベース                       | TreeView, QuickPick, Webview |
| **速度**         | Python/PowerShell 起動オーバーヘッド | ネイティブ TypeScript        |
| **配布**         | 手動コピー                           | Marketplace からワンクリック |
| **更新**         | 手動実行                             | 自動更新可能                 |

## Core Concept

拡張機能が「スキルのインストーラー」兼「Copilot への登録係」になる。

```
ユーザー: "pdf スキル入れて"
     ↓
┌─────────────────────────────────────────┐
│  VS Code 拡張機能                        │
│  1. skill-index.json から pdf を検索     │
│  2. GitHub から .github/skills/pdf/ DL   │
│  3. instruction file にスキル参照を追加   │
└─────────────────────────────────────────┘
     ↓
Copilot: agents.md 読む → pdf スキル認識 → 使える！
```

---

## Features

### Phase 1: MVP

- [ ] QuickPick 検索
- [ ] skill-index.json プレインストール
- [ ] .github/skills/ へインストール
- [ ] instruction file へ自動登録

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
    "default": ".github/agents.md",
    "enum": [
      ".github/agents.md",
      ".github/copilot-instructions.md",
      ".claude/CLAUDE.md",
      "custom"
    ],
    "enumDescriptions": [
      "GitHub Copilot Agents (default)",
      "GitHub Copilot Instructions",
      "Claude Code",
      "Specify custom path"
    ],
    "description": "File to register installed skills"
  },
  "skillFinder.customInstructionPath": {
    "type": "string",
    "default": "",
    "description": "Custom path when 'custom' is selected"
  },
  "skillFinder.skillsDirectory": {
    "type": "string",
    "default": ".github/skills",
    "description": "Directory to install skills"
  },
  "skillFinder.autoUpdateInstruction": {
    "type": "boolean",
    "default": true,
    "description": "Automatically update instruction file on install/uninstall"
  },
  "skillFinder.autoCheckUpdates": {
    "type": "boolean",
    "default": true,
    "description": "Check for index updates on startup"
  },
  "skillFinder.updateCheckInterval": {
    "type": "number",
    "default": 7,
    "description": "Days between update checks"
  }
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

- [pdf](.github/skills/pdf/SKILL.md) - PDF processing and manipulation
- [docx](.github/skills/docx/SKILL.md) - Word document handling

<!-- SKILL-FINDER-END -->

ここも手動の内容...
```

### Enable/Disable by Comment

```markdown
<!-- SKILL-FINDER-START -->

## Installed Skills

### Active

- [pdf](.github/skills/pdf/SKILL.md) - PDF processing

### Disabled

<!-- - [docx](.github/skills/docx/SKILL.md) - Word documents -->

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

| Agent                | Instruction File                  | Skills Directory  |
| -------------------- | --------------------------------- | ----------------- |
| **Copilot**          | `.github/agents.md`               | `.github/skills/` |
| **Copilot (legacy)** | `.github/copilot-instructions.md` | `.github/skills/` |
| **Claude Code**      | `.claude/CLAUDE.md`               | `.claude/skills/` |
| **Custom**           | User-defined                      | User-defined      |

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

---

## Author

yamapan (https://github.com/aktsmm)
