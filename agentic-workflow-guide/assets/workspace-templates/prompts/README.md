# `.github/prompts` ディレクトリ

ワークフローで再利用するプロンプト断片をまとめる場所。`*.prompt.md` 形式で保管し、`/prompt <name>` で呼び出して使う。

## 標準プロンプト

以下のプロンプトがテンプレートに含まれています。

| ファイル                                   | 説明                                         |
| ------------------------------------------ | -------------------------------------------- |
| `create-workflow.prompt.md`                | エージェント/ワークフロー作成（統合版）      |
| `review-agents-and-instructions.prompt.md` | エージェント定義・instructions のレビュー    |
| `plan-workflow.prompt.md`                  | 複数エージェントを使ったタスク実行計画       |
| `design-workflow.prompt.md`                | 新しいエージェントワークフロー設計           |
| `debug-error.prompt.md`                    | エラーメッセージ分析によるデバッグ支援       |
| `write-tests.prompt.md`                    | テストコード生成                             |
| `gc_Commit.prompt.md`                      | Git コミット（Push なし）                    |
| `gcp_Commit_Push.prompt.md`                | Git コミット＆プッシュ                       |
| `gpull.prompt.md`                          | Git プル                                     |
| `review-retrospective-learnings.prompt.md` | 学びを抽象化して設計資産へ反映（ふりかえり） |
| `review-session-export-md.prompt.md`       | セッション内容を Markdown 形式でエクスポート |
| `wrap-up-work.prompt.md`                   | 作業の締め・要約                             |
| `sample.prompt.md`                         | カスタムプロンプト作成用テンプレート         |

## カスタマイズ

- 短い指示なら数行で OK。コード例を含めるときはフェンスコードを使う。
- `sample.prompt.md` をコピーして書き換えてね。
- runSubagent を呼び出すテンプレは「直列実行のみ」「サマリ粒度」など制約をプロンプトに書き込んでおくと安定する。
