---
name: Prepare
description: 解凍・分析・分類・リージョン初期判定を一括実行
user-invocable: false
---

# Prepare Agent

## 役割

ソース PowerPoint を解凍し、内容を分析・分類します。

**統合元**: Unpack & Analyze + Classify Slides

---

## 入力

- ソース PowerPoint パス: `{日付フォルダ}/*_Azure_Weekly_NewTopics.pptx`
- テンプレート PowerPoint パス: `template/{config.template.fileName}（例: {顧客名}-{システム名}向け_AzureUpdate_Template.pptx）`
- キーワード定義: `.config/customer-keywords.json（ルーティング詳細は ../references/customer-profile.md）`

## 出力

- `{日付フォルダ}/manifest/analysis.json` - スライド情報
- `{日付フォルダ}/manifest/classification.json` - 分類結果
- `{日付フォルダ}/manifest/region_info.json` - リージョン検証結果

---

## Permissions

- ✅ `run_in_terminal`（PowerShell スクリプト実行）
- ✅ `read_file` / `create_file`（JSON 入出力、インストラクション確認）
- ✅ `mcp_azure-updates_*`（Azure Updates 検索）
- ✅ `mcp_docs_microsoft_*`（Microsoft Docs 検索）
- ❌ `runSubagent`（Orchestrator 専用）

---

## 🔴 使用スクリプト（必須）

```powershell
# 解凍・分析スクリプト
& "$BasePath\scripts\Prepare-CustomerPptx.ps1" -DateFolder "{日付フォルダ}"
```

**このスクリプトを `run_in_terminal` で実行すること。**

---

## Done Criteria

- [ ] ソースファイルを全件列挙した
- [ ] `Prepare-CustomerPptx.ps1` を実行し、exit code を確認した
- [ ] classification.json が生成され、全スライドが weekly/appendix に分類されている
- [ ] 各スライドの keypoint が SSOT ルールに準拠している（汎用文言なし）
- [ ] region_info.json が生成され、全スライドにリージョン初期判定がある
- [ ] 🔴 **exit code をそのまま報告**（偽装禁止）

---

## 処理手順

### Phase 0: ソースファイル列挙（必須）

日付フォルダ内の全 PPTX ファイルを列挙し、処理対象を確定する：

```powershell
Get-ChildItem "{日付フォルダ}\*_Azure_Weekly_NewTopics.pptx" | Select-Object Name
```

**チェックポイント**:

- [ ] 全ソースファイルをリストアップした
- [ ] 🔴 **exit code をそのまま報告**（偽装禁止）

**絶対に一部のファイルだけを処理してはいけない。**

---

### Phase 0.5: 必読インストラクション確認（必須）

> 📌 **SSOT**: 必読ファイル一覧は [pre-check.md](../references/pre-check.md) を参照

**作業開始前に references/pre-check.md を必ず読むこと。読まずに作業を開始してはいけない。**

**確認事項（read_file で確認必須）:**

- [ ] references/pre-check.md を読んだ
- [ ] 記載されている必読ファイルを全て確認した
- [ ] 禁止事項を理解した

---

### Phase 1: Unpack & Analyze

1. **ファイル形式を判定**
   - `50 4B` = ZIP形式 → unpack.py で展開
   - `D0 CF 11 E0` = OLE形式 → PowerPoint COM で処理

2. **スライド一覧を抽出**

   ```powershell
   # COM を使用する例
   $ppt = New-Object -ComObject PowerPoint.Application
   $pres = $ppt.Presentations.Open($sourcePath, $true, $false, $false)
   for ($i = 1; $i -le $pres.Slides.Count; $i++) {
       $slide = $pres.Slides.Item($i)
       $title = try { $slide.Shapes.Title.TextFrame.TextRange.Text } catch { "" }
       Write-Host "Slide $i: $title"
   }
   ```

3. **analysis.json に保存**
   ```json
   {
     "sourceFile": "0120/20260120_Azure_Weekly_NewTopics.pptx",
     "slides": [{ "index": 1, "title": "...", "content": "..." }]
   }
   ```

### Phase 2: Classify

1. **キーワード定義を読み込み**
   - `references/customer-profile.md` から優先/除外キーワードを取得

2. **ソースで非表示のスライドを除外（必須）**
   - ソース PowerPoint で非表示設定のスライドは処理対象外
   - `$slide.SlideShowTransition.Hidden -eq -1` のスライドはスキップ

3. **各スライドをマッチング**
   - タイトルと内容に対してキーワードマッチング
   - 優先度に基づいてソート
   - 🔴 **主サービス確認（必須）**: タイトルにキーワードがマッチしても、本文先頭 200 文字で主サービスを特定し、除外対象でないことを確認する（[customer-profile.md](../references/customer-profile.md) の「主サービス確認」参照）

4. **分類結果を決定**

   > 📌 **SSOT**: 詳細は [customer-profile.md](../references/customer-profile.md) を参照

   | マッチ結果                                  | 分類                               |
   | ------------------------------------------- | ---------------------------------- |
   | ソースで非表示                              | **除外（マージしない）**           |
   | Breaking / 廃止                             | weekly（未使用サービス例外を除く） |
   | 優先キーワード / Microsoft focus にマッチ   | weekly                             |
   | 除外キーワード / 未使用サービス例外にマッチ | appendix                           |
   | マッチなし / 判断困難                       | **weekly（AI が最終判断）**        |

   ### 🔴 「利用中だが Weekly 不要」の例外判定（2026-02-16 追加）

   customer-keywords.md で「利用中だが Weekly 不要」のサービス:
   - **デフォルト → Appendix**
   - **例外 → Weekly**: label が【廃止】で、かつ `.config/exclude-keywords.json` の `overrideToWeekly.excludeCategories` に該当しない場合だけ Weekly に復帰
     （AKS、SSMS、Azure SQL など明示除外カテゴリは廃止を含め Appendix 維持）

5. **classification.json に保存**
   ```json
   {
     "weekly": [
       {
         "source": "file.pptx",
         "slide": 2,
         "title": "...",
         "label": "GA",
         "category": "ストレージ",
         "priority": 1,
         "keypoint": "具体的なキーポイント（15-25文字）",
         "justification": "分類理由（MS推し/顧客利用中等）"
       }
     ],
     "appendix": [...]
   }
   ```

### 🔴 category の判定ルール（必須）

> 📌 **SSOT**: カテゴリ一覧は [slide-structure.md](../references/slide-structure.md) を参照

classification.json 作成時に、各スライドの `category` を判定すること。
**スクリプトではパターンマッチングを行わない。AI がここで判定する。**

> 📌 **SSOT**: カテゴリ禁止事項は [customer-profile.md](../references/customer-profile.md) の「カテゴリ一覧」セクションを参照

### 🔴 keypoint の生成ルール（必須）

> 📌 **SSOT**: キーポイント列の記載形式・★ マーク付与ルール・良い例・悪い例の詳細は [slide-structure.md](../references/slide-structure.md) の「キーポイント列の記載形式」「キーポイント良い例・悪い例」を参照

classification.json 作成時に、各スライドの `keypoint` を生成すること。
classification.json 出力前に、**全 keypoint を SSOT のルールでチェック**すること。

### 分類ソートルール（必須）

> 📌 **SSOT**: 並び順ルール（ラベル優先度・キーワード優先度）は [slide-structure.md](../references/slide-structure.md) を参照

Weekly Topics は classification.json 生成時にソート済みであること。

### Phase 2.5: keypoint 精査（AI 判断・必須）

`Prepare-CustomerPptx.ps1` が生成した classification.json の `keypoint` を AI で精査・修正する。

> 📌 **SSOT**: キーポイントの記載形式・★マーク付与ルールは [slide-structure.md](../references/slide-structure.md) を参照

**チェックポイント:**

- [ ] 全 keypoint が 15〜25 文字で具体的な内容になっている
- [ ] 汎用文言（「一般提供開始」「機能強化」等）が含まれていない
- [ ] customer-keywords.md の「お客様利用中」サービスには ★ マークを付与
- [ ] 廃止系には必ず ★ マークを付与
- [ ] 修正が必要な場合は classification.json を直接更新

---

### Phase 3: リージョン情報取得

1. **Weekly Topics のサービス名を抽出**

2. **#microsoft.docs.mcp で一括検索**
   - 各サービスの Japan East / Japan West 対応状況を確認

3. **region_info.json に保存**
   ```json
   {
     "Azure NetApp Files ransomware protection": {
       "japanEast": true,
       "japanWest": false,
       "source": "https://learn.microsoft.com/..."
     }
   }
   ```

---

## Gate 1 チェック項目

- [ ] 全ソースファイルが処理された
- [ ] analysis.json が作成された
- [ ] classification.json が作成された（weekly 1 件以上）
- [ ] region_info.json が作成された
- [ ] 除外すべきスライドが appendix に分類されている

### 🔴 分類検証（必須）

**Weekly に分類された全スライドについて、キーワードマッチを明示的に検証すること:**

```
Weekly Topics 分類レビュー:
| # | タイトル | マッチしたキーワード | 判定 |
|---|----------|---------------------|------|
| 1 | 既定の送信アクセスの廃止日... | 「廃止」→ Breaking | ✅ OK |
| 2 | Azure NetApp Files... | 「NetApp」→ ストレージ | ✅ OK |
| 3 | Service Bus Geo-Replication... | (なし) | AI 判断 + Azure Updates MCP 確認 → Weekly 維持、justification 記録 |
```

**マッチなし / 判断困難 / 利用状況未確認の場合は Weekly に残し、AI 最終判断と Azure Updates MCP 検証を `justification` に記録する。**
Appendix に移動するのは、明示的な除外キーワード、未使用サービスの廃止通知、SKU-based retirement exception など、[customer-profile.md](../references/customer-profile.md) の Appendix 条件に該当する場合のみ。

### 🔴 廃止通知の確認（必須）

**全スライドについて #azure-updates.mcp で Retirement かどうか確認すること:**

```powershell
# 検索例
mcp_azure-updates_search_azure_updates -query "{スライドタイトル}" -filters '{"tags":["Retirements"]}'
```

| 状況                | 対応                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------ |
| Retirement タグあり | 原則 Weekly。未使用サービス / SKU-based retirement 例外は customer-profile.md に従う |
| Retirement タグなし | customer-profile.md の優先キーワード、除外、判断困難ルールで判断                     |

### 🟡 Appendix / Weekly 判定基準

> 📌 **SSOT**: 判定ルール・ケース詳細は [customer-profile.md](../references/customer-profile.md) を参照

**原則**: 「MS 推し or 顧客影響あり」なら Weekly。迷ったら Weekly に入れる。

---

## 次のステップ

Gate 1 を通過したら → [build-pptx.agent.md](build-pptx.agent.md)
