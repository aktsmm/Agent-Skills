# Customization

## 声 (edge-tts voice)

| voice                            | 性別/言語         | 印象                  |
| -------------------------------- | ----------------- | --------------------- |
| `ja-JP-NanamiNeural`             | 女性・日本語      | 落ち着き・標準 (既定) |
| `ja-JP-KeitaNeural`              | 男性・日本語      | やや低め・解説向き    |
| `en-US-AvaMultilingualNeural`    | 女性・英語/多言語 | 自然・推奨            |
| `en-US-AndrewMultilingualNeural` | 男性・英語/多言語 | 落ち着き              |

全リスト: `edge-tts --list-voices`。edge-tts の日本語音声は Nanami / Keita のみ（`ja-JP-AoiNeural` などは Azure Speech 側の音声）。

## 配色変更

`scripts/build_video.py` 上部の定数を編集:

```python
BG     = (15, 23, 42)    # 背景
ACCENT = (56, 189, 248)  # アクセント (帯・下線・ドット)
TEXT   = (241, 245, 249) # 本文
MUTED  = (148, 163, 184) # 補助テキスト
```

ブランドカラーで上書きすればOK。

## アスペクト比

`W, H` を変えるだけ:

- 16:9 横 (既定): `1920, 1080`
- 9:16 縦 (X/Reels): `1080, 1920`
- 1:1 正方形 (Instagram): `1080, 1080`

縦版にする場合は `bullets` を短く (各 20 字以内) しないと折り返し過多になる。

## フォント

`FONT_B` / `FONT_R` を差し替え。Windows なら:

- BIZ UDGothic (既定)
- `YuGothB.ttc` / `YuGothR.ttc` (Yu Gothic)
- `meiryob.ttc` / `meiryo.ttc` (Meiryo)

## 字幕焼き込み / BGM ミックス

コマンドは [ffmpeg-advanced-filters.md](ffmpeg-advanced-filters.md) を参照。
