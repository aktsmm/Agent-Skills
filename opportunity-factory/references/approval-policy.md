# Approval Policy

Opportunity-factory は AUTO 既定。AI が自律で回し、人間承認は **security-approve** バケットの操作のみ。金銭に関わる操作 (paid subscription 新規契約等) は稀にしか発生しないため security-approve の一例として扱い、独立バケットは持たない。

## Buckets

### `auto` (AI 自律)

以下は AUTO / FULL / ALL いずれでも承認不要:

- Workspace 内 file 読取・作成・編集
- Workspace 内 git commit、および setup で承認済みの既存 private/internal remote への push
- Secret / `.env` / `secrets/` / OS keyring / env var の **読取と使用**
- Reversible な操作 (git branch 追加、backup 済み削除、cache clear、tmp 削除)
- LLM 呼び出し・prompt 実行・skill 呼び出し
- Read-only な external 参照 (Docs fetch、Web 検索の GET、API GET、DOM snapshot、screenshot)
- Adapter (scheduler / task runner) の再走
- Anti-pattern registry 更新、dashboard-state 更新、learning append

### `security-approve` (人間承認必須)

以下は user 明示承認まで proceed 不可:

- Secret / credential の **書込み・新規発行・削除・external 送信**
- 新規サービスへの login / account 作成 (paid / free 問わず)
- 有料 subscription 申込・課金契約 (金銭発生シナリオはここに集約)
- External publish: Marketplace / npm / PyPI / SNS post / blog 公開 / public issue 起票 / public PR 作成
- Public remote への git push、または remote visibility / destination が未確認の push
- Personal data の外部送信
- 法的リスク (他人の著作物 upload、規約違反 scraping 等)
- 不可逆 broadcast (一斉メール、public 通知)
- Browser 経由の **書込み系操作** (form submit、purchase、post、file upload)
- **Focus theme apply** (3 ヶ月更新の確定)
- **Backup 不能な破壊的操作** (下記 Backup-First 参照)
- **Blocking mode の critic reject 済み task の強行**

### Money 発生シナリオ (security-approve の 1 例)

日常運用でほぼ発生しないため独立バケットは持たない。以下は例:

- OpenAI / Anthropic 有料 API の新規 subscription
- Azure / AWS リソースの課金付き provisioning
- SaaS の有料 plan アップグレード
- Marketplace publish の PAT 発行 (Azure DevOps 課金設定を伴う場合)

判定は **AI 使用料 (LLM 呼び出し量) は対象外**。それは skill 側で考慮しない (adapter / 外部で管理)。

## Reversibility Classifier

操作を `auto` か `security-approve` かに分類する判定基準。

- **Reversible = auto**: rollback 可能。git revert / branch delete on unpushed / cache clear / tmp 削除 / artifact 再生成
- **Irreversible but recoverable = auto (backup 付き)**: 破壊的だが backup があれば元に戻せる。file overwrite (copy 済み)、tracked delete (git 履歴に残る)、DB row delete (dump 済み)
- **Irreversible not recoverable = security-approve**: 外部 broadcast、public publish、payment、account 作成、他人巻き込む操作
- **判定不能 = security-approve**: 安全側に倒す

## Backup-First (対象別手順)

破壊的操作は backup を取れれば AUTO で自律実行してよい。取れない場合は security-approve に escalate。

| 対象                            | Backup 手段                         | AUTO 可否                                    |
| ------------------------------- | ----------------------------------- | -------------------------------------------- |
| Code file (tracked)             | git stash / feature branch snapshot | AUTO                                         |
| Code file (untracked)           | copy to `backup/YYYYMMDD-HHmmss/`   | AUTO                                         |
| DB (workspace 内 SQLite)        | `.dump` を `backup/` に保存         | AUTO                                         |
| DB (外部 managed)               | export API / snapshot API           | AUTO if API 可、否なら security-approve      |
| Config file                     | copy to `backup/`                   | AUTO                                         |
| External state (SaaS 側 record) | 手段なし                            | security-approve                             |
| Third-party account state       | 手段なし                            | security-approve                             |
| Cloud リソース (課金付き)       | ARM export / Terraform state 保存   | AUTO if export 成功、否なら security-approve |

Rule: **backup 手段が確立できない = AUTO でも security-approve へ escalate**。判断は critic-log にも記録。

## Override / Escalation Flow

- Worker が security-approve 判定を出したら、task を `blocked-approval` 状態にして dashboard-state.pendingApprovals に append
- Digest (daily human digest) で pending approval batch を提示
- User は Approve / Reject / Modify で応答
- Approve → 元の worker が resume、approval 事由と operator を log 化
- Reject → task を `rejected-by-user` に落とし、fallback lane で代替を dispatch
- Modify → user が修正した条件で worker 再走

## Autonomy Mode との関係

| Mode            | `auto` バケット                                     | `security-approve` バケット                |
| --------------- | --------------------------------------------------- | ------------------------------------------ |
| Normal          | 削減 (Normal 追加 gate 参照)                        | 拡張 (initial-setup 系操作も含む)          |
| **AUTO (既定)** | 本文の通り                                          | 本文の通り                                 |
| FULL            | 本文の通り + backup 不能な破壊操作も自律 (log 必須) | Bucket は security 系 external のみ        |
| ALL             | FULL 相当 + criteria 自律拡張可                     | Bucket は最小 (broadcast / payment 系のみ) |

Detail: `references/runtime-modes.md` の `ai-autonomous` preset を参照。

## Log Contract

security-approve バケットの全 event は append-only で `dashboard-state.approvalLog` に記録。schema:

```json
{
  "ts": "ISO-8601",
  "operation": "e.g. external-publish, secret-write, focus-theme-apply",
  "requestedBy": "worker|commander|critic",
  "decidedBy": "user|user+override|blocked",
  "verdict": "approve|reject|modify",
  "artifactRef": "path or hash",
  "reason": "short explanation",
  "criticVerdict": "optional pass|reject|advisory (Layer 3 blocking の場合)"
}
```

## See Also

- `references/runtime-modes.md`: Autonomy mode preset 定義
- `references/fallback-lane.md`: Blocker 時の代替 task 順序
- `references/rubber-duck-review.md`: Role-level critic checkpoint 契約
- `assets/templates/dashboard-state.json`: pendingApprovals / approvalLog スキーマ
