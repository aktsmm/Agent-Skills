# Setup Guide - Receipt OCR Sorter

OCR領収書仕分けツールの環境構築手順。

## 必要要件

| 要件 | バージョン | 備考 |
|------|-----------|------|
| Python | 3.11+ | 3.12推奨 |
| GPU | CUDA対応 | 任意（CPUでも動作するが遅い） |
| ffmpeg | 最新安定版 | 動画変換時のみ |
| ストレージ | ~3GB | モデルキャッシュ含む |

## Step 1: Python venv 作成

```powershell
python -m venv C:\Users\vainf\ocr_env
C:\Users\vainf\ocr_env\Scripts\Activate.ps1
```

## Step 2: CUDA版 PyTorch インストール（GPU利用時）

```powershell
# まず既存のCPU版を削除
pip uninstall torch torchvision torchaudio -y

# CUDA 12.4 版をインストール
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

確認:
```powershell
python -c "import torch; print('CUDA:', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

## Step 3: Surya OCR + 依存パッケージ

```powershell
pip install surya-ocr Pillow jaconv
```

## Step 4: ffmpeg（動画対応時のみ）

```powershell
winget install Gyan.FFmpeg
```

確認:
```powershell
ffmpeg -version
```

## Step 5: receipt_sorter.py 配置

`receipt_sorter.py` をワークスペースルートに配置する。
Skill の `references/receipt_sorter.py` にリファレンスコピーがある。

## 環境変数

| 変数 | 値 | 説明 |
|------|-----|------|
| `PYTHONUTF8` | `1` | Python UTF-8 出力強制 |
| `UV_CACHE_DIR` | `C:\Temp\uv_cache` | キャッシュ先（任意） |

```powershell
$env:PYTHONUTF8='1'
$env:UV_CACHE_DIR='C:\Temp\uv_cache'
```

## トラブルシューティング

| 問題 | 解決策 |
|------|--------|
| `torch.cuda.is_available()` が False | Step 2 の CUDA版 PyTorch を再インストール |
| `ModuleNotFoundError: surya` | `pip install surya-ocr` を実行 |
| `WinError 32` ファイルロック | `receipt_sorter.py` 最新版を使用（画像ハンドル自動クローズ対応済み） |
| OCRが遅い | GPU未使用の可能性。CUDA確認コマンドで検証 |
| 文字化け | `$env:PYTHONUTF8='1'` を設定 |
