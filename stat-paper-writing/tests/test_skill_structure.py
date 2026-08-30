from __future__ import annotations

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
        self.assertLessEqual(sizes["SKILL.md"], 10_000)
        # These are byte proxies for canonical reference bundles, not runtime
        # token totals. Default full-audit reporting follows the required
        # WHOLE_PAPER_NARRATIVE pass and therefore includes its owner reference.
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
                "polishing-protocol.md",
                "argument-architecture.md",
            ],
            "method_draft": [
                "SKILL.md",
                "method-description.md",
            ],
            "high_risk_method_draft": [
                "SKILL.md",
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
            "full_audit_reporting": [
                "SKILL.md",
                "revision-audit.md",
                "quick-section-audit.md",
                "argument-architecture.md",
                "reporting-and-validation.md",
                "full-audit-operations.md",
            ],
            "full_audit_authoring": [
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
            "light_polish": 22_000,
            "substantive_register": 32_000,
            "local_register": 24_000,
            "structural_method_revision": 28_000,
            "paper_restructuring": 30_000,
            "method_draft": 16_000,
            "high_risk_method_draft": 24_000,
            "proof_polish": 28_000,
            "quick_audit_startup": 18_000,
            "quick_audit_reporting": 23_000,
            "abstract_positioning": 23_000,
            "full_audit_startup": 22_000,
            "full_audit_diagnostic": 30_000,
            "full_audit_reporting": 51_000,
            "full_audit_authoring": 62_000,
        }
        totals = {
            route: sum(sizes[name] for name in names)
            for route, names in routes.items()
        }
        self.assertEqual(
            {route: total for route, total in totals.items() if total > limits[route]},
            {},
        )

    def test_canonical_contract_owners(self) -> None:
        content = {
            path.name: path.read_text(encoding="utf-8") for path in markdown_files()
        }
        fixed_proof_phrase = "This is the stated conclusion."
        self.assertEqual(
            [name for name, text in content.items() if fixed_proof_phrase in text],
            [],
        )

        ledger_header = (
            "Rank | Contribution | Method object or construction | Formal support | "
            "Empirical support | Boundary"
        )
        ledger_owners = [name for name, text in content.items() if ledger_header in text]
        self.assertEqual(ledger_owners, ["argument-architecture.md"])

        proof_boundary = (
            "Do not add a new proof-completion claim or a standardized replacement."
        )
        proof_owners = [
            name for name, text in content.items() if proof_boundary in text
        ]
        self.assertEqual(proof_owners, ["theoretical-proofs.md"])
        self.assertIn("$stat-paper-proofcheck", content["SKILL.md"])
        self.assertIn("$stat-paper-proofcheck", content["theoretical-proofs.md"])
        self.assertIn("do not start it implicitly", content["SKILL.md"])
        self.assertIn("do not start that audit implicitly", content["theoretical-proofs.md"])

        provenance_rule = "independent confirmation was not performed"
        provenance_owners = [
            name for name, text in content.items() if provenance_rule in text
        ]
        self.assertEqual(provenance_owners, ["terminology-audit.md"])

        material_change_owners = [
            name for name, text in content.items() if "Material change:" in text
        ]
        self.assertEqual(material_change_owners, ["polishing-protocol.md"])
        self.assertIn(
            "Whenever a terminology provenance note uses Manuscript-supported",
            content["terminology-audit.md"],
        )

    def test_requested_action_controls_intervention(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        polish = (REFERENCES / "polishing-protocol.md").read_text(encoding="utf-8")
        quick_audit = (REFERENCES / "quick-section-audit.md").read_text(
            encoding="utf-8"
        )
        author_decisions = (
            REFERENCES / "support-and-author-decisions.md"
        ).read_text(encoding="utf-8")
        self.assertIn("An audit diagnoses and reports without rewriting.", skill)
        self.assertIn(
            "A polish or revision performs its checks privately and directly returns or "
            "applies every safe supported edit",
            skill,
        )
        self.assertIn(
            "Combined audit and revision records findings first, then applies supported "
            "repairs",
            skill,
        )
        self.assertIn(
            "return or apply the improved manuscript text rather than an audit report",
            polish,
        )
        self.assertIn("Continue with safe edits elsewhere.", polish)
        self.assertIn("Do not rewrite unless revision was requested.", quick_audit)
        self.assertIn(
            "| Prose or structural revision | [polishing-protocol.md]",
            skill,
        )
        self.assertIn(
            "| Deliberate planning | [argument-architecture.md]",
            skill,
        )
        self.assertIn("for paper-level restructuring", skill)
        self.assertIn(
            "**Planning:** return an anchored move map without editing.",
            skill,
        )
        self.assertIn(
            "**Structural revision:** build a private meaning lock and edit directly "
            "using the section guide.",
            skill,
        )
        self.assertNotIn("Deliberate planning or restructuring", skill)
        self.assertIn(
            "author-supplied material uniquely supports a narrower",
            author_decisions,
        )
        self.assertIn("apply that bounded replacement directly", author_decisions)
        self.assertIn(
            "Require an author choice when supplied representations conflict, causal or "
            "identification status would change, or multiple scientifically meaningful "
            "replacements remain",
            author_decisions,
        )
        self.assertNotIn("diagnosis precedes any authorized revision", skill)
        self.assertNotIn("diagnose first", skill)

    def test_router_exposes_all_high_risk_triggers(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        required = [
            "support-and-author-decisions.md",
            "reporting-and-validation.md",
            "quick-section-audit.md",
            "full-audit-data-contract.md",
            "full-audit-operations.md",
            "revision-audit.md",
            "polishing-protocol.md",
            "theoretical-proofs.md",
            "argument-architecture.md",
            "terminology-audit.md",
            "numerical-experiments.md",
            "missing or proposed assumption",
            "conflicting",
            "citation",
            "construction-to-theorem",
            "Full audit only",
        ]
        self.assertEqual([item for item in required if item not in text], [])
        self.assertIn(
            "Substantive revision involving logic and terminology or register",
            text,
        )
        self.assertIn(
            "polishing-protocol.md](references/polishing-protocol.md) and "
            "[wording-register.md",
            text,
        )

    def test_abstract_positioning_routes_to_candidate_hierarchy_outside_ledger(
        self,
    ) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        introduction = (REFERENCES / "introduction.md").read_text(encoding="utf-8")
        argument = (REFERENCES / "argument-architecture.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "For paper-level abstract or introduction positioning, add "
            "[argument-architecture.md]",
            skill,
        )
        self.assertIn(
            "For contribution identities, hierarchy, dependency, and rank, load "
            "[argument-architecture.md]",
            introduction,
        )
        for rule in {
            "propose at most two candidate headline contributions",
            "Candidate primary contribution",
            "keep it outside the contribution ledger's supplied rank",
            "Editorial candidate ranks remain outside the factual ledger",
        }:
            self.assertIn(rule, argument)
        self.assertIn(
            "do not call it novel, first, or boundary-pushing without supplied or "
            "independently verified evidence",
            argument,
        )

    def test_shared_quick_and_section_audit_protocol(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        quick = (REFERENCES / "quick-section-audit.md").read_text(encoding="utf-8")
        revision = (REFERENCES / "revision-audit.md").read_text(encoding="utf-8")
        self.assertIn(
            "| Quick or section presentation audit | "
            "[quick-section-audit.md](references/quick-section-audit.md)",
            skill,
        )
        for heading in {
            "## 1. Neutral orientation",
            "## 2. Atomic documentary consistency",
            "## 3. Formal-object and claim contracts",
            "## 4. Local presentation",
            "## 5. Section jobs and transitions",
        }:
            self.assertIn(heading, quick)
        self.assertIn(
            "For the default full audit, after neutral orientation load "
            "[quick-section-audit.md](quick-section-audit.md)",
            revision,
        )
        self.assertNotIn("## 2. Audit atomic documentary consistency", revision)
        owners = [
            path.name
            for path in markdown_files()
            if "Begin with the finest applicable checks:" in path.read_text(
                encoding="utf-8"
            )
        ]
        self.assertEqual(owners, ["quick-section-audit.md"])

    def test_full_audit_data_contract_is_deferred_and_exact(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        contract = (REFERENCES / "full-audit-data-contract.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "Load [full-audit-data-contract.md]"
            "(references/full-audit-data-contract.md) only when editing",
            skill,
        )
        link_owners = {
            path.name
            for path in markdown_files()
            if "[full-audit-data-contract.md]" in path.read_text(encoding="utf-8")
        }
        self.assertEqual(
            link_owners,
            {"SKILL.md", "full-audit-operations.md"},
        )
        required_contract_text = {
            '"kind": "line"',
            '"kind": "page"',
            '"kind": "artifact"',
            '"identity_anchors": []',
            '"finding_dispositions": null',
            '"phase": "audit, baseline, or post_edit"',
            '["references/reporting-and-validation.md", '
            '"references/full-audit-operations.md", '
            '"references/full-audit-data-contract.md"]',
            "Allowed compile statuses are passed, failed, not_run, and unavailable.",
            "Allowed render statuses are inspected, failed, not_run, and unavailable.",
            "The path must start with artifacts/",
            "Never hand-edit them.",
        }
        self.assertEqual(
            [item for item in required_contract_text if item not in contract],
            [],
        )

    def test_harness_is_full_audit_only(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("scripts/writer_audit.py", text)
        self.assertIn("Full audit only", text)
        self.assertNotIn("validate_writer_audit.py", text)
        self.assertTrue((ROOT / "scripts" / "writer_audit.py").is_file())
        self.assertFalse((ROOT / "scripts" / "validate_writer_audit.py").exists())
        self.assertIn(
            "freeze", (ROOT / "scripts" / "writer_audit.py").read_text(encoding="utf-8")
        )

    def test_portable_commands_and_discovery_metadata(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        operations = (REFERENCES / "full-audit-operations.md").read_text(
            encoding="utf-8"
        )
        combined = skill + operations
        self.assertNotIn("python scripts/writer_audit.py", combined)
        self.assertIn('python "SKILL_DIR/scripts/writer_audit.py" init', skill)
        self.assertIn(
            'python "AUDIT_DIR/protocol/scripts/writer_audit.py" status', skill
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
            r"(?m)^\| `stat-paper-writing` \| v([^ |]+) \|$",
            readme,
        )
        self.assertIsNotNone(skill_version)
        self.assertIsNotNone(readme_version)
        assert skill_version is not None and readme_version is not None
        self.assertEqual(skill_version.group(1), "1.2")
        self.assertEqual(readme_version.group(1), skill_version.group(1))

    def test_runtime_metadata_covers_writer_harness(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        required = {
            "proofcheck and writing helpers and tests require Python 3.10",
            "pypdf",
            "PyPDF2",
            '--pdf-page-count "SOURCE=N"',
            "python -m unittest discover -s stat-paper-writing/tests",
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
