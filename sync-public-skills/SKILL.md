---
name: sync-public-skills
description: Synchronize curated Agent Skills across approved repositories with policy checks and verification. Use when publishing or updating managed skills, validating a repository mirror, or selecting a safe sync scope. Triggers on "sync public skills", "publish skills", "public 公開", "skill sync", "repository mirror".
argument-hint: "対象 skill 名、private/public/EMU/GIM repo path（任意）、mode（safe-auto / review-only / dry-run / all）"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# sync-public-skills

private skill repo（SSOT）から public / EMU private / GIM internal へ、行き先ごとに安全な skill だけを同期する。CLI（`.copilot`、prompt 不可）向けの自己完結 SKILL。VS Code では同名 prompt を使う。

## Scope

- 対象 source: private repo の `.github/skills/<skill>/`（native skill）。`copilot-skills/{skills,m-skills}/` は private inventory とし、public へ同期しない
- 公開先: public skill repo, EMU private repo, GIM internal repo
- 配布（public/private → 実行環境 `~/.copilot`）は Agent Skills Ninja の担当。この SKILL は repo への同期 / 公開だけを扱う

## Environment

- `SYNC_PUBLIC_SKILLS_PRIVATE_REPO`: private repo ルート
- `SYNC_PUBLIC_SKILLS_PUBLIC_REPO`: public repo ルート
- `SYNC_PUBLIC_SKILLS_SCRIPT`: `Sync-AndPush.ps1` のフルパス
- `SYNC_INTERNAL_SKILLS_EMU_REPO`: EMU private repo
- `SYNC_INTERNAL_SKILLS_GIM_REPO`: GIM internal repo
- いずれも Process scope 優先、無ければ User scope で解決する（`[System.Environment]::GetEnvironmentVariable($name,'User')`）

## Mode

- 既定は `safe-auto`: この skill が明示実行された場合に限り、監査 → 行き先別に安全な skill だけ sync → push まで進める
- `review-only` / `dry-run` / `プレビュー` 指定時は、候補・監査・予定差分・commit message を提示して停止する
- `all` 指定時は、`primary` だけでなく private repo の未コミット skill 差分も対象にする（下記 All Mode）

## All Mode（`all` 指定時の dirty 取り込み）

- まず `scripts/Commit-DirtySkills.ps1` をdry-runし、skill contentとNot Doneを確認する。意味・scopeが明確な場合だけ `-Apply`でskill単位にcommitする
- 対象は skill content のみ: `.github/skills/<skill>/**` と `copilot-skills/skills/<skill>/**`。`copilot-skills/m-skills/<skill>/**` は legacy/手動 opt-in 時だけ対象にする。`.skill-meta.json` と shared file（README / assets）は除外する
- `.skill-meta.json` が未追跡で dirty に出たら local-only metadata とみなし、stage せず削除してよい。tracked なら自動削除せず停止する
- skill 以外の dirty（scripts、設定、無関係ファイル、`/memories/**`）はコミットしない。混在すれば stage せず Not Done に列挙する
- 各 dirty skill を skill 単位で個別コミットする（`feat|fix|docs(<skill>): ...`）。複数 skill を 1 コミットに混ぜない
- コミット後に各 skill の public / EMU / GIM 振り分けを監査する。public-safe だけ public へ、internal-only / private-only は EMU/GIM へ振り、public へ漏らさない
- secret / 顧客名 / 個人メール / 具体 TPID / ローカル絶対パスを含む skill は、コミットは可だが public sync から除外する。一般化できないものは EMU/GIM 側も停止して確認する
- 大規模削除、意味変更、scope 不明な差分が混ざる skill は、その skill だけ自動コミットせず停止する

## Gates（公開前に必ず確認）

- public / internal / denied / copilot-deniedの分類SSOTは `scripts/skill-distribution.json`。`publicCopilotSkills` は空を維持し、promptやSKILL本文へ現在の一覧を複製しない
- `dirty` は sync 必要性ではなく、未確定 authoring の gate として扱う。通常 sync の要否は private source path と public / EMU / GIM destination path の content diff で判定する
- 実行前に `Mode / Selected Skills / 選択外の public diff` を示す。対象が明示されていれば `primary-only`、`all` / `broad` なら broad とし、会話の流れだけで primary を推測しない
- primary が明示されている場合、既定の確認範囲は primary とその同期経路に限定する。全 skill 棚卸し、全 duplicate、全 copilot-skills license audit は `all` / `broad` / `audit` / `棚卸し` が明示された場合だけ行う
- private-only / internal-only / MS 社内向け skill は public sync から除外する。社内限定は EMU private repo や GIM internal repo 経路へ逃がす
- `.skill-meta.json` は local-only metadata として、dirty 判定 / stage / push / public diff から除外する
- shared file（`.github/skills/README.md`、`assets/**`、自動生成の `.github/skills/LICENSE`）は skill commit と分離する。broad sync 後に `LICENSE` だけ generated drift が残ったら内容を確認し、意図どおりなら sync/index commit へ分ける
- sync-only 実行中は README / assets / index / SKILL 本文を編集しない
- public safety audit: 想定外の skill 漏れ込みや、想定外の削除が出たら停止して原因を確認する
- branch / remote ambiguity、unexpected deletion、audit failure、content authoring 必要時は停止する
- 手動コピーや一時 sync script を作らず、正式 runner の `Sync-AndPush.ps1` とその scope parameter を使う
- secret / 顧客情報 / 個人メール / 具体 TPID / ローカル絶対パスを public にも EMU にも入れない。例は placeholder にする

## Destination Audits and Gates

Destination 別の判定（公開可否 / 除外リスト / repo visibility / sensitive scan）はこの SKILL が決める。詳細手順と既定リストは [references/instructions/audits-and-gates.md](references/instructions/audits-and-gates.md)。
- **New Skill Classification Gate**: `skill-distribution.json` のpublic / internal / deniedのどこにもない skill がprivate repoにある限りsyncを強制停止する。未分類skillは分類をconfigへ保存してから再実行
- **Agent Discovery Gate**: script の停止に頼らず、実行前に未分類 skill を検出したら必ずユーザーへ分類を確認する。内容から推測して分類せず、明示回答なしに `-AllowUnknownSkills` を使わない
- **Copilot-Skills Private Inventory Gate**: `.copilot` 由来ミラーは license に関係なく public 対象外とし、private repo 内だけに保持する
- **EMU Private Sync Gate**: visibility `PRIVATE`/`INTERNAL` 確認、secret 連を placeholder 化
- **GIM Internal Sync Gate**: org-owned internal へ MS 社内向け skill を集約。既定 internal セット SSOT
- **Incident Recovery**: prevention gate を抜けて public へ漏れた場合の復旧（filter-repo の限界、GitHub Sensitive Data Removal 申請、fork purge、rename vs delete、robocopy move の罠）は references の Incident Recovery 節を参照

## Sync Strategy

- 今回同期する明示 skill を `primary` とする
- primary-only は `Sync-AndPush.ps1 -PrimarySkills <skill-name...>` を使う。選択外 skill、README、LICENSE index、assets、copilot-skills、orphan deletion は変更しない
- 対象 skill が明示されている場合は、その skill の readiness、source/destination diff、漏れ込みだけを先に確認する。既定は `primary-only` とする
- `primary` が clean かつ commit 済みなら、unselected dirty があっても即停止しない。dirty が primary path にある場合は未確定 authoring とみなし、`all` 指定がない限り `retro-private-skills` へ戻す
- private repo が clean で ahead の場合は、sync 前に remote private へ push してよい。private repo が clean かつ remote と同期済みでも、destination と content diff があれば sync 対象にする
- `all` 指定時は unselected dirty を放置せず、All Mode で skill 単位にコミットしてから sync する
- unselected dirty が primary path に無ければ `-PrimarySkills` の scope gate で選択外 path を commit しない。primary path 自体が dirty なら authoring 未確定として停止する
- `primary-only` では他 skill directory の削除、shared file 更新、broad 一括削除ロジックを使わない。public / internal diff が selected primary destination path だけであることを検証する

## Workflow

1. private / public / script、必要なら EMU / GIM repo を解決し、`primary`・branch / remote・ahead/behind・dirty 状態を確認する
2. `primary` の readiness と source/destination content diff を確認し、未分類 skill があれば先にユーザーへ分類確認する。`shared-dirty` / `private-only-dirty` / `unselected-dirty` が public / EMU / GIM sync に漏れるかを判定し、`copilot-skills/` が public に存在しないことを確認する
3. `all` 指定時は、`Commit-DirtySkills.ps1`のdry-run→`-Apply`でskill単位にcommitする。skill以外のdirtyはNot Doneに残し、同期scriptはprivate dirtyを暗黙commitしない
4. safe path を選ぶ
  - primary-only: `Sync-AndPush.ps1 -PrimarySkills <skill-name...> -Message "sync: <skill summary>" -SkipDevPush`
  - broad: `Sync-AndPush.ps1 -Message "sync: <summary>" -SkipDevPush -ExcludeCopilotSkills <監査で確定した除外名>`
   - EMU private: `Sync-AndPush.ps1 -SyncEmu [-EmuDryRun]`
   - GIM internal: `Sync-AndPush.ps1 -SyncInternal [-InternalDryRun]`
5. private repo の current branch を remote へ push し、public / EMU / GIM 各 repo で想定した skill だけが更新されたことを確認する
6. Git の `master = origin/master` だけで完了としない。publicはlocal source/destination hashとremote到達を確認し、GIM/EMUはremote treeのpath集合とblob SHAを確認する。`Missing / Mismatch / Extra = 0`になるまで完了扱いにしない

## Gotchas

- **Formatter drift**: VS Code / editor formatter が既存 markdown table を再整形して意味のない whitespace / column-align 差分を残すことがある。skill authoring commit に混ぜず、`chore(<skill>): normalize table whitespace after formatter run` として **必ず別 commit** で分離する。混ぜると後で revert しづらい
- **Push rejected → rebase**: sync 前後に remote が別セッションで進んでいて `git push` が rejected になる場合、`git pull --rebase origin master` で **`HEAD.lock` rename failure** の無限プロンプト (y/n 応答無効) に陥ることがある。対処: (1) `git rebase --abort` (2) `git reset --hard HEAD` で index / worktree を HEAD に一致させる (3) `Get-ChildItem .git\*.lock -Force | Remove-Item -Force` で残 lock を除去 (4) `git merge --no-ff -m 'merge: ...' origin/master` で rebase を諦めて merge に切替。merge commit 1 個追加のコストで確実に前進できる
- **Cross-cutting git operations**: この 2 点は sync だけでなく `retro-private-skills` / 大 skill 育成の直後にも同じ症状で再発する。skill 側で cross-cutting reminder として持つ
- **Git Data API transient failure**: blob/tree/commit/ref APIは共通retryと空SHA fail-fastを通す。ref更新後にremote treeを再取得し、stale path削除と完全一致を確認する
- **Internal full mirror only**: internal subset指定は未選択Skillを削除し得るため拒否する。distribution configの全集合だけをdesired setとして使う
- **All Mode rollback**: tracked metadata、cross-root rename、commit失敗で停止する。commit途中の失敗は元HEADへ戻し、差分をunstagedで保持する

## Report

- Summary / Primary / Path Chosen / Audit / Private Sync / EMU Private Sync / GIM Internal Sync / Public Sync / Verify / Not Done

