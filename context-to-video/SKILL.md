---
name: context-to-video
description: Turn any context (blog URL, pasted article, PR diff, meeting notes, release notes, raw prompt) into a narrated explainer mp4 with slides, subtitles, and optionally a talking-head avatar. Uses a free local stack (Pillow + edge-tts + ffmpeg) with optional SadTalker for the avatar. Use when the user says "動画化", "explainer video", "解説動画作って", "ブログを動画に", "記事を動画化", "PRを動画で説明", "議事録を動画化", "context to video", or wants an mp4 from arbitrary text/source. Output is mp4 + srt under the user's chosen project workspace.
argument-hint: "入力(URL/テキスト/PR/メモ)、言語(JP/EN)、長さ目安、アバター要否、出力先パス"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan
---

# Context → Video

任意の入力コンテキストを、ナレーション+スライド+字幕+(任意で)アバター付きの mp4 に変換する。

## When to Use

- `動画化`, `解説動画作って`, `ブログを動画に`, `記事を動画化`, `explainer video`, `context to video`
- リリースブログ / PR 説明 / 議事録 / 設計メモ / リリースノート / 学習コンテンツを短尺動画化したい
- YouTube / 社内勉強会 / Teams / X 向けの素材を時短で量産したい
- 顧客向けに出すなら **TTS は Azure Speech 正規版に差し替える** (既定は edge-tts 無料エンドポイント)

## Input Sources (any of these works)

| 入力 | 取り方 |
|---|---|
| ブログ/記事 URL | `web_fetch` で本文取得 |
| 貼り付けテキスト | そのまま要約 |
| PR / commit diff | `gh pr view` + `gh pr diff` |
| 議事録・設計メモ | ファイル読み込み |
| リリースノート | URL or Markdown |
| 自由プロンプト | LLM に直接構成依頼 |

→ ソース取得後の処理は共通(LLM が `notes/script.json` を書く)。

## Stack (all free, local)

| 役割 | ツール |
|---|---|
| 台本生成 | LLM (このスキル呼び出し元) |
| スライド | Pillow (BIZ UDGothic 等) |
| ナレーション | `edge-tts` (Edge の Neural 音声・無料・非公式) |
| 動画合成 | `ffmpeg` (`imageio-ffmpeg` 同梱バイナリ可) |
| 字幕 | `.srt` 自動生成 |
| **アバター (任意)** | **SadTalker** (GPU推奨) + ffmpeg 楕円マスク |

## Quick Workflow (no avatar)

```powershell
pip install edge-tts imageio-ffmpeg pillow
# 1. 入力からscript.json生成 (LLM)
# 2. 動画生成
python scripts\build_video.py --project D:\path\to\project
# → output\final.mp4 + final.srt
```

詳細: [references/script-schema.md](references/script-schema.md) / [references/setup.md](references/setup.md)

## Avatar Mode (talking-head in corner)

GPU(VRAM 8GB+)があるなら、SadTalkerで右下にアバターを足せる。
**初回セットアップは別 venv (Python 3.10) で 30〜40分**、以降は 1動画あたり +20〜30分。

```powershell
# 既存動画 + 8音声 → アバター合成
python scripts\add_avatar.py --project D:\path\to\project --face D:\path\to\face.jpg
# 楕円マスク版を作る
python scripts\ellipse_overlay.py --project D:\path\to\project
# → output\final_with_avatar.mp4 と final_with_avatar_ellipse.mp4
```

セットアップ・落とし穴・キャラ選び: [references/avatar.md](references/avatar.md)

## Output Layout

```
<project>/
├── notes/script.json                  台本 (LLM が書く)
├── slides/slide_XX.png                1920x1080
├── audio/audio_XX.mp3                 スライドごとのナレ
├── avatar/                            (任意)
│   ├── input/face.jpg                 アバター元写真
│   ├── SadTalker/                     repo + checkpoints
│   ├── venv/                          Python 3.10 + torch cu121
│   └── clips/audio_XX.mp4             各ナレぶんアバター動画
└── output/
    ├── final.mp4                      無印 (スライド+ナレ)
    ├── final.srt                      字幕
    ├── final_with_avatar.mp4          (任意) アバター矩形
    └── final_with_avatar_ellipse.mp4  (任意) アバター円形ワイプ
```

## Defaults

- 解像度: 1920x1080 30fps (16:9)
- 音声: `ja-JP-NanamiNeural` (女性・落ち着き)。男性なら `ja-JP-KeitaNeural`
- スライド数: 表紙 + 本編 5〜7 枚 (合計 6〜8 枚)
- 配色: slate-900 / sky-400 / BIZ UDGothic
- 1スライドあたり 15〜25 秒、合計 2〜4 分

声・配色・フォント・アスペクト比変更: [references/customization.md](references/customization.md)

## Production Use

無料 `edge-tts` は **非公式・SLA なし・商用グレー**。顧客配布や常時運用には:
- ナレーション → **Azure Speech (Neural TTS)** に差し替え
- アバター付き商用 → **Azure TTS Avatar** (Lisa等・公式・$0.30/分〜)

詳細: [references/production-upgrade.md](references/production-upgrade.md)

## Common Variants

- **9:16 ショート版** (X/Reels): `W,H = 1080, 1920`、ナレを 60 秒に圧縮
- **字幕焼き込み**: ffmpeg `subtitles=final.srt` フィルタで動画に焼く
- **BGM 追加**: 別 mp3 を低音量でミックス (`-filter_complex amix`)
- **章/コース化** (学習教材): script.json を章単位に分割、共通イントロ/アウトロ
- **多言語版**: `voice` 切替 + script を翻訳

## Done Criteria

- [ ] `<out>/output/final.mp4` (またはアバター版) が再生でき、音声と映像がズレない
- [ ] スライド本文 28pt 以上 / タイトル 56pt 以上で可読
- [ ] ナレが入力の主要メッセージを正しく反映
- [ ] `final.srt` がナレーションと同期
- [ ] 入力ソースの著作権を侵害していない (本文丸読みでなく要約 + 引用範囲)
- [ ] (アバター時) GPU メモリ溢れ無く完走、口パクが極端にズレていない
