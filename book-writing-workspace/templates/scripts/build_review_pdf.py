from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from review_metadata import generate_cover_image, load_review_metadata


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
REVIEW_ROOT = WORKSPACE_ROOT / "03_re-view_output"


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

    output_pdf_dir = REVIEW_ROOT / "output_pdf"
    output_pdf_dir.mkdir(parents=True, exist_ok=True)
    for stale_output_pdf in output_pdf_dir.glob("*.pdf"):
        stale_output_pdf.unlink()
    for pdf_path in REVIEW_ROOT.glob("*.pdf"):
        shutil.move(str(pdf_path), output_pdf_dir / pdf_path.name)
        print(f"Moved: {pdf_path.name} -> output_pdf/{pdf_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())