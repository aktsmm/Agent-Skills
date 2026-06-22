---
name: "permission-max"
description: "Microsoft Scout と Copilot CLI/ホスト側の権限確認を減らすため、shell allow list、server/tool autoApprove、CLI 実行確認まわりをユーザー承認付きで最大限広く整える。"
---

# permission-max

目的: Microsoft Scout セッション中に頻出する権限確認を減らすため、Scout 側の shell allow list / read-only auto approve / server autoApprove / tool allow map を最大限広く申請し、さらに Copilot CLI / ホスト側の `Read` / `Write` / `PowerShell command` などの確認が出る場合も診断する。

## 重要な前提

- この Skill はセキュリティ確認を突破しない。必ず現在設定を確認し、変更可能なものだけユーザー承認付きで申請する。
- Scout 側の権限と、Copilot CLI / ホスト側のツール実行確認は別レイヤーとして扱う。
- `Allow everywhere` 相当の完全な無条件許可や、security-sensitive location の警告を消すことは保証しない。警告が残る場合は安全ガードとして扱う。
- パス許可は、Scout が許可する範囲では `D:\*` や `C:\Users\<you>\OneDrive\*` のような親フォルダ/ワイルドカードを優先する。ただし `m_request_permission_escalation` で変更できるのは shell allow list、tool allow map、autoApproveReadOnly、server autoApprove が中心で、パス単位の警告を常に一括変更できるとは限らない。
- `allow` はフル置換なので、必ず現在の allow list を読み、既存項目 + 追加項目の和集合を `string[]` として渡す。既存項目を落とさない。
- CLI / ホスト側の確認を減らす設定が見つからない場合は、「Scout 側は最大化済みだが CLI 側は別ガードで変更不可」と明示する。推測で「完了」と言わない。
- 危険操作、削除、外部送信、M365送信、サインアウト、サービス停止などは、権限が広くてもユーザーの明示指示と確認を優先する。

## 対象レイヤー

| レイヤー | 例 | この Skill でやること |
|---|---|---|
| Scout permissions | `m_get_settings` の `permissions.allow` / `tools` / `servers` | `m_request_permission_escalation` で承認申請 |
| Scout file/server autoApprove | filesystem / shell / playwright / workiq | server autoApprove を有効化申請 |
| Copilot CLI / host tool confirmation | `Read` / `Write` / `Edit` / `PowerShell command` の確認 | 設定場所を調査し、変更可能なら設定。不可なら制限として報告 |
| command allow flags | `copilot -p ... --allow-all-tools` など | サブプロセスの `copilot` 実行時だけ使える補助策として記録 |

## 実行手順 A: Scout 側の最大化

1. `m_get_settings` を呼び、以下を確認する。
   - `permissions.allowModelPermissionsChange`
   - 現在の `permissions.allow`
   - 現在の `permissions.tools`
   - 現在の `permissions.servers`
   - `permissions.autoApproveReadOnly`

2. `permissions.allowModelPermissionsChange` が `false` の場合は停止し、ユーザーに Settings -> Permissions -> "Allow AI to request permission changes" を有効化してから再実行するよう伝える。

3. 現在の `permissions.allow` に、以下の broad allow パターンを追加した重複なし配列を作る。

```text
Add-Type *
Compress-Archive *
Copy-Item *
Expand-Archive *
Format-List *
Format-Table *
Get-ChildItem *
Get-Content *
Get-Item *
Get-Location *
Import-Module *
Invoke-RestMethod *
Invoke-WebRequest *
Join-Path *
Move-Item *
New-Item *
Remove-Item *
Rename-Item *
Resolve-Path *
Select-Object *
Set-Content *
Set-ExecutionPolicy *
Set-Location *
Sort-Object *
Start-Process *
Start-Sleep *
Stop-Process -Id *
Test-Path *
Where-Object *
az *
cmd *
code *
curl *
docker *
dotnet *
gh *
git *
go *
node *
npm *
npx *
pip *
pip3 *
pnpm *
powershell *
pwsh *
py *
py -m *
python *
python -m *
robocopy *
uv *
winget *
yarn *
```

4. `m_request_permission_escalation` を呼び、以下をまとめて申請する。

```json
{
  "allow": ["既存項目", "追加項目"],
  "autoApproveReadOnly": true,
  "servers": {
    "filesystem": { "autoApprove": true },
    "playwright": { "autoApprove": true },
    "shell": { "autoApprove": true },
    "workiq": { "autoApprove": true }
  },
  "tools": {
    "tool:m_get_horizon_actions": true,
    "tool:m_ask_user": true,
    "tool:workiq_email": true,
    "tool:workiq_calendar": true,
    "tool:workiq_onedrive": true,
    "tool:workiq_teams": true,
    "tool:workiq_people": true,
    "tool:workiq_meetings": true,
    "tool:m_memory": true,
    "tool:m_automations": true,
    "tool:m_skills": true,
    "tool:m_settings": true,
    "tool:m_sessions": true,
    "tool:m_models": true,
    "tool:m_heartbeat": true,
    "tool:m_m365_auth": true,
    "tool:m_teams": true,
    "tool:m_recall": true,
    "tool:m_list_memories": true,
    "tool:m_list_automations": true,
    "tool:m_get_automation": true,
    "tool:m_list_skills": true,
    "tool:m_get_skill": true,
    "tool:m_get_settings": true,
    "tool:m_search_sessions": true,
    "tool:m_get_session_transcript": true,
    "tool:m_list_models": true,
    "tool:m_get_current_model": true,
    "tool:m_list_personalities": true,
    "tool:m_get_heartbeat_status": true,
    "tool:m_m365_status": true,
    "tool:m_relay_status": true,
    "tool:m_send_teams_message": true,
    "tool:read": true
  }
}
```

5. 申請後、承認された場合は `m_get_settings` で反映確認し、増えた/有効化された主要項目だけを簡潔に報告する。

## 実行手順 B: Copilot CLI / ホスト側の確認を診断する

Scout 側が最大化済みでも、`Read` / `Write` / `Edit` / `PowerShell command` の確認が出る場合は、次を確認する。

1. まずユーザーに「これは Scout 側ではなく Copilot CLI / ホスト側の別レイヤーかもしれない」と説明する。

2. 既知の設定・候補ファイルを読み取り専用で探す。

```powershell
$candidates = @(
  "$env:USERPROFILE\.copilot",
  "$env:APPDATA\GitHub Copilot",
  "$env:APPDATA\Code\User",
  "$env:LOCALAPPDATA\GitHub Copilot"
)
foreach ($p in $candidates) {
  if (Test-Path -LiteralPath $p) {
    Get-ChildItem -LiteralPath $p -Force -Recurse -Include '*permission*','*settings*.json','*.toml','*.yaml','*.yml' |
      Select-Object FullName,Length,LastWriteTime
  }
}
```

3. `copilot` CLI が使える場合は、現在のCLIで権限関連オプションがあるか確認する。

```powershell
copilot --help
copilot -p "help" --help
```

4. 以下のような設定が見つかった場合のみ、ユーザーへ説明してから編集する。
   - read/write/edit/shell の autoApprove / approval / confirmation 設定
   - workspace trust / tool allowlist 設定
   - current workspace の許可済みツール設定

5. 設定が見つからない、または現在のホストが管理していて変更できない場合は、以下のように報告する。

```text
Scout 側の permission-max は最大化済みです。
ただし Read / Write / PowerShell command の確認は Copilot CLI / ホスト側の別ガードで、現在の設定ファイルからは一括無効化できる項目が見つかりませんでした。
サブプロセスとして copilot を実行する場合だけ `--allow-all-tools` などの CLI オプションを使えますが、この会話中のツール確認には効かない可能性があります。
```

## 実行手順 C: サブプロセス copilot 実行時の補助

現在の会話の `Read` / `Write` / `PowerShell` 確認には効かない場合があるが、PowerShell から `copilot -p` をサブプロセスとして使う場合は、必要に応じて以下を使える。

```powershell
copilot -p "<prompt>" `
  --allow-all-tools `
  --allow-all-urls `
  --silent
```

これはサブプロセスの `copilot` 実行に対する許可であり、Scout や現在ホストされている CLI セッションの内部ツール確認を必ず無効化するものではない。

## 報告方針

- 「Scout 側」「Copilot CLI / ホスト側」を必ず分けて報告する。
- どちらを最大化できたか、どちらが変更不可だったかを明確にする。
- 設定変更をしていないのに「最大化完了」と言わない。
- 読み取り調査だけで終わった場合は「調査結果」として報告する。
