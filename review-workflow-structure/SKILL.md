---
name: review-workflow-structure
description: "ワークフロー設計資産としての agent / instruction / skill / AGENTS を横断レビューし、SSOT・整合性・構造の問題を検出する"
disable-model-invocation: true
argument-hint: "対象パス、review 観点、all / 徹底的 などの範囲指定"
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

# review workflow structure

エージェント定義（`.agent.md`）と customization 指示（`.instructions.md` / skill / entry files）を、構造・SSOT・配置の観点で横断レビューする。

## Use / Do Not Use

- 使う: agent / instruction / prompt / entry file を横断して、SSOT、配置、発火条件、肥大化、依存破綻を確認したいとき。
- 使う: `fix` / `ALLFIX` 指定があり、低リスクな customization 変更まで自律実行したいとき。
- 使わない: scripts / hooks / validators / CLI の実装整合性が主題のとき、または単一ファイルの文章圧縮だけが目的のとき。

## Scope Gate

- 既定: workspace の `AGENTS.md`、`.github/copilot-instructions.md`、`.github/agents/*.agent.md`、`.github/instructions/**/*.instructions.md` を対象にする。対象パスに実際に適用される祖先・近接の `AGENTS.md` / `AGENTS.override.md` の指示 chain を解決し、明示スコープ外の資産へ監査を広げない。
- `all` / `徹底的`（大文字小文字を区別しない）: 上記に、現在セッションで自動ロードまたは明示参照された workspace 側 instruction injection files を加える。
- Global: 引数に `global`、`~/.copilot` がある、または対象ファイルが明示添付された場合だけ含める。
- Skills: `skill` / `SKILL.md` / skill folder が明示された場合だけ `SKILL.md` の frontmatter と自己完結性を対象にする。
- `AGENTS.md` または `.github/copilot-instructions.md` を含む場合は、必ず両方を読み、常時入口の役割差分と DRY/SSOT を確認する。

対象が存在しない場合は、ワークスペースの目的・構造・主要ツールから最小限の設計資産を提案する。生成はユーザーが `fix` / `create` を指定した場合だけ行う。

## Review Basis

以下の観点を単体で使う。対象 workspace に設計レビュー専用 rubric instruction がある場合は、通常の適用指示と区別して補助基準として読む。host 変換や圧縮では [review-safeguards.md](references/review-safeguards.md) も適用する。

## Required Review Dimensions

次を確認する。

- Placement / SSOT: always-loaded、path-scoped、task prompt、skill、agent、docs の置き場が正しいか。
- Always-On Boundary: `copilot-instructions.md` と `AGENTS.md` が短い入口に留まり、catalog / workflow map / reference list を昇格させていないか。
- Primitive / SRP: prompt / instruction / skill / agent / hook の選択が最小で、1 agent が 1 責務か。
- Frontmatter / Placement: `.instructions.md` / `.agent.md` / `SKILL.md` の supported fields（skill は `disable-model-invocation: true` の手動専用に `argument-hint` があるか、実験的な `context: fork` に依存していないかも確認）、`applyTo` 過大（絞る提案は対象 instruction の全文を読み、除外されるファイルの編集に効く規則が無いことを確認してから出す）、`.github/agents/` 直下配置を確認する。agent は本文の tool reference が frontmatter `tools` と整合しているかも確認する。両 harness（VS Code Local / Agent Host）で使う資産は、`tools:` が個別 ID（`read/readFile` 等）だけで harness により無視されないか（tool set 別名 `read` / `edit` / `search` / `execute` / `agent` / `todo` が portable）、本文が `runSubagent` / `run_in_terminal` / `read_file` など harness 固有のツール名に依存していないかも見る。
- Deterministic Offload: extract / count / validate / diff / format / parse / lint が LLM loop に混ざっていないか。既存 script / CLI がある処理を agent が UI・手作業で書き、SSOT の script 経路と手順が矛盾していないか。
- Reference Integrity: 相対 Markdown link の実在に加え、`#anchor` と `セクション N` / `section N` / `§N` の散文ポインタが対象の見出しへ解決するか。ファイル実在だけを PASS にしない。機械検査では code span / fenced code 内の記法例、`URL` / `path` などの placeholder target を除外する。
- Context Compression / Preservation: 記述なしでも正常・例外・停止時の判断が変わらない一般論・自明な説明・装飾・metadataの言い換え・重複は、圧縮より先に削除候補にする。判断に必要なユーザー固有事実・ID・パス・方針・根拠・Example・非自明な手順、承認範囲・未検証要件・停止／復旧条件、運用メタコメントは保持する。
- Runtime Classification: 各 finding を `runtime-affected` / `review-only` に分け、casual input forced routing の有無を確認する。

## Fix Policy

`fix` / `ALLFIX` / `自動修正` 指定がある場合は、次の順で低リスク修正を実行する。

1. 削除: 判断に不要な記述を短く言い換えて残さない。履歴は古さだけで消さず、現行判断に不要かつ原文の保存を確認できたものだけ削除し、必要なら固定リビジョン等の再取得先を残す。未保存の追記は保持する。
2. 統合 / 圧縮: 必要な残りだけを整理する。重複をSSOT参照へ置換する場合は、参照先の実在と読み込み経路で同じ判断が成立し、自己完結性を損なわないことを確認する。
3. 分離 / 移動: always-loaded の詳細を許可スコープ内の scoped instruction、prompt、skill、docs へ移す。Global対象はGlobal内で完結し、明示許可なくworkspaceへ移さない。
4. 追加: 削除 / 統合 / 移動で解けない場合だけ追加する。

`fix` / `ALLFIX` / `all fix` は優先度で選別しない。承認範囲内の指摘は Medium 以下も全件修正し、修正しない指摘には確認が必要な条件か維持の根拠を明記する。Low 以外を修正したときは `rubberduck` 指定がなくても、修正後 diff を別モデルの評価サブエージェントで Rubber Duck レビューし、指摘を反映してから完了とする（`review-only` では不要）。

自動修正してよいもの: 明示対象の prompt 圧縮、リンク切れ修正、supported frontmatter への小修正、未参照であることを確認した孤立コメントの削除。

自動修正しないもの: `AGENTS.md` / `copilot-instructions.md` へ metadata 目的だけで YAML frontmatter を追加する変更、generated marker の削除判断が未検証の変更、Global の skill / instruction を workspace へ複製する変更、大規模 agent rewrite、公開同期、履歴改変。

`review-only` / `read-only` は `fix` より優先する。競合指定時は変更せず、競合を報告する。

review / audit 依頼だけでは変更しない。commit / push / publish、権限拡大、無関係な dirty 変更の巻き戻しは明示承認なしに行わない。移植時も元のライセンス・帰属を保持する。

## Rubber Duck Mode

`rubberduck` / `rubber duck` 指定は名前付き agent の要求ではなく、各前提を言語化して根拠で反証するレビュー手法として扱う。

- 利用可能な評価サブエージェントへ、対象・制約・期待出力とともに Rubber Duck 方式を明示して委譲する。
- `RubberDuck` という agent が登録されていなくても、新規 agent は作らない。
- サブエージェントが利用できない場合は同じ問いで fallback review を行い、`PASS` ではなく `INCOMPLETE` とする。
- サブレビューの path、行、件数、重複、欠落の主張は、実ファイルに対する deterministic check または限定 read で照合してから採用する。

## Verification Gate

- frontmatter、参照整合性、配置、重複件数は、利用可能な既存 validator / parser / search tool を優先して検査する。
- 参照整合性は、見出し / `#anchor` の解決を実際に行った gate 名を validator の出力または source で特定できたときだけ `PASS` とし、特定できなければ `NOT_RUN` とする。
- 各検査を `PASS` / `FAIL` / `NOT_RUN` で記録し、使った tool または script、対象、判定根拠を示す。
- validator が無い場合は検査を LLM の目視だけで `PASS` にせず、限定 read で代替できない項目を `NOT_RUN` にする。
- 必須ファイルを読めない、検査が失敗する、または coverage が不足する場合は修正を止め、未確認対象と再開条件を伴う `INCOMPLETE` とする。
- 一時 validator や中間ファイルを作った場合は、検証後に削除する。
- 圧縮・削除は原文と修正後で正常・例外・停止時の代表入力の判断を比較する。キーワード残存だけで合格にせず、意図しない差を修正し、挙動変更は承認範囲を確認する。横断レビューでは重複消失と要件の空白が増えていないことも確認する。

## Review Flow

1. Scope Gate を通す。
2. 必要な rubric / entry と対象全件の全文を読み、削除候補を先に判定する。直近の変更節だけで全体を評価しない。圧縮案は同条件の改行で文字数・行数・見出し数のBefore→Afterを示す。数値は補助指標とし、明確な問題がなければ変更不要。
3. Verification Gate で frontmatter、agent placement、参照整合性（link 実在 + 見出し解決）を検査する。機械検査は code span / fenced code と placeholder target を false positive として除外する。
4. Rubber Duck 指定時は評価サブエージェントで前提を反証し、主張を実ファイルで照合する。
5. finding を優先度順に出し、`削除 / 統合 / 分離 / 移動 / 追加 / 維持` に分類する。
6. `fix` 指定時は1ファイルずつ低リスク修正を適用し、Verification Gateと同じ観点で再レビューする。最大 3 回で止め、残件があれば理由を報告する。
7. 追加提案には、削除 / 統合 / 移動で解けない理由を添える。

## Output Format

### ✅ Good Points
- {良い点}

### ⚠️ Improvements Needed
- {Priority} [{削除|統合|分離|移動|追加|維持}] {Category}: {file}:{line} → {fix} | Impact={runtime-affected|review-only} | Trigger={wording-only|wording + catalog|duplicated entry routing|always-loaded boundary violation|other}

### Runtime Impact
- runtime-affected: {既定会話挙動、always-loaded entry、または実行時に自動ロードされる / agent が読む asset に影響する残件}
- review-only: {人間が明示的に開いたときだけ読まれる asset の残件}

### Verification
- {実施した read / grep / link / frontmatter / subagent review / 再レビュー}

### Recommendation
- {総合評価 `PASS` / `NEEDS_IMPROVEMENT` / `INCOMPLETE`、修正済みファイル、残リスク、次アクション}
