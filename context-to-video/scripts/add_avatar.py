"""Generate SadTalker avatar clips for every narration in <project>/audio/
and composite the final mp4 with avatar in bottom-right corner.

Prereqs (see references/avatar.md):
  - <project>/avatar/SadTalker/ cloned
  - <project>/avatar/venv/ Python 3.10 + torch cu121 + deps
  - <project>/avatar/SadTalker/checkpoints/ populated
  - ffmpeg + ffprobe in PATH

Usage:
    python add_avatar.py --project D:\path\to\project --face D:\path\to\face.jpg
"""
from __future__ import annotations
import argparse
import os
import shutil
import subprocess
from pathlib import Path


def run(cmd, **kw):
    print(">>", " ".join(str(c) for c in cmd))
    return subprocess.run(cmd, check=True, **kw)


def generate_avatar_clip(py: Path, sadtalker: Path, face: Path, audio: Path, out_dir: Path,
                         size: int = 256, enhancer: str | None = None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / f"_{audio.stem}"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir()
    cmd = [
        str(py), "inference.py",
        "--driven_audio", str(audio),
        "--source_image", str(face),
        "--result_dir", str(tmp),
        "--still", "--preprocess", "full", "--size", str(size),
    ]
    if enhancer:
        cmd += ["--enhancer", enhancer]
    run(cmd, cwd=sadtalker)
    mp4s = sorted(tmp.glob("*.mp4"))
    if not mp4s:
        raise RuntimeError(f"no mp4 in {tmp}")
    final_clip = out_dir / f"{audio.stem}.mp4"
    shutil.move(str(mp4s[-1]), final_clip)
    shutil.rmtree(tmp, ignore_errors=True)
    return final_clip


def concat_clips(clips: list[Path], out: Path) -> None:
    list_file = out.parent / "_avatar_list.txt"
    list_file.write_text("".join(f"file '{p.as_posix()}'\n" for p in clips), encoding="utf-8")
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-an", str(out),
    ])


def overlay_square(base: Path, avatar: Path, out: Path, size: int = 360, margin: int = 48) -> None:
    run([
        "ffmpeg", "-y", "-i", str(base), "-i", str(avatar),
        "-filter_complex",
        f"[1:v]scale={size}:-1[av];[0:v][av]overlay=W-w-{margin}:H-h-{margin}:shortest=1[v]",
        "-map", "[v]", "-map", "0:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "copy",
        str(out),
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, type=Path)
    ap.add_argument("--face", type=Path, default=None,
                    help="顔画像。省略時は <project>/avatar/input/face.jpg")
    ap.add_argument("--size", type=int, default=256, choices=[256, 512])
    ap.add_argument("--enhancer", default=None, help="例: gfpgan (512 推奨)")
    ap.add_argument("--ffmpeg-dir", default=None,
                    help="ffmpeg/ffprobe を含むディレクトリ。未指定なら PATH に依存")
    args = ap.parse_args()

    project: Path = args.project
    avatar_root = project / "avatar"
    sadtalker = avatar_root / "SadTalker"
    py = avatar_root / "venv" / "Scripts" / "python.exe"
    face = args.face or (avatar_root / "input" / "face.jpg")
    audio_dir = project / "audio"
    clips_dir = avatar_root / "clips"
    base_mp4 = project / "output" / "final.mp4"
    out_mp4 = project / "output" / "final_with_avatar.mp4"

    for p in (sadtalker, py, face, audio_dir, base_mp4):
        if not p.exists():
            raise SystemExit(f"missing: {p}")

    if args.ffmpeg_dir:
        os.environ["PATH"] = args.ffmpeg_dir + os.pathsep + os.environ["PATH"]

    audios = sorted(audio_dir.glob("audio_*.mp3"))
    print(f"[info] {len(audios)} narration files")

    clips: list[Path] = []
    for a in audios:
        target = clips_dir / f"{a.stem}.mp4"
        if target.exists():
            print(f"[skip] {target.name}")
            clips.append(target)
            continue
        c = generate_avatar_clip(py, sadtalker, face, a, clips_dir,
                                 size=args.size, enhancer=args.enhancer)
        clips.append(c)

    concat = clips_dir / "_avatar_full.mp4"
    concat_clips(clips, concat)
    overlay_square(base_mp4, concat, out_mp4)
    print(f"[ok] wrote {out_mp4}")


if __name__ == "__main__":
    main()
