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
    # Unescape Markdown backslash escapes (e.g. \_ -> _)
    text = re.sub(r"\\([_*`\\])", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"@<b>{\1}", text)
    text = re.sub(r"\*([^*]+)\*", r"@<i>{\1}", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"@<href>{\2, \1}", text)
    return text


def is_markdown_table_delimiter(line: str) -> bool:
    stripped = line.strip()
    if "|" not in stripped:
        return False
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells if cell)


def is_markdown_table_row(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and "|" in stripped[1:-1]


def parse_markdown_table_row(line: str) -> list[str]:
    cells = [replace_inline(cell.strip()) for cell in line.strip().strip("|").split("|")]
    return [cell or "." for cell in cells]


def strip_review_inline(text: str) -> str:
    previous = None
    current = text
    while previous != current:
        previous = current
        current = re.sub(r"@<[^>]+>\{([^{}]*)\}", r"\1", current)
    return current.replace("{", "").replace("}", "")


def estimate_review_tsize(table_rows: list[list[str]]) -> str | None:
    if not table_rows:
        return None

    column_count = max(len(row) for row in table_rows)
    if column_count <= 1:
        return None

    normalized_rows: list[list[str]] = []
    for row in table_rows:
        normalized_rows.append(row + ["."] * (column_count - len(row)))

    visible_lengths: list[int] = []
    for column_index in range(column_count):
        max_length = max(
            len(strip_review_inline(row[column_index]))
            for row in normalized_rows
        )
        visible_lengths.append(max(max_length, 4))

    total_width_mm = 126
    min_width_mm = 14 if column_count <= 4 else 10
    remaining_width_mm = max(total_width_mm - min_width_mm * column_count, column_count)
    total_length = sum(visible_lengths)
    widths = [
        min_width_mm + round(remaining_width_mm * (length / total_length))
        for length in visible_lengths
    ]

    width_diff = total_width_mm - sum(widths)
    widths[-1] += width_diff

    if column_count >= 2:
        minimum_last_width = 34 if column_count == 2 else 42
        if widths[-1] < minimum_last_width:
            shortage = minimum_last_width - widths[-1]
            widths[-1] = minimum_last_width
            donor_indexes = list(range(column_count - 1))
            while shortage > 0 and donor_indexes:
                adjusted = False
                for donor_index in donor_indexes:
                    if widths[donor_index] > min_width_mm + 2:
                        widths[donor_index] -= 1
                        shortage -= 1
                        adjusted = True
                        if shortage == 0:
                            break
                if not adjusted:
                    break

    return "|" + "|".join(f"L{{{width}mm}}" for width in widths) + "|"


def ensure_blank_line_before_list(output: list[str]) -> None:
    if not output:
        return
    if output[-1] == "":
        return
    if re.match(r"^\s+(?:\*+|\d+\.)\s+", output[-1]):
        return
    output.append("")


def fence_caption_from_info(fence_info: str) -> tuple[str, str | None]:
    code_lang = "text"
    code_caption = None
    if fence_info:
        fence_parts = fence_info.split(maxsplit=1)
        code_lang = fence_parts[0]
        if len(fence_parts) > 1:
            code_caption = fence_parts[1].strip()
    return code_lang, code_caption


def consume_list_continuation(lines: list[str], index: int) -> tuple[list[str], int]:
    items: list[str] = []
    current_index = index

    while current_index < len(lines):
        raw_line = lines[current_index]
        line = raw_line.rstrip()
        if not line.strip():
            break
        if re.match(r"^\s{2,}\S", raw_line) or raw_line.startswith("\t"):
            items.append(line.strip())
            current_index += 1
            continue
        break

    return items, current_index


def is_link_only_line(text: str) -> bool:
    stripped = text.strip()
    return bool(re.fullmatch(r"\[[^\]]+\]\([^\)]+\)", stripped))


def convert_markdown(text: str, stem: str) -> str:
    output: list[str] = []
    in_code_block = False
    code_id = 1
    code_lang = "text"

    lines = text.splitlines()
    index = 0

    while index < len(lines):
        raw_line = lines[index]
        line = raw_line.rstrip()
        fence = re.match(r"^```(.*)$", line)
        if fence:
            if not in_code_block:
                fence_info = fence.group(1).strip()
                code_lang, code_caption = fence_caption_from_info(fence_info)
                if code_caption:
                    output.append(f"//listnum[{stem}-{code_id}][{code_caption}]{{")
                else:
                    output.append(f"//listnum[{stem}-{code_id}][]{{")
                code_id += 1
                in_code_block = True
            else:
                output.append("//}")
                in_code_block = False
            index += 1
            continue

        if in_code_block:
            output.append(raw_line)
            index += 1
            continue

        if index + 1 < len(lines) and is_markdown_table_row(line) and is_markdown_table_delimiter(lines[index + 1]):
            table_rows = [parse_markdown_table_row(line)]
            index += 2
            while index < len(lines) and is_markdown_table_row(lines[index]):
                table_rows.append(parse_markdown_table_row(lines[index]))
                index += 1

            tsize = estimate_review_tsize(table_rows)
            if tsize:
                output.append(f"//tsize[|latex|{tsize}]")
            output.append("//table{")
            output.append("\t".join(table_rows[0]))
            output.append("-" * 60)
            for row in table_rows[1:]:
                output.append("\t".join(row))
            output.append("//}")
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            level = len(heading.group(1))
            title = replace_inline(heading.group(2).strip())
            output.append(f"{'=' * level} {title}")
            index += 1
            continue

        image = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", line)
        if image:
            caption = image.group(1) or Path(image.group(2)).stem
            image_id = slugify(Path(image.group(2)).stem)
            output.append(f"//image[{image_id}][{caption}]{{")
            output.append(image.group(2))
            output.append("//}")
            index += 1
            continue

        unordered = re.match(r"^\s*[-*+]\s+(.*)$", line)
        if unordered:
            ensure_blank_line_before_list(output)
            continuation_lines, next_index = consume_list_continuation(lines, index + 1)
            output.append(f" * {replace_inline(unordered.group(1))}")
            for continuation_line in continuation_lines:
                if is_link_only_line(continuation_line):
                    output.append("   @<br>{}")
                output.append(f"   {replace_inline(continuation_line)}")
            index = next_index
            continue

        ordered = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if ordered:
            ensure_blank_line_before_list(output)
            continuation_lines, next_index = consume_list_continuation(lines, index + 1)
            output.append(f" 1. {replace_inline(ordered.group(1))}")
            for continuation_line in continuation_lines:
                if is_link_only_line(continuation_line):
                    output.append("    @<br>{}")
                output.append(f"    {replace_inline(continuation_line)}")
            index = next_index
            continue

        output.append(replace_inline(line))
        index += 1

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