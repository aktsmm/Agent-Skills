# Agent Skills

A collection of Agent Skills for GitHub Copilot and Claude.

GitHub Copilot と Claude 向けの Agent Skills コレクションです。

## Demo

### OCR Super Surya

![OCR Demo](assets/image.png)

### draw.io Diagram Forge

![draw.io Demo](assets/drawio-demo.gif)

## Skills

<!-- public-skills-table:start -->
| Skill | Description / 説明 |
| --- | --- |
| [agentic-workflow-guide](agentic-workflow-guide/) | Design, review, and debug agent workflows, and decide when a request should use a prompt, instruction, skill, agent, or hook before escalating to multi-agent design. Use for .ag... |
| [analyze-copilot-sessions](analyze-copilot-sessions/) | Analyze historical VS Code GitHub Copilot Chat sessions by model, reasoning effort, AIU, time, reliability, workflow behavior, and external quality evidence; compare sessions wh... |
| [azure-advisor-report](azure-advisor-report/) | Generate Azure environment monthly report (Markdown + PowerPoint) from Azure Advisor and Cost Management API |
| [azure-env-builder](azure-env-builder/) | [Alpha] Experimental Azure environment builder for infrastructure and deployment design |
| [azure-infra-validation](azure-infra-validation/) | Build and validate Azure infrastructure in a lab or sandbox using Azure CLI and official Microsoft docs |
| [azure-screenshot-mask](azure-screenshot-mask/) | Mosaic environment-sensitive areas (tenant name, user avatar, subscription name / ID, resource group, internal hostnames) on Azure Portal screenshots before publishing to blogs,... |
| [azure-troubleshooting](azure-troubleshooting/) | Investigate Azure incidents and service degradations with a read-only workflow using Azure CLI, Resource Health, Activity Log, and official Microsoft docs |
| [azure-update-customer-pptx](azure-update-customer-pptx/) | Build a customer-facing Azure Update PowerPoint from Azure Updates MCP results, including customer classification, Japan region stamps, UPDATE Points, speaker notes, and Verify-... |
| [biz-ops-setup](biz-ops-setup/) | Business operations workspace setup with workIQ integration. Creates report generation, task management, and customer management system |
| [book-writing-workspace](book-writing-workspace/) | Operate a reusable technical book manuscript workspace with writing structure, review rules, and optional Markdown to Re:VIEW/PDF support |
| [browser-max-automation](browser-max-automation/) | Browser automation using Playwright MCP, CDP, and direct WebSocket CDP for web testing, UI verification, and form automation |
| [chrome-extension-dev](chrome-extension-dev/) | Chrome/ブラウザ拡張機能開発の包括的ガイド。WXTフレームワーク、Manifest V3、Chrome API、テスト手法をカバー。Use when: ブラウザ拡張機能を作成・修正する時。Triggers on 'ブラウザ拡張機能', 'Chrome拡張', 'browser extension', 'WXT', 'content script'... |
| [code-simplifier](code-simplifier/) | Guide for simplifying and refining code after coding sessions |
| [context-to-video](context-to-video/) | Turn any context (blog URL, pasted article, PR diff, meeting notes, release notes, raw prompt) into a narrated explainer mp4 with slides, subtitles, and optionally a talking-hea... |
| [customer-workspace](customer-workspace/) | Customer workspace initialization skill. Provides inbox (information accumulation), meeting minutes management, and auto-classification rules. Use for "setup customer workspace"... |
| [drawio-diagram-forge](drawio-diagram-forge/) | Generate draw.io editable diagrams (.drawio, .drawio.svg) from text, images, or Excel. Orchestrates 3-agent workflow (Analysis → Manifest → SVG generation) with quality gates |
| [duck-critic](duck-critic/) | Run a Duck Critic producer-critic loop: you (main) keep producing the plan/code/tests and gate your own work at checkpoints with a different-model critic, revising until it passes |
| [goal-loop](goal-loop/) | Run an explicit end-to-end goal loop with frozen Scope/criteria, worker delegation, external verification, evaluator review, and bounded retries |
| [humanize-writing](humanize-writing/) | Remove AI-generated tone and make writing sound more human in Japanese and English |
| [local-media-transcription](local-media-transcription/) | Transcribe local audio/video files to text, then optionally produce meeting minutes, action items, speaker separation, and PPT-ready summaries |
| [microsoft-graph-gateway](microsoft-graph-gateway/) | Route Microsoft Graph work in this workspace |
| [ocr-super-surya](ocr-super-surya/) | GPU-optimized OCR using Surya |
| [opportunity-factory](opportunity-factory/) | Run a reusable opportunity-to-artifact workflow: discover unmet needs, set up workspace factories, schedule recurring commander/worker/reporter prompts, batch-refine many items,... |
| [packet-capture-analysis](packet-capture-analysis/) | Use when analyzing pcap or pcapng files, triaging network captures, labeling IPs with evidence, generating PNG charts, or writing packet analysis reports. Keywords: pcap, pcapng... |
| [peer-feedback](peer-feedback/) | 同僚への半期ピアフィードバック下書きを自動生成する。workIQ で 1:1 チャット・グループチャット・メンション・共通会議・メール・SPO の履歴を収集し、6項目テンプレートに沿ってポジティブかつプロモーション志向で起票する。Use when: ピアフィードバック, フィードバック下書き, 同僚評価, 半期フィードバック, 360度フィードバック。 |
| [permission-max](permission-max/) | Reduce repeated permission prompts across Microsoft Scout, Copilot CLI, and host tool confirmations with user-approved settings and explicit before/after verification |
| [powerpoint-automation](powerpoint-automation/) | Create and edit professional PowerPoint presentations from web articles, blog posts, existing PPTX files, or templates |
| [powerpoint-planning](powerpoint-planning/) | Plan high-quality PowerPoint presentations before file creation or editing |
| [project-workspace](project-workspace/) | Create and manage topic-specific project workspace folders for validation, investigation, PoC, comparison, or workstream projects |
| [receipt-expense-workflow](receipt-expense-workflow/) | Company expense receipt workflow. OCR, rename, sort, summarize, and prepare receipt images/PDFs/videos for D365 expense mapping and attachment |
| [receipt-tax-ocr](receipt-tax-ocr/) | 個人事業・副業・確定申告専用。日本の勘定科目（印刷費 / 事業主借 等）で領収書画像を OCR してリネームし、月次メモを整える。会社経費 / D365 / 出張精算は receipt-expense-workflow を使う。Use when: 領収書, レシート, receipt, OCR, リネーム, 確定申告, 勘定科目, 経費, rename. |
| [repurpose-deck-from-reference](repurpose-deck-from-reference/) | Build a new-topic PPTX by reusing an existing reference deck's template (layouts / footers / fonts / palette) while replacing all content from primary sources |
| [retro-copilot](retro-copilot/) | Run a retro for ~/.copilot assets and turn incident learnings into updates for copilot-instructions, instructions, skills, agents, and hooks |
| [retro-private-skills](retro-private-skills/) | Reflect reusable learnings into a managed Agent Skills repository with scope gates, safe local commits, and conditional push |
| [retro-workspace](retro-workspace/) | Reflect reusable learnings into the current workspace / repository design and automation assets (.github/**, AGENTS.md, repo scripts/tasks) |
| [review-security-structure](review-security-structure/) | Review owned or authorized code for security using structure-first evidence: AST/structure maps, call graphs, complexity, Source/Sink flow, and defensive findings |
| [session-handoff](session-handoff/) | Create a compact handoff note so a new chat/session can first acknowledge the current state before work resumes |
| [skill-creator-plus](skill-creator-plus/) | Create or review a reusable skill (SKILL.md) that packages a workflow, and decide whether the request should be a skill instead of a prompt, instruction, agent, or hook |
| [skill-finder](skill-finder/) | Search, install, and manage Agent Skills locally and from GitHub, then help decide whether the task really needs a skill or another customization primitive |
| [sync-public-skills](sync-public-skills/) | Synchronize curated Agent Skills across approved repositories with policy checks and verification |
| [video-watch](video-watch/) | Prepare video URLs or local video files for GitHub Copilot analysis by extracting captions, sampled frames, contact sheets, and a prompt packet |
| [visualize-as-infographic](visualize-as-infographic/) | Create colorful infographic PNGs from a conversation, topic, file, skill, or workflow |
| [vscode-extension-guide](vscode-extension-guide/) | Guide for creating VS Code extensions and plugins from scratch through Marketplace publication |
| [web-accessibility](web-accessibility/) | Build and review accessible web products using WCAG 2.2 AA |
| [x-hashtag-research](x-hashtag-research/) | Collect and analyze public X posts from hashtags to discover primary sources, official docs, related GitHub repos, and reusable images |
| [x-twitter-browser-ops](x-twitter-browser-ops/) | Read-only X/Twitter browser data workflow |
<!-- public-skills-table:end -->

## Usage / 使い方

### 🚀 Recommended: Agent Skill Ninja (VS Code Extension)

Install the **Agent Skill Ninja** extension for easy skill management:

**Agent Skill Ninja** 拡張機能でスキル管理が簡単に：

**[📦 Agent Skill Ninja - VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=yamapan.agent-skill-ninja)**

- 🔍 Browse and search skills / スキルの検索・閲覧
- 📥 One-click install to your project / ワンクリックでプロジェクトにインストール
- 🔄 Auto-update installed skills / インストール済みスキルの自動更新
- 📋 View skill details and documentation / スキル詳細とドキュメントの表示

### Manual Installation / 手動インストール

Copy the desired skill folder to your project's `.github/skills/` or `.claude/skills/` directory.

使いたいスキルフォルダをプロジェクトの `.github/skills/` または `.claude/skills/` にコピーしてください。

```bash
# Example / 例
cp -r skill-finder /path/to/your/project/.github/skills/
```

## Structure / 構成

Each skill follows this structure / 各スキルは以下の構成です：

```
skill-name/
├── SKILL.md          # Skill definition / スキル定義
├── LICENSE.txt       # License / ライセンス
├── references/       # Reference files / 参照ファイル
└── scripts/          # Helper scripts / ヘルパースクリプト
```

## License / ライセンス

Each skill has its own license in `LICENSE.txt`. Please refer to the license file in each skill folder.

各スキルは個別のライセンスを持ちます。各スキルフォルダ内の `LICENSE.txt` を参照してください。

- **Self-created skills / 自作スキル**: CC BY-NC-SA 4.0
- **External skills / 外部由来**: Original license retained (MIT, Apache 2.0, etc.)

## Author / 作者

yamapan ([@aktsmm](https://github.com/aktsmm))
