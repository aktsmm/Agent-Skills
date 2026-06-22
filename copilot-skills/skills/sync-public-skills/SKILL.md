---
name: sync-public-skills
description: Sync curated skills from the private skill repo to public, EMU private, and GIM internal repos, then push or mirror as needed. Use when publishing/updating public skills, syncing private→public, or running internal/private skill sync for EMU and GIM. Audits license, duplication, visibility, and secrets before publishing. Triggers on "sync public skills", "publish skills", "public 公開", "private を public に同期", "EMU internal skill sync", "GIM internal skill sync".
user-invocable: true
license: CC BY-NC-SA 4.0
---

# sync-public-skills

private skill repo（SSOT）から public / EMU private / GIM internal へ、行き先ごとに安全な skill だけを同期する。CLI（`.copilot`、prompt 不可）向けの自己完結 SKILL。VS Code では同名 prompt を使う。

## Scope

- 対象 source: private repo の `.github/skills/<skill>/`（native skill）と `copilot-skills/{skills,m-skills}/`（`.copilot` 由来ミラー）
- 公開先: public skill repo, EMU private repo, GIM internal repo
- 配布（public/private → 実行環境 `~/.copilot`）は Agent Skills Ninja の担当。この SKILL は public 公開のみを扱う

## Environment

- `SYNC_PUBLIC_SKILLS_PRIVATE_REPO`: private repo ルート
- `SYNC_PUBLIC_SKILLS_PUBLIC_REPO`: public repo ルート
- `SYNC_PUBLIC_SKILLS_SCRIPT`: `Sync-AndPush.ps1` のフルパス
- `SYNC_INTERNAL_SKILLS_EMU_REPO`: EMU private repo
- `SYNC_INTERNAL_SKILLS_GIM_REPO`: GIM internal repo
- いずれも Process scope 優先、無ければ User scope で解決する（`[System.Environment]::GetEnvironmentVariable($name,'User')`）

## Mode

- 既定は `safe-auto`: 監査 → 行き先別に安全な skill だけ sync → push
- `review-only` / `dry-run` / `プレビュー` 指定時は、候補・監査・予定差分・commit message を提示して停止する
- `all` 指定時は、`primary` だけでなく private repo の未コミット skill 差分も対象にする（下記 All Mode）

## All Mode（`all` 指定時の dirty 取り込み）

- 対象は skill content のみ: `.github/skills/<skill>/**` と `copilot-skills/{skills,m-skills}/<skill>/**`。`.skill-meta.json` と shared file（README / assets）は除外する
- `.skill-meta.json` が未追跡で dirty に出たら local-only metadata とみなし、stage せず削除してよい。tracked なら自動削除せず停止する
- skill 以外の dirty（scripts、設定、無関係ファイル、`/memories/**`）はコミットしない。混在すれば stage せず Not Done に列挙する
- 各 dirty skill を skill 単位で個別コミットする（`feat|fix|docs(<skill>): ...`）。複数 skill を 1 コミットに混ぜない
- コミット後に各 skill の public / EMU / GIM 振り分けを監査する。public-safe だけ public へ、internal-only / private-only は EMU/GIM へ振り、public へ漏らさない
- secret / 顧客名 / 個人メール / 具体 TPID / ローカル絶対パスを含む skill は、コミットは可だが public sync から除外する。一般化できないものは EMU/GIM 側も停止して確認する
- 大規模削除、意味変更、scope 不明な差分が混ざる skill は、その skill だけ自動コミットせず停止する

## Gates（公開前に必ず確認）

- private-only / internal-only / MS 社内向け skill は public sync から除外する。社内限定は EMU private repo や GIM internal repo 経路へ逃がす
- `.skill-meta.json` は local-only metadata として、dirty 判定 / stage / push / public diff から除外する
- shared file（`.github/skills/README.md`、`assets/**`、自動生成の `.github/skills/LICENSE`）は skill commit と分離する。broad sync 後に `LICENSE` だけ generated drift が残ったら内容を確認し、意図どおりなら sync/index commit へ分ける
- sync-only 実行中は README / assets / index / SKILL 本文を編集しない
- public safety audit: 想定外の skill 漏れ込みや、想定外の削除が出たら停止して原因を確認する
- branch / remote ambiguity、unexpected deletion、audit failure、content authoring 必要時は停止する
- 手動コピーで public / EMU repo を直接触らず、script（または一時 script variant）で完結させる
- secret / 顧客情報 / 個人メール / 具体 TPID / ローカル絶対パスを public にも EMU にも入れない。例は placeholder にする

## Copilot-Skills Public Audit（license / DUP / secret）

`copilot-skills/`（`.copilot` 由来ミラー）を public へ出す前に、skill 単位で 3 観点を監査し、除外対象を `Sync-AndPush.ps1 -ExcludeCopilotSkills` に渡す。判断は毎回ここで行い、script にハードコードしない。

- ①ライセンス: 第三者 Proprietary は除外。Anthropic / Microsoft Scout ビルトイン（`docx` / `pptx` / `xlsx` 等、LICENSE.txt が複製・派生・サービス外保持を禁止）は public 不可。LICENSE 不明（`expense-report` / `receipt-ocr` / `loop` / `excalidraw` 等）は安全側で除外。Apache 2.0 等の再配布可ライセンス（`web-artifacts-builder` 等）は LICENSE / NOTICE を保持して公開可
- ②DUP: 同名 skill が private repo `.github/skills/<skill>/` にある場合は、そちらを正として copilot-skills 側を public から除外する（二重公開防止）
- ③機密: ユーザー名、ローカル絶対パス、Tenant ID、顧客名、個人メールを含む skill は、一般化できないなら除外する。一般化済みの自作 skill（`export-session-log` / `m365-copilot-research` / `retro-private-skills` / `permission-max` 等）は公開可
- 既定ブラックリスト例: `docx,pptx,xlsx,expense-report,receipt-ocr,loop,excalidraw`（①②）＋ `.github/skills` と重複する skill（②）。新規 skill が増えたら上 3 観点で再判定してリストを更新する
- `Sync-AndPush.ps1` は hard denylist（native: `c360-operations` / `excel-plus`、copilot: 上記ビルトイン 7 件）を引数に関わらず常に除外する。ここで確定する除外名は、それに上乗せする判断分だけ渡す

## EMU Private Sync Gate

- 行き先は user-owned private repo（`SYNC_INTERNAL_SKILLS_EMU_REPO`）。既定セットは GIM internal と同じ `InternalSkills`
- EMU repo の visibility が `PRIVATE` または `INTERNAL` であることを確認する。`PUBLIC` なら停止する
- user-owned private は EMU 全員に自動公開されない。全員利用が要件なら org-owned internal（GIM）が必要で、作成可否を確認する
- EMU sync 先にも secret / 顧客情報 / 個人メール / 具体 TPID / ローカル絶対パスを入れない。例は placeholder にする
- `gh` で pull/push 権限が確認できるのに `git clone` が `Repository not found` になる場合は、repo 不在ではなく Git credential transport の不一致として扱い、clone に固執せず Contents / Git Data API で更新する

## GIM Internal Sync Gate

org-owned internal repo（既定 `gim-home/yamapan-skills`）へ MS 社内向け skill を集約するゲート。`Sync-InternalSkills.ps1` が実装を担うが、「どれを internal へ出すか」は毎回ここで判断する。

- 既定 internal セット（SSOT）: `c360-operations`, `d365-expense-sorter`, `m365-copilot-research`, `esxp-labor-entry`。新規 skill は下 3 観点で再判定して追加する
- 判定 3 観点: ①社内専用（public 不可だが社内なら有益）②対象ロールまたは全社員に有益 ③匿名化済み（顧客実名 / TPID 実値 / 個人メール / ローカル絶対パスなし）
- internal repo の visibility が `INTERNAL` または `PRIVATE` であることを確認する。`PUBLIC` なら停止する
- internal skill は public sync の `ExcludeSkills` / `ExcludeCopilotSkills` に残し、public へ漏れないことを確認する（internal リストと public 除外リストは別管理）
- README は script が各 SKILL.md の `description` + audience map から自動生成する。手書き編集しない
- push 前に sensitive scan を実行する（script がヒットで停止）。誤検知確認済みのときだけ `-AllowSensitive`
- script は `finally` で `RestoreAccount`（既定 `aktsmm`）へ復帰する。実行後に active アカウントを確認する

## Sync Strategy

- 今回同期する明示 skill を `primary` とする
- `primary` が clean かつ commit 済みなら、unselected dirty があっても即停止しない
- `all` 指定時は unselected dirty を放置せず、All Mode で skill 単位にコミットしてから sync する
- unselected dirty が public sync に漏れ得る場合は、main repo で直接実行せず isolated path を使う
- isolated path: current HEAD の一時 clean worktree（同等の clean source）で public repo の `<primary>/` だけを更新する
- `primary-only` では他 skill directory の削除、shared file 更新、broad 一括削除ロジックを使わない

## Workflow

1. private / public / script、必要なら EMU / GIM repo を解決し、`primary`・branch / remote・local commits・dirty 状態を確認する
2. readiness を監査し、`shared-dirty` / `private-only-dirty` / `unselected-dirty` が public / EMU / GIM sync に漏れるかを判定する。`copilot-skills/` を含む場合は Public Audit の 3 観点でブラックリストを確定する
3. `all` 指定時は、All Mode に従い未コミットの skill 差分を skill 単位でコミットする（skill 以外の dirty は除外し Not Done へ回す）。コミット後に各 skill の public / EMU / GIM 振り分けを監査する
4. safe path を選ぶ
   - 直接実行: 漏れ込みが無い場合は `Sync-AndPush.ps1 -Message "sync: <skill summary>" -SkipDevPush -ExcludeCopilotSkills <監査で確定した除外名>`
   - isolated 実行: current HEAD の clean source で public repo の `<primary>/` だけを mirror する
   - EMU private: `Sync-AndPush.ps1 -SyncEmu [-EmuDryRun]`
   - GIM internal: `Sync-AndPush.ps1 -SyncInternal [-InternalDryRun]`
5. private repo の current branch を remote へ push し、public / EMU / GIM 各 repo で想定した skill だけが更新されたことを確認する

## Report

- Summary / Primary / Path Chosen / Audit / Private Sync / EMU Private Sync / GIM Internal Sync / Public Sync / Verify / Not Done

## Notes

- `Sync-AndPush.ps1` は機械適用のみ。除外は `-ExcludeSkills`（native）/ `-ExcludeCopilotSkills`（copilot-skills）で渡し、internal mirror は `-SyncEmu` / `-SyncInternal`（`-EmuDryRun` / `-InternalDryRun` で preview）を明示する
- 公開可否・internal 振り分けの判断はこの SKILL（と同名 prompt）が持つ。script は受け取ったリストを機械適用するだけ
- push は明示実行のときだけ。VS Code では同名 prompt を使う
