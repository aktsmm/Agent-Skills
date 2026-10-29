---
name: fact-check
description: "ファイル、選択範囲、貼り付けた本文、URL 一覧に含まれる主張・数値・引用・参照先を 3 フェーズで検証する汎用ファクトチェック。"
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

# Fact Check

ファイル、選択範囲、貼り付けた本文、URL 一覧に含まれる事実主張を検証するための汎用 prompt です。

## 使う場面

- 技術記事、設計メモ、レポート、説明文、Issue、README、設定メモの事実確認
- URL、引用、数値、製品名、バージョン、対応状況、コマンド例の裏取り

## 使わない場面

- 文体だけを整えたいとき
- 主観的な感想や意見だけをレビューしたいとき

## 基本方針

- 記憶だけで正しいと断定しない
- まずワークスペース内の実ファイルと既知の一次情報で確認する
- 外部確認が必要な主張だけ、公式ドキュメントや公式ページを取りに行く
- 根拠が弱い主張は `Unverified`、根拠と矛盾する主張は `Contradicted` にする
- デフォルトは read-only とし、修正案は出しても自動編集はしない

## 3 フェーズ

### Phase 1: 主張の抽出

対象から以下を抽出する。

- 日付、時系列、GA / Preview / retirement などの状態
- 数値、統計、価格、件数、割合、ベンチマーク
- 引用文、要約、出典付きの断定
- 製品名、ブランド名、ロール名、ポータル名、機能名
- URL、画像参照、ファイル参照、パス、コマンド例

### Phase 2: 検証

主張ごとに最も近い根拠で検証する。

- ワークスペース内の根拠: ファイル内容、設定、画像参照、コード、コメント
- URL: ステータス確認と本文照合
- パス・ファイル名: `Test-Path`、`Get-ChildItem`
- コマンド例: `Get-Command`、`--version`、安全な read-only 実行
- Microsoft / Azure / Microsoft 365: 公式 Docs と公式コードサンプルを優先
- GitHub 関連: GitHub Docs、リポジトリ metadata、README、Releases を優先
- 一般 Web 情報: 公式ドキュメント、公式ブログ、公式リリースノートを優先

製品名、ブランド名、ポータル名、ロール名は、現行の正式名称かを確認する。rename や `classic` / `new` が見えたら overview / what-is / product page を追加で確認する。

### Phase 3: 判定と報告

各主張を以下に分類する。

- `Verified`: 十分な根拠で確認できた
- `Unverified`: 根拠不足、または確認不能
- `Contradicted`: 根拠と矛盾していた

重要度の高い問題から先に報告する。

## 優先順位

1. 公式ドキュメント、仕様書、一次情報
2. 公式ブログ、製品ページ、公式リリースノート
3. ワークスペース内の実ファイル、コード、画像参照
4. 信頼できる二次情報

## 実行ルール

- 重要な日付、バージョン、価格、可用性、制限は最新情報で確認する
- URL、画像参照、ファイル参照は実在確認まで行う
- 数値や比較表現は、可能なら一次情報か公式ベンチマークで確認する
- 根拠が 1 件しかない場合は、その弱さを明示する
- 挙動が画面・ハーネス・版・プランで変わる機能は、出典ごとに対象の表面を記録する。出典が食い違うときは「ない」と断定せず条件付きで併記し、利用者の実画面を一次証拠として確認を依頼する。まとめ記事や他の AI が引いた公式の引用文は、原典を取得して逐語検索し、見つからなければ撤回して GA・preview などの状態を断定しない。
- 外部情報が見つからない場合は、見つからないこと自体を結果に残す
- 不明な点を推測で埋めない

## 出力形式

```markdown
## Fact Check Result

### Findings
- [High|Medium|Low] 対象箇所: 問題点。根拠: ...

### Verified
- 主張: 根拠

### Unverified
- 主張: 不足している根拠

### Contradicted
- 主張: 正しい情報 / 根拠

### Sources
- URL またはファイル
```

`Findings` がない場合は、その理由を 1 行だけ添える。

`Verified` は確認できた重要項目だけに絞り、網羅列挙しない。

## 完了条件

- [ ] 主要な事実主張、数値、固有名詞、参照先を抽出した
- [ ] 各主要主張を `Verified`、`Unverified`、`Contradicted` に分類した
- [ ] 重要な指摘に根拠を添えた
- [ ] 最新情報が論点なら外部確認を行った
- [ ] 確認できなかった内容を断定していない