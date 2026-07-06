#!/usr/bin/env python3
"""Initialize an optional SQLite state store for Opportunity Factory."""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def replace_placeholders(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, str):
        for old, new in replacements.items():
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [replace_placeholders(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: replace_placeholders(item, replacements) for key, item in value.items()}
    return value


def load_first_run_queue(skill_root: Path, args: argparse.Namespace, now: str) -> dict[str, Any]:
    template = read_json(skill_root / "assets" / "templates" / "first-run-queue.json")
    replacements = {
        "YYYY-MM-DDTHH:mm:ssZ": now,
        "YYYYMMDD": now[:10].replace("-", ""),
        "<domain>": args.domain,
        "<audience>": args.audience,
        "<primary metric>": args.success_metric,
    }
    queue = replace_placeholders(template, replacements)
    queue["updatedAt"] = now
    return queue


def seed_database(connection: sqlite3.Connection, queue: dict[str, Any], args: argparse.Namespace, now: str) -> None:
    run_id = f"run-{now[:10].replace('-', '')}-001"
    connection.execute(
        "INSERT INTO runs (id, started_at, mode, target_set, status, summary) VALUES (?, ?, ?, ?, ?, ?)",
        (run_id, now, args.mode, args.target_set, "running", "Initial Opportunity Factory SQLite state"),
    )
    item_id = "item-initial-opportunity-factory"
    connection.execute(
        "INSERT INTO items (id, title, domain, audience, status, priority, source, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (item_id, "Initial Opportunity Factory batch", args.domain, args.audience, "new", "high", "initializer", now, now),
    )
    for task in queue.get("tasks", []):
        connection.execute(
            """
            INSERT INTO tasks (id, item_id, kind, assignee, priority, status, instruction, artifact_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task["id"],
                item_id,
                task["kind"],
                task.get("assignee"),
                task.get("priority", "medium"),
                task.get("status", "pending"),
                task["instruction"],
                task.get("outputs", {}).get("artifact"),
                task.get("createdAt", now),
                task.get("updatedAt", now),
            ),
        )
    connection.execute(
        "INSERT INTO pipeline_log (ts, actor, event, details) VALUES (?, ?, ?, ?)",
        (now, "init_factory_sqlite", "sqlite_initialized", f"Seeded {len(queue.get('tasks', []))} first-run tasks"),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize an optional Opportunity Factory SQLite state store.")
    parser.add_argument("--skill-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--db-path", required=True)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--audience", required=True)
    parser.add_argument("--success-metric", default="validated signal")
    parser.add_argument("--mode", default="batch-refinement")
    parser.add_argument("--target-set", default="all")
    parser.add_argument("--apply", action="store_true", help="Write the SQLite database. Without this flag, only print the plan.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing database file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_root = Path(args.skill_root).resolve()
    db_path = Path(args.db_path).resolve()
    schema_path = skill_root / "assets" / "templates" / "factory-state.sqlite.sql"
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    queue = load_first_run_queue(skill_root, args, now)

    print("Opportunity Factory SQLite initializer")
    print(f"db_path: {db_path}")
    print(f"mode: {'apply' if args.apply else 'dry-run'}")
    print(f"first_run_tasks: {len(queue.get('tasks', []))}")

    if not args.apply:
        print("dry-run only; rerun with --apply to write the database")
        return 0

    if db_path.exists() and not args.force:
        raise FileExistsError(f"refusing to overwrite existing database without --force: {db_path}")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists() and args.force:
        db_path.unlink()

    connection = sqlite3.connect(db_path)
    try:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        seed_database(connection, queue, args, now)
        connection.commit()
    finally:
        connection.close()
    print("initialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())