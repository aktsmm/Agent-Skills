---
name: code-review-multi-angle
description: "差分、PR、選択範囲、指定ファイルを多角的にレビューし、既定は read-only、明示指示があれば critic review 後に修正と検証まで行う。日常コードレビューの入口で、`fix` 指定で Fix now / Guard now / Block に分けて最小修正・同根 Sweep・検証まで閉じる"
disable-model-invocation: true
argument-hint: "レビュー対象、比較ブランチ、重点観点、review-only / fix / thorough"
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

# code review multi angle

指定された差分、PR、選択範囲、ファイル、または現在の Git 変更を read-only でレビューする。

## When to Use

- 使う: コード変更をマージ前・コミット前・PR 前にレビューしたいとき
- 使う: `/review` 的な不具合レビューと `/security-review` 的なセキュリティレビューを一度に見たいとき
- 使う: 「多角的にレビュー」「厳しめにレビュー」「重大な見落としがないか見て」と依頼されたとき
- 使う: 「レビューして修正」「fix」「直して」など、レビュー後の修正まで明示されたとき
- 使わない: 文体、ドキュメント、記事、workflow customization の構造レビュー。その場合は専用 prompt / agent / skill を使う
- 使わない: リリース前の本格 QA、プロダクト全体の反復改善、release / publish / version sync。それらは `refine-product-100` を使う

## Mode

- 既定は `review-only`: コードを編集せず、finding と修正方針だけを出す
- `fix` / `修正して` / `直して` が明示された場合だけ `review-and-fix`: レビュー、critic review、修正、focused validation まで行う
- destructive operation、外部反映、履歴改変、push、広範囲 refactor は fix mode でも実行前に確認する

### Fix mode の分類と範囲

fix mode では、見つけた問題を 1 回のレビューで次に分類する。

- `Fix now`: 依頼範囲内・非破壊・ローカル検証可能・正しさを説明できるものだけ。最小差分で修正する
- `Guard now`: 本修正は難しいが、テスト、静的チェック、docs、確認手順のいずれか 1 つ以上でリスクを下げられるもの。その成果物を作る
- `Block`: 破壊的操作、外部公開、仕様判断、secret、本番データ、権限不足が絡むもの。実行せず報告する
- 安全に編集できない `Fix now` はレビューだけで残さず、`Guard now` または `Block` にする
- Sweep は、修正した観点と同じ原因の問題だけに横展開する（文字列・関数名・型・エラー文・設定キーで検索）。概念的に近いだけの改善や別軸の品質改善は Next Steps に回す
- 検証に失敗したら原因を読み、同一原因につき最大 2 サイクルまで修正と再検証を行う。それ以上は `Block` として残す
- 学びは `Learnings Candidate` として候補を提示するだけにする。instruction や review-learnings ファイルへの反映は、ユーザーが明示した場合だけ行う

## Scope Detection

優先順でレビュー対象を決める。

1. ユーザーが指定した PR URL、比較ブランチ、ファイル、選択範囲、貼り付け diff
2. staged changes: `git --no-pager diff --staged`
3. unstaged changes: `git --no-pager diff`
4. working tree が clean の場合: `git --no-pager diff main...HEAD`

`main` 以外の base branch が自然なリポジトリでは、branch 名や upstream を確認してから使う。

## Review Lanes

同じ対象を少なくとも 3 つの独立した観点で見る。

### 1. Correctness and Regression

- 仕様・既存挙動・境界条件を壊していないか
- null / empty / missing / duplicate / out-of-order / concurrent input で破綻しないか
- public API、schema、CLI contract、output format の互換性を壊していないか
- エラー処理不足で crash、data loss、partial update が起きないか

### 2. Security and Trust Boundary

- injection、path traversal、SSRF、unsafe deserialization、prototype pollution がないか
- 認証・認可・権限境界・tenant / repo / workspace boundary を越えていないか
- secret、token、PII、内部 URL、stack trace をログや出力へ漏らしていないか
- untrusted input が LLM prompt、tool routing、shell command、URL、file path に混ざっていないか

### 3. Reliability, Operations, and Maintainability

- retry、timeout、idempotency、cleanup、rollback、resume が必要な箇所で抜けていないか
- performance impact が測定可能に悪化していないか
- build artifact、generated file、大量 diff による誤検出を避けているか
- 既存パターン・近傍実装・テスト方針から外れていないか

## Noise Filter

報告してよいのは、読者が実際に直す価値のある finding だけ。Critical / High / Medium / Low に分類し、Low も根拠と修正価値があるなら出す。

報告しないもの。

- style、format、命名、好みの設計
- grammar、spelling、コメント文の軽微な改善
- 「できれば」「一般的には」レベルの best practice
- 修正しても要求成果に影響しない refactor

迷った finding は報告しない。代わりに `Assumptions / Not Reviewed` に短く残す。

## Critic Review

非自明な変更、security finding、複数ファイル変更、または fix mode では、利用可能な rubber duck / critic 経路でレビュー結果をもう一度確認する。

- 利用可能なら native Rubber Duck、`duck-critic` skill、read-only subagent、別モデル critic のいずれかを使う
- critic は read-only とし、修正や状態変更を任せない
- critic の指摘は重複排除し、実際に採用したものだけ findings または fixes に反映する
- critic 経路が使えない場合は、自分で second-pass review を行い、使えなかった理由を `Verification` に書く

## Verification

可能な範囲で、finding を出す前に read-only または低リスクの確認を行う。

- 周辺コード、既存テスト、call site、schema、README、設定を確認する
- 必要なら compile / typecheck / lint / focused test を実行する
- 実行できない場合は、理由と代替確認を明記する
- review-only ではコードを編集しない。ファイル作成・修正・削除も行わない
- fix mode では、critic review 後に最小修正を行い、focused validation を実行する

## Output Format

重大度順に findings を先に出す。

```markdown
## Review Findings

### 1. {短いタイトル}
- Severity: Critical | High | Medium | Low
- Lane: Correctness | Security | Reliability
- File: {path}:{line}
- Problem: {実際に起きる問題}
- Evidence: {差分、周辺コード、テスト、仕様から確認した根拠}
- Suggested Fix: {実装方針。コードは変更しない}

## No Significant Issues

{finding がない場合だけ、重大な問題が見つからなかった理由を 1 行で書く}

## Assumptions / Not Reviewed

- {未確認範囲、実行できなかった検証、前提。なければ None}

## Fixes Applied

- {fix mode の場合だけ、変更したファイルと理由。分類（Fix now / Guard now / Block）と Sweep の結果を含める。review-only では None}

## Learnings Candidate

- {永続化したい学び候補。なければ None}

## Verification

- {実行した確認、または未実行理由}
```

褒め、長い作業ログ、見たファイルの網羅列挙は出さない。

## Completion Criteria

- 対象差分または指定範囲を特定した
- 3 つ以上の観点で確認した
- finding は actionable なものだけに絞り、Critical / High / Medium / Low に分類した
- 非自明なレビューまたは fix mode では critic review を行った、または代替 second-pass を明記した
- 可能な範囲で根拠確認または focused validation を行った
- review-only ではコードを変更していない
- fix mode では最小修正後に focused validation を行った