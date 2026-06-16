---
name: export-session-log
description: "Export the current session into structured Markdown for blog-draft seeds. Use when the user wants a session log saved as a blog-ready work note, article seed, or post draft with references."
argument-hint: "topic、記事テーマ、出力タイトル"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan
---

# Export Session Log

セッション内容を、**ブログ下書きの素地になる構造化 Markdown** としてエクスポートする。

この skill は **Blog 向け基本版** として使う。通常ログ向け分岐は扱わず、出力先はブログ用を前提にする。

## When to Use

- セッションをブログ記事ネタとして保存したいとき
- Zenn / Qiita / はてな向けの下書き素材を作りたいとき
- 実行コマンド、変更ファイル、学び、次アクションを 1 ファイルに整理したいとき
- 「あとで記事化しやすい形」で会話を残したいとき

## Output Path

- 既定出力先: `D:\11_My_Personal_Blog\drafts_topic\YYYYMMDD-NN--{topic}.md`
- `NN` は同日の連番 (`01`, `02`, `03`...)
- 同日同トピックのファイルが既にある場合は **新規採番より追記を優先** する

## Required Steps

1. エクスポート前に `Get-Date -Format "yyyy-MM-ddTHH:mm:ss"` を実行し、その結果を `exported_at` に使う
2. セッションからタイトル、要約、主要フェーズ、使ったツール、成果状態を抽出する
3. 試行錯誤が多い箇所は圧縮し、3 回以上の反復は `N attempts` のように要約する
4. 結論や説明に使った URL と関連ファイルを整理する
5. 指定フォーマットで Markdown を生成し、対象ファイルへ保存または追記する

## Output Format

````markdown
---
type: coding|research|debug|design|discussion
exported_at: { エクスポート時刻 }
tools_used: [tool1, tool2]
outcome_status: success|partial|failed
---

# {Session Title}

## Summary

{1-2文の概要}

## Timeline

### Phase N - {フェーズ名}

- {作業内容}
- Modified: [file](file#L10)

## Key Learnings

- {発見・学び}

## Commands & Code

```{lang}
{有用なコード}
```

## References

- Title - https://example.com/article
- Related File - C:\work\repo\path\to\file.md

## Next Steps

- [ ] {次のタスク}
````

## Reference Rules

- Web / Docs / ブログ / 外部ページを使ったセッションでは `## References` を省略しない
- `## References` には、**実際に結論や説明に使った出典** だけを残す
- ブログ向け出力では、URL だけでなく **ページタイトルも併記** する
- 外部情報ベースの要約、可否判断、仕様説明、比較は、対応する URL を必ず残す
- 使っていない検索候補や本文に反映していない URL は列挙しない
- 他ワークスペースや別 repo の資料を参照した場合は、関連ファイルのパスも残す
- URL とファイルパスの両方がある場合は両方残し、`## References` を索引として使う

## Timeline Rules

- Timeline 見出しは時刻ではなく `Phase N - {フェーズ名}` を使う
- 正確な時刻が取れない前提で、段階ベースの流れを優先する
- 変更ファイルや重要な判断は各フェーズに寄せて書く

## Writing Rules

- Summary は 1-2 文で簡潔に書く
- `type` は主目的に合わせて 1 つ選ぶ
- `outcome_status` は `success` / `partial` / `failed` のいずれかに正規化する
- `Commands & Code` には再利用価値のあるものだけを残す
- `Next Steps` は未完了項目や後続作業だけに絞る
- ブログ向けでも、まずは **事実ベースのログ** として整える
- 記事本文そのものを書くのではなく、**あとで記事化しやすい素材** に整える

## Done Criteria

- `exported_at` が実コマンド結果で埋まっている
- 出力先とファイル名がブログ用ルール通りに決まっている
- Summary / Timeline / Key Learnings / References / Next Steps がそろっている
- 外部情報を使った場合に `## References` が実データで埋まっている
- 冗長な試行錯誤が圧縮され、後で読み返せる密度になっている
