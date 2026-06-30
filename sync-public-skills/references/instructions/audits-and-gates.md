# sync-public-skills: Audits and Sync Gates

`sync-public-skills` SKILL.md から分離した、destination 別 audit / gate 判定の詳細。

## New Skill Classification Gate (incident 2026-06-24 再発防止)

`Sync-AndPush.ps1` は Step 0.5 で `Invoke-NewSkillGate` を実行し、private repo の `.github/skills/` 配下と、既知集合（`$KnownPublicSkills` + `$DefaultInternalSkills` + `$HardDeniedSkills`）を照合する。未分類 skill が 1 件でもあれば `exit 2` で sync を強制停止する。

- 検知された skill は以下のいずれかへ分類してから再実行する
  - **public-safe**→ `$KnownPublicSkills` へ追記する。Copilot-Skills Public Audit Gate（下記 license / DUP / secret）を先に通す
  - **internal-only**→ `$DefaultInternalSkills` へ追記する。script が自動的に `$HardDeniedSkills` へマージし、public 除外され GIM/EMU へ mirror される
  - **public-denied**→ `$HardDeniedSkills` へ追記する。internal にも出さない
- 例外扱いしたい場合だけ `-AllowUnknownSkills` を指定すると public-safe として同期される。面倒だからという理由で使わず、ケースごとに分類を保存する
- この Gate は internal skill の public 漏洩（2026-06-24）の直接根原因（internal SSOT に未登録の skill が sync を通ってしまう）を防ぐために追加された

## Copilot-Skills Public Audit（license / DUP / secret）

`copilot-skills/`（`.copilot` 由来ミラー）を broad sync で public へ出す前に、skill 単位で 3 観点を監査し、除外対象を `Sync-AndPush.ps1 -ExcludeCopilotSkills` に渡す。primary-only では primary の分類と漏れ込み確認だけを行い、対象外 skill の公開可否を毎回再判定しない。判断は必要時にここで行い、script にハードコードしない。

- **①ライセンス**: 第三者 Proprietary は除外。Anthropic / Microsoft Scout ビルトイン（`docx` / `pptx` / `xlsx` 等、LICENSE.txt が複製・派生・サービス外保持を禁止）は public 不可。LICENSE 不明（`expense-report` / `loop` / `excalidraw` 等）は安全側で除外。Apache 2.0 等の再配布可ライセンス（`web-artifacts-builder` 等）は LICENSE / NOTICE を保持して公開可。自作 skill（`receipt-tax-ocr` / `permission-max` / `x-twitter-browser-ops` 等）は license / metadata.author / LICENSE.txt が揃っていれば公開候補にできる
- **②DUP**: 同名 skill が private repo `.github/skills/<skill>/` にある場合は、そちらを正として copilot-skills 側を public から除外する（二重公開防止）
- **③機密**: ユーザー名、ローカル絶対パス、Tenant ID、顧客名、個人メールを含む skill は、一般化できないなら除外する。一般化済みの自作 skill でも license / metadata.author / LICENSE.txt の provenance が揃うまでは public へ出さない
- 既定ブラックリスト例: `docx,pptx,xlsx,expense-report,loop,excalidraw`（①②）＋ `.github/skills` と重複する skill（②）。新規 skill が増えたら上 3 観点で再判定してリストを更新する
- `Sync-AndPush.ps1` は hard denylist（native: `excel-plus`、copilot: 上記 6 件）を引数に関わらず常に除外する。さらに 2026-06-24 以降は、`$DefaultInternalSkills`（下記 GIM Gate の SSOT）は自動的に native denylist へマージされるため、internal セットに入った skill は例外なく public から除外される。ここで確定する除外名は、それに上乗せする判断分だけ渡す

## EMU Private Sync Gate

- 行き先は user-owned private repo（`SYNC_INTERNAL_SKILLS_EMU_REPO`）。既定セットは GIM internal と同じ `InternalSkills`
- EMU repo の visibility が `PRIVATE` または `INTERNAL` であることを確認する。`PUBLIC` なら停止する
- user-owned private は EMU 全員に自動公開されない。全員利用が要件なら org-owned internal（GIM）が必要で、作成可否を確認する
- EMU sync 先にも secret / 顧客情報 / 個人メール / 具体 TPID / ローカル絶対パスを入れない。例は placeholder にする
- `gh` で pull/push 権限が確認できるのに `git clone` が `Repository not found` になる場合は、repo 不在ではなく Git credential transport の不一致として扱い、clone に固執せず Contents / Git Data API で更新する

## GIM Internal Sync Gate

org-owned internal repo（env `SYNC_INTERNAL_SKILLS_GIM_REPO`、例: `<internal-org>/<internal-skills-repo>`）へ MS 社内向け skill を集約するゲート。`Sync-InternalSkills.ps1` が実装を担うが、「どれを internal へ出すか」は毎回ここで判断する。

- 既定 internal セット（SSOT）: `<denied-skill-1>`, `<denied-skill-2>`, `<denied-skill-3>`, `<denied-skill-4>`。新規 skill は下 3 観点で再判定して追加する
- 判定 3 観点: ①社内専用（public 不可だが社内なら有益）②対象ロールまたは全社員に有益 ③匿名化済み（顧客実名 / TPID 実値 / 個人メール / ローカル絶対パスなし）
- internal repo の visibility が `INTERNAL` または `PRIVATE` であることを確認する。`PUBLIC` なら停止する
- internal skill は public sync の `ExcludeSkills` / `ExcludeCopilotSkills` に残し、public へ漏れないことを確認する（2026-06-24 以降は `Sync-AndPush.ps1` が `$DefaultInternalSkills` を自動マージして除外するため、加え忘れによる public 漏洩を構造的に防ぐ。internal リストと public 除外リストは別管理だが、runtime では同一集合になる）
- README は script が各 SKILL.md の `description` + audience map から自動生成する。手書き編集しない
- push 前に sensitive scan を実行する（script がヒットで停止）。誤検知確認済みのときだけ `-AllowSensitive`
- script は `finally` で `RestoreAccount`（既定 `aktsmm`）へ復帰する。実行後に active アカウントを確認する

## Script CLI

- `Sync-AndPush.ps1` は機械適用のみ。除外は `-ExcludeSkills`（native）/ `-ExcludeCopilotSkills`（copilot-skills）で渡し、internal mirror は `-SyncEmu` / `-SyncInternal`（`-EmuDryRun` / `-InternalDryRun` で preview）を明示する
- 公開可否・internal 振り分けの判断は SKILL（と同名 prompt）が持つ。script は受け取ったリストを機械適用するだけ
- push はこの skill が明示実行され、`review-only` / `dry-run` でない場合だけ行う。VS Code では同名 prompt を使う

## Incident Recovery（internal content が public へ漏れた後）

prevention gate を通り抜けて漏洩した場合の復旧手順。internal skill が public へ漏洩した incident（2026-06-24）の実対応から。

- **filter-repo + force push だけでは消えない**。`git filter-repo --path <leaked> --invert-paths` + `git push --force --all` で branch から到達不能にしても、dangling commit は GitHub 上に残り `https://github.com/<owner>/<repo>/commit/<sha>` が **HTTP 200 のまま**。直接 SHA URL / cached view / code search から内容を引ける
- **404 化は GitHub Sensitive Data Removal 申請のみ**。<https://support.github.com/contact/private-information> から、漏洩 path の blob URL（`/blob/<sha>/<path>`、commit URL は form の検証で弾かれる）+ owner 関係 + 既に history rewrite 済みである旨 + 残存 commit SHA + fork 一覧を添えて申請する。漏洩内容そのものは貼らず SHA + path 参照に留める
- **path は 2 系統消す**。`.github/skills/<skill>` と root `<skill>` の両方を filter-repo 対象にする（sync 経路で root 直下に出ることがある）。force push 後に `git log --all -S '<secret-marker>' --oneline` で 0 件を実測してから完了扱いにする
- **fork は親削除でも残る**。fork は独立 repo に昇格し旧 object を保持するため、申請文で fork 一覧も purge 依頼する
- **star/fork がある repo は delete より rename**。rename は star / fork / URL redirect を維持し、削除のデメリットがない。新名で作り直したい場合も rename を優先する
- **ローカル move の罠**: cross-directory の `Move-Item` は途中失敗で `.git` を空殻化することがある。`robocopy <src> <dst> /MOVE /E` を使い、`.git` が壊れたら GitHub から fresh clone で置き換える（GitHub 側が intact なら最も確実）

## Sync Operational Hazards（broad sync 実行時の事故防止）

`Sync-AndPush.ps1` の broad sync は「source にない skill を public から削除」するため、source が空だと public 全削除になる。実際に repo rename 後の env stale で 2 回起きた（2026-06-24）。

- **env stale → public 全削除**: repo path / repo 名を rename した後、rename 前に起動した既存ターミナルは古い `SYNC_PUBLIC_SKILLS_PRIVATE_REPO` を保持する。`$DevRepo` が存在しない旧パスに解決され、source skill 0 件 → コピー 0 件 → 削除ループで public 全 skill が消える。対策として script に **DevRepo 健全性 Guard**（Step 0.0: source skill 数が下限 `$MinSourceSkills` 未満なら abort）と **削除 abort Guard**（コピー 0 件なら public 削除を中止）の二重防御を実装済み。rename 後は新ターミナルで env を読み直すか、プロセスに `$env:...` で明示注入してから sync する
- **pwsh 7 専用**: `Sync-AndPush.ps1` は PowerShell 7 構文を使う。Windows PowerShell 5.1 で起動すると 40+ の parse error で落ちる。必ず `pwsh` で実行する（`powershell.exe` ではない）
- **復旧手順**: 全削除に気づいたら、削除直前の正常 commit へ `git reset --hard <good-sha>` + `git push --force` で即復元できる（public repo の 1 commit 前がクリーンなら最速）
