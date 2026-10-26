"""Offline regression: python scripts\\test_report_skill_deployment.py."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import unittest
import uuid

import yaml


ROOT = Path(__file__).resolve().parents[1]
BASELINE = json.loads((ROOT / "scripts" / "report-contract-baseline.json").read_text(encoding="utf-8"))
NAMES = tuple(BASELINE["reports"])
PWSH = shutil.which("pwsh")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def frontmatter(path: Path) -> tuple[dict, str]:
    match = re.fullmatch(r"---\n(.*?)\n---\n(.*)", read(path), re.S)
    if not match:
        raise AssertionError(f"Missing YAML frontmatter: {path}")
    return yaml.safe_load(match[1]), match[2]


class ReportSkillDeploymentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not PWSH:
            raise RuntimeError("PowerShell 7 (pwsh) is required")
        # Own every scratch path and keep it inside this skill, never the OS temp directory.
        cls.scratch = ROOT / "scripts" / f".report-skill-test-{uuid.uuid4().hex}"
        cls.scratch.mkdir()
        cls.addClassCleanup(shutil.rmtree, cls.scratch)
        cls.workspace = cls.scratch / "workspace with spaces 日本語"
        cls.init_output = cls.run_script(
            "Initialize-BizOpsWorkspace.ps1", cls.workspace, "-Customers", "contoso"
        ).stdout
        cls.deploy_output = cls.run_script("Deploy-BizOpsTemplates.ps1", cls.workspace).stdout

    @classmethod
    def run_script(cls, name, workspace, *arguments, success=True):
        result = subprocess.run(
            [PWSH, "-NoLogo", "-NoProfile", "-NonInteractive", "-File",
             str(ROOT / "scripts" / name), "-WorkspacePath", str(workspace), *map(str, arguments)],
            cwd=ROOT, capture_output=True, encoding="utf-8", errors="strict", timeout=45,
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"},
        )
        if (result.returncode == 0) != success:
            raise AssertionError(f"{name}: exit={result.returncode}\n{result.stdout}\n{result.stderr}")
        return result

    def test_01_original_bodies_bindings_and_license(self):
        parent, _ = frontmatter(ROOT / "SKILL.md")
        self.assertEqual(parent["license"], BASELINE["license"])
        self.assertEqual(parent["metadata"]["author"], BASELINE["author"])
        license_bytes = (ROOT / "LICENSE.txt").read_bytes()
        self.assertEqual(digest(read(ROOT / "LICENSE.txt")), BASELINE["license_sha256"])
        for name, original in BASELINE["reports"].items():
            with self.subTest(report=name):
                package = ROOT / "assets" / "workspace-skills" / name
                meta, wrapper = frontmatter(package / "SKILL.md")
                body = read(package / "references" / "report-contract.md")
                self.assertEqual(len(body), original["body_chars"])
                self.assertEqual(digest(body), original["body_sha256"])
                # During migration compare the still-present originals too; pinned hashes survive removal.
                old = ROOT / "assets" / "prompts" / f"{name}.prompt.template.md"
                if old.exists():
                    old_meta, old_body = frontmatter(old)
                    self.assertEqual(old_body, body)
                    self.assertEqual(old_meta["agent"], original["agent"])
                self.assertEqual(meta["name"], name)
                self.assertIn(original["description"], meta["description"])
                self.assertIs(meta["disable-model-invocation"], True)
                self.assertIs(meta["user-invocable"], True)
                self.assertIsInstance(meta["argument-hint"], str)
                self.assertGreater(len(meta["argument-hint"]), 15)
                self.assertNotIn("agent", meta)
                self.assertEqual(meta["license"], parent["license"])
                self.assertEqual(meta["metadata"]["author"], parent["metadata"]["author"])
                self.assertEqual((package / "LICENSE.txt").read_bytes(), license_bytes)
                self.assertIn(f'agentName: "{original["agent"]}"', wrapper)
                self.assertIn(f'.github/agents/{original["agent"]}.agent.md', wrapper)
                for invariant in (
                    "complete contract content", "all user arguments verbatim",
                    "report an explicit error and stop", "Never run the report inline",
                    "substitute a general-purpose agent", "widen tools",
                ):
                    self.assertIn(invariant, wrapper)

    def test_02_real_init_deploy_and_resolving_references(self):
        workspace = self.workspace
        self.assertFalse(list((ROOT / "assets").rglob("*.prompt.template.md")))
        self.assertTrue((workspace / "Customers" / "contoso" / "profile.md").is_file())
        self.assertTrue((workspace / "Tasks" / "active.md").is_file())
        self.assertFalse((workspace / ".github" / "prompts").exists())
        self.assertFalse(list(workspace.rglob("*.prompt.md")))
        self.assertIn("Report skills: 4", self.deploy_output)
        self.assertIn("Agents: 9", self.deploy_output)
        self.assertNotIn("Copy prompt", self.init_output)
        deployed = workspace / ".github" / "skills"
        self.assertEqual({path.parent.name for path in deployed.glob("*/SKILL.md")}, set(NAMES))
        index = read(deployed / "README.md")
        self.assertIn("Four manual-only", index)
        self.assertIn("stop explicitly", index)
        for name, original in BASELINE["reports"].items():
            with self.subTest(report=name):
                for relative in ("SKILL.md", "references/report-contract.md", "LICENSE.txt"):
                    self.assertEqual(
                        (deployed / name / relative).read_bytes(),
                        (ROOT / "assets" / "workspace-skills" / name / relative).read_bytes(),
                    )
                self.assertIn(f"/{name}", index)
                self.assertTrue((deployed / name / "references" / "report-contract.md").is_file())
                agent_file = workspace / ".github" / "agents" / f'{original["agent"]}.agent.md'
                agent, _ = frontmatter(agent_file)
                self.assertEqual(agent["name"], original["agent"])
        generator = read(workspace / ".github" / "agents" / "report-generator.agent.md")
        for reference in re.findall(r"`(\.github/skills/[^`]+/references/report-contract\.md)`", generator):
            self.assertTrue((workspace / reference).is_file(), reference)
        self.assertEqual(len(re.findall(r"\.github/skills/[^`]+/references/report-contract\.md", generator)), 3)
        self.assertTrue((workspace / "_datasources" / "scripts" / "daily-ops" / "collect_daily_activity.py").is_file())

    def test_03_role_tool_approval_and_output_invariants(self):
        generator_path = ROOT / "assets" / "agents" / "report-generator.agent.template.md"
        meta, _ = frontmatter(generator_path)
        self.assertEqual(meta["tools"], ["read", "edit", "search", "agent"])
        generator = read(generator_path)
        outside_reference = re.sub(
            r"## MANDATORY: (?:Prompt Reference|Report Contract Reference)\n.*?(?=\n---\n)",
            "", generator, flags=re.S,
        )
        self.assertEqual(digest(outside_reference), BASELINE["generator_outside_contract_sha256"])
        self.assertIn("APPROVED or 3 iterations completed", generator)
        self.assertIn('agentName: "report-reviewer"', generator)
        self.assertIn("Maximum 3 iterations", generator)
        self.assertIn("before date checks", generator.lower())
        self.assertIn("take precedence", generator)
        self.assertNotIn(".github/prompts/", generator)
        for relative, expected in BASELINE["unchanged_assets"].items():
            self.assertEqual(digest(read(ROOT / relative)), expected, relative)
        reviewer_meta, reviewer = frontmatter(ROOT / "assets" / "agents" / "report-reviewer.agent.template.md")
        self.assertEqual(reviewer_meta["tools"], ["read", "search"])
        self.assertIn("Direct editing of report files", reviewer)
        self.assertIn("New data collection", reviewer)
        review_wrapper = read(ROOT / "assets" / "workspace-skills" / "review-report" / "SKILL.md")
        self.assertIn("no report editing and no new data collection", review_wrapper)
        self.assertIn("verdict only", review_wrapper)
        expected_paths = {
            "daily-report": "ActivityReport/{YYYY-MM}/daily/{YYYY-MM-DD}.md",
            "weekly-report": "ActivityReport/{YYYY-MM}/weekly/{YYYY}-W{WW}.md",
            "monthly-report": "ActivityReport/{YYYY-MM}/{YYYY-MM}.md",
        }
        for name, expected in expected_paths.items():
            body = read(ROOT / "assets" / "workspace-skills" / name / "references" / "report-contract.md")
            self.assertIn(expected, body)
            self.assertIn(expected, generator)
        review_contract = read(ROOT / "assets" / "workspace-skills" / "review-report" / "references" / "report-contract.md")
        for invariant in ("IMPACT", "overall_score >= 75", "overall_score < 75", "max 3 iterations", "STAR"):
            self.assertIn(invariant, review_contract)

    def test_04_daily_preflight_pto_holiday_and_unverified_zero(self):
        contract = read(ROOT / "assets" / "workspace-skills" / "daily-report" / "references" / "report-contract.md")
        for invariant in (
            "_datasources/scripts/daily-ops/collect_daily_activity.py --date {target date}",
            "_reports/{YYYY-MM}/daily-ops/{YYYY-MM-DD}.json",
            "`targetDate` differs", "`summary.rootCount` is zero", "`status` is `error`",
            "Continue on `partial` only", "unverified, not zero activity",
            "`complete` plus a zero count", "skip only when verified activity is zero",
            "{YYYY-MM-DD}_dayoff.md", "_workiq/{country}-holidays.md",
            "Tentative also counts as PTO", "PTO + Actual = 8h",
            "[Estimated]", "Estimation Prohibited Tasks",
        ):
            self.assertIn(invariant, contract)
        self.assertIn("unavailable", read(ROOT / "assets" / "scripts" / "collect_daily_activity.py"))

    def test_05_redeploy_preserves_customized_destinations(self):
        workspace = self.scratch / "customized workspace"
        self.run_script("Initialize-BizOpsWorkspace.ps1", workspace)
        self.run_script("Deploy-BizOpsTemplates.ps1", workspace)
        customized = [
            workspace / ".github" / "skills" / name / relative
            for name in NAMES
            for relative in ("SKILL.md", "references/report-contract.md", "LICENSE.txt")
        ] + [
            workspace / ".github" / "skills" / "README.md",
            workspace / ".github" / "agents" / "report-generator.agent.md",
            workspace / ".github" / "agents" / "report-reviewer.agent.md",
            workspace / "_datasources" / "daily-activity-sources.json",
        ]
        legacy = workspace / ".github" / "prompts" / "daily-report.prompt.md"
        legacy.parent.mkdir()
        legacy.write_text("user-owned legacy content\n", encoding="utf-8")
        customized.append(legacy)
        for path in customized[:-1]:
            with path.open("ab") as stream:
                stream.write(b"\nuser-owned customization\n")
        before = {path: path.read_bytes() for path in customized}
        self.run_script("Initialize-BizOpsWorkspace.ps1", workspace)
        self.run_script("Deploy-BizOpsTemplates.ps1", workspace)
        self.assertEqual(before, {path: path.read_bytes() for path in customized})
        self.assertEqual(list(legacy.parent.iterdir()), [legacy])

    def test_06_missing_required_resources_fail_before_writes(self):
        fixture = self.scratch / "source fixture"
        shutil.copytree(ROOT / "assets", fixture / "assets")
        required = [
            Path("workspace-skills") / name / relative
            for name in NAMES
            for relative in ("SKILL.md", "references/report-contract.md", "LICENSE.txt")
        ] + [
            Path("agents/report-generator.agent.template.md"),
            Path("agents/report-reviewer.agent.template.md"),
            Path("_datasources/daily-activity-sources.template.json"),
            Path("scripts/collect_daily_activity.py"),
        ]
        for number, relative in enumerate(required):
            with self.subTest(resource=str(relative)):
                source = fixture / "assets" / relative
                content = source.read_bytes()
                source.unlink()
                workspace = self.scratch / f"missing-{number}"
                result = self.run_script(
                    "Deploy-BizOpsTemplates.ps1", workspace, "-SkillPath", fixture, success=False
                )
                self.assertIn("required report resource", result.stderr)
                self.assertFalse(workspace.exists())
                source.write_bytes(content)
        empty = fixture / "assets" / "workspace-skills" / "review-report" / "LICENSE.txt"
        empty.write_bytes(b"")
        workspace = self.scratch / "empty-resource"
        self.run_script("Deploy-BizOpsTemplates.ps1", workspace, "-SkillPath", fixture, success=False)
        self.assertFalse(workspace.exists())

    def test_07_deployed_collector_zero_partial_and_required_failure(self):
        workspace = self.scratch / "offline collector"
        self.run_script("Deploy-BizOpsTemplates.ps1", workspace)
        empty_root = workspace / "empty evidence root"
        empty_root.mkdir()
        config_path = workspace / "_datasources" / "daily-activity-sources.json"
        collector = workspace / "_datasources" / "scripts" / "daily-ops" / "collect_daily_activity.py"
        # A fixed UTC TZif fixture keeps Windows tests independent of the optional tzdata package.
        timezone_path = workspace / "timezone fixture"
        timezone_path.mkdir()
        (timezone_path / "UTC").write_bytes(
            b"TZif\0" + b"\0" * 15 + struct.pack(">6l", 0, 0, 0, 0, 1, 4)
            + struct.pack(">lbb", 0, 0, 0) + b"UTC\0"
        )
        roots = [{"id": "local", "path": str(empty_root), "kinds": ["files"], "required": True}]
        for state in ("complete", "partial", "error"):
            with self.subTest(status=state):
                if state == "partial":
                    roots.append({
                        "id": "missing", "path": str(workspace / "missing optional root"),
                        "kinds": ["files"], "required": False,
                    })
                elif state == "error":
                    roots[1]["required"] = True
                config_path.write_text(json.dumps({
                    "schemaVersion": 1, "timeZone": "UTC", "roots": roots,
                }), encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, "-B", str(collector), "--date", "2000-01-01"],
                    cwd=workspace, capture_output=True, encoding="utf-8", timeout=30,
                    env={**os.environ, "PYTHONTZPATH": str(timezone_path), "PYTHONUTF8": "1"},
                )
                self.assertEqual(result.returncode, 1 if state == "error" else 0, result.stderr)
                payload = json.loads(read(workspace / "_reports" / "2000-01" / "daily-ops" / "2000-01-01.json"))
                self.assertEqual(payload["targetDate"], "2000-01-01")
                self.assertEqual(payload["status"], state)
                self.assertEqual(payload["summary"]["fileCount"], 0)
                self.assertEqual(payload["summary"]["commitCount"], 0)
                self.assertEqual(payload["summary"]["rootCount"], len(roots))
                if state != "complete":
                    self.assertNotEqual(payload["roots"][1]["status"], "complete")
                if state == "partial":
                    self.assertEqual(payload["roots"][1]["status"], "unavailable")


if __name__ == "__main__":
    unittest.main(verbosity=2)
