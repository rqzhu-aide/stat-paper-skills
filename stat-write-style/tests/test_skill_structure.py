from __future__ import annotations

import ast
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
REPO_ROOT = ROOT.parent
SKILL = ROOT / "SKILL.md"
REFERENCES = ROOT / "references"


def markdown_files() -> list[Path]:
    return [SKILL, *sorted(REFERENCES.glob("*.md"))]


def markdown_links(path: Path) -> list[Path]:
    text = path.read_text(encoding="utf-8")
    targets: list[Path] = []
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        raw = match.group(1).split("#", 1)[0]
        if not raw or "://" in raw or not raw.endswith(".md"):
            continue
        targets.append((path.parent / raw).resolve())
    return targets


class SkillStructureTests(unittest.TestCase):
    def test_all_markdown_links_resolve(self) -> None:
        missing = [
            (path.relative_to(ROOT), target)
            for path in markdown_files()
            for target in markdown_links(path)
            if not target.is_file()
        ]
        self.assertEqual(missing, [])

    def test_all_references_are_reachable(self) -> None:
        seen: set[Path] = set()
        pending = [SKILL.resolve()]
        while pending:
            current = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            pending.extend(target for target in markdown_links(current) if target not in seen)
        expected = {path.resolve() for path in REFERENCES.glob("*.md")}
        self.assertEqual(expected - seen, set())

    def test_entrypoint_and_route_byte_budgets(self) -> None:
        sizes = {path.name: path.stat().st_size for path in markdown_files()}
        self.assertLessEqual(sizes["SKILL.md"], 8_000)
        # Byte proxies for representative route unions, not runtime tokens.
        # Behavioral routing and editorial authority are tested with manuscript
        # tasks; do not lock their instruction phrasing into this test suite.
        routes = {
            "light_polish": ["SKILL.md", "polishing-protocol.md"],
            "substantive_register": [
                "SKILL.md",
                "polishing-protocol.md",
                "wording-register.md",
            ],
            "local_register": ["SKILL.md", "wording-register.md"],
            "structural_method_revision": [
                "SKILL.md",
                "polishing-protocol.md",
                "method-description.md",
            ],
            "paper_restructuring": [
                "SKILL.md",
                "manuscript-workflow.md",
                "polishing-protocol.md",
                "argument-architecture.md",
            ],
            "paper_planning": [
                "SKILL.md", "manuscript-workflow.md", "argument-architecture.md"
            ],
            "paper_method_draft": [
                "SKILL.md",
                "manuscript-workflow.md",
                "polishing-protocol.md",
                "wording-register.md",
                "method-description.md",
            ],
            "method_draft": [
                "SKILL.md",
                "polishing-protocol.md",
                "method-description.md",
            ],
            "high_risk_method_draft": [
                "SKILL.md",
                "polishing-protocol.md",
                "support-and-author-decisions.md",
                "method-description.md",
            ],
            "proof_polish": [
                "SKILL.md",
                "polishing-protocol.md",
                "theoretical-proofs.md",
            ],
            "quick_audit_startup": [
                "SKILL.md",
                "quick-section-audit.md",
            ],
            "quick_audit_reporting": [
                "SKILL.md",
                "quick-section-audit.md",
                "reporting-and-validation.md",
            ],
            "abstract_positioning": [
                "SKILL.md",
                "introduction.md",
                "argument-architecture.md",
            ],
            "full_audit_startup": [
                "SKILL.md",
                "revision-audit.md",
            ],
            "full_audit_diagnostic": [
                "SKILL.md",
                "revision-audit.md",
                "quick-section-audit.md",
            ],
            "ordinary_audit_reporting": [
                "SKILL.md",
                "revision-audit.md",
                "quick-section-audit.md",
                "argument-architecture.md",
                "reporting-and-validation.md",
            ],
            "tracked_audit_authoring": [
                "SKILL.md",
                "revision-audit.md",
                "quick-section-audit.md",
                "argument-architecture.md",
                "reporting-and-validation.md",
                "full-audit-operations.md",
                "full-audit-data-contract.md",
            ],
        }
        limits = {
            "light_polish": 18_000,
            "substantive_register": 26_000,
            "local_register": 24_000,
            "structural_method_revision": 28_000,
            # Complete-paper work now includes planning and reconciliation;
            # bounded edits retain their existing limits. These bundles model
            # one active section, not every section guide at once.
            "paper_restructuring": 29_000,
            "paper_planning": 20_000,
            "paper_method_draft": 32_000,
            # Conservative whole-file bounds: drafting only needs the linked
            # prose core, not the rest of the polishing protocol.
            "method_draft": 19_000,
            "high_risk_method_draft": 26_000,
            "proof_polish": 28_000,
            "quick_audit_startup": 18_000,
            "quick_audit_reporting": 23_000,
            "abstract_positioning": 23_000,
            "full_audit_startup": 22_000,
            "full_audit_diagnostic": 30_000,
            "ordinary_audit_reporting": 40_000,
            "tracked_audit_authoring": 62_000,
        }
        totals = {
            route: sum(sizes[name] for name in names)
            for route, names in routes.items()
        }
        self.assertEqual(
            {route: total for route, total in totals.items() if total > limits[route]},
            {},
        )

    def test_serialized_ledger_columns_match_runtime(self) -> None:
        module = ast.parse((ROOT / "scripts" / "writer_audit.py").read_text(encoding="utf-8"))
        headers = next(
            ast.literal_eval(node.value)
            for node in module.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "EXPECTED_LEDGER_HEADERS"
                for target in node.targets
            )
        )
        contract = (REFERENCES / "full-audit-data-contract.md").read_text(encoding="utf-8")
        tables = [
            [cell.strip() for cell in line.strip().strip("|").split("|")]
            for line in contract.splitlines()
            if line.startswith("|")
        ]
        self.assertIn(headers, tables)
        # The example must remain usable as a record with these exact keys.
        blocks = re.findall(r"(?m)(?:^ {4}.*(?:\n|$))+", contract)
        rows = [
            json.loads(block)
            for block in blocks
            if '"identity_anchors"' in block and '"cells"' in block
        ]
        self.assertEqual(len(rows), 1)
        self.assertEqual(list(rows[0]["cells"]), headers)

    def test_portable_commands_and_discovery_metadata(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        operations = (REFERENCES / "full-audit-operations.md").read_text(
            encoding="utf-8"
        )
        combined = skill + operations
        self.assertNotIn("python scripts/writer_audit.py", combined)
        self.assertNotIn('python "SKILL_DIR/', skill)
        self.assertIn('python "SKILL_DIR/scripts/writer_audit.py" init', operations)
        self.assertIn(
            'python "AUDIT_DIR/protocol/scripts/writer_audit.py" status', operations
        )
        self.assertIn(
            'python "AUDIT_DIR/protocol/scripts/writer_audit.py" freeze', operations
        )
        self.assertIn(
            'python "AUDIT_DIR/protocol/scripts/writer_audit.py" check', operations
        )
        description = skill.split("---", 2)[1]
        for term in {
            "presentation-audit",
            "supplied citations",
            "cross-references",
            "does not validate proofs",
        }:
            self.assertIn(term, description)
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        skill_version = re.search(r'(?m)^  version: "([^"]+)"$', description)
        readme_version = re.search(
            r"(?m)^\| `stat-write-style` \| v([^ |]+) \|",
            readme,
        )
        self.assertIsNotNone(skill_version)
        self.assertIsNotNone(readme_version)
        assert skill_version is not None and readme_version is not None
        self.assertRegex(skill_version.group(1), r"^\d+\.\d+(?:\.\d+)?$")
        self.assertEqual(readme_version.group(1), skill_version.group(1))

    def test_runtime_metadata_covers_writer_harness(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        required = {
            "proofcheck and writing helpers and tests require Python 3.10",
            "pypdf",
            "PyPDF2",
            '--pdf-page-count "SOURCE=N"',
            "python -m unittest discover -s stat-write-style/tests",
        }
        self.assertEqual([item for item in required if item not in readme], [])

    def test_no_platform_paths_or_forbidden_dashes(self) -> None:
        violations: list[tuple[str, str]] = []
        text_paths = [
            *markdown_files(),
            *sorted((ROOT / "scripts").glob("*.py")),
            *sorted((ROOT / "tests").glob("*.py")),
            *sorted((ROOT / "assets").rglob("*.json")),
        ]
        for path in text_paths:
            text = path.read_text(encoding="utf-8")
            if "\u2013" in text or "\u2014" in text:
                violations.append((str(path.relative_to(ROOT)), "unicode dash"))
        for path in [
            *markdown_files(),
            *sorted((ROOT / "scripts").glob("*.py")),
            *sorted((ROOT / "assets").rglob("*.json")),
        ]:
            text = path.read_text(encoding="utf-8")
            if re.search(r"[A-Za-z]:\\\\|/Users/|/home/", text):
                violations.append((str(path.relative_to(ROOT)), "absolute path"))
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
