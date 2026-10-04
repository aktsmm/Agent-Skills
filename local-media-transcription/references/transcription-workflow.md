# Transcription Workflow Reference

手順と判断分岐は SKILL.md が正。ここは具体コマンドと話者分離の補足だけを持つ。出力先フォルダは事前に作成する。

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

SKILL.md の Workflow 4 の基本形を使う。

### 4. 冒頭確認

```powershell
Get-Content "C:\path\to\out\meeting.txt" -TotalCount 80
```

## Recommended Post-processing

### 話者分離が必要なとき

ラベル付けと実名化の判断は SKILL.md の Decision Points D に従う。

#### 推奨ツール

- `WhisperX`
  - Whisper + forced alignment + diarization を一体で扱いやすい
  - 会議録画の「だいたいの話者分け」を最短で作りたいときに向く
- `pyannote.audio`
  - 話者分離専用として柔軟
  - 既に別の文字起こし結果があり、後段で diarization だけ追加したいときに向く

#### インストール時の注意

- `whisperx` / `pyannote.audio` はそれぞれ専用 venv に入れる。GPU / CUDA / torch の組み合わせで失敗しやすく、既存の Whisper 環境を壊しやすい。
- pyannote.audio は Hugging Face モデル利用前提になることがあり、追加認証やモデル同意が必要なケースがある。

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

### WhisperX / pyannote の依存衝突

- 既存の whisper 環境に直接入れると torch 系の依存がぶつかることがある
- 可能なら diarization 専用の別 venv を切る

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

### 会議種別・参加者の誤分類

- 保存先は会議で実際に行った活動で決める。顧客への紹介、スコーピング、定例は、ライブデモ、ハンズオン、デリバリーを実施していない限り議事録として扱い、デモ記録にしない。
- Teams などの参加者タイルは出席を示す情報であり、発言の証跡ではない。出席者と発言者を別項目にし、発言者は書き起こしまたはユーザー確認で判定する。アイコンや表示名による所属の判定は、ユーザー確認がある場合に限る。
