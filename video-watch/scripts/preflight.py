#!/usr/bin/env python3
"""Check local dependencies for the video-watch skill."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys


def version(command: str) -> str:
    try:
        completed = subprocess.run(
            [command, "--version"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        return "missing"
    first_line = (completed.stdout or completed.stderr).splitlines()
    return first_line[0] if first_line else "present"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check dependencies for video-watch.")
    parser.add_argument("--url-mode", action="store_true", help="Require yt-dlp for URL inputs")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    requirements = ["ffmpeg", "ffprobe"]
    optional = ["yt-dlp"]
    missing = []

    print("video-watch dependency check")
    print(f"python: {sys.version.split()[0]}")
    for command in requirements:
        path = shutil.which(command)
        state = version(command) if path else "missing"
        print(f"{command}: {state}")
        if not path:
            missing.append(command)
    for command in optional:
        path = shutil.which(command)
        state = version(command) if path else "missing"
        suffix = " (required for URL mode)"
        print(f"{command}: {state}{suffix}")
        if args.url_mode and not path:
            missing.append(command)

    if missing:
        print("\nMissing dependencies:")
        for command in missing:
            print(f"- {command}")
        print("\nWindows hints:")
        print("winget install --id Gyan.FFmpeg -e")
        print("python -m pip install --user yt-dlp")
        return 1

    print("\nOK: required dependencies are available on PATH.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
