import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from package_skill import package_skill, validate_archive


class PackageSkillTests(unittest.TestCase):
    def test_excludes_python_cache_and_bytecode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill = root / "sample-skill"
            scripts = skill / "scripts"
            cache = scripts / "__pycache__"
            cache.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: sample-skill\n"
                'description: "Sample skill. Use when testing package contents."\n'
                "license: CC BY-NC-SA 4.0\n"
                "metadata:\n"
                "  author: Example Author\n"
                "---\n",
                encoding="utf-8",
            )
            (skill / "LICENSE.txt").write_text("license\n", encoding="utf-8")
            (scripts / "helper.py").write_text("print('ok')\n", encoding="utf-8")
            (cache / "helper.cpython-313.pyc").write_bytes(b"bytecode")
            output = root / "dist"

            archive = package_skill(skill, output)

            self.assertIsNotNone(archive)
            with zipfile.ZipFile(archive) as packaged:
                names = packaged.namelist()
            self.assertIn("sample-skill/scripts/helper.py", names)
            self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in names))

    def test_rejects_windows_unsafe_archive_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            archive = Path(tmpdir) / "unsafe.skill"
            with zipfile.ZipFile(archive, "w") as packaged:
                packaged.writestr("sample-skill/CON.txt", "unsafe")

            valid, message = validate_archive(archive, "sample-skill")

            self.assertFalse(valid)
            self.assertIn("reserved Windows device", message)

    def test_rejects_archive_without_skill_md(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            archive = Path(tmpdir) / "incomplete.skill"
            with zipfile.ZipFile(archive, "w") as packaged:
                packaged.writestr("sample-skill/LICENSE.txt", "license")

            valid, message = validate_archive(archive, "sample-skill")

            self.assertFalse(valid)
            self.assertIn("missing required", message)

    def test_failed_package_keeps_existing_archive(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill = root / "sample-skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: sample-skill\ndescription: \"Sample skill. Use when testing package contents.\"\nlicense: MIT\nmetadata:\n  author: Example Author\n---\n",
                encoding="utf-8",
            )
            (skill / "LICENSE.txt").write_text("license\n", encoding="utf-8")
            output = root / "dist"
            output.mkdir()
            existing = output / "sample-skill.skill"
            existing.write_bytes(b"known-good-archive")

            with patch("package_skill.validate_skill", return_value=(True, "ok")), patch(
                "package_skill.validate_archive", return_value=(False, "forced failure")
            ):
                archive = package_skill(skill, output)

            self.assertIsNone(archive)
            self.assertEqual(existing.read_bytes(), b"known-good-archive")

    @unittest.skipUnless(hasattr(Path, "symlink_to"), "symlink support is unavailable")
    def test_rejects_symlink_output_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            destination = root / "destination"
            destination.mkdir()
            alias = root / "alias"
            try:
                alias.symlink_to(destination, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"symlink creation is unavailable: {error}")

            archive = package_skill(root / "missing-skill", alias)

            self.assertIsNone(archive)
            self.assertFalse((destination / "missing-skill.skill").exists())


if __name__ == "__main__":
    unittest.main()