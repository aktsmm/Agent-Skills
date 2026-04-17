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

### 話者分離が必要なとき

- まずローカル環境に diarization 手段があるか確認する
- 使える場合は `話者A`, `話者B` のような中立ラベルで一度出す
- 参加者名が確定してから実名へ置換する
- 名前が曖昧なままなら実名化しない

#### 推奨ツール

- `WhisperX`
	- Whisper + forced alignment + diarization を一体で扱いやすい
	- 会議録画の「だいたいの話者分け」を最短で作りたいときに向く
- `pyannote.audio`
	- 話者分離専用として柔軟
	- 既に別の文字起こし結果があり、後段で diarization だけ追加したいときに向く

#### 具体コマンド例

##### WhisperX 例

```powershell
# 事前に whisperx が入っている前提
whisperx "C:\path\to\meeting.mp4" --language ja --model large-v3 --diarize --output_dir "C:\path\to\out"
```

##### pyannote.audio 例

```powershell
# まず音声抽出
ffmpeg -i "C:\path\to\meeting.mp4" -vn -ac 1 -ar 16000 "C:\path\to\meeting.wav"

# その後 diarization スクリプトや notebook で話者分離
```

#### 実務上の使い分け

- まず速く全体像を出したい: `WhisperX`
- 既存の文字起こしに話者情報を後付けしたい: `pyannote.audio`
- 環境準備が重い場合は、話者分離なしで先に議事録化し、必要箇所だけ人手補正する

### 議事録に整理するときの観点
- 目的
- 議題
- 決定事項
- 検討事項
- 次回までの論点

### 顧客向け議事録に清書するときの観点
- 内部だけの相談や調整コメントは落とす
- 誤認識が疑わしい固有名詞は確認できる表現に寄せる
- 「誰が何をするか」を読み手が追えるように整理する
- 断定できない箇所は「〜との認識」「〜との説明」に留める
- 施策の押し付けではなく、提案ベースの表現にする

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

### 話者誤判定
- 話者分離結果はそのまま信用せず、会議文脈で確認する
- 話者交代が短い会話では、ラベルが揺れる前提でレビューする
- 顧客向け議事録では、話者名確定前のラベルをそのまま出さない
