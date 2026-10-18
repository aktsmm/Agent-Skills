---
name: export-knowledge
description: "Reusable learnings: セッション中の再利用知見を構造化し、ドメイン別（microsoft / copilot など）に振り分けて出力。Use when: knowledge, lessons learned, 知見化。作業ログは export-session-log、対話再現は export-copilot-session-dialogue を使う"
disable-model-invocation: true
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---
<!-- syncToGlobal: true -->
<!-- author: aktsmm -->
<!-- repository: https://github.com/aktsmm/Agent-Customization -->
<!-- license: CC BY-NC-SA 4.0 -->
<!-- copyright: Copyright (c) 2025 aktsmm -->

# export knowledge

このセッションで得られた知見を構造化してエクスポートします。
ドメインを自動判定し、適切な出力先に振り分けます。

## Core Contract

- セッション知見を `microsoft` または `copilot` ドメインへ振り分ける
- primary category を 1 つ選び、残りは tags に回す
- Markdown と index の両方を更新する
- 判定に迷う場合だけユーザー確認する

## Domain Routing

出力先の優先順は、ユーザー指定 > 環境変数 > 明示された workspace/local > 確認。

| ドメイン | キーワード |
| --- | --- |
| **microsoft** | Azure, M365, Entra ID, Intune, Defender, Power Platform, Windows Server, SQL Server, Dynamics 365, Copilot Studio |
| **copilot** | GitHub Copilot, MCP, Agent, Prompt, VS Code 拡張, VS Code, Workflow, Skills, Context Engineering |

| ドメイン | 環境変数 |
| --- | --- |
| **microsoft** | `$env:EXPORT_KNOWLEDGE_MICROSOFT_DIR\{category}\` |
| **copilot** | `$env:EXPORT_KNOWLEDGE_COPILOT_DIR\{category}\` |

- 判定に迷う場合はユーザーに確認
- 1セッションで両ドメインの知見がある場合は、それぞれ個別にエクスポート
- 対応する環境変数が未設定または path が存在しない場合は、workspace/local が明示されたときだけ `{workspace}/_output-knowledge/{domain}/{category}/` を使い、それ以外は作成前に確認する

### 出力先の上書き

| 条件                        | 出力先                                      |
| --------------------------- | ------------------------------------------- |
| デフォルト                  | 上記ドメイン別の環境変数。未設定または path 不在なら、workspace/local の明示がない限り確認 |
| 「workspace」「ローカル」等 | `{workspace}/_output-knowledge/{domain}/{category}/` |
| パス指定あり                | 指定パス                                    |

## Categories

### microsoft ドメイン

azure-compute / azure-networking / azure-storage / azure-security / azure-identity / azure-monitoring / azure-migration / azure-arc / m365 / intune / defender / entra-id / power-platform / licensing / architecture / troubleshooting / lessons-learned

### copilot ドメイン

prompts / agents / workflows / subagent / context / mcp / skills / debugging / automation / evaluation / vscode-settings / lessons-learned / templates

## Workflow

1. セッションから知見を抽出（技術的発見、エラー解決、設計判断、参照 URL）
2. ドメインを判定（microsoft or copilot）
3. カテゴリを1つ選定、他はタグに
4. 以下の形式でMarkdownファイルを作成
5. ファイル名: `{YYYYMMDD}-{topic-slug}.md`
6. インデックス更新（ドメインに応じた \_index フォルダ）

## Output Requirements

必須要素:

- frontmatter: `title`, `datetime`, `domain`, `primaryCategory`, `tags`
- `references`
- `## 知見`
- `## 具体例`
- microsoft ドメインなら `products` と `## 顧客への影響`

テンプレート:

```markdown
---
title: "知見のタイトル"
datetime: { エクスポート時刻 }
domain: microsoft | copilot
primaryCategory: { カテゴリ }
tags: [tag1, tag2]
products: [製品名] # microsoft ドメインのみ
references:
  - url: https://...
    title: ドキュメントタイトル
---

## 知見

（本文）

## 具体例

（コード例・構成例があれば）

## 顧客への影響

（microsoft ドメインで該当する場合：影響範囲・対応推奨）
```

## Index Targets

各ドメインで解決した `<resolved-root>\_index\knowledge-index.json` を使う。

`resolved-root` は Markdown の出力 root と同じ場所を使う。root が決まるまでファイル作成と index 更新を開始しない。

## ルール

- エクスポート前に `Get-Date -Format "yyyy-MM-ddTHH:mm:ss"` を実行し、その結果を `datetime` に使用する
- microsoft ドメイン: 公式ドキュメント URL（learn.microsoft.com）を必ず含める
- microsoft ドメイン: Azure Updates の情報がある場合は updates URL も含める
- microsoft ドメイン: 顧客対応で得た知見は個人情報・社名をマスクしてから記録する
