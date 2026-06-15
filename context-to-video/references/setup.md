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

## アバター(SadTalker)を使う場合の追加 PATH 注意

ffprobe が pydub に必要だが winget でインストールしてもセッションごとに PATH が引き継がれないことがある。スクリプト先頭で明示する:

```powershell
$ffdir = (Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Gyan.FFmpeg*" -Recurse -Filter ffmpeg.exe | Select-Object -First 1).Directory.FullName
$env:PATH = "$ffdir;$env:PATH"
```

Python から呼ぶ場合は `os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ["PATH"]` を実行ファイルの先頭で行う。

## トラブル

| 症状 | 対処 |
|---|---|
| `edge-tts` で 401/403 | 一時的なエンドポイント制限。数分待つか別マシン |
| 音声が無音 | text が空文字。`narration` を確認 |
| ffmpeg `Conversion failed` | スライド PNG サイズ不一致。1920x1080 で再生成 |
| 文字化け | `script.json` を UTF-8 (BOM 無し) で保存 |
| 日本語フォント崩れ | `.ttc` パスを絶対指定、別フォントへフォールバック |
| concat で映像/音声ズレ | セグメント mp4 の fps と sample rate を揃える (本スクリプトは 30fps / 44.1kHz aac で統一済み) |
| `uv venv` 直後の python で `No module named pip` | `uv pip install --python <venv>\Scripts\python.exe <pkg>` を使う(`-m pip` ではなく `uv pip`) |
| `pydub` が `FileNotFoundError: ffprobe` | ffmpeg だけでは不足。ffprobe を含む完全版を winget でインストール (`Gyan.FFmpeg`) し、PATH を明示 |
| `Failed to initialize NumPy: _ARRAY_API not found` | torch 2.1.2 cu121 を入れると NumPy 2.x が自動で入る。`pip install "numpy==1.23.5"` で強制ダウングレード |
