# sync-public-skills: Audits and Sync Gates

`sync-public-skills` SKILL.md から分離した、destination 別 audit / gate 判定の詳細。

## New Skill Classification Gate (incident 2026-06-24 再発防止)

`Sync-AndPush.ps1` は Step 0.5 で `Invoke-NewSkillGate` を実行し、private repo の `.github/skills/` 配下と `scripts/skill-distribution.json` のpublic / internal / denied集合を照合する。未分類 skill が1件でもあればsyncを強制停止する。

Agent はこの script 停止を待たず、sync 実行前に同じ照合を行う。未分類 skill があれば、内容・命名・直近会話から勝手に public/internal/private を推測せず、必ずユーザーに `public-safe` / `internal-only` / `public-denied` / `今回は同期しない` の分類を確認する。

- 検知された skill は以下のいずれかへ分類してから再実行する
  - **public-safe**→ `publicSkills`へ追記する。Copilot-Skills Public Audit Gateを先に通す
  - **internal-only**→ `internalSkills`へname / audience / internalOnlyを追記する。public denylistへ自動統合されGIM/EMUへmirrorされる
  - **public-denied**→ `deniedSkills`へ追記する。internalにも出さない
- `-AllowUnknownSkills` は後方互換で受理してもoverrideには使わない。分類をconfigへ保存するまで停止する
- この Gate は internal skill の public 漏洩（2026-06-24）の直接根原因（internal SSOT に未登録の skill が sync を通ってしまう）を防ぐために追加された

## Copilot-Skills Private Inventory Gate

`copilot-skills/`（`.copilot` 由来ミラー）は private inventory とし、license に関係なく public へ同期しない。distribution config の `publicCopilotSkills` は空を維持し、inventory 全件を `deniedCopilotSkills` に分類する。`-IncludeCopilotSkills` は script が拒否する。

- 新しい inventory が増えたら `deniedCopilotSkills` へ分類してから sync gate を再実行する。未分類 inventory は停止する
- 同名 native skill が必要なら、内容・provenance を private repo の `.github/skills/<skill>/` へ別途 authoring し、native skill として public safety audit を通す。mirror をそのまま公開しない
- public repo に `copilot-skills/` が存在したら broad sync で削除し、remote tree でも不在を確認する

## EMU Private Sync Gate

- 行き先は user-owned private repo（`SYNC_INTERNAL_SKILLS_EMU_REPO`）。既定セットは GIM internal と同じ `InternalSkills`
- EMU repo の visibility が `PRIVATE` または `INTERNAL` であることを確認する。`PUBLIC` なら停止する
- user-owned private は EMU 全員に自動公開されない。全員利用が要件なら org-owned internal（GIM）が必要で、作成可否を確認する
- EMU sync 先にも secret / 顧客情報 / 個人メール / 具体 TPID / ローカル絶対パスを入れない。例は placeholder にする
- `gh` で pull/push 権限が確認できるのに `git clone` が `Repository not found` になる場合は、repo 不在ではなく Git credential transport の不一致として扱い、clone に固執せず Contents / Git Data API で更新する

## GIM Internal Sync Gate

org-owned internal repo（env `SYNC_INTERNAL_SKILLS_GIM_REPO`、例: `<internal-org>/<internal-skills-repo>`）へ MS 社内向け skill を集約するゲート。`Sync-InternalSkills.ps1` が実装を担うが、「どれを internal へ出すか」は毎回ここで判断する。

- 既定internalセットとaudience mapのSSOTは `scripts/skill-distribution.json` の `internalSkills`。新規skillは下3観点で再判定してconfigへ追加する
- 判定 3 観点: ①社内専用（public 不可だが社内なら有益）②対象ロールまたは全社員に有益 ③匿名化済み（顧客実名 / TPID 実値 / 個人メール / ローカル絶対パスなし）
- internal repo の visibility が `INTERNAL` または `PRIVATE` であることを確認する。`PUBLIC` なら停止する
- `internalSkills` はruntimeでpublic除外集合へ自動統合される。public mirror後もinternal skill pathが存在しないことを確認する
- README は script が各 SKILL.md の `description` + audience map から自動生成する。手書き編集しない
- push 前に sensitive scan を実行する（script がヒットで停止）。誤検知確認済みのときだけ `-AllowSensitive`
- sensitive scan の keyword hit は該当行を読んで判定する。実 credential / 個人メール / tenant・TPID 実値 / ローカル絶対パスは blocker。「secret を保存しない」という guardrail、redaction test fixture、明示的 placeholder は review 済み false positive として記録できる。`-AllowSensitive` を一括 bypass に使わない
- script は `finally` で `RestoreAccount`（既定 `aktsmm`）へ復帰する。実行後に active アカウントを確認する

## Script CLI

- `Sync-AndPush.ps1` はcleanな確定済みcommitの機械適用のみ。dirty intakeは `Commit-DirtySkills.ps1` のdry-run / `-Apply`へ分離する。internal mirrorは `-SyncEmu` / `-SyncInternal`（各DryRunあり）を明示する
- native public の狭い同期は `-PrimarySkills <skill-name...>` を使う。temporary copy script を作らず、正式 runner の classification / staging / rollback / path scope / hash gate を再利用する
- internal API syncはretry＋空SHA fail-fastを使い、stale skill pathを削除する。ref更新後のremote treeでMissing / Mismatch / Extraが0にならなければ失敗とする
- internal同期はdistribution configの全集合をfull mirrorする。subset指定は他Skill削除につながるため拒否する
- 公開可否・internal振り分けの判断基準はSKILL（と同名prompt）が持ち、確定結果はdistribution configへ保存する。scriptはconfigを機械適用する
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
