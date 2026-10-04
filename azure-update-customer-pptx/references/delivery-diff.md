# Previous Delivery Diff

Moved from SKILL.md "Previous Delivery Diff (必須)".

## Steps

1. `previousDate` を決める: 直近の `{MMDD}/manifest/classification.json` を持つフォルダ。`fetched-updates.json` が無い場合は `{date}/logs/` や README の「対象週」記述から範囲を割り出す。
2. `previousEndDate` を出す: 前回inventoryの全itemから`created`最大日を算出する。会議日、フォルダ名、PPTX日付を取得終端とみなさない。
3. 今回 Fetch 範囲を `created ge <previousEndDate+1> and created le <today>` にする。Days ベースの fallback ではなく、前回終端を必ず使う。
4. **必須の二重チェック**: Azure Updates MCP の `*_get_recent_azure_updates` で `created ge <previousEndDate> and created le <newStartDate-1>` を投げて 0 件になることを確認する（境界日で漏れが出やすい）。
5. 見つけた抜け item を `{date}/logs/diff-check.md` に「id / title / created / 追加 or 次回持ち越し」で残す。
