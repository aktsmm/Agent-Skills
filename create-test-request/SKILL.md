---
name: create-test-request
description: "Use when: 会話・設計資料・回答文書から検証タスクを抽出し、別workspaceへ渡すテスト依頼文を作成する。受け手は最初に理解内容と実施項目を返し、承認後に検証する"
disable-model-invocation: true
argument-hint: "検証対象、元資料、対象環境、完了条件、変更可能範囲（省略時は会話から推定）"
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

# 検証タスクとテスト依頼文を作成

現在の会話、選択範囲、開いている資料、workspace内の成果物から検証タスクを抽出し、別の検証workspaceのエージェントへ貼り付ける自己完結したテスト依頼文を作る。設定の読み取り確認も対象に含む。このskillを実行するセッションでは検証・構築・設定変更を行わず、依頼文だけを生成する。

## 実行境界と応答フェーズ

- このskillを実行するセッションでは、読み取り・検索・状態確認以外の操作を行わない。handoff生成前も検証対象を変更しない。
- **第1応答**: 会話と成果物から検証目的を1文で推定し、`ask_user`で必ず1問だけ確認する。
	- header: `検証目的の確認`
	- question: `検証の目的は「{推定した目的}」で合っていますか？`
	- 推奨option: `はい、この目的でhandoffを作成`
	- freeformで目的の修正を受け付ける。
- 第1応答ではhandoff本文を生成せず、ユーザー回答を待つ。回答・訂正を検証目的の正本とする。
- ユーザーが目的の不足・狭さ・誤解を指摘した場合は、訂正文だけへ置換しない。会話と成果物を再確認し、指摘された観点を検証対象、構築・変更手順、証跡、rollback、cleanup、完了条件へ再統合した目的文を作る。
- 訂正後も同じ形式の1問だけを再提示し、ユーザーが明示的に承認するまで第1応答を繰り返す。承認前に第2応答へ進まない。目的以外（形式・内容・参照資料の不備）の指摘は再確認せず、反映したhandoff全文を再出力する。
- **第2応答**: 確認済みの目的を反映したhandoff全文を、単一の`markdown` fenced blockだけで出力する。ブロック外に前置きや補足を書かない。

## 入力の確定

- 優先順位は `最新のユーザー指示 > 現在の成果物と検証結果 > 会話中の計画 > 古い仮説` とする。
- まず対象資料、検証対象、現時点の設計判断、未確認事項、対象環境、変更可能範囲を特定する。
- workspace内に元資料があれば、会話の要約より実ファイルを優先して読む。
- 未取得のsubscription、resource、tenant、region、SKU、権限、接続情報は推測せず`<要確認>`とする。secret値はhandoffへ書かない。
- 検証目的以外の情報が不足していても、第1応答では追加質問を増やさない。不足情報は生成するhandoffの`Environment`または`First Response Contract`に`<要確認>`として含め、受け手側で確認させる。

## 生成するhandoffの開始ゲート

handoffを受け取ったエージェントへ、最初の応答ではtoolを実行せず、次だけを日本語で返すよう明記する。

1. `理解しました。今回の目的は...です。`
2. `実施することは次のとおりです。`として、検証項目を順序付きで要約する。
3. 確定済みの前提と不足情報を分ける。
4. 構築・設定変更・deploy・権限変更・削除が含まれる場合は、実行前に承認が必要な操作を列挙する。
5. `この理解と進め方でよければ、進めてくださいとお知らせください。`で止める。

ユーザーが`進めて`、`検証して`、または同等の明示承認を返すまで、読み取り確認を含むtool実行を開始させない。最新のユーザー指示が「受領後すぐ検証開始」と明示している場合だけ、この待機を省略できる。

## handoffに含める内容

### Goal

- 何を実環境で証明または反証するか。
- どの設計判断・仮説・構成候補を検証するか。
- 誰が判断に使う成果物か。

### Source of Truth

- 受け手が元資料を読める保証はない。検証に必要な主張・数値・手順・仕様の記述はhandoff本文へ全文で埋め込み、「資料を提供してください」と言わせない。fileの相対 path は、受け手のworkspaceに同じfileがあるとユーザーが確認した場合だけ使う。
- 公式仕様URLと、その仕様から導いた設計判断を分ける。
- 既に確認済みの事実、未確認、仮説を分類する。

### Environment and Safety Boundary

- 対象tenant、subscription、resource group、resource、region、SKU。未取得値は`<要確認>`。
- read-onlyで確認できる項目と、変更を伴う項目を分ける。
- 明示承認なしで禁止する操作: resource作成・変更・削除、deploy、権限付与、network/DNS変更、public access変更、secret取得・表示、共有process操作、push。
- secretは環境変数・既存認証session・Key Vault等から取得し、保存・表示しない。

### Required Validation

検証項目を依存順に並べ、各項目へ次を付ける。

- 対象と確認方法
- 合格条件
- 失敗時に区別する仮説
- 保存する証跡
- 変更が必要な場合のrollback

最低限、該当する範囲で次を含める。

1. control planeとresource状態、SKU、region、権限。
2. network path、routing/peering、Private Endpoint、Private DNS、TLS。
3. 認証主体、tokenのissuer/audience/claim、managed identity、RBAC。
4. public accessを無効にした状態でのprivate経路成功。
5. producer単体、接続部品単体、end-to-endの順での切り分け。
6. timeout、response size、retry、重複処理、ログ・メトリクス。
7. negative testと、変更前へ戻せるrollback確認。

### Execution Phases

`Discovery → Read-only baseline → Change plan and approval → Minimal build/change → Component tests → End-to-end test → Rollback test → Cleanup → Report`の順にする。変更不要の検証では不要なphaseを省く。

### Completion Criteria

- 合格条件を結果と証跡で判定できる。
- 設定値や自己申告だけで完了にしない。
- 未確認項目は未確認の理由と次の確認条件を残す。
- 一時resource・一時script・一時権限のcleanup状態を明記する。
- 最終報告に`Verified / Failed / Unverified`、実行したtool/CLI、証跡path、変更内容、rollback結果、残リスクを含める。

## 出力形式

第1応答で検証目的の確認が完了した後、次の順序で貼り付け可能なhandoff全文だけを単一の`markdown` fenced blockで出力する。

1. Title
2. First Response Contract
3. Goal
4. Background and Current Decision
5. Source of Truth
6. Environment
7. Required Validation
8. Execution Phases
9. Evidence
10. Completion Criteria
11. Must NOT
12. Final Report Format

handoff本文に内部推論、不要な会話履歴、顧客の個人情報、secret、ローカル絶対パスを含めない。元資料は本文へ埋め込み、file参照に依存させない。