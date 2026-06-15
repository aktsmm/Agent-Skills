# Setup

## 必須

```powershell
pip install edge-tts imageio-ffmpeg pillow
```

- `edge-tts`: Edge の Neural 音声を Python から呼ぶ非公式クライアント
- `imageio-ffmpeg`: ffmpeg バイナリを Python パッケージとして同梱 (システムインストール不要)
- `pillow`: 画像生成

## フォント (Windows)

BIZ UDGothic は Windows 10/11 にプリインストール:
- `C:\Windows\Fonts\BIZ-UDGothicB.ttc` (Bold)
- `C:\Windows\Fonts\BIZ-UDGothicR.ttc` (Regular)

無い場合は Yu Gothic (`YuGothB.ttc` / `YuGothR.ttc`) に差し替え可。`scripts/build_video.py` の `FONT_B` / `FONT_R` を変更。

## 動作確認

```powershell
python -c "import edge_tts, imageio_ffmpeg, PIL; print('ok')"
```

## トラブル

| 症状 | 対処 |
|---|---|
| `edge-tts` で 401/403 | 一時的なエンドポイント制限。数分待つか別マシン |
| 音声が無音 | text が空文字。`narration` を確認 |
| ffmpeg `Conversion failed` | スライド PNG サイズ不一致。1920x1080 で再生成 |
| 文字化け | `script.json` を UTF-8 (BOM 無し) で保存 |
| 日本語フォント崩れ | `.ttc` パスを絶対指定、別フォントへフォールバック |
| concat で映像/音声ズレ | セグメント mp4 の fps と sample rate を揃える (本スクリプトは 30fps / 44.1kHz aac で統一済み) |
