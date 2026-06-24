---
name: sync-public-skills
description: Sync curated skills from the private skill repo to public, EMU private, and GIM internal repos, then push or mirror as needed. Use when publishing/updating public skills, syncing private→public, or running internal/private skill sync for EMU and GIM. Audits license, duplication, visibility, and secrets before publishing. Triggers on "sync public skills", "publish skills", "public 公開", "private を public に同期", "EMU internal skill sync", "GIM internal skill sync".
argument-hint: "対象 skill 名、private/public/EMU/GIM repo path（任意）、mode（safe-auto / review-only / dry-run / all）"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# sync-public-skills

private skill repo（SSOT）から public / EMU private / GIM internal へ、行き先ごとに安全な skill だけを同期する。CLI（`.copilot`、prompt 不可）向けの自己完結 SKILL。VS Code では同名 prompt を使う。

## Scope

- 対象 source: private repo の `.github/skills/<skill>/`（native skill）と `copilot-skills/skills/<skill>/`（`.copilot` 由来ミラー）。`copilot-skills/m-skills/<skill>/` は legacy/手動 opt-in として、明示時だけ扱う
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

- 対象は skill content のみ: `.github/skills/<skill>/**` と `copilot-skills/skills/<skill>/**`。`copilot-skills/m-skills/<skill>/**` は legacy/手動 opt-in 時だけ対象にする。`.skill-meta.json` と shared file（README / assets）は除外する
- `.skill-meta.json` が未追跡で dirty に出たら local-only metadata とみなし、stage せず削除してよい。tracked なら自動削除せず停止する
- skill 以外の dirty（scripts、設定、無関係ファイル、`/memories/**`）はコミットしない。混在すれば stage せず Not Done に列挙する
- 各 dirty skill を skill 単位で個別コミットする（`feat|fix|docs(<skill>): ...`）。複数 skill を 1 コミットに混ぜない
- コミット後に各 skill の public / EMU / GIM 振り分けを監査する。public-safe だけ public へ、internal-only / private-only は EMU/GIM へ振り、public へ漏らさない
- secret / 顧客名 / 個人メール / 具体 TPID / ローカル絶対パスを含む skill は、コミットは可だが public sync から除外する。一般化できないものは EMU/GIM 側も停止して確認する
- 大規模削除、意味変更、scope 不明な差分が混ざる skill は、その skill だけ自動コミットせず停止する

## Gates（公開前に必ず確認）

- `dirty` は sync 必要性ではなく、未確定 authoring の gate として扱う。通常 sync の要否は private source path と public / EMU / GIM destination path の content diff で判定する
- primary が明示されている場合、既定の確認範囲は primary とその同期経路に限定する。全 skill 棚卸し、全 duplicate、全 copilot-skills license audit は `all` / `broad` / `audit` / `棚卸し` が明示された場合だけ行う
- private-only / internal-only / MS 社内向け skill は public sync から除外する。社内限定は EMU private repo や GIM internal repo 経路へ逃がす
- `.skill-meta.json` は local-only metadata として、dirty 判定 / stage / push / public diff から除外する
- shared file（`.github/skills/README.md`、`assets/**`、自動生成の `.github/skills/LICENSE`）は skill commit と分離する。broad sync 後に `LICENSE` だけ generated drift が残ったら内容を確認し、意図どおりなら sync/index commit へ分ける
- sync-only 実行中は README / assets / index / SKILL 本文を編集しない
- public safety audit: 想定外の skill 漏れ込みや、想定外の削除が出たら停止して原因を確認する
- branch / remote ambiguity、unexpected deletion、audit failure、content authoring 必要時は停止する
- 手動コピーで public / EMU repo を直接触らず、script（または一時 script variant）で完結させる
- secret / 顧客情報 / 個人メール / 具体 TPID / ローカル絶対パスを public にも EMU にも入れない。例は placeholder にする

## Destination Audits and Gates

Destination 別の判定（公開可否 / 除外リスト / repo visibility / sensitive scan）はこの SKILL が決める。詳細手順と既定リストは [references/instructions/audits-and-gates.md](references/instructions/audits-and-gates.md)。
- **New Skill Classification Gate**: `$KnownPublicSkills` / `$DefaultInternalSkills` / `$HardDeniedSkills` のどこにもない skill が private repo にある限り sync を強制停止する（`Sync-AndPush.ps1` の Step 0.5、incident 2026-06-24 の再発防止）。未分類 skill は public-safe / internal-only / public-denied へ分類してから再実行
- **Copilot-Skills Public Audit**: license / DUP / secret の 3 観点で broad sync 除外を確定
- **EMU Private Sync Gate**: visibility `PRIVATE`/`INTERNAL` 確認、secret 連を placeholder 化
- **GIM Internal Sync Gate**: org-owned internal へ MS 社内向け skill を集約。既定 internal セット SSOT
- **Incident Recovery**: prevention gate を抜けて public へ漏れた場合の復旧（filter-repo の限界、GitHub Sensitive Data Removal 申請、fork purge、rename vs delete、robocopy move の罠）は references の Incident Recovery 節を参照

## Sync Strategy

- 今回同期する明示 skill を `primary` とする
- 対象 skill が明示されている場合は、その skill の readiness、source/destination diff、漏れ込みだけを先に確認する。既定は `primary-only` とする
- `primary` が clean かつ commit 済みなら、unselected dirty があっても即停止しない。dirty が primary path にある場合は未確定 authoring とみなし、`all` 指定がない限り `retro-private-skills` へ戻す
- private repo が clean で ahead の場合は、sync 前に remote private へ push してよい。private repo が clean かつ remote と同期済みでも、destination と content diff があれば sync 対象にする
- `all` 指定時は unselected dirty を放置せず、All Mode で skill 単位にコミットしてから sync する
- unselected dirty が public sync に漏れ得る場合は、main repo で直接実行せず isolated path を使う
- isolated path: current HEAD の一時 clean worktree（同等の clean source）で public repo の `<primary>/` だけを更新する
- `primary-only` では他 skill directory の削除、shared file 更新、broad 一括削除ロジックを使わない。public / internal diff が selected primary destination path だけであることを検証する

## Workflow

1. private / public / script、必要なら EMU / GIM repo を解決し、`primary`・branch / remote・ahead/behind・dirty 状態を確認する
2. `primary` の readiness と source/destination content diff を確認し、`shared-dirty` / `private-only-dirty` / `unselected-dirty` が public / EMU / GIM sync に漏れるかを判定する。broad sync で `copilot-skills/` を含む場合だけ Public Audit の 3 観点でブラックリストを確定する
3. `all` 指定時は、All Mode に従い未コミットの skill 差分を skill 単位でコミットする（skill 以外の dirty は除外し Not Done へ回す）。コミット後に各 skill の public / EMU / GIM 振り分けを監査する
4. safe path を選ぶ
   - 直接実行: 漏れ込みが無い場合は `Sync-AndPush.ps1 -Message "sync: <skill summary>" -SkipDevPush -ExcludeCopilotSkills <監査で確定した除外名>`
   - isolated 実行: current HEAD の clean source で public repo の `<primary>/` だけを mirror する
   - EMU private: `Sync-AndPush.ps1 -SyncEmu [-EmuDryRun]`
   - GIM internal: `Sync-AndPush.ps1 -SyncInternal [-InternalDryRun]`
5. private repo の current branch を remote へ push し、public / EMU / GIM 各 repo で想定した skill だけが更新されたことを確認する

## Report

- Summary / Primary / Path Chosen / Audit / Private Sync / EMU Private Sync / GIM Internal Sync / Public Sync / Verify / Not Done

