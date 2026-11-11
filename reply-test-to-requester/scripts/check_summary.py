#!/usr/bin/env python3
"""Check a requester-facing PoC summary before it is pasted elsewhere.

Read-only: reports findings and never edits the summary or the evidence record.
Exit code 0 = pass, 1 = findings, 2 = bad input.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FORBIDDEN = {
    "absolute path": re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/]|\\\\[A-Za-z0-9_.$-]+\\"),
    "email address": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "GUID": re.compile(
        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
    ),
    "code fence": re.compile(r"`{3}"),
    "placeholder": re.compile(r"<[^<>\n]{1,40}>|TODO|XXX|○○|\[\[|\]\]"),
    "empty heading bracket": re.compile(r"【\s*】"),
}
EVIDENCE_COUNT = re.compile(r"画面証跡\s*(\d+)\s*枚")


def evidence_count(record: Path) -> int:
    if not record.is_file():
        raise FileNotFoundError(f"evidence record not found: {record}")
    data = json.loads(record.read_text(encoding="utf-8-sig"))
    evidence = data.get("evidence")
    if not isinstance(evidence, list):
        raise ValueError("evidence record has no evidence list")
    return len(evidence)


def check(text: str, expected_count: int | None) -> list[str]:
    findings: list[str] = []
    for name, pattern in FORBIDDEN.items():
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            findings.append(f"line {line}: {name}: {match.group(0)[:40]!r}")
    if expected_count is not None:
        for match in EVIDENCE_COUNT.finditer(text):
            if int(match.group(1)) != expected_count:
                line = text.count("\n", 0, match.start()) + 1
                findings.append(
                    f"line {line}: evidence count {match.group(1)} != record {expected_count}"
                )
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path, help="summary markdown to check")
    parser.add_argument(
        "--evidence-record",
        type=Path,
        help="JSON file with an 'evidence' list; its length is compared with the 画面証跡N枚 mentions",
    )
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    if not args.summary.is_file():
        print(f"error: summary not found: {args.summary}", file=sys.stderr)
        return 2
    expected = None
    if args.evidence_record is not None:
        try:
            expected = evidence_count(args.evidence_record)
        except (OSError, ValueError) as error:
            print(f"error: {error}", file=sys.stderr)
            return 2

    findings = check(args.summary.read_text(encoding="utf-8-sig"), expected)
    if findings:
        print("\n".join(findings))
        return 1
    suffix = f" (evidence count {expected})" if expected is not None else ""
    print(f"ok: no findings{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
