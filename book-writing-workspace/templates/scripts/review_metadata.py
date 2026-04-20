from __future__ import annotations

from copy import deepcopy
from datetime import date
from pathlib import Path
import re
import shutil

from PIL import Image, ImageDraw, ImageFont
import yaml


DEFAULT_TEXDOCUMENTCLASS = [
    "review-jsbook",
    "media=print,paper=a4,fontsize=10pt,baselineskip=15.4pt,line_length=40zw,number_of_lines=35,jafont=noto-otf,serial_pagination=true,openright",
]


def slugify(value: str) -> str:
    lowered = value.lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = lowered.strip("-")
    return lowered or "book"


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def deep_merge(base: dict, override: dict) -> dict:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_review_metadata(workspace_root: Path, metadata_name: str = "project") -> dict:
    root = workspace_root / "config" / "review-metadata"
    common = load_yaml(root / "common.yml")
    specific = load_yaml(root / f"{metadata_name}.yml")
    merged = deep_merge(common, specific)

    today = date.today().isoformat()
    merged.setdefault("review_version", "5.0")
    merged.setdefault("language", "ja")
    merged.setdefault("toclevel", 3)
    merged.setdefault("secnolevel", 3)
    merged.setdefault("toc", True)
    merged.setdefault("titlefile", "custom-titlepage.tex")
    merged.setdefault("stylesheet", ["style.css"])
    merged.setdefault("texdocumentclass", DEFAULT_TEXDOCUMENTCLASS)
    merged.setdefault("contentdir", "output_re")
    merged.setdefault("date", today)
    merged.setdefault("history", [[f"{merged['date']} 初版第1刷"]])
    merged.setdefault("colophon", True)
    merged.setdefault("colophon_order", ["aut", "pbl"])
    if merged.get("aut") and not merged.get("rights"):
        merged["rights"] = f"(C) {merged['date'][:4]} {', '.join(merged['aut'])}"
    if merged.get("booktitle") and not merged.get("bookname"):
        merged["bookname"] = slugify(merged["booktitle"])

    cover = merged.setdefault("cover", {})
    cover.setdefault("enabled", True)
    cover.setdefault("image_name", "cover.jpg")
    cover.setdefault("background_color", "#F6F4EE")
    cover.setdefault("band_color", "#326450")
    cover.setdefault("accent_color", "#C98B3A")
    cover.setdefault("text_color", "#173026")
    cover.setdefault("subtitle_color", "#355B4B")
    cover.setdefault("author_color", "#244738")
    cover.setdefault("publisher_color", "#355B4B")
    cover.setdefault("badge", "")
    cover.setdefault("strapline", "")
    cover.setdefault("author_suffix", "著")
    cover.setdefault("author_font_size", 54)
    cover.setdefault("author_y", 1860)
    cover.setdefault("publisher_font_size", 38)
    cover.setdefault("publisher_y", 2140)
    return merged


def write_review_support_files(review_root: Path, generated_files: list[str], metadata: dict) -> None:
    catalog_path = review_root / "catalog.yml"
    config_path = review_root / "config.yml"

    catalog_lines = ["PREDEF:", "CHAPS:"]
    catalog_lines.extend(f"  - {name}" for name in generated_files)
    catalog_lines.append("POSTDEF:")
    catalog_path.write_text("\n".join(catalog_lines) + "\n", encoding="utf-8")

    config_data: dict = {
        "bookname": metadata["bookname"],
        "booktitle": metadata["booktitle"],
        "review_version": metadata["review_version"],
        "language": metadata["language"],
        "toclevel": metadata["toclevel"],
        "secnolevel": metadata["secnolevel"],
        "toc": metadata["toc"],
        "titlefile": metadata["titlefile"],
        "texdocumentclass": metadata["texdocumentclass"],
        "stylesheet": metadata["stylesheet"],
        "contentdir": metadata["contentdir"],
        "date": metadata["date"],
        "history": metadata["history"],
        "colophon": metadata["colophon"],
        "colophon_order": metadata["colophon_order"],
    }
    for field in ["subtitle", "aut", "pbl", "rights"]:
        value = metadata.get(field)
        if value:
            config_data[field] = value

    if metadata.get("cover", {}).get("enabled", False):
        config_data["coverimage"] = metadata["cover"]["image_name"]

    config_path.write_text(
        yaml.safe_dump(
            config_data,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        ),
        encoding="utf-8",
    )


def _find_font(candidates: list[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    if len(words) == 1 and " " not in text:
        words = list(text)

    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}" if words is not list(text) else current + word
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]


def _draw_multiline(draw, text, font, fill, x, y, max_width, line_spacing):
    lines = _wrap_text(draw, text, font, max_width)
    current_y = y
    for line in lines:
        draw.text((x, current_y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, current_y), line, font=font)
        current_y = bbox[3] + line_spacing
    return current_y


def _format_cover_author_text(authors: list[str], suffix: str) -> str:
    if not authors:
        return ""
    if len(authors) == 1:
        return f"{authors[0]}　{suffix}" if suffix else authors[0]
    joined = " / ".join(authors)
    return f"{joined}　{suffix}" if suffix else joined


def generate_cover_image(workspace_root: Path, review_root: Path, metadata: dict) -> Path | None:
    cover = metadata.get("cover", {})
    if not cover.get("enabled", False):
        return None

    image_name = cover.get("image_name", "cover.jpg")
    images_dir = review_root / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    output_path = images_dir / image_name

    source = cover.get("source")
    if source:
        source_path = (workspace_root / source).resolve()
        if source_path.exists():
            shutil.copy2(source_path, output_path)
            return output_path

    width, height = 1600, 2400
    image = Image.new("RGB", (width, height), cover["background_color"])
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 260), fill=cover["band_color"])
    draw.rectangle((90, 180, width - 90, 205), fill=cover["accent_color"])
    draw.rectangle((100, 2080, width - 100, 2092), fill=cover["accent_color"])

    title_font = _find_font([r"C:\Windows\Fonts\YuGothB.ttc", r"C:\Windows\Fonts\meiryob.ttc", r"C:\Windows\Fonts\msgothic.ttc"], 96)
    subtitle_font = _find_font([r"C:\Windows\Fonts\YuGothM.ttc", r"C:\Windows\Fonts\meiryo.ttc", r"C:\Windows\Fonts\msgothic.ttc"], 42)
    author_font = _find_font([r"C:\Windows\Fonts\YuGothM.ttc", r"C:\Windows\Fonts\meiryo.ttc", r"C:\Windows\Fonts\msgothic.ttc"], int(cover["author_font_size"]))
    publisher_font = _find_font([r"C:\Windows\Fonts\YuGothM.ttc", r"C:\Windows\Fonts\meiryo.ttc", r"C:\Windows\Fonts\msgothic.ttc"], int(cover["publisher_font_size"]))
    badge_font = _find_font([r"C:\Windows\Fonts\YuGothB.ttc", r"C:\Windows\Fonts\meiryob.ttc", r"C:\Windows\Fonts\msgothic.ttc"], 30)

    badge = cover.get("badge", "")
    if badge:
        draw.rounded_rectangle((100, 96, 380, 182), radius=28, fill=cover["accent_color"])
        draw.text((132, 116), badge, font=badge_font, fill=cover["background_color"])

    strapline = cover.get("strapline", "")
    if strapline:
        draw.text((100, 320), strapline, font=subtitle_font, fill=cover["subtitle_color"])

    current_y = _draw_multiline(draw, metadata["booktitle"], title_font, cover["text_color"], 100, 520, width - 200, 18)
    subtitle = metadata.get("subtitle")
    if subtitle:
        current_y += 26
        _draw_multiline(draw, subtitle, subtitle_font, cover["subtitle_color"], 100, current_y, width - 220, 12)

    authors = metadata.get("aut", [])
    if authors:
        author_text = _format_cover_author_text(authors, str(cover.get("author_suffix", "")))
        draw.text((100, int(cover["author_y"])), author_text, font=author_font, fill=cover["author_color"])

    publisher = metadata.get("pbl")
    if publisher:
        publisher_bbox = draw.textbbox((0, 0), publisher, font=publisher_font)
        publisher_width = publisher_bbox[2] - publisher_bbox[0]
        draw.text((width - 100 - publisher_width, int(cover["publisher_y"])), publisher, font=publisher_font, fill=cover["publisher_color"])

    image.save(output_path, quality=92)
    return output_path