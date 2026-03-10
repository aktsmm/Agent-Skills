# -*- coding: utf-8 -*-
"""
Markdown to Re:VIEW converter.

Converts Markdown files under 02_contents/ into .re files under
03_re-view_output/output_re/. The script intentionally covers a compact,
predictable subset of Markdown used by this workspace.
"""

from pathlib import Path
import re
import sys


def resolve_contents_dir() -> Path | None:
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    cwd = Path.cwd()
    if (cwd / "02_contents").exists():
        return cwd / "02_contents"
    if (cwd.parent / "02_contents").exists():
        return cwd.parent / "02_contents"
    return None


def slugify(value: str) -> str:
    lowered = value.lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = lowered.strip("-")
    return lowered or "chapter"


def replace_inline(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"@<code>{\1}", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"@<b>{\1}", text)
    text = re.sub(r"\*([^*]+)\*", r"@<i>{\1}", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"@<href>{\2, \1}", text)
    return text


def convert_markdown(text: str, stem: str) -> str:
    output: list[str] = []
    in_code_block = False
    code_id = 1
    code_lang = "text"

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        fence = re.match(r"^```(.*)$", line)
        if fence:
            if not in_code_block:
                code_lang = fence.group(1).strip() or "text"
                output.append(f"//listnum[{stem}-{code_id}][{code_lang}]{{")
                code_id += 1
                in_code_block = True
            else:
                output.append("//}")
                in_code_block = False
            continue

        if in_code_block:
            output.append(raw_line)
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            level = len(heading.group(1))
            title = replace_inline(heading.group(2).strip())
            output.append(f"{'=' * level} {title}")
            continue

        image = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", line)
        if image:
            caption = image.group(1) or Path(image.group(2)).stem
            image_id = slugify(Path(image.group(2)).stem)
            output.append(f"//image[{image_id}][{caption}]{{")
            output.append(image.group(2))
            output.append("//}")
            continue

        unordered = re.match(r"^\s*[-*+]\s+(.*)$", line)
        if unordered:
            output.append(f" * {replace_inline(unordered.group(1))}")
            continue

        ordered = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if ordered:
            output.append(f" 1. {replace_inline(ordered.group(1))}")
            continue

        output.append(replace_inline(line))

    if in_code_block:
        output.append("//}")

    return "\n".join(output).strip() + "\n"


def build_output_name(md_file: Path) -> str:
    stem = md_file.stem
    match = re.match(r"ch(\d+)-(\d+)_(.*)", stem)
    if match:
        chapter = int(match.group(1))
        slug = slugify(match.group(3))
        return f"ch{chapter:02d}-{slug}.re"
    return f"{slugify(stem)}.re"


def write_support_files(output_root: Path, generated_files: list[str], project_name: str) -> None:
    catalog_path = output_root.parent / "catalog.yml"
    config_path = output_root.parent / "config.yml"

    catalog_lines = ["PREDEF:", "CHAPS:"]
    catalog_lines.extend(f"  - {name}" for name in generated_files)
    catalog_lines.append("POSTDEF:")
    catalog_path.write_text("\n".join(catalog_lines) + "\n", encoding="utf-8")

    if not config_path.exists():
        config_path.write_text(
            "\n".join(
                [
                    f"bookname: {slugify(project_name)}",
                    f"booktitle: {project_name}",
                    "language: ja",
                ]
            )
            + "\n",
            encoding="utf-8",
        )


def main() -> int:
    contents_dir = resolve_contents_dir()
    if contents_dir is None:
        print("Error: Could not find 02_contents/ folder")
        print("Usage: python convert_md_to_review.py [path]")
        return 1
    if not contents_dir.exists():
        print(f"Error: Path not found: {contents_dir}")
        return 1

    project_root = contents_dir.parent
    output_root = project_root / "03_re-view_output" / "output_re"
    output_root.mkdir(parents=True, exist_ok=True)

    generated_files: list[str] = []
    for md_file in sorted(contents_dir.rglob("*.md")):
        output_name = build_output_name(md_file)
        output_path = output_root / output_name
        converted = convert_markdown(md_file.read_text(encoding="utf-8"), slugify(md_file.stem))
        output_path.write_text(converted, encoding="utf-8")
        generated_files.append(output_name)
        print(f"Converted: {md_file.relative_to(project_root)} -> {output_path.relative_to(project_root)}")

    write_support_files(output_root, generated_files, project_root.name)
    print(f"Generated {len(generated_files)} Re:VIEW files in {output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())