from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import subprocess
import sys
from datetime import date, datetime, time
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo


def canonical_path(value: str | Path) -> Path:
    return Path(os.path.expandvars(str(value))).expanduser().resolve(strict=False)


def path_key(path: Path) -> str:
    return os.path.normcase(str(path))


def is_descendant(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def load_config(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    config = json.loads(raw.decode("utf-8"))
    if config.get("schemaVersion") != 1 or not config.get("roots"):
        raise ValueError("config requires schemaVersion 1 and at least one root")
    return config, hashlib.sha256(raw).hexdigest()


def normalize_roots(config: dict[str, Any]) -> list[dict[str, Any]]:
    roots: list[dict[str, Any]] = []
    ids: set[str] = set()
    for source in config["roots"]:
        root_id = source.get("id")
        kinds = sorted(set(source.get("kinds", ["files"])))
        if not root_id or root_id in ids or not set(kinds).issubset({"files", "git"}):
            raise ValueError(f"invalid or duplicate root: {root_id!r}")
        ids.add(root_id)
        roots.append(
            {
                **source,
                "id": root_id,
                "path": canonical_path(source["path"]),
                "kinds": kinds,
                "required": bool(source.get("required", False)),
            }
        )
    roots.sort(key=lambda item: (len(item["path"].parts), path_key(item["path"]), item["id"]))
    effective: list[dict[str, Any]] = []
    for root in roots:
        parent = next(
            (
                item
                for item in effective
                if is_descendant(root["path"], item["path"])
                and set(root["kinds"]).issubset(item["kinds"])
            ),
            None,
        )
        if parent:
            raise ValueError(f"root {root['id']!r} is covered by {parent['id']!r}")
        effective.append(root)
    return effective


def iter_files(root: Path, excluded: set[str]) -> Iterable[Path]:
    excluded_lower = {item.lower() for item in excluded}
    for current, directories, files in os.walk(root, topdown=True, followlinks=False):
        directories[:] = sorted(
            (item for item in directories if item.lower() not in excluded_lower), key=str.casefold
        )
        for filename in sorted(files, key=str.casefold):
            yield Path(current, filename)


def stat_file(path: Path) -> os.stat_result:
    raw = str(path)
    if os.name == "nt" and len(raw) >= 248 and not raw.startswith("\\\\?\\"):
        return os.stat(f"\\\\?\\{raw}")
    return path.stat()


def discover_repositories(root: Path, excluded: set[str]) -> list[Path]:
    repositories: dict[str, Path] = {}
    excluded_lower = {item.lower() for item in excluded if item.lower() != ".git"}
    for current, directories, files in os.walk(root, topdown=True, followlinks=False):
        if ".git" in directories or ".git" in files:
            repository = canonical_path(current)
            repositories[path_key(repository)] = repository
        directories[:] = sorted(
            (
                item
                for item in directories
                if item.lower() not in excluded_lower and item.lower() != ".git"
            ),
            key=str.casefold,
        )
    return [repositories[key] for key in sorted(repositories)]


def git_commits(repository: Path, start: datetime, end: datetime) -> list[dict[str, str]]:
    completed = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={repository}",
            "-C",
            str(repository),
            "log",
            "--all",
            f"--since={start.isoformat()}",
            f"--until={end.isoformat()}",
            "--format=%H%x1f%aI%x1f%an%x1f%s",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "git log failed")
    commits = []
    for line in completed.stdout.splitlines():
        if line:
            commit_hash, authored_at, author, subject = line.split("\x1f", 3)
            commits.append(
                {"hash": commit_hash, "authoredAt": authored_at, "author": author, "subject": subject}
            )
    return sorted(commits, key=lambda item: (item["authoredAt"], item["hash"]))


def classify(relative_path: str, config: dict[str, Any]) -> str:
    normalized = relative_path.replace("\\", "/").lower()
    for rule in config.get("classifications", []):
        if any(fnmatch.fnmatch(normalized, pattern.lower()) for pattern in rule.get("patterns", [])):
            return rule["category"]
    return "signal"


def collect_root(root: dict[str, Any], config: dict[str, Any], start: datetime, end: datetime) -> dict[str, Any]:
    path = root["path"]
    result: dict[str, Any] = {
        "id": root["id"], "path": str(path), "required": root["required"],
        "status": "complete", "files": [], "repositories": [], "errors": [],
    }
    if not path.exists():
        result["status"] = "error" if root["required"] else "unavailable"
        result["errors"].append("root does not exist")
        return result
    excluded = set(config.get("excludeDirectories", []))
    if "files" in root["kinds"]:
        for file_path in iter_files(path, excluded):
            try:
                stat = stat_file(file_path)
                modified_at = datetime.fromtimestamp(stat.st_mtime, start.tzinfo)
            except OSError as error:
                result["errors"].append(f"{file_path}: {error}")
                continue
            if start <= modified_at < end:
                relative = file_path.relative_to(path).as_posix()
                result["files"].append(
                    {"path": str(file_path), "relativePath": relative,
                     "modifiedAt": modified_at.isoformat(), "sizeBytes": stat.st_size,
                     "category": classify(relative, config)}
                )
    if "git" in root["kinds"]:
        for repository in discover_repositories(path, excluded):
            try:
                commits = git_commits(repository, start, end)
                result["repositories"].append(
                    {"path": str(repository), "relativePath": repository.relative_to(path).as_posix() or ".",
                     "commitCount": len(commits), "commits": commits}
                )
            except RuntimeError as error:
                result["errors"].append(f"{repository}: {error}")
    result["files"].sort(key=lambda item: item["relativePath"].casefold())
    result["repositories"].sort(key=lambda item: item["relativePath"].casefold())
    if result["errors"]:
        result["status"] = "partial"
    result["fileCount"] = len(result["files"])
    result["repositoryCount"] = len(result["repositories"])
    result["commitCount"] = sum(item["commitCount"] for item in result["repositories"])
    return result


def write_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json.loads(temporary.read_text(encoding="utf-8"))
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect deterministic local evidence for a daily report")
    parser.add_argument("--date", type=date.fromisoformat)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate-config", action="store_true")
    parser.add_argument("--explain-path", type=Path)
    arguments = parser.parse_args()
    try:
        repo_root = canonical_path(arguments.repo_root)
        config_path = canonical_path(arguments.config or repo_root / "_datasources/daily-activity-sources.json")
        config, config_hash = load_config(config_path)
        roots = normalize_roots(config)
        if arguments.explain_path:
            candidate = canonical_path(arguments.explain_path)
            covering = [root["id"] for root in roots if is_descendant(candidate, root["path"])]
            print(json.dumps({"path": str(candidate), "covered": bool(covering), "coveringRoots": covering}))
            return 0 if covering else 2
        if arguments.validate_config:
            print(json.dumps({"status": "valid", "rootCount": len(roots), "configHash": config_hash}))
            return 0
        if not arguments.date:
            raise ValueError("--date is required")
        timezone = ZoneInfo(config.get("timeZone", "UTC"))
        start = datetime.combine(arguments.date, time.min, timezone)
        end = datetime.combine(date.fromordinal(arguments.date.toordinal() + 1), time.min, timezone)
        results = [collect_root(root, config, start, end) for root in roots]
        required_failed = any(root["required"] and root["status"] != "complete" for root in results)
        status = "error" if required_failed else "partial" if any(
            root["status"] != "complete" for root in results
        ) else "complete"
        summary = {
            "rootCount": len(results),
            "fileCount": sum(root.get("fileCount", 0) for root in results),
            "repositoryCount": sum(root.get("repositoryCount", 0) for root in results),
            "commitCount": sum(root.get("commitCount", 0) for root in results),
            "errorCount": sum(len(root["errors"]) for root in results),
        }
        payload = {
            "schemaVersion": 1, "targetDate": arguments.date.isoformat(),
            "timeZone": config.get("timeZone", "UTC"),
            "window": {"fromInclusive": start.isoformat(), "toExclusive": end.isoformat()},
            "collectedAt": datetime.now(timezone).isoformat(), "configHash": config_hash,
            "status": status, "summary": summary, "roots": results,
        }
        output = canonical_path(arguments.output or repo_root / "_reports" / arguments.date.strftime("%Y-%m") / "daily-ops" / f"{arguments.date}.json")
        write_atomic(output, payload)
        print(json.dumps({"status": status, "output": str(output), **summary}))
        return 0 if status in {"complete", "partial"} else 1
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "error", "error": str(error)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())