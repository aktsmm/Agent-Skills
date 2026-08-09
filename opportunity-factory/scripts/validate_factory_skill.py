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
    "references/tunable-defaults.md",
    "references/persistence-profile.md",
    "references/fallback-lane.md",
    "references/approval-policy.md",
    "references/prompt-self-improvement.md",
    "references/self-designing-factory.md",
    "references/lifecycle-and-health.md",
    "references/dashboard-state.md",
    "assets/prompts/commander.md",
    "assets/prompts/worker.md",
    "assets/prompts/reporter-learner.md",
    "assets/templates/factory-plan.md",
    "assets/templates/factory-state.json",
    "assets/templates/dashboard-state.json",
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
            r"(?<![A-Za-z0-9])[A-Za-z]:\\",
            r"(?<![A-Za-z0-9])[A-Za-z]:/",
            r"\\\\[^\\\r\n]+\\",
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
    check("repair -> validate -> independent re-review" in skill, "SKILL.md missing repair/re-review rule", failures)
    check(len(skill.splitlines()) <= 150, "SKILL.md should stay under 150 lines", failures)

    rubber_duck = read_text(root / "references/rubber-duck-review.md")
    for phrase in ["Repair -> Re-review Contract", "repair-started", "blocked-independence", "parked-independence", "overridden-independence", "repair-start-failed", "review-exhausted", "persistence-exhausted", "workflow repair round", "never self-certifies", "min(reviewRepairRounds, profile.maxIteration - iterationsUsed)"]:
        check(phrase in rubber_duck, f"rubber-duck-review.md missing repair contract phrase: {phrase}", failures)

    dashboard_reference = read_text(root / "references/dashboard-state.md")
    for phrase in ["parentTaskId", "workflowRound", "findingIds", "findingResolution", "validationResults", "repairTaskId", "receiptSource", "receiptRef", "receiptHash", "outputHash", "criticLog", "唯一の durable log", "Open repair"]:
        check(phrase in dashboard_reference, f"dashboard-state.md missing criticLog repair field: {phrase}", failures)

    runtime = read_text(root / "references/runtime-modes.md")
    for phrase in ["Hosted Agent Scheduler", "Copilot Scheduler (VS Code Extension)", "OpenClaw / Cron", "GitHub Actions", "Windows Task Scheduler"]:
        check(phrase in runtime, f"runtime-modes.md missing scheduler preset: {phrase}", failures)
    check("workflow-review" in runtime, "runtime-modes.md missing workflow-review cadence", failures)
    check("user-approved autonomy envelope" in runtime, "runtime-modes.md missing autonomy-envelope gate rule", failures)
    check("create-new/O_EXCL" in runtime and "never test-then-create" in runtime, "runtime-modes.md missing atomic lock rule", failures)
    lifecycle = read_text(root / "references/lifecycle-and-health.md")
    for phrase in [
        "Portfolio Promotion Lane",
        "Product Maturation Lane",
        "Independent Review",
        "Health Reconciler",
        "private release-readiness",
        "persisted slice/revision counters",
        "deterministic selection order",
        "Never delete a lock from TTL alone",
    ]:
        check(phrase in lifecycle, f"lifecycle-and-health.md missing: {phrase}", failures)
    check("repair-start-failed" in lifecycle, "lifecycle-and-health.md missing repair-start recovery", failures)
    approval_policy = read_text(root / "references/approval-policy.md")
    check("private/internal remote" in approval_policy, "approval-policy.md missing qualified private/internal push rule", failures)
    check("Public remote" in approval_policy, "approval-policy.md missing public remote security-approve rule", failures)

    batch = read_text(root / "references/batch-refinement.md")
    for phrase in ["Three-Pass Rubber-Duck Loop", "passCount", "SQLite", "Stop Conditions", "independent re-review", "stable finding IDs"]:
        check(phrase in batch, f"batch-refinement.md missing: {phrase}", failures)

    tunable = read_text(root / "references/tunable-defaults.md")
    for phrase in ["Review repair workflow rounds", "下限 3", "上限 20", "Review repair contract", "Repair -> Re-review Contract", "blocked-independence"]:
        check(phrase in tunable, f"tunable-defaults.md missing repair invariant: {phrase}", failures)

    workflow = read_text(root / "references/workflow.md")
    for phrase in ["`repair`", "`replan`", "Repair and Re-review Queue"]:
        check(phrase in workflow, f"workflow.md missing repair queue contract: {phrase}", failures)

    persistence = read_text(root / "references/persistence-profile.md")
    for phrase in ["Review Repair Accounting", "parentTaskId", "独立 attempt-log", "persistence-exhausted"]:
        check(phrase in persistence, f"persistence-profile.md missing repair accounting: {phrase}", failures)

    for phrase in ["parked-independence", "overridden-independence"]:
        check(phrase in approval_policy, f"approval-policy.md missing independence approval rule: {phrase}", failures)

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
    for table_name in ["runs", "items", "tasks", "claims", "reviews", "critic_log", "repair_attempts", "artifacts", "outcomes", "pipeline_log"]:
        check(f"CREATE TABLE IF NOT EXISTS {table_name}" in sqlite_schema, f"SQLite schema missing table: {table_name}", failures)
    for task_field in ["parent_task_id", "finding_ids_json", "input_hash", "acceptance_checks_json"]:
        check(task_field in sqlite_schema, f"SQLite tasks missing repair field: {task_field}", failures)
    for critic_field in ["workflow_round", "validation_results_json", "repair_task_id", "layer", "role", "receipt_source", "receipt_ref", "receipt_hash", "independence_verdict", "next_state"]:
        check(critic_field in sqlite_schema, f"SQLite critic_log missing field: {critic_field}", failures)
    for attempt_field in ["parent_task_id", "repair_task_id", "workflow_round", "repair-start-failed", "validation-failed"]:
        check(attempt_field in sqlite_schema, f"SQLite repair_attempts missing field or state: {attempt_field}", failures)
    check("UNIQUE (parent_task_id, workflow_round)" in sqlite_schema, "SQLite repair_attempts missing parent-round uniqueness", failures)
    for claim_field in ["run_id", "heartbeat_at", "expires_at"]:
        check(claim_field in sqlite_schema, f"SQLite claims missing field: {claim_field}", failures)

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
    dashboard_state = validate_json(root, "assets/templates/dashboard-state.json", failures)
    first_run_queue = validate_json(root, "assets/templates/first-run-queue.json", failures)
    task = validate_json(root, "assets/templates/task.json", failures)
    runtime_state = state.get("runtime", {}) if isinstance(state, dict) else {}
    check("adapter" in runtime_state, "factory-state.json missing runtime.adapter", failures)
    check("limits" in runtime_state, "factory-state.json missing runtime.limits", failures)
    check("notifications" in runtime_state, "factory-state.json missing runtime.notifications", failures)
    adapter = runtime_state.get("adapter", {}) if isinstance(runtime_state, dict) else {}
    limits = runtime_state.get("limits", {}) if isinstance(runtime_state, dict) else {}
    repair_rounds = limits.get("reviewRepairRounds") if isinstance(limits, dict) else None
    check(isinstance(repair_rounds, int) and 3 <= repair_rounds <= 20, "factory-state.json reviewRepairRounds must be 3-20", failures)
    independence_limit = limits.get("independenceBlockLimit") if isinstance(limits, dict) else None
    check(isinstance(independence_limit, int) and 1 <= independence_limit <= 5, "factory-state.json independenceBlockLimit must be 1-5", failures)
    queue_targets = runtime_state.get("queueTargets", {}) if isinstance(runtime_state, dict) else {}
    for kind in ["repair", "replan"]:
        check(kind in queue_targets, f"factory-state.json queueTargets missing: {kind}", failures)
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
    for kind in ["repair", "replan"]:
        check(kind in str(task.get("kind", "")), f"task.json missing task kind: {kind}", failures)
    for field in ["parentTaskId", "findingIds", "inputHash", "acceptanceChecks"]:
        check(field in task, f"task.json missing repair field: {field}", failures)
    acceptance_checks = task.get("acceptanceChecks") if isinstance(task, dict) else None
    check(isinstance(acceptance_checks, list) and bool(acceptance_checks), "task.json acceptanceChecks must be a non-empty list", failures)
    if isinstance(acceptance_checks, list) and acceptance_checks and isinstance(acceptance_checks[0], dict):
        for field in ["id", "check", "expected", "actual", "result", "evidenceRef"]:
            check(field in acceptance_checks[0], f"task.json acceptanceChecks entry missing: {field}", failures)
        check(acceptance_checks[0].get("result") in {"pending", "pass", "fail"}, "task.json acceptanceChecks result is invalid", failures)
    for claim_field in ["claimRunId", "claimHeartbeatAt", "claimExpiresAt"]:
        check(claim_field in task, f"task.json missing claim field: {claim_field}", failures)
    answering_policy = dashboard_state.get("answeringPolicy", {}) if isinstance(dashboard_state, dict) else {}
    check(answering_policy.get("useDashboardFirst") is True, "dashboard-state.json missing answeringPolicy.useDashboardFirst=true", failures)
    for field in [
        "executiveSummary",
        "workflows",
        "queues",
        "risksAndBlockers",
        "nextActions",
        "portfolioPromotion",
        "productMaturation",
        "criticLog",
        "pendingApprovals",
    ]:
        check(field in dashboard_state, f"dashboard-state.json missing {field}", failures)
    automation_policy = dashboard_state.get("automationPolicy", {}) if isinstance(dashboard_state, dict) else {}
    check("allowedWithReviewerAndQueueGate" in automation_policy, "dashboard-state.json missing reviewer/queue autonomy policy", failures)
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
            for claim_field in ["claimRunId", "claimHeartbeatAt", "claimExpiresAt"]:
                check(claim_field in task_item, f"first-run task {task_id} missing claim field: {claim_field}", failures)
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
    for phrase in ["criticLogEvent", "one `repair` child task", "repair_attempts", "blocked-independence", "one parent attempt whenever deterministic validation runs"]:
        check(phrase in commander, f"commander prompt missing repair orchestration: {phrase}", failures)

    worker = read_text(root / "assets/prompts/worker.md")
    check("Do not edit shared queues" in worker, "worker prompt missing artifact-only guard", failures)
    check("approved tools" in worker, "worker prompt missing surface adapter permission guard", failures)
    for phrase in ["criticLogEvent", "## required fixes", "## review repair handoff", "parentTaskId"]:
        check(phrase in worker, f"worker prompt missing repair handoff: {phrase}", failures)
    for phrase in ["reviewRecheck", "producerModel", "criticModel", "producerFamily", "criticFamily", "familyResolver", "independenceVerdict", "receiptSource", "receiptRef", "receiptHash", "nextState"]:
        check(phrase in worker, f"worker prompt missing independent re-review record: {phrase}", failures)
    check("````\n\n```" not in worker, "worker prompt has dangling nested fence", failures)

    reporter = read_text(root / "assets/prompts/reporter-learner.md")
    for phrase in ["Adapter health", "Schedule drift", "Persistence failures", "criticLog", "parked-independence"]:
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
            if path.resolve() == Path(__file__).resolve():
                continue
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