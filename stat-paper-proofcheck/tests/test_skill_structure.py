from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCES = SKILL_ROOT / "references"
REPOSITORY_ROOT = SKILL_ROOT.parent


class SkillStructureTests(unittest.TestCase):
    def test_release_version_surfaces_agree(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        script = (SKILL_ROOT / "scripts" / "proofcheck.py").read_text(
            encoding="utf-8"
        )
        examples = json.loads(
            (SKILL_ROOT / "assets" / "templates" / "AUDIT_RECORD_EXAMPLES.json")
            .read_text(encoding="utf-8")
        )
        report = (
            SKILL_ROOT / "assets" / "templates" / "FINAL_REPORT.md"
        ).read_text(encoding="utf-8")
        readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")

        skill_match = re.search(
            r'(?m)^\s+version:\s+"([^"]+)"\s*$', skill
        )
        script_match = re.search(
            r'(?m)^SKILL_VERSION\s*=\s*"([^"]+)"\s*$', script
        )
        report_match = re.search(
            r"(?m)^- Skill version:\s+([^\s]+)\s*$", report
        )
        readme_match = re.search(
            r"(?m)^\| `stat-paper-proofcheck` \| v([^ |]+) \|", readme
        )
        self.assertIsNotNone(skill_match)
        self.assertIsNotNone(script_match)
        self.assertIsNotNone(report_match)
        self.assertIsNotNone(readme_match)

        versions = {
            "SKILL.md": skill_match.group(1),
            "proofcheck.py": script_match.group(1),
            "record examples": examples["skill_version"],
            "manifest example": examples[
                "manifest_report_deliverables_example"
            ]["protocol"]["skill_version"],
            "final report template": report_match.group(1),
            "README.md": readme_match.group(1),
        }
        self.assertEqual({"1.2"}, set(versions.values()), versions)

    def test_canonical_role_references_are_directly_discoverable(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        required = {
            "workspace-and-resume.md",
            "proof-system-audit.md",
            "line-by-line-protocol.md",
            "evidence-and-verdicts.md",
            "issues-and-repairs.md",
            "challenge-protocol.md",
            "reporting-and-release.md",
        }
        for name in required:
            with self.subTest(name=name):
                self.assertIn(f"(references/{name})", skill)

    def test_legacy_references_are_small_non_normative_routes(self) -> None:
        for name in (
            "evidence-status-and-issues.md",
            "state-and-reporting.md",
        ):
            with self.subTest(name=name):
                path = REFERENCES / name
                text = path.read_text(encoding="utf-8")
                self.assertLess(path.stat().st_size, 1_000)
                self.assertIn("contains no normative audit rules", text)

    def test_role_context_budgets_prevent_accidental_reexpansion(self) -> None:
        sizes = {
            path.name: path.stat().st_size
            for path in [SKILL_ROOT / "SKILL.md", *REFERENCES.glob("*.md")]
        }
        skill = sizes["SKILL.md"]
        totals = {
            "primary": (
                skill
                + sizes["line-by-line-protocol.md"]
                + sizes["evidence-and-verdicts.md"]
            ),
            "challenger": skill + sizes["challenge-protocol.md"],
            "reporter": skill + sizes["reporting-and-release.md"],
            "coordinator": (
                skill
                + sizes["workspace-and-resume.md"]
                + sizes["proof-system-audit.md"]
            ),
            "calibration": skill + sizes["checker-calibration.md"],
        }
        limits = {
            "primary": 65_500,
            "challenger": 22_500,
            "reporter": 30_000,
            "coordinator": 59_000,
            "calibration": 20_500,
        }
        for role, total in totals.items():
            with self.subTest(role=role):
                self.assertLessEqual(total, limits[role])

    def test_proofcheck_is_gated_to_explicit_invocation(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = skill.split("---")[1]
        # The Agent Skills spec validator (skills-ref) rejects any top-level
        # frontmatter field outside this whitelist, including runtime-specific
        # gates such as disable-model-invocation. The invocation gate
        # therefore lives in the description (portable), openai.yaml (Codex),
        # and the documented skillOverrides setting (Claude Code / Cowork).
        allowed = {
            "name",
            "description",
            "license",
            "allowed-tools",
            "metadata",
            "compatibility",
        }
        top_level_keys = {
            match.group(1)
            for match in re.finditer(r"(?m)^([A-Za-z][\w-]*):", frontmatter)
        }
        self.assertTrue(
            top_level_keys <= allowed, top_level_keys - allowed
        )
        agent_metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "policy:\n  allow_implicit_invocation: false", agent_metadata
        )
        self.assertRegex(
            frontmatter,
            r"description:.*explicitly invokes /stat-paper-proofcheck",
        )
        body = skill.split("---", 2)[2]
        self.assertIn("## Explicit invocation only", body)
        self.assertIn(
            '{"skillOverrides": {"stat-paper-proofcheck": '
            '"user-invocable-only"}}',
            body,
        )

    def test_challenge_semantics_have_one_instruction_owner(self) -> None:
        challenge = (REFERENCES / "challenge-protocol.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("The effective-critical set is the union of", challenge)
        self.assertIn("covered_issue_ids", challenge)

        linked_only = (
            "evidence-and-verdicts.md",
            "issues-and-repairs.md",
            "proof-system-audit.md",
            "workspace-and-resume.md",
        )
        for name in linked_only:
            with self.subTest(name=name):
                text = (REFERENCES / name).read_text(encoding="utf-8")
                self.assertIn("challenge-protocol.md", text)
                self.assertNotIn("covered_issue_ids", text)

    def test_sampling_and_evidence_wording_stays_contract_current(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        protocol = (REFERENCES / "line-by-line-protocol.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("sample drawn from all in-scope units", skill)
        self.assertNotIn("sample of the remaining units", skill)
        self.assertIn("The current evidence\ncontract treats", protocol)
        self.assertNotRegex(protocol, r"Evidence contract \d+ treats")

    def test_canonical_references_do_not_route_through_legacy_files(self) -> None:
        protocol = (REFERENCES / "line-by-line-protocol.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("evidence-status-and-issues.md", protocol)
        reporting = (REFERENCES / "reporting-and-release.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("report_deliverables", reporting)
        self.assertIn("NONFINAL SCAFFOLD", reporting)

    def test_method_interface_scope_contract_is_discoverable(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("targeting materially different population quantities", skill)
        self.assertIn("only assuming an oracle object", skill)
        self.assertIn("method-to-implementation verification", skill)
        self.assertIn("`scope.trigger` as `required` or `not_required`", skill)
        self.assertIn("domain-risk-checks.md", skill)
        self.assertIn("evidence-and-verdicts.md", skill)


if __name__ == "__main__":
    unittest.main()
