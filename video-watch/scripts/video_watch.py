#!/usr/bin/env python3
"""Create Copilot-friendly artifacts from a video URL or local video file."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse


DETAIL_DEFAULTS = {
    "transcript": 0,
    "efficient": 12,
    "balanced": 24,
    "token-burner": 60,
}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}
SIDECAR_EXTENSIONS = [".vtt", ".srt", ".txt", ".md"]


def run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def parse_time(value: str | None) -> float | None:
    if value is None:
        return None
    parts = value.strip().split(":")
    try:
        numbers = [float(part) for part in parts]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid time value: {value}") from exc
    if len(numbers) == 1:
        return numbers[0]
    if len(numbers) == 2:
        return numbers[0] * 60 + numbers[1]
    if len(numbers) == 3:
        return numbers[0] * 3600 + numbers[1] * 60 + numbers[2]
    raise argparse.ArgumentTypeError(f"invalid time value: {value}")


def format_time(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def is_url(source: str) -> bool:
    parsed = urlparse(source)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def source_label(source: str) -> str:
    if is_url(source):
        parsed = urlparse(source)
        host = re.sub(r"[^a-zA-Z0-9.-]+", "-", parsed.netloc).strip("-")
        stem = re.sub(r"[^a-zA-Z0-9._-]+", "-", Path(parsed.path).stem or "video").strip("-")
        return f"{host}-{stem}"[:80] or "video-url"
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", Path(source).stem).strip("-")[:80] or "video-file"


def source_display(source: str) -> str:
    if not is_url(source):
        return Path(source).name
    parsed = urlparse(source)
    display = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        display += "?REDACTED_QUERY"
    return display


def dependency(command: str) -> bool:
    return shutil.which(command) is not None


def warn_sensitive_url(source: str) -> list[str]:
    if not is_url(source):
        return []
    parsed = urlparse(source)
    query = parsed.query.lower()
    sensitive_keys = ["token", "access_token", "sig", "signature", "key", "auth", "jwt"]
    if any(key in query for key in sensitive_keys):
        return ["URL query contains token-like parameters. Do not share generated artifacts publicly without review."]
    return []


def ffprobe_duration(video_path: Path) -> float | None:
    completed = run([
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ])
    if completed.returncode != 0:
        return None
    try:
        return float(completed.stdout.strip())
    except ValueError:
        return None


def normalize_vtt(text: str) -> str:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line == "WEBVTT" or line.startswith("NOTE"):
            continue
        if "-->" in line:
            lines.append(f"\n[{line}]")
            continue
        if re.fullmatch(r"\d+", line):
            continue
        cleaned = re.sub(r"<[^>]+>", "", line)
        if cleaned:
            lines.append(cleaned)
    return "\n".join(lines).strip()


def find_sidecar_transcript(video_path: Path) -> Path | None:
    for extension in SIDECAR_EXTENSIONS:
        candidate = video_path.with_suffix(extension)
        if candidate.exists():
            return candidate
    return None


def extract_subtitles(source: str, run_dir: Path, warnings: list[str], transcript_file: str | None = None) -> tuple[str, str]:
    transcript_path = run_dir / "transcript.md"
    if transcript_file:
        source_path = Path(transcript_file).expanduser().resolve()
        if not source_path.exists():
            warnings.append("Explicit transcript file was not found; transcript is unavailable.")
            transcript_path.write_text(
                "Transcript unavailable. The explicit transcript file was not found.\n",
                encoding="utf-8",
            )
            return "unavailable", "external-file"
        raw = source_path.read_text(encoding="utf-8", errors="replace")
        text = normalize_vtt(raw) if source_path.suffix.lower() in {".vtt", ".srt"} else raw.strip()
        transcript_path.write_text(text or "Explicit transcript file was empty.\n", encoding="utf-8")
        return "available", "external-file"

    if is_url(source):
        if not dependency("yt-dlp"):
            warnings.append("yt-dlp is unavailable; transcript extraction was skipped.")
            transcript_path.write_text(
                "Transcript unavailable. yt-dlp is not installed, so URL captions were not checked.\n",
                encoding="utf-8",
            )
            return "unavailable", "none"
        subs_dir = run_dir / "subtitles"
        subs_dir.mkdir(parents=True, exist_ok=True)
        completed = run([
            "yt-dlp",
            "--no-playlist",
            "--skip-download",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs",
            "ja.*,en.*",
            "--sub-format",
            "vtt",
            "-o",
            str(subs_dir / "subtitle.%(ext)s"),
            source,
        ])
        if completed.returncode != 0:
            warnings.append("yt-dlp subtitle extraction failed; transcript is unavailable.")
        subtitle_files = sorted(subs_dir.glob("*.vtt"))
        if subtitle_files:
            text = normalize_vtt(subtitle_files[0].read_text(encoding="utf-8", errors="replace"))
            transcript_path.write_text(text or "Transcript file was empty after VTT cleanup.\n", encoding="utf-8")
            return "available", "yt-dlp-captions"
    else:
        sidecar = find_sidecar_transcript(Path(source))
        if sidecar:
            raw = sidecar.read_text(encoding="utf-8", errors="replace")
            text = normalize_vtt(raw) if sidecar.suffix.lower() in {".vtt", ".srt"} else raw.strip()
            transcript_path.write_text(text or "Transcript sidecar was empty.\n", encoding="utf-8")
            return "available", "sidecar"

    transcript_path.write_text(
        "Transcript unavailable. No captions or local sidecar transcript were found.\n",
        encoding="utf-8",
    )
    return "unavailable", "none"


def download_video(source: str, run_dir: Path, warnings: list[str]) -> Path | None:
    if not is_url(source):
        path = Path(source).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"local video not found: {source}")
        if path.suffix.lower() not in VIDEO_EXTENSIONS:
            warnings.append(f"Local file extension {path.suffix} is not a common video extension.")
        return path

    video_dir = run_dir / "download"
    video_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(video_dir / "video.%(ext)s")
    completed = run([
        "yt-dlp",
        "--no-playlist",
        "-f",
        "bv*[height<=720]+ba/b[height<=720]/best[height<=720]/best",
        "-o",
        output_template,
        source,
    ])
    if completed.returncode != 0:
        warnings.append("yt-dlp video download failed; visual artifacts were not generated.")
        return None
    videos = [path for path in video_dir.iterdir() if path.suffix.lower() in VIDEO_EXTENSIONS]
    if not videos:
        warnings.append("yt-dlp completed but no supported video file was found.")
        return None
    return videos[0]


def extract_frames(
    video_path: Path,
    run_dir: Path,
    max_frames: int,
    resolution: int,
    start: float | None,
    end: float | None,
    warnings: list[str],
) -> list[dict[str, str]]:
    frames_dir = run_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    duration = ffprobe_duration(video_path)
    if duration is None:
        warnings.append("ffprobe could not read duration; using a conservative 60 second sampling window.")
        duration = 60.0
    clip_start = start or 0.0
    clip_end = end if end is not None else duration
    clip_end = min(clip_end, duration)
    clip_duration = max(0.1, clip_end - clip_start)
    fps = min(2.0, max_frames / clip_duration)
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        str(clip_start),
        "-i",
        str(video_path),
        "-t",
        str(clip_duration),
        "-vf",
        f"fps={fps},scale={resolution}:-1:force_original_aspect_ratio=decrease",
        "-frames:v",
        str(max_frames),
        str(frames_dir / "frame_%04d.jpg"),
    ]
    completed = run(command)
    if completed.returncode != 0:
        warnings.append("ffmpeg frame extraction failed.")
        return []
    frame_paths = sorted(frames_dir.glob("frame_*.jpg"))
    frame_rows = []
    for index, frame_path in enumerate(frame_paths):
        approx_time = clip_start + (index / fps if fps else 0)
        frame_rows.append({"file": frame_path.relative_to(run_dir).as_posix(), "approx_time": format_time(approx_time)})
    return frame_rows


def create_contact_sheet(run_dir: Path, frame_count: int, warnings: list[str]) -> str | None:
    if frame_count == 0:
        return None
    cols = min(4, max(1, math.ceil(math.sqrt(frame_count))))
    rows = math.ceil(frame_count / cols)
    output = run_dir / "contact-sheet.jpg"
    completed = run([
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-framerate",
        "1",
        "-i",
        str(run_dir / "frames" / "frame_%04d.jpg"),
        "-vf",
        f"tile={cols}x{rows}:margin=8:padding=4",
        "-frames:v",
        "1",
        str(output),
    ])
    if completed.returncode != 0:
        warnings.append("ffmpeg contact sheet generation failed.")
        return None
    return output.name


def write_frame_index(run_dir: Path, frames: list[dict[str, str]]) -> None:
    lines = ["# Frame Index", ""]
    if not frames:
        lines.append("No frames were generated.")
    else:
        lines.append("| Frame | Approx time |")
        lines.append("| --- | --- |")
        for frame in frames:
            lines.append(f"| {frame['file']} | {frame['approx_time']} |")
    (run_dir / "frame-index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_prompt(run_dir: Path, question: str, transcript_status: str, transcript_backend: str, contact_sheet: str | None) -> None:
    lines = [
        "# Copilot Video Analysis Prompt",
        "",
        f"User question: {question or '(no specific question provided)'}",
        "",
        "Read artifacts in this order:",
        "1. manifest.json",
        "2. transcript.md",
        "3. frame-index.md",
    ]
    if contact_sheet:
        lines.append(f"4. {contact_sheet}")
    lines.extend([
        "5. Selected frame files under frames/ only when needed",
        "",
        f"Transcript status: {transcript_status} (backend: {transcript_backend})",
        "Ground the answer in the transcript and visible frames. Say when evidence is missing or sampling is sparse.",
    ])
    (run_dir / "prompt.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare Copilot-friendly video analysis artifacts.")
    parser.add_argument("source", help="Video URL or local video path")
    parser.add_argument("--question", default="", help="Question Copilot should answer from the artifacts")
    parser.add_argument("--detail", choices=DETAIL_DEFAULTS.keys(), default="balanced")
    parser.add_argument("--max-frames", type=int, default=None)
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--start", type=parse_time, default=None, help="Start time as SS, MM:SS, or HH:MM:SS")
    parser.add_argument("--end", type=parse_time, default=None, help="End time as SS, MM:SS, or HH:MM:SS")
    parser.add_argument("--transcript-file", default=None, help="Use an existing transcript file instead of URL captions or sidecar discovery")
    parser.add_argument("--metadata-only", action="store_true", help="Create transcript/manifest/prompt without downloading or extracting frames")
    parser.add_argument("--out-dir", default=None, help="Exact output directory for this run")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    warnings = warn_sensitive_url(args.source)
    max_frames = args.max_frames if args.max_frames is not None else DETAIL_DEFAULTS[args.detail]
    needs_frames = args.detail != "transcript" and max_frames > 0 and not args.metadata_only

    if args.end is not None and args.start is not None and args.end <= args.start:
        raise SystemExit("--end must be greater than --start")
    if needs_frames:
        for command in ["ffmpeg", "ffprobe"]:
            if not dependency(command):
                raise SystemExit(f"missing dependency: {command}. Run scripts/preflight.py")
    if is_url(args.source) and needs_frames and not dependency("yt-dlp"):
        raise SystemExit("missing dependency: yt-dlp. Run scripts/preflight.py")

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    default_dir = Path.cwd() / "output" / "video-watch" / f"{timestamp}-{source_label(args.source)}"
    run_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else default_dir
    run_dir.mkdir(parents=True, exist_ok=True)

    transcript_status, transcript_backend = extract_subtitles(args.source, run_dir, warnings, args.transcript_file)
    frames: list[dict[str, str]] = []
    contact_sheet = None
    video_path: Path | None = None

    if needs_frames:
        video_path = download_video(args.source, run_dir, warnings)
        if video_path:
            frames = extract_frames(video_path, run_dir, max_frames, args.resolution, args.start, args.end, warnings)
            contact_sheet = create_contact_sheet(run_dir, len(frames), warnings)

    write_frame_index(run_dir, frames)
    write_prompt(run_dir, args.question, transcript_status, transcript_backend, contact_sheet)
    duration_source = video_path
    if duration_source is None and not is_url(args.source):
        local_source = Path(args.source).expanduser().resolve()
        duration_source = local_source if local_source.exists() else None
    duration_seconds = ffprobe_duration(duration_source) if duration_source and dependency("ffprobe") else None

    manifest = {
        "created_at": timestamp,
        "source_type": "url" if is_url(args.source) else "local-file",
        "source_display": source_display(args.source),
        "source_query_redacted": bool(urlparse(args.source).query) if is_url(args.source) else False,
        "detail": args.detail,
        "question": args.question,
        "time_window": {"start": format_time(args.start or 0), "end": format_time(args.end) if args.end else None},
        "duration_seconds": round(duration_seconds, 3) if duration_seconds is not None else None,
        "artifacts": {
            "prompt": "prompt.md",
            "transcript": "transcript.md",
            "frame_index": "frame-index.md",
            "contact_sheet": contact_sheet,
            "frames": [frame["file"] for frame in frames],
        },
        "transcript_status": transcript_status,
        "transcript_backend": transcript_backend,
        "frame_count": len(frames),
        "warnings": warnings,
        "limitations": [
            "Frames are sampled and may miss short events unless a focused --start/--end window is used.",
            "Transcript may be unavailable when captions or sidecar files are missing.",
        ],
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({"run_dir": str(run_dir), "manifest": str(run_dir / "manifest.json"), "warnings": warnings}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
