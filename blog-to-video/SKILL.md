---
name: blog-to-video
description: Turn a technical blog article (URL or pasted text) into a narrated explainer mp4 with slides and subtitles, using a fully free local stack (Pillow + edge-tts + ffmpeg). Use when the user says "blog to video", "記事を動画化", "explainer video", "解説動画作って", "ブログを動画に", or wants an mp4 from a URL with Japanese narration. Output is mp4 + srt under the user's chosen project workspace.
argument-hint: "記事URL or 記事テキスト、希望の言語(JP/EN)、長さ目安、出力先パス"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan
---

# Blog → Video

技術ブログ1本を、ナレーション+スライド+字幕付きの mp4 に自動変換する。

## When to Use

- `blog to video`, `記事を動画化`, `ブログを動画に`, `解説動画作って`, `explainer video`
- リリースブログや技術解説を社内勉強会・X・Teams 向けに短尺動画化したい
- 顧客向け配布が必要 → **使ってよいが TTS は Azure Speech 正規版に差し替える** (このスキルの既定は edge-tts 無料エンドポイント)

## Stack (all free, local)

| 役割 | ツール |
|---|---|
| 台本生成 | LLM (このスキル呼び出し元) |
| スライド | Pillow (BIZ UDGothic 等) |
| ナレーション | `edge-tts` (Edge の Neural 音声・無料・非公式) |
| 動画合成 | `ffmpeg` (`imageio-ffmpeg` 同梱バイナリ可) |
| 字幕 | `.srt` 自動生成 |

## Prerequisites

```powershell
pip install edge-tts imageio-ffmpeg pillow
```

Windows なら BIZ UDGothic がプリインストール済み。詳細・トラブル対応は [references/setup.md](references/setup.md)。

## Workflow

1. **入力確認** — URL / 言語 / 長さ目安 / 出力ディレクトリを確認 (未指定なら確認)
2. **記事取得** — `web_fetch` で本文 + 見出し抽出
3. **台本生成** — [references/script-schema.md](references/script-schema.md) の JSON を `<out>/notes/script.json` に書く
   - スライド 5〜8 枚、各ナレ 40〜120 字、原文の主要メッセージを保持
   - 著作権配慮: 本文丸読みではなく要約と解説に留める
4. **生成実行** — [scripts/build_video.py](scripts/build_video.py) を `--project <out>` で実行
5. **検収** — `<out>/output/final.mp4` を再生確認、ズレ/読み間違い/誤字を修正して再実行

## Output Layout

```
<project>/
├── notes/script.json        台本 (LLM が書く)
├── slides/slide_XX.png      1920x1080
├── audio/audio_XX.mp3       スライドごとのナレ
└── output/
    ├── final.mp4            完成動画
    └── final.srt            字幕
```

## Defaults

- 解像度: 1920x1080 30fps (16:9)
- 音声: `ja-JP-NanamiNeural` (女性・落ち着き)。男性なら `ja-JP-KeitaNeural`
- スライド数: 表紙 + 本編 5〜7 枚 (合計 6〜8 枚)
- 配色: slate-900 背景 / sky-400 アクセント / BIZ UDGothic
- 1スライドあたり 15〜25 秒、合計 2〜4 分

声・配色・フォント変更は [references/customization.md](references/customization.md)。

## Production Use

無料 `edge-tts` は **非公式・SLA なし・商用グレー**。顧客配布や常時運用には:

- ナレーション → **Azure Speech (Neural TTS)** に差し替え
- アバター付きが必要なら → **Azure TTS Avatar**

詳細: [references/production-upgrade.md](references/production-upgrade.md)

## Common Variants

- **9:16 ショート版** (X/Reels): スライド側を `1080x1920`、ナレを 60 秒に圧縮
- **字幕焼き込み**: ffmpeg `subtitles=final.srt` フィルタで動画に焼く
- **BGM 追加**: 別 mp3 を低音量でミックス (`-filter_complex amix`)
- **ブログ内の図を埋め込み**: スライド画像にPillowで貼り付け
- **英語ナレ**: `en-US-AvaMultilingualNeural` 等

## Done Criteria

- [ ] `<out>/output/final.mp4` が再生でき、音声と映像がズレない
- [ ] スライド本文 28pt 以上 / タイトル 56pt 以上で可読
- [ ] ナレが原文の主要メッセージを正しく反映
- [ ] `final.srt` がナレーションと同期
- [ ] 本文の直接コピペや権利不明の画像を含んでいない
