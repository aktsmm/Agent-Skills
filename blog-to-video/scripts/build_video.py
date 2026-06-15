"""Blog-to-video pipeline.

Reads <project>/notes/script.json, renders slides (PNG), generates narration
(edge-tts), and assembles a single mp4 with a synced SRT subtitle file.

Usage:
    python build_video.py --project D:\\path\\to\\project [--voice ja-JP-NanamiNeural]

The project folder must contain notes/script.json. Output is written to
slides/, audio/, and output/ under the same project folder.
"""
from __future__ import annotations
import argparse
import asyncio
import json
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import edge_tts
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1920, 1080
BG = (15, 23, 42)
ACCENT = (56, 189, 248)
TEXT = (241, 245, 249)
MUTED = (148, 163, 184)

FONT_B = r"C:\Windows\Fonts\BIZ-UDGothicB.ttc"
FONT_R = r"C:\Windows\Fonts\BIZ-UDGothicR.ttc"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def draw_wrapped(draw, text, xy, fnt, fill, max_width):
    x, y = xy
    line = ""
    line_h = fnt.size + 12
    for ch in text:
        test = line + ch
        if draw.textlength(test, font=fnt) > max_width and line:
            draw.text((x, y), line, font=fnt, fill=fill)
            y += line_h
            line = ch
        else:
            line = test
    if line:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def render_title(slide, out, page, total):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 24, H], fill=ACCENT)
    d.text((96, 80), slide["source"], font=font(FONT_R, 32), fill=MUTED)
    y = 280
    for line in slide["title"].split("\n"):
        d.text((96, y), line, font=font(FONT_B, 110), fill=TEXT)
        y += 130
    d.text((96, y + 40), slide["subtitle"], font=font(FONT_R, 54), fill=ACCENT)
    d.text((96, H - 80), f"{page}/{total}", font=font(FONT_R, 28), fill=MUTED)
    img.save(out)


def render_content(slide, out, page, total, title_text):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 24, H], fill=ACCENT)
    d.text((96, 60), title_text, font=font(FONT_R, 28), fill=MUTED)
    d.text((96, 130), slide["heading"], font=font(FONT_B, 76), fill=TEXT)
    d.rectangle([96, 230, 360, 238], fill=ACCENT)
    y = 320
    bf = font(FONT_R, 52)
    for b in slide["bullets"]:
        d.ellipse([100, y + 22, 130, y + 52], fill=ACCENT)
        y = draw_wrapped(d, b, (160, y), bf, TEXT, W - 220) + 30
    d.text((96, H - 80), f"{page}/{total}", font=font(FONT_R, 28), fill=MUTED)
    img.save(out)


async def tts(text, out, voice):
    await edge_tts.Communicate(text, voice=voice).save(str(out))


def ffmpeg_duration(path: Path) -> float:
    proc = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", proc.stderr)
    if not m:
        raise RuntimeError(f"no duration in: {proc.stderr}")
    h, mn, s = m.groups()
    return int(h) * 3600 + int(mn) * 60 + float(s)


def fmt_srt(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t - h * 3600 - m * 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, type=Path)
    ap.add_argument("--voice", default="ja-JP-NanamiNeural")
    args = ap.parse_args()

    root: Path = args.project
    script_file = root / "notes" / "script.json"
    if not script_file.exists():
        raise SystemExit(f"missing {script_file}")

    slides_dir = root / "slides"
    audio_dir = root / "audio"
    out_dir = root / "output"
    for d in (slides_dir, audio_dir, out_dir):
        d.mkdir(parents=True, exist_ok=True)

    data = json.loads(script_file.read_text(encoding="utf-8"))
    slides = data["slides"]
    total = len(slides) + 1

    render_title(
        {"title": data["title"], "subtitle": data["subtitle"], "source": data["source"]},
        slides_dir / "slide_00.png", 1, total,
    )
    brand = data["title"].replace("\n", " / ")
    for i, s in enumerate(slides, start=1):
        render_content(s, slides_dir / f"slide_{i:02d}.png", i + 1, total, brand)
    print(f"[ok] rendered {total} slides")

    async def gen_all():
        intro = data["title"].replace("\n", "、") + "。" + data["subtitle"] + "。"
        await tts(intro, audio_dir / "audio_00.mp3", args.voice)
        for i, s in enumerate(slides, start=1):
            await tts(s["narration"], audio_dir / f"audio_{i:02d}.mp3", args.voice)
    asyncio.run(gen_all())
    print(f"[ok] generated {total} audio files")

    seg_dir = out_dir / "_segments"
    if seg_dir.exists():
        shutil.rmtree(seg_dir)
    seg_dir.mkdir(parents=True)
    durations, segs = [], []
    for i in range(total):
        png = slides_dir / f"slide_{i:02d}.png"
        mp3 = audio_dir / f"audio_{i:02d}.mp3"
        dur = ffmpeg_duration(mp3) + 0.4
        durations.append(dur)
        seg = seg_dir / f"seg_{i:02d}.mp4"
        subprocess.run([
            FFMPEG, "-y", "-loop", "1", "-i", str(png), "-i", str(mp3),
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-t", f"{dur:.3f}",
            "-vf", "scale=1920:1080,fps=30", str(seg),
        ], check=True, capture_output=True)
        segs.append(seg)

    list_file = seg_dir / "list.txt"
    list_file.write_text("".join(f"file '{p.as_posix()}'\n" for p in segs), encoding="utf-8")
    final = out_dir / "final.mp4"
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
                    "-c", "copy", str(final)], check=True, capture_output=True)
    print(f"[ok] wrote {final}")

    captions = [data["title"].replace("\n", " — ") + " / " + data["subtitle"]]
    captions += [s["narration"] for s in slides]
    lines, t = [], 0.0
    for idx, (cap, dur) in enumerate(zip(captions, durations), start=1):
        lines.append(f"{idx}\n{fmt_srt(t)} --> {fmt_srt(t + dur)}\n{cap}\n")
        t += dur
    (out_dir / "final.srt").write_text("\n".join(lines), encoding="utf-8")
    print(f"[ok] wrote SRT, total {t:.1f}s")


if __name__ == "__main__":
    main()
