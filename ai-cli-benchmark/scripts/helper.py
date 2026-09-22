#!/usr/bin/env python3
"""Validate cache-aware AI CLI benchmark JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


TOKEN_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "cache_write_tokens",
    "output_tokens",
    "reasoning_tokens",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--require-cache-metadata", action="store_true")
    parser.add_argument("--require-zero-cache-read", action="store_true")
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def validate(path: Path, require_cache_metadata: bool, require_zero_cache_read: bool) -> dict:
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    design = document.get("test_design")
    providers = document.get("providers")
    if not isinstance(design, dict) or not isinstance(providers, list) or not providers:
        raise ValueError("Benchmark requires test_design and a nonempty providers array.")

    prompt_hash = design.get("prompt_sha256")
    if not isinstance(prompt_hash, str) or len(prompt_hash) != 64:
        raise ValueError("Missing prompt SHA-256.")
    cache = design.get("cache_observation")
    if require_cache_metadata and not isinstance(cache, dict):
        raise ValueError("Missing cache_observation metadata.")
    if isinstance(cache, dict):
        nonce_hash = cache.get("nonce_sha256")
        if cache.get("nonce_added_at_prompt_start") and (
            not isinstance(nonce_hash, str) or len(nonce_hash) != 64
        ):
            raise ValueError("Nonce is enabled but its SHA-256 is missing.")

    summaries = []
    for provider in providers:
        name = provider.get("provider")
        usage = provider.get("usage")
        if not isinstance(name, str) or not isinstance(usage, dict):
            raise ValueError("Provider name or usage is missing.")
        for field in TOKEN_FIELDS:
            value = usage.get(field)
            if field == "reasoning_tokens" and value is None:
                continue
            if not isinstance(value, (int, float)) or value < 0:
                raise ValueError(f"{name} has invalid {field}.")
        cached = usage["cached_input_tokens"]
        if require_zero_cache_read and cached != 0:
            raise ValueError(f"{name} reported {cached} cached input tokens.")
        elapsed = provider.get("elapsed_ms")
        passed = provider.get("passed")
        cases = provider.get("cases")
        if not isinstance(elapsed, (int, float)) or elapsed < 0:
            raise ValueError(f"{name} has invalid elapsed_ms.")
        if not isinstance(passed, int) or not isinstance(cases, int) or not 0 <= passed <= cases:
            raise ValueError(f"{name} has invalid accuracy counts.")
        summaries.append(
            {
                "provider": name,
                "passed": passed,
                "cases": cases,
                "elapsed_ms": elapsed,
                "cache_read": cached,
                "cache_write": usage["cache_write_tokens"],
            }
        )
    return {
        "status": "PASS",
        "input": path.name,
        "providers": summaries,
        "cache_controlled_by_cli": False,
    }


def main() -> None:
    args = parse_args()
    result = validate(args.input, args.require_cache_metadata, args.require_zero_cache_read)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
