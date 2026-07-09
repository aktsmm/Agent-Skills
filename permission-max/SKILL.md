---
name: "permission-max"
description: "Reduce repeated permission prompts across Microsoft Scout, Copilot CLI, and host tool confirmations with user-approved settings and explicit before/after verification. Use when users ask for permission max, fewer approval prompts, shell allow-list expansion, autoApprove, or diagnosis of repeated Read/Write/PowerShell confirmations."
argument-hint: "権限確認を減らしたい実行環境、Scout/Copilot CLI/ホスト側の症状"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# permission-max

目的: Microsoft Scout セッション中に頻出する権限確認を減らすため、Scout 側の shell allow list / read-only auto approve / server autoApprove / tool allow map を最大限広く申請し、さらに Copilot CLI / ホスト側の `Read` / `Write` / `PowerShell command` などの確認が出る場合も診断する。

## When to Use

- 「permission max」「権限確認を減らしたい」「shell allow list を広げたい」
- Scout の server/tool `autoApprove` を確認・拡張したい
- `Read` / `Write` / `Edit` / `PowerShell command` の確認が繰り返され、Scout と CLI / host のどちらが制御しているか切り分けたい
- 別プロセスの `copilot -p` で利用可能な allow flags を確認したい

## 重要な前提

- この Skill はセキュリティ確認を突破しない。必ず現在設定を確認し、変更可能なものだけユーザー承認付きで申請する。
- Scout 側の権限と、Copilot CLI / ホスト側のツール実行確認は別レイヤーとして扱う。
- `Allow everywhere` 相当の完全な無条件許可や、security-sensitive location の警告を消すことは保証しない。警告が残る場合は安全ガードとして扱う。
- パス許可は、Scout が許可する範囲では `<allowed-root>\*` のような確認済み親フォルダ/ワイルドカードを優先する。ただし `m_request_permission_escalation` で変更できるのは shell allow list、tool allow map、autoApproveReadOnly、server autoApprove が中心で、パス単位の警告を常に一括変更できるとは限らない。
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

3. [Scout permission profile](references/scout-permission-profile.md) を読み、現在の allow list と要求パターンの重複なし union を作る。`allow` は full replacement なので、既存項目を落とさない。

4. 現在の環境に存在する server/tool ID だけを含む escalation payload を作り、ユーザー承認付きで `m_request_permission_escalation` を呼ぶ。

5. 申請後に `m_get_settings` を再実行し、配列順を無視して `added` / `preserved` / `removed` / `not-approved` に分類する。`removed` が 1 件でもあれば成功扱いにしない。

## 実行手順 B: Copilot CLI / ホスト側の確認を診断する

Scout 側が最大化済みでも、`Read` / `Write` / `Edit` / `PowerShell command` の確認が出る場合は、次を確認する。

1. まずユーザーに「これは Scout 側ではなく Copilot CLI / ホスト側の別レイヤーかもしれない」と説明する。

2. [Copilot CLI and host diagnostics](references/host-cli-diagnostics.md) に従って、候補設定と現在の CLI help を読み取り専用で調査する。

3. 対応する approval / confirmation / workspace trust / tool allow-list 設定が見つかった場合だけ、ユーザーへ範囲を説明してから編集する。

4. 設定が見つからない、または host 管理で変更できない場合は、その制限と subprocess flags の適用範囲を分けて報告する。

## 実行手順 C: サブプロセス copilot 実行時の補助

現在の会話の確認には効かない場合がある。利用可能な flags と適用範囲は [Copilot CLI and host diagnostics](references/host-cli-diagnostics.md) で現在の CLI help と照合する。

## 報告方針

- 「Scout 側」「Copilot CLI / ホスト側」を必ず分けて報告する。
- どちらを最大化できたか、どちらが変更不可だったかを明確にする。
- 設定変更をしていないのに「最大化完了」と言わない。
- 読み取り調査だけで終わった場合は「調査結果」として報告する。
- Scout の結果は `added` / `preserved` / `removed` / `not-approved` で示し、`removed` があれば修復するまで完了扱いにしない。
