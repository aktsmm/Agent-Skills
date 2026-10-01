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
- Explicit requests approve their named scope and known destinations. Display remotes/visibility; confirm new or unclear destinations, visibility/privileges, destructive deletion or sensitive decisions. "All" adds no destinations.
- EMU/GIM require an explicit destination request and their sync flags; known configuration alone is not approval. Safe-auto all includes confirming/pushing its own allowed intake commits to the verified private origin before distribution, never unrelated queued commits.
- `all` 指定時は、`primary` だけでなく private repo の未コミット skill 差分も対象にする（下記 All Mode）

## All Mode（`all` 指定時の dirty 取り込み）

- まず `scripts/Commit-DirtySkills.ps1` をdry-runし、skill contentとNot Doneを確認する。意味・scopeが明確な場合だけ `-Apply`でskill単位にcommitする
- 対象は skill content のみ: `.github/skills/<skill>/**` と `copilot-skills/skills/<skill>/**`。`copilot-skills/m-skills/<skill>/**` は legacy/手動 opt-in 時だけ対象にする。`.skill-meta.json` と shared file（README / assets）は除外する
- `.skill-meta.json` が未追跡で dirty に出たら local-only metadata とみなし、stage せず削除してよい。tracked なら自動削除せず停止する
- skill 以外の dirty（scripts、設定、無関係ファイル、`/memories/**`）はコミットしない。混在すれば stage せず Not Done に列挙する
- Commit by owning skill; group its related small edits and relevant formatting together. Never mix unrelated skills, shared files or other dirty paths, and do not require separate pushes for one bounded improvement.
- コミット後に各 skill の public / EMU / GIM 振り分けを監査する。public-safe だけ public へ、internal-only / private-only は EMU/GIM へ振り、public へ漏らさない
- secret / 顧客名 / 個人メール / 具体 TPID / ローカル絶対パスを含む skill は、コミットは可だが public sync から除外する。一般化できないものは EMU/GIM 側も停止して確認する
- Hold only the affected skill when scope is unclear, deletion is destructive, or privileges/publication/default behavior change; bounded authoring within approved scope needs no repeated approval.

## Gates（公開前に必ず確認）

- public / internal / denied / copilot-deniedの分類SSOTは `scripts/skill-distribution.json`。`publicCopilotSkills` は空を維持し、promptやSKILL本文へ現在の一覧を複製しない
- `dirty` は sync 必要性ではなく、未確定 authoring の gate として扱う。通常 sync の要否は private source path と public / EMU / GIM destination path の content diff で判定する。content diff は **tracked file を基準**にし、raw な filesystem hash 比較だけで判断しない。両 repo で untracked な build 生成物（`__pycache__/*.pyc` 等）が phantom diff として出て、pending 集合が実際の倍近くに見える。候補が出たら `git ls-files` で tracked かどうかを確認してから対象に含める
- 実行前に `Mode / Selected Skills / 選択外の public diff` を示す。対象が明示されていれば `primary-only`、`all` / `broad` なら broad とし、会話の流れだけで primary を推測しない
- primary が明示されている場合、既定の確認範囲は primary とその同期経路に限定する。全 skill 棚卸し、全 duplicate、全 copilot-skills license audit は `all` / `broad` / `audit` / `棚卸し` が明示された場合だけ行う
- private-only / internal-only / MS 社内向け skill は public sync から除外する。社内限定は EMU private repo や GIM internal repo 経路へ逃がす
- `.skill-meta.json` は local-only metadata として、dirty 判定 / stage / push / public diff から除外する
- shared file（`.github/skills/README.md`、`assets/**`、自動生成の `.github/skills/LICENSE`）は skill commit と分離する。broad sync 後に `LICENSE` だけ generated drift が残ったら内容を確認し、意図どおりなら sync/index commit へ分ける
- sync-only 実行中は README / assets / index / SKILL 本文を編集しない
- public safety audit: 想定外の skill 漏れ込みや、想定外の削除が出たら停止して原因を確認する
- Stop for ambiguous remotes, unconfirmed selected content, unexpected deletion or audit failure. Complete explicitly authorized all-mode intake/private push before distribution; snapshot primary-only rejects selected dirty/unpushed content. Preserve unrelated dirty; broad/all retains branch/clean/current/classification.
- 手動コピーや一時 sync script を作らず、正式 runner の `Sync-AndPush.ps1` とその scope parameter を使う
- secret / 顧客情報 / 個人メール / 具体 TPID / ローカル絶対パスを public にも EMU にも入れない。例は placeholder にする

## Destination Audits and Gates

Destination 別の判定（公開可否 / 除外リスト / repo visibility / sensitive scan）はこの SKILL が決める。詳細手順と既定リストは [references/instructions/audits-and-gates.md](references/instructions/audits-and-gates.md)。
- **Runner capability gate**: relaxed primary-only requires committed audited-SHA/origin, same-SHA policy, scoped audits, source preservation and public tree/scope checks. Local drafts are not support. Otherwise use no new flags/relaxation and hand off the update; legacy broad may retain its existing full gates.
- **New Skill Classification Gate**: with that runner, primary-only audits selected skills and defers unselected dirty/unknowns without copying them; broad/all retains whole-repo classification. Legacy runners retain their existing stop conditions.
- **Agent Discovery Gate**: ask classification only for an unknown selected skill. Never infer public permission or use `-AllowUnknownSkills` as a bypass. "Not this run" excludes that skill temporarily; it is neither permanent deny nor publication approval.
- **Copilot-Skills Private Inventory Gate**: `.copilot` 由来ミラーは license に関係なく public 対象外とし、private repo 内だけに保持する
- **EMU Private Sync Gate**: visibility `PRIVATE`/`INTERNAL` 確認、secret 連を placeholder 化
- **GIM Internal Sync Gate**: org-owned internal へ MS 社内向け skill を集約。既定 internal セット SSOT
- **Incident Recovery**: prevention gate を抜けて public へ漏れた場合の復旧（filter-repo の限界、GitHub Sensitive Data Removal 申請、fork purge、rename vs delete、robocopy move の罠）は references の Incident Recovery 節を参照

## Sync Strategy

- 今回同期する明示 skill を `primary` とする
- Capable primary-only pins selected native content/config with `-PrimarySkills`, `-SourceCommit`, `-ExpectedSourceOrigin`; unselected/shared/inventory/orphan paths remain untouched.
- 対象 skill が明示されている場合は、その skill の readiness、source/destination diff、漏れ込みだけを先に確認する。既定は `primary-only` とする
- Capability-verified snapshots reject selected/config dirty or unpushed commits, but allow detached/behind original sources with unrelated dirty. Legacy primary/broad retains master/clean/current gates; never apply snapshot exceptions to it.
- Review the whole ahead range before a separate authorized private push; integrate divergence before push and refresh pins. Read-only primary never pushes private authoring; zero committed diff means no sync.
- `all` 指定時は unselected dirty を放置せず、All Mode で skill 単位にコミットしてから sync する
- For capability-verified primary-only, audit/pin remote blobs/config, re-audit after advancement, and use matching code from a clean audited checkout when needed; temporarily redirect Process source env and restore finally. Legacy cannot promise SHA-bound execution and must not simulate it.
- `primary-only` では他 skill directory の削除、shared file 更新、broad 一括削除ロジックを使わない。public / internal diff が selected primary destination path だけであることを検証する
- Capability-verified primary-only requires pre-push public index/commit identity and whole-commit literal scope after exclusions. Reject transformation/leakage without retrying. Legacy keeps its existing verification but is insufficient for this new pre-push guarantee; use the update handoff when that guarantee is required.

## Workflow

1. private / public / script、必要なら EMU / GIM repo を解決し、`primary`・branch / remote・ahead/behind・dirty 状態を確認する
2. Check capabilities and selected readiness/classification/content diff. Only capable primary-only defers unselected authoring; legacy/broad/all retains full stop gates. Never skip selected license, secret, deletion or mirror checks.
3. `all` 指定時は、`Commit-DirtySkills.ps1`のdry-run→`-Apply`でskill単位にcommitする。skill以外のdirtyはNot Doneに残し、同期scriptはprivate dirtyを暗黙commitしない
  - In safe-auto all, verify private origin/visibility and the entire ahead range, isolate unrelated dirty, integrate behind/divergence, validate and push only the authorized intake commits before sync. If isolation or scope cannot be established, stop that pre-step; never let `-SkipDevPush` hide pending commits.
  - Legacy/broad distribution must execute from a verified clean/current checkout with its Process source env temporarily aligned and restored afterward; otherwise hold distribution, not unrelated authoring.
4. safe path を選ぶ
  - legacy primary-only: retain the old gates or hand off the runner update when relaxed behavior is required; never substitute broad to bypass a selected-scope stop.
  - capability-verified primary-only: `Sync-AndPush.ps1 -PrimarySkills <skill-name...> -SourceCommit <audited-full-sha> -ExpectedSourceOrigin <approved-origin-url> -Message "sync: <skill summary>" -SkipDevPush`
  - broad: `Sync-AndPush.ps1 -Message "sync: <summary>" -SkipDevPush -ExcludeCopilotSkills <監査で確定した除外名>`
   - EMU private: `Sync-AndPush.ps1 -SyncEmu [-EmuDryRun]`
   - GIM internal: `Sync-AndPush.ps1 -SyncInternal [-InternalDryRun]`
5. Confirm only the approved destination set changed. Primary-only never pushes private source; any separately requested private push must have a scoped ahead range, clean execution checkout and integrated remote updates.
6. Git の `master = origin/master` だけで完了としない。publicはlocal source/destination hashとremote到達を確認し、GIM/EMUはremote treeのpath集合とblob SHAを確認する。`Missing / Mismatch / Extra = 0`になるまで完了扱いにしない

## Gotchas

- **Formatter drift**: relevant alignment belongs with the owning skill's bounded change; unrelated whitespace drift is a separate normalization change after verification. Do not blanket-stage other authoring or require a separate commit for every formatting line.
- **Push rejected / divergence**: push前にfetchしてahead/behindを再計算する。双方にcommitがあれば変更pathの重複を調べ、競合がなければnormal mergeで同期する。stale tracking refのままrebaseやpushへ進まない
- **`HEAD.lock` rename failure**: 同じ失敗が2回続いたら`n`で停止し、HEAD・status・diff・rebase metadata・lock所有を確認する。未commit変更を保護し、`reset --hard`やlock一括削除はしない。HEADが不変でindex/worktreeだけがfetched remoteと一致すると証明できる場合だけ対象をHEADへ戻し、HEADをdetachしないverified mergeへ切り替える
- **Git Data API transient failure**: blob/tree/commit/ref APIは共通retryと空SHA fail-fastを通す。ref更新後にremote treeを再取得し、stale path削除と完全一致を確認する
- **Internal full mirror only**: internal subset指定は未選択Skillを削除し得るため拒否する。distribution configの全集合だけをdesired setとして使う
- **Skill rename**: フォルダ名と `name`、distribution config、README / LICENSE index を同じ変更で揃え、旧フォルダを消す broad sync で反映する（primary-only は旧フォルダを消さない）。配布先でインストール済みの旧名コピーは更新で解決できず保留・要修復になり得るため、完了報告で新名の再インストールと旧フォルダ削除を案内する
- **All Mode rollback**: tracked metadata、cross-root rename、commit失敗で停止する。commit途中の失敗は元HEADへ戻し、差分をunstagedで保持する

## Report

- Summary / Primary / Path Chosen / Audit / Private Sync / EMU / GIM / Public Sync / Verify / Not Done / Next Suggestions
- List up to three read-only candidates from Git state/committed differences: dirty -> Retro; pending -> private range review; public-safe gap -> separately requested sync. Honor holds/visibility; no unknown/private/internal/denied public proposals, extra mutations or unsolicited full audits.

