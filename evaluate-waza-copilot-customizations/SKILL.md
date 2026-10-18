---
name: evaluate-waza-copilot-customizations
description: "Waza で個人（~/.copilot）/ ワークスペース / 任意パスの instructions / agents / skills をセットアップ、static/runtime 評価、gate 単体実行、結果要約、report 更新まで行う。"
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

# WAZA evaluate copilot customizations

個人（`~/.copilot`）、現在のワークスペース、または任意パスの Copilot customization files を対象に、Waza 評価プロジェクトのセットアップ、static/runtime 評価、gate 単体実行、結果要約、report 更新を行う。

## Scope

- 既定の評価対象: `$HOME\.copilot`（instructions / skills / agents）
- ワークスペース評価対象の例: `<workspace>\.github`
- 任意評価対象の例: instruction / agent / skill を含むディレクトリまたは単一ファイル
- 既定の Waza 評価プロジェクト: `~/waza-copilot-customization-evals`
- 既定の static eval: `evals\copilot-customizations\eval.yaml`
- 既定の runtime eval: `evals\copilot-customizations\runtime-eval.yaml`
- 既定の結果 JSON: `results\customizations-eval.json`
- 既定の runtime 結果 JSON: `results\runtime-customizations-eval.json`
- 既定の report: `reports\YYYY-MM-DD-copilot-customizations-waza-report.md`

## Setup Links

- Setup guide: https://github.com/aktsmm/Agent-Customization/blob/master/docs/waza-copilot-customizations-setup.md
- Template: https://github.com/aktsmm/Agent-Customization/tree/master/templates/waza-copilot-customization-evals

この skill だけをコピーした場合は、まず setup guide を開く。`evalProject` が無い場合は template から始める。

## 引数

skill には入力変数の仕組みがない。依頼文と `argument-hint` から次の値を読み取り、指定がなければ既定を使う。

- `targetScope`: `personal`（`~/.copilot`） / `workspace` / `custom`。既定は `personal`
- `targetPath`: `custom` のときは必須。`workspace` で空なら `<workspace>\.github`、`personal` で空なら `$HOME\.copilot`
- `evalProject`: 空なら `~/waza-copilot-customization-evals`
- `action`: `setup` / `run` / `runtime` / `gate` / `report` / `full`。既定は `full`
- `executionMode`: `static` / `runtime` / `both`。既定は `static`
- `gateMode`: `metadata` / `agent-structure` / `token-budget` / `all`。`action` が `gate` のときだけ使う。既定は `all`（3 モードを順次実行する論理指定）
- `maxFileTokens`: 既定は 5000
- `maxTotalTokens`: 既定は `personal` が 130000、`workspace` / `custom` が 60000
- `runtimePrompt`: `runtime` のときに実行・記録する prompt。空なら target を要約する smoke prompt を使う
- `runtimeModel`: runtime / copilot-sdk 用 model。空なら、現在の環境で使える model 名を確認して選ぶ
- `runtimeTaskStrategy`: `template` / `record`。既定は `template`

## Operating Rules

- 評価対象の instruction / agent / skill 本体は、この skill では変更しない。
- 修正はユーザーが明示した場合だけ行う。評価だけなら Waza project 配下の eval 資産、結果 JSON、report だけ更新してよい。
- secret、認証情報、個人アカウント値は report に書かない。問題がある場合はファイル名と観点だけを書く。
- PowerShell 前提で、コマンドは非対話・単発・timeout 付きで実行する。
- 結果の出力が長い場合は、summary、failed gate、issue、warning、next fix candidates だけを抽出して報告する。
- `action=setup` または `action=full` では、必要なら Waza project 側の `.waza.yaml`、static/runtime eval、task、grader script、report script、results/`、`reports/` を作成または更新してよい。
- `action=report` は既存の結果 JSON / report を優先して読み、無ければ `run` を実行してから report を作る。
- `runtime` は `copilot-sdk` 前提。必要なら `waza models`、`copilot login` 状態、モデル名を確認する。
- `runtime` で target 自体の実挙動を検証したい場合、既定では `write-runtime-task.ps1` で deterministic task を作る。
- `waza new task from-prompt` は exploratory には便利だが、一時パスや特定文面に過剰適合した grader を生成しやすい。既定では使わず、使う場合も生成後に task を必ず見直す。
- `runtimePrompt` が空欄でも、target path と出力フォーマットを含む smoke prompt を自動生成してよい。
- runtime task には未展開変数名（例: `$resolvedTarget`, `$targetName`）を残さず、解決済みの target path と basename が literal に入っていることを確認する。
- runtime 実行前に task ファイルを一度読み、target path、期待見出し、grader の厳しさが意図どおりかを確認する。

## Workflow

1. `evalProject` が空欄なら `Join-Path $HOME 'waza-copilot-customization-evals'` を使う。
2. `targetScope` と `targetPath` から評価対象を決める。
   - `personal` または空欄: `targetPath` が空なら `$HOME\.copilot`
   - `workspace`: `targetPath` が空なら `<workspace>\.github`
   - `custom`: `targetPath` を必須として扱う
   - 単一ファイルもディレクトリも可
   - `maxTotalTokens` が空なら、全個人資産を含む `personal` は130000、読み込み単位を想定する `workspace / custom` は60000を使う
3. 評価対象が存在するか確認する。存在しない場合は、候補パスを出して停止する。
4. `action` を決める。
   - `setup`: Waza project の存在確認と不足資産の作成/更新だけ行う
   - `run`: static eval を実行し、結果 JSON と report を更新する
   - `runtime`: `copilot-sdk` で runtime task を記録・実行し、結果 JSON と report を更新する
   - `gate`: 指定 gate だけ実行する
   - `report`: 既存結果の要約と report 更新を行う。必要なら実行を補完する
   - `full` または空欄: setup -> static run -> optional runtime -> report を順に行う
5. 評価プロジェクトが存在するか確認する。
   - `.waza.yaml`
   - `evals\copilot-customizations\eval.yaml`
   - `evals\copilot-customizations\runtime-eval.yaml`
   - `evals\copilot-customizations\scripts\grade-copilot-customizations.ps1`
   - `evals\copilot-customizations\scripts\write-copilot-customizations-report.ps1`
   - 見つからない場合は、公開 repo の setup guide / companion template を案内し、template から初期化する案を優先する
6. `action=setup` または `full` のとき、不足している資産を作成または更新する。
   - `.waza.yaml`
   - `evals\copilot-customizations\eval.yaml`
   - `evals\copilot-customizations\runtime-eval.yaml`
   - `evals\copilot-customizations\tasks\customization-static.yaml`
   - `evals\copilot-customizations\runtime-tasks\`
   - `evals\copilot-customizations\scripts\grade-copilot-customizations.ps1`
   - `evals\copilot-customizations\scripts\write-copilot-customizations-report.ps1`
   - `results\`
   - `reports\`
7. Waza standalone が使えるか確認する。
   - `waza --version`
   - `Get-Command waza`
8. 評価対象を `$env:WAZA_CUSTOMIZATIONS_TARGET` に入れる。
9. `action=run` または `full` のとき static eval を実行する。
   - `waza run evals\copilot-customizations\eval.yaml --output results\customizations-eval.json --no-update-check -v`
10. `action=runtime`、または `action=full` かつ `executionMode=runtime/both` のとき runtime task を作成・実行する。
   - 既定の `runtimeTaskStrategy=template` では `write-runtime-task.ps1` を使う
   - `runtimePrompt` が空なら target を要約・制約抽出する smoke prompt を組み立てる
   - `write-runtime-task.ps1 -TargetPath <target> -OutputPath evals\copilot-customizations\runtime-tasks\runtime-target.yaml`
   - task 生成後、`runtime-target.yaml` を読み、literal な target path と `Purpose:/Guardrails:/Usage:` が入っていることを確認する
   - `runtimeTaskStrategy=record` のときだけ `waza new task from-prompt ... --overwrite` を使う
   - `record` を使った場合は task ファイルを読み、path_pattern 固定や過剰に厳しい `contains_cs` を緩めてから実行する
   - `waza run evals\copilot-customizations\runtime-eval.yaml --output results\runtime-customizations-eval.json --no-update-check -v`
11. `action=gate` のとき `gateMode` に応じて必要な gate だけ実行する。
   - `metadata`
   - `agent-structure`
   - `token-budget`
   - `all`: grader に `Mode all` を渡さず、上記3モードを1回ずつ順次実行する
12. 結果 JSON を読み、summary を抽出する。
   - total tests
   - succeeded / failed / errors
   - success rate
   - aggregate score
13. 失敗 gate がある場合、または `action=gate` のとき、同じ `$env:WAZA_CUSTOMIZATIONS_TARGET` を指定したまま必要な個別 gate を単体実行して詳細を取る。
14. `action=report` または `run/runtime/full` のあと、`write-copilot-customizations-report.ps1` を使って `reports\YYYY-MM-DD-copilot-customizations-waza-report.md` を作成または更新する。
   - Date
   - Model: GitHub Copilot
   - Action
   - Evaluated source
   - Commands run
   - Waza summary
   - Gate results
   - Findings
   - Next fix candidates
15. 最終回答では、action、execution mode、評価対象、結果、赤 gate、警告、次の一手を簡潔に出す。

## Command Reference

代表的な static eval。workspace / custom target は `Workflow` の target 解決規則に従って `$env:WAZA_CUSTOMIZATIONS_TARGET` だけを変える。

```powershell
$project = Join-Path $HOME 'waza-copilot-customization-evals'
Set-Location $project
$env:WAZA_CUSTOMIZATIONS_TARGET = Join-Path $HOME '.copilot'
waza run evals\copilot-customizations\eval.yaml --output results\customizations-eval.json --no-update-check -v
```

- runtime、record、個別 gate、report のコマンドは `Workflow` 手順10〜14を正本とする。
- `record` では生成taskを実行前に読み、固定された一時pathや過剰に厳しい `contains_cs` を修正する。
- setup / repair では手順5の必須資産を `Test-Path` で確認し、不足分だけtemplateから復元する。

## Final Response Format

```markdown
## 結果
- Action: <setup/run/gate/report/full>
- Execution mode: <static/runtime/both>
- Target: <path>
- Waza eval: pass/fail
- Success rate: <value>
- Aggregate score: <value>
- Result JSON: <path>
- Report: <path>

## 赤 Gate
- <gate>: <issue>

## 警告
- <warning>

## 次の一手
1. <action>
2. <action>
```

`赤 Gate` や `警告` がない場合も、`なし` と明記する。
