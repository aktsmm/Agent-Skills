#!/usr/bin/env python3
"""Extract aggregate metrics from VS Code GitHub Copilot Chat debug logs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


CHILD_PREFIXES = ("runSubagent-", "searchSubagent-")
SESSION_ID_PATTERN = re.compile(r"^[0-9a-fA-F-]{36}$")


for _stream_name in ("stdout", "stderr"):
    _stream = getattr(sys, _stream_name, None)
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract model, reasoning, timing, error, token, and AIU metrics from Copilot Chat logs.",
    )
    parser.add_argument("--session-dir", action="append", default=[], help="Explicit debug session directory; repeatable")
    parser.add_argument("--debug-root", action="append", default=[], help="Directory containing debug sessions; repeatable")
    parser.add_argument("--session-id", action="append", default=[], help="Session UUID selected from debug roots; repeatable")
    parser.add_argument("--recent", type=int, help="Select the N most recently modified sessions from debug roots")
    parser.add_argument("--contains", help="Select sessions whose first request contains this text; never emitted")
    parser.add_argument("--after", help="Include events at or after this ISO timestamp or epoch milliseconds")
    parser.add_argument("--before", help="Include events at or before this ISO timestamp or epoch milliseconds")
    parser.add_argument("--unit-count", type=int, help="Common workload unit count for each selected session")
    parser.add_argument("--unit-name", default="unit", help="Workload unit label, for example question or test")
    parser.add_argument("--task-kind", default="", help="Comparable task class")
    parser.add_argument("--revision", default="", help="Input revision or content hash")
    parser.add_argument("--workflow-version", default="", help="Workflow version")
    parser.add_argument("--rubric-version", default="", help="Quality rubric version")
    parser.add_argument("--output-json", help="Optional aggregate JSON output path")
    parser.add_argument("--json-only", action="store_true", help="Print only JSON")
    parser.add_argument("--strict-exit-codes", action="store_true", help="Return 1 when extraction fails")
    return parser.parse_args()


def parse_boundary(value: str | None) -> int | None:
    if not value:
        return None
    if value.isdigit():
        return int(value)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def default_debug_roots() -> list[Path]:
    candidates: list[Path] = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        for product in ("Code", "Code - Insiders"):
            candidates.append(Path(appdata) / product / "User" / "workspaceStorage")
    home = Path.home()
    candidates.extend([
        home / ".config" / "Code" / "User" / "workspaceStorage",
        home / ".config" / "Code - Insiders" / "User" / "workspaceStorage",
        home / "Library" / "Application Support" / "Code" / "User" / "workspaceStorage",
        home / "Library" / "Application Support" / "Code - Insiders" / "User" / "workspaceStorage",
    ])
    roots: list[Path] = []
    for workspace_storage in candidates:
        if workspace_storage.is_dir():
            roots.extend(workspace_storage.glob("*/GitHub.copilot-chat/debug-logs"))
    return sorted({path.resolve() for path in roots if path.is_dir()})


def iter_events(path: Path, warnings: Counter[str]) -> Iterator[dict[str, Any]]:
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if "\ufffd" in line:
                warnings["invalid_utf8_replaced"] += 1
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                warnings["invalid_json_lines_skipped"] += 1
                continue
            if isinstance(event, dict):
                yield event
            else:
                warnings["non_object_json_lines_skipped"] += 1


def request_options(attrs: dict[str, Any]) -> dict[str, Any]:
    raw = attrs.get("requestOptions")
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def reasoning_effort(attrs: dict[str, Any]) -> str:
    options = request_options(attrs)
    reasoning = options.get("reasoning") if isinstance(options.get("reasoning"), dict) else {}
    output_config = options.get("output_config") if isinstance(options.get("output_config"), dict) else {}
    return str(reasoning.get("effort") or output_config.get("effort") or "default")


def role_for(path: Path) -> str:
    if path.name == "main.jsonl":
        return "orchestrator"
    stem = path.stem
    for prefix in CHILD_PREFIXES:
        if stem.startswith(prefix):
            role = stem[len(prefix):]
            role = re.sub(r"-call_[A-Za-z0-9-]+$", "", role)
            return role or prefix.rstrip("-")
    return "other"


def log_paths(session_dir: Path) -> list[Path]:
    main = session_dir / "main.jsonl"
    children = sorted(
        path for path in session_dir.glob("*.jsonl")
        if path.name != "main.jsonl" and path.name.startswith(CHILD_PREFIXES)
    )
    return [path for path in [main, *children] if path.is_file()]


def event_identity(event: dict[str, Any]) -> str:
    attrs = event.get("attrs") if isinstance(event.get("attrs"), dict) else {}
    identity = {
        "type": event.get("type"),
        "name": event.get("name"),
        "span": event.get("spanId"),
        "parent": event.get("parentSpanId"),
        "ts": event.get("ts"),
        "dur": event.get("dur"),
        "model": attrs.get("model"),
        "input": attrs.get("inputTokens"),
        "output": attrs.get("outputTokens"),
        "aiu": attrs.get("copilotUsageNanoAiu"),
    }
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("ascii")).hexdigest()


def fingerprint(workload: dict[str, Any], measurement_scope: str) -> str:
    fields = {
        "task_kind": workload.get("task_kind") or "",
        "revision": workload.get("revision") or "",
        "workflow_version": workload.get("workflow_version") or "",
        "rubric_version": workload.get("rubric_version") or "",
        "unit_name": workload.get("unit_name") or "unit",
        "unit_count": workload.get("unit_count"),
        "measurement_scope": measurement_scope,
    }
    encoded = json.dumps(fields, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("ascii")).hexdigest()[:16]


def in_window(event: dict[str, Any], after: int | None, before: int | None) -> bool:
    timestamp = event.get("ts")
    if not isinstance(timestamp, int):
        return True
    return (after is None or timestamp >= after) and (before is None or timestamp <= before)


def extract_session(
    session_dir: Path,
    *,
    after: int | None = None,
    before: int | None = None,
    workload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    session_dir = session_dir.resolve()
    paths = log_paths(session_dir)
    if not paths or paths[0].name != "main.jsonl":
        raise ValueError(f"main.jsonl not found: {session_dir}")

    warnings: Counter[str] = Counter()
    seen: set[str] = set()
    aggregates: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    first_main_request: int | None = None
    last_main_response: int | None = None
    llm_errors = 0
    tool_calls = 0
    tool_errors = 0
    aiu_present_calls = 0
    aiu_missing_calls = 0

    for path in paths:
        role = role_for(path)
        for event in iter_events(path, warnings):
            if not in_window(event, after, before):
                continue
            identity = event_identity(event)
            if identity in seen:
                warnings["duplicate_events_skipped"] += 1
                continue
            seen.add(identity)
            event_type = event.get("type")
            attrs = event.get("attrs") if isinstance(event.get("attrs"), dict) else {}
            if event_type == "llm_request":
                model = str(attrs.get("model") or "unknown")
                effort = reasoning_effort(attrs)
                bucket = aggregates[(role, model, effort)]
                bucket["llm_calls"] += 1
                bucket["input_tokens"] += int(attrs.get("inputTokens") or 0)
                bucket["output_tokens"] += int(attrs.get("outputTokens") or 0)
                bucket["cached_tokens"] += int(attrs.get("cachedTokens") or 0)
                bucket["duration_ms"] += int(event.get("dur") or 0)
                if "copilotUsageNanoAiu" in attrs and attrs.get("copilotUsageNanoAiu") is not None:
                    bucket["nano_aiu"] += int(attrs.get("copilotUsageNanoAiu") or 0)
                    aiu_present_calls += 1
                else:
                    aiu_missing_calls += 1
                if model == "unknown":
                    warnings["llm_requests_missing_model"] += 1
                if event.get("status") == "error":
                    llm_errors += 1
                if role == "orchestrator" and isinstance(event.get("ts"), int):
                    first_main_request = min(first_main_request or event["ts"], event["ts"])
            elif event_type == "agent_response" and role == "orchestrator" and isinstance(event.get("ts"), int):
                last_main_response = max(last_main_response or event["ts"], event["ts"])
            elif event_type == "tool_call":
                tool_calls += 1
                if event.get("status") == "error":
                    tool_errors += 1

    if not aggregates:
        raise ValueError(f"no llm_request events found: {session_dir}")

    usage = []
    for (role, model, effort), values in sorted(aggregates.items()):
        usage.append({
            "role": role,
            "model": model,
            "reasoning_effort": effort,
            "llm_calls": values["llm_calls"],
            "input_tokens": values["input_tokens"],
            "output_tokens": values["output_tokens"],
            "cached_tokens": values["cached_tokens"],
            "nano_aiu": values["nano_aiu"],
            "llm_duration_seconds": round(values["duration_ms"] / 1000, 3),
        })

    primary = Counter(
        (item["model"], item["reasoning_effort"])
        for item in usage
        for _ in range(item["llm_calls"])
        if item["role"] == "orchestrator"
    ).most_common(1)
    total_nano_aiu = sum(item["nano_aiu"] for item in usage)
    total_calls = sum(item["llm_calls"] for item in usage)
    unit_count = int((workload or {}).get("unit_count") or 0)
    complete_aiu = aiu_missing_calls == 0
    total_aiu = round(total_nano_aiu / 1_000_000_000, 6) if complete_aiu else None
    measurement_scope = "orchestrator and runSubagent/searchSubagent llm_request events within the selected time window"
    workload_payload = {
        "task_kind": str((workload or {}).get("task_kind") or ""),
        "revision": str((workload or {}).get("revision") or ""),
        "workflow_version": str((workload or {}).get("workflow_version") or ""),
        "rubric_version": str((workload or {}).get("rubric_version") or ""),
        "unit_name": str((workload or {}).get("unit_name") or "unit"),
        "unit_count": unit_count or None,
    }
    workload_payload["fingerprint"] = fingerprint(workload_payload, measurement_scope)

    observed = None
    if first_main_request is not None and last_main_response is not None and last_main_response >= first_main_request:
        observed = round((last_main_response - first_main_request) / 1000, 3)

    return {
        "schema_version": 1,
        "source_format": "vscode-copilot-chat-debug-log",
        "session_id": session_dir.name,
        "measurement_scope": measurement_scope,
        "workload": workload_payload,
        "primary_model": {
            "model": primary[0][0][0] if primary else "unknown",
            "reasoning_effort": primary[0][0][1] if primary else "default",
        },
        "timing": {
            "session_observed_seconds": observed,
            "active_llm_seconds": round(sum(item["llm_duration_seconds"] for item in usage), 3),
        },
        "usage": usage,
        "cost": {
            "metric": "AIU",
            "total_nano_aiu": total_nano_aiu if complete_aiu else None,
            "total_aiu": total_aiu,
            "aiu_per_unit": round(total_aiu / unit_count, 6) if total_aiu is not None and unit_count else None,
            "coverage": {
                "llm_calls_with_aiu": aiu_present_calls,
                "llm_calls_missing_aiu": aiu_missing_calls,
                "complete": complete_aiu,
            },
        },
        "operations": {
            "llm_calls": total_calls,
            "llm_errors": llm_errors,
            "tool_calls": tool_calls,
            "tool_errors": tool_errors,
            "log_files": len(paths),
        },
        "warnings": [
            {"code": code, "count": count}
            for code, count in sorted(warnings.items())
        ],
    }


def first_request_contains(session_dir: Path, text: str) -> bool:
    warnings: Counter[str] = Counter()
    for event in iter_events(session_dir / "main.jsonl", warnings):
        attrs = event.get("attrs") if isinstance(event.get("attrs"), dict) else {}
        if event.get("type") == "user_message" and attrs.get("content") is not None:
            return text in str(attrs["content"])
        if event.get("type") == "llm_request" and attrs.get("userRequest") is not None:
            return text in str(attrs["userRequest"])
    return False


def select_session_dirs(args: argparse.Namespace) -> list[Path]:
    explicit = [Path(value).expanduser().resolve() for value in args.session_dir]
    roots = [Path(value).expanduser().resolve() for value in args.debug_root] or default_debug_roots()
    selected = list(explicit)
    if args.session_id:
        for session_id in args.session_id:
            if not SESSION_ID_PATTERN.fullmatch(session_id):
                raise ValueError(f"invalid session UUID: {session_id}")
            matches = [root / session_id for root in roots if (root / session_id).is_dir()]
            if len(matches) != 1:
                raise ValueError(f"expected one session directory for {session_id}, found {len(matches)}")
            selected.append(matches[0].resolve())
    elif args.recent:
        candidates = [path for root in roots if root.is_dir() for path in root.iterdir() if (path / "main.jsonl").is_file()]
        candidates.sort(key=lambda path: ((path / "main.jsonl").stat().st_mtime, path.name), reverse=True)
        selected.extend(candidates[:args.recent])
    if not selected:
        raise ValueError("provide --session-dir, --session-id, or --recent")
    unique = sorted({path.resolve() for path in selected}, key=lambda path: path.name)
    if args.contains:
        unique = [path for path in unique if first_request_contains(path, args.contains)]
    if not unique:
        raise ValueError("no sessions matched the selection")
    return unique


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def render(payload: dict[str, Any], json_only: bool) -> None:
    if not json_only:
        print("=== Copilot Session Metrics ===")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    args = parse_args()
    try:
        after = parse_boundary(args.after)
        before = parse_boundary(args.before)
        if after is not None and before is not None and after > before:
            raise ValueError("--after must not be later than --before")
        if args.unit_count is not None and args.unit_count <= 0:
            raise ValueError("--unit-count must be positive")
        workload = {
            "unit_count": args.unit_count,
            "unit_name": args.unit_name,
            "task_kind": args.task_kind,
            "revision": args.revision,
            "workflow_version": args.workflow_version,
            "rubric_version": args.rubric_version,
        }
        sessions = [
            extract_session(path, after=after, before=before, workload=workload)
            for path in select_session_dirs(args)
        ]
        payload = {
            "status": "PASS",
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "session_count": len(sessions),
            "sessions": sessions,
        }
        if args.output_json:
            atomic_write_json(Path(args.output_json), payload)
        render(payload, args.json_only)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        payload = {"status": "FAIL", "error": {"type": type(exc).__name__, "message": str(exc)}}
        render(payload, args.json_only)
        return 1 if args.strict_exit_codes else 0


if __name__ == "__main__":
    raise SystemExit(main())