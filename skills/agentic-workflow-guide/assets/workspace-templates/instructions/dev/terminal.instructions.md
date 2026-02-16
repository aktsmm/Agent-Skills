# Terminal Command Execution Instructions

エージェントがターミナルでコマンドを実行する際の安全基準です。

## 1. カレントディレクトリの確認

コマンドを実行する前に、必ず現在地が正しいか確認してください。
特に、相対パスでファイルを操作する場合や、プロジェクトルートで実行する必要があるコマンド（`npm install`, `git` 等）の場合に重要です。

### 必須手順

1. **最初に `Get-Location` で現在地を確認する**（省略禁止）
2. 期待するディレクトリでなければ `Set-Location` (または `cd`) で移動する
3. コマンドを実行する

### チェック項目

- **実行前確認**: `Get-Location` で現在地を確認する。
- **ワークスペース確認**: 複数リポジトリが存在する環境では、意図したリポジトリにいることを必ず確認する。
- **存在確認**: ファイルを操作する前に `Test-Path` (PowerShell) や `ls` で対象の存在を確認する。

### 実行例

```powershell
# 1. 現在地を確認
Get-Location

# 2. 必要に応じて移動
Set-Location "d:\03_github\ghc_template"

# 3. コマンド実行
git status
```

## 2. コマンド構文 (PowerShell)

- Windows 環境での作業を前提とし、コマンドは **PowerShell 互換** で記述してください。
- 複数のコマンドを連結する場合は `;` を使用してください（`&&` は使用しない）。
- パイプライン `|` を活用し、オブジェクトベースのデータ操作を行ってください。

### PowerShell 特有の注意事項

| Bash/Linux            | PowerShell                              | 備考                                                   |
| --------------------- | --------------------------------------- | ------------------------------------------------------ |
| `&&`                  | `;`                                     | コマンド連結（`;` は前のコマンドの成否に関わらず実行） |
| `\|\|`                | `; if ($?) { } else { }`                | 条件分岐は `$?` で直前のコマンド成否を確認             |
| `export VAR=value`    | `$env:VAR = "value"`                    | 環境変数の設定                                         |
| `echo $VAR`           | `$env:VAR` または `Write-Output`        | 環境変数の参照                                         |
| `cat file`            | `Get-Content file`                      | ファイル内容の表示                                     |
| `grep pattern`        | `Select-String -Pattern pattern`        | テキスト検索                                           |
| `find . -name "*.py"` | `Get-ChildItem -Recurse -Filter "*.py"` | ファイル検索                                           |
| `rm -rf dir`          | `Remove-Item -Recurse -Force dir`       | ディレクトリ削除                                       |
| `/dev/null`           | `$null`                                 | 出力の破棄（**`/dev/null` は使用禁止**）               |

### よくある間違い

```powershell
# ❌ NG: Bash構文
command1 && command2
export MY_VAR="hello"
cat file.txt | grep "pattern"

# ✅ OK: PowerShell構文
command1; command2
$env:MY_VAR = "hello"
Get-Content file.txt | Select-String -Pattern "pattern"
```

## 3. 破壊的操作の慎重な実行

- ファイルの削除 (`rm`, `Remove-Item`) や移動 (`mv`) は、対象を間違えると復旧困難になるため、実行前に必ずパスを確認してください。
- ワイルドカード (`*`) を使用した削除は特に注意し、可能な限り具体的なファイル名を指定してください。

## 4. 長時間実行プロセスの扱い

- サーバーの起動や監視プロセスなど、終了しないコマンドを実行する場合は、バックグラウンド実行 (`Start-Job` 等) を検討するか、ユーザーにその旨を伝えてください。
