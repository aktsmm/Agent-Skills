#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path

from license_metadata import render_license, sha256_file


SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

SKILL_TEMPLATE = """---
name: {skill_name}
description: "TODO: Describe what this Skill does and when it should trigger."
license: {license_name}
metadata:
  author: {author}
---

# {skill_title}

## When to Use

- TODO: Add concrete trigger phrases and task conditions.

## Workflow

1. TODO: Add the smallest useful workflow.
2. TODO: State how success is verified.
"""

PYTHON_HELPER = """#!/usr/bin/env python3

def main():
    raise NotImplementedError("Implement this Skill helper")


if __name__ == "__main__":
    main()
"""

PYTHON_TEST = """import unittest


class HelperTests(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
"""


def title_case_skill_name(skill_name: str) -> str:
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def validate_request(skill_name: str, output_root: Path, profile: str, author: str) -> None:
    if not SKILL_NAME_PATTERN.fullmatch(skill_name) or len(skill_name) > 64:
        raise ValueError("Skill name must be hyphen-case and no longer than 64 characters")
    if not output_root.is_dir() or output_root.is_symlink():
        raise ValueError("Output path must be an existing non-symlink directory")
    if not author.strip():
        raise ValueError("Author attribution is required for a self-authored Skill")
    render_license(profile, author)


def write_resource_starters(skill_dir: Path, with_python_helper: bool, with_resources: bool) -> None:
    if with_python_helper:
        scripts = skill_dir / "scripts"
        scripts.mkdir()
        (scripts / "helper.py").write_text(PYTHON_HELPER, encoding="utf-8")
        (scripts / "requirements.txt").write_text("# Add runtime dependencies here.\n", encoding="utf-8")
        (scripts / "test_helper.py").write_text(PYTHON_TEST, encoding="utf-8")

    if with_resources:
        references = skill_dir / "references"
        assets = skill_dir / "assets"
        references.mkdir()
        assets.mkdir()
        (references / "usage-notes.md").write_text("# Usage Notes\n\nTODO: Add on-demand detail.\n", encoding="utf-8")
        (assets / "template.txt").write_text("TODO: Replace or delete this template.\n", encoding="utf-8")


def init_skill(
    skill_name: str,
    output_path: str | Path,
    license_profile: str,
    author_attribution: str,
    *,
    with_python_helper: bool = False,
    with_resources: bool = False,
) -> Path | None:
    supplied_output_root = Path(output_path).expanduser()
    output_root = supplied_output_root.resolve()
    stage_root: Path | None = None

    try:
        if supplied_output_root.is_symlink():
            raise ValueError("Output path must not be a symlink")
        validate_request(skill_name, output_root, license_profile, author_attribution)
        target = output_root / skill_name
        if target.exists() or target.is_symlink():
            raise ValueError(f"Skill directory already exists: {target}")

        evidence_file, evidence_content, profile = render_license(license_profile, author_attribution)
        stage_root = Path(tempfile.mkdtemp(prefix=f".{skill_name}-", dir=output_root))
        stage_skill = stage_root / skill_name
        stage_skill.mkdir()

        (stage_skill / "SKILL.md").write_text(
            SKILL_TEMPLATE.format(
                skill_name=skill_name,
                skill_title=title_case_skill_name(skill_name),
                license_name=profile["frontmatterLicense"],
                author=author_attribution,
            ),
            encoding="utf-8",
        )
        evidence_path = stage_skill / evidence_file
        evidence_path.write_text(evidence_content, encoding="utf-8")
        write_resource_starters(stage_skill, with_python_helper, with_resources)

        manifest = {
            "schemaVersion": 1,
            "provenance": "self-authored",
            "spdxId": profile["spdxId"],
            "frontmatterLicense": profile["frontmatterLicense"],
            "profile": profile,
            "authorAttribution": {"value": author_attribution},
            "evidence": [{"path": evidence_file, "sha256": sha256_file(evidence_path)}],
            "confirmationMode": "explicit-cli",
        }
        (stage_skill / "skill-license.json").write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )

        if not (stage_skill / "SKILL.md").is_file() or not evidence_path.is_file():
            raise RuntimeError("Generated Skill is incomplete")
        stage_skill.rename(target)
        shutil.rmtree(stage_root, ignore_errors=True)
        print(f"Created Skill: {target}")
        return target
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Error: {error}")
        return None
    finally:
        if stage_root and stage_root.exists():
            shutil.rmtree(stage_root, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a minimal self-authored Skill")
    parser.add_argument("skill_name")
    parser.add_argument("--path", required=True, help="Existing directory that will contain the Skill")
    parser.add_argument("--license-profile", required=True, help="Target profile ID, for example cc-by-nc-sa-4.0")
    parser.add_argument("--author-attribution", required=True, help="Display attribution stored in metadata.author")
    parser.add_argument("--with-python-helper", action="store_true", help="Create an opt-in Python helper starter set")
    parser.add_argument("--with-resources", action="store_true", help="Create opt-in reference and asset starters")
    args = parser.parse_args()

    result = init_skill(
        args.skill_name,
        args.path,
        args.license_profile,
        args.author_attribution,
        with_python_helper=args.with_python_helper,
        with_resources=args.with_resources,
    )
    return 0 if result else 1


if __name__ == "__main__":
    raise SystemExit(main())
