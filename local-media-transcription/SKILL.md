---
name: local-media-transcription
description: "ローカル音声/動画の文字起こし skill。MP4/M4A/MP3/WAV/WEBM から ffmpeg + whisper で文字起こしし、必要に応じて話者分離、顧客向け議事録への清書、アクションアイテム、PPT要点まで整理する。Use when: 文字起こし, transcription, transcribe mp4, meeting transcript, mp4から文字起こし, 録画から議事録, 話者分離, diarization, 顧客向け議事録, whisper CLI, ffmpeg."
argument-hint: "文字起こししたいファイルパス or 対象会議の説明"
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Local Media Transcription

ローカルにある音声/動画ファイルを文字起こしし、必要に応じて議事録・アクションアイテム・PPT要点まで整理する skill。

## When to Use

- **文字起こし**, **transcription**, **transcribe mp4**, **meeting transcript**
- **mp4から文字起こし**, **録画から議事録**, **whisperで書き起こし**
- Teams録画、Screenpresso録画、会議音声から要点を抽出したいとき
- ローカル環境で完結させたいとき

## Supported Inputs

- MP4 / M4A / MP3 / WAV / WEBM
- 日本語会議、社内ミーティング、顧客打合せ録画

## Outputs

- 生書き起こし `.txt`
- 話者分離付き書き起こし `.txt` / `.md`
- 議事録 `.md`
- 顧客向け清書版議事録 `.md`
- アクションアイテム `.md`
- PowerPoint用要点 `.md`

## Workflow

1. **入力確認**
- 対象ファイルが存在するか確認する
- 長さ、サイズ、更新日時を確認する

2. **ツール確認**
- `ffmpeg`, `ffprobe`, `whisper` CLI が使えるか確認する
- 使えない場合は、ローカル書き起こしは中断して代替案を提示する

3. **メディア確認**
- `ffprobe` で duration を取得する
- 長時間録画なら処理時間を見積もる

4. **文字起こし実行**
- 日本語会議なら以下を基本形とする

```powershell
$env:PYTHONIOENCODING='utf-8'
whisper "<media-file>" --language Japanese --task transcribe --model turbo --fp16 False --verbose False --output_format txt --output_dir "<output-dir>"
```

5. **品質確認**
- 出力 `.txt` の先頭数十行を読んで破綻していないか確認する
- 最低限、発話として読めるか、ファイルが空でないかを確認する

6. **必要に応じて話者分離**
- 話者分離が必要なら、利用可能な diarization 手段を確認する
- 使える場合は話者ラベル付きの書き起こしを生成する
- 使えない場合は、話者分離なしで進めるか、制約を明示して中断する

7. **必要に応じて整形**
- 議事録
- 顧客向け清書版議事録
- アクションアイテム
- PPT要点
- 断定しすぎず、音声認識揺れを補正して整理する

## Decision Points

### A. ツールがない場合
- `ffmpeg` / `whisper` がない場合は中断
- 代替として Teams文字起こしテキスト貼付 or 事前インストールを案内

### B. 文字起こしだけでよい場合
- `.txt` を出力して終了

### C. 会議整理まで必要な場合
- 以下の成果物を追加生成する
  - 議事録
  - 顧客向け清書版議事録
  - 議事録
  - アクションアイテム
  - PPT要点

### D. 話者分離が必要な場合
- diarization ツールや既存環境を確認する
- 使える場合は `話者A / 話者B` などのラベルで一度出力する
- 名前が確定していない段階では推定名を断定しない
- 使えない場合は「話者分離なしで進める / 後で人手補正する」を明示する

### E. 顧客向け資料に載せる場合
- 固有名詞や音声認識誤りを目視補正する
- 曖昧な箇所は断定せず「〜との認識」「〜との説明」などにする
- 内部会話、未確定情報、雑談は削る
- 顧客向けには「決定事項 / 検討事項 / 次回アクション」が一目で分かる形に整える

## Completion Criteria

- 入力メディアの存在確認が完了している
- 書き起こし `.txt` が生成されている
- 冒頭確認で致命的な破綻がない
- 話者分離が必要な依頼では、可否判定か分離済み出力のどちらかが明示されている
- 依頼があれば議事録 / 顧客向け清書版 / アクション / PPT要点まで生成されている

## Quality Rules

- 元音声にない断定を追加しない
- 数値・固有名詞は誤認識の可能性を意識する
- 顧客向け要約では、施策ありきで決めつけない
- 顧客向け議事録では、内部相談や未承認事項をそのまま残さない
- 話者分離では、人名確定できないラベルを勝手に実名化しない
- 長時間音声では、まず文字起こし成功を優先し、その後に整理へ進む

## References

- [transcription-workflow.md](./references/transcription-workflow.md)
