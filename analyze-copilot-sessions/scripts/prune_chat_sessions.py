#!/usr/bin/env python3
"""Safely prune workspace-scoped VS Code Copilot Chat session history."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse


SESSION_ID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run or prune local Copilot Chat sessions for one VS Code workspace.",
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--workspace", help="Workspace root or .code-workspace path")
    target.add_argument("--workspace-storage", help="Exact VS Code workspaceStorage child directory")
    parser.add_argument("--older-than-hours", type=float, required=True, help="Delete sessions older than this age")
    parser.add_argument(
        "--protect-session-id",
        action="append",
        default=[],
        help="Session UUID to retain; repeatable",
    )
    parser.add_argument("--keep-latest", type=int, default=1, help="Always retain this many newest sessions")
    parser.add_argument("--apply", action="store_true", help="Apply deletion; default is dry-run")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    return parser.parse_args()


def workspace_storage_roots() -> list[Path]:
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
    return [path for path in candidates if path.is_dir()]


def file_uri_to_path(value: str) -> Path:
    parsed = urlparse(value)
    if parsed.scheme != "file":
        raise ValueError("workspace.json contains a non-file URI")
    path = unquote(parsed.path)
    if os.name == "nt" and re.match(r"^/[A-Za-z]:", path):
        path = path[1:]
    return Path(path).resolve()


def workspace_paths(storage: Path) -> set[Path]:
    metadata_path = storage / "workspace.json"
    if not metadata_path.is_file():
        return set()
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    paths: set[Path] = set()
    for key in ("folder", "workspace"):
        value = metadata.get(key)
        if not isinstance(value, str):
            continue
        try:
            path = file_uri_to_path(value)
        except ValueError:
            continue
        paths.add(path)
        if path.suffix.lower() == ".code-workspace":
            paths.add(path.parent)
    return paths


def newest_session_mtime(storage: Path) -> float | None:
    session_root = storage / "chatSessions"
    mtimes = [path.stat().st_mtime for path in session_root.glob("*.jsonl")]
    return max(mtimes) if mtimes else None


def resolve_workspace_storage(workspace: Path, roots: list[Path] | None = None) -> Path:
    target = workspace.resolve()
    matches = [
        storage
        for root in (roots if roots is not None else workspace_storage_roots())
        for storage in root.iterdir()
        if storage.is_dir() and target in workspace_paths(storage)
    ]
    if len(matches) == 1:
        return matches[0]
    active_matches = [
        (modified, storage)
        for storage in matches
        if (modified := newest_session_mtime(storage)) is not None
    ]
    active_matches.sort(reverse=True, key=lambda item: item[0])
    if active_matches and (len(active_matches) == 1 or active_matches[0][0] > active_matches[1][0]):
        return active_matches[0][1]
    raise ValueError(
        f"workspace storage is ambiguous across {len(matches)} matches; use --workspace-storage"
    )


def validate_storage(storage: Path) -> Path:
    resolved = storage.resolve()
    if not (resolved / "workspace.json").is_file():
        raise ValueError("workspace storage must contain workspace.json")
    if not (resolved / "chatSessions").is_dir():
        raise ValueError("workspace storage must contain chatSessions")
    return resolved


def auxiliary_roots(storage: Path) -> list[Path]:
    return [
        storage / "chatEditingSessions",
        storage / "GitHub.copilot-chat" / "chat-session-resources",
    ]


def build_plan(
    storage: Path,
    older_than_hours: float,
    protected_ids: set[str],
    keep_latest: int,
    now: datetime | None = None,
) -> dict:
    if older_than_hours <= 0:
        raise ValueError("older-than-hours must be greater than zero")
    if keep_latest < 0:
        raise ValueError("keep-latest must not be negative")
    current_time = now or datetime.now(timezone.utc)
    cutoff = current_time - timedelta(hours=older_than_hours)
    cutoff_timestamp = cutoff.timestamp()
    session_root = storage / "chatSessions"
    session_files = sorted(session_root.glob("*.jsonl"), key=lambda path: path.stat().st_mtime, reverse=True)
    invalid_protected = sorted(session_id for session_id in protected_ids if not SESSION_ID_PATTERN.fullmatch(session_id))
    if invalid_protected:
        raise ValueError(f"invalid protected session IDs: {', '.join(invalid_protected)}")

    effective_protected = set(protected_ids)
    effective_protected.update(path.stem for path in session_files[:keep_latest])
    session_candidates = [
        path
        for path in session_files
        if SESSION_ID_PATTERN.fullmatch(path.stem)
        and path.stem not in effective_protected
        and path.stat().st_mtime < cutoff_timestamp
    ]
    candidate_ids = {path.stem for path in session_candidates}
    existing_ids = {path.stem for path in session_files}

    auxiliary_candidates: list[Path] = []
    for root in auxiliary_roots(storage):
        if not root.is_dir():
            continue
        for path in root.iterdir():
            if not path.is_dir() or not SESSION_ID_PATTERN.fullmatch(path.name):
                continue
            linked = path.name in candidate_ids
            old_orphan = path.name not in existing_ids and path.stat().st_mtime < cutoff_timestamp
            if path.name not in effective_protected and (linked or old_orphan):
                auxiliary_candidates.append(path)

    return {
        "storage": storage,
        "workspace_storage_id": storage.name,
        "cutoff": cutoff,
        "session_files": session_candidates,
        "auxiliary_dirs": auxiliary_candidates,
        "protected_ids": effective_protected,
        "session_count": len(session_files),
    }


def apply_plan(plan: dict) -> dict[str, int]:
    deleted_session_ids: set[str] = set()
    cutoff_timestamp = plan["cutoff"].timestamp()
    for path in plan["session_files"]:
        if path.is_file() and path.stat().st_mtime < cutoff_timestamp:
            path.unlink()
            deleted_session_ids.add(path.stem)

    deleted_auxiliary = 0
    for path in plan["auxiliary_dirs"]:
        linked_session = path.name in deleted_session_ids
        old_orphan = not (plan["storage"] / "chatSessions" / f"{path.name}.jsonl").exists()
        if path.is_dir() and (linked_session or (old_orphan and path.stat().st_mtime < cutoff_timestamp)):
            shutil.rmtree(path)
            deleted_auxiliary += 1
    return {"session_files": len(deleted_session_ids), "auxiliary_dirs": deleted_auxiliary}


def report(plan: dict, mode: str, deleted: dict[str, int] | None = None) -> dict:
    return {
        "mode": mode,
        "workspace_storage_id": plan["workspace_storage_id"],
        "cutoff_utc": plan["cutoff"].isoformat(),
        "sessions_scanned": plan["session_count"],
        "protected_count": len(plan["protected_ids"]),
        "candidate_session_count": len(plan["session_files"]),
        "candidate_auxiliary_count": len(plan["auxiliary_dirs"]),
        "candidate_session_ids": sorted(path.stem for path in plan["session_files"]),
        "remaining_candidate_session_count": sum(path.exists() for path in plan["session_files"]),
        "remaining_candidate_auxiliary_count": sum(path.exists() for path in plan["auxiliary_dirs"]),
        "deleted": deleted or {"session_files": 0, "auxiliary_dirs": 0},
    }


def main() -> int:
    args = parse_args()
    try:
        storage = validate_storage(
            Path(args.workspace_storage)
            if args.workspace_storage
            else resolve_workspace_storage(Path(args.workspace))
        )
        plan = build_plan(
            storage,
            args.older_than_hours,
            set(args.protect_session_id),
            args.keep_latest,
        )
        deleted = apply_plan(plan) if args.apply else None
        result = report(plan, "apply" if args.apply else "dry-run", deleted)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=True))
    else:
        print(f"Mode: {result['mode']}")
        print(f"Workspace storage: {result['workspace_storage_id']}")
        print(f"Cutoff UTC: {result['cutoff_utc']}")
        print(f"Sessions: {result['sessions_scanned']} scanned, {result['candidate_session_count']} candidates")
        print(f"Protected: {result['protected_count']}")
        print(f"Auxiliary candidates: {result['candidate_auxiliary_count']}")
        if args.apply:
            print(f"Deleted: {result['deleted']['session_files']} sessions, {result['deleted']['auxiliary_dirs']} auxiliary directories")
            print(
                "Remaining candidates: "
                f"{result['remaining_candidate_session_count']} sessions, "
                f"{result['remaining_candidate_auxiliary_count']} auxiliary directories"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())