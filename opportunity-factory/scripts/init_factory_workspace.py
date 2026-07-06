#!/usr/bin/env python3
"""Initialize an Opportunity Factory state folder from bundled templates."""

from __future__ import annotations

import argparse
import copy
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any], *, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite existing file without --force: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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


def build_state(template: dict[str, Any], args: argparse.Namespace, now: str) -> dict[str, Any]:
    state = copy.deepcopy(template)
    state["frame"]["domain"] = args.domain
    state["frame"]["artifactType"] = args.artifact_type
    state["frame"]["audience"] = args.audience
    state["frame"]["successMetric"] = args.success_metric
    state["frame"]["constraints"] = args.constraint

    runtime = state["runtime"]
    runtime["mode"] = args.runtime_mode
    runtime["adapter"]["primarySurface"] = args.primary_surface
    runtime["adapter"]["secondarySurfaces"] = args.secondary_surface
    runtime["adapter"]["skillLocation"] = args.skill_location
    runtime["adapter"]["promptRunner"] = args.prompt_runner
    runtime["adapter"]["stateStore"] = args.state_store
    runtime["adapter"]["scheduleMechanism"] = args.schedule_mechanism
    runtime["adapter"]["approvalPolicy"] = args.approval_policy
    runtime["adapter"]["verifiedDocs"] = args.verified_doc
    runtime["adapter"]["lastSetupCheckAt"] = now
    state["updatedAt"] = now
    return state


def build_queue(template: dict[str, Any], args: argparse.Namespace, now: str, date_id: str) -> dict[str, Any]:
    queue = copy.deepcopy(template)
    replacements = {
        "YYYY-MM-DDTHH:mm:ssZ": now,
        "YYYYMMDD": date_id,
        "<domain>": args.domain,
        "<audience>": args.audience,
        "<primary metric>": args.success_metric,
    }
    queue = replace_placeholders(queue, replacements)
    queue["updatedAt"] = now
    return queue


def build_empty_done(now: str) -> dict[str, Any]:
    return {"schemaVersion": 1, "updatedAt": now, "tasks": []}


def build_outcome_log(now: str) -> dict[str, Any]:
    return {"schemaVersion": 1, "updatedAt": now, "outcomes": []}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize an Opportunity Factory state folder.")
    parser.add_argument("--skill-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--artifact-type", required=True)
    parser.add_argument("--audience", required=True)
    parser.add_argument("--success-metric", required=True)
    parser.add_argument("--constraint", action="append", default=[])
    parser.add_argument("--runtime-mode", default="vscode-manual")
    parser.add_argument("--primary-surface", default="VS Code GitHub Copilot Chat")
    parser.add_argument("--secondary-surface", action="append", default=[])
    parser.add_argument("--skill-location", default="<set by target surface>")
    parser.add_argument("--prompt-runner", default="manual prompt invocation")
    parser.add_argument("--state-store", default="repo files")
    parser.add_argument("--schedule-mechanism", default="manual")
    parser.add_argument("--approval-policy", default="human approval for publish/payment/account/secrets/personal data/destructive commands")
    parser.add_argument("--verified-doc", action="append", default=[])
    parser.add_argument("--apply", action="store_true", help="Write files. Without this flag, only print the plan.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated state files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_root = Path(args.skill_root).resolve()
    state_dir = Path(args.state_dir).resolve()
    template_dir = skill_root / "assets" / "templates"
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    date_id = now[:10].replace("-", "")

    state = build_state(read_json(template_dir / "factory-state.json"), args, now)
    queue = build_queue(read_json(template_dir / "first-run-queue.json"), args, now, date_id)

    outputs = {
        "factory-state.json": state,
        "tasks-pending.json": queue,
        "tasks-done.json": build_empty_done(now),
        "outcome-log.json": build_outcome_log(now),
    }

    print("Opportunity Factory initializer")
    print(f"state_dir: {state_dir}")
    print(f"mode: {'apply' if args.apply else 'dry-run'}")
    for relative_path in [*outputs.keys(), "pipeline-log.jsonl", "artifacts/"]:
        print(f"- {relative_path}")

    if not args.apply:
        print("dry-run only; rerun with --apply to write files")
        return 0

    state_dir.mkdir(parents=True, exist_ok=True)
    for file_name, data in outputs.items():
        write_json(state_dir / file_name, data, force=args.force)
    pipeline_log = state_dir / "pipeline-log.jsonl"
    if pipeline_log.exists() and not args.force:
        raise FileExistsError(f"refusing to overwrite existing file without --force: {pipeline_log}")
    pipeline_log.write_text(json.dumps({"ts": now, "event": "factory_initialized"}, ensure_ascii=False) + "\n", encoding="utf-8")
    (state_dir / "artifacts").mkdir(exist_ok=True)
    print("initialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())