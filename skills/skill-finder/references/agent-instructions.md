# Agent Instructions

> ⚠️ **CRITICAL**: AI agents MUST follow these instructions. Prefer action proposals over verbose explanations.

## Core Principle

**Use "Do it? Yes/No?" style proposals.**

- ❌ Bad: "If you want to add new skills, you can run the following command..."
- ✅ Good: "Update the index?"

## Recommendation Workflow

When user asks for recommendations (e.g., "おすすめは？", "何かいいスキルある？"):

| Persona          | Categories                | Example Skills                                |
| ---------------- | ------------------------- | --------------------------------------------- |
| オフィスワーカー | document, office          | docx, xlsx, pptx, pdf                         |
| 開発者           | development, testing, git | test-driven-development, systematic-debugging |
| Azure エンジニア | azure, development        | azure-env-builder, mcp-builder                |
| デザイナー       | design, creative, web     | brand-guidelines, canvas-design               |
| 初心者           | meta, planning            | skill-creator, brainstorming                  |

**Response Format:**

1. Ask about user's role/context if unclear
2. Show top 3-5 skills with descriptions
3. Include source breakdown table
4. Propose next actions

## Skill Search Workflow

1. **Search ALL sources in local index**
   - Read `references/skill-index.json`
   - **ALWAYS search ALL sources**
   - Check `lastUpdated` field

2. **🌟 Recommend from results (when 3+ hits)**

   ```
   ### 🌟 おすすめ: {skill-name}
   {理由: 公式スキル、機能が豊富、用途にマッチ など}
   ```

   **Selection criteria:**
   1. Official source preferred
   2. Feature richness
   3. Relevance to user's purpose
   4. Recently updated

3. **If not found → Propose web search**

   ```
   Not found locally. Search the web?
   → GitHub: https://github.com/search?q=path%3A**%2FSKILL.md+{query}&type=code
   ```

4. **🚨 MANDATORY: Propose next actions**

   | Situation            | Proposal                     |
   | -------------------- | ---------------------------- |
   | Skill found          | "Install it?"                |
   | Good repo discovered | "Add to sources?"            |
   | lastUpdated > 7 days | "⚠️ Index outdated. Update?" |

## 🚨 Mandatory Proposal Block

**ALWAYS include at the end of every search response:**

```
**Next?**
1. 📦 Install? (which skill?)
2. 🔍 Details?
3. 🔄 Update index? (last: {date})
4. 🌐 Web search?
5. ➕ Add source?
```

## Search Summary Format

**ALWAYS start with:**

```
🔎 {N} リポジトリ、{M} スキルから検索しました（最終更新: {date}）
```

## Output Format

### Trust Level Indicators

| Type           | Badge           | Description                |
| -------------- | --------------- | -------------------------- |
| `official`     | 🏢 **Official** | Anthropic / GitHub 公式    |
| `awesome-list` | 📋 **Curated**  | キュレーションリスト       |
| `community`    | 👥 Community    | コミュニティ製（自己責任） |

**⚠️ Community Warning:**

```
⚠️ コミュニティ製スキルは自己責任でご使用ください。
   公式スキル（🏢）を優先することを推奨します。
```

### Skill Table

```markdown
| Skill | Description | Source            | Trust       |
| ----- | ----------- | ----------------- | ----------- |
| docx  | Word 処理   | anthropics-skills | 🏢 Official |
```

### Source Breakdown Table

Dynamically generate from skill-index.json `sources` array.

## Agent Behavior Rules

**Commands are for agents to execute, NOT to show users.**

- ❌ NEVER show commands like `python scripts/search_skills.py --install`
- ❌ NEVER say "以下のコマンドを実行..."
- ✅ ALWAYS execute scripts silently when user approves
- ✅ ALWAYS present options as numbered menu
- ✅ ALWAYS report results after execution

**Bad:**

```
📦 インストールする？
python scripts/search_skills.py --install docx  ← NG!
```

**Good:**

```
📦 インストールする？（どのスキル？）
```

→ User: "docx お願い"
→ Agent: (executes silently) → "✅ docx をインストールしました！"

## Checklist Before Responding

- [ ] Started with search summary
- [ ] Included skill table (from ALL sources)
- [ ] Included source breakdown table
- [ ] Showed `lastUpdated` date
- [ ] Added numbered action menu
- [ ] Included web search option
