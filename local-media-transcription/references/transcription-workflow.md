# Transcription Workflow Reference

## Preflight Checklist

1. 対象ファイルが存在する
2. `ffmpeg`, `ffprobe`, `whisper` がローカルで使える
3. 出力先フォルダを事前に作成する
4. 長時間録画では処理時間を見積もる

## Example Commands

### 1. ファイル確認

```powershell
$p='C:\path\to\meeting.mp4'
Write-Output "exists=$([bool](Test-Path $p))"
Get-Item $p | Select-Object FullName, Length, LastWriteTime
```

### 2. duration確認

```powershell
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "C:\path\to\meeting.mp4"
```

### 3. 文字起こし

```powershell
$env:PYTHONIOENCODING='utf-8'
whisper "C:\path\to\meeting.mp4" --language Japanese --task transcribe --model turbo --fp16 False --verbose False --output_format txt --output_dir "C:\path\to\out"
```

### 4. 冒頭確認

```powershell
Get-Content "C:\path\to\out\meeting.txt" -TotalCount 80
```

## Recommended Post-processing

### 議事録に整理するときの観点
- 目的
- 議題
- 決定事項
- 検討事項
- 次回までの論点

### アクション抽出の観点
- 誰が
- 何を
- いつまでに
- Microsoft 側に相談したい事項
- 顧客側で整理したい事項

### PPT要点化の観点
- 3〜5点に絞る
- 施策名より、論点と示唆を前面に出す
- 顧客に見せる場合は断定より提案ベースにする

## Failure Patterns

### whisper の help 表示で文字化け / 例外
- Windows の CP932 で `UnicodeEncodeError` が起きることがある
- 実行時は `PYTHONIOENCODING=utf-8` を付ける

### 長時間録画で時間がかかる
- duration を先に見積もる
- まず `.txt` 完了を優先し、要約はその後に行う

### 音声認識ゆれ
- 固有名詞、製品名、数字、参加者名は人手で補正する
- 誤りが疑わしい箇所は断定しない
