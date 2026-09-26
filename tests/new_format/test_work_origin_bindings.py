"""Generic mapping preserves controller review provenance without relaxing generic OCC."""
from __future__ import annotations

from unittest import mock

from support import R, TempCase, edit, locator
from paper_core import assessment, controller, review, sources
from paper_core.canonical import canonical_bytes
from paper_core.errors import ConflictError


class WorkOriginBindingTests(TempCase):
    def setUp(self):
        super().setUp()
        self.fx = self.fixture().primary()
        self.db = self.fx.open()
        self.addCleanup(self.db.close)

    def pending(self, *, work_origin=True):
        if work_origin:
            prepared = controller.prepare_work(self.db, audit_id="aud_1", mode="independent",
                                                focus=R("items", "itm_lem"))
            self.assertTrue(prepared["prepared"], prepared)
            packet = prepared["packet"]
        else:
            packet = self.fx.packet(self.db, "items:itm_lem", mode="independent")
        worker = {"packet_id": packet["packet_id"], "covered_targets": [R("items", "itm_lem")],
            "coverage_note": "Read the source proof", "exposure_report": {"status": "none_known", "note": ""},
            "judgments": [{"target": {"source_anchor_id": "anc_lem_proof", "description": "The proof argument"},
                "kind": "composition", "state": "complete", "outcome": "supported", "reasoning": "Source-based examination",
                "evidence_refs": ["anc_lem_proof"], "conditions": [], "next_action": None, "supersedes": None}]}
        submission = {"contract_version": 3, "request_id": self.fx.request_id(), "packet_id": packet["packet_id"],
                      "reviewer": "checker-A", "qualification_id": "qua_r1", "exposure": "source_only", "exposure_note": ""}
        if work_origin:
            envelope = dict(submission, rebase_packet_id=None)
            submitted = controller.submit_work(self.db, envelope_bytes=canonical_bytes(envelope),
                                                 response_bytes=canonical_bytes(worker))
        else:
            submitted = review.submit_review(self.db, submission=submission, response_bytes=canonical_bytes(worker))
        self.assertEqual("needs_revision", submitted["state"], submitted)
        mapping_packet = self.fx.packet(self.db, "items:itm_lem", mode="primary")
        self.assertNotIn("work", mapping_packet)
        request = {"contract_version": 3, "request_id": self.fx.request_id(), "packet_id": mapping_packet["packet_id"],
                   "response_id": submitted["response_id"], "entries": [{"judgment_index": 0,
                    "target": R("arguments", "arg_lem"), "rationale": "This argument has the reviewed source passage"}],
                   "reviewer": "coordinator"}
        return request

    def mapped(self, *, historical_binding=False, **kwargs):
        request = self.pending(**kwargs)
        if historical_binding:
            # Freeze the historical stored shape explicitly. Merely changing a
            # current packet's version would still produce contract-4 bindings.
            insert = self.db.insert_binding
            def insert_historical(collection, identifier, version, packet_id, binding):
                original_shape = dict(binding)
                original_shape.pop("semantic_memberships", None)
                return insert(collection, identifier, version, packet_id, original_shape)
            with mock.patch.object(self.db, "insert_binding", side_effect=insert_historical):
                mapped = review.map_response(self.db, mapping=request)
        else:
            mapped = review.map_response(self.db, mapping=request)
        self.assertEqual("accepted", mapped["state"])
        check_id = mapped["checks"][0]["check_id"]
        self.assertEqual("current", self.freshness(check_id)["freshness"])
        return check_id

    def freshness(self, check_id):
        snap = assessment.Snapshot(self.db, self.db.max_revision())
        return assessment.judgment_freshness(snap, self.db.head("checks", check_id), superseded=False)

    def coverage_progress(self):
        old = self.db.head("coverage", "cov_lem")
        successor = self.fx.check_edit("chk_successor", R("groups", "grp_lem"), "derivation",
            supersedes=self.fx.pin(self.db, "checks", "chk_der_lem"))
        self.fx.apply(self.db, [successor,
            edit("replace", "coverage", old.id, dict(old.body, check_ids=["chk_successor"], note="Linked corrected primary review"),
                 old.version)], mode="primary")

    def test_work_origin_mapping_survives_check_link_and_note_only_coverage_edit(self):
        check_id = self.mapped()
        stored = self.db.binding("checks", check_id, 1)["bindings"]
        self.assertIn("semantic_memberships", stored)
        self.assertEqual([], [r for r in stored["records"] if r["ref"]["collection"] == "checks"])
        self.coverage_progress()
        self.assertEqual("current", self.freshness(check_id)["freshness"])

    def test_work_origin_mapping_stales_when_coverage_span_changes(self):
        check_id = self.mapped()
        old = self.db.head("coverage", "cov_lem")
        self.fx.apply(self.db, [edit("replace", "coverage", old.id,
            dict(old.body, end_offset=old.body["end_offset"] - 1), old.version)], mode="primary")
        changed = self.freshness(check_id)
        self.assertEqual("needs_review", changed["freshness"])
        self.assertTrue(any(r["ref"]["id"] == "cov_lem" and r["facet"] == "coverage"
                            for r in changed["changes"]["records"]))

    def test_work_origin_mapping_stales_when_coverage_claim_changes(self):
        check_id = self.mapped()
        old = self.db.head("coverage", "cov_lem")
        self.fx.apply(self.db, [edit("replace", "coverage", old.id,
            dict(old.body, claim_refs=[R("items", "itm_thm")]), old.version)], mode="primary")
        self.assertEqual("needs_review", self.freshness(check_id)["freshness"])

    def test_work_origin_mapping_stales_when_reviewed_proof_excerpt_changes(self):
        check_id = self.mapped()
        anchor = self.db.head("anchors", "anc_lem_proof")
        packet = self.fx.packet(self.db)
        sources.anchor_sources(self.db, request={"contract_version": 3, "request_id": self.fx.request_id(),
            "packet_id": packet["packet_id"], "anchors": [{"id": anchor.id, "expected_version": anchor.version,
                "source_id": self.fx.source_id, "locator": locator(start=6, end=6)}]})
        changed = self.freshness(check_id)
        self.assertEqual("needs_review", changed["freshness"])
        self.assertTrue(any(r["ref"]["id"] == "anc_lem_proof" for r in changed["changes"]["records"]))

    def test_current_generic_origin_uses_semantic_memberships(self):
        check_id = self.mapped(work_origin=False)
        self.assertIn("semantic_memberships", self.db.binding("checks", check_id, 1)["bindings"])
        self.coverage_progress()
        self.assertEqual("current", self.freshness(check_id)["freshness"])

    def test_stored_historical_binding_keeps_strict_membership_behavior(self):
        check_id = self.mapped(work_origin=False, historical_binding=True)
        self.assertNotIn("semantic_memberships", self.db.binding("checks", check_id, 1)["bindings"])
        self.coverage_progress()
        self.assertEqual("needs_review", self.freshness(check_id)["freshness"])

    def test_work_origin_does_not_relax_mapping_packets_transaction_conflict_checks(self):
        request = self.pending()
        lemma = self.db.head("items", "itm_lem")
        self.fx.apply(self.db, [edit("replace", "items", lemma.id, dict(lemma.body, caption="Updated caption"), lemma.version)])
        before = self.db.max_revision()
        with self.assertRaises(ConflictError):
            review.map_response(self.db, mapping=request)
        self.assertEqual(before, self.db.max_revision())
        self.assertEqual("needs_revision", self.db.head("responses", request["response_id"]).body["state"])


if __name__ == "__main__":
    import unittest
    unittest.main()
