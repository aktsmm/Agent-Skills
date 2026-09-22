#!/usr/bin/env python3
"""Validate an animated infographic and create representative QA artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--expected-width", type=int)
    parser.add_argument("--expected-height", type=int)
    parser.add_argument("--min-frames", type=int, default=2)
    parser.add_argument(
        "--timing-mode", choices=("illustrative", "measured", "mixed"), required=True
    )
    parser.add_argument("--measured-ms", type=int)
    parser.add_argument("--duration-tolerance", type=float, default=0.1)
    parser.add_argument("--contact-sheet", type=Path)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def font(size: int) -> ImageFont.ImageFont:
    for path in (
        Path("C:/Windows/Fonts/YuGothM.ttc"),
        Path("C:/Windows/Fonts/meiryo.ttc"),
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def fit(image: Image.Image, width: int, height: int) -> Image.Image:
    copy = image.convert("RGB")
    copy.thumbnail((width, height))
    canvas = Image.new("RGB", (width, height), "#202020")
    canvas.paste(copy, ((width - copy.width) // 2, (height - copy.height) // 2))
    return canvas


def main() -> None:
    args = parse_args()
    image = Image.open(args.input)
    frame_count = getattr(image, "n_frames", 1)
    if not getattr(image, "is_animated", False) or frame_count < args.min_frames:
        raise SystemExit(f"Expected at least {args.min_frames} animated frames, got {frame_count}.")
    if args.expected_width and image.width != args.expected_width:
        raise SystemExit(f"Expected width {args.expected_width}, got {image.width}.")
    if args.expected_height and image.height != args.expected_height:
        raise SystemExit(f"Expected height {args.expected_height}, got {image.height}.")

    durations: list[int] = []
    variances: list[float] = []
    blank_frames: list[int] = []
    samples: list[tuple[int, Image.Image]] = []
    sample_indices = sorted({0, frame_count // 2, frame_count - 1})
    for index in range(frame_count):
        image.seek(index)
        frame = image.convert("RGB")
        durations.append(int(image.info.get("duration", 0)))
        statistics = ImageStat.Stat(frame)
        variance = max(statistics.var)
        variances.append(variance)
        if variance <= 1 and (
            all(value >= 250 for value in statistics.mean)
            or all(value <= 5 for value in statistics.mean)
        ):
            blank_frames.append(index)
        if index in sample_indices:
            samples.append((index, frame.copy()))
    if blank_frames:
        raise SystemExit(f"Blank or nearly blank frames found: {blank_frames}.")

    total_duration = sum(durations)
    if args.timing_mode == "measured":
        if args.measured_ms is None:
            raise SystemExit("--measured-ms is required for measured timing mode.")
        tolerance = max(1, round(args.measured_ms * args.duration_tolerance))
        if abs(total_duration - args.measured_ms) > tolerance:
            raise SystemExit(
                f"GIF duration {total_duration} ms differs from measured {args.measured_ms} ms "
                f"by more than {tolerance} ms."
            )

    if args.contact_sheet:
        thumb_width, thumb_height, label_height = 400, 225, 32
        sheet = Image.new("RGB", (thumb_width * len(samples), thumb_height + label_height), "#111111")
        draw = ImageDraw.Draw(sheet)
        for column, (index, frame) in enumerate(samples):
            left = column * thumb_width
            sheet.paste(fit(frame, thumb_width, thumb_height), (left, 0))
            draw.text((left + 8, thumb_height + 6), f"frame {index}/{frame_count - 1}", font=font(14), fill="white")
        args.contact_sheet.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(args.contact_sheet, quality=90)

    report = {
        "input": args.input.name,
        "size": [image.width, image.height],
        "frames": frame_count,
        "duration_ms": total_duration,
        "timing_mode": args.timing_mode,
        "measured_ms": args.measured_ms,
        "sample_indices": sample_indices,
        "minimum_frame_variance": min(variances),
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
