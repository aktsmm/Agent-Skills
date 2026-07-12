import json
import tempfile
import unittest
from pathlib import Path

from init_skill import init_skill
from quick_validate import validate_skill


class InitSkillTests(unittest.TestCase):
    def test_creates_minimal_manifest_skill_without_python_assets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill = init_skill(
                "sample-skill",
                tmpdir,
                "cc-by-nc-sa-4.0",
                "Example Author",
            )

            self.assertIsNotNone(skill)
            self.assertEqual(
                {item.name for item in skill.iterdir()},
                {"SKILL.md", "LICENSE.txt", "skill-license.json"},
            )
            manifest = json.loads((skill / "skill-license.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["spdxId"], "CC-BY-NC-SA-4.0")
            self.assertEqual(manifest["authorAttribution"]["value"], "Example Author")
            valid, message = validate_skill(skill)
            self.assertTrue(valid, message)

    def test_python_starter_is_explicit_opt_in(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill = init_skill(
                "python-skill",
                tmpdir,
                "mit",
                "Example Author",
                with_python_helper=True,
            )

            self.assertTrue((skill / "scripts" / "helper.py").is_file())
            self.assertTrue((skill / "scripts" / "requirements.txt").is_file())
            self.assertTrue((skill / "scripts" / "test_helper.py").is_file())

    def test_invalid_request_does_not_leave_target_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill = init_skill("sample-skill", tmpdir, "unknown-profile", "Example Author")

            self.assertIsNone(skill)
            self.assertFalse((Path(tmpdir) / "sample-skill").exists())

    @unittest.skipUnless(hasattr(Path, "symlink_to"), "symlink support is unavailable")
    def test_rejects_symlink_output_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            destination = root / "destination"
            destination.mkdir()
            alias = root / "alias"
            try:
                alias.symlink_to(destination, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"symlink creation is unavailable: {error}")

            skill = init_skill("sample-skill", alias, "mit", "Example Author")

            self.assertIsNone(skill)
            self.assertFalse((destination / "sample-skill").exists())


if __name__ == "__main__":
    unittest.main()