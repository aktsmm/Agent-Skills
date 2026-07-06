#!/usr/bin/env python3
"""Smoke-test Opportunity Factory JSON and SQLite initializers."""

from __future__ import annotations

import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path


def run_command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    return result


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_json_initializer(root: Path, work_dir: Path) -> None:
    state_dir = work_dir / "json-state"
    script = root / "scripts" / "init_factory_workspace.py"
    common_args = [
        sys.executable,
        "-B",
        str(script),
        "--state-dir",
        str(state_dir),
        "--domain",
        "mobile app ideas",
        "--artifact-type",
        "prototype",
        "--audience",
        "solo creators",
        "--success-metric",
        "validated pain",
    ]
    dry_run = run_command(common_args, root)
    assert_true("dry-run only" in dry_run.stdout, "JSON initializer dry-run did not report dry-run mode")
    assert_true(not state_dir.exists(), "JSON initializer dry-run created state directory")

    run_command([*common_args, "--apply"], root)
    for file_name in ["factory-state.json", "tasks-pending.json", "tasks-done.json", "outcome-log.json", "pipeline-log.jsonl"]:
        assert_true((state_dir / file_name).exists(), f"JSON initializer missing {file_name}")
    assert_true((state_dir / "artifacts").is_dir(), "JSON initializer missing artifacts directory")

    state = json.loads((state_dir / "factory-state.json").read_text(encoding="utf-8"))
    pending = json.loads((state_dir / "tasks-pending.json").read_text(encoding="utf-8"))
    assert_true(state["frame"]["domain"] == "mobile app ideas", "JSON state domain not substituted")
    assert_true(len(pending["tasks"]) == 3, "JSON pending queue should have 3 first-run tasks")
    assert_true("<domain>" not in json.dumps(pending), "JSON pending queue still contains <domain>")


def test_sqlite_initializer(root: Path, work_dir: Path) -> None:
    db_path = work_dir / "sqlite-state" / "factory-state.sqlite"
    script = root / "scripts" / "init_factory_sqlite.py"
    common_args = [
        sys.executable,
        "-B",
        str(script),
        "--db-path",
        str(db_path),
        "--domain",
        "game ideas",
        "--audience",
        "solo indie developers",
        "--success-metric",
        "wishlist intent",
    ]
    dry_run = run_command(common_args, root)
    assert_true("dry-run only" in dry_run.stdout, "SQLite initializer dry-run did not report dry-run mode")
    assert_true(not db_path.exists(), "SQLite initializer dry-run created database")

    run_command([*common_args, "--apply"], root)
    assert_true(db_path.exists(), "SQLite initializer did not create database")

    connection = sqlite3.connect(db_path)
    try:
        task_count = connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        run_count = connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        item_count = connection.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    finally:
        connection.close()
    assert_true(task_count == 3, "SQLite initializer should seed 3 tasks")
    assert_true(run_count == 1, "SQLite initializer should seed 1 run")
    assert_true(item_count == 1, "SQLite initializer should seed 1 item")


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    work_dir = Path(tempfile.mkdtemp(prefix="opportunity-factory-smoke-"))
    try:
        test_json_initializer(root, work_dir)
        test_sqlite_initializer(root, work_dir)
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
    print("PASS")
    print(f"validated initializers: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())