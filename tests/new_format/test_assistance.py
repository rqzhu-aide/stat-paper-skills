"""Contract-derived help remains uncommitted, scoped and free of invented judgments."""
import copy
import json
import unittest
from unittest.mock import patch

from support import Fixture, R, TempCase, edit
from paper_core import acceptance, assistance, contract, controller, review
from paper_core.assessment import derive_full
from paper_core.canonical import canonical_bytes
from paper_core.errors import InvalidRequest


class AssistanceTests(TempCase):
    def test_selected_authoring_shape_includes_required_nulls_without_scientific_defaults(self):
        result = assistance.authoring_template("items", packet_id="pkt_author")
        entry = result["template"]["edits"][0]
        body = entry["body"]
        item_schema = contract.BODY_SCHEMAS["items"]
        self.assertEqual(set(item_schema.fields) - set(item_schema.optional), set(body))
        self.assertIn("proof_idea", result["body_shape"]["optional_fields"])
        self.assertEqual("", body["kind"])
        self.assertEqual("", body["origin"])
        self.assertEqual({"form": "", "text": ""}, body["statement"])
        self.assertIsNone(body["uncertainty"])
        self.assertIsNone(body["owner_id"])
        self.assertIsNone(entry["expected_version"])
        self.assertNotEqual(entry["id"], assistance.authoring_template("items", packet_id="pkt_author")
                            ["template"]["edits"][0]["id"])
        self.assertTrue(contract.validate_body("items", body))
        self.assertEqual([], contract.validate_shape(contract.BATCH, result["template"]))
        self.assertNotIn("reconciliations", str(result["body_shape"]))

    def test_authoring_template_can_be_completed_through_public_acceptance(self):
        fx = self.fixture().audit()
        with fx.open() as db:
            packet = fx.packet(db, f"papers:{fx.paper_id}")
            result = assistance.authoring_template("items", packet_id=packet["packet_id"])
            entry = result["template"]["edits"][0]
            entry["body"] = Fixture.item_edit(entry["id"], "assumption", "Assumption C", "anc_lem", "anc_lem_proof")["body"]
            before = db.max_revision()
            self.assertIsNone(db.head("items", entry["id"]))
            try:
                acceptance.apply_batch(db, result["template"])
            except InvalidRequest as exc:
                self.fail(str(exc.records))
            self.assertGreater(db.max_revision(), before)
            self.assertEqual(entry["body"], db.head("items", entry["id"]).body)

    def test_application_identity_and_nullable_not_optional_are_explicit(self):
        with self.assertRaisesRegex(InvalidRequest, "existing use ID"):
            assistance.authoring_template("application_details", packet_id="pkt_author")
        result = assistance.authoring_template("application_details", packet_id="pkt_author", record_id="use_source")
        entry = result["template"]["edits"][0]
        self.assertEqual(entry["id"], entry["body"]["use_id"])
        self.assertIn("needed_form", entry["body"])
        self.assertIsNone(entry["body"]["needed_form"])
        self.assertNotIn("scope_id", entry["body"])
        self.assertEqual(["scope_id"], result["body_shape"]["optional_fields"])
        self.assertTrue(result["body_shape"]["fields"]["needed_form"]["nullable"])

    def test_worker_guidance_is_role_specific_and_has_no_assignment_dependencies(self):
        with patch("paper_core.assessment.derive_full", side_effect=AssertionError("worker guidance reads no DB")):
            guidance = assistance.worker_guidance("independent")
        self.assertEqual(set(contract.JUDGMENT.fields), set(guidance["judgment_shape"]["fields"]))
        self.assertEqual({"source_anchor_id": "", "description": ""}, guidance["source_target_template"])
        self.assertEqual({kind: list(targets) for kind, targets in contract.CHECK_TARGETS.items()},
                         guidance["canonical_target_collections"])
        self.assertEqual(["arguments"], guidance["canonical_target_collections"]["composition"])
        self.assertEqual(["audits"], guidance["canonical_target_collections"]["adversarial"])
        self.assertEqual({"kind", "target"}, set(guidance["source_target_example"]))
        self.assertNotIn("outcome", str(guidance["source_target_example"]))
        text = canonical_bytes(guidance).decode("utf-8")
        for forbidden in ("draft_refs", "primary_checks", "qualification_id", "assigned_task_ids", "prerequisite_ids"):
            self.assertNotIn(forbidden, text)
        self.assertNotIn("row_shape", guidance)
        self.assertNotIn("judgment_shape", assistance.worker_guidance("primary"))
        self.assertEqual(set(contract.BODY_SCHEMAS["reconciliations"].fields),
                         set(assistance.worker_guidance("reconcile")["row_shape"]["fields"]))
        with self.assertRaises(InvalidRequest):
            assistance.worker_guidance("unknown")

    def test_guidance_distinguishes_controller_coverage_and_reconciliation_identity(self):
        guidance = assistance.worker_guidance("primary", composition=True)
        coverage = guidance["response_shape"]["fields"]["coverage"]["array_of"]["fields"]
        self.assertTrue({"check_task_ids", "existing_check_refs", "replaces"}.issubset(coverage))
        self.assertNotIn("check_ids", coverage)
        direct = assistance.authoring_template("coverage", packet_id="pkt_author")
        self.assertIn("check_ids", direct["body_shape"]["fields"])
        self.assertNotIn("replaces", direct["body_shape"]["fields"])
        self.assertIn("direct stored coverage uses check_ids", guidance["coverage_note"])
        self.assertIn("same ID in the submission envelope", assistance.worker_guidance("reconcile")["note"])

    def test_drafts_keep_distinct_owners_and_intended_predecessors(self):
        fx = self.fixture().audit(independent_required=False)
        with fx.open() as db:
            prior = Fixture.check_edit("chk_prior", R("groups", "grp_lem"), "derivation")
            fx.apply(db, [prior], "items:itm_lem", mode="primary")
            predecessor = fx.pin(db, "checks", "chk_prior")
            drafts = [Fixture.check_edit("chk_draft_a", R("groups", "grp_lem"), "derivation",
                       state="draft", reviewer="checker-a", supersedes=predecessor),
                      Fixture.check_edit("chk_draft_b", R("groups", "grp_lem"), "derivation",
                       state="draft", reviewer="checker-b")]
            drafts[0]["body"]["next_action"] = "Finish the induction step."
            drafts[1]["body"]["next_action"] = "Check the base case."
            fx.apply(db, drafts, "items:itm_lem", mode="primary")
            prepared = controller.prepare_work(db, audit_id=fx.audit_id, mode="primary", focus=R("items", "itm_lem"))
            self.assertTrue(prepared["prepared"])
            before = db.max_revision()
            result = assistance.coordinator_guidance(db, prepared["manifest"])
            by_owner = {row["reviewer"]: row for row in result["draft_candidates"]}
            self.assertEqual({"checker-a", "checker-b"}, set(by_owner))
            self.assertEqual(predecessor, by_owner["checker-a"]["supersedes"])
            self.assertIsNone(by_owner["checker-b"]["supersedes"])
            self.assertEqual("Check the base case.", by_owner["checker-b"]["next_action"])
            self.assertEqual(before, db.max_revision())
            limited = copy.deepcopy(prepared["manifest"])
            limited["read_set"] = [pin for pin in limited["read_set"] if pin["id"] != "chk_draft_b"]
            self.assertEqual(["checker-a"], [r["reviewer"] for r in assistance.coordinator_guidance(db, limited)["draft_candidates"]])

    def test_reconciliation_candidates_are_exact_and_require_an_authored_decision(self):
        fx = self.fixture().independent()
        with fx.open() as db:
            prepared = controller.prepare_work(db, audit_id=fx.audit_id, mode="reconcile", focus=R("items", "itm_lem"))
            self.assertTrue(prepared["prepared"], prepared)
            assessed = derive_full(db, audit_id=fx.audit_id)
            with patch("paper_core.assessment.derive_full", side_effect=AssertionError("reuse assessment")):
                result = assistance.coordinator_guidance(db, prepared["manifest"], assessed=assessed)
            candidate = next(row for row in result["reconciliation_candidates"] if row["target"] == R("arguments", "arg_lem"))
            self.assertTrue(candidate["has_both_roles"])
            self.assertEqual(["chk_comp_lem"], [pin["id"] for pin in candidate["primary_checks"]])
            self.assertEqual([fx.independent_checks["itm_lem"]], [pin["id"] for pin in candidate["independent_checks"]])
            self.assertTrue(all("row_template" not in entry for entry in result["reconciliation_candidates"]))
            row = result["reconciliation_row_template"]
            self.assertEqual("", row["decision"])
            self.assertEqual("", row["rationale"])
            self.assertEqual([], row["primary_checks"])
            self.assertEqual([], row["independent_checks"])
            self.assertTrue(contract.validate_body("reconciliations", row))
            row.update(target=candidate["target"], primary_checks=candidate["primary_checks"], independent_checks=candidate["independent_checks"],
                       decision="agree", rationale="Compared the exact composition under the same premises.", adjudicator="coordinator")
            review.reconcile(db, batch=fx.batch([edit("create", "reconciliations", "rec_guided", row)], prepared["packet_id"]))
            self.assertEqual(row, db.head("reconciliations", "rec_guided").body)
            with self.assertRaisesRegex(InvalidRequest, "current assessment"):
                assistance.coordinator_guidance(db, prepared["manifest"], assessed=assessed)

    def test_primary_renewal_candidates_are_assigned_readable_and_currently_stale(self):
        fx = self.fixture().primary()
        with fx.open() as db:
            old = db.head("coverage", "cov_lem")
            fx.apply(db, [edit("replace", "coverage", old.id,
                dict(old.body, end_offset=old.body["end_offset"] - 1), old.version)], mode="primary")
            prepared = controller.prepare_work(db, audit_id=fx.audit_id, mode="primary", focus=R("items", "itm_lem"))
            assessed = derive_full(db, audit_id=fx.audit_id)
            with patch("paper_core.assessment.derive_full", side_effect=AssertionError("reuse assessment")):
                result = assistance.coordinator_guidance(db, prepared["manifest"], assessed=assessed)
            candidates = result["renewal_candidates"]
            self.assertEqual([fx.pin(db, "checks", "chk_comp_lem")], [c["ref"] for c in candidates])
            self.assertEqual("primary-1", candidates[0]["reviewer"])
            self.assertEqual(prepared["assigned_task_ids"], [c["task_id"] for c in candidates])
            self.assertNotIn("renewal_candidates", prepared["worker_guidance"])
            self.assertTrue(all(r.get("supersedes") is None for r in prepared["scaffold"]["results"]))

            limited = copy.deepcopy(prepared["manifest"])
            limited["read_set"].remove(candidates[0]["ref"])
            self.assertNotIn("renewal_candidates", assistance.coordinator_guidance(db, limited, assessed=assessed))
            unrelated = copy.deepcopy(prepared["manifest"])
            unrelated["work"]["tasks"][0]["target"] = R("arguments", "arg_thm")
            self.assertNotIn("renewal_candidates", assistance.coordinator_guidance(db, unrelated, assessed=assessed))

            # Inspecting an old packet after an explicit successor must not offer
            # its superseded predecessor as though renewal were still needed.
            fx.apply(db, [Fixture.check_edit("chk_renewed", R("arguments", "arg_lem"), "composition",
                supersedes=candidates[0]["ref"])], mode="primary")
            inspected = controller.inspect_work(db, packet_id=prepared["packet_id"])
            self.assertNotIn("renewal_candidates", inspected["coordinator_guidance"])
            with self.assertRaisesRegex(InvalidRequest, "current assessment"):
                assistance.coordinator_guidance(db, prepared["manifest"], assessed=assessed)

    def test_normal_and_independent_guidance_add_no_renewal_inventory(self):
        fx = self.fixture().audit(independent_required=False)
        with fx.open() as db:
            prepared = controller.prepare_work(db, audit_id=fx.audit_id, mode="primary", focus=R("items", "itm_lem"))
            with patch("paper_core.assessment.derive_full", side_effect=AssertionError("no extra assessment")):
                normal = assistance.coordinator_guidance(db, prepared["manifest"])
            self.assertNotIn("renewal_candidates", normal)
            self.assertNotIn("renewal_note", normal)
            hidden = copy.deepcopy(prepared["manifest"])
            hidden["mode"] = "independent"
            with patch("paper_core.assessment.derive_full", side_effect=AssertionError("independent remains blind")):
                self.assertNotIn("renewal_candidates", assistance.coordinator_guidance(db, hidden))

    def test_changed_target_offers_historical_check_for_explicit_renewal(self):
        fx = self.fixture().primary()
        with fx.open() as db:
            group = db.head("groups", "grp_lem")
            fx.apply(db, [edit("replace", "groups", group.id,
                dict(group.body, rationale="Revised explanation of the elementary estimate."), group.version)])
            _, assessed = derive_full(db, audit_id=fx.audit_id)
            self.assertEqual("historical", assessed["judgments"]["checks:chk_der_lem"]["freshness"])
            prepared = controller.prepare_work(db, audit_id=fx.audit_id, mode="primary", focus=R("items", "itm_lem"))
            candidates = {row["task_id"]: row for row in prepared["coordinator_guidance"]["renewal_candidates"]}
            self.assertIn(fx.pin(db, "checks", "chk_der_lem"), [c["ref"] for c in candidates.values()])
            worker = copy.deepcopy(prepared["scaffold"])
            for row in worker["results"]:
                row.update(state="complete", outcome="supported", evidence_refs=["anc_lem_proof"],
                           reasoning="Re-examined the changed local inference and its composition.",
                           supersedes=candidates[row["task_id"]]["ref"])
            envelope = {"contract_version": 4, "request_id": fx.request_id(), "packet_id": prepared["packet_id"],
                "rebase_packet_id": None, "reviewer": "primary-1", "qualification_id": None,
                "exposure": None, "exposure_note": ""}
            result = controller.submit_work(db, envelope_bytes=canonical_bytes(envelope), response_bytes=canonical_bytes(worker))
            self.assertEqual("accepted", result["state"], result)
            self.assertEqual([], result["remaining_task_ids"])

    def test_mapping_template_keeps_source_and_authorization_packets_distinct(self):
        fx = self.fixture().primary()
        with fx.open() as db:
            source = fx.packet(db, "items:itm_lem", mode="independent")
            judgment = copy.deepcopy(assistance.worker_guidance("independent")["source_target_example"])
            judgment["target"].update(source_anchor_id="anc_lem_proof", description="Lemma proof composition")
            judgment.update(state="complete", outcome="supported",
                            reasoning="Induction establishes the claimed uniform bound.", evidence_refs=["anc_lem_proof"],
                            conditions=[], next_action=None, supersedes=None)
            worker = {"packet_id": source["packet_id"], "covered_targets": [R("items", "itm_lem")],
                      "coverage_note": "Examined the entire lemma proof.", "exposure_report": {"status": "none_known", "note": ""},
                      "judgments": [judgment]}
            raw = canonical_bytes(worker)
            submitted = review.submit_review(db, submission={"contract_version": 4, "request_id": fx.request_id(),
                "packet_id": source["packet_id"], "reviewer": "checker-A", "qualification_id": "qua_r1",
                "exposure": "source_only", "exposure_note": ""}, response_bytes=raw)
            self.assertEqual("needs_revision", submitted["state"])
            packet = fx.packet(db, "items:itm_lem", mode="primary")
            result = assistance.mapping_template(source_packet_id=source["packet_id"], mapping_packet_id=packet["packet_id"],
                response_id=submitted["response_id"], judgment_indexes=[0])
            mapping = result["template"]
            self.assertEqual(packet["packet_id"], mapping["packet_id"])
            self.assertNotEqual(result["source_packet_id"], mapping["packet_id"])
            self.assertEqual("", mapping["entries"][0]["rationale"])
            mapping["reviewer"] = "coordinator"
            mapping["entries"][0].update(target=R("arguments", "arg_lem"), rationale="The reviewed source passage is this exact argument.")
            mapped = review.map_response(db, mapping=mapping)
            self.assertEqual("accepted", mapped["state"])
            response = db.head("responses", submitted["response_id"])
            self.assertEqual(raw, db.get_blob(response.body["original_blob"]))
            with self.assertRaises(InvalidRequest):
                assistance.mapping_template(source_packet_id=source["packet_id"], mapping_packet_id=packet["packet_id"],
                    response_id=submitted["response_id"], judgment_indexes=[0, 0])

    def test_compromised_opinion_is_not_offered_as_eligible_independent_evidence(self):
        fx = self.fixture().independent()
        with fx.open() as db:
            good_check = db.head("checks", fx.independent_checks["itm_lem"])
            good_response = db.head("responses", good_check.body["response_id"])
            worker = json.loads(db.get_blob(good_response.body["original_blob"]))
            packet = fx.packet(db, "items:itm_lem", mode="independent")
            worker["packet_id"] = packet["packet_id"]
            worker["exposure_report"] = {"status": "possible_exposure", "note": "Primary reasoning was visible."}
            submitted = review.submit_review(db, submission={"contract_version": 4, "request_id": fx.request_id(),
                "packet_id": packet["packet_id"], "reviewer": "checker-A", "qualification_id": "qua_r1",
                "exposure": "compromised", "exposure_note": "Primary reasoning was visible."},
                response_bytes=canonical_bytes(worker))
            mapping_packet = fx.packet(db, "items:itm_lem", mode="primary")
            mapping = assistance.mapping_template(source_packet_id=packet["packet_id"], mapping_packet_id=mapping_packet["packet_id"],
                response_id=submitted["response_id"], judgment_indexes=[0])["template"]
            mapping["reviewer"] = "coordinator"
            mapping["entries"][0].update(target=R("arguments", "arg_lem"), rationale="Same source proof, with compromised exposure retained.")
            mapped = review.map_response(db, mapping=mapping)
            self.assertEqual("accepted", mapped["state"])
            bad_id = mapped["checks"][0]["check_id"]
            prepared = controller.prepare_work(db, audit_id=fx.audit_id, mode="reconcile", focus=R("items", "itm_lem"))
            self.assertTrue(prepared["prepared"], prepared)
            guidance = assistance.coordinator_guidance(db, prepared["manifest"])
            eligible = [pin["id"] for row in guidance["reconciliation_candidates"] for pin in row["independent_checks"]]
            self.assertIn(good_check.id, eligible)
            self.assertNotIn(bad_id, eligible)
            recorded = [entry["ref"]["id"] for row in guidance["reconciliation_candidates"]
                        for entry in row["required_other_opinions"]]
            self.assertIn(bad_id, recorded)

    def test_revised_opinion_guidance_keeps_readable_history_separate_from_current_support(self):
        fx = self.fixture().independent()
        with fx.open() as db:
            prior = db.head("checks", fx.independent_checks["itm_lem"])
            original = db.head("responses", prior.body["response_id"])
            worker = json.loads(db.get_blob(original.body["original_blob"]))
            packet = fx.packet(db, "items:itm_lem", mode="independent")
            worker["packet_id"] = packet["packet_id"]
            worker["judgments"][0].update(supersedes=prior.pinned, reasoning="Explicitly renewed synthetic examination of the same proof.")
            submitted = review.submit_review(db, submission={"contract_version": 4, "request_id": fx.request_id(),
                "packet_id": packet["packet_id"], "reviewer": "checker-A", "qualification_id": "qua_r1",
                "exposure": "source_only", "exposure_note": "Synthetic same-reviewer continuation."}, response_bytes=canonical_bytes(worker))
            authority = fx.packet(db, "items:itm_lem", mode="reconcile")
            mapping = assistance.mapping_template(source_packet_id=packet["packet_id"], mapping_packet_id=authority["packet_id"],
                response_id=submitted["response_id"], judgment_indexes=[0])["template"]
            mapping["reviewer"] = "coordinator"
            mapping["entries"][0].update(target=R("arguments", "arg_lem"), rationale="The renewed source judgment examines this exact argument.")
            mapped = review.map_response(db, mapping=mapping)
            successor = db.head("checks", mapped["checks"][0]["check_id"])
            prepared = controller.prepare_work(db, audit_id=fx.audit_id, mode="reconcile", focus=R("items", "itm_lem"))
            self.assertTrue(prepared["prepared"], prepared)
            assessed = derive_full(db, audit_id=fx.audit_id)
            with patch("paper_core.assessment.derive_full", side_effect=AssertionError("reuse existing snapshot")):
                guidance = assistance.coordinator_guidance(db, prepared["manifest"], assessed=assessed)
            candidate = next(row for row in guidance["reconciliation_candidates"] if row["target"] == prior.body["target"])
            self.assertEqual([successor.pinned], candidate["independent_checks"])
            self.assertEqual([prior.pinned], [entry["ref"] for entry in candidate["required_other_opinions"]])
            self.assertTrue(candidate["required_other_opinions"][0]["superseded"])
            self.assertIn(prior.pinned, prepared["manifest"]["read_set"])
            self.assertNotIn("missing_required_opinion_count", candidate)
            limited = copy.deepcopy(prepared["manifest"])
            limited["read_set"].remove(prior.pinned)
            limited_guidance = assistance.coordinator_guidance(db, limited, assessed=assessed)
            limited_row = next(row for row in limited_guidance["reconciliation_candidates"] if row["target"] == prior.body["target"])
            self.assertEqual([], limited_row["required_other_opinions"])
            self.assertEqual(1, limited_row["missing_required_opinion_count"])
            # Current eligible pins alone omit an opinion required by validation.
            row = copy.deepcopy(guidance["reconciliation_row_template"])
            row.update(target=candidate["target"], primary_checks=candidate["primary_checks"],
                independent_checks=candidate["independent_checks"], decision="independent_revised",
                successor_checks=[successor.pinned], rationale="The explicit successor replaces the earlier opinion.", adjudicator="coordinator")
            with self.assertRaises(InvalidRequest) as error:
                review.reconcile(db, batch=fx.batch([edit("create", "reconciliations", "rec_history", row)], prepared["packet_id"]))
            self.assertIn(prior.id, str(error.exception.records))
            row["independent_checks"] += [entry["ref"] for entry in candidate["required_other_opinions"]]
            review.reconcile(db, batch=fx.batch([edit("create", "reconciliations", "rec_history", row)], prepared["packet_id"]))
            self.assertEqual("independent_revised", db.head("reconciliations", "rec_history").body["decision"])


if __name__ == "__main__":
    unittest.main()
