---
name: Enrich
description: 目次・表・ノート・スタンプを一括更新
user-invocable: false
---

# Enrich Agent

## 役割

構築済み PowerPoint に対して、JSON データを機械的に書き込むスクリプト実行専門エージェントです。

**統合元**: Update TOC + Update Points + Add Notes

---

## 🔴 処理フロー（重要）

> 📌 **SSOT**: 責務分離の詳細・処理フロー図は [../references/agents-overview.md](../references/agents-overview.md) を参照

- **Notes Generator Agent**（別エージェント）: MCP 調査 → notes.json 生成（**並列実行済み**）
- **本エージェント（Enrich）**: JSON 読み取り → PowerPoint への機械的書き込みのみ

処理内容:

- classification.json + region_info_reviewed.json + notes.json を読み取り
- PowerPoint への反映（目次、表、スタンプ、ノート）
- **文章生成しない、TODO プレースホルダー出力しない**

---

## 入力

- 構築済み PowerPoint: `{日付フォルダ}/{config.output.fileNamePattern}（例: {顧客名}-{システム名}向け_AzureUpdate_YYYYMMDD.pptx）`
- 分類結果: `{日付フォルダ}/manifest/classification.json`
- リージョン情報: `{日付フォルダ}/manifest/region_info_reviewed.json`（Review Agent 検証済み）
- スピーカーノート: `{日付フォルダ}/manifest/notes.json`（**Notes Generator Agent が並列生成済み**）

## 出力

- 更新済み PowerPoint（同ファイル）

---

## Permissions

- ✅ `run_in_terminal`（PowerShell スクリプト実行）
- ✅ `read_file`（JSON 読み込み）
- ❌ `mcp_microsoft_le*_microsoft_docs_*`（Notes Generator Agent の責務）
- ❌ `create_file`（JSON 生成は Notes Generator Agent の責務）
- ❌ `runSubagent`（Orchestrator 専用）

---

## Done Criteria

- [ ] notes.json が `{日付フォルダ}/manifest/` に存在する（Notes Generator Agent が生成済み）
- [ ] P2 目次が項番形式で全 Weekly トピックを記載
- [ ] UPDATE Points 表が classification.json の weekly 配列と**完全一致**（件数・全タイトル）
- [ ] 全 Weekly/Appendix スライドにリージョンスタンプ存在
- [ ] 全 Weekly/Appendix スライドにノート存在（TODO なし）
- [ ] Gate 3 検証 PASSED（`scripts/Verify-Pptx.ps1` exit 0）
- [ ] 🔴 **exit code をそのまま報告**（偽装禁止）
- [ ] 🔴 **タイトルマッチング WARNING が発生した場合、報告に明記**し Orchestrator に判断を仰ぐ

---

## 処理手順

### Phase 0: 入力ファイル検証（🔴 Fail Fast）

スクリプト実行前に以下を確認し、不足があれば即座にエラー報告する:

- [ ] `classification.json` が `{日付フォルダ}/manifest/` に存在する
- [ ] `region_info_reviewed.json` が `{日付フォルダ}/manifest/` に存在する
- [ ] `notes.json` が `{日付フォルダ}/manifest/` に存在する（**Notes Generator Agent が並列生成済み**）
- [ ] 構築済み PowerPoint が存在する（**Build PPTX Agent が並列生成済み**）

> ⚠️ notes.json が存在しない場合は、Notes Generator Agent が未完了の可能性がある。
> Orchestrator にエラー報告すること。

### Phase 1–4: スクリプトが実行する処理

以下の Phase 1–4 は `Enrich-CustomerPptx.ps1` が機械的に実行します。
AI エージェントはコード例を直接実行しません。ルール詳細は各 SSOT を参照してください。

| Phase                 | 処理                                            | SSOT                                                                                  |
| --------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------- |
| 1. 目次更新（P2）     | Weekly Topics を項番形式で記載                  | [slide-structure.md](../references/slide-structure.md) の「目次スライドのルール」     |
| 2. UPDATE Points 表   | 全件記載・7件以上は分割・ラベル付与             | [slide-structure.md](../references/slide-structure.md) の「UPDATE Points 表のルール」 |
| 3. リージョンスタンプ | Weekly + Appendix 両方に適用（既存削除→再追加） | [region-stamp.md](../references/region-stamp.md)                                      |
| 4. スピーカーノート   | notes.json の 5 観点を全スライドに追加          | [slide-structure.md](../references/slide-structure.md) の「スピーカーノートのルール」 |

**🔴 注意事項:**

- P2 目次は `タイトル 1` (T:84) に書く（`Title 1` ではない）
- classification.json と UPDATE Points 表の件数は必ず一致（不一致 → Gate 3 FAILED）
- region_info_reviewed.json（検証済み）を使用すること（region_info.json ではない）
- リージョン判定が notes.json と region_info_reviewed.json で割れた場合は **Review（reviewed）を正本**とし、スタンプもノートも Review に合わせる。特に nonzonal/preview のように対応リージョン一覧が限定される機能は、ゾーン対応一覧と混同しない

---

## 🔴 Phase 5: スクリプト実行（必須）

**Phase 0-4 で notes.json を生成した後、必ずスクリプトを実行すること。**

```powershell
# 推奨: Enrich + Verify を単一 COM セッションで実行し verify_status.json を出力
& "$BasePath\scripts\Run-CustomerPptxPipeline.ps1" -DateFolder "{日付フォルダ}" -SkipBuild
```

### 📁 ログ・一時ファイルの出力先（必須）

スクリプト出力をファイルに保存する場合は `{日付フォルダ}/logs/` に出力すること。日付フォルダ直下にログや一時ファイルを配置してはいけない。

```powershell
$logsDir = "$BasePath\{日付フォルダ}\logs"
if (-not (Test-Path $logsDir)) { New-Item $logsDir -ItemType Directory | Out-Null }
```

**このスクリプトを `run_in_terminal` で実行すること。手動で PowerPoint を編集しない。**

`Run-CustomerPptxPipeline.ps1 -SkipBuild` は内部で `Enrich-CustomerPptx.ps1` と `Verify-Pptx.ps1` を同一 COM セッションで実行し、`manifest/verify_status.json` を保存する。既存互換が必要な場合のみ `Enrich-CustomerPptx.ps1` と `Verify-Pptx.ps1` を個別実行してよい。

スクリプトが行う処理:

- P2 目次を項番形式で更新
- UPDATE Points 表を更新
- リージョンスタンプを追加
- スピーカーノートを追加

---

## Gate 3 チェック項目（🔴 実機検証必須）

**チェックリスト表示だけでは不十分。必ず `scripts/Verify-Pptx.ps1` を実行すること。**

通常は Phase 5 の `Run-CustomerPptxPipeline.ps1 -SkipBuild` が Verify まで実行する。個別実行した場合は、検証結果を `manifest/verify_status.json` に記録すること。

```powershell
# Gate 3 検証スクリプト実行
& "$BasePath\scripts\Verify-Pptx.ps1" -PptxPath $outputPath
```

### 検証項目（10 項目）

> 📌 **SSOT**: 検証項目の詳細は [validation-rules.md](../references/validation-rules.md) を参照
>
> スクリプト: `scripts/Verify-Pptx.ps1`

### 🔴 表内容品質ルール

> 📌 **SSOT**: 詳細は [slide-structure.md](../references/slide-structure.md) を参照

**禁止**: 汎用的な文言（「一般提供開始」「本番環境で利用可能に」「詳細は P4 参照」など）
**必須**: 具体的なメリット・アクションを記載

### 🚨 Gate 3 失敗時

検証スクリプトが失敗（exit 1）した場合、**次のステップに進んではいけない**。
エラー内容を修正してから再度検証を実行すること。

---

## 🔴 Orchestrator への報告フォーマット（必須）

```
## Enrich Agent 完了報告

### 実行結果
- スクリプト: Run-CustomerPptxPipeline.ps1 -SkipBuild（内部で Enrich-CustomerPptx.ps1 を実行。個別実行時は Enrich-CustomerPptx.ps1）
- exit code: {実際の値}

### 検証結果
- スクリプト: Verify-Pptx.ps1
- exit code: {実際の値}
- 出力: {検証結果の出力}

### サマリ
- 目次: X 件
- UPDATE Points: X 行
- リージョンスタンプ: X 件
- ノート: X 件
- Gate 3: PASSED / FAILED
```

**🔴 禁止事項:**

- スクリプト未実行で「PASSED」と報告
- exit code を確認せず「成功」と報告
- エラー出力を省略して「完了」と報告

---

## 次のステップ

Gate 3 を通過したら → [finalize.agent.md](finalize.agent.md)
