from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from review_metadata import generate_cover_image, load_review_metadata


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
REVIEW_ROOT = WORKSPACE_ROOT / "re-view-output"


def bootstrap_sty() -> None:
    if (REVIEW_ROOT / "sty").exists():
        return

    subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{REVIEW_ROOT}:/work",
            "-w",
            "/work",
            "vvakame/review",
            "sh",
            "-lc",
            "rm -rf /tmp/review-init; mkdir -p /tmp/review-init; cd /tmp/review-init; review-init sample >/dev/null; cp -r sample/sty /work/; cp sample/style.css /work/",
        ],
        check=True,
    )


def main() -> int:
    for stale_pdf in REVIEW_ROOT.glob("*.pdf"):
        stale_pdf.unlink()

    bootstrap_sty()
    metadata = load_review_metadata(WORKSPACE_ROOT, "project")
    generate_cover_image(WORKSPACE_ROOT, REVIEW_ROOT, metadata)

    subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{REVIEW_ROOT}:/work",
            "-w",
            "/work",
            "vvakame/review",
            "review-pdfmaker",
            "config.yml",
        ],
        check=True,
    )

    pdf_dir = WORKSPACE_ROOT / "pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    for stale_pdf in pdf_dir.glob("*.pdf"):
        stale_pdf.unlink()
    for pdf_path in REVIEW_ROOT.glob("*.pdf"):
        shutil.move(str(pdf_path), pdf_dir / pdf_path.name)
        print(f"Moved: {pdf_path.name} -> pdf/{pdf_path.name}")

    # Post-process: insert cover image as full-bleed first page
    cover_image = REVIEW_ROOT / "images" / "cover.png"
    if not cover_image.exists():
        cover_image = REVIEW_ROOT / "images" / "cover.jpg"
    if cover_image.exists():
        for pdf_file in pdf_dir.glob("*.pdf"):
            _insert_cover_page(pdf_file, cover_image)
            print(f"[cover] inserted {cover_image.name} into {pdf_file.name}")

    return 0


def _insert_cover_page(pdf_path: Path, cover_image_path: Path) -> None:
    """Insert cover image as full-bleed first page using PyMuPDF."""
    import fitz

    doc = fitz.open(str(pdf_path))
    rect = doc[0].rect

    cover_doc = fitz.open()
    cover_page = cover_doc.new_page(width=rect.width, height=rect.height)
    cover_page.insert_image(rect, filename=str(cover_image_path))

    doc.insert_pdf(cover_doc, from_page=0, to_page=0, start_at=0)
    cover_doc.close()

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".pdf", dir=str(pdf_path.parent))
    os.close(tmp_fd)
    doc.save(tmp_path, deflate=True)
    doc.close()
    Path(tmp_path).replace(pdf_path)


if __name__ == "__main__":
    raise SystemExit(main())