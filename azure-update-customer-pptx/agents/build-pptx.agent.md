---
name: Build PPTX
description: テンプレートにスライドを挿入して PowerPoint を構築
user-invocable: false
---

# Build PPTX Agent

## 役割

テンプレート PowerPoint をベースに、分類済みスライドを挿入して新しい PowerPoint を構築します。

## 入力

- テンプレート PowerPoint: `template/{config.template.fileName}（例: {顧客名}-{システム名}向け_AzureUpdate_Template.pptx）`
- ソース PowerPoint: `{日付フォルダ}/*_Azure_Weekly_NewTopics.pptx`
- 分類結果: `{日付フォルダ}/manifest/classification.json`

## 出力

- 構築済み PowerPoint: `{日付フォルダ}/{config.output.fileNamePattern}（例: {顧客名}-{システム名}向け_AzureUpdate_YYYYMMDD.pptx）`

---

## Permissions

- ✅ `run_in_terminal`（PowerShell スクリプト実行）
- ✅ `read_file` / `create_file`（JSON 入出力）
- ❌ `runSubagent`（Orchestrator 専用）

---

## 🔴 使用スクリプト（必須）

```powershell
# スライド挿入スクリプト
& "$BasePath\scripts\Build-CustomerPptx.ps1" -DateFolder "{日付フォルダ}"
```

> **このスクリプトを `run_in_terminal` で実行すること。手動でスライドを挿入しない。**

## 📁 ログ・一時ファイルの出力先（必須）

スクリプト出力をファイルに保存する場合は、必ず `{日付フォルダ}/logs/` に出力すること。
日付フォルダ直下にログや一時ファイルを配置してはいけない。

```powershell
$logsDir = "$BasePath\{日付フォルダ}\logs"
if (-not (Test-Path $logsDir)) { New-Item $logsDir -ItemType Directory | Out-Null }
# 例: & script.ps1 ... *> "$logsDir\build_log.txt"
```

---

## Done Criteria

- [ ] 出力 PowerPoint が存在する
- [ ] Weekly Topics スライドが P4 以降に配置されている
- [ ] Appendix スライドが全て非表示設定（Hidden = -1）
- [ ] セクション構成がテンプレートと一致
- [ ] **🔴 スライド数が期待値と一致**（重複防止）
  - 期待値: 2 + Weekly件数 + 1 + Appendix件数 + 1
  - 許容誤差: ±5枚（サンプル削除の誤差を考慮）
  - 期待値の +50% を超える場合は異常として中断
- [ ] Gate 2 検証 PASSED
- [ ] 🔴 **exit code をそのまま報告**（偽装禁止）

## 処理手順

### Phase 0: 入力ファイル検証（🔴 Fail Fast）

スクリプト実行前に以下を確認し、不足があれば即座にエラー報告する:

- [ ] `classification.json` が `{日付フォルダ}/manifest/` に存在する
- [ ] `classification.json` の `weekly` 配列が 1 件以上ある
- [ ] テンプレート PPTX が `template/` に存在する
- [ ] ソース PPTX が `{日付フォルダ}/` に存在する

### Phase 1: Build スクリプト実行（必須）

以下のスクリプトを `run_in_terminal` で実行し、テンプレートへのスライド挿入を行う。

```powershell
& "$BasePath\scripts\Build-CustomerPptx.ps1" -DateFolder "{日付フォルダ}"
```

> 📌 **SSOT**: 並び順ルールは [slide-structure.md](../references/slide-structure.md) を参照

このスクリプトが内部で処理する内容:

- テンプレート PPTX を複製して出力ファイルを作成
- Weekly スライドをラベル順で挿入
- Appendix スライドを挿入し、非表示設定を適用
- セクション構成を維持しながら挿入位置を調整

### Phase 2: セクション構成を確認（必須）

#### ❗ テンプレートのセクション構成を確認（必須）

**セクション構成をハードコードしない。必ずテンプレートから読み取る:**

```powershell
# テンプレートのセクション構成を確認
$app = New-Object -ComObject PowerPoint.Application
$template = $app.Presentations.Open($templatePath, $true, $false, $false)
Write-Host "=== Template Sections ==="
for ($i = 1; $i -le $template.SectionProperties.Count; $i++) {
    $name = $template.SectionProperties.Name($i)
    $first = $template.SectionProperties.FirstSlide($i)
    $count = $template.SectionProperties.SlidesCount($i)
    Write-Host "$i : $name (P$first, $count枚)"
}
$template.Close()
```

> ⚠️ **テンプレートのセクション構成をそのまま維持すること**
> セクションの削除・再作成は行わない。スライド挿入のみ行う。
> セクション構成はテンプレートごとに異なるため、上記スクリプトで必ず確認すること。

**🔴 セクション追加時の注意:**

```powershell
# ❌ 禁止: Sections.Add() → スライドに紐づかない空セクションになる
# ✅ 推奨: AddBeforeSlide() でスライド位置を指定
$pres.SectionProperties.AddBeforeSlide($slideIndex, "SectionName")
```

**スライド挿入位置:**

- Weekly Topics → WeeklyUPDATE セクション（P3 UPDATE Points 表の後）に挿入
- Appendix → Appendix セクションに挿入（非表示設定）

### Phase 3: Appendix スライドの非表示設定を確認（必須）

**すべての Appendix スライドに対して非表示を設定すること。設定漏れは不可。**

```powershell
# Appendix セクションの全スライドを非表示に
for ($i = $appendixStartSlide; $i -le $pres.Slides.Count; $i++) {
    $pres.Slides.Item($i).SlideShowTransition.Hidden = -1
}
```

---

## Gate 2 チェック項目

- [ ] 出力 PPTX が存在する
- [ ] Weekly Topics スライドが P4 以降に配置されている
- [ ] Appendix ヘッダースライドが存在する
- [ ] **セクション構成が正しい**
  - Weekly New Topics セクションにスライドが 1 件以上ある
  - Appendix セクションが存在する
- [ ] **非表示設定が正しい**
  - Appendix セクションの全スライドが非表示（Hidden = -1）
  - Weekly New Topics セクションのスライドは表示
- [ ] **Appendix スライド数が classification.json と一致**
  - classification.json の appendix 配列の件数と実際に追加されたスライド数を照合

---

## 注意事項

現在のワークフローは COM ベースで直接編集・保存するため、unpack / repack や XML 手編集は行わない。
スライド ID、relationship、メディアコピーは `Build-CustomerPptx.ps1` の内部処理に委ねる。

---

## 次のステップ

Gate 2 を通過したら → [enrich.agent.md](enrich.agent.md)
