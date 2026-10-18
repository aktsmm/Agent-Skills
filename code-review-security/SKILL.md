---
name: code-review-security
description: "差分、PR、選択範囲、指定ファイルをセキュリティ観点で read-only レビューし、rubber duck / critic review で確認してから高信頼の脆弱性を報告する"
disable-model-invocation: true
argument-hint: "レビュー対象、比較ブランチ、重点 threat model、review-only / fix / thorough"
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

# code review security

指定された差分、PR、選択範囲、ファイル、または現在の Git 変更をセキュリティ観点でレビューする。

## When to Use

- 使う: `/security-review` 的に、変更差分の exploitability を確認したいとき
- 使う: injection、認証認可、secret leak、supply chain、LLM prompt injection を重点的に見たいとき
- 使う: 「セキュリティレビュー」「脆弱性見て」「攻撃可能性を見て」と依頼されたとき
- 使う: 「レビューして修正」「fix」「直して」など、レビュー後の修正まで明示されたとき
- 使わない: 一般的なコード品質、style、設計好み、性能だけを見たいとき。その場合は `/code-review-multi-angle` を使う

## Mode

- 既定は `review-only`: コードを編集せず、security finding と修正方針だけを出す
- `fix` / `修正して` / `直して` が明示された場合だけ `review-and-fix`: security review、critic review、最小修正、focused validation まで行う
- destructive operation、外部反映、履歴改変、push、広範囲 refactor、secret rotation は fix mode でも実行前に確認する

## Scope Detection

優先順でレビュー対象を決める。

1. ユーザーが指定した PR URL、比較ブランチ、ファイル、選択範囲、貼り付け diff
2. staged changes: `git --no-pager diff --staged`
3. unstaged changes: `git --no-pager diff`
4. working tree が clean の場合: `git --no-pager diff main...HEAD`

`main` 以外の base branch が自然なリポジトリでは、branch 名や upstream を確認してから使う。

## Security Review Rules

- 変更行または変更により到達可能になったコードだけを主対象にする
- 既存脆弱性でも、diff に vulnerable code が現れている場合は報告してよい
- exploit path、trust boundary、attacker-controlled input、impact を説明できないものは finding にしない
- test code は production vulnerability を示す場合だけ報告する
- style、maintainability、generic best practice、単なる DoS、rate limiting、CPU / memory exhaustion は原則報告しない

## Vulnerability Categories

最低限、次の 11 カテゴリを確認する。

- `StringInjection`: SQL / shell / HTML / JSON / YAML / code 生成で unsafe string composition がないか
- `BadCrypto`: 弱い暗号、短い鍵、非暗号乱数、弱い password hashing がないか
- `BrokenAccessControl`: path traversal、CSRF、open redirect、権限境界破りがないか
- `HardcodedCredentials`: source / config に credential、key、token がないか
- `SensitiveDataLeak`: secret、PII、stack trace、内部 URL を log / response / file に出していないか
- `SecurityMisconfiguration`: CSP / HTTPS / HttpOnly / CORS / debug / XXE など安全設定を壊していないか
- `AuthenticationFailure`: certificate validation、認証方式、origin check、sensitive operation の HTTPS が抜けていないか
- `DataIntegrityFailure`: integrity check なし deserialization、prototype pollution、insecure content execution がないか
- `SSRF`: attacker-controlled URL / host / protocol を fetch していないか
- `SupplyChainAttack`: mutable dependency、remote code execution、未検証 download、registry / action / image 参照の乗っ取りがないか
- `XPIA`: untrusted data が LLM prompt、tool routing、stage transition、policy、debug bypass に影響していないか

## Severity and Confidence

- Critical: RCE、full system compromise、重大な data breach
- High: privilege escalation、authentication bypass、sensitive data access
- Medium: 条件付きだが有意な exploit、limited data access、information disclosure
- Low: defense-in-depth、lower-impact security control bypass

報告閾値。

- Critical: confidence 6/10 以上
- High: confidence 7/10 以上
- Medium: confidence 8/10 以上
- Low: confidence 9/10 以上

閾値未満は `Assumptions / Not Reviewed` に回し、finding として断定しない。

## Critic Review

security finding を出す前、または fix mode で修正する前に、利用可能な rubber duck / critic 経路で確認する。

- 利用可能なら native Rubber Duck、`duck-critic` skill、read-only subagent、別モデル critic のいずれかを使う
- critic には exploit path、confidence、false positive の可能性、修正案の副作用を重点確認させる
- critic は read-only とし、修正や状態変更を任せない
- critic の指摘は重複排除し、採用したものだけ findings または fixes に反映する
- critic 経路が使えない場合は、自分で second-pass security review を行い、使えなかった理由を `Verification` に書く

## Verification

可能な範囲で、finding を出す前に read-only または低リスクの確認を行う。

- data flow、call site、sanitizer、auth guard、policy、config、dependency source を確認する
- 既存の secure coding pattern と比較する
- 必要なら focused test、typecheck、lint、secret scan、dependency metadata 確認を実行する
- 実行できない場合は、理由と代替確認を明記する
- review-only ではコードを編集しない。ファイル作成・修正・削除も行わない
- fix mode では、critic review 後に最小修正を行い、focused validation を実行する

## Output Format

重大度順に findings を先に出す。

```markdown
## Security Findings

### 1. {短いタイトル}
- Severity: Critical | High | Medium | Low
- Confidence: N/10
- Category: {カテゴリ名}
- File: {path}:{line}
- Problem: {脆弱性と exploit path}
- Evidence: {差分、data flow、guard 確認、仕様から確認した根拠}
- Suggested Fix: {実装方針。review-only ではコードは変更しない}

## No Security Vulnerabilities

{finding がない場合だけ、高信頼の脆弱性が見つからなかった理由を 1 行で書く}

## Assumptions / Not Reviewed

- {未確認範囲、閾値未満の懸念、実行できなかった検証。なければ None}

## Fixes Applied

- {fix mode の場合だけ、変更したファイルと理由。review-only では None}

## Verification

- {実行した確認、critic review 経路、または未実行理由}
```

褒め、長い作業ログ、見たファイルの網羅列挙は出さない。

## Completion Criteria

- 対象差分または指定範囲を特定した
- 11 カテゴリを確認した
- finding は exploit path と confidence threshold を満たすものだけに絞った
- finding または fix mode では critic review を行った、または代替 second-pass を明記した
- 可能な範囲で guard / sanitizer / data flow / focused validation を確認した
- review-only ではコードを変更していない
- fix mode では最小修正後に focused validation を行った