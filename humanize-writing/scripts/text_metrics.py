#!/usr/bin/env python3
"""Count mechanical AI-tell metrics in Markdown/plain Japanese text (stdlib only).

Thresholds are discovery heuristics, not verdicts. Report findings as signals and
judge them in context (genre, quoted text, tables, numbered procedures).
Soft line wraps are joined per paragraph, so wrapping does not change the numbers.
Link targets and bare URLs are dropped (link text is kept) so link-heavy articles are not inflated.
Known limit: a heading or table indented inside a list item ends that item's paragraph.
"""
import argparse
import json
import re
import sys

BOLD = re.compile(r"(?<!\*)\*\*(?=\S)(?:(?!\*\*).)+?(?<=\S)\*\*(?!\*)|(?<!_)__(?=\S)(?:(?!__).)+?(?<=\S)__(?!_)")
INLINE_CODE = re.compile(r"`+[^`\n]*`+")
LINK = re.compile(r"!?\[([^\]]*)\]\([^)\s]*[^)]*\)")
BARE_URL = re.compile(r"https?://\S+")
BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
FENCE_OPEN = re.compile(r"^\s*(`{3,}|~{3,})")
# Pictographs, flags and ZWJ sequences count as one; ballot boxes and plain symbols do not.
EMOJI = re.compile(
    "(?:[\U0001F1E6-\U0001F1FF]{2}|[\U0001F300-\U0001FAFF\u2705\u2728\u2B50\u2764\u26A1]"
    "(?:\uFE0F|\u200D[\U0001F300-\U0001FAFF])*)"
)
SENT_END = re.compile(r"(?<=[。！？!?])|(?<=[.])(?=\s)")
TAIL = re.compile(r"(でした|ました|です|ます|である|だった)[。！？!?]?$")

LIMITS = {
    "bold_per_1000": (2.0, 3.0),
    "bullet_ratio": (0.15, 0.25),
    "avg_sentence_chars": (45, 60),
    "commas_per_sentence": (2.0, 3.0),
}


def prose_lines(text):
    fence = None
    for line in text.splitlines():
        match = FENCE_OPEN.match(line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not line.strip().strip(marker[0]):
                fence = None
            continue
        if fence is None:
            yield line


def join_wrapped(parts):
    """Join soft-wrapped lines; no space between CJK characters so wrapping adds no characters."""
    out = ""
    for part in parts:
        if out and not (re.search(r"[\u3000-\u9fff\uff00-\uffef]$", out) and re.match(r"[\u3000-\u9fff\uff00-\uffef]", part)):
            out += " "
        out += part
    return out


def paragraphs(lines):
    """Yield (is_bullet, text) with soft wraps joined; bullet continuation lines stay in their item.

    Headings, tables and quotes are skipped.
    """
    buffer = []
    in_bullet = False

    def flush():
        nonlocal buffer
        if buffer:
            yield in_bullet, join_wrapped(buffer)
            buffer = []

    for line in lines + [""]:
        stripped = line.strip()
        skip = stripped.startswith(("#", "|", ">"))
        bullet = bool(BULLET.match(line))
        if not stripped or skip:
            yield from flush()
            in_bullet = False
        elif bullet:
            yield from flush()
            in_bullet = True
            buffer.append(BULLET.sub("", line).strip())
        else:
            buffer.append(stripped)
    yield from flush()


def measure(text):
    units = list(paragraphs(list(prose_lines(text))))
    cleaned = [(b, INLINE_CODE.sub("", BARE_URL.sub("", LINK.sub(r"\1", t)))) for b, t in units]
    chars = sum(len(t) for _, t in cleaned) or 1
    bullets = sum(1 for b, _ in cleaned if b)
    bold = sum(len(BOLD.findall(t)) for _, t in cleaned)
    sentences = [s.strip() for _, t in cleaned for s in SENT_END.split(t) if s.strip()]
    sent_lens = [len(s) for s in sentences] or [0]
    commas = [s.count("、") + s.count(",") for s in sentences] or [0]
    run = longest = 0
    previous = None
    for sentence in sentences:
        found = TAIL.search(sentence)
        tail = found.group(1) if found else None
        run = run + 1 if tail and tail == previous else (1 if tail else 0)
        previous = tail
        longest = max(longest, run)
    colon_ends = sum(1 for _, t in cleaned if t.rstrip().endswith(("：", ":")))
    return {
        "chars": chars,
        "bold_per_1000": round(bold * 1000 / chars, 2),
        "bullet_ratio": round(bullets / len(cleaned), 3) if cleaned else 0.0,
        "avg_sentence_chars": round(sum(sent_lens) / len(sent_lens), 1),
        "commas_per_sentence": round(sum(commas) / len(commas), 2),
        "emoji": len(EMOJI.findall("\n".join(t for _, t in cleaned))),
        "colon_endings": colon_ends,
        "longest_same_ending_run": longest,
    }


def judge(metrics):
    flags = []
    for key, (ok, warn) in LIMITS.items():
        value = metrics[key]
        if value > warn:
            flags.append((key, value, "warn"))
        elif value > ok:
            flags.append((key, value, "watch"))
    if metrics["emoji"]:
        flags.append(("emoji", metrics["emoji"], "watch"))
    if metrics["colon_endings"]:
        flags.append(("colon_endings", metrics["colon_endings"], "watch"))
    if metrics["longest_same_ending_run"] >= 3:
        flags.append(("longest_same_ending_run", metrics["longest_same_ending_run"], "warn"))
    return flags


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", help="file to inspect (default: stdin)")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="exit 1 on any warn")
    args = parser.parse_args()
    if args.path:
        with open(args.path, encoding="utf-8") as handle:
            text = handle.read()
    else:
        text = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    metrics = measure(text)
    flags = judge(metrics)
    if args.json:
        print(json.dumps({"metrics": metrics, "flags": flags}, ensure_ascii=False))
    else:
        for key, value in metrics.items():
            print(f"{key}: {value}")
        for key, value, level in flags:
            print(f"[{level}] {key} = {value}")
    return 1 if args.strict and any(level == "warn" for *_, level in flags) else 0


if __name__ == "__main__":
    raise SystemExit(main())
