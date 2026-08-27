from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCES = SKILL_ROOT / "references"


class SkillStructureTests(unittest.TestCase):
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
        }
        limits = {
            "primary": 59_000,
            "challenger": 20_000,
            "reporter": 28_000,
            "coordinator": 55_000,
        }
        for role, total in totals.items():
            with self.subTest(role=role):
                self.assertLessEqual(total, limits[role])

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
