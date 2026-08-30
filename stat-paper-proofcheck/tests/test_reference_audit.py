from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "proofcheck.py"
SPEC = importlib.util.spec_from_file_location("proofcheck_reference", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load {SCRIPT}")
proofcheck = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proofcheck)

REFERENCE = SCRIPT.parents[1] / "assets" / "reference-audit"
REFRESH_SCRIPT = REFERENCE / "refresh_reference_audit.py"
REFRESH_SPEC = importlib.util.spec_from_file_location(
    "reference_refresh", REFRESH_SCRIPT
)
if REFRESH_SPEC is None or REFRESH_SPEC.loader is None:
    raise RuntimeError(f"Cannot load {REFRESH_SCRIPT}")
reference_refresh = importlib.util.module_from_spec(REFRESH_SPEC)
REFRESH_SPEC.loader.exec_module(reference_refresh)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class ReferenceAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "proofcheck-audit"
        shutil.copytree(REFERENCE / "proofcheck-audit", self.root)
        manifest = read_json(self.root / "AUDIT_MANIFEST.json")
        current = proofcheck.protocol_identity()["validator_sha256"]
        if manifest["protocol"]["validator_sha256"] != current:
            # A validator change stales the challenge bindings by design; the
            # bundled refresh helper performs the mechanical rebind on this
            # temporary copy without touching any recorded judgment.
            reference_refresh.refresh(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_shipped_audit_passes_the_full_finalization_gate(self) -> None:
        errors, result = proofcheck.check_audit_finalization(self.root)
        self.assertEqual([], errors)
        self.assertEqual(0, result["errors"])

    def test_shipped_audit_refinalizes_and_delivers_after_relocation(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            status = proofcheck.cmd_finalize(argparse.Namespace(root=self.root))
        self.assertEqual(0, status)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            delivery = proofcheck.cmd_delivery_check(
                argparse.Namespace(root=self.root)
            )
        self.assertEqual(0, delivery)
        result = json.loads(stdout.getvalue())
        self.assertEqual("FINAL", result["delivery_status"])
        self.assertTrue(result["usable_finalization"])

    def test_shipped_audit_exercises_the_new_evidence_gates(self) -> None:
        lem = read_json(
            self.root / "audit" / "04_local_checks" / "lem-growing-max.ledger.json"
        )
        failures = [
            move["failure"]
            for step in lem["steps"]
            for move in (step.get("inference") or {}).get("moves", [])
            if isinstance(move, dict) and isinstance(move.get("failure"), dict)
        ]
        counterexamples = [
            failure
            for failure in failures
            if failure.get("kind") == "counterexample"
        ]
        self.assertTrue(counterexamples)
        for failure in counterexamples:
            computation = failure["computation"]
            self.assertEqual("instantiated", computation["status"])
            script = (
                self.root / "audit" / "04_local_checks" / computation["script_file"]
            ).resolve()
            self.assertTrue(script.is_file())
            self.assertEqual(
                proofcheck.sha256_file(script), computation["script_sha256"]
            )

        issues = read_json(
            self.root / "audit" / "06_reports" / "ISSUE_LOG.json"
        )["issues"]
        self.assertEqual(1, len(issues))
        issue = issues[0]
        self.assertEqual("S1", issue["severity"])
        repair_search = issue["repair_search"]
        self.assertEqual("candidate_repair_exists", repair_search["conclusion"])
        outcomes = {row["outcome"] for row in repair_search["strategies"]}
        self.assertIn("failed", outcomes)
        self.assertIn("survives_local_inspection", outcomes)
        self.assertEqual(
            ["lem:growing-max", "thm:main"], issue["affected_results"]
        )

        calibration = read_json(
            self.root / "audit" / "07_runtime" / "CALIBRATION.json"
        )
        self.assertTrue(calibration["sessions"][-1]["passed"])
        self.assertEqual([], proofcheck.checker_calibration_errors(self.root))

        thm = read_json(
            self.root / "audit" / "04_local_checks" / "thm-main.ledger.json"
        )
        self.assertEqual("refuted", lem["review"]["statement_status"])
        self.assertEqual(
            "not_established", thm["review"]["statement_status"]
        )
        report = (
            self.root / "audit" / "06_reports" / "FINAL_REPORT.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Repair search conclusion: `candidate_repair_exists`", report)
        self.assertIn("| Strategy | Attempt | Outcome | Evidence |", report)

        changes = issue["suggested_changes"]
        by_action = {change["action"]: change for change in changes}
        strengthen = by_action["strengthen_assumption"]
        self.assertEqual("unit_statement", strengthen["repair_scope"])
        self.assertEqual(
            "adds_regularity_or_moment", strengthen["assumption_cost"]
        )
        self.assertNotIn("claim_cost", strengthen)
        weaken = by_action["weaken_claim"]
        self.assertEqual("none", weaken["assumption_cost"])
        self.assertEqual("restricts_scope", weaken["claim_cost"])
        self.assertIn(
            "| Target | Action | Repair scope | Assumption cost | Claim cost "
            "| Proposal | Verification status | Required rechecks |",
            report,
        )

    def test_workbench_examples_carry_the_current_annotation_schema(self) -> None:
        receipt = proofcheck.current_calibration_receipt(self.root)["sha256"]
        for name in ("lem", "thm"):
            annotations = read_json(
                REFERENCE / "workbench" / f"{name}.annotations.json"
            )
            self.assertEqual(
                proofcheck.SEMANTIC_ANNOTATION_SCHEMA_VERSION,
                annotations["annotation_schema_version"],
            )
            self.assertEqual(
                receipt, annotations["calibration_receipt_sha256"]
            )


if __name__ == "__main__":
    unittest.main()
