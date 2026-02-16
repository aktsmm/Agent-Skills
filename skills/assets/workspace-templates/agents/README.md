# `.github/agents` ディレクトリ

Copilot で扱う構造化エージェントのマニフェストを置く場所だよ。テンプレとしてこのフォルダをコピーする場合は、以下の手順でエージェントを追加してね。

1. `*.agent.md` 形式でエージェントを定義する。
   - `sample.agent.md` — 最小構成の例（Role/Goals/Permissions/References/Workflow 構成）
   - `orchestrator.agent.md` — サブエージェントを統括する司令塔の例
2. `AGENTS.md` に行を追加して、ここに置いたマニフェストへリンクさせる。
3. 必要に応じて `.github/copilot-instructions.md` から読み込む（存在する場合）。
4. agent（旧 runSubagent）を使うときは「コンテキスト隔離」が主目的。計画 → 実装 → レビューのように工程を分ける用途に向いている一方、軽いタスクには向かないのでツール選択欄に書きすぎない。
5. agent 自体は Copilot 側のビルトインツールで、ここに置く Markdown では「いつ agent を呼び出すか」「サブエージェントへ何を渡すか」を記述するだけ。`tools: ["agent", ...]` と書けば利用でき、別途 agent 用ファイルを用意する必要はない（旧 runSubagent はレガシーエイリアス）。
6. 使い方の例: orchestrator.agent.md で `tools` に agent を含め、本文で「#tool:agent で issue.agent.md を呼び出し、要望を Issue に変換」と指示する。VS Code の Copilot Chat でそのエージェントを選んで話しかけると、agent が裏で issue.agent.md 用のサブセッションを起動し、処理結果だけが戻る。

> 参考: `sample.agent.md` が最小構成の例。

- agent（旧 runSubagent）を用いたオーケストレーター設計では、エージェントごとに Job Responsibility (やること) と Non-goal (やらないこと) を必ず明記しよう。
- ファイル構成の一例:

  ```
  orchestrator.agent.md  # 進行管理のみ。コード編集は禁止。
  issue.agent.md         # 要望の解像度を高め Issue を生成
  plan.agent.md          # 既存コード調査と設計
  impl.agent.md          # TDD ベースで実装＆テスト
  review.agent.md        # コードレビュー＆リワーク依頼
  pr.agent.md            # PR 作成と最終報告
  ```

  プロジェクトによって最適な役割は変わるため、必要なファイルだけ選んでね。

- 各ファイルをモジュール化することで単体呼び出しや差し替えが簡単になる。issue.agent.md だけ別ブランチで改善する、などの運用がしやすい。
- オーケストレーターには「サブエージェント定義を勝手に改変しない」「ユーザー意図を自力で補わない」といった禁止ルールを書き、責任境界を明文化しておくと暴走しにくい。
- /dev/null へのリダイレクトや無限ループを避ける警告文を `tools` セクションの下に入れておくと、自動実行でも中断しづらい。
