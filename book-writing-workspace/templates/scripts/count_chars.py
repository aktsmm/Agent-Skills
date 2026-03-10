# -*- coding: utf-8 -*-
"""
Character Counter Script

Count characters in Markdown files under 02_contents/.
Excludes Markdown syntax such as headings, code blocks, and links.
"""

from collections import defaultdict
from pathlib import Path
import re
import sys


def clean_markdown(text: str) -> str:
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\|", "", text)
    text = re.sub(r"^[-:]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[-*_]{3,}$", "", text, flags=re.MULTILINE)
    text = re.sub(r"[\s\r\n\t　]", "", text)
    return text


def get_file_type(filename: str) -> tuple[str, str]:
    if "Column" in filename or "コラム" in filename:
        return "Column", "2,000-3,000"
    if re.match(r"^ch\d+-00_", filename):
        return "Intro", "300-500"
    return "Main", "3,000-5,000"


def check_status(char_count: int, file_type: str) -> str:
    ranges = {
        "Column": (1500, 3500),
        "Intro": (200, 700),
        "Main": (2000, 6000),
    }
    min_val, max_val = ranges.get(file_type, (2000, 6000))
    if char_count < min_val:
        return "⚠️ Under"
    if char_count > max_val:
        return "⚠️ Over"
    return "✅ OK"


def resolve_base_path() -> Path | None:
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    cwd = Path.cwd()
    if (cwd / "02_contents").exists():
        return cwd / "02_contents"
    if (cwd.parent / "02_contents").exists():
        return cwd.parent / "02_contents"
    return None


def main() -> int:
    base_path = resolve_base_path()
    if base_path is None:
        print("Error: Could not find 02_contents/ folder")
        print("Usage: python count_chars.py [path]")
        return 1
    if not base_path.exists():
        print(f"Error: Path not found: {base_path}")
        return 1

    results = []
    chapter_totals = defaultdict(lambda: {"count": 0, "files": 0})

    for md_file in sorted(base_path.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        char_count = len(clean_markdown(content))
        relative_path = md_file.relative_to(base_path)
        chapter = relative_path.parts[0] if relative_path.parts else "Unknown"
        file_type, target = get_file_type(md_file.name)
        status = check_status(char_count, file_type)

        results.append(
            {
                "chapter": chapter,
                "file_type": file_type,
                "char_count": char_count,
                "target": target,
                "status": status,
                "relative_path": relative_path.as_posix(),
            }
        )
        chapter_totals[chapter]["count"] += char_count
        chapter_totals[chapter]["files"] += 1

    print("## Chapter Summary\n")
    print("| Chapter | Files | Characters | Status |")
    print("|:--------|------:|-----------:|:-------|")

    total_chars = 0
    total_files = 0
    for chapter in sorted(chapter_totals):
        data = chapter_totals[chapter]
        total_chars += data["count"]
        total_files += data["files"]
        if data["count"] < 5000:
            note = "⚠️ Under"
        elif data["count"] < 15000:
            note = "Low"
        elif data["count"] > 40000:
            note = "⚠️ Over"
        else:
            note = "✅ OK"
        print(f"| {chapter} | {data['files']} | {data['count']:,} | {note} |")

    print("\n## Total\n")
    print(f"- Total files: {total_files}")
    print(f"- Total characters: **{total_chars:,}**")

    issues = [row for row in results if "⚠️" in row["status"]]
    if issues:
        print(f"\n## Issues ({len(issues)} files)\n")
        print("| File | Type | Count | Target | Status |")
        print("|:-----|:----:|------:|:-------|:------:|")
        for row in issues:
            print(
                f"| {row['relative_path']} | {row['file_type']} | {row['char_count']:,} | {row['target']} | {row['status']} |"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())