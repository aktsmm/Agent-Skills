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

## Gates（公開前に必ず確認）

- private-only / internal-only / MS 社内向け skill は public sync から除外する。社内限定は EMU private repo や GIM internal repo 経路へ逃がす
- public safety audit: 想定外の skill 漏れ込みや、想定外の削除が出たら停止して原因を確認する
- secret / 顧客情報 / 個人メール / 具体 TPID / ローカル絶対パスを public にも EMU にも入れない。例は placeholder にする

## Copilot-Skills Public Audit（license / DUP / secret）

`copilot-skills/`（`.copilot` 由来ミラー）を public へ出す前に、skill 単位で 3 観点を監査し、除外対象を `Sync-AndPush.ps1 -ExcludeCopilotSkills` に渡す。判断は毎回ここで行い、script にハードコードしない。

- ①ライセンス: 第三者 Proprietary は除外。Anthropic / Microsoft Scout ビルトイン（`docx` / `pptx` / `xlsx` 等、LICENSE.txt が複製・派生・サービス外保持を禁止）は public 不可。LICENSE 不明（`expense-report` / `receipt-ocr` / `loop` / `excalidraw` 等）は安全側で除外。Apache 2.0 等の再配布可ライセンス（`web-artifacts-builder` 等）は LICENSE / NOTICE を保持して公開可
- ②DUP: 同名 skill が private repo `.github/skills/<skill>/` にある場合は、そちらを正として copilot-skills 側を public から除外する（二重公開防止）
- ③機密: ユーザー名、ローカル絶対パス、Tenant ID、顧客名、個人メールを含む skill は、一般化できないなら除外する。一般化済みの自作 skill（`export-session-log` / `m365-copilot-research` / `retro-private-skills` / `permission-max` 等）は公開可
- 既定ブラックリスト例: `docx,pptx,xlsx,expense-report,receipt-ocr,loop,excalidraw`（①②）＋ `.github/skills` と重複する skill（②）。新規 skill が増えたら上 3 観点で再判定してリストを更新する
- ブラックリストは `ExcludeSkills` 方式の踏襲。script は受け取った名前を機械的に除外するだけで、公開可否の判断はしない

## Internal Sync Defaults

- 既定 internal セット（EMU / GIM 共通 SSOT）: `c360-operations`, `d365-expense-sorter`, `m365-copilot-research`, `esxp-labor-entry`
- `Sync-AndPush.ps1 -SyncEmu` は上記セットを EMU private repo へ mirror する
- `Sync-AndPush.ps1 -SyncInternal` は上記セットを GIM internal repo へ mirror する

## Workflow

1. private repo の status を確認し、未コミット差分が public へ意図せず混ざらないか見る
2. readiness を監査し、`shared-dirty` / `private-only-dirty` / `unselected-dirty` が public / EMU / GIM sync に漏れるかを判定する。`copilot-skills/` を含む場合は上の 3 観点でブラックリストを確定する
3. safe path を選ぶ
   - 直接実行: 漏れ込みが無い場合は `Sync-AndPush.ps1 -Message "sync: <skill summary>" -SkipDevPush -ExcludeCopilotSkills <監査で確定した除外名>`
   - EMU private: `Sync-AndPush.ps1 -SyncEmu [-EmuDryRun]`
   - GIM internal: `Sync-AndPush.ps1 -SyncInternal [-InternalDryRun]`
4. push 後、public / EMU / GIM 各 repo で想定した skill だけが更新されたことを確認する

## Notes

- `Sync-AndPush.ps1` は機械適用のみ。除外は `-ExcludeSkills`（native）/ `-ExcludeCopilotSkills`（copilot-skills）で渡し、internal mirror は `-SyncEmu` / `-SyncInternal` を明示する
- push は明示実行のときだけ。判断はこの SKILL（と同名 prompt）が持つ
