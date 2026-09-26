"""Exercise the shipped mathematical example without a private fixture dependency."""
import importlib.util

from support import PROOFCHECK, TempCase
from paper_core import storage
from paper_core.assessment import derive_full
from paper_core.projection import build_projection

EXAMPLE = PROOFCHECK / "assets" / "examples" / "probability" / "build_example.py"
spec = importlib.util.spec_from_file_location("proofcheck_probability_example", EXAMPLE)
example = importlib.util.module_from_spec(spec)
spec.loader.exec_module(example)


class ProbabilityExampleTests(TempCase):
    def test_example_records_full_primary_reasoning_but_no_independent_credit(self):
        result = example.build_example(self.work / "built")
        self.assertGreater(result["primary_submissions"], 0)
        self.assertFalse(result["progress"]["process_complete"])
        with storage.Database(result["database"]) as db:
            self.assertEqual([], db.heads("qualifications"))
            self.assertEqual([], db.heads("responses"))
            _, assessment = derive_full(db, audit_id=example.AUDIT)
            primary = [o for o in assessment["obligations"] if o["required"] and o["role"] == "primary"]
            self.assertTrue(primary)
            self.assertEqual([], [o for o in primary if not o["satisfied"]])
            self.assertEqual(8, len(db.heads("groups")))
            self.assertEqual(10, len(db.heads("application_details")))
            self.assertEqual({"anc_hoeffding_proof", "anc_ratio_proof"},
                             {pin["id"] for b in db.heads("proof_boundaries") for pin in b.body["anchor_refs"]})
            self.assertTrue(all("worked example" in c.body["reasoning"] for c in db.heads("checks")))
            projection = build_projection(db, audit_id=example.AUDIT)
            self.assertFalse(projection["summary"]["progress"]["process_complete"])
            self.assertIn("denominator", str(projection))
        with self.assertRaisesRegex(ValueError, "never overwrites"):
            example.build_example(self.work / "built")

    def test_global_conditional_theorem_and_temporary_assumption_have_distinct_scope(self):
        result = example.build_example(self.work / "scopes")
        self.assertEqual({
            "conditional_theorem_in_event_scope": "available",
            "temporary_premise_inside_scope": "available",
            "temporary_premise_outside_scope": "unavailable",
            "denominator_inside_scope": "available",
            "denominator_outside_scope": "unavailable",
            "discharged_implication": "available"}, result["scope_examples"])
