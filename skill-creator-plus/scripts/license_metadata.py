#!/usr/bin/env python3

import hashlib
import json
from pathlib import Path, PurePosixPath


SKILL_ROOT = Path(__file__).resolve().parent.parent
REFERENCES_ROOT = SKILL_ROOT / "references"
PROFILE_FILE = REFERENCES_ROOT / "target-license-profiles.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_profiles() -> dict:
    return json.loads(PROFILE_FILE.read_text(encoding="utf-8"))


def profile_snapshot(profile_id: str) -> dict:
    registry = load_profiles()
    profile = registry["profiles"].get(profile_id)
    if profile is None:
        raise ValueError(f"Unknown target license profile: {profile_id}")

    template = REFERENCES_ROOT / profile["template"]
    if not template.is_file():
        raise ValueError(f"License template not found: {profile['template']}")

    return {
        "id": profile_id,
        "registryVersion": registry["schemaVersion"],
        "spdxId": profile["spdxId"],
        "frontmatterLicense": profile["frontmatterLicense"],
        "evidenceFile": profile["evidenceFile"],
        "templateSha256": sha256_file(template),
        "requiresAuthorAttribution": profile["requiresAuthorAttribution"],
    }


def render_license(profile_id: str, author: str) -> tuple[str, str, dict]:
    registry = load_profiles()
    profile = registry["profiles"].get(profile_id)
    if profile is None:
        raise ValueError(f"Unknown target license profile: {profile_id}")

    template = REFERENCES_ROOT / profile["template"]
    return (
        profile["evidenceFile"],
        template.read_text(encoding="utf-8").format(author=author),
        profile_snapshot(profile_id),
    )


def safe_relative_path(value: str) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return False
    return all(":" not in part and not part.endswith((".", " ")) for part in path.parts)


def resolve_evidence_path(skill_root: Path, value: str) -> Path | None:
    if not safe_relative_path(value):
        return None
    candidate = skill_root / Path(*PurePosixPath(value).parts)
    if candidate.is_symlink() or not candidate.is_file():
        return None
    try:
        candidate.resolve().relative_to(skill_root.resolve())
    except ValueError:
        return None
    return candidate