---
name: refine-product-100
description: "プロダクトを反復実行で最高品質へ近づける。前回サマリーを読み、重複観点を避けて自律的に改善軸を選び、各回で具体改善・検証・記録まで行う。明示 release mode では品質 gate 後に配布と公開状態確認まで進める"
disable-model-invocation: true
argument-hint: "対象、重点観点、モード（例: current workspace / all / quick / plan / review / release）"
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
<!-- updated: 2026-09-15 -->

# refine product 100

前回サマリーから今回最も効く改善軸を選び、code / docs / slide / runbook / prompt / data / AI assetを具体改善・検証・記録する。

## Non-Negotiables

- 実行可能 mode では、各回で必ず 1 つ以上の具体改善を行う。レビューだけで終わらない。安全に編集できない場合でも `Guard now` として test / docs / checklist / static guard などの成果物を残す。
- 実行可能 mode では、`.git/info/refine-product-state.md` を必ず compact rewrite する。`.git/` が無い場合だけ `Local State: skipped` とし、理由を書く。
- 100% を目指し、検証なし完了、同根放置、`Fix now` の残件逃げをしない。分類は `Safety + Classification` を SSOT とし、残せるのは成果物付き `Guard now` または確認待ち `Block` だけ。
- 実機確認が必要でも、機械的代替（test / static guard / manifest consistency / dry-run payload / checklist）を最低 1 つ追加してから止まる。
- 止まる前に次を確認する: 今回の具体改善 / 前回との差分 / 同根 sweep / test or guard / docs sync / cleanup / artifact hygiene / 別軸 review / terminal cleanup / prompt or instruction 側の再発要因。

## Inputs / Modes

- Target: `current workspace` / `all` / `src` / file / folder / product name
- Focus: `feature` / `non-functional` / `UIUX` / `security` / `docs` / `cleanup` / `all`
- Mode: 空欄 / `fix` / `improve` / `quick` / `plan` / `review` / `dry-run` / `verbose` / `release` / `deploy` / `publish`（空欄は default）

| Mode | 動作 |
| --- | --- |
| default / `fix` / `improve` | 前回サマリーから今回の主改善軸を自律選定し、修正・Sweep・検証・state 更新まで行う |
| `quick` | P0/P1 と検証を最優先。P0/P1 の `Fix now` は残さず、関連する最小 Sweep / Guard / Docs / Cleanup は行う |
| `plan` / `review` / `dry-run` | No-Edit。計画または指摘だけ出し、修正・state file 作成/更新はしない |
| `verbose` / `full` / `詳細` | 通常の mode に詳細出力を足す modifier。Coverage Matrix 全表や詳細な Findings は明示時だけ出す |
| `release` / `deploy` / `publish` | default の品質 gate 後、明示された配布対象だけ Release Addendum へ進む |

No-Edit の指定は、この skill 全体の修正・Guard 成果物追加・state 更新・release・cleanup 要求より優先する。`Fix now` も未修正の指摘として報告し、ファイル・state・永続メモを変更しない。

### Release Intent

- `release` / `deploy` / `publish` または同義の明示依頼だけを full release intent とする。単語が文脈に出ただけ、`release-prep`、`準備だけ`、`publishしない` は実行承認にしない。
- repo、単一配布物、manifest上の package/version、公開先が一意なら、品質 gate 後に commit / tag / push / publish / GitHub Release / verification まで再確認なしで進める。
- 配布対象、version、公開先、権限が不明、または破壊的履歴操作が必要なら `Block` として確認する。
- `Fix now` がある状態では配布せず、各配布工程を個別に `done / skipped / blocked` で報告する。

## Safety + Classification

安全とは「小さい変更」ではなく、依頼範囲内・可逆・ローカル検証可能・外部公開なし・secret/本番/個人データなし・影響範囲と正しさを説明できること。

| 分類 | 条件 | 必須対応 |
| --- | --- | --- |
| `Fix now` | 依頼範囲内、正しさを説明可能、ローカル検証可能、非破壊的 | 修正・再検証まで実行。残件送り不可 |
| `Guard now` | 本修正は不可だが test / static guard / docs / checklist でリスク低減可能 | 最低 1 つの成果物を追加し、残理由を書く |
| `Block` | 破壊的、外部公開、本番データ、仕様判断、権限不足 | 不足入力、試した代替、次の確認を明記 |

Retry は同一原因 3 回まで。超えたら、試した代替と失敗理由を添えて `Block` に再分類する。

既存の test / lint / build 失敗は、依頼範囲との関係で分類する。依頼範囲内なら `Fix now`、無関係なら `Guard now` として証跡を残し、対象範囲の修正を続ける。原因不明で安全に進めない場合だけ `Block` にする。

## State Intake / Local State / Run Ledger

- 永続先は `.git/info/refine-product-state.md` だけ。Run Ledger / Handoff はチャット出力とし、`.github/` や代替logを作らない。
- 前回状態は、ユーザー指定state → local state → 直近Run Ledger/Handoffの順に読む。最新の実測を優先し、完了済み操作を旧Blockやtodoだけで再実行しない。
- Executableではlocal stateを確定時点ごとにcompact rewriteする。No-Editまたは`.git/`なしでは作らず、`Local State: skipped`と理由を記録する。
- 構成は `Current Snapshot / Last Run Detail / Open Items / Recent Runs / Do Not Repeat / Next Focus Candidates / Guard or Block` に限定する。
- 上限は Last Run 25行、Recent Runs 5件、Open/Do Not Repeat/Guard各10件、Next Focus 3件、全体160行または16KB。超過前に古いrunを1行へ圧縮する。
- 未解決項目は圧縮前に `OPEN|GUARD|BLOCK-YYYYMMDD-NN` でupsertし、閉じたIDを再利用しない。
- raw log、全文Findings、terminal出力、diff、長文Handoff、secret、個人データ、絶対path、未検証推測を書かない。
- 前回項目を `Closed / Still Open / Reclassified / New` に動かし、本文を転載せず進展だけをstateとLedgerへ残す。

## Autonomous Improvement Planning

この skill は checklist を上から消化するためではなく、AI が今回いちばん効く改善を計画・実装・検証するために使う。

1. 前回サマリーから `closed / still open / next hypothesis / do-not-repeat` を拾う。
2. 今回は前回と違う主改善軸を 1 つ選ぶ。前回と同じ軸を選ぶのは、新 evidence、未解決 P0/P1、または前回修正の検証不足がある場合だけ。
3. Coverage Matrix は候補地図として使う。すべての小観点を機械的に埋めず、対象と前回履歴から高レバレッジな軸を選ぶ。
4. 実行可能 mode では、選んだ主改善軸から少なくとも 1 つの concrete improvement を完了させる。例: bug fix、UX copy 修正、入力 validation、test 追加、docs 同期、cleanup、guard 追加。
5. 「改善余地なし」と言う前に、別 persona（ユーザー / 運用者 / 保守者 / 監査者 / 次に引き継ぐ AI）で 1 回だけ見直す。
6. それでも安全に編集できない場合だけ、`Block` にし、AI が代替で追加した `Guard now` 成果物を明記する。

## Coverage Matrix

各軸を `Covered / N/A / Open` に分類する。`N/A` は対象外理由を書き、`Open` は `Fix now / Guard now / Block` に分類する。ただし、この表は観点の候補地図であり、AI の自律的な問題発見を縛る上限ではない。小観点に無い問題を見つけた場合は、最も近い軸に置いて直す。

| 軸 | 主要観点 |
| --- | --- |
| 目的・適合 | 対象ユーザー、主要ジョブ、機能要件、受入条件、成功条件、非目的、優先順位、現状とのズレ |
| 機能・状態 | 機能名、用語、ユースケース、境界値、失敗経路、状態遷移、同時実行、冪等性、後方互換 |
| 入力・データ | schema、型、必須/任意、空値、重複、文字コード、locale、時刻、ファイル/URL、外部データ品質 |
| 出力・読まれる面 | 最終 surface、書式、文言、リンク、引用、通知、メール、チャット、CLI、PDF/slide/export、閲覧環境 |
| UI/UX・アクセシビリティ | 視認性、導線、Affordance、Feedback、Recovery、キーボード、スクリーンリーダー、responsive |
| 非機能・運用 | 性能、信頼性、可用性、互換性、保守性、設定、ログ、監視、rollback、コスト、rate limit |
| セキュリティ・安全 | 認証/認可、secret、個人情報、権限、入力検証、injection、依存関係、公開範囲、破壊的操作 |
| 連携・契約 | API 契約、SDK/version、外部サービス、feature flag、migration、error contract、timeout/retry |
| 検証・品質 gate | unit/integration/e2e、lint/typecheck/build、snapshot、dry-run、eval、fixture、artifact/state/exit code 確認 |
| Docs・学習導線 | README、Quick Start、help、runbook、エラーメッセージ、CHANGELOG、機能名/用語統一、設計/運用 docs の同期 |
| AI / 自動化資産 | prompt injection、幻覚防止、根拠、禁止事項、出力形式、不明時、handoff/state、tool scope、決定論処理の script 化 |
| Cleanup・成果物衛生 | dead code、重複、古い資材、一時ファイル、不要 terminal、生成物混入、絶対パス、ローカル依存 |

追加探索では `ユーザー / 運用者 / 保守者 / 監査者 / 次のAI` の誰がどこで困るかを1回問い、通知やCLI出力は最終surfaceで評価する。

Priority: P0 = 主要機能破壊・データ損失・情報露出 / P1 = 導線混乱・テスト不在・README 不一致 / P2 = 品質改善・文言・dead code。

## Fix Cycle

1. Context/Health: entry point、instruction、前回state、検証手段を読み、baseline failureと今回由来を分ける。
2. Review: Coverageを分類し、Openを `Fix now / Guard now / Block` に分ける。
3. Implement/Sweep: 既存パターンに合わせて最小修正し、同根gapを検索してまとめて直す。
4. Test/Verify: 回帰testやguardを追加し、diagnostics → lint → typecheck → test → buildをartifact/state/exit codeまで確認する。
5. Docs/Cleanup: README、help、CHANGELOG、用語を同期し、一時資材、dead code、terminalを片付ける。
6. Close: `Fix now`を0にし、残件は条件を満たす `Guard now / Block` へ再分類する。

未解決項目が残る場合は、安全条件を再評価し、`Guard now` / `Block` に再分類してから current run を閉じる。再分類できない `Fix now` が残る場合は未完了として明記し、完了宣言しない。

Subagent は、大規模 repo / 複数観点 Sweep / 長いログ解析で read-only 調査に限定して使う。使わない場合は理由を最終報告に残す。

## Meta Improvement Scope

prompt / instruction / skill / hook / reusable script 自体に再発要因がある場合のみ扱う。主タスクの修正と検証後、同じスコープで安全な最小変更だけ反映する。別系統の大整理、public/private sync、他資産への波及編集は明示依頼がない限り Next Steps に積む。

## Release Addendum

`release` mode かつ配布対象が明示されたソフトウェア配布物だけに適用する。ドキュメント等は skip。

1. versionの公開済み有無を確認し、既存ならpatch以上を上げ、metadata、lockfile、表示、CHANGELOG、release notesを同期する。
2. typecheck、lint、test、audit後にbuild/packし、artifactの存在・サイズ・時刻とtarball内容を確認する。
3. 明示release intentがある場合だけ commit → push → publish → GitHub Releaseへ進む。
4. registry/APIと掲載ページでversion、tag、Release、添付を確認し、送信成功と公開反映を区別する。stale表示だけで再publishしない。
5. 各工程を個別報告し、認証・審査・権限不足は `Block` にする。必須gate達成後はstate同期とcleanupだけ行い、新しい監査を足さない。

## Prompt-only Handoff

この skill は単体で動く前提とする。`handoffs:` frontmatter や custom agent 前提の記述は追加しない。代わりに、チャット文脈で再開できる context-based handoff を出力する。

`Run Ledger` は常に出すが、最大 10 行の compact form に限定する。`Handoff Packet` と `Handoff Options / Next Action Suggestions` は、`Block`、ユーザー判断待ち、重要な文脈を持つ `Guard now`、または途中停止・partial fix・環境変化など非自明な再開経路がある場合だけ出す。通常の `AI can continue now` だけなら省略する。

Handoff option は `Plan first` / `Rerun refine` / `AI can continue now` / `User decision` を基本にし、目的・いつ選ぶか・そのまま使える依頼文を含める。

Coverage output は通常 delta-based にする: `Covered / N/A / Open` の総数、全 `Open` 軸、前回 state からの分類変化（`Covered -> Open` の退行を含む）だけを出す。Full Coverage Matrix はユーザーが `verbose` / `full` / `詳細` を明示した場合だけ出す。

## Output Contract

出力は次の順序にする。空の任意セクションは省略し、長い作業ログや前回出力の再掲はしない。

| Mode | 必須セクション |
| --- | --- |
| No-Edit | `Plan or Findings` / `Gate` / `Coverage Matrix Summary` / `Safe-to-Fix 判定` / `Recommendation` / `Run Ledger` |
| Executable | `Done` / `Improvement Focus` / `Sweep` / `Check` / `Findings` / `Safe-to-Fix 判定` / `Coverage Sweep` / `100% Pass 判定` / `Next Steps` / `Run Ledger` |
| release | Executable に `Release Status` を追加し、version、artifact、commit、tag、push、publish、GitHub Release、公開確認を個別に `done / skipped / blocked` で示す |

- No-Edit は未編集であること、全 `Open` 軸、分類変化、未修正の `Fix now / Guard now / Block` を明記する。
- Executable は実行した変更と検証コマンド、同根 sweep、`Fix now = 0`、残る `Guard now / Block` の代替と次確認を示す。
- Coverage は通常、`Covered / N/A / Open` 件数、全 `Open` 軸、前回からの分類変化だけにする。全表は verbose 時だけ出す。
- `Documentation / Cleanup` と `Meta Improvements` は該当時だけ出す。

### Run Ledger

常に次の compact form を最大 10 行で出す。No-Edit では `Local State: skipped (no-edit mode)`、`Concrete Improvement` は次回 target、`Closed This Run` は `none` とする。

```text
Run Type: baseline|continuation|rerun|release-prep
Prior State Used: local state|user state file|previous Handoff Packet|previous Run Ledger|none
Local State: used|updated|skipped ({path or reason})
Primary Axis This Run: {前回と重複しない主改善軸}
Concrete Improvement: {完了した改善、またはNo-Editで次回改善する最小対象}
Closed This Run: {閉じた項目と検証結果、またはnone}
Still Open: {No-EditのFix now、またはGuard now / Block / Next Steps}
Reclassified: {分類変更と理由、またはnone}
New Axis Covered: {今回追加で見た別軸}
Next Run Focus: {次に見る1〜3項目}
```

### Handoff（該当時のみ）

`Block`、ユーザー判断待ち、重要な `Guard now`、または非自明な再開経路がある場合だけ次を出す。

```text
Goal: {次に達成すること}
Current State: {未編集のFindings、または完了済み変更・検証・成果物}
Open Items: {Fix now / Guard now / Block / Next Steps。ExecutableではFix now不可}
Prior State Used: {使用したstate}
Recommended Path: {Plan first / Rerun refine / AI can continue now / User decision}
Resume Prompt: {次ターンでそのまま使える依頼文}
Do Not: {触らない範囲 / 未確認前提 / 公開・削除禁止}
```

複数経路の選択が必要な場合だけ、`Handoff Options / Next Action Suggestions` を `候補 / 目的 / いつ選ぶか / 依頼文` の表で追加する。

## Final Self-Check

- 前回状態を `Closed / Still Open / Reclassified / New` に動かし、今回の主改善軸と具体改善を示した。
- Coverage を `Covered / N/A / Open`、gap を `Fix now / Guard now / Block` に分類した。
- Executable は具体改善または Guard 成果物を完了し、`Fix now = 0` まで再検証した。No-Edit は未修正と明記した。
- `Guard now / Block` に試行、代替、次確認があり、Run Ledger は最大10行で state の使用・更新・省略理由を含む。
- state file は `.git/info/refine-product-state.md` だけを使い、履歴圧縮、stable ID、上限を守った。
- Handoff は必要条件を満たす場合だけ出し、前回本文を転載していない。
- 一時資材、dev server、task terminalを片付け、残す場合は理由を書いた。

## Run Boundary

- No-Edit mode（plan / review / dry-run）指定。
- `Fix now` が 0 件で、`Guard now` / `Block` の代替と次確認が記録済み。
- 同一原因の再試行が 3 回超過。
- 安全上ユーザー確認が必要で、非破壊の Guard now を試した。