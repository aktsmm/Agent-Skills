#!/usr/bin/env python3
"""Validate the Opportunity Factory skill package.

This checks the reusable skill assets, not any user workspace state.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path


REQUIRED_FILES = [
    "SKILL.md",
    "LICENSE.txt",
    "references/workflow.md",
    "references/battle-tested-patterns.md",
    "references/runtime-modes.md",
    "references/batch-refinement.md",
    "references/sqlite-state-store.md",
    "references/workspace-setup.md",
    "references/rubber-duck-review.md",
    "assets/prompts/commander.md",
    "assets/prompts/worker.md",
    "assets/prompts/reporter-learner.md",
    "assets/templates/factory-plan.md",
    "assets/templates/factory-state.json",
    "assets/templates/factory-state.sqlite.sql",
    "assets/templates/first-run-queue.json",
    "assets/templates/task.json",
    "assets/templates/artifact.md",
    "assets/templates/setup-preflight.md",
    "assets/examples/setup-packets.md",
    "scripts/init_factory_workspace.py",
    "scripts/init_factory_sqlite.py",
    "scripts/smoke_test_initializers.py",
]

ABSOLUTE_PATH_PATTERN = re.compile(
    "|".join(
        [
            r"[A-Za-z]:\\",
            "/" + "home/",
            "/" + "Users/",
            "~/" + ".openclaw",
            "/" + "mnt/",
        ]
    )
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def validate_json(root: Path, relative_path: str, failures: list[str]) -> dict:
    path = root / relative_path
    try:
        return json.loads(read_text(path))
    except Exception as exc:  # noqa: BLE001 - validator reports exact failure
        failures.append(f"{relative_path}: invalid JSON: {exc}")
        return {}


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    failures: list[str] = []

    check(root.exists(), f"skill root does not exist: {root}", failures)
    for relative_path in REQUIRED_FILES:
        check((root / relative_path).is_file(), f"missing required file: {relative_path}", failures)

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    skill = read_text(root / "SKILL.md")
    check("name: opportunity-factory" in skill, "SKILL.md missing matching name", failures)
    check("description:" in skill, "SKILL.md missing description", failures)
    check("Workspace Setup" in skill, "SKILL.md missing Workspace Setup mode", failures)
    check("Periodic Runtime" in skill, "SKILL.md missing Periodic Runtime mode", failures)
    check("Batch refinement" in skill or "/Refine-Product-100" in skill, "SKILL.md missing batch refinement trigger", failures)
    check(len(skill.splitlines()) <= 150, "SKILL.md should stay under 150 lines", failures)

    runtime = read_text(root / "references/runtime-modes.md")
    for phrase in ["Hosted Agent Scheduler", "Copilot Scheduler (VS Code Extension)", "OpenClaw / Cron", "GitHub Actions", "Windows Task Scheduler"]:
        check(phrase in runtime, f"runtime-modes.md missing scheduler preset: {phrase}", failures)

    batch = read_text(root / "references/batch-refinement.md")
    for phrase in ["Three-Pass Rubber-Duck Loop", "passCount", "SQLite", "Stop Conditions"]:
        check(phrase in batch, f"batch-refinement.md missing: {phrase}", failures)

    sqlite_reference = read_text(root / "references/sqlite-state-store.md")
    for phrase in ["Use SQLite When", "Avoid SQLite When", "factory-state.sqlite.sql", "Smoke Test"]:
        check(phrase in sqlite_reference, f"sqlite-state-store.md missing: {phrase}", failures)

    sqlite_schema = read_text(root / "assets/templates/factory-state.sqlite.sql")
    try:
        connection = sqlite3.connect(":memory:")
        connection.executescript(sqlite_schema)
        connection.close()
    except sqlite3.Error as exc:
        failures.append(f"factory-state.sqlite.sql invalid SQLite schema: {exc}")
    for table_name in ["runs", "items", "tasks", "claims", "reviews", "artifacts", "outcomes", "pipeline_log"]:
        check(f"CREATE TABLE IF NOT EXISTS {table_name}" in sqlite_schema, f"SQLite schema missing table: {table_name}", failures)

    setup = read_text(root / "references/workspace-setup.md")
    for surface in [
        "GitHub Copilot App",
        "GitHub Copilot CLI",
        "Microsoft Scout",
        "VS Code GitHub Copilot Chat",
        "Copilot Scheduler",
        "OpenClaw",
        "GitHub Actions",
    ]:
        check(surface in setup, f"workspace-setup.md missing surface: {surface}", failures)
    for phrase in ["Capability Checklist", "Verification source", "Verification timestamp", "Checked by"]:
        check(phrase in setup, f"workspace-setup.md missing setup evidence field: {phrase}", failures)

    state = validate_json(root, "assets/templates/factory-state.json", failures)
    first_run_queue = validate_json(root, "assets/templates/first-run-queue.json", failures)
    task = validate_json(root, "assets/templates/task.json", failures)
    runtime_state = state.get("runtime", {}) if isinstance(state, dict) else {}
    check("adapter" in runtime_state, "factory-state.json missing runtime.adapter", failures)
    check("limits" in runtime_state, "factory-state.json missing runtime.limits", failures)
    check("notifications" in runtime_state, "factory-state.json missing runtime.notifications", failures)
    adapter = runtime_state.get("adapter", {}) if isinstance(runtime_state, dict) else {}
    for field in [
        "primarySurface",
        "skillLocation",
        "promptRunner",
        "stateStore",
        "scheduleMechanism",
        "approvalPolicy",
        "verifiedDocs",
        "lastSetupCheckAt",
    ]:
        check(field in adapter, f"factory-state.json missing runtime.adapter.{field}", failures)
    check("outputs" in task, "task.json missing outputs", failures)
    first_tasks = first_run_queue.get("tasks", []) if isinstance(first_run_queue, dict) else []
    check(len(first_tasks) >= 3, "first-run-queue.json should include at least three starter tasks", failures)
    first_kinds = {task_item.get("kind") for task_item in first_tasks if isinstance(task_item, dict)}
    for kind in ["discover", "review", "learn"]:
        check(kind in first_kinds, f"first-run-queue.json missing starter task kind: {kind}", failures)
    first_ids: set[str] = set()
    for task_item in first_tasks:
        if isinstance(task_item, dict):
            task_id = task_item.get("id")
            check(isinstance(task_id, str) and task_id not in first_ids, f"first-run task has duplicate or missing id: {task_id}", failures)
            if isinstance(task_id, str):
                first_ids.add(task_id)
            check(task_item.get("assignee") is None, f"first-run task {task_id} should keep assignee null for surface portability", failures)
            constraints = task_item.get("constraints")
            check(isinstance(constraints, list) and len(constraints) >= 3, f"first-run task {task_id} should include safety constraints", failures)
            for required_constraint in ["no login", "no payment", "no personal data", "no external publishing"]:
                check(
                    any(required_constraint in str(constraint) for constraint in constraints or []),
                    f"first-run task {task_id} missing constraint containing: {required_constraint}",
                    failures,
                )
            outputs = task_item.get("outputs", {})
            artifact = outputs.get("artifact")
            check("artifact" in outputs, f"first-run task {task_id} missing outputs.artifact", failures)
            if isinstance(task_id, str) and isinstance(artifact, str):
                check(task_id in artifact, f"first-run task {task_id} artifact path should include task id", failures)

    workspace_setup = read_text(root / "references/workspace-setup.md")
    check("replace domain, audience, success metric" in workspace_setup, "workspace-setup.md missing first-run substitution rule", failures)
    check("assets/examples/setup-packets.md" in workspace_setup, "workspace-setup.md missing setup packet examples reference", failures)

    setup_examples = read_text(root / "assets/examples/setup-packets.md")
    for surface in [
        "GitHub Copilot App",
        "VS Code GitHub Copilot Chat",
        "GitHub Copilot CLI",
        "Microsoft Scout",
        "Copilot Scheduler",
        "OpenClaw",
        "GitHub Actions",
    ]:
        check(surface in setup_examples, f"setup-packets.md missing example for: {surface}", failures)
    for phrase in ["Verification source", "Runtime profile", "Preflight result", "First three jobs"]:
        check(phrase in setup_examples, f"setup-packets.md missing field: {phrase}", failures)

    preflight = read_text(root / "assets/templates/setup-preflight.md")
    for phrase in ["Capability Gate", "Approval Boundaries", "Schedule Gate", "Verification source", "Evidence"]:
        check(phrase in preflight, f"setup-preflight.md missing: {phrase}", failures)

    commander = read_text(root / "assets/prompts/commander.md")
    for phrase in ["setup preflight", "adapter selected", "approval policy"]:
        check(phrase in commander, f"commander prompt missing preflight phrase: {phrase}", failures)

    worker = read_text(root / "assets/prompts/worker.md")
    check("Do not edit shared queues" in worker, "worker prompt missing artifact-only guard", failures)
    check("approved tools" in worker, "worker prompt missing surface adapter permission guard", failures)
    check("````\n\n```" not in worker, "worker prompt has dangling nested fence", failures)

    reporter = read_text(root / "assets/prompts/reporter-learner.md")
    for phrase in ["Adapter health", "Schedule drift", "Persistence failures"]:
        check(phrase in reporter, f"reporter prompt missing operational status: {phrase}", failures)

    check(not (root / "scripts" / "__pycache__").exists(), "scripts/__pycache__ should not be packaged", failures)

    initializer = read_text(root / "scripts/init_factory_workspace.py")
    for phrase in ["--apply", "--force", "first-run-queue.json", "tasks-pending.json", "pipeline-log.jsonl"]:
        check(phrase in initializer, f"init_factory_workspace.py missing: {phrase}", failures)

    sqlite_initializer = read_text(root / "scripts/init_factory_sqlite.py")
    for phrase in ["--apply", "--force", "factory-state.sqlite.sql", "first-run-queue.json", "INSERT INTO tasks"]:
        check(phrase in sqlite_initializer, f"init_factory_sqlite.py missing: {phrase}", failures)

    smoke_test = read_text(root / "scripts/smoke_test_initializers.py")
    for phrase in ["init_factory_workspace.py", "init_factory_sqlite.py", "dry-run", "SELECT COUNT(*) FROM tasks", "shutil.rmtree"]:
        check(phrase in smoke_test, f"smoke_test_initializers.py missing: {phrase}", failures)

    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".py"}:
            text = read_text(path)
            if ABSOLUTE_PATH_PATTERN.search(text):
                failures.append(f"machine-specific absolute path in {path.relative_to(root)}")

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS")
    print(f"validated: {root}")
    print(f"required_files: {len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())