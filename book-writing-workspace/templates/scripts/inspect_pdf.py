from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect a PDF file.")
    parser.add_argument("pdf_path")
    parser.add_argument("--pages", type=int, default=6)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reader = PdfReader(str(Path(args.pdf_path)))
    print(f"pages={len(reader.pages)}")
    for index in range(min(args.pages, len(reader.pages))):
        text = (reader.pages[index].extract_text() or "").replace("\n", " ")
        print(f"PAGE {index + 1}: {text[:300]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())