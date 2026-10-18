---
name: write-tests
description: "コードを分析し、テストを段階的に生成・実行"
disable-model-invocation: true
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---
<!-- syncToGlobal: true -->
<!-- author: aktsmm -->
<!-- repository: https://github.com/aktsmm/Agent-Customization -->
<!-- license: CC BY-NC-SA 4.0 -->
<!-- copyright: Copyright (c) 2025 aktsmm -->

# write tests

対象コードを分析し、テストを段階的に生成・実行する。

## 対象（必須）

- **ファイル**: （ファイルを添付 or パスを記載）
- **フレームワーク**: pytest / jest / vitest / 他（指定なければ自動検出）
- 対象ファイルまたはパスが無い場合は、広い範囲を推測せず確認して停止する

## 指示

### Step 1: 分析（SRP）

- テスト対象の**責務**を特定する（何をする関数/クラスか）
- 入出力のパターンを洗い出す
- 既存テストがあれば確認し、**重複を避ける**

### Step 2: 計画（Transparency）

テストケースを書く前に計画を示す：

| ケース | 入力例 | 期待結果 | 優先度 |
| ------ | ------ | -------- | ------ |
| 正常系 | ...    | ...      | 高     |
| 異常系 | ...    | ...      | 中     |
| 境界値 | ...    | ...      | 中     |

### Step 3: 実装（Iterative）

1. **1 ケースずつ**テストを書く
2. 各テストは AAA パターン（Arrange / Act / Assert）
3. テスト名は既存 repo と framework の命名規則を最優先する
	- pytest の例: `test_<何を>_<どんな条件で>_<期待結果>`
	- Jest / Vitest: 既存の `describe` / `it` / `test` の文体と粒度に合わせる

### Step 4: 検証（Feedback Loop）

- テストを実行して全て PASS するか確認
- VS Code の task 実行（`runTask`）は使わない（確認待ちを避けるため、`powershell` で非対話・単発で実行する）
- テスト実行は `execute/runInTerminal` を利用可（非対話・単発・timeout 指定を推奨）
- 失敗したらその場で修正
- カバレッジを確認（可能なら）

## オプション

- フレームワーク: pytest / jest / 他
- モック対象: 外部 API / DB など
- 既存テストファイル: パスを記載
