"""Extract customer-facing PDF text and reject empty or customer-specific body content."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader
from pptx import Presentation


def profile_terms(path: Path) -> list[str]:
    if not path.exists():
        return []
    terms = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\|\s*(Customer name|System name|Tenant domain|Tenant id)\s*\|\s*(.*?)\s*\|", line, re.IGNORECASE)
        if match:
            value = match.group(2).strip().strip("`")
            if len(value) >= 4:
                terms.append(value)
    return terms


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--workspace-root", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--pptx", required=True, type=Path)
    args = parser.parse_args()
    reader = PdfReader(args.pdf)
    presentation = Presentation(args.pptx)
    visible_slide_count = sum(slide._element.get("show") != "0" for slide in presentation.slides)
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    nonempty = [text for text in pages if text]
    full_text = "\n".join(pages)
    terms = profile_terms(args.workspace_root / ".config" / "customer-profile.md")
    body_text = "\n".join(pages[1:])
    findings = [term for term in terms if term.casefold() in body_text.casefold()]
    result = {
        "schemaVersion": 1,
        "pdf": str(args.pdf),
        "pageCount": len(pages),
        "visibleSlideCount": visible_slide_count,
        "pageCountMatchesVisibleSlides": len(pages) == visible_slide_count,
        "encrypted": bool(reader.is_encrypted),
        "nonemptyPageCount": len(nonempty),
        "textCharacters": len(full_text),
        "customerTermsChecked": len(terms),
        "customerTermsFoundOutsideCover": findings,
        "passed": bool(pages) and len(nonempty) == len(pages) and len(pages) == visible_slide_count and not reader.is_encrypted and bool(terms) and not findings,
    }
    args.result.parent.mkdir(parents=True, exist_ok=True)
    args.result.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
