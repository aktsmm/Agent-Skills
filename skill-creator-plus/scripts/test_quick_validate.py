import tempfile
import unittest
import json
import subprocess
import sys
from pathlib import Path

from init_skill import init_skill
from quick_validate import validate_skill


class QuickValidateTests(unittest.TestCase):
    def write_skill(self, root: Path, folder: str, frontmatter: str) -> Path:
        skill_dir = root / folder
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            f"---\n{frontmatter}\n---\n\n# Skill\n",
            encoding="utf-8",
        )
        (skill_dir / "LICENSE.txt").write_text("license\n", encoding="utf-8")
        return skill_dir

    def test_accepts_current_vscode_skill_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self.write_skill(
                Path(tmpdir),
                "compare-copilot-sessions",
                "\n".join([
                    "name: compare-copilot-sessions",
                    'description: "Compare Copilot sessions. Use when comparing model cost and quality or セッション比較."',
                    'argument-hint: "session paths or metrics files"',
                    "user-invocable: true",
                    "disable-model-invocation: false",
                    "context: fork",
                    'compatibility: "VS Code and Claude Code; use ordinary subagent delegation elsewhere."',
                    "license: CC BY-NC-SA 4.0",
                    "metadata:",
                    "  author: Example Author",
                ]),
            )

            valid, message = validate_skill(skill_dir)

            self.assertTrue(valid, message)

    def test_curated_description_cli_counts_decoded_yaml_characters(self):
        validator = Path(__file__).with_name("quick_validate.py")
        for size, exit_code, diagnostic in (
            (600, 0, None),
            (601, 0, "600 or fewer is recommended"),
            (1023, 0, "600 or fewer is recommended"),
            (1024, 1, "maximum is 1023"),
        ):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as tmpdir:
                # The literal block keeps an internal newline but strips the final one.
                value = "\u52d5" * 300 + "\n  " + "\u753b" * (size - 301)
                skill_dir = self.write_skill(
                    Path(tmpdir),
                    "description-boundary",
                    f"name: description-boundary\ndescription: |-\n  {value}\nlicense: MIT",
                )
                result = subprocess.run(
                    [sys.executable, "-B", str(validator), "--curated-description", str(skill_dir)],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=False,
                )
                self.assertEqual(result.returncode, exit_code, result.stdout + result.stderr)
                if diagnostic:
                    self.assertIn(f"description-boundary: 'description' is {size} characters", result.stdout)
                    self.assertIn(diagnostic, result.stdout)
                else:
                    self.assertNotIn("'description' is", result.stdout)

    def test_standard_description_limit_is_unchanged(self):
        for size in (1024, 1025):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as tmpdir:
                skill_dir = self.write_skill(
                    Path(tmpdir),
                    "standard-limit",
                    f"name: standard-limit\ndescription: {'a' * size}\nlicense: MIT",
                )
                valid, message = validate_skill(skill_dir)
                self.assertEqual(valid, size == 1024, message)
                if not valid:
                    self.assertIn("'description' is 1025 characters; maximum is 1024", message)

    def test_rejects_non_string_compatibility(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self.write_skill(
                Path(tmpdir),
                "bad-compatibility",
                "\n".join([
                    "name: bad-compatibility",
                    'description: "Test compatibility validation. Use when reviewing Skill frontmatter."',
                    "compatibility:",
                    "  - VS Code",
                    "license: CC BY-NC-SA 4.0",
                    "metadata:",
                    "  author: Example Author",
                ]),
            )

            valid, message = validate_skill(skill_dir)

            self.assertFalse(valid)
            self.assertIn("compatibility", message)

    def test_rejects_name_that_does_not_match_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self.write_skill(
                Path(tmpdir),
                "expected-name",
                "\n".join([
                    "name: different-name",
                    'description: "Compare sessions. Use when analyzing logs."',
                    "license: CC BY-NC-SA 4.0",
                    "metadata:",
                    "  author: Example Author",
                ]),
            )

            valid, message = validate_skill(skill_dir)

            self.assertFalse(valid)
            self.assertIn("parent directory", message)

    def test_requires_license_file_and_author(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "missing-metadata"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: missing-metadata\n"
                'description: "Compare sessions. Use when analyzing logs."\n'
                "license: CC BY-NC-SA 4.0\n"
                "metadata: {}\n"
                "---\n",
                encoding="utf-8",
            )

            valid, message = validate_skill(skill_dir)

            self.assertFalse(valid)
            self.assertIn("License evidence", message)

    def test_rejects_non_boolean_invocation_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self.write_skill(
                Path(tmpdir),
                "bad-boolean",
                "\n".join([
                    "name: bad-boolean",
                    'description: "Compare sessions. Use when analyzing logs."',
                    'user-invocable: "yes"',
                    "license: CC BY-NC-SA 4.0",
                    "metadata:",
                    "  author: Example Author",
                ]),
            )

            valid, message = validate_skill(skill_dir)

            self.assertFalse(valid)
            self.assertIn("boolean", message)

    def test_allows_third_party_skill_without_author_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self.write_skill(
                Path(tmpdir),
                "third-party-skill",
                "\n".join([
                    "name: third-party-skill",
                    'description: "Third-party skill. Use when testing imported skills."',
                    "license: Proprietary. LICENSE.txt has complete terms",
                ]),
            )

            valid, message = validate_skill(skill_dir)

            self.assertTrue(valid, message)

    def test_rejects_self_authored_license_tampering_even_when_hash_is_updated(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = init_skill("sample-skill", tmpdir, "mit", "Example Author")
            license_path = skill_dir / "LICENSE.txt"
            license_path.write_text("unrelated license text\n", encoding="utf-8")
            manifest_path = skill_dir / "skill-license.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            import hashlib
            manifest["evidence"][0]["sha256"] = hashlib.sha256(license_path.read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            valid, message = validate_skill(skill_dir)

            self.assertFalse(valid)
            self.assertIn("license evidence does not match", message)

    def test_rejects_missing_profile_template_hash(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = init_skill("sample-skill", tmpdir, "mit", "Example Author")
            manifest_path = skill_dir / "skill-license.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            del manifest["profile"]["templateSha256"]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            valid, message = validate_skill(skill_dir)

            self.assertFalse(valid)
            self.assertIn("profile snapshot", message)

    def test_rejects_self_authored_custom_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = init_skill("sample-skill", tmpdir, "mit", "Example Author")
            manifest_path = skill_dir / "skill-license.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["profile"]["id"] = "custom"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            valid, message = validate_skill(skill_dir)

            self.assertFalse(valid)
            self.assertIn("registered target license profile", message)


if __name__ == "__main__":
    unittest.main()